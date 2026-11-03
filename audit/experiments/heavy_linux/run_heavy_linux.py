"""HL driver (see PROTOCOL.md). Writes only under --out (must not exist).

Usage: python -B run_heavy_linux.py --companion <dir> --heavy heavy_rows.json \
          --base-verl <0c4c3d4 tree> --fixed-verl <patched tree> --python <venv python> --out <new dir>
"""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HEAVY_SHA = "297c3deb7026c766f2feef7a0040c63cf6bdee41cd689fda1245da5175cedbc7"
THREE = ("m-8364284f555502b7", "m-ac45c2e3c4109182", "m-2a2cbb703cd7d47a")
MEM_FLOOR = 2 << 30
SCENE_LIMIT = 600


def mem_available():
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024


def descendants(pid):
    out, frontier = [], [pid]
    while frontier:
        p = frontier.pop()
        try:
            kids = open(f"/proc/{p}/task/{p}/children").read().split()
        except OSError:
            kids = []
        for k in map(int, kids):
            out.append(k)
            frontier.append(k)
    return out


def rss(pid):
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except OSError:
        return 0
    return 0


def run_scene(name, spec, a, tree, out):
    d = out / name
    d.mkdir(parents=True)
    spec = dict(spec, dir=str(d / "scene"), sources=str(out / "source"))
    (d / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([tree, str(a.companion)]), HOME=str(out / "home"))
    t0 = time.time()
    proc = subprocess.Popen([a.python, "-B", str(a.companion / "experiments/s2_e1.py"), "--scene", str(d / "spec.json")],
                            cwd=a.companion, env=env, stdout=open(d / "stdout.log", "w"), stderr=open(d / "stderr.log", "w"),
                            start_new_session=True)
    samples, why = [], None
    while proc.poll() is None:
        kids = descendants(proc.pid)
        avail = mem_available()
        samples.append([round(time.time() - t0, 2), avail, rss(proc.pid) + sum(rss(k) for k in kids)])
        if avail < MEM_FLOOR:
            why = "memory intervention"
        elif time.time() - t0 > SCENE_LIMIT:
            why = "timeout"
        if why:
            for k in reversed(kids):
                try:
                    os.kill(k, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            break
        time.sleep(0.5)
    res = d / "scene/result.json"
    result = json.loads(res.read_text()) if res.exists() else None
    item = {"scene": name, "tree": Path(tree).name, "exit": proc.returncode, "wall": round(time.time() - t0, 2),
            "intervention": why, "max_scene_rss_bytes": max((s[2] for s in samples), default=0),
            "min_mem_available_bytes": min((s[1] for s in samples), default=None),
            "batches": [{k: b.get(k) for k in ("name", "scores", "extras", "exception")} for b in (result or {}).get("batches", [])]}
    (d / "watchdog.json").write_text(json.dumps({"samples": samples}, indent=0))
    (d / "outcome.json").write_text(json.dumps(item, ensure_ascii=False, indent=1))
    return item


def main():
    ap = argparse.ArgumentParser()
    for k in ("companion", "heavy", "base-verl", "fixed-verl", "out"):
        ap.add_argument("--" + k, type=Path, required=True)
    ap.add_argument("--python", required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    raw = a.heavy.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HEAVY_SHA
    heavy = {r["id"]: r for r in json.loads(raw)["rows"]}
    for r in heavy.values():
        assert hashlib.sha256(r["answer"].encode()).hexdigest() == r["answer_sha256"]
        assert hashlib.sha256(r["generation"].encode()).hexdigest() == r["generation_sha256"]
    (a.out / "source").mkdir()
    src = (a.companion / "sources/main-wrapper.py").read_bytes()
    assert hashlib.sha256(src).hexdigest() == "1242011cddc041ea6cb19fc9a1872ebab742d8ae7e8ebd3342f6b3b8b6e2ba15"
    (a.out / "source/verl_main_acad987.py").write_bytes(src)
    normal = [{"id": f"ctl-{n}", "gt": str(n), "out": f"The answer is \\boxed{{{n}}}."} for n in range(2, 10)]
    warm = [{"id": f"warm-{n}", "gt": "1", "out": "\\boxed{1}"} for n in range(4)]
    three = [{"id": i, "gt": heavy[i]["answer"], "out": heavy[i]["generation"]} for i in THREE] + normal[3:]
    following = [{**r, "id": "following-" + r["id"]} for r in normal]

    def spec(wrapper, lib, manager, rows, variant):
        return dict(wrapper=wrapper, lib=lib, outer=30, observe=True, variant=variant, repeat=1, manager=manager,
                    rows=rows, warm=warm, following=following)
    plan = [("S1", spec("pr", None, "naive", normal, "normal"), "base"),
            ("S2", spec("pr", None, "naive", three, "three"), "base"),
            ("S3", spec("pr", None, "limited", three, "three"), "base"),
            ("S4", spec("main", None, "naive", three, "three"), "base"),
            ("S5a", spec("pr", 60, "naive", three, "three"), "base"),
            ("S5b", spec("pr", 60, "naive", three, "three"), "base"),
            ("S5c", spec("pr", 60, "naive", three, "three"), "base"),
            ("S6", spec("pr", 60, "limited", three, "three"), "base"),
            ("S7", spec("pr", 60, "naive", normal, "normal"), "base"),
            ("S2f", spec("pr", None, "naive", three, "three"), "fixed"),
            ("S5f", spec("pr", 60, "naive", three, "three"), "fixed")]
    (a.out / "plan.json").write_text(json.dumps([[n, s, t] for n, s, t in plan], ensure_ascii=False, indent=1))
    items, interventions = [], 0
    for name, s, t in plan:
        tree = str(a.base_verl if t == "base" else a.fixed_verl)
        print(time.strftime("%H:%M:%S"), name, t, s["wrapper"], s["lib"], s["manager"], s["variant"], flush=True)
        item = run_scene(name, s, a, tree, a.out)
        print("   ", json.dumps({k: item[k] for k in ("exit", "wall", "intervention")}), flush=True)
        items.append(item)
        interventions += item["intervention"] == "memory intervention"
        if interventions >= 2:
            print("two memory interventions: campaign stopped", flush=True)
            break
    (a.out / "summary.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
