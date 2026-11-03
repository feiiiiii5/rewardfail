# 首轮本机机制验证：判分失败的记录会不会在汇总时丢掉，或让整批报错

用户 10-06 批准（申请季 `决策与待办/已定决策.md` D115）的首轮验证。只用本机 CPU；**没有下载任何模型或数据集**，没有训练。
主做 Claude，Codex 独立复核。本仓是独立的本地 git 仓，不推送；申请季的汇报与 Codex 10-06 复核记录见 `../RLVR首轮验证.md`（Codex 在仓外副本复跑，原件在 `~/.local/share/rewardfail/codex-audit/20261006-1804/`，本仓原始记录未被改动）。第二阶段方案见 `../RLVR第二阶段方案.md`（10-06 按 Codex 审核修订，双方一致前不测量）。

## 被测对象（固定版本）

| 对象 | 版本 | 用途 |
|---|---|---|
| verl PR #8015 head | `0c4c3d40d46d5f47d1918c905641eea969b7fa09` | 被测：Math-Verify 包装（坏池重建、重试一次后往上抛）、rate_limited 与 naive 管理器、两条汇总路径 |
| verl PR #7437 head | `1403781f1ae88b50c7544adc2d4bc2ddb1c178af` | 已知缺陷对照：prime_math 的期限修复及其自带测试 |
| Math-Verify | PyPI 0.9.0 | 本机安装包的 8 个源码文件与固定提交 `ba3d3aaff23b3f4cac7a14672b4f6e293d97c98b` 逐字相同（10-06 用 `cmp` 核对） |

另核：#8015 head 的 `prime_math/grader.py` 与固定 main `8718ca30a3f002f93b7c4fd99b9b2506718681bc` 逐字相同，所以 #8015 head 可以当“修复前”的代码。

这个 Math-Verify 包装不在 verl 固定版本的默认判分路由里（MATH 默认走 `math_reward`，GSM8K 走 `gsm8k`，包装只出现在 MATH 分支的注释建议里），要用自定义奖励函数指定；verl 自己的测试和本仓 `rewardfail/reward_fn.py` 都是这样接的。所以这里的结果只适用于选用这个包装的配置。

## 环境

- CPython 3.12.8（uv 管理），macOS 27.2 arm64，M2 Pro；uv 0.12.10。
- `requirements.in` → `requirements.lock`：128 个包，全部带哈希；verl 的 `install_requires` 原样照抄，另加 CPU 版 torch、math-verify==0.9.0、pytest，以及实际导入时才发现缺的 `cachetools`、`uvicorn`、`fastapi`（verl 的 `install_requires` 没列）。
- 关键版本：torch 2.14.1、ray 2.59.0、transformers 5.12.1、tensordict 0.10.0、sympy 1.14.0、numpy 2.5.3。
- 占用：`.venv` 约 1.2 GB；两份 verl 浅克隆约 18 MB、16 MB。
- 模型目录是替身：`rewardfail/tiny_model.py` 在本机现造字节级分词器和一个只有配置、没有权重的 Qwen2 配置（`artifacts/tiny_model`），只供 verl 读分词器和 `hf_config`。

## 复跑

```bash
./setup.sh        # 拉固定提交、在 ~/.local/share/rewardfail/venv 建环境并按锁文件安装，.venv 链接过去
.venv/bin/python experiments/c1c_chain.py --all --out results/c1c/run1                      # 10–20 分钟，13 个情形各自独立进程与 Ray 会话
.venv/bin/python experiments/c1a_timeout_layers.py run1.json 2> results/c1a/run1.stderr.log  # 约 1 分钟
.venv/bin/python experiments/c2a_alarm_nesting.py run1.json                                  # 约 15 秒
.venv/bin/python experiments/c1b_pr7437_control.py run1                                      # 约 1 分钟
.venv/bin/python experiments/compare_runs.py                                                 # 逐项比较 run1 与 run2，并打印汇总表
```

每个结果文件都带运行环境；`results/c1c/*/summary.json` 另记 verl 实际提交、工作树是否干净、锁文件与各脚本的 sha256、输入行的 sha256。
本机桌面开着 iCloud 同步，所以环境放在不同步的 `~/.local/share/rewardfail/venv`；第一次建在桌面的旧环境已改名为 `.venv.nosync`（iCloud 不同步带这个后缀的目录）。用户 10-06 决定删除它；移进废纸篓两次都卡在 iCloud（`mv` 和 Finder 都不返回），按规则不直接永久删除，交用户本人删。

`c1c_chain.py` 每个情形结束、Ray 会话关闭后，打分进程池的子进程会留下来（父进程已退出，不再参与计算；10-06 清理时有两百多个，来自当天的多次运行）。全部跑完后清理：

```bash
ps -eo pid,ppid,command | awk '$2==1 && /rewardfail\/venv\/bin\/python -B -c from multiprocessing/ {print $1}' | xargs kill
```

