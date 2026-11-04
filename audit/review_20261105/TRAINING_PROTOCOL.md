# 控制训练方案与最小试跑（2026-11-05审查轮次；最小试跑于11-04执行前规定）

## 目的与验收

新增证据只检验“失败处理会实际改变可训练模型的梯度和参数，以及固定预算下的干净评测结果能否测出”，不把优势模拟称为训练。最小试跑验收：至少一个公开小语言模型，真实反向传播与优化器更新；oracle/no-fault、失败记零、剔除、校准估计四条路径；相同初值、任务划分、步数、采样规则；记录非零梯度、参数差异、干净评测和耗时。预设最多3个种子、每臂24步；不因结果好坏增减。只跑MCAR p=0.25作为代码/资源可行性试验，不给显著性或真实数学RLVR收益结论。内存压力4即停止，1/2继续。先串行单设备运行，不同时启动第二个训练。

## 最小试跑（与主论文测量分开）

- 模型：HuggingFaceTB/SmolLM2-135M-Instruct，revision `12fd25f77366fa6b3b4b768ec3050bf629380bac`；单个权重269,060,552 bytes。仅本地下载，LoRA r=4、alpha=8、q_proj/v_proj、dropout=0；冻结其余权重。MPS float32，单臂在内存，逐臂重置同一adapter初值。
- 任务：所有a,b∈{0,…,19}的400个算术提示，答案是(a+b)的末位十进制数字。固定NumPy seed 20261105打乱，200训练、100校准、100测试。各集合提示不重合，但数字组合和模型预训练并不保证互斥。
- 行为策略是语言模型在提示最后位置对10个单token数字logit归一化得到的受限策略。每次4个提示，各采8个数字。无自由文本推理、无真实Math-Verify超时、无完整verl训练器。
- 算法：每个新on-policy组只更新一次，使用sample-std组优势与score-function损失；全组方差为0时优势0，剔除后单个幸存者按verl约定 mean=0,std=1。加入固定β=0.01的相对初始受限策略KL。它是实际语言模型参数上的组归一化策略梯度，不是多epoch clipped PPO/完整GRPO实现。
- 故障注入：在采到的答案之后、评分之前按预先随机数使每行独立以0.25缺失。精确算术oracle仅供no-fault臂与事后评测。故障掩码独立于答案；各臂同一seed/step/位置的均匀随机数相同，策略改变后实际动作可以不同。
- zero：缺失奖励置0，进入组统计和损失。exclude：缺失行不进入组统计和损失，分母用幸存行；全丢组跳过。calibrated：用独立校准集拟合的冻结置信度可靠率q代填缺失奖励，保留组和损失。校准特征只用冻结基模型对候选数字的受限概率；10个等宽置信度bin，各bin加Beta(1,1)平滑。校准标签是另外100个提示的所有10个候选，失败训练行的oracle绝不进入q；因此这是均值代填启发式，非真值、非无偏GRPO保证。oracle：所有奖励用精确算术，不注入缺失。
- 每臂24步、AdamW lr=3e-4、grad clip=1、seed∈{11,22,33}。每步使用该seed固定抽取的4个训练提示。step0/12/24对100个测试提示报告greedy精确正确率、期望oracle奖励、KL、校准Brier；每步报告实际失败/正例/幸存行、梯度范数、参数更新L2。固定预算比较保留各臂实际少用的行，不靠重采样悄悄补足。
- 交付脚本、结果与环境，模型权重留在仓外cache；不提交权重和数据。只可报告此有限动作算术任务，不推到长推理、自然故障或下游基准。

## 下一阶段足以检验论文问题的训练

