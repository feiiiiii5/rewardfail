# Building the manuscript

```bash
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The author's header names `tectonic -X compile main.tex`; tectonic was not available in the checking
environment, so pdfLaTeX (TeX Live 2023, Ubuntu 24.04 packages `texlive-latex-recommended
texlive-latex-extra texlive-fonts-recommended lmodern`) with BibTeX/`plainnat` was used.

## arXiv package

```bash
bash paper/arxiv/make_arxiv_package.sh <output dir>
```

builds `rewardfail-arxiv-source.tar.gz` (`main.tex`, `main.bbl`, `refs.bib`) and test-compiles it from a clean
directory with pdfLaTeX and the shipped `.bbl`, as arXiv does. The committed package and PDF
(`paper/rewardfail-preprint-2026-11-03.pdf`, 23 pages) were checked as recorded in `VALIDATION_FINAL_2026-11-03.md`.
Earlier builds are kept in `paper/superseded/`.