## 什么是真实运行的，什么是替身

| 部分 | 状态 |
|---|---|
| Ray 打分进程 `RewardLoopWorker`、rate_limited / naive 管理器、#8015 的 Math-Verify 包装与 spawn 进程池、真实 Math-Verify | 真实 |
| 路径 A：`AgentLoopManager` 起两个 `AgentLoopWorker`（Ray 进程），逐条把回答交给随机一个打分进程，`_postprocess` 汇总，再跨进程 `DataProto.concat` | 真实 |
| 路径 B：`RewardLoopManager.compute_rm_score` 把整批切块交给打分进程后汇总 | 真实函数；**触发条件不同**：生产中只在“用奖励模型且没有单独资源池”时走这条，本机没有奖励模型，所以直接调用同一个函数（`reward_model_manager` 为 None 时只是跳过 wake_up/sleep） |
| 训练器读奖励：`extract_reward` | 真实 |
| 生成 | 替身：`rewardfail/fixed_agent_loop.py`，把每行预先写好的回答文本编码成 token，不调用模型 |
| 判分失败的来源 | 注入：`rewardfail/inject.py` 让带标记的回答一进 Math-Verify 子进程就退出（模拟子进程被杀）。两次尝试都触发，所以是“持续失败”。每次触发写一行台账（`*.ledger.jsonl`），不靠日志证明注入发生 |
| 库内超时 | 注入：`rewardfail/inject_timeout.py` 只让库内被计时的步骤变慢，库自己的计时器和捕获代码不动 |
| 计时器嵌套的外壳 | 标准库替身，模仿“每题 `signal.alarm(N)`”的写法，不是 2609.01354 作者的代码 |

## 结果

全部结果各跑两轮（`run1`、`run2`），`experiments/compare_runs.py` 逐项比较：**两轮不一致项为零**。下文的“预测”都是运行前写在脚本里的。

### 1. 失败记录经过管理器与汇总之后（`experiments/c1c_chain.py`）

8 行，第 0、2、4、6、7 行本来答对（1 分）。单行失败的情形都选本来答对的行，好和“答错记 0”区分；整块、整批失败的情形（A4–A6、B3）含原本答错的行。路径 A 有两个生成进程：第 0–3 行进第一个，第 4–7 行进第二个。台账证实每个失败行都被注入，且重试后又失败。

| 情形 | 管理器 | 失败行 | 结局 | 报错位置（被测代码） | `extract_reward` 返回的附加列 | 各行分数 |
|---|---|---|---|---|---|---|
| A0 | rate_limited | 无 | 完成 | — | acc | 1 0 1 0 1 0 1 1 |
| A1 | rate_limited | 2 | **完成，第 2 行由 1 变 0，`extract_reward` 返回里没有 error** | — | acc | 1 0 **0** 0 1 0 1 1 |
| A2 | rate_limited | 0（第一个生成进程的首行） | **中止**：KeyError 'error' | agent_loop.py:1111 | — | — |
| A3 | rate_limited | 4（第二个生成进程的首行） | **中止**：KeyError 'error' | agent_loop.py:1111 | — | — |
| A4 | rate_limited | 全部 | 完成，error 列在 | — | error, acc | 全 0 |
| A5 | rate_limited | 4–7（第二个生成进程整块） | **中止**：AssertionError，键 error 不在第一块里 | py_functional.py:366（跨进程合并） | — | — |
| A6 | rate_limited | 0–3（第一个生成进程整块） | **中止**：AssertionError，meta_info 的 reward_extra_keys 冲突 | protocol.py:949（跨进程合并） | — | — |
| B0 | rate_limited | 无 | 完成 | — | acc | 1 0 1 0 1 0 1 1 |
| B1 | rate_limited | 2 | **完成，第 2 行由 1 变 0，`extract_reward` 返回里没有 error** | — | acc | 1 0 **0** 0 1 0 1 1 |
| B2 | rate_limited | 0（整批首行） | **中止**：KeyError 'error' | reward_loop.py:369 | — | — |
| B3 | rate_limited | 全部 | 完成，error 列在 | — | error, acc | 全 0 |
| N1 | naive（verl 默认） | 2（路径 A） | 中止：BrokenProcessPool（真实原因） | math_verify.py:84 | — | — |
| N2 | naive（verl 默认） | 2（路径 B） | 中止：BrokenProcessPool（真实原因） | math_verify.py:84 | — | — |

13 个情形的结局都与运行前的预测一致。完整表（含预测原文、注入台账）由 `compare_runs.py` 打印。要点：

