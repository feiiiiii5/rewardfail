# 2026-11-02 真实链路实验记录

本目录是 rewardfail 毕设新增实验的实际运行记录。实验在用户明确授权下，于 2026-11-02 完成。所有数值来自实际运行写出的 `case.json`、`case.log`、`ledger.jsonl` 和 `export/1.jsonl`，没有手工填写、修改或补造分数、错误文本或台账。

## 1. 目的与范围

- 在固定 verl PR #8015 头 `0c4c3d40d46d5f47d1918c905641eea969b7fa09` 与 Math-Verify 0.9.0 上，验证 `RewardLoopManager.compute_rm_score` 的 union-and-fill 修复。
- 真实运行：Ray 奖励工作进程、`rate_limited` 管理器、#8015 包装器与进程池、真实批汇总、`extract_reward`、真实 `_write_generations` 导出。
- 替身：生成环节用固定回答（`rewardfail/fixed_agent_loop.py`），故障由子进程退出注入（`rewardfail/inject.py`，退出码 17）。不训练模型、不加载模型权重、不下载数据、不使用 GPU。

## 2. 隔离与版本

| 项目 | 值 |
| --- | --- |
| 工作副本 | `<WORKSPACE>/rewardfail`，HEAD `d86baaa404f1b3b5b1a1fe49453075e9a82d2a0e` |
| 固定源码 | `third_party/verl-pr8015`，detached `0c4c3d4`，工作树干净 |
| 修复副本 | `thesis-runs/verl-pr8015-unionfill`，只改 `reward_loop.py` 两行 |
| 原版副本 | `thesis-runs/verl-pr8015-original`，与固定源码逐字节相同 |
| 补丁 | `env/patch.diff`；补丁 AST SHA-256 `4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325` |
| 驱动 | `rewardfail/experiments/thesis_chain.py`（新增，未提交） |
| 环境 | Python 3.12.8；Math-Verify 0.9.0、SymPy 1.14.0、Ray 2.59.0、Torch 2.14.1、NumPy 2.5.3 |
| 输入 | `c1c_chain.ROWS` 八行；`rows_sha256 = b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719` |

环境记录还写入了驱动进程和 Ray 工作进程实际导入的 `verl.__file__` 与 `reward_loop.__file__`；两者都指向目标副本。预检文件见 `env/preflight_source.json`、`env/preflight_env.json`。

## 3. 执行命令（摘要）

```bash
# C0 冒烟
.venv/bin/python experiments/thesis_chain.py --case C0 \
  --verl-dir ../thesis-runs/verl-pr8015-unionfill \
  --out ../thesis-runs/2026-11-02-chain/run-01/C0 --run-id run-01 --export

# 其余原版/修复用例（逐例子进程、独立 Ray 会话）
.venv/bin/python experiments/thesis_chain.py --case <O4|O5|O6|C1..C6|C1r|C2r> \
  --verl-dir <../thesis-runs/verl-pr8015-original|...-unionfill> \
  --out ../thesis-runs/2026-11-02-chain/run-01/<case> --run-id run-01 --export
```

## 4. 结果

| 用例 | 版本 | agent worker | 结果 | 分数 | 失败编号 | 台账 | 导出 |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| C0 | 修复 | 2 | 完成 | `[1,0,1,0,1,0,1,1]` | 无 | 空 | 8 行，读回一致 |
| C1 | 修复 | 2 | 完成 | `[0,0,1,0,1,0,1,1]` | `{0}` | `{0:2}` | 8 行，读回一致 |
| C2 | 修复 | 2 | 完成 | `[1,0,0,0,1,0,1,1]` | `{2}` | `{2:2}` | 8 行，读回一致 |
| C3 | 修复 | 2 | 完成 | 全零 | `{0..7}` | 各行 1–2 次 | 8 行，读回一致 |
| C4 | 修复 | 2 | 完成 | `[1,0,1,0,1,0,0,1]` | `{6}` | `{6:2}` | 8 行，读回一致 |
| C5 | 修复 | 1 | 完成 | `[1,0,1,0,1,0,0]` | `{6}` | `{6:2}` | 7 行，读回一致 |
| C6 | 修复 | 2 | 完成 | `[0,1,0,0,1,0,1,1]` | `{2}` | `{2:2}` | 8 行，读回一致 |
| O4 | 原版 | 2 | 完成 | `[1,0,1,0,1,0,0,1]` | 丢失（无 error 列） | `{6:2}` | 8 行，读回一致 |
| O5 | 原版 | 1 | 完成 | `[1,0,1,0,1,0,0]` | 丢失（无 error 列） | `{6:2}` | 7 行，读回一致 |
| O6 | 原版 | 2 | 中止 | — | — | `{2:2}` | — |
| C1r | 修复 | 2 | 完成 | 同 C1 | `{0}` | `{0:2}` | 8 行，读回一致 |
| C2r | 修复 | 2 | 完成 | 同 C2 | `{2}` | `{2:2}` | 8 行，读回一致 |

