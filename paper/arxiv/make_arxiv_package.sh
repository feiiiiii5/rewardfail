#!/usr/bin/env bash
# Build the arXiv source package from paper/ and test-compile it the way arXiv does (pdfLaTeX, shipped .bbl).
# Usage: bash paper/arxiv/make_arxiv_package.sh <output dir>
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
out=${1:?output directory}
mkdir -p "$out"
stage=$(mktemp -d)
cp "$here/main.tex" "$here/main.bbl" "$here/refs.bib" "$stage/"
# arXiv uses the .bbl; refs.bib is included for editability. No figures or other inputs are needed.
tar -C "$stage" --sort=name --owner=0 --group=0 --numeric-owner --mtime='2026-11-03 00:00Z' -czf "$out/rewardfail-arxiv-source.tar.gz" main.tex main.bbl refs.bib
test_dir=$(mktemp -d)
tar -xzf "$out/rewardfail-arxiv-source.tar.gz" -C "$test_dir"
( cd "$test_dir" && rm -f refs.bib && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null )
cp "$test_dir/main.pdf" "$out/rewardfail-arxiv-testbuild.pdf"
grep -E "^!|Warning.*undefined" "$test_dir/main.log" || true
echo "pages: $(pdfinfo "$test_dir/main.pdf" | awk '/Pages/{print $2}')"
sha256sum "$out/rewardfail-arxiv-source.tar.gz"
rm -rf "$stage" "$test_dir"
