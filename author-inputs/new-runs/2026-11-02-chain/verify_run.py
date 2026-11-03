"""Read-only verification of the 2026-11-02 thesis experiment.

Checks the recorded case.json files against the pre-declared expectations,
verifies export readback and ledger evidence, records the two preserved
generation-path failures, and writes verification.json / verification.md /
summary-all.json / manifest-all.json. It never edits a raw case record.
"""
import hashlib
import json
import os
import subprocess

CHAIN = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(CHAIN, "run-01")
FAIL = os.path.join(RUN, "failures")
ROOT = os.path.dirname(os.path.dirname(CHAIN))  # 毕业设计
REWARD = os.path.join(ROOT, "rewardfail")
UNION = os.path.join(ROOT, "thesis-runs", "verl-pr8015-unionfill")
ORIG = os.path.join(ROOT, "thesis-runs", "verl-pr8015-original")
FIXED_AST = "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325"
ORIG_AST = "afb5d6c40caf9f3992726c9dacfc8d6ba8ff83c0f581fa3af543cc37e03e54fc"
ROWS_SHA = "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719"

EXPECTED = {
    "C0": {"scores": [1, 0, 1, 0, 1, 0, 1, 1], "rows": 8, "fail": []},
    "C1": {"scores": [0, 0, 1, 0, 1, 0, 1, 1], "rows": 8, "fail": [0]},
    "C2": {"scores": [1, 0, 0, 0, 1, 0, 1, 1], "rows": 8, "fail": [2]},
    "C3": {"scores": [0] * 8, "rows": 8, "fail": list(range(8))},
    "C4": {"scores": [1, 0, 1, 0, 1, 0, 0, 1], "rows": 8, "fail": [6]},
    "C5": {"scores": [1, 0, 1, 0, 1, 0, 0], "rows": 7, "fail": [6]},
    "C6": {"scores": [0, 1, 0, 0, 1, 0, 1, 1], "rows": 8, "fail": [2]},
    "C1r": {"scores": [0, 0, 1, 0, 1, 0, 1, 1], "rows": 8, "fail": [0]},
    "C2r": {"scores": [1, 0, 0, 0, 1, 0, 1, 1], "rows": 8, "fail": [2]},
}
ORIG_EXPECTED = {
    "O4": {"scores": [1, 0, 1, 0, 1, 0, 0, 1], "rows": 8, "fail": [6]},
    "O5": {"scores": [1, 0, 1, 0, 1, 0, 0], "rows": 7, "fail": [6]},
    "O6": {"aborted": True, "raise": "verl/experimental/reward_loop/reward_loop.py:369", "fail": [2]},
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(args, cwd):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True, text=True)
    return p.stdout.strip()


def load(case, base=RUN):
    p = os.path.join(base, case, "case.json")
    if not os.path.exists(p):
        return None, p
    return json.load(open(p, encoding="utf-8")), p


def check(checks, name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})


