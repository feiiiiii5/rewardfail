# Before submitting to arXiv: items only the author can confirm

The package (`paper/arxiv/rewardfail-arxiv-source.tar.gz`, PDF `paper/rewardfail-preprint-2026-11-03.pdf`) builds
and passes the checks in `VALIDATION_FINAL_2026-11-03.md`. The following are decisions or confirmations, not
technical checks:

1. **Read the whole manuscript.** It was revised with AI assistance (Claude, Codex) and has not been reviewed by
   the author in this form. The author is responsible for every claim.
2. **AI-use statement.** The footnote (condensed in the release pass, same facts) reads: the author selected the
   topic, determined the direction and methodology, and is responsible for the final content and all claims; AI
   agents (Claude and Codex) provided substantial assistance with implementation, experiment execution, code-based
   analysis, the evidence audit, the Linux re-executions, the offline policy analysis, and drafting and revision.
   Confirm the wording and that it satisfies arXiv's and the institution's policies.
3. **Authorship, affiliation and correspondence.** As checked in the source and the PDF metadata: sole author
   *Yufeiyang Chen*; *School of Cyber Science and Technology, Sun Yat-sen University, Shenzhen, China*; correspondence
   *fei76161@gmail.com*. No co-author is listed. Confirm the affiliation is appropriate for this preprint and that
   the e-mail address may be public (it is visible in the PDF, the source package and the repository).
4. **Manuscript licence (proposal, not yet confirmed).** The manuscript text and `README.md` currently state
   CC BY 4.0. Under CC BY 4.0 anyone may copy, redistribute, translate, adapt and use the work **commercially**,
   provided they give attribution, link the licence and indicate changes. A licence granted with a posted arXiv
   version cannot be revoked: that version and copies already made keep its terms even if a later version uses a
   different licence (check arXiv's current licence policy before changing it). If you choose another arXiv licence (e.g. the arXiv
   non-exclusive distribution licence, or CC BY-NC/ND variants), change the sentence at the end of the
   reproducibility appendix of `paper/main.tex` and the README, rebuild the PDF and the package
   (`paper/BUILD.md`), and pick the same option in the arXiv form.
5. **Category (author decides).** An endorsement for **cs.SE** has been obtained. Assessment against the content:
   - **cs.SE (primary, recommended):** the contribution is a failure trace through a software pipeline (wrapper,
     manager, batch assembly, trainer), controlled fault injection, regression fixtures, a ported upstream repair and
     a validation-accumulation patch: software reliability and testing of ML infrastructure.
   - **cs.LG (cross-list, recommended):** the setting is RLVR training, and §8 analyses how failure handling
     changes GRPO advantages. The paper does not claim a learning result, so cs.LG is a secondary audience, not the
     primary contribution.
   - **cs.AI (optional, weaker fit):** the subject is LLM reasoning verification, but there is no new AI method,
     reasoning result or agent study; adding cs.AI is defensible only as a further audience and is not needed.
   This file does not infer endorsement status for any category other than cs.SE; check the arXiv form's current
   requirements yourself. Moderators may reclassify.
6. **Repository link.** The appendix cites `https://github.com/feiiiiii5/rewardfail`; the reviewed state is merged into
   `main`, and the analysis snapshot is commit `da00bd6`. Decide whether to tag a release, and what happens to the
   public `author-inputs-20261103` branch (an author archive with old drafts, thesis material and raw data; local
   folder names and a planning note are visible there; see `audit/AUTHOR_INPUTS_AUDIT.md`). It was not merged into
   `main` and was not modified.
7. **Report-only result.** `u = 18` (and the 1–19 range, the 2.97e-4 bound, and the pooled 32/34 endpoints) rest on
   the formal report; the supplied pre-correction rows reproduce `k = 1` and `u = 9,573` but not the correction.
   Accept this framing, or supply the reference-pass event files (`audit/MAIN_METRIC.md`) so it can be rebuilt.
8. **Citations.** The 21 arXiv entries were checked against primary records in the Codex pass
   (`LITERATURE_CHECK.md`); this environment could not reach arXiv to repeat it. GitHub and pinned-commit references
   were checked here (`CHANGES.md`). Spot-check any you rely on heavily.
9. **Offline policy analysis.** New in this version (§8.2). It uses the public MIT-licensed label CSV and synthetic
   failures; confirm you are comfortable presenting it as a mechanism analysis, not a training result. Its
   numbers are now generated from and checked against the result files. Your independent recheck (original label
   CSV, 72 complete groups, 720 means and Monte Carlo standard errors, max difference about 1.11e-16) is yours and
   was not repeated here; the real-verl estimator cross-check was run in this environment.
10. **Thesis consistency.** The Chinese thesis has known mismatches with these results (`audit/THESIS_REVIEW.md`);
    keep the two documents consistent in numbers and in what each claims.
11. **Code licence (proposal, not yet confirmed).** Files under `audit/` currently carry no licence. The proposal in
    `audit/LICENSING_PLAN.md` is Apache-2.0 for the author-licensable code (as for the companion), with a NOTICE
    that keeps third-party terms: patch 0001 (verl PR #7151, keepkeen) and verl context in patch 0002 under verl's
    Apache-2.0, OpenR1 texts in the heavy-scene specs under the dataset's Apache-2.0, and the MIT human-label CSV
    cited, not relicensed. Add `audit/LICENSE` and `audit/NOTICE` only after deciding.
12. **Package hash.** The arXiv source package in the release commit has SHA-256
    `fc21849fc106ea8f033423be63a44b65830be2d6a8f0b9bddef4f5ea3d1fff27`; rebuild with `make_arxiv_package.sh` after
    any edit and re-run `check_paper_numbers.py` and its counter-tests.
13. **Submission itself.** Nothing has been submitted to arXiv, and no endorser or third party has been contacted
    from this repository's work. Upload, category, licence and the final PDF check in the arXiv preview are the
    author's steps.