- rate_limited 管理器确实按 #8015 的设计写了 `error`（A4、B3 里能看到原文 “A process in the process pool was terminated abruptly…”），但两条汇总只按首行的键名取列：失败行不在首位时，`extract_reward` 返回的只有 `acc`，单看这个返回值，失败行的 0 分与答错的 0 分分不开（没有运行训练器）；失败行在首位、且同一批里还有正常行时，整批报 KeyError（全部行都失败时正常完成，`error` 列在，见 A4、B3）。
- **路径 A 的“首行”是每个生成进程分到的那一块的首行**，不是整批首行；另外，两块的键名不一样时，跨进程的 `DataProto.concat` 也会断言失败（A5、A6）。这两点是读代码时没有写进提案的，运行前根据 `concat` 的代码补写了预测。
- 路径 A 另有一列 `reward_extra_info`（来自 `extra_fields`）原样保存每行的字典，A1 里第 2 行的字典仍带 `error`；所以准确说法是“奖励读取接口 `extract_reward` 的返回里没有”，不是“哪里都没有”。v0 训练器 `ray_trainer.py` 里没有找到读这一列的代码（只做了文本搜索，未运行验证）。路径 B 没有这一列。
- verl 默认的 naive 管理器不接异常：同样的持续失败直接让整批中止，报的是真实原因。也就是说，#8015 的“往上抛”只有配 rate_limited 时才会进入“标记失败行”这条路。
- 注入台账里，同一打分进程中第一个持续失败的行被注入两次，紧接着的失败行只注入一次。与代码一致：第二次失败时包装直接往上抛、没有替换坏池（math_verify.py:100–103），下一次调用的第一次尝试撞上旧的坏池、重建后才真正提交。

### 2. 库内超时能否走到包装的超时分支（`experiments/c1a_timeout_layers.py`）

`timeout_score` 设成哨兵值 −7：返回 −7 说明走到了包装的超时分支。

| 情形 | 不注入时 | 注入后返回 | 耗时 | 走到超时分支 |
|---|---|---|---|---|
| 库内解析超时（回答的解析步骤变慢） | 1.0 | **0.0** | 约 5.0 秒 | 否 |
| 库内比较超时，字符串形式不同（1/4 对 0.25） | 1.0 | **0.0** | 约 5.0 秒 | 否 |
| 库内比较超时，但字符串那一对相同（7 对 7） | 1.0 | **1.0** | 约 5.0 秒 | 否 |
| 外壳阳性对照：子进程直接抛 TimeoutException | — | −7 | 立即 | 是（TimeoutException 分支，进程池不换） |
| 外层等待超时（外层期限 4 秒，步骤睡 8 秒，不在库计时内） | — | −7 | 4.0 秒 | 是（外层等待分支，进程池被替换） |

- 库内超时在库里就被折成空列表或 False，包装照常返回 0（只在子进程的日志里留一行 “Timeout during parsing/comparison” 警告）；`timeout_score` 管不到它们。#8015 的注释把 TimeoutException 分支说成“库自己的计时器在子进程里触发”的情形，这与默认参数下的实际行为不符。
- 分支走错改不改分，要看库怎么收场：库把超时折成 0 时（上表前两行），实际得分和包装超时分支会给的默认 `timeout_score`（0）相同；比较超时但字符串那一对相同时（第三行），实际得 1，和该分支会给的 0 不同。用户把 `timeout_score` 改成别的值（例如想单独标记超时）时差别更大，而且库内超时不留可识别的信号。该分支按契约是否应当触达，与得分变化分开（10-06 按 Codex 第二阶段审核修正：原写“分支走错本身不改分”过宽）。
- 但和正常判分相比，原本答对的回答会变 0（上表 3 个受控用例里 2 个变 0，1 个靠字符串回退仍为 1）。这部分伤害有多大取决于自然发生率，本轮没有测（10-06 按 Codex 复核修正：原写“影响有限”过宽）。
- 同一个慢步骤，在本进程主线程直接调用库：`raise_on_error=False`（默认）返回空列表；`raise_on_error=True` 抛 TimeoutException。这是默认协议与诊断协议的对照，不是缺陷。

### 3. 外壳计时器与库内计时器嵌套（`experiments/c2a_alarm_nesting.py`）

| 情形 | 外壳期限 | 结果 |
|---|---|---|
| 对照：不调用库 | 2 秒 | 2.0 秒时外壳期限触发 |
| 调用一次库的 parse，之后再做 4 秒的事 | 2 秒 | **外壳期限不再触发**；读出剩余为 0；外壳的处理函数仍在 |
| 调用一次库的 verify，之后再做 4 秒的事 | 2 秒 | 同上 |
| 库内一步要 3 秒 | 1 秒 | **外壳 1 秒期限不触发**，这一题跑满 3 秒（库把期限改成了自己的 5 秒） |

库的计时器在结束时 `alarm(0)`，把外壳设在同一进程主线程里的期限清掉；处理函数会恢复，剩余时间不会。被测 verl 版本里只有 Math-Verify 包装调用这个库，而且在子进程里调用，文本搜索没找到“外层 alarm 包着 Math-Verify”的写法；所以这一条在 verl 里仍只是 2609.01354 外壳那种写法的个例。

### 4. 已知缺陷对照：#7437（`experiments/c1b_pr7437_control.py`）