1. 先固定任务与真值：数学用公开、有清洁答案且能人工复核争议的训练/测试分割；代码用独立隐藏测试。固定抽取/规范化，真正生成推理，保留原始rollout、预算、failure class。用完全无故障oracle scorer定义clean baseline；再保留同一scorer在资源失败时的availability标签V，数学对错Y与V分开。自然超时组中仍不可判定的Y不能“长超时=1”补真值。
2. 四个必需臂：clean/oracle；zero（所有组和token分母不变）；exclude（从组moments和token loss贡献剔除，<2幸存者跳过，另列verl单幸存者敏感性）；calibrated（随机审计子样本拟合q(Y=1|X,V=0)，按题cross-fit，不用测试标签）。正式比较的共同分母与deployment式active分母分成预定的二因子检查，细则见下文，不能混为同一drop政策。loss-only mask仅作冻结rollout机制诊断；resample-to-G属于生成预算不同的次级问题，不挤入主要四臂。所有臂保持生成token预算、优化器、KL、batch、checkpoint、评测频率一致；同时报告wall time/被丢token，防止把预算增加当算法收益。
3. 三类注入分别运行，不混成一个率：M1 MCAR 1/5/10/25%；M2 按长度/表达式复杂度/正确性条件选择（预先列logistic propensity，包含有/无oracle知识的合成机制）；M3 共享reference/worker/group整组缺失，用块级故障模拟相关性。注入点既覆盖库内timeout无flag路径，也覆盖wrapper/manager有flag路径；额外oracle-mask臂检查故障探测本身的误检/漏检。先用相同冻结rollout做paired梯度检查，再做在线各自rollout的端到端训练，不能将冻结rollout结果称在线训练收益。
4. 校准估计的条件：在MCAR/可观测MAR且π(X)>0时，可用cross-fit AIPW reward `q(X)+V/π(X)*(Y-q(X))` 对非归一化score-function期望纠偏；必须另测方差、clip与权重截断偏差。当前组sample-std、归一化、PPO clip均为非线性，奖励无偏不推出GRPO梯度无偏。MNAR时q不可由幸存者识别，必须随机抽审失败案例（已知抽样率）或给sensitivity/partial-identification范围；不能承诺校准“修好”。对整组失败，代填可能凭空制造组内信号，应单列并预先决定跳过/审计/重采样。
5. 主要终点：最终固定checkpoint的独立oracle test pass@1（固定解码与prompt），预指定另一个task作外部验证；次要为每生成/训练token的收益、wall time、校准、失败探测、梯度与clean方向的cosine、各难度/长度子群。所有比较使用同一测试题、cluster在题级和种子级；在线rollout不能机械配对动作。报告所有种子、失败臂、95%区间和多重比较处理，不挑best checkpoint。
6. 功效：三种处理对clean基准共有3个主要对比，双侧FWER0.05 Bonferroni α=0.0167。80% power，seed-paired accuracy-difference SD若为1.5/2/3个百分点，检测2个百分点需 `ceil((z_(1-α/2)+z_.8)^2*(SD/2)^2)`≈6/11/24个seed对（正态近似，先pilot估SD，正式采用t/非参数规划）。检测1个百分点约24/42/95。测试题级若独立Bernoulli正确率0.5、两臂保守不配对，2个百分点需要约13,100题/臂；同题McNemar设discordant率q=0.1则约2,620对题。题级样本再多也不能替代独立训练seed；只用3seed属于探索性。
7. 算力与排期：先135M/0.5B LoRA可行性1晚；再单个0.5B–1.5B、短上下文、2–3臂×3seed×小预算用24–48小时测实测吞吐与方差；按`臂×seed×生成token/实测tokens_per_second`推算正式预算，不用参数量直接承诺时长。预算确认后再扩大到6–24seed和独立任务。优先一张24GB/48GB GPU，数据/单个模型下载仍≤3GB；大于3GB在明确授权前不下载。无法在现机完成正式功效时交付pilot和可运行配置，不把未跑排期写成实验。

## 正式训练的可执行细则（在任何下一阶段训练前锁定；不是已执行结果）

### 注入与oracle：F1–F4不改名论文中的M1–M3

所有训练回答先由隔离的精确oracle得到Y，oracle仅交给clean臂、注入器的预定MNAR机制和事后分析；训练器按政策只能读取V=1时的Y。先完成逻辑availability注入以隔离处理政策，再单独做真实wrapper sleep/worker-exit注入；真实进程故障可能波及同池邻居，必须按实际ledger生成V，而非假设每次只丢一行。

