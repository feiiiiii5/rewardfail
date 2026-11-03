# 2026-11-02 P1：本机可做的补充实验

用户授权“把本机能做的都给做了”。本目录只包含新增的只读/固定输出实验，不修改历史记录、不加载模型、不训练、不下载数据。

## 1. 环境

- 工作副本：<WORKSPACE>/rewardfail，固定源码 third_party/verl-pr8015，头 0c4c3d40d46d5f47d1918c905641eea969b7fa09。
- Python：rewardfail/.venv/bin/python，3.12.8；CPU-only（Apple M2 Pro，16 GiB）。
- 路径 A 探针使用原版源码副本 thesis-runs/verl-pr8015-original；自然重输入使用 original/unionfill 两个副本。
- 所有命令和日志在本目录；没有写入 rewardfail/results、rewardfail-原始资料 或 ~/.local/share/rewardfail。

## 2. 路径 A 固定输出探针（path-a/）

方法：构造 _InternalAgentLoopOutput，调用真实的 AgentLoopWorker._postprocess，再调用 extract_reward；union-and-fill 是同一函数源码的本地两行替换（不是上游补丁）。不加载模型、不启动 Ray、不走完整训练器。

结果：
- 基础案例 6 个；扩展矩阵把 error 和 timeout 分别放在 8 个位置，共 16 个位置案例。
- 原实现：失败在位置 0 时 KeyError；失败在位置 1–7 时完成，但 extract_reward 只看到 acc，error/timeout 列被丢弃。
- union-and-fill 原型：16 个位置全部完成，error/timeout 列保留，奖励向量不变。
- 这只证明路径 A 的汇总/消费者边界；完整训练器的 loss/advantage 仍未验证。

关键文件：results.json（基础案例）、positions.json（16 位置矩阵）、probe.log、positions.log、probe.py、positions.py。

## 3. 自然重输入批次传播（heavy/）

方法：从历史 D1 的 4 条重输入（IMO 1981 P6 和 5 的幂塔）读取标准答案与 R1 生成回答；用固定回答替身、真实 AgentLoopManager + RateLimitedRewardManager + Math-Verify 跑 8 行批次。没有注入故障。

| 用例 | 重输入位置 | 版本 | 结果 | 分数 | error/timeout 列 | 墙钟 |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | 2 | 原版 | 完成 | [1,0,0,0,1,0,1,1] | 无 | 14.58s |
| H1 | 2 | 修复 | 完成 | [1,0,0,0,1,0,1,1] | 无 | 15.44s |
| H3 | 0,1,2 | 原版 | 完成 | [0,0,0,1,0,1,0,1] | 无 | 26.17s |
| H3 | 0,1,2 | 修复 | 完成 | [0,0,0,1,0,1,0,1] | 无 | 24.73s |

解释：日志里出现 “Timeout during comparison”，但 Math-Verify 在库内把比较超时正常返回为 0，没有抛异常；管理器没有写 error/timeout 标记，所以原版和修复版都没有列。两行修复只能保留已经写出的标记，不能把库内静默超时变成可观测事件。这是修复的边界，也是“自然重输入不能替代稀疏键注入”的证据；不是自然发生率估计。

关键文件：heavy_rows.json（4 条输入的 hash/长度）、run-01/H1-*/case.json、run-01/H3-*/case.json、各日志、heavy_probe.py、load_heavy.py。

## 4. None 的离线 GRPO 算术（none/）

固定一组 8 条回答，其中 1 条失败，其余 7 条正确；比较“把失败记 0 并参与”“排除失败并调整分母”“把失败记 1（反事实）”。这是固定奖励的算术演示，不是训练实验。

| 处理 | 使用条数 | 均值 | 标准差 | 失败 advantage | 其余 advantage |
| --- | ---: | ---: | ---: | ---: | ---: |
| 记 0 并参与 | 8 | 0.875 | 0.331 | -2.646 | +0.378 |
| 排除并调整分母 | 7 | 1.000 | 0 | — | 0 |
| 记 1（反事实） | 8 | 1.000 | 0 | 0 | 0 |

结论：保留标记但不改 loss mask，与“记 0 并参与”的 advantage 相同；排除失败会改变均值/标准差；在这个全正确组里排除后 std=0，所有 advantage 变 0。可观测性本身不决定排除策略，三种策略的后果不同。

关键文件：none_arithmetic.json、none_arithmetic.log、none_arithmetic.py。

## 5. 数据完整性

- 所有结果来自脚本实际运行写出的 JSON/日志；没有手工填写分数或列。
- summary.json 记录每个文件的 SHA-256 和字节数；各 case.json 记录环境、源码路径、AST/源码哈希。
- 路径 A 的 union-and-fill 是本地源码替换，results.json 里的 fixed_source_sha256 是替换后源码的哈希；不是上游补丁。
- 自然重输入的 4 条输入 hash、长度、预览在 heavy_rows.json；没有修改原始数据。
- 本目录之外没有新增/修改历史结果。

## 5.1 补充只读数据流（未写入论文）

在路径 A 探针之后又做了一次只读数据流核对，不运行训练器：
- extract_reward 按 meta_info["reward_extra_keys"] 从 non_tensor_batch 取列；路径 A 在 rm_scores 存在时也设置该 meta。
- 训练器把 reward_extra_infos_dict 更新进 non_tensor_batch；默认 GRPO 的 compute_advantage 只读取 uid 和 token_level_rewards，error 列不进入默认 loss/advantage。
- error 列主要供日志、导出和可选过滤（如 filter_groups_metric）使用；这是静态观察，不是完整训练器运行验证，也没有证明训练收益。

## 5.2 其他审计（只读）

- **路径 A 批量矩阵**：1/2/3/7/8/16 行，error 在首/中/尾；原实现位置 0 KeyError、其余位置丢列；union-fill 全部保留。记录在 path-a/batch_sizes.json。
- **重输入内存曲线复核**：D1 三条嵌套幂样本的平均增长为 88.0/81.9/82.8 MiB/s，18–19 秒到约 1.5 GiB；第四条峰值 351 MiB、60 秒比较结束。与论文“82–88 MiB/s、约 18 秒”基本一致；这是读既有报告，不是重跑。记录在 heavy/memory_check.json。
- **跨框架静态审计**：TRL/OpenRLHF 以标量奖励/远程 reward model 为主，没有与 verl 相同的逐样本稀疏附加键汇总层；verl main（提交 6879e1a）的 reward_loop.py 仍可见首行取键写法。只是静态查看，没有运行其他框架。记录在 cross-framework/README.md。
- **参考文献核验**：28 条引用中 25 条页面 HTTP 200（20 arXiv + 5 GitHub）；1 条 PR 评论仅父页面；OpenR1 数据集页面本次网络失败（本地数据存在）；Clopper–Pearson 1934 为纸质文献未在线核验。没有发现缺失 arXiv/严重题名不符。记录在 refs/README.md 与 refs/refs_audit.json。

## 6. 边界

- 路径 A 探针：固定输出、无模型、无 Ray、无完整训练器；只到汇总/消费者边界。
- 自然重输入：4 次 8 行批次、固定回答、单机；条件传播，不是自然发生率；库内超时没有标记，说明修复不充分而非修复失败。
- None 算术：固定奖励、固定组；不是训练，不是模型行为证据。
- 这些结果可以补论文的机制/边界，但不能消除“没有训练收益、没有自然训练分布、没有跨平台”的限制。
