# 近一年原始论文更新与最强审稿质疑

2026-11-05审查轮次；实际联网访问日 **2026-11-04 UTC / CST**。检索窗口为近一年（2025-11起），按“verifier failure / noisy RLVR / missing evaluation / MNAR reward”检查arXiv原始论文正文；下列短引文均来自链接原文，每篇不足25个英文词。没有依赖聚合站或模型评论，也不声称穷尽优先权。现稿中的Cai `2510.00915v5`继续作为较早基础工作，不能把其2025-10首版算成近一年新论文。

## 新增/应补的直接比较

| 原始论文与读取位置 | 短引文 | 对本研究的实质影响与增量边界 |
|---|---|---|
| [Rad et al., Rate or Fate? RLVεR, 2601.04411v1](https://arxiv.org/html/2601.04411v1)，§3.2、§6.1、§7.4 | “noise primarily rescales convergence time” | 【明文】在其bandit/mean-field假设下以Youden J区分学习/反学习，另讨论KL和有限步限制。【分析】本研究不能把“出现负优势”直接推成最终退化；有限预算、KL、模式结构都须固定。它不是不可判定奖励的完整软件故障追踪；本稿增量仍是具体链路及执行事件。 |
| [Zhu & Kang, Noisy Data is Destructive…, 2603.16140v2](https://arxiv.org/html/2603.16140v2)，§3.3、§4 | “noisy data used in prior work is not 100% noisy” | 【明文】对原有噪声数据再验证，指出所谓全错标签中混有正确标签，重新训练后呈现不同结论。【分析】合成失败必须与答案真值独立记录，不能把超时零分自动计作false negative；证明训练伤害也需先审真值与noise construction。其标签污染问题不等于本稿availability failure。 |
| [Milikic et al., Learning Lean Feedback…, 2610.21881v1](https://arxiv.org/html/2610.21881v1)，摘要与训练评估章节 | “withhold rewards from potentially correct proofs” | 【明文】明确讨论慢检查/超时使潜在正确证明拿不到奖励，训练GPU评估器预测Lean反馈并进行训练比较。【分析】这是应补的近邻：不能声称首先提出“超时丢监督”或首先给出替代验证器训练策略。本稿仍可独立贡献Math-Verify到consumer的row-position追踪与固定事件复算；此处的1条恢复不是它所说潜在正确证明的真值认证。 |
| [Kim, Augmenting Human Evaluation with LLM Judges…, 2605.16354v1](https://arxiv.org/html/2605.16354v1)，§2–3 | “missingness model is known by design” | 【明文】将全部LLM评价加部分人工复核做两阶段抽样，以已知抽样机制的DR估计与方差做样本量设计。【分析】失败案例的随机抽审可把不可识别MNAR问题部分转成已知抽样设计，但需要真实人工/oracle结果与入样概率；不能把训练中的任意故障当作已知抽样。 |
| [Off-Policy Evaluation for Missingness-Aware Policies…, 2606.20206v1](https://arxiv.org/html/2606.20206v1)，§3、Appendix B | “identification typically requires additional assumptions” | 【明文】用reward-dependent propensity和next-state shadow variable，在排除限制/相关性假设下识别MNAR奖励并做OPE。【分析】没有这些结构时，幸存者校准不能识别失败奖励；不可把其MDP/OPE定理直接移到单次Math-Verify/组标准化训练。本稿应给识别界/敏感性，而非提出无条件“校准修复”。 |
| [Wu, Nair & Candès, Efficient Evaluation of LLM Performance…, 2601.20251v1](https://arxiv.org/html/2601.20251v1)，§3、Appendix A | “coverage-preserving finite-population extension of active inference” | 【明文】有限题库视角下用有设计的自适应选题和推断构造覆盖率区间，预测模型只提高效率。【分析】值得借鉴其区分finite-bank与superpopulation的做法；本稿[k/n,(k+u)/n]是已测行的补全范围，CP是另加二项工作模型。未设计随机审计就不能借其coverage保证。 |

## 已在现稿引用但本轮重新核实的边界

| 原始论文 | 短引文 | 重新核到的限制 |
|---|---|---|
| [Plesner et al., An Imperfect Verifier is Good Enough, 2604.07666v2](https://arxiv.org/html/2604.07666v2)，摘要、Appendix B/E | “these point estimates do not establish a general tolerance threshold” | 多seed固定晚期检查点的点估计损失较小，但CI允许更大损失；不应沿用v1摘要/搜索缓存的“15%噪声普遍无害”。固定题集上的seed不确定性也不是新题总体不确定性。现稿已经收窄，保留。 |
| [Egashira et al., Delay, Plateau, or Collapse, 2605.02909v2](https://arxiv.org/html/2605.02909v2)，§1、§3–4 | “cannot be explained solely by simple sample-level metrics” | 同初始FPR/FNR可以有不同训练动力学，结构化触发与随机噪声须分开。我们的M1/M2/M3注入只给三种有限例子，不估自然故障的结构或发生率。 |
| [Xin, Where the Verifier Fails, 2609.01354v1](https://arxiv.org/html/2609.01354v1)，§2.3 | “judgement accuracy and judgement availability” | 已明确定义返回真/假与timeout/error/crash的区别，零coverage应n/a。故障作为第三结果、coverage报告都不是本稿首先提出；增量是跨层实际代码追踪。 |
| [Xin, Are Verifier Errors Independent…, 2609.06386v1](https://arxiv.org/html/2609.06386v1)，§3.4–3.6 | “a marginal correlation, pooled across prompts of varying difficulty” | pooled相关可以来自prompt难度异质性；本稿的103 directed event pairs不能当条件依赖的证据。其人工标签是分层选择集，72个完整组更不是随机总体样本。 |
| [Masters et al., Rollout Cards, 2605.12131v1](https://arxiv.org/html/2605.12131v1)，Appendix B | “missing regression-test results default to [0]*10000” | 已描述跨层丢失/零填充/分母变化，包括异常变零。本稿不能声称首先发现失效信息跨层消失，具体行位置契约与执行对照仍是其可交付增量。 |
| [Yang et al., iCoder-27B, 2609.29626v1](https://arxiv.org/html/2609.29626v1)，§4.4.3 | “excluded unjudgeable samples from both group statistics and loss normalization” | 已实际采用同时剔除策略，且≤1幸存者优势为0；本稿offline/Pilot按verl的单幸存者mean0/std1约定，不能说完全同一实现。本研究的metadata patch仍不自动执行剔除。 |

【未知】本轮没有复跑这些论文的训练或审计其全部代码；引述的结果属于原作者报告。未核出版/同行评审状态，只按固定arXiv版本称论文或预印本。本轮也未找到足以支持普适“失败处理提高准确率”的原始证据；文献并不替代本研究自己的对照训练。

## 最强审稿质疑与最小补救

1. **“核心机制和修法早已公开，论文增量只是bug复述。”** 成立的压力点。#6545/#7151已描述first-row key与union-fill；Rollout Cards已描述跨层失效，iCoder已执行剔除，Lean反馈已谈超时失去监督。保留最可辩护主张：特定opt-in wrapper失败经真实manager、两种assembly到validation consumer的可执行组合；补文献，把新validation对齐patch与已有assembly修法分开。不要靠扩大训练风险措辞制造原创性。
2. **“主结论u=18无法独立重建。”** 本轮内部证据已改善：完整8pass从77个parent/child/guard文件严格重建，旧/新规则同事件对照，全部哈希不变；补样本也已重建。但事件仍不在公开包，公开复现缺口未闭合。最小补救是发布经过许可/隐私核查的必要事件或可核验派生链，说明内部freeze非外部注册；不需要再扫93,733条来替代原事件审查。
3. **“长超时不是真值，且参考error被当普通零分，范围过窄。”** 成立。继续称limit-sensitive recovery；报告error-inclusive u=34和one-to-thirty-five范围。本轮逐行复算补了16个error零分的来源，但不证明这些是错判。若要讨论false negatives，先由独立数学审阅/oracle核对争议行，并保留不可判定状态。
4. **“一个已预过滤语料、一次选答且孤立串行，不能给训练发生率。”** 成立。93,733是该固定回答帧，193,767全答有组内依赖；event co-occurrence不区分条件相关。最小补救是按问题cluster、按真实训练调度/worker采样预设另一个测量；在此前只给已实现补全范围，CP仍标为working model。
5. **“重负载中Linux没有复现abort，平台解释混了control input。”** 成立。现有Linux替代control与原mac不是单因素；不能把一次差异判成平台因果。最小补救是同input、wrapper、版本、线程/资源设置、observer和调度trace的matched跨平台复跑；在此之前历史abort仅是指定诊断条件的存在性证据。
6. **“72组优势图不等于梯度，更不等于学得更好。”** 成立。原稿边界正确；本轮真实135M LoRA试跑证明路径能改变参数，12臂完整结果没有一致收益。下一步要自由生成、真实scorer failure、独立clean test、足够seed和固定token预算，详见TRAINING_PROTOCOL；不能把本轮有限动作pilot包装为完整RLVR结论。
7. **“剔除和代填都有选择偏差，校准只是oracle leakage。”** 必须用设计回答。保留独立calibration分割、冻结特征/模型与失败标签隔离；pilot的校准器并未胜过常数Brier。正式MNAR实验需要随机抽审/外部真值或敏感性界，不承诺单靠存活者拟合能修复；AIPW奖励无偏也不推出组std/clip后的梯度无偏。
8. **“统计量很多但有效独立单位很少，选最佳checkpoint和臂间分母不同。”** 必须固定最终checkpoint、题级/seed级单位、共同评测集与多重比较。无故障/记零/剔除/校准保持相同生成预算，另报实际损失token与wall time。3seed只能探索，不能通过更多抽样动作假装增加独立训练次数。

## 推荐的稿件行动（仅供后续作者采用）

本轮不改已提交arXiv终稿、PDF或申请稿。公告后可在下一版本补上述六项近邻并用这次原始事件重建更新证据限定；同时明确公开输入是否仍缺。对研究的最强现有说法仍是**经执行验证的局部软件可靠性案例加有边界的固定回答测量**，另有一项单独标明范围的真实训练可行性pilot。不存在已证明的通用训练增益。
