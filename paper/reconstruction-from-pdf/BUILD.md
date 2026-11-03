# Building the reconstructed manuscript

Source: `main.tex` (reconstructed from the public PDF; see `CHANGES.md`) and
`e3_linux_paragraph.tex` (generated text for §5.7, included with `\input`).

Requirements (tested 2026-11-03 on Ubuntu 24.04, TeX Live 2023 from apt):
`texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended lmodern latexmk`.

```bash
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Output: `main.pdf`; the committed copy is `paper/paper-revised-2026-11-03.pdf`. The public
`paper.pdf` at the repository root is the unchanged 12 October version.

Checks performed on the committed build: no LaTeX errors; no undefined references or
citations; zero overfull boxes; every page rendered and inspected at 70 dpi; 22 A4 pages. Remaining warnings are underfull lines caused by long URLs in the bibliography.