| 代码 | 子进程启动方式 | 两个“等价答案应判对”测试 | “慢求值应超时”测试 |
|---|---|---|---|
| 修复前（#8015 head，= 固定 main） | spawn（macOS 默认） | 失败 | 通过 |
| 修复前 | fork（本机显式指定；Linux 上 Python 3.12 通常默认用它） | 失败 | 通过 |
| 修复后（#7437 head） | spawn | 失败（每一步都打印超时） | 通过 |
| 修复后 | fork | **通过** | 通过 |

- 在本机显式 fork 方式下，对照按预期（只在 macOS 上跑，不等于 Linux 条件）：修复前等价答案被判错，修复后判对。修复前那条“慢求值应超时”的测试能通过，是因为异常被吞后直接返回 False，不是真的超时。
- 附带观察（不计入本题主张）：#7437 的修复每次判等都起一个子进程计时；spawn 方式下等价答案又被判错，并出现 2 秒期限的超时日志。子进程要重新导入 verl：10-06 在新解释器里单独导入该模块，三次 5.6–6.8 秒（`results/c1b/import_timing_20261006.txt`），与“期限被启动耗光”相符，但测试运行中没有拆分各段耗时。Linux 上 Python 3.14 起默认启动方式不再是 fork，是否受影响未核。

## 没有确认的事

- 自然发生率：子进程真的被杀、或库真的超时，在实际训练里多常见，本轮没有测（需要第二阶段的数据）。
- 训练影响：失败行记 0 分对学习的影响没有测（需要第三阶段）。
- 路径 B 在生产中的触发条件（启用奖励模型）没有复现。
- 固定 main `8718ca3` 上没有运行。读代码看，两条汇总的“只取首行键名”在 main 上也一样，只是 main 的 Math-Verify 包装把异常吞成 0，不会往上抛；配 rate_limited 时，任何会抛异常的奖励函数都会走到同样的汇总。
- verl 的 v1 训练器（TransferQueue）没有运行；读代码看到它在验证阶段按全部行的键名并集汇总、缺的补 None。
- TRL、open-r1 有没有“外层计时器包着 Math-Verify”的写法，本轮没有查。
- Linux 上没有运行；本机是 macOS（spawn 启动方式、信号行为同属 POSIX，但未在 Linux 上核）。

## 第二阶段数据（10-06 已下载并核对；测量尚未开始）

用户 10-06 决定：数据集由本人下载，Claude 在下载前停下、给出指令。`data_manifest.tsv` 列出 22 个文件的固定版本、字节数和校验值，共 2,181,301,233 bytes（约 2.18 GB）；10-06 只用 Hugging Face 的文件树接口和 HEAD 请求核对过链接、大小与 sha256，没有下载内容。

**10-06 晚实际下载**（申请季 D121：用户在对话里让 Claude 运行本脚本，只限这份清单）：

- 20:56–21:06，Claude 在中文 UTF-8 环境下用 macOS 自带 bash 3.2 运行，经 Claude Code 的本机代理出网。用户自己的终端没设代理，那样直连能不能下，没有验证。
- 21 个文件一次核对通过。人工标注集 CSV 报校验失败，但字节数相同，按 git blob 定义另算的值也与清单一致，问题在脚本：本机全局 git 设了 `core.autocrlf=input`，`git hash-object` 默认先把 CRLF 换成 LF 再算。已改用 `--no-filters`，并把“下完但核对不符”和“没下完整”分开提示。离线测试 `tests/test_get_data.sh` 加到 17 项，中文、英文 UTF-8 和 C 三种环境都通过；修复前的脚本在新增的 3 项上失败。
- 修好后重跑：22 个文件都在本机核对通过，没有再下载；`--check` 也通过。数据目录的 `下载记录.tsv` 记了这两次运行（通过 21、未通过 1；通过 22、未通过 0）。
- 只读清点（没有判分）：`plan/data_inventory.py`，结果在 `plan/data_inventory.json`。93,733 题与数据卡一致；uuid 不唯一（664 行缺失或写成 `NaN`，60 个 uuid 各被两道不同的题共用），每题回答 1–6 条。主样本因此改用题面原文的哈希作标识，见申请季方案第 3、5 节。

| 数据 | 固定版本 | 文件 | 字节数 | 用途 |
|---|---|---|---|---|
| OpenR1-Math-220k default | `e4e141e` | `data/train-*` 10 个 parquet + 数据卡 | 2,149,897,914 + 5,131 | 长推理回答被重新判分时，库内超时、计时管不住的输入等内容触发的失败多常见；系统资源导致的崩溃率用回答重放测不了 |
| rlvr_group_correlation 人工标注集 | `ccb3302` | `gold_set_1p5b_manual_labeled.csv` + LICENSE + README | 2,320,128 + 1,067 + 5,836 | 有人工对错标签，用来逐条诊断“判错”是不是判分失败造成的；不保证完整组 |
| MATH-lighteval | `0530c78` | train、test parquet + 数据卡 | 4,848,021 + 8,412 | 标准答案一侧能不能被解析 |
| GSM8K main | `740312a` | train、test parquet + 数据卡 | 2,725,633 + 7,935 | 同上 |
| DeepScaleR | `b6ae8c6` | `deepscaler.json` + 数据卡 | 21,479,374 + 1,782 | 同上 |

