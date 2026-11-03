"""Extract a ZIP only if no entry is absolute, contains .., a backslash, a drive prefix or a symlink.

Usage: python3 -I safe_unzip.py <archive.zip> <new empty directory>
"""
import sys, zipfile, os, stat, hashlib
zp, out = sys.argv[1], sys.argv[2]
out = os.path.realpath(out)
bad = []
with zipfile.ZipFile(zp) as z:
    infos = z.infolist()
    for i in infos:
        n = i.filename
        mode = (i.external_attr >> 16)
        if n.startswith('/') or '..' in n.split('/') or '\\' in n or ':' in n.split('/')[0] or stat.S_ISLNK(mode):
            bad.append(n)
        dest = os.path.realpath(os.path.join(out, n))
        if not dest.startswith(out + os.sep) and dest != out:
            bad.append(n)
    if bad:
        print("UNSAFE", bad); sys.exit(2)
    tot = sum(i.file_size for i in infos)
    print("entries", len(infos), "uncompressed bytes", tot, "testzip", z.testzip())
    z.extractall(out)
