# Primary-source literature check (3 November 2026)

This manuscript-only check starts from PR #1 head
`9a2fdd56c5844f3f01d285b5e70f98153fc22a12`. It does not rerun cited authors'
experiments or establish exhaustive priority. The GitHub PR's activity timestamp
is not evidence that its authoring session is currently running.

## Content checks that affect the manuscript

- [Cai et al., v5, Appendices A–B](https://arxiv.org/html/2510.00915v5): explicitly bridges to group centering and implements corrections in a GRPO-style pipeline. It distinguishes those results from current-group standardization and clipping. Corrected the manuscript's overly broad suggestion that its results are simply “before GRPO.”
- [Xin, verifier audit, v1, §2.3](https://arxiv.org/html/2609.01354v1): separates verdict availability from correctness and uses contract-aware metamorphic testing. Retained explicit attribution; changed the description to “separates returned verdicts from timeouts, errors and crashes,” avoiding an unsupported claim about an exact five-valued classification.
- [Xin, group correlation, v1, §§3.4–3.6 and limitations](https://arxiv.org/html/2609.06386v1): distinguishes pooled from conditional dependence and describes stratified human labels. Our manuscript already makes these distinctions and does not claim a random, independently adjudicated sample.
- [Rollout Cards, v1, Appendix B](https://arxiv.org/html/2605.12131v1): documents cross-layer failure handling in its repository audit, including exception-to-zero coercion. Retained it as direct prior art, not merely a generic reproducibility citation.
- [Plesner et al., v2](https://arxiv.org/html/2604.07666v2): bounded empirical tolerance with uncertainty and limitations of transferring advantage changes to gradients. Existing wording is appropriately limited; no new tolerance claim added.
- [iCoder, v1, §4.4.3](https://arxiv.org/html/2609.29626v1): explicitly excludes unjudgeable trajectories from group moments and loss normalization. Expanded the comparison to acknowledge this concrete prior policy; our metadata patch does not implement it.
- [Yang et al., v3](https://arxiv.org/html/2601.08521v3): characterizes conditional bias among non-degenerate groups. Existing generic attribution remains appropriate; no theorem is imported into this study.

## Metadata and abstract checks

Primary arXiv records were opened for all 21 arXiv entries below. Titles and lead authors agree with the bibliography, allowing typography differences. URLs now pin the inspected version; an abstract check is not a full-methods audit.

| Identifier | Version linked | Check depth |
|---|---:|---|
| 2411.15124 | 5 | metadata/abstract |
| 2402.03300 | 3 | metadata/abstract |
| 2501.12948 | 2 | metadata/abstract |
| 2503.14476 | 2 | metadata/abstract |
| 2409.19256 | 2 | metadata/abstract |
| 2609.01354 | 1 | relevant full-text sections |
| 2609.06386 | 1 | relevant full-text sections |
| 2510.00915 | 5 | relevant full-text sections |
| 2605.07689 | 1 | metadata/abstract |
| 2601.08521 | 3 | metadata/abstract and full-text scope |
| 2605.02909 | 2 | metadata/abstract |
| 2605.04431 | 1 | metadata/abstract |
| 2604.07666 | 2 | metadata/abstract and full-text scope |
| 2605.12131 | 1 | relevant full-text sections |
| 2609.36958 | 2 | metadata/abstract |
| 2610.02808 | 2 | metadata/abstract |
| 2609.36900 | 1 | metadata/abstract |
| 2610.02911 | 1 | metadata/abstract |
| 2606.01066 | 1 | metadata/abstract |
| 2607.11022 | 1 | metadata/abstract |
| 2609.29626 | 1 | relevant full-text sections |

Software and dataset citations remain pinned as supplied in the evidence revision.
Their code-level claims are not newly re-audited by this writing pass. Clopper–Pearson's
historical bibliographic entry is unchanged and was not separately publisher-verified.
No new reference is added solely to increase citation count.