```bash
bash get_data.sh            # 下载到 ~/.local/share/rewardfail/data（不同步 iCloud），仓内 data 链接过去；逐个核对，可断点续传
bash get_data.sh --check    # 只核对已有文件：不下载，不建目录或链接
```

数据卡里的许可标签（Apache-2.0、MIT）是作者声明，上游权利链没有逐一核实；数据只在本机做测量，不再分发。

## 第二阶段测量代码（10-07：自检、资源试跑与主测量脚本；同日按 Codex 审核修订两次；主样本尚未判分）

按申请季《RLVR第二阶段方案》第 4–7 节与 Codex 第 11.2 节实现，代码在提交 `aad920c`。Codex 同日审核（方案第 13 节）要求修正六项，修订说明在方案第 14 节，证据见本节末“10-07 修订”；Codex 复核修订（方案第 15 节）又要求修正工作块结束时漏停，说明在方案第 16 节，证据见本节末“10-07 晚第二次修订”。主测量要等 Codex 审核修订、经用户确认（申请季 D111、D130、D131），`s2_main.py` 对主样本运行须加 `--confirm-main`。下面“自检”“资源试跑”“读法比对”“主测量脚本测试”四段是修订前的结果，由 `aad920c` 生成，三份报告里记的代码 sha256 与该提交逐文件一致；这些报告原样保留，修订后的结果另写在 `results/s2_rev1/`。原始记录在 `~/.local/share/rewardfail/stage2/runs/`，不进仓。

| 文件 | 作用 |
|---|---|
| `rewardfail/s2/obs.py`、`child.py` | 观测层。父侧记请求、尝试、池代次、每次等待的结局、重置与杀进程；子侧逐步记墙钟、CPU、结果、库日志类别和计时信号（SIGALRM）到达时刻。输入只存哈希和长度。10-07 修订后每条记录带序号（父侧文件 seq、每行 rseq，子侧文件 fseq、每个任务 tseq），每行以 row_begin、row_end 起止，任务结束行记收到的计时信号总数 |
| `rewardfail/s2/mem.py`、`guard.py` | 整机保护。内存按 macOS phys_footprint 算（RSS 在内存被压缩后会掉）；预算 min(8 GiB, max(1 GiB, 可用 − 1.5 GiB))；暂停、整项停止、单个子进程 3 GiB 上限。1 GiB 下限不会强行开跑：可用低于 2.5 GiB 时按 3 GiB 子进程上限算出的 P 是 0 |
| `rewardfail/s2/stepguard.py` | 10-07 修订新增：准备与分析环节（构建任务与生成版本锁、核对版本锁、分桶合成、段间统计、汇总）的资源保护，同一套条件；停在检查点或卡住时直接结束，输出先写临时文件再改名。第二次修订后，工作块结束等同最后一个检查点，结束时才查到的停止也抛 |
| `rewardfail/s2/supervise.py` | 按进程组启动与清理测量进程；中断两次的行记未裁定；检查点续跑；调度不在了测量进程就停 |
| `rewardfail/s2/analyze.py` | 逐行合成与完整性检查：序号连续不重复；父侧提交、等待结局与池代次；子侧与父侧的请求、尝试、池代次、测量进程、子进程登记、时限与注入对得上；任务起止与步骤配对、顺序合包装（先两次解析，再按循环比较），结果能由步骤复现；计时信号都落在步骤里。不过的行记“观测不完整（未裁定）”。中断后重跑的行只取产出结果那次启动的记录；大运行分桶合成 |
| `rewardfail/s2/data.py`、`atype.py` | 抽样映射、逐行读回答、试跑集、答案类型 |
| `rewardfail/s2/report.py` | 裁定、主指标与界、答案类型、跟进各表、判定 |
| `experiments/s2_worker.py` | 测量进程：逐行调用被测包装（observe、off、reference，`--limits N`） |
| `experiments/s2_selftest.py` | 自检，只用合成输入 |
| `experiments/s2_pilot.py` | 资源试跑与观测开关对照，只用主样本以外的回答 |
| `experiments/s2_reader_check.py` | 读法改动前后逐条比对与内存 |
| `experiments/s2_main.py` | 主测量：默认一遍 → 参照 → 时限 2/10 秒 → 重放 3 次（事件、参照事件、k、时限敏感、超过 10 秒的并集）→ 随机 1% 重测 → 判定；续跑核对版本锁与段参数；测试模式只用试跑集与注入行 |
| `experiments/s2_rev1_recheck.py`、`s2_rev1_tail.py`、`s2_rev1_switch_repeat.py` | 10-07 修订：用新检查复核修订前的全部原始运行；按修订口径从旧试跑报告重算长尾情景；开关对照按相反顺序重跑并拆分耗时 |
| `tests/test_s2_stats.py`、`test_s2_flow.py`、`test_s2_resume.py`、`test_s2_stepguard.py`、`test_s2_main_e2e.py` | 10-07 修订：置信界独立核对、跟进流程替身、续跑版本核对、准备与分析保护的控制测试、主测量脚本在真实入口上的续跑与拒绝。第二次修订后后四个的结果写 `results/s2_rev2/` |

