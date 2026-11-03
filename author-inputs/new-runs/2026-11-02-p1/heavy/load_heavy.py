"""Load the four historical heavy rows into a local JSON fixture."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path("<WORKSPACE>/rewardfail")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import s2_u18_diag as diag
from rewardfail.s2 import data

OUT = Path(__file__).resolve().parent
rows = []
tasks = diag.tasks_for(list(diag.D1_IDS))
reader = data.Reader()
for tid in diag.D1_IDS:
    t = tasks[tid]
    answer, gens = reader.get(t["shard"], t["row"])
    idx = t["idx"] if t["idx"] < len(gens) else 0
    generation = gens[idx]
    rows.append({
        "id": tid,
        "shard": t["shard"],
        "row": t["row"],
        "pick": t["idx"],
        "generation_index": idx,
        "answer": answer,
        "generation": generation,
        "answer_sha256": hashlib.sha256(str(answer).encode()).hexdigest(),
        "generation_sha256": hashlib.sha256(str(generation).encode()).hexdigest(),
        "generation_chars": len(str(generation)),
        "generation_preview": str(generation)[:200],
    })
json.dump({"rows": rows}, open(OUT / "heavy_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps([{k: r[k] for k in ["id","answer","generation_chars","generation_preview"]} for r in rows], ensure_ascii=False, indent=2))
