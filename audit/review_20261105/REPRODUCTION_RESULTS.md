# 2026-11-05轮次独立审查交付（实际执行2026-11-04 CST）

基线是GitHub `main` **d9ef9cb3cf50d6b55d9491dd8d8b6adadef7ce7c**，23页 `paper/rewardfail-preprint-2026-11-03.pdf` / `paper/main.tex`。独立clone `/Users/fei/.local/share/rewardfail/review-2026-11-05`，分支 `review/2026-11-05`。没有改申请季、旧clone、锁定数据、已提交手稿或main；没有push/投稿/登录/付费/联系任何人。贡献是Codex本轮执行与分析，不改原稿的人机贡献归属。

## 结果与证据地图

| 主张/原件 | 本轮独立检查 | 结果与边界 |
|---|---|---|
| main.tex:704起的主测量1/18与预算更正；:663–668决策门槛 | `rebuild_events.py`，77个原始parent/child/guard/results等文件，完整8pass；同事件对照新/旧analyze.py | n93,733 k1 u18逐行重建；与正式main_metric整个字典精确相等，原文件前后哈希不变。lower5.4723e-7<1e-3、upper2.97418e-4>1e-4，两个数值门槛均不满足。旧规则同事件u9,573；非warmup更正9,863。`EVENT_REBUILD.md` / `rebuilt_events.json` |
| main.tex:848–900的全答扩展 | 补样本default/reference原始事件同样重建，不只加历史报告数 | 补样本n100,034 k1 u14，formal counts+ids一致；合并n193,767 k2 u32，32条来自21题，两个恢复同题。`rebuilt_complement.json` 的 `pooled`；主/补样本输入均不变 |
| main.tex:704附近error-inclusive敏感性 | 主reference事件逐行查reference error零分 | 16行，u_err34，上端35；不是把这16行宣布为数学错判。主恢复范围与error-inclusive界仍依照原操作定义 |
| default计数与question/event pairs | `recount_derived_records.py`在新解包执行；主/补样本原始事件另行重建 | 主54事件、补49事件、合计103；85零分/18一分；92,287多答题、103有向pairs中84双端事件。`derived_recount.json`。这些是固定记录，不是自然训练发生率或条件相关参数 |
| main.tex:385–411的真实worker failure→manager→assembly→extract_reward | 原13场景、修复13场景重新启动真实本地Ray；驱动/固定答文本/注入器与companion相同 | 原版13个contract结局与保存Linux记录吻合；修复后11个rate_limited场景完成、9个注入场景error列全部到达consumer，2个naive仍abort，原能返回处reward不变。`c1c_mac/summary.json` / `c1c_mac_fixed/summary.json`及注入ledgers |
| 21个局部fixture与完整real-function consumer suite | 重新执行现成suite，未降低断言 | 原型21/21、旧聚合16漏列+3异常；real suite原版exit1、75失败/22通过（预期反例），补丁版exit0、30通过+66subtests、3prototype-only skip。`fixtures.json`、`execution_checks.json` |
| main.tex:920–973的人工标签答案集 | E3-L原驱动在本机macOS新执行，固定CSV/wrapper hash，4个pass共22,176次真实评分 | 每条score及event标记均与历史一致。raw分歧1530（1487 positive-label/score0，43 negative-label/score1），boxed204（113/91）；放宽时限不改score。`e3_mac/report.json`及4个新trial gzip。标签未重新人工裁定，disagreement不是确定的verifier error |
| main.tex:1198–1358的优势例子、72组×2,000 draws政策表及supplement | 重新执行run_offline_policy.py与supplement.py，另跑9个既有单测 | 新旧JSON逐值完全相同；与真实verl优势函数288例max差2.90145894e-7；枚举131,072个failed-correct案例0违例。`execution_checks.json`。仍是优势计算，不是梯度 |
| 168个正文/表格数字定位检查与21反例 | 当前checker和countertests重新执行 | 168/168、21/21；源报告一致性，不替代原始实验。`paper_numbers.json`。另7个prefix tests通过；预算更正测试用原测试函数，仅将旧版本loader指向已提供archive，51项0失败 |
| 二项上界算术 | 另写log-binomial有限和CDF二分反演，与冻结report使用不同数值实现 | upper0.00029741840261100555，与冻结值差−3.77e-16；这不消除二项工作模型的假设 |
| 主PDF与arXiv源包 | 23页全部渲染接触页查看，第9/16页表格放大核对；tar三项与当前源字节比较 | 23页可读无截断/重叠；tar的main.tex/main.bbl/refs.bib与当前完全相同。没改PDF、没在本轮重编TeX，不把它称新编译验收 |

重要收窄：主/补样本的更正原始事件**在本机可重建**，但这些事件仍不在既有公开companion，公开读者的输入缺口依然存在。此分支新增的是可核验脚本、输入哈希、重建转移与结果；不能只拿一次成功标志宣称公开原始数据复现已解决。更长超时仍不是真值。

## 实际命令、退出码与环境

所有长作业均以nohup运行，新clone为cwd（c1c另用tmp companion为cwd），输出指定新目录。`execution_checks.json`列实际exit、日志SHA、环境、12项实质对照。核心调用如下；`COMP/AUTH/OLD`是系统tmp中的新解包，已在本轮结束清理，复核时重新解包即可。依赖树保留在 `/Users/fei/.local/share/rewardfail/review-deps-20261105/`：`verl-pr8015`是固定0c4c3d4 git archive；`verl-fixed`在新副本上应用既有0001/0002；`verl-ray`及`verl-ray-fixed`是独立git clone，未修改旧树。

