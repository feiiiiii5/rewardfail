# Before submitting to arXiv: author confirmations

The package (`paper/arxiv/rewardfail-arxiv-source.tar.gz`, PDF `paper/rewardfail-preprint-2026-11-03.pdf`) builds
and passes the checks in `VALIDATION_FINAL_2026-11-03.md`. The following are decisions or confirmations, not
technical checks:

1. **Responsibility — confirmed.** The author takes responsibility for the manuscript and every claim. Reading the
   final PDF once more before upload remains good practice.
2. **AI-use statement — confirmed.** The footnote states that the author selected the topic, determined the
   direction and methodology, and is responsible for the final content and all claims; AI agents (Claude and Codex)
   provided substantial assistance with implementation, experiment execution, code-based analysis, the evidence
   audit, the Linux re-executions, the offline policy analysis, and drafting and revision. This matches arXiv's
   policy that AI tools are not authors and that their use is disclosed.
3. **Authorship, affiliation and correspondence — confirmed.** Sole author *Yufeiyang Chen*; *School of Cyber
   Science and Technology, Sun Yat-sen University, Shenzhen, China*; public correspondence address
   *fei76161@gmail.com*. No co-author.
4. **Manuscript licence — confirmed: CC BY 4.0.** Choose "CC BY 4.0" in the arXiv form, matching the manuscript and
   `README.md`. Anyone may copy, redistribute, adapt and use the work commercially with attribution; the licence of a
   posted version cannot be revoked.
5. **Categories — confirmed: cs.SE primary (endorsement obtained), cs.LG cross-list; no cs.AI.** cs.SE fits the
   contribution (failure trace through a software pipeline, fault injection, regression fixtures, upstream repair);
   cs.LG fits the RLVR setting and the §8 GRPO analysis, which is not a learning result. Follow the arXiv form's
   current prompts for cross-listing; moderators may reclassify.
6. **Repository link.** The appendix cites `https://github.com/feiiiiii5/rewardfail`; the reviewed state is merged into
   `main`, and the analysis snapshot is commit `da00bd6`. `author-inputs-20261103` stays a separate, unmodified
   author archive (not merged; local folder names and a planning note are visible there, see
   `audit/AUTHOR_INPUTS_AUDIT.md`). Tagging a release is optional.
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
11. **Code licence — confirmed: Apache-2.0.** `audit/LICENSE` and `audit/NOTICE` are added. Third-party parts keep
    their own terms (verl code in patches 0001/0002, OpenR1 texts in the heavy-scene specs, the MIT human-label CSV);
    see `audit/LICENSING_PLAN.md`.
12. **Package hash.** The arXiv source package in this commit has SHA-256
    `6bccf07bca8da8707dcd7853e6c2b1b373bbfe98e1929513add2e85e042e988a`; rebuild with `make_arxiv_package.sh` after
    any edit and re-run `check_paper_numbers.py` and its counter-tests.
13. **Submission itself — not authorised yet.** The author has instructed that the paper must **not** be posted to
    arXiv for now. Nothing has been submitted, and no endorser or third party has been contacted. Upload, the final
    PDF check in the arXiv preview and the timing are the author's steps.