```bash
.venv/bin/python -I experiments/s2_selftest.py       # 约 4.5 分钟；写 results/s2_rev2/selftest/report.json
.venv/bin/python -I experiments/s2_pilot.py          # 约 1 分钟；写 results/s2_rev1/pilot/report.json
.venv/bin/python -I experiments/s2_reader_check.py   # 约 1 分钟；修订没有重跑
.venv/bin/python -I tests/test_s2_main_e2e.py        # 约 5 分钟：先跑主测量脚本测试（下一行，报告写 results/s2_rev2/），再验真实入口上的续跑、拒绝与结束时停止
.venv/bin/python -I experiments/s2_main.py --source pilot --n 300 --synthetic --child-limit-mib 768 --P 2   # 约 4 分钟
.venv/bin/python -I tests/test_s2_report.py
.venv/bin/python -I tests/test_s2_stats.py
.venv/bin/python -I tests/test_s2_flow.py
.venv/bin/python -I tests/test_s2_resume.py
.venv/bin/python -I tests/test_s2_stepguard.py       # 约 40 秒
.venv/bin/python -I experiments/s2_rev1_recheck.py
.venv/bin/python -I experiments/s2_rev1_switch_repeat.py   # 约 30 秒
# Codex 审核修订并经用户确认后才跑：.venv/bin/python -I experiments/s2_main.py --source main --confirm-main
```

**自检**（`results/s2_selftest/report.json`）：70 项全过，用时 267 秒。G 保护逻辑 12、G2 真实内存读数 2、A 顺序注入 22、B 并发连带 7、C 开关对照 11、R 参照时限 4、D 整项停止 6、E 中断重跑与调度不在 6。同日第一次完整自检 58 项里 D 段 3 项未过：每秒采样的进程合计 RSS 峰值 1.15 GiB（`peak_total_rss`），低于那次 1.32 GiB 的预算，整项停止没有触发（0.88 GiB 只是第 10 秒的合计读数，不是峰值，也不是单行占用）。改按 footprint 后通过。RSS 下降而 footprint 保持的证据是独立探针 `results/s2_selftest/footprint_probe.*`（600 MiB：RSS 从 621 掉到 350 MiB，footprint 一直 612 MiB）；G2 那次 RSS 没有下降，只证明 400 MiB 的存续占用按 footprint 计入。

**资源试跑**（`results/s2_pilot/report.json`）：1,003 条主样本以外的回答，按分片和答案类型分层。
- 观测开、关各跑 500 行，逐行分数相同，每行耗时差 p99 为 1.3 毫秒。
- 一条流水线的 footprint 采样最大 0.80–0.84 GiB（ref 段约 0.805 GiB；测量进程 0.50–0.53、子进程约 0.30），调度 0.16 GiB。
- 当时可用内存约 5.4 GiB，按方案公式算出 P=1。
- 参照覆盖的 315 行仍全是 0 分。
- 整机保护没有干预，旧池子进程都已退出。
- 按 P=1 的吞吐估：默认一遍 0.7 小时，参照 30,438 行 0.4 小时，跟进约 2,800 行不到 0.1 小时。
- 试跑里没有任何超时或异常事件（0/1,003），长尾只能给带假设的情景，不是主测量的上界或预计。试跑回答按分片和题型定额抽自主样本以外、不含只有一条回答的题，零事件的单侧 95% 模型界（约 0.3%）要另外假设主总体与试跑同分布、各行独立才能借用。在这个假设下，每条事件行七段各按外层时限等满：每段一次等待加一次新池预热约 498.4 秒，P=1 外推约 38.7 小时（报告里原写 495.8 秒、38.5 小时，少计一次预热）；池损坏后重试、等待再走满、每次尝试各计一次新池启动约 996.9 秒（16.6 分钟），外推约 77 小时。导入、读数据、保护暂停与人工续跑都没有设界。重算见 `results/s2_rev1/tail_scenarios.json`，原报告不改。

**读法比对**（`results/s2_pilot/reader_check.json`）：93,733 行、193,767 条回答，新旧两种读法逐条相同，全部文字的 sha256 一致。按主测量的顺序读前 3 个分片，每读完一个分片记一次到那时为止的 footprint 峰值：旧读法 699–837 MiB，新读法 448–499 MiB；读完各分片时的当时读数另为 631–767 MiB 与 374–392 MiB，两种口径不混成一个范围。