```sh
# main：exit 0；完整命令与原件哈希见EVENT_REBUILD.md
python3 -I -B audit/review_20261105/rebuild_events.py --companion "$COMP" \
  --run /Users/fei/.local/share/rewardfail/stage2/runs/main-20261007-202545 \
  --old-analyzer "$OLD/rewardfail/s2/analyze.py" \
  --formal-report "$COMP/results/s2_main/report.json" --out NEW_MAIN.json

# complement：exit 0；counts和recovery/unresolved id sets比较
python3 -I -B audit/review_20261105/rebuild_events.py --companion "$COMP" \
  --run /Users/fei/.local/share/rewardfail/stage2/runs/e2-complement-20261008-codex \
  --formal-report "$COMP/results/s2_e2/report.json" --formal-key extension \
  --segments default reference --main-rebuild NEW_MAIN.json --out NEW_COMPLEMENT.json

# real functions：原版exit 1是预期反例；固定树exit 0
PYTHONPATH="$VERL:audit/upstream_chain" "$RF_PYTHON" -B -m pytest -q \
  -p no:cacheprovider audit/upstream_chain/test_reward_chain.py

# real Ray：parent与Ray worker必须使用同一VERL树；两次正确执行均exit 0
# COMP内third_party/verl-pr8015的链接也必须指向该树。
PYTHONPATH="$VERL" "$RF_PYTHON" -B "$COMP/experiments/c1c_chain.py" --all --out NEW_RAY_DIR

# E3新评分：exit 0（driver原名含linux，此次实际OS是macOS）
PYTHONPATH="$VERL:audit/experiments/e3_linux" "$RF_PYTHON" -B \
  audit/experiments/e3_linux/run_e3_linux.py --csv "$GOLD_CSV" \
  --historical "$COMP/records/e3-20261008-codex" --out NEW_E3_DIR

# offline计算与supplement：均exit 0
"$RF_PYTHON" -B audit/experiments/offline_policy/run_offline_policy.py \
  --csv "$GOLD_CSV" --out NEW_OP_DIR --verl "$VERL"
"$RF_PYTHON" -B audit/experiments/offline_policy/supplement.py "$GOLD_CSV" \
  audit/results/offline_policy/results.json NEW_SUPPLEMENT.json
```

实际 `RF_PYTHON=/Users/fei/.local/share/rewardfail/venv/bin/python`，`GOLD_CSV=/Users/fei/.local/share/rewardfail/data/rlvr_group_correlation/data/gold/gold_set_1p5b_manual_labeled.csv`。macOS arm64，CPython3.12.8；具体torch/ray/transformers/Math-Verify/SymPy版本保存在environment。不是新机器/全新venv/Linux再复现。E3与部分Ray场景同期执行，耗时只作本轮描述，不作性能比较。记录到的压力1/2，无观测到4；pilot每步记录均1。

简洁错误记录：首次主重建误把原run中旧u9,573 report作为比较对象，故exit1；显式指定更正formal report后完整重跑exit0。首次数值countertest漏CLI参数报错，按usage重跑21/21。预算测试原封装不能读取旧git历史，仅替换旧source loader后51/51。首次patched Ray命令漏父进程PYTHONPATH，造成未补丁parent与补丁worker混树，**不进入科学结论**；按文档统一两端树后完整重跑13场景通过。不是把该误调用当新库故障。

## 训练、文献与公告脚本的交付

- [TRAINING_PROTOCOL.md](TRAINING_PROTOCOL.md)：F1 MCAR、F2可观测MAR、F3 oracle-controlled MNAR、F4组/worker相关缺失；三处理与oracle、同组/seed/frozen rollout/在线分化、共同与active分母、heldout、seed级功效/何时加seed、≤3GB本地与GPU预算估计、11–2月阶段线。后续完整方案是本轮形成的计划，不是已跑结果。
- [PILOT_RESULTS.md](PILOT_RESULTS.md)、`pilot/`、`pilot_train.py`：269MB真实135M LM，230,400 LoRA参数，12臂/288次反传与AdamW，全部真实更新；oracle最终均值16%，三处理各15.33%。未建立优劣，不能拿3seed短任务作普遍训练结论。
- [LITERATURE_AND_REVIEW.md](LITERATURE_AND_REVIEW.md)：6篇近一年新增近邻、6篇既有引用重读、短引文/固定版本链接/真实访问日、最强8条审稿质疑及最小补救。没有用原作者训练结果替代自己的证据。
- [ANNOUNCEMENT_CHECK.md](ANNOUNCEMENT_CHECK.md)、`check_arxiv_announcement.py`、`test_announcement.py`：只读比较公开编号/版本/题目/作者/摘要/PDF页数；7个离线测试通过，真实他稿网络负对照exit1，提交号拒绝exit2，终稿哈希不变。真实rewardfail arXiv ID未提供，公告比对未执行。

负对照已明确拒绝：**延长时限得1不是数学真正确；优势模拟和本轮受限动作pilot都不能证明三策略提升真实RLVR准确率。**

## 未运行/不能升级的部分

未重新从OpenR1完整文本给主93,733/全193,767条长答案全量打分；本轮是完整原始事件重建，加独立labelled-set真实重评分。未新跑u18的300秒诊断、三heavy共享池矩阵及14个追加控制，也未在本轮Linux重新评分；它们的历史原始/报告记录和边界不因此改成新实验。未运行带自由文本生成的完整verl trainer；新训练是明确受限的一位数字策略梯度可行性试验。未证明自然训练发生率、真实数学FN率、训练收益、通用噪声阈值、跨平台abort因果或任何录取/发表结果。实际公告还要等有效公开ID。

这些未跑项已在证据地图分开标明，不把保存报告的PASS当新的复跑。稿件后续若采用本轮增强，仍需作者决定公开哪些必要原始输入、核授权，并完整验收新版本；本轮没有改已提交稿或申请稿。
