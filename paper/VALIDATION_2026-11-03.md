> Superseded by `VALIDATION_FINAL_2026-11-03.md`; this record describes the intermediate 21-page build now at `paper/superseded/main-preprint-review-2026-11-03.pdf`.

# Integrated manuscript validation

Based on PR #1 `9a2fdd56c5844f3f01d285b5e70f98153fc22a12`, with the independent
manuscript-clarity and population-scope patches integrated locally. No remote
branch was changed during local validation. Original `paper.pdf`, original revised PDF, companion ZIP,
and historical result files were left unchanged.

## Passed

- `python3 -I -B audit/scripts/test_recount_main_prefix.py`: 7 tests passed.
- `git diff 9a2fdd5 --check`: passed.
- pdfLaTeX, BibTeX, pdfLaTeX, pdfLaTeX: 21-page A4 PDF, no errors, undefined
  citations/references, BibTeX warnings, overfull or underfull boxes in final logs.
- Rendered all 21 pages with Poppler and inspected three contact sheets: no
  clipping, overlapping elements, blank pages or broken table layout observed.
- Primary-source citation checks: `LITERATURE_CHECK.md`; all 21 arXiv links pinned.

Build product: `main-preprint-review-2026-11-03.pdf`. The committed `main.bbl`
is refreshed to match the versioned bibliography.

## Not newly executed in this writing/integration pass

No new corpus scoring, training, injection suite, or heavy-input experiment was
run. Their evidence remains the original/re-executed outputs documented in
`audit/`. The separate population-scope patch includes a raw-row recount output;
this pass reran its seven unit tests, not its private-input recount command.
Corrected `u=18` remains report-only.

## Local TeX runtime recovery

This environment had LaTeX packages but no working format/font-map cache. The
normal build initially failed. The following cache-only setup, under `/tmp`,
was used without changing the manuscript's fonts or writing system directories:

```bash
mkdir -p /tmp/rewardfail-paper-build /tmp/rewardfail-texmf-var /tmp/rewardfail-texmf-config
export TEXMF='{/usr/share/texlive/texmf-dist,/usr/share/texmf,/var/lib/texmf,/etc/texmf}'
export TEXMFVAR=/tmp/rewardfail-texmf-var TEXMFCONFIG=/tmp/rewardfail-texmf-config
cd /tmp/rewardfail-paper-build
pdftex -ini -etex -jobname=pdflatex -interaction=nonstopmode '\input pdflatex.ini'
cat /usr/share/texmf/fonts/map/dvips/lm/lm.map \
    /usr/share/texlive/texmf-dist/fonts/map/dvips/amsfonts/cm.map \
    /usr/share/texlive/texmf-dist/fonts/map/dvips/amsfonts/cmextra.map > pdftex.map
export TEXFORMATS=/tmp/rewardfail-paper-build: TEXFONTMAPS=/tmp/rewardfail-paper-build:
cd /workspace/shared/rewardfail-paper/paper
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/rewardfail-paper-build main.tex
cd /tmp/rewardfail-paper-build
BIBINPUTS=/workspace/shared/rewardfail-paper/paper: bibtex main
cd /workspace/shared/rewardfail-paper/paper
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/rewardfail-paper-build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/rewardfail-paper-build main.tex
```

On a fully configured TeX installation, the ordinary commands in `BUILD.md`
suffice; this local cache setup is not a dependency change.