**主测量脚本测试**（`results/s2_main_test/report.json`，不是测量结果）：试跑集 300 行加 5 条注入行，P=2，单个子进程上限测试用 768 MiB。注入行全部按预期：
- 慢 8 秒的记为 k，时限 2/5/10 秒的裁定是 0/0/1。
- 参照也超时的、持续杀池的、超内存上限的、外层超时的记为 u。
- 持续杀池那行进入继续第 1 条的列表；外层超时与池损坏两行成为条件实验候选，超内存上限那行不算。
- 300 行真实回答里，默认得 0 的 102 行在参照下仍是 0，默认得 1 的 198 行在参照下仍是 1。

**10-07 修订**（Codex 审核见申请季方案第 13 节，修订说明见第 14 节；证据都在 `results/s2_rev1/`，修订前的报告与原始记录不改）：
- 观测完整性。父侧每条记录带文件序号 seq 和行内序号 rseq，每行以 row_begin、row_end 起止；子侧每条记录带文件序号 fseq 和任务内序号 tseq，任务结束时记收到的计时信号总数。`analyze.py` 补查序号、任务起止与步骤配对、步骤顺序（先两次解析，再按包装的循环比较）、结果能否由步骤复现，以及父子记录的请求、尝试、池代次、测量进程、子进程登记、时限和注入是否对得上；不过的行记“观测不完整（未裁定）”。旗标“计时信号被吞”改名为“收到计时信号、库没记超时”：前者是推断，后者是看到的现象。
  - 自检新增 A- 负对照 18 种，每种在 A 段记录的一份副本上删、改或重复记录：删回答侧解析的起止与日志；只删超时日志；删任务开始；删回答侧解析的结束；子侧池代次改成 778；重复一条比较结束；换成父侧没登记的进程号；前两步种类互换；子侧时限改成 9 秒；回答侧解析结果改成空；比较结果改成不相等；删计时信号；改子侧记的测量进程名；重复一条等待结局；删行结束；删父侧重置记录；删子进程退出；重复结果行。被改的行都进“观测不完整（未裁定）”，其他行的问题与类别不变；增删了记录的另触发文件序号检查。另一项说明不带序号时只删超时日志查不出来。
  - 用新检查复核修订前 10 次运行的 52 个目录、4,768 行（旧记录没有序号，按 strict=False 跳过序号三项）：与旧检查结论不同的只有 3 行，都是自检里故意中断两次的 D-hog，类别仍是“未裁定（中断两次）”，新检查多报了两次启动的尝试编号重复。按包装的循环复现了 4,651 个任务的 15,121 个比较步骤，没有一处对不上；新检查在这些运行里也没有报出结构或关联问题。两种检查都报的问题只在第一次自检（11:34，58 项那次）：那一版子进程还没装计时信号的观测，钩子记录里缺 `alarm_ours`，所以 57 次尝试报“子进程钩子安装异常”、4 次报“有库超时日志，却没有计时信号记录”；后来的版本已补上（`legacy_recheck.json`）。
