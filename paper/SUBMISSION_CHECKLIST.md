# Before submitting to arXiv: items only the author can confirm

The package (`paper/arxiv/rewardfail-arxiv-source.tar.gz`, PDF `paper/rewardfail-preprint-2026-11-03.pdf`) builds
and passes the checks in `VALIDATION_FINAL_2026-11-03.md`. The following are decisions or confirmations, not
technical checks:

1. **Read the whole manuscript.** It was revised with AI assistance (Claude, Codex) and has not been reviewed by
   the author in this form. The author is responsible for every claim.
2. **AI-use statement.** The footnote keeps the original contribution statement and adds that AI agents assisted
   with the evidence audit, Linux re-executions, the offline policy analysis and this revision. Confirm wording and
   that it satisfies arXiv's and the institution's policies.
3. **Affiliation and correspondence.** Confirm that listing Sun Yat-sen University (School of Cyber Science and
   Technology) is appropriate for an independent preprint, and that the e-mail address may be public.
4. **Licence.** The manuscript states CC BY 4.0; choose the same licence in the arXiv form, or change both.
5. **Category and endorsement.** Likely cs.LG (cross-list cs.SE); first-time submitters usually need an endorsement.
6. **Repository link.** The appendix cites `https://github.com/feiiiiii5/rewardfail`. Before submission, decide which
   branch readers should see, merge or tag the reviewed state, and decide what happens to the public
   `author-inputs-20261103` branch (local folder names and a planning note are visible there; see
   `audit/AUTHOR_INPUTS_AUDIT.md`).
7. **Report-only result.** `u = 18` (and the 1–19 range, the 2.97e-4 bound, and the pooled 32/34 endpoints) rest on
   the formal report; the supplied pre-correction rows reproduce `k = 1` and `u = 9,573` but not the correction.
   Accept this framing, or supply the reference-pass event files (`audit/MAIN_METRIC.md`) so it can be rebuilt.
8. **Citations.** The 21 arXiv entries were checked against primary records in the Codex pass
   (`LITERATURE_CHECK.md`); this environment could not reach arXiv to repeat it. GitHub and pinned-commit references
   were checked here (`CHANGES.md`). Spot-check any you rely on heavily.
9. **Offline policy analysis.** New in this version (§8.2). It uses the public MIT-licensed label CSV and synthetic
   failures; confirm you are comfortable presenting it as a mechanism analysis, not a training result. Its
   numbers are now generated from and checked against the result files; your independent re-run of the 2,000-draw
   statistics matched, and the real-verl estimator cross-check was run in this environment.
10. **Thesis consistency.** The Chinese thesis has known mismatches with these results (`audit/THESIS_REVIEW.md`);
    keep the two documents consistent in numbers and in what each claims.