| 机制 | 注入规则 | rate与识别边界 |
|---|---|---|
| F1 MCAR | 每个response独立 `P(V=0)=p`，随机数在实验前按seed/step/group/row生成 | p=0.01/0.05/0.10/0.25；主要训练对比固定p=0.05、0.25，其余是预先列出的敏感性条件，不按结果挑选 |
| F2 MAR | `P(V=0|X)=sigmoid(α+log(3)z)`；z为冻结校准池上标准化的输出长度（X在验证失败前已可观测）；另一个预定分层检查用廉价表达式括号/运算符计数 | 对每个p解α，使冻结池平均缺失率为p；rate同F1，保存α、z均值/SD、实际率。X包含z，不含oracle Y；MAR条件由注入器设计保证，不声称自然超时也满足它 |
| F3 MNAR | `P(V=0|X,Y)=sigmoid(α+log(3)z+γY)`，γ固定为+log(4)、−log(4)，α同样按冻结池目标p校准；γ=0是F2嵌套对照 | 正式主分析先固定γ=+log(4)，负向只作预定敏感性；trainer和q不能偷看Y。自然MNAR没有已知propensity，需随机抽审/部分识别，不能用此受控oracle机制冒充已识别自然机制 |
| F4 相关缺失 | 以p对完整prompt组置V=0；另一个独立工程检查按固定worker/chunk块置V=0，块长度/路由在前置协议里固定 | rate同F1，报告response边际率与独立故障块数量。统计按题/块聚类；不把8个同组回答当8次独立故障 |

首个自由生成任务用程序生成的整数/有理数算术，oracle以精确整数/Fraction计算，解析政策在所有臂固定；不以延长Math-Verify时限定义“真正确”。第二任务在预算内再选择可独立裁定的代码或数学集；不能在尚未完成真值审查时预称它是无误oracle。训练/校准/测试按问题隔离，近重复的生成模板参数也分层检查。自然Math-Verify故障另列availability与未知真值，不补为Y=0或Y=1。

### 四臂定义、同rollout诊断与梯度分母

1. 在完全相同的冻结prompt、8-response组、old-policy logprob、oracle Y、故障掩码上，先比较四种奖励处理的真实梯度：oracle=Y；zero=`VY`；drop仅V=1行进moments与policy-gradient分子；calibrated=`VY+(1−V)q(X)`，全部行进moments。q以独立校准问题/随机抽审标签按题cross-fit，输入冻结基模型特征、z与failure class，不能用失败训练行的oracle标签或测试标签。相同audit token/标注预算计入所有臂成本，不把calibrated的额外监督当免费。
2. **主要控制分母**固定为该batch实际生成的有效response token总数M；drop失败行的PG贡献为0，moments只用幸存行，但不因M减少而放大剩余梯度。这个controlled-drop不是框架常用的active-token平均。**部署约定的副比较**将drop改为M_keep（实际幸存token数），其余不变，分开估计“组统计/缺失监督”与“loss重新缩放”的效果。zero/calibrated/oracle的分母都是M。所有臂的KL项用共同M，失败组仍可受同一KL约束；不把“没有PG信号”等同完全无参数变化。
3. group mean/std、epsilon、token聚合（token-mean或sequence-mean只选一个）、PPO clip、importance ratio、KL实现/β、梯度累积、clip-grad、优化器和学习率固定。可改变的只有预定处理与分母因子。drop在<2幸存者时PG置0；single-survivor的verl规则只作预定敏感性。全丢组不偷偷重采样，不因此改变prompt顺序；zero可能仍带KL，calibrated可能由q制造组内信号，均单列记录。
4. 在线训练所有臂同checkpoint、同seed、同prompt/任务次序与采样uniform流、同rollout/token总预算，逐臂独立生成。策略分化后答案不同，这是处理效应的一部分；不能称其后续“相同rollout”或把不同动作强配对。冻结rollout阶段能同组逐梯度比较，在线阶段以相同prompt与训练seed配对结果。oracle clean臂可在各p/机制之间复用同一个seed的训练结果，因为无注入时路径完全相同；若实际配置改变则不可复用。
5. heldout使用固定解码、固定最终checkpoint、独立完整oracle评分，主终点pass@1；test不用于挑q、p、γ或best checkpoint。各题重复解码属于题内抽样，不增加独立题数；各题结果按题cluster，主要政策比较的独立训练单位是seed。报告每个seed的准确率/期望奖励/失败率/生成与loss token/耗时和算法崩溃；不得删除坏seed来提高均值。

