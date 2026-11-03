"""Structural comparison of two JSON reports that went through different path redactions.

Leaves are compared after walking both trees. A differing string pair is classed
"path-only" if, after replacing every known placeholder/prefix with a single token,
the strings become identical; otherwise it is "content". Non-string differences
(numbers, booleans, list lengths, keys) are always "content". A string whose
difference involves a <PHONE>/<EMAIL>/token placeholder is reported separately
as a "redaction artifact" (the redactor replaced content, e.g. part of a hash). Nothing is assumed
about the cause of a content difference. stdlib only; run with python3 -I.

Usage: compare_redacted_json.py A.json B.json [--show N]
"""
import json
import re
import sys

PLACEHOLDERS = re.compile(r"(<[A-Za-z0-9_]+>|WORKSPACE|REWARDfail_LOCAL|LOCAL_USER|/Users/[^/\"']+|~)")
REDACTION_MARKS = ("<PHONE>", "<EMAIL>", "REDACTED_TOKEN", "<REDACTED_TOKEN>")


def norm(s):
    s = PLACEHOLDERS.sub("@P@", s)
    s = re.sub(r"@P@(/Desktop/[^/]+/[^/]+/[^/]+)?", "@P@", s)  # author copies keep a local folder chain
    s = re.sub(r"@P@/stage2/", "@P@/", s)
    s = re.sub(r"(@P@/?)+", "@P@/", s)
    # collapse any remaining path prefix before a known relative tail
    s = re.sub(r"@P@/[^\s\"']*?/(stage2|rewardfail|runs|results|experiments|third_party|data|\.local)/", r"@P@/\1/", s)
    return s


def walk(a, b, path, out):
    if type(a) is not type(b):
        out["content"].append((path, a, b)); return
    if isinstance(a, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                out["content"].append((path + "/" + str(k), a.get(k, "<absent>"), b.get(k, "<absent>")))
            else:
                walk(a[k], b[k], path + "/" + str(k), out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out["content"].append((path + "[len]", len(a), len(b))); return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out)
    elif a != b:
        if isinstance(a, str) and norm(a) == norm(b):
            out["path_only"].append((path, a, b))
        elif isinstance(a, str) and isinstance(b, str) and any(m in a + b for m in REDACTION_MARKS):
            out["redaction_artifact"].append((path, a, b))
        else:
            out["content"].append((path, a, b))


def main():
    a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
    show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 10
    out = {"path_only": [], "content": [], "redaction_artifact": []}
    walk(a, b, "", out)
    print(json.dumps({"path_only_differences": len(out["path_only"]), "content_differences": len(out["content"]),
                      "redaction_artifacts": [[p, str(x)[:120], str(y)[:120]] for p, x, y in out["redaction_artifact"]],
                      "content_examples": [[p, str(x)[:160], str(y)[:160]] for p, x, y in out["content"][:show]],
                      "path_only_examples": [[p, str(x)[:120], str(y)[:120]] for p, x, y in out["path_only"][:3]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
