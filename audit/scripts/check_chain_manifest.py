"""Compare new-runs/2026-11-02-chain/manifest-all.json with the delivered files (read-only).

For every manifest entry: present / missing; if present, whether SHA-256 and size match.
For mismatches it tests one specific explanation only: that the delivered file equals the
original with absolute paths replaced by placeholders. Because the pre-redaction bytes are
not delivered, that explanation is reported as "consistent" only when (a) the delivered text
contains a redaction placeholder and (b) the size difference is non-zero; otherwise
"unexplained". It never edits the manifest.

Usage: python3 -I check_chain_manifest.py <chain dir>
"""
import hashlib
import json
import re
import sys
from pathlib import Path

PH = re.compile(r"<(WORKSPACE|REWARDfail_LOCAL|LOCAL_USER|REDACTED_TOKEN|EMAIL|PHONE)>|\b(WORKSPACE|REWARDfail_LOCAL|LOCAL_USER)\b")

root = Path(sys.argv[1])
m = json.loads((root / "manifest-all.json").read_text(encoding="utf-8"))
rows = []
for rel, meta in sorted(m.items()):
    p = root / rel
    want_sha = meta.get("sha256")
    want_n = meta.get("bytes", meta.get("size"))
    if not p.is_file():
        rows.append({"path": rel, "status": "missing", "manifest_bytes": want_n})
        continue
    b = p.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    if sha == want_sha and (want_n is None or len(b) == want_n):
        rows.append({"path": rel, "status": "match"})
        continue
    if rel == "manifest-all.json":
        rows.append({"path": rel, "status": "self-reference (a manifest cannot contain its own final hash)",
                     "manifest_bytes": want_n, "delivered_bytes": len(b)})
        continue
    txt = b.decode("utf-8", "replace")
    hits = sorted(set(x.group(0) for x in PH.finditer(txt)))
    rows.append({"path": rel, "status": "differs", "manifest_bytes": want_n, "delivered_bytes": len(b),
                 "placeholders_in_delivered": hits,
                 "explanation": "consistent with path redaction (not proven: original bytes not delivered)"
                 if hits and want_n != len(b) else "unexplained"})
summary = {}
for r in rows:
    summary[r["status"]] = summary.get(r["status"], 0) + 1
print(json.dumps({"entries": len(rows), "summary": summary, "rows": [r for r in rows if r["status"] != "match"]},
                 ensure_ascii=False, indent=1))
