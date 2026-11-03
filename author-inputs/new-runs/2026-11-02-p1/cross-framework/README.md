# 跨框架静态审计（2026-11-02）

范围：只读查看三个上游仓库的公开源码；不安装、不运行、不做等价性结论。目的：判断“首行取键 + 稀疏附加键”是否是 verl 特有的接口问题，还是其他框架也有同形结构。

## 固定版本

| 项目 | 仓库 | main 分支提交 | 抓取时间 |
| --- | --- | --- | --- |
| TRL | https://github.com/huggingface/trl | 3a3b6c1464498364f69c01ad698b0a6a3990f534 | 2026-11-02 |
| OpenRLHF | https://github.com/OpenRLHF/OpenRLHF | dc2a7ad326f619fc5a47737ea47d1920ce2c0b53 | 2026-11-02 |
| verl | https://github.com/volcengine/verl | 6879e1ab07b9cfd0b4b27c31ca4e7afcad1466b3 | 2026-11-02 |

## 观察

### TRL

- 文件：trl/trainer/grpo_trainer.py，_calculate_rewards 附近。
- 奖励函数返回每条 completion 的标量列表；None 被转换为 torch.nan；额外的 completion 字段通过 log_extra 记录，不是训练用的逐样本稀疏 metadata。
- 该段未观察到“从第一行取键集合、再索引其他行”的聚合层；奖励函数的异常没有在这里被转成逐样本 error 列（会按函数调用路径传播）。
- 边界：只看主训练器文件，不能代表所有 reward 插件/环境接口。

### OpenRLHF

- 文件：openrlhf/trainer/ppo_trainer.py、openrlhf/trainer/ppo_utils/experience_maker.py。
- 奖励是远程 reward model 返回的标量张量列表，_flatten_results 后写入 samples.rewards / samples.info["reward"]；没有逐样本 reward_extra_info 键集合，也没有 error/timeout 列。
- 该段未观察到首行取键的汇总层；没有运行验证。
- 边界：只看这两个文件；reward model 实现和异常处理未逐一展开。

### verl main

- 文件：verl/experimental/reward_loop/reward_loop.py（提交 6879e1a）。
- 仍可见与固定 #8015 头版本相同的写法：reward_extra_keys = list(reward_extra_infos[0].keys())，随后 info[key] 逐行索引（约 365–369 行）。
- 这是静态观察，不是 main 分支运行验证；不据此声称 main 的完整行为或上游是否计划修复。
- 意义：该模式不只是一个旧 PR 的局部写法；至少在当前 main 的这段代码中仍存在。

## 结论与边界

- 三个框架的奖励接口不同：TRL/OpenRLHF 以标量奖励为主，verl 有逐样本附加信息的键集合；因此“首行取键”问题不能直接外推到 TRL/OpenRLHF，也不能说它们“安全”。
- verl main 的静态同形写法说明本文讨论的机制仍有版本相关性；但没有运行 main，不能把固定版本的实验结果写成 main 的结论。
- 这不是跨框架实验，只是相关工作和风险定位；论文正文仍以固定 #8015 版本的实验为准。

## 证据文件

- trl.txt、openrlhf.txt、openrlhf_experience_maker.txt、verl_main_reward_loop_pinned.txt、verl_main_reward_loop.txt。
- 原始 URL 与提交 SHA 见上表；抓取内容未改动。