- 跟进。顺序改为默认 → 参照 → 时限 2/10 秒 → 原设置重放 3 次 → 随机 1% 重测。重放集合取默认有事件、参照有事件、主指标翻转、时限敏感变化（2/5/10 秒的裁定不全相同，含未裁定）和默认单行超过 10 秒的并集；单行超过 10 秒也进条件实验候选，预算终止的行照旧不算。不调用判分器的流程替身复现了审核里的两行反例：修订前两行都没重放、候选为空；修订后两行各重放 3 次，三步各 4 秒那行进候选（`flow_check.json`，10 项）。
- 置信界。改用正则化不完全贝塔函数（对数前因子加连分式）反演尾概率。n=93,733、k=1,000 时单侧 95% 下界、上界为 0.01012254、0.01123725，与审核给的独立值相同；修订前两个都下溢成 0.00791802。与对数逐项求和比，最大相对差 2.8×10⁻¹⁰；mpmath 50 位核对界上的尾概率等于 0.05；k ≥ 111、k+u ≤ 4 两条门槛不变（`stats_check.json`，9 项）。原有 27 项统计单元测试仍全过。
- 准备与分析环节的保护。新增 `stepguard.py`：构建任务、算版本锁、分桶合成、段间统计和最终汇总都在同一套整机保护下跑，记录写运行目录的 `guard-steps.jsonl`。控制测试 6 项：正常完成；读数失败、内存压力严重、小规模真实超预算（预算设成本进程 footprint 加 64 MiB，再写满 256 MiB）都会停下；压力警告时停在检查点，解除后继续；主线程不走检查点时，2 秒宽限后进程直接退出，退出码 6（`stepguard_check.json`）。没有做耗尽整机的测试。
- 续跑版本。第一次运行把执行代码、被测源码、依赖版本、Python、抽样映射和十个数据分片的 sha256、预先抽取写进 `run.json` 的锁，并存一份代码快照；每段另写 `pass_spec.json`（行集合、模式、时限参数、子进程上限）。续跑时逐项核对，不同就停下，不删记录、不重判；只改注释或文档字符串的代码要在 `compat.json` 登记说明，而且语法树相同才放行。单元测试 25 项（`resume_check.json`）。真实入口上：同版本续跑八段都复用、结论相同；改子进程上限、改锁里记的 sympy 版本、某段缺 `pass_spec.json` 都被拒绝（`main_test/resume_e2e.json`，5 项）。
- 长尾。只给带假设的情景，见上面资源试跑一段和 `tail_scenarios.json`。修订后的试跑预热 2.50 秒，同样算出 497.5 秒、38.6 小时与 995.0 秒、77.3 小时。
- 修订后重跑。完整自检 90 项：通过 89，未通过 0，未验证 1，用时 261 秒（`selftest/report.json`）。未验证的是 G2“RSS 下降时 footprint 保持”：这次 RSS 一直没降，不为此制造整机内存压力，RSS 下降的证据仍是独立探针。试跑 1,003 行五道关卡全过：开关对照 500 行逐行分数相同，各段没有观测不完整的行，P=1（`pilot/report.json`）。这次开关对照的每行耗时差 p99 是 9.6 毫秒（修订前 1.3）；同样 500 行先关后开再跑一遍是 1.1 毫秒；观测开启时记录的库步骤之外的耗时，三次的均值都是 0.6 毫秒；修订后试跑差值最大的一行，开的那一遍记录的库步骤就用了 251 毫秒，关的那一遍整行才 117 毫秒（`pilot/switch_repeat.json`）。这与库计算时间波动的解释相容，但日志处理和计时信号记录可以发生在被计时的库调用内部，DEBUG 级别在调用期间也生效，所以 0.6 毫秒不代表全部观测开销，也不能据此隔离或排除库调用内部的观测开销（按方案第 15.3 节收窄；原先写“差值大的几行是库调用本身慢了”说过了头）。主测量脚本测试（试跑集 300 行加 5 条注入行；P=2、子进程上限 768 MiB，不等于主测量 3 GiB 上限下的并发验收）：5 条注入行的裁定都对，重放集合 5 行，候选是外层超时与池损坏两行，300 行真实回答的结果与修订前相同（`main_test/report.json`）。

**10-07 晚第二次修订**（Codex 复核见申请季方案第 15 节，修订说明见第 16 节；代码 `70dc00e`、`6c6cf9b`，证据都在 `results/s2_rev2/`，`results/s2_rev1/` 原样保留）：
- 工作块结束时漏停。`stepguard.py` 的工作块正常结束改为等同最后一个检查点：暂停就等，停止就抛 `StepStop`；先让后台线程结束、等它退出，再读状态，收尾那次采样才查到的停止也抛；线程 10 秒内没退出按停止处理。主线程已带着别的异常离开时原样传出，结束记录写 `outcome=error`、异常摘要和 `pending_stop`。保护控制测试 13 项全过（原 6 项不改，新增 7 项，含修订前代码在同一情景下漏停的对照；`stepguard_check.json`）。流程替身 12 项全过，新增两项：段间统计结束时要求停止，下一段不执行、已完成段的文件不变；修订前代码同一情景八段照常全跑（`flow_check.json`）。
- 真实入口（`main_test/resume_e2e.json`，8 项全过）：在主测量脚本测试的副本里删掉 retest 段和报告，用真实入口续跑，“构建任务与生成版本锁”做完后注入停止：退出码 7，没有核对版本锁、没有派发 retest、没有写报告，副本里原有文件逐个不变；之后不注入照常续跑，只重跑 retest，各表与第一次相同。
- 版本锁日志。“构建任务与核对版本”改名“构建任务与生成版本锁”；比较单独成“核对版本锁”一块，拒绝续跑时它的结束记录写 `outcome=error`，`error` 里列出不同项。
- 测量进程收尾的退出码。第二次修订后第一次重跑主测量脚本测试时，外层超时那行恰好是测量进程的最后一行：收尾离杀子进程只有 0.1 毫秒，读不到退出码，那行在默认和第二次重放里记成“观测不完整（未裁定）”，合成行核对因此不过（结果留在 `main_test/attempt1-70dc00e/`）。这个时序问题从 `99b086d` 起就有。`obs.py` 的收尾改为先等还没有退出码的子进程，合计最多 5 秒（`6c6cf9b`）。重跑后 16 个测量进程收尾都记到了退出码，注入行与 300 行真实回答的结果与第一次修订后的测试相同，只有耗时数值不同（`main_test/report.json`）。因为改了测量进程，完整自检重跑：90 项，通过 89，未通过 0，未验证 1（仍是 G2，RSS 没降；`selftest/report.json`）。续跑单元测试 25 项全过（`resume_check.json`）。资源试跑和开关对照没有重跑。
