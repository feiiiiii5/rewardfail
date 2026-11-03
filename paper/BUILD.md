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

Checks on the committed build (`main-revised-2026-11-03.pdf`, 2026-11-03): no LaTeX errors; no undefined
references or citations; no BibTeX warnings; no overfull boxes; 21 A4 pages; the pages with new tables and
paragraphs were rendered and inspected. PDF metadata contains only title, author, keywords and producer.
