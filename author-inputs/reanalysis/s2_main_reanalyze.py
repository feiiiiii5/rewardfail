"""主测量只重新分析（方案第 18.3 节，Codex 2026-10-08 审核）：用修订后的 rewardfail/s2/analyze.py（本机预算终止只记到
被杀时结果还没送回的尝试）在原始记录的临时副本上重新合成各段逐行记录，按 s2_main.followups 原流程重算判定与统计，
更新 results/s2_main/report.json。不判分、不续跑，原运行目录与执行版本锁只读；运行目录里的 report.json 仍是 10-07 原版，
旧正式版另见实验仓 6c416b2。

做什么：
1. 原运行目录 162 个文件逐个 sha256，开始与结束各算一次，要求不变。
2. 按 s2_main.build 重建任务与预先抽取，与 run.json 版本锁里的 pre 逐项核对；再算当前版本锁，列出与原锁的不同
   （预期只有代码文件，执行版本见原锁与 9a88991）。
3. 每段复制到临时目录，先用原执行版本（9a88991）的 analyze.py 合成，要求与原 rows.jsonl 逐字节相同（证明差异只来自修订）；
   再用修订后的合成，逐段列出类别变化。
4. 用 s2_main.followups 重算：段函数不判分，只核对这一段要的行是不是原段跑过的行（编号摘要与 pass_spec 相同，或是其子集），
   返回原 pass_done。修订后重放集合按规则是 47 行，原段按修订前的集合跑了 9,898 行：多出来的单列为额外核对，不进判定。
5. 调度与耗时：参照段从各次启动的保护日志与运行目录旁的 -attempts.log 重建；pass_done 里的 P 与秒数只描述最后一次续跑。

用法：.venv/bin/python -I experiments/s2_main_reanalyze.py [运行目录]
"""
import argparse
import concurrent.futures as cf
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import s2_main  # noqa: E402

from rewardfail.s2 import analyze, report  # noqa: E402
from rewardfail.s2.envinfo import env  # noqa: E402
from rewardfail.s2.stepguard import NoGuard, write_atomic  # noqa: E402

RUN = s2_main.RUNS / "main-20261007-202545"
OUT = ROOT / "results/s2_main/report.json"
EXEC_COMMIT = "9a88991"  # 主测量执行的版本（run.json 版本锁）
PASSES = ["default", "reference", "limit2s", "limit10s", "replay1", "replay2", "replay3", "retest"]
BUDGET = "本机预算终止（未裁定）"


def manifest(run):
    files = sorted(p for p in run.rglob("*") if p.is_file())
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(run)}" for p in files]
    return {"files": len(files), "sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest()}


def old_analyze_path(tmp):
    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{EXEC_COMMIT}:rewardfail/s2/analyze.py"], capture_output=True,
                         text=True, check=True).stdout
    p = Path(tmp) / "analyze_exec.py"
    p.write_text(src, encoding="utf-8")
    return p