- 修复版 C0–C6 全部完成；分数与预先写定的向量一致；`error` 列只在计划失败样本上非空，非失败行为 `None`；C5 为 7 行；C6 按原始编号对应。
- 原版 O4/O5 完成但丢失 `error` 列；O6 在 `verl/experimental/reward_loop/reward_loop.py:369` 以 `KeyError('error')` 中止。这与实验前的静态推断一致。
- C1/C2 的独立重启 C1r/C2r 与首次执行一致。
- 导出读回全部通过：行数、分数、输入、输出、标准答案、`error` 值一致；`None` 写成 JSON `null`；长度不符的附加列被忽略。
- 注入台账：每个计划失败样本至少 1 条，非失败样本没有台账；实际次数 1 或 2，照实记录。

## 5. 偏差与失败记录（未删除、未改写）

1. **O5/C5 首次尝试在生成阶段中止**：7 行批次配 2 个 agent worker 时，`AgentLoopManager.generate_sequences` 调用 `prompts.chunk(2)`，在 `verl/protocol.py:871` 断言 `only support equal chunk. Got size of DataProto 7 and chunk 2.`。两次中止的原始 `case.json`/`case.log` 保存在：
   - `run-01/failures/O5-two-agent-workers/`
   - `run-01/failures/C5-two-agent-workers/`
2. 随后只把 C5/O5 的 **agent worker** 设为 1，**奖励工作进程仍为 2**，重跑通过。C5 的 7→8 补齐与 8→7 裁剪发生在 `compute_rm_score`，该路径未改；生成阶段的 agent worker 数不是本实验的研究对象。
3. C0–C4 在驱动加入 `agent_workers` 字段之前运行，`case.json` 中没有该字段；当时驱动硬编码 2。C5/C6/C1r/C2r/O5 在适配后运行，显式记录 `agent_workers`。驱动哈希有两组：`3b3aa0…`（C0–C4、O4、O6）和 `6cce7c…`（C5、C6、C1r、C2r、O5）。这不是数据修改，是驱动版本差异，已如实记录。
4. 第一次 `--all` 的汇总 `summary.json`/`manifest.json` 只覆盖到 C5 中止为止；它们保留为 `logs/summary-first-attempt.json`/`logs/manifest-first-attempt.json`。最终核对以 `run-01/verification.json`（249 项检查、0 失败）和 `manifest-all.json` 为准。

## 6. 数据完整性

- 每个用例保留 `case.json`、`case.log`、`ledger.jsonl`；完成的用例另有 `export/1.jsonl` 与 `export/wronglen/2.jsonl`。
- `run-01/verification.json` 与 `verification.md` 由只读脚本 `verify_run.py` 生成；脚本不修改任何 `case.json`。
- `manifest-all.json` 记录本目录、两份源码副本关键文件和驱动文件的 SHA-256：当前 `thesis_chain.py` 为 `6cce7c…`；C0–C4/O4/O6 记录中的旧驱动为 `3b3aa0…`。
- 未写入 `rewardfail/results`、`rewardfail-原始资料` 或 `~/.local/share/rewardfail`；固定源码 `third_party/verl-pr8015` 工作树干净。
- `rewardfail` 工作副本的未跟踪项只有 `.DS_Store` 和新增的 `experiments/thesis_chain.py`；没有提交、没有推送。

## 7. 结论边界

- 固定版本、单机（Apple M2 Pro，CPU-only）、小批量（7/8 行）、固定回答、受控子进程退出注入；不代表自然故障率、训练效果、其他平台或其他路径。
- 修复只覆盖 `RewardLoopManager.compute_rm_score` 的批汇总；路径 A、naive 管理器、下游训练屏蔽策略不在本次新增验证范围。
- C5/O5 的 agent worker 数与 8 行用例不同；该差异是为绕开生成阶段的等分块断言，已在结果中标注。

## 8. 后续

- 实验一至三的验收项已完成；下一步是整理结果表、机制分析和论文写作，不再重跑这 12 次执行。
- 若发现具体问题需要补充运行，使用新目录、先报告，不覆盖本记录。
