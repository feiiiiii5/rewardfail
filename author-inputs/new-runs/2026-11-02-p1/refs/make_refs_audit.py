import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
arxiv = {
    "2501.12948": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
    "2402.03300": "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models",
    "2411.15124": "Tulu 3: Pushing Frontiers in Open Language Model Post-Training",
    "2503.14476": "DAPO: An Open-Source LLM Reinforcement Learning System at Scale",
    "2409.19256": "HybridFlow: A Flexible and Efficient RLHF Framework",
    "2510.00915": "Reinforcement Learning with Verifiable yet Noisy Rewards under Imperfect Verifiers",
    "2609.01354": "Where the Verifier Fails: A Category-Level Audit of Reward Signals in RLVR",
    "2609.06386": "Are Verifier Errors Independent Within a GRPO Group? Evidence from Qwen2.5 Rollouts",
    "2605.07689": "Gradient Starvation in Binary-Reward GRPO: Why Group-Mean Centering Fails and Why the Simplest Fix Works",
    "2601.08521": "Your Group-Relative Advantage Is Biased",
    "2605.02909": "Delay, Plateau, or Collapse: Evaluating the Impact of Systematic Verification Error on RLVR",
    "2605.04431": "Towards Robust LLM Post-Training: Automatic Failure Management for Reinforcement Fine-Tuning",
    "2604.07666": "An Imperfect Verifier is Good Enough: Learning with Noisy Rewards",
    "2605.12131": "Rollout Cards: A Reproducibility Standard for Agent Research",
    "2609.36958": "VStress: Correlation-Aware Auditing and Adaptive Budget Allocation for Repeated Verifiers",
    "2610.02808": "ROUTEAUDIT: Interaction-Aware Identification for Budgeted Multi-Verifier Routing",
    "2609.36900": "STAR-GRPO: Canonical Anchoring and Reliability-First Advantages against Representation-Dependent Reward Hacking",
    "2610.02911": "Probe the Harness: Setup Checks for Stale-Data RL Comparisons in Language Models",
    "2606.01066": "Before the Model Learns the Bug: Fuzzing RLVR Verifiers",
    "2607.11022": "When the Reward Suite Is Leaky: A Preregistered Causal Contrast of Natural Verifier False Positives in RLVR",
}
github = {
    "mathverify": ("https://github.com/huggingface/Math-Verify", "GitHub - huggingface/Math-Verify"),
    "verl8015": ("https://github.com/verl-project/verl/pull/8015", "[reward] fix: recover from broken/stuck worker pool in math_verify compute_score"),
    "verl6545": ("https://github.com/verl-project/verl/pull/6545", "[reward] fix: union reward_extra_info keys across samples in compute_rm_score"),
    "verl7151": ("https://github.com/verl-project/verl/pull/7151", "[reward, rollout] fix: align sparse reward_extra_info across batch paths"),
    "humanlabels": ("https://github.com/ethxin0011/rlvr_group_correlation", "GitHub - ethxin0011/rlvr_group_correlation"),
}
rows = {}
for rid, title in arxiv.items():
    rows[rid] = {"type": "arxiv", "url": "https://arxiv.org/abs/" + rid, "status": 200, "title": title}
for rid, (url, title) in github.items():
    rows[rid] = {"type": "github", "url": url, "status": 200, "title": title}
rows["openr1math"] = {
    "type": "dataset", "url": "https://huggingface.co/datasets/open-r1/OpenR1-Math-220k",
    "status": "network_failed", "title": None,
    "note": "web_fetch failed; local OpenR1 data and historical measurements exist, but the dataset card was not independently fetched this round",
}
rows["clopper1934"] = {
    "type": "print", "url": None, "status": "not_url_checked",
    "title": "The use of confidence or fiducial limits illustrated in the case of the binomial",
    "note": "Biometrika 1934; bibliographic entry, no URL",
}
rows["verl8015discussion"] = {
    "type": "github_comment", "url": "https://github.com/verl-project/verl/pull/8015",
    "status": "partial", "title": "PR #8015 discussion page fetched 200; comment anchor not separately checked",
    "note": "parent page reachable; comment text not independently re-read",
}
alias = {
    "deepseek2025r1": "2501.12948", "shao2024deepseekmath": "2402.03300",
    "lambert2024tulu3": "2411.15124", "yu2025dapo": "2503.14476",
    "sheng2024hybridflow": "2409.19256", "nie2026starvation": "2605.07689",
    "yang2026biased": "2601.08521", "egashira2026delay": "2605.02909",
    "xin2026wherefails": "2609.01354", "xin2026groupcorr": "2609.06386",
    "cai2025noisy": "2510.00915", "plesner2026imperfect": "2604.07666",
    "zhang2026rftfailure": "2605.04431", "hu2026vstress": "2609.36958",
    "hu2026routeaudit": "2610.02808", "tian2026stargrpo": "2609.36900",
    "ray2026fuzzing": "2606.01066", "zhang2026leaky": "2607.11022",
    "pan2026probe": "2610.02911", "masters2026rolloutcards": "2605.12131",
}
for k in list(rows):
    pass
rows_by_key = {}
for k, v in rows.items():
    rows_by_key[k] = v
for k, v in alias.items():
    rows_by_key[k] = rows[v]
build = json.load(open("<WORKSPACE>/thesis/build_thesis.json", encoding="utf-8"))
order = build["refs_order"]
missing = [k for k in order if k not in rows_by_key]
audit = {"verified_at": "2026-11-02T17:45:00+08:00", "n_cited": len(order), "n_rows": len(rows_by_key),
         "missing": missing, "refs": {k: rows_by_key[k] for k in order}}
(OUT / "refs_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("cited", len(order), "missing", missing)
print(Counter(v["status"] for v in rows.values()))
for k in order:
    print(k, rows[k]["status"], rows[k].get("url"))