### 功效与何时追加seed

当前135M、100题、24步试跑是实现检查，**不**进入正式功效估计或主要训练样本。自由生成阶段先做3–5个独立seed对估计paired差值SD与吞吐；在不知道政策平均差的方差评估下，用预定MDE=2个百分点、80% power、3个主要政策对比FWER0.05重新锁定N。正态近似N=6/11/24对应SD=1.5/2/3个百分点，正式采用t分布或seed级仿真校正，取SD不确定性的保守上界，通常会更多。若只能预算6seed但所需N=24，报告探索性/区间，不声称有足够power。

追加样本只能由预定方差/CI精度目标或预定基础设施恢复规则触发，并在看政策效应或p值前锁定最大N（建议上限24）；不能因为p值不显著就再跑。若pilot与正式协议不同，pilot不并入主检验；若计划合并，须在开始前规定只按盲化方差重估样本量的设计。跑满锁定N即停止；更大预算属下一项研究。算法导致的崩溃/塌缩也是结果，只有明确外部基础设施中断才按锁定checkpoint恢复，保留中断与恢复日志。

### 算力估计与11–2月阶段线

以下均为**尚未测得吞吐的预算估计**，先用真实free-generation pilot替换tokens/s；当前受限单数字60.5秒不能外推长文本吞吐。

| 阶段 | 工作与规模 | 算力/时间估计、完成条件 |
|---|---|---|
| 11月上旬 | 本轮原始事件、schema/consumer测试、arXiv只读脚本、135M真梯度可行性 | 已完成部分见各结果文件；本地单权重269MB。公告需真实ID，不为赶日期猜ID |
| 11月中下旬（申请核心提交窗口） | 固定free-generation数据分割、真值、F1–F4注入、q审计、冻结rollout梯度/分母诊断；本地先1个MCAR条件、≤3GB模型 | 小型本地12臂若每臂约0.5M生成token，总6M；假设MPS 10–40 tokens/s，纯生成约42–167小时，更新/评测另加。故只把少数臂作为可行性测量，长作业nohup、压力4停，不承诺一晚跑完；申请工作不依赖它完成 |
| 12月中旬至1月上旬 | 获得算力授权后，0.5B–1.5B LoRA、真实自由rollout、3–5seed探索；量吞吐、SD、校准漂移，锁正式N | 初始单张24/48GB GPU，batch/microbatch按实测确定；单模型下载若>3GB就不下载。预留2–7天做harness、pilot及失败修正，**不是**已测训练工期。GPU租用/费用须本人另行批准，本方案不租机器 |
| 1月上中旬至1月底 | F1–F4×主要p=0.05/0.25，三处理×Nseed，加每seed一条oracle；分母副比较单列 | 若N=6，主要150run（3×8×6+6），active-denominator drop副比较48run，总198run。假设每run2M生成token，共396M；假设100–400 tokens/s，纯生成275–1100 GPU小时，乘1.5–2覆盖更新/评测≈413–2200 GPU小时。1GPU约17–92天，4个独立GPU约4–23天，另加排队/I/O。均待实测；若N升至24，约4倍，不承诺1月底完成 |
| 2月 | 完成预算内预定seed、独立任务/不同故障结构复核、误差/中断清单、下一版稿件 | 若power所需算力超出已批预算/窗口，交付有界探索性结果与CI，保留正式缺口，不挑结果填上。申请材料只按实际已达到状态更新、遵守各校补件要求，由本人最终采用/提交；研究不保证在任何申请截止前产生训练增益 |

停止条件：本轮固定最小试跑完成、结果有效（无参数更新错误）即停止，不在本轮启动上述正式训练；不为正结果调参。任何数据隔离或资源错误修正后重跑受影响臂，记录失败与原因。