def resynth(src, dst, old_path):
    """一段：复制原始记录，先用原执行版本合成（要与原 rows.jsonl 相同），再用修订后的合成。在子进程里跑。"""
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("analyze_exec", old_path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    from rewardfail.s2 import analyze as new
    src, dst = Path(src), Path(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("rows.jsonl"))
    t0 = time.time()
    old.summarize_stream(dst, dst / "rows-exec.jsonl")
    same = (dst / "rows-exec.jsonl").read_bytes() == (src / "rows.jsonl").read_bytes()
    stats = new.summarize_stream(dst, dst / "rows.jsonl")
    return {"exec_version_reproduces_rows": same, "stats": stats, "seconds": round(time.time() - t0, 1)}


def rows_by_id(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            out[r["id"]] = r
    return out


def class_changes(old_rows, new_rows):
    ch = Counter((o["class"], new_rows[i]["class"]) for i, o in old_rows.items() if o["class"] != new_rows[i]["class"])
    return {f"{a} → {b}": n for (a, b), n in ch.most_common()}


def schedule(run):
    """参照段实际派发：各次启动（保护日志 launch/launch_end）、整项停止与预算终止，另附 -attempts.log 原文。"""
    d = run / "reference"
    launches, events = [], []
    for f in sorted(d.glob("guard-reference*.jsonl")):
        for e in analyze._jsonl(f):
            if e["ev"] == "launch":
                launches.append({"log": f.name, "launch": e["launch"], "P": e["P"], "workers": e["workers"],
                                 "todo": e["todo"], "t_start": e["t"]})
            elif e["ev"] == "launch_end":
                launches[-1].update(t_end=e["t"], seconds=round(e["t"] - launches[-1]["t_start"], 1), done_after=e["done"],
                                    stopped=e["stopped"], interrupted=e["interrupted"], codes=e["codes"])
            elif e["ev"] in ("pause", "hard_stop", "budget_kill", "resume"):
                events.append(dict(e, log=f.name, time=time.strftime("%H:%M:%S", time.localtime(e["t"]))))
    launches.sort(key=lambda x: x["t_start"])
    events.sort(key=lambda e: e["t"])
    for x in launches:
        x["time"] = time.strftime("%H:%M:%S", time.localtime(x["t_start"]))
        if "t_end" not in x:  # 10-07 21:36 改用按段调度时手动停下，保护日志没有结束记录
            x["note"] = "默认段完成后、参照段刚开始时手动停下，改用 experiments/s2_main_sched.py（-attempts.log 21:36:10）"
    att = run.parent / f"{run.name}-attempts.log"
    dispatched = sum(x.get("seconds", 0) for x in launches)
    first, last = min(x["t_start"] for x in launches), max(x.get("t_end", 0) for x in launches)
    return {"launches": launches, "guard_events": events,
            "no_dispatch_attempt": "S2_REF_P=2 的一次（21:44:04）在“构建任务与生成版本锁”被准备阶段保护停下（暂停后仍内存压力警告），"
                                   "退出码 7，没有派发判分",
            "dispatched_seconds_with_end_record": round(dispatched, 1),
            "wall_seconds_first_launch_to_last_end": round(last - first, 1),
            "pass_done_P_and_seconds": "pass_done.json 的 P=1 与 1236.1 秒只描述最后一次成功续跑（S2_REF_P=1，21:44:55–22:05:31），"
                                       "不是整段配置或累计耗时",
            "attempts_log": att.read_text(encoding="utf-8").splitlines() if att.exists() else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?", default=str(RUN))
    ap.add_argument("--jobs", type=int, default=len(PASSES))
    a = ap.parse_args()
    run = Path(a.run)
    t0 = time.time()
    before = manifest(run)
    rj = json.loads((run / "run.json").read_text(encoding="utf-8"))

    # 任务与预先抽取：与版本锁 pre 逐项核对
    ns = argparse.Namespace(source="main", synthetic=False, n=0)
    tasks, meta = s2_main.build(ns, lambda: None)
    ids = [t["id"] for t in tasks]
    by_id = {t["id"]: t for t in tasks}
    draws = s2_main.make_draws(ids, meta)
    retest_ids = [i for i in ids if draws[i][0]]
    rand_lim = {i for i in ids if draws[i][1]}
    pre = {"source": "main", "n": len(ids), "ids_sha256": s2_main.digest(ids), "retest": len(retest_ids),
           "retest_sha256": s2_main.digest(retest_ids), "limits_random": len(rand_lim),
           "limits_random_sha256": s2_main.digest(sorted(rand_lim)),
           "refone_order_sha256": s2_main.digest(sorted(ids, key=lambda i: draws[i][2])), "synthetic": False,
           "child_limit_mib": 3072}
    if pre != rj["lock"]["pre"]:
        raise SystemExit(f"预先抽取与版本锁不同：{s2_main.lock_diffs(rj['lock']['pre'], pre)}")
    lock = s2_main.current_lock(pre)
    lock_diffs = [{"item": k, "run_lock": x, "now": y} for k, x, y in s2_main.lock_diffs(rj["lock"], lock)]
    if any(not d["item"].startswith("code_sha256 / ") for d in lock_diffs):
        raise SystemExit(f"代码以外的版本锁项不同，停下：{lock_diffs}")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "run"
        base.mkdir()
        old_path = old_analyze_path(tmp)
        with cf.ProcessPoolExecutor(max_workers=a.jobs) as ex:
            futs = {p: ex.submit(resynth, run / p, base / p, old_path) for p in PASSES}
            synth = {p: f.result() for p, f in futs.items()}
        bad = [p for p, s in synth.items() if not s["exec_version_reproduces_rows"]]
        if bad:
            raise SystemExit(f"原执行版本重新合成与原 rows.jsonl 不同：{bad}")
        changes, budget_rows, changed_main = {}, {}, {}
        for p in PASSES:
            o, n = rows_by_id(base / p / "rows-exec.jsonl"), rows_by_id(base / p / "rows.jsonl")
            if set(o) != set(n):
                raise SystemExit(f"{p}：修订前后合成的行不同")
            changes[p] = class_changes(o, n)
            budget_rows[p] = sorted(i for i, r in n.items() if r["class"] == BUDGET)
            changed_main[p] = sum(1 for i, r in o.items() if not i.startswith("warm-") and r["class"] != n[i]["class"])
            del o, n

        def run_pass(name, ts, mode, extra):
            spec = json.loads((run / name / "pass_spec.json").read_text(encoding="utf-8"))
            want = [t["id"] for t in ts]
            if s2_main.digest(want) == spec["ids_sha256"] and len(want) == spec["n"]:
                same = True
            else:
                ran = {r["id"] for r in analyze._jsonl(run / name / "rows.jsonl") if not r.get("warm")}
                if not set(want) <= ran or len(ran) != spec["n"]:
                    raise SystemExit(f"{name}：按修订后的规则要的行不全在原段里，不能只重新分析")
                same = False
            if spec["mode"] != mode or spec["extra"] != list(extra):
                raise SystemExit(f"{name}：段参数与原段不同")
            info = json.loads((run / name / "pass_done.json").read_text(encoding="utf-8"))
            info.update(reused=True, reanalysis={"rows_required": len(want), "rows_ran": spec["n"], "same_rows": same,
                                                 "stats": synth[name]["stats"], "class_changes": changes[name]})
            return info

        f = s2_main.followups(base, ids, by_id, draws, run_pass, lambda _label: NoGuard())
        tally, dcls, rcls, k_set = f["tally"], f["dcls"], f["rcls"], set(f["k_ids"])
        types = report.answer_types(ids, meta, k_set, set(f["u_ids"]))
        ref_ones = {"rows": len(f["ones"]), "reference_classes": dict(Counter(rcls.get(i) for i in f["ones"])),
                    "not_1": sum(1 for i in f["ones"] if report.ref_verdict(rcls.get(i)) != 1)}
        rep = f["replays"]
        # 原段按修订前的重放集合跑了 9,898 行：多出来的单列，不进判定
        ran = [r["id"] for r in analyze._jsonl(run / "replay1" / "rows.jsonl") if not r.get("warm")]
        req = set(f["rep_ids"])
        extra_ids = [i for i in ids if i in set(ran) - req]
        reps = [{r["id"]: r for r in s2_main.scan(base / f"replay{j}")} for j in (1, 2, 3)]
        rep_x = report.replays(extra_ids, dcls, reps)
        cands_x = report.candidates(extra_ids, tally.keep, reps)
        why_u = {}
        for i in f["u_ids"]:
            d = dcls.get(i)
            why_u[i] = {"default": d, "reference": rcls.get(i),
                        "reason": ("默认：" + (d or "没有记录")) if report.default_verdict(d) is None
                        else ("参照：" + (rcls.get(i) or "没有记录"))}
        out = {"what": "第二阶段主测量（10-08 只重新分析：修正本机预算终止归因，未重判；方案第 18.3 节）",
               "run_dir": str(run), "pre": pre, "lock": {k: v for k, v in rj["lock"].items() if k != "pre"},
               "reanalysis": {
                   "why": "修订前 analyze.py 按子进程 pid 与池代次把预算终止贴到这个子进程判过的所有行；修订后只记被杀时结果还没"
                          "送回父侧的尝试（analyze.returned_at，KILL_MARGIN 秒）。主样本不重判，原运行目录与版本锁只读。",
                   "execution_version": EXEC_COMMIT, "analysis_env": env(),
                   "lock_diffs_vs_run": lock_diffs,
                   "exec_version_reproduces_rows": {p: s["exec_version_reproduces_rows"] for p, s in synth.items()},
                   "class_changes_by_pass": changes, "main_rows_changed_by_pass": changed_main,
                   "budget_rows_by_pass": budget_rows,
                   "resynth_seconds": {p: s["seconds"] for p, s in synth.items()},
                   "run_dir_report_json": "运行目录里的 report.json 是 10-07 原版，没有改；旧正式版见实验仓 6c416b2"},
               "env": rj["env"], "passes": f["passes"], "main_metric": f["metric"],
               "k_ids": f["k_ids"], "u_detail": why_u, "answer_types": types,
               "default_events": {name: report.rate(tally.ev[name], len(ids)) for name, _ in report.EVENTS},
               "default_classes": dict(Counter(dcls.values())), "reference_classes": dict(Counter(rcls.values())),
               "replay_set": {"rows": len(f["rep_ids"]), "why": f["replay_why"], "ran_rows": len(ran),
                              "extra_rows": len(extra_ids),
                              "note": "按修订后的规则必需重放的行都在原段里、各有完整三次结果；原段按修订前的集合多跑的行单列在"
                                      " replays_extra，不进判定"},
               "replays": {k: v for k, v in rep.items() if k != "detail"}, "replay_detail": rep["detail"],
               "replays_extra": {**{k: v for k, v in rep_x.items() if k != "detail"},
                                 "sometimes_ids": sorted(i for i, v in rep_x["detail"].items() if not v["every_time"]),
                                 "candidates": cands_x},
               "concurrency_candidates": f["candidates"], "limits": f["limits"], "retest": f["retest"],
               "reference_check_on_default_1": ref_ones, "reference_schedule": schedule(run),
               "decision": report.decide(f["metric"], types, rep, f["candidates"])}
    after = manifest(run)
    out["reanalysis"]["source_manifest"] = {"before": before, "after": after, "unchanged": before == after}
    out["seconds"] = round(time.time() - t0, 1)
    write_atomic(OUT, json.dumps(out, ensure_ascii=False, indent=1, default=str))
    m = out["main_metric"]
    print(f"n={m['n']} k={m['k']} u={m['u']} 上界={m['upper_one_sided_95_k_plus_u']:.6g}；重放必需 {len(f['rep_ids'])}、"
          f"实跑 {len(ran)}；原件不变={before == after}；判定 {out['decision']}")


if __name__ == "__main__":
    main()