def main():
    checks = []
    records = {}
    for case in list(EXPECTED) + list(ORIG_EXPECTED):
        rec, path = load(case)
        records[case] = rec
        check(checks, f"{case}: case.json exists", rec is not None, path)
        if rec is None:
            continue
        exp = EXPECTED.get(case) or ORIG_EXPECTED.get(case)
        is_fixed = case in EXPECTED
        mode = "fixed" if is_fixed else "original"
        check(checks, f"{case}: mode", rec.get("mode") == mode, rec.get("mode"))
        env = rec.get("environment") or {}
        want_dir = UNION if is_fixed else ORIG
        want_ast = FIXED_AST if is_fixed else ORIG_AST
        check(checks, f"{case}: imported verl under intended copy",
              str(env.get("verl_file", "")).startswith(want_dir + os.sep), env.get("verl_file"))
        check(checks, f"{case}: reward_loop under intended copy",
              str(env.get("reward_loop_file", "")).startswith(want_dir + os.sep), env.get("reward_loop_file"))
        check(checks, f"{case}: compute_rm_score AST hash", env.get("compute_rm_score_ast_sha256") == want_ast,
              env.get("compute_rm_score_ast_sha256"))
        check(checks, f"{case}: ROWS hash matches historical", env.get("rows_match_historical") is True,
              env.get("rows_sha256"))
        check(checks, f"{case}: pinned third_party clean", env.get("pinned_third_party_status") == "",
              env.get("pinned_third_party_status"))
        if is_fixed:
            check(checks, f"{case}: completed", rec.get("outcome") == "completed", rec.get("outcome"))
            check(checks, f"{case}: row count", rec.get("n_rows") == exp["rows"], rec.get("n_rows"))
            check(checks, f"{case}: scores match expected", rec.get("scores_match_expected") is True,
                  rec.get("row_scores"))
            check(checks, f"{case}: expected score vector", rec.get("row_scores") == [float(x) for x in exp["scores"]],
                  rec.get("row_scores"))
            check(checks, f"{case}: error set matches expected",
                  rec.get("error_set_matches_expected") is True, rec.get("error_original_ids"))
            check(checks, f"{case}: error column present" if exp["fail"] else f"{case}: no false error column",
                  (rec.get("error_column_present") is True) if exp["fail"] else (not rec.get("error_original_ids")),
                  rec.get("error_column_present"))
            ledger = rec.get("ledger", {}).get("counts", {})
            fail_ids = [str(x) for x in exp["fail"]]
            nonfail = [k for k in ledger if k not in fail_ids]
            check(checks, f"{case}: every planned failure has ledger >=1",
                  all(int(ledger.get(x, 0)) >= 1 for x in fail_ids), ledger)
            check(checks, f"{case}: no ledger for non-failing rows", nonfail == [], nonfail)
            ex = rec.get("export") or {}
            rb = ex.get("readback") or {}
            wl = ex.get("wronglen_check") or {}
            check(checks, f"{case}: export line count", rb.get("n_lines") == exp["rows"], rb.get("n_lines"))
            check(checks, f"{case}: export scores equal", rb.get("scores_equal") is True, rb.get("scores_equal"))
            check(checks, f"{case}: export inputs equal", rb.get("inputs_equal") is True, rb.get("inputs_equal"))
            check(checks, f"{case}: export outputs equal", rb.get("outputs_equal") is True, rb.get("outputs_equal"))
            check(checks, f"{case}: export gts equal", rb.get("gts_equal") is True, rb.get("gts_equal"))
            check(checks, f"{case}: export error values equal", rb.get("error_values_equal") is True, rb.get("error_values_equal"))
            check(checks, f"{case}: wrong-length column ignored", wl.get("wrong_len_absent") is True, wl.get("wrong_len_absent"))
        else:
            exp = ORIG_EXPECTED[case]
            if exp.get("aborted"):
                check(checks, f"{case}: aborted as expected", rec.get("outcome") == "aborted", rec.get("outcome"))
                check(checks, f"{case}: raise site", rec.get("raise_site") == exp["raise"], rec.get("raise_site"))
                ledger = rec.get("ledger", {}).get("counts", {})
                check(checks, f"{case}: injection ledger present", int(ledger.get(str(exp["fail"][0]), 0)) >= 1, ledger)
            else:
                check(checks, f"{case}: completed", rec.get("outcome") == "completed", rec.get("outcome"))
                check(checks, f"{case}: row count", rec.get("n_rows") == exp["rows"], rec.get("n_rows"))
                check(checks, f"{case}: scores match pre-run inference",
                      rec.get("row_scores") == [float(x) for x in exp["scores"]], rec.get("row_scores"))
                check(checks, f"{case}: error flag lost in original", rec.get("error_original_ids") == [],
                      rec.get("error_original_ids"))
                ledger = rec.get("ledger", {}).get("counts", {})
                check(checks, f"{case}: injection ledger present", int(ledger.get(str(exp["fail"][0]), 0)) >= 1, ledger)
                ex = rec.get("export") or {}
                rb = ex.get("readback") or {}
                check(checks, f"{case}: export readback", rb.get("scores_equal") is True and rb.get("n_lines") == exp["rows"], rb.get("n_lines"))
    # restart equality
    for first, restart in (("C1", "C1r"), ("C2", "C2r")):
        a, b = records.get(first), records.get(restart)
        if a and b:
            check(checks, f"{restart}: scores equal to {first}", a.get("row_scores") == b.get("row_scores"),
                  {"first": a.get("row_scores"), "restart": b.get("row_scores")})
            check(checks, f"{restart}: error ids equal to {first}", a.get("error_original_ids") == b.get("error_original_ids"),
                  {"first": a.get("error_original_ids"), "restart": b.get("error_original_ids")})
            check(checks, f"{restart}: export equal to {first}",
                  (a.get("export", {}).get("readback", {}).get("n_lines") == b.get("export", {}).get("readback", {}).get("n_lines")
                   and b.get("export", {}).get("readback", {}).get("scores_equal") is True),
                  {"first": a.get("export", {}).get("readback", {}).get("n_lines"),
                   "restart": b.get("export", {}).get("readback", {}).get("n_lines")})
    # preserved generation-path failures
    for case in ("O5", "C5"):
        path = os.path.join(FAIL + f"/{case}-two-agent-workers", "case.json")
        rec = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None
        check(checks, f"{case} first attempt: preserved", rec is not None, path)
        if rec:
            check(checks, f"{case} first attempt: aborted at generation",
                  rec.get("outcome") == "aborted" and rec.get("exception_type") == "AssertionError"
                  and rec.get("raise_site") == "verl/protocol.py:871"
                  and "7 and chunk 2" in str(rec.get("exception_message")),
                  {"outcome": rec.get("outcome"), "raise": rec.get("raise_site"),
                   "message": str(rec.get("exception_message"))[:160]})
    # driver hash metadata (C0-C4 ran before the 7-row adaptation)
    driver_hashes = {}
    for case, rec in records.items():
        if rec:
            h = (rec.get("environment") or {}).get("code_sha256", {}).get("experiments/thesis_chain.py")
            driver_hashes.setdefault(h, []).append(case)
    check(checks, "driver hash recorded for all cases", all(k for k in driver_hashes), driver_hashes)
    # workspace untouched except new driver + .DS_Store
    status = git(["status", "--porcelain"], REWARD).splitlines()
    allowed = {"?? .DS_Store", "?? experiments/thesis_chain.py"}
    check(checks, "rewardfail workspace unchanged except new driver",
          set(x.strip() for x in status) <= allowed, status)
    check(checks, "pinned third_party clean",
          git(["status", "--porcelain"], os.path.join(REWARD, "third_party", "verl-pr8015")) == "", "")
    check(checks, "original copy reward_loop hash",
          sha(os.path.join(ORIG, "verl/experimental/reward_loop/reward_loop.py"))
          == "f30932e2445ab01ca7fa4fbcec13910c85bfaf2cd8a4f49d040f15d7fe2ed973", "")
    check(checks, "unionfill copy AST hash",
          json.load(open(os.path.join(CHAIN, "env", "preflight_source.json"), encoding="utf-8")).get("ast_match") is True, "")

    summary = {
        "run": "2026-11-02-chain",
        "run_dir": RUN,
        "checked_at": __import__("time").strftime("%Y-%m-%d %H:%M:%S %z"),
        "cases": [],
        "failures_preserved": ["run-01/failures/O5-two-agent-workers", "run-01/failures/C5-two-agent-workers"],
        "checks": checks,
        "n_checks": len(checks),
        "n_fail": sum(1 for c in checks if not c["pass"]),
        "driver_hashes": driver_hashes,
        "records": {k: {kk: v.get(kk) for kk in ["case", "mode", "outcome", "agent_workers", "row_scores",
                                                 "error_original_ids", "seconds", "started", "finished"]}
                    for k, v in records.items() if v},
    }
    json.dump(summary, open(os.path.join(RUN, "verification.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    lines = ["# 2026-11-02 真实链路实验核对", "",
             f"- 检查项：{len(checks)}，失败：{summary['n_fail']}",
             f"- 记录目录：{RUN}",
             "- 两次 7 行首次尝试（2 个 agent worker）在生成阶段中止，原样保留在 failures/。", ""]
    lines.append("| 检查 | 结果 | 证据 |")
    lines.append("| --- | --- | --- |")
    for c in checks:
        lines.append(f"| {c['check']} | {'通过' if c['pass'] else '未通过'} | {json.dumps(c['detail'], ensure_ascii=False)[:300]} |")
    open(os.path.join(RUN, "verification.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    # manifest of every file under chain, plus the two source copies' key file
    manifest = {}
    for dirpath, _, filenames in os.walk(CHAIN):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            manifest[os.path.relpath(p, CHAIN)] = {"sha256": sha(p), "bytes": os.path.getsize(p)}
    for label, p in (("verl-pr8015-original/reward_loop.py", os.path.join(ORIG, "verl/experimental/reward_loop/reward_loop.py")),
                     ("verl-pr8015-unionfill/reward_loop.py", os.path.join(UNION, "verl/experimental/reward_loop/reward_loop.py")),
                     ("driver/thesis_chain.py", os.path.join(REWARD, "experiments/thesis_chain.py")),
                     ("driver/c1c_chain.py", os.path.join(REWARD, "experiments/c1c_chain.py")),
                     ("driver/inject.py", os.path.join(REWARD, "rewardfail/inject.py")),
                     ("driver/reward_fn.py", os.path.join(REWARD, "rewardfail/reward_fn.py")),
                     ("driver/fixed_agent_loop.py", os.path.join(REWARD, "rewardfail/fixed_agent_loop.py"))):
        manifest[label] = {"sha256": sha(p), "bytes": os.path.getsize(p)}
    json.dump(manifest, open(os.path.join(CHAIN, "manifest-all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({"n_checks": len(checks), "n_fail": summary["n_fail"],
                      "driver_hashes": driver_hashes, "manifest_files": len(manifest)}, ensure_ascii=False, indent=1))
    return 0 if summary["n_fail"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
