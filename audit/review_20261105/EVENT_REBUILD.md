# 原始事件独立复算（2026-11-05审查轮次，实际执行起于11-04 CST）

审核对象：GitHub `main` `d9ef9cb3cf50d6b55d9491dd8d8b6adadef7ce7c`，23页稿 `paper/main.tex` 与 `paper/rewardfail-preprint-2026-11-03.pdf`。新clone `/Users/fei/.local/share/rewardfail/review-2026-11-05`，`review/2026-11-05`。申请季与旧clone全程只读。本记录供研究审核，不是新论文版本或申请稿批准。

## 可以改变的证据限定

**本机现在已从完整原始事件重建主测量的更正结果，不再只有报告级核对。** 77个原始输入文件来自仓外保留目录 `/Users/fei/.local/share/rewardfail/stage2/runs/main-20261007-202545/`；`rebuilt_events.json` 逐个记录绝对路径、bytes与SHA-256，并在结束重新哈希，`inputs_unchanged=true`。这些原始事件仍不在GitHub主分支/companion中；公开读者仅靠现有分发包仍不能重建。此区别必须保留，不能因本机成功就说公开复现缺口全闭合。

结果：`n=93,733, k=1, u=18`；`upper_one_sided_95_k_plus_u=0.0002974184026113824`（0.02974184026113824%）；`[k/n,(k+u)/n]=[0.000010668601239691463,0.00020270342355413782]`。与companion中**更正后**正式报告的整个 `main_metric` 字典精确相等，退出0。所有8个pass严格序号检查均无file problems/重复结果。未重新调用Math-Verify，也未重新生成回答。

| pass | 重建的非warmup行 | 与原目录 retained rows 的class差异 |
|---|---:|---:|
| default | 93,733 | 0 |
| reference | 33,487 | 9,863（旧 retained rows 未应用预算归因更正） |
| limit2s / limit10s | 各928 | 各0 |
| replay1 / replay2 / replay3 | 各9,898 | 各0 |
| retest | 963 | 0 |

u=18逐行组成：14 comparison timeout、1 reference-parse timeout、1 guard-stopped、2 interrupted-twice。更长时限恢复的唯一行 `m-377a40b9adf29ef8` 由 comparison-timeout零分转为1；这仍不是数学真值。另16个reference error零分由事件逐行重建（3 comparison errors在预算更正后重现），error-inclusive `u=34`、upper_count=35得到独立支持。

同一批reference事件、同一新report规则，换用旧分析器得 `u=9,573`。新旧非warmup转换9,863行：9,551→normal0，305→score1，3→comparison-timeout，3→comparison-error，1→answer-parse-error。warmup另计，不能把全行308个score1与非warmup305个混用。主稿汇总中全行更正9,866与非warmup9,863正是这个差别。

## 事件归并逻辑与原始版本

- 更正后分析器SHA-256：`f6e70c6c1f65e3d7d307cc25dbc795cad689c01a7fde58383e21ea79d3760e1a`，来自当前companion `rewardfail/s2/analyze.py`，未修改。
- 旧分析器SHA-256：`a8fa21e2b041c327ac5fe2bd8144b3b1c3bc2cc8470cfe994c9550bb63248745`，来自author-inputs `e29d296` 的 `history/9a88991/code.tar.gz`，未修改。
- `summarize_stream(strict=True,batch=1000)` 读取parent `obs-*`、child `child_logs/child-*`、guard、results、warmups及interrupts；parent seq、child fseq、任务序列、worker/pool generation、pid与返回时间跨层核对。先分桶后逐桶综合，不加载整个807MB事件树。
- 原目录每个被消费文件只读symlink到 `TemporaryDirectory`；`_buckets` 与 reconstructed rows只写镜像，退出自动删除。没有把原目录传给会写 `_buckets` 的分析器。
- 新预算归因只把guard kill归到被杀时尚未完整返回的尝试：完整关联的子侧task_end与父侧wait_end两者较晚者须比kill早至少1秒。旧规则把同一pid/池代判过的历史任务一并标为预算终止。
- 然后用未修改 `report.main_metric` 配对default/reference class。更正report显式指定；原run里的 `report.json` 仍是旧 `u=9,573`，不能误当正式更正值。

## 精确命令和执行结果

先用当前 `audit/scripts/safe_unzip.py` 把companion解到新的系统tmp目录 `COMP`，把author-inputs固定提交解到 `AUTH`，将旧code.tar.gz解到 `OLD`。下面参数中的原始 `--run` 不要改为工作输出路径，也不要直接在它运行上游脚本。

```sh
python3 -I -B audit/review_20261105/rebuild_events.py \
  --companion "$COMP" \
  --run /Users/fei/.local/share/rewardfail/stage2/runs/main-20261007-202545 \
  --old-analyzer "$OLD/rewardfail/s2/analyze.py" \
  --formal-report "$COMP/results/s2_main/report.json" \
  --out audit/review_20261105/rebuilt_events.json
```

实际运行cwd为本clone，nohup启动，退出0。首轮只比较了原run的旧report，因此退出1；这是比较对象错误，未改事件或规则。改为显式 `--formal-report` 后重新完整复算，退出0。任何压力4会在下个5000条读事件/分桶检查点停止；本轮一直1。

同时独立重新执行当前主分支提供的分发检查：

| 命令（cwd如注明） | exit | 结果 |
|---|---:|---|
| `experiments/check_artifacts.py --index package_manifest.json`（COMP） | 0 | 724文件、32报告值匹配 |
| `experiments/compare_runs.py`（COMP） | 0 | 两轮13个保存注入场景一致；这是保存记录检查，不是新注入 |
| `experiments/audit_public_evidence.py`（COMP） | 0 | 12/12公开包一致性检查 |
| `audit/scripts/recount_derived_records.py COMP` | 0 | `derived_recount.json`，主/补样本default记录193,767，main 54事件、complement49事件，标签重推无差异 |
| `audit/scripts/check_paper_numbers.py . COMP AUTH` | 0 | `paper_numbers.json`，168/168，源值到正文/表格定位；仍是数值一致性而非全部原始实验复跑 |
| `audit/scripts/test_check_paper_numbers.py . COMP AUTH` | 0 | 21/21反例；首次漏CLI参数报错后按usage修正 |
| `audit/scripts/test_recount_main_prefix.py` | 0 | 7/7 |
| `python -m unittest test_offline_policy`（offline_policy目录） | 0 | 9/9 |

## 必须拒绝的负对照

> “延长超时后恢复的每个答案都是真实数学正确答案，并证明三种奖励处理可以提升真实RLVR训练准确率。”

**拒绝。** 恢复表示固定评分器在较长预算下返回1，不是独立数学裁定；主论文只测固定回答与离线优势，不含训练。另行最小训练pilot即使完成，也只覆盖受限动作算术、合成MCAR缺失和很小预算，不能支持三种处理普遍提升真实RLVR准确率。
