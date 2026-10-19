# No Free Checker：机器人策略验证器的可用性-可信度权衡——150 篇 verifier 调研精读 + Hermes Evals 体系映射 + microduck 验证器对照

> **来源**：微信公众号（机器人 policy verifier 综述转述）2026-09-10
> **原文链接**：https://mp.weixin.qq.com/s/6iKiNaqkcPQ2JTU3ck2eqQ
> **抓取方式**：桌面 UA curl + js_content 提取，34KB 全文（7 节完整结构 + 150 篇文献的系统性综述）
> **综述原文**：约 150 种机器人 policy verifier 的调研（human / rule-based / learned / model-intrinsic 四类）
> **笔记日期**：2026-09-10
> **关联笔记**：《LLM-as-Judge八模式》《为不信任而设计》《GraphEngineering全景解说-锚点论》《Astra启示与Dyna-2缩放律》（microduck）
> **特别价值**：这是我们 Evals 体系三份笔记（判官八模式→不信任八模式→本文）的**理论终点**——判官问题的形式化表述

---

## 零、结论先行

**综述的核心定理式结论：No Free Checker——verifier 的 Availability（获取判定的成本/时机/频次）与 Credibility（高分代表真实任务完成的程度）呈反向变化，物理世界不存在同时拥有两者的验证器。**

对我们的三重价值：
1. **理论定名**：昨天判官笔记的"确定性检查 vs LLM 判断"边界问题，本文给出了形式化坐标——我们的 notes_eval_gate 六项检查 = 高 Availability/中 Credibility 的 rule-based verifier；content-judge = 高 Availability/低 Credibility 的 learned verifier；用户审查 = 低 Availability/高 Credibility 的 human verifier。**我们上周自发搭的体系，恰好落在这条权衡曲线上**
2. **reward hacking 的机器人版**：第 6.3 节是全文最深——被优化的 verifier 会失效（conformal calibration 的 exchangeability 前提被训练破坏），这正是我们 RL 训练里"ep_len 变好但鸭子位移没变好"的理论解释
3. **microduck 直接映射**：验收看真实功能指标（鸭子位移）而非代理指标（奖励曲线）——本文 §6.2 的"用训练出的 policy 性能衡量 verifier"的同构

## 一、框架忠实还原

### 1.1 两维坐标（Availability × Credibility）

| 维度 | 定义 |
|------|------|
| Availability | 获取一次 verdict 的成本 + rollout 内返回时机 + 发起判定请求的频次（越廉价/越早/越密集 = 越高） |
| Credibility | 高 score 多大程度代表真实任务完成；judgment 容易被博弈/偏向模型自身时下降 |

### 1.2 四类 verifier（判定来源分类）

| 类 | 判定来源 | Availability | Credibility | 代表方法 |
|----|---------|-------------|-------------|---------|
| (a) Human | 人类直接判断 | 最低（人力贵、样本稀） | 最高（直接反映 task intent，但有主观性/不一致） | 偏好对比 / reward sketching / 执行介入 / rollout 校验 |
| (b) Rule-based & Formal | 预定义准则 | 高（查询廉价可复现） | 高（可给 formal guarantees）——**前提是准则/状态估计/动力学假设贴合真实任务** | STL satisfaction margin / goal predicate / CBF 不变证书 |
| (c) Learned & Pretrained | 神经网络输出 | 高（查询低、dense feedback） | 中低（取决于模型精度/校准/泛化） | VIP/LIV 进度奖励 / SuccessVQA / RoboFAC / PRM-as-a-Judge |
| (d) Model-intrinsic | 模型内部已算好的量 | **最高**（几乎零额外计算） | **最低**（信号描述模型自身，与任务真实表现是间接关系） | action uncertainty / latent discrepancy / reachability value |

**规律：判定来源越靠近被评估模型，获取成本越低，但证明 signal 反映真实任务的证据越难获取。**

### 1.3 各类内部的关键方法（选录最有工程价值的）

**Human（§2）四模式**：轨迹对比（RoboArena 双盲排名）→ reward sketching（Cabi，逐帧 0-1 曲线，少量标注训练 reward model）→ 执行介入（HGDAgger 人选时机 / ThriftyDAgger 机器选时机+介入预算 / SiriusFleet 上线舰队+随性能放宽阈值）→ 生成 rollout 校验（GigaWorld1 四级 World Model as Evaluator score）。**共同策略：human verdict 作为 supervision 训练廉价 verifier**。

**Rule-based（§3）三层**：
- 全轨迹：STL satisfaction margin（>0 满足，绝对值=距边界远近；**conformal prediction 校准**给任意 predictor 加统计边界）+ RINSE 几何评分（谱弧长/包络距离，无需任务规约但**平滑≠成功**）+ Eureka 模型写规则（**进化循环里用 ground-truth task metric 校验生成代码**——Code-as-Monitor/ReKep 缺这步校验）
- 终态 predicate：LIBERO 等 benchmark 的 success bit；MimicGen generate-and-verify 闭环（生成万级 trial 只留通过者）；Simple-VLA-RL 用 predicate 做 GRPO 稀疏 reward
- 物理约束：CBF 前向不变性证书（**So 等人的 filter 实验没做神经网络近似的独立验证步骤**——综述点名）；symbolic feasibility check（Text2Motion 在执行前判断 plan 物理可行）

**Learned（§4）三场景**：评估（process-level 帧级 / trajectory-level 整体；PRM-as-a-Judge 输出 outcome+progress+diagnosis 三件套）→ 推理时筛选（RoboMonkey 候选采样+打分，**action error 随采样数幂律下降**；KnowNo conformal 多合理候选时请求人类帮助）→ 反馈进训练（RECAP 通过遥测介入训 value function，**家庭任务吞吐翻倍、失败率减半**）

**Model-intrinsic（§5）**：policy 内部（SAFE 在 VLA latent 上训轻量 predictor，failure pattern 跨任务迁移；MGSelect mask 输入看 token 概率变化）→ world model 预测（latent discrepancy 零样本检测物理不合理；HJ reachability 识别"无论做什么都无法规避失败"的状态）→ 任务选择（ACCEL/PAIRED 的 regret 驱动 curriculum）

### 1.4 第 6 节：验证验证器（全文最深的贡献）

**verifier 的四类用途 × error 传导**：curation（筛数据）/ ranking（排序）/ training reward / runtime gate。前两类候选不访问 score（error 在语料上平均掉）；**后两类候选会主动搜索 score 出错的输入——一小片错误打分区域就能让 verifier 失效**。

**三类 metric**：
1. 固定集一致性（但会漏：分歧来自 verifier 还是 reference / 置信区间 / rollout 类型——GESim 2.0 实测 world-model 生成 rollout vs 真实视频的 8% 准确率差）
2. 训练出的 policy 性能（开销高文献少；**一致性与下游 gain 会偏离——训练主动把 policy 推向 verifier 失效的样本**）
3. 对抗优化下的表现（reward hacking；**Proxy gain that transfers 公式**：训练 verifier 打分差 Δt ÷ 未见 panel 打分差 Δp，=1 全真 / =0 全假 / 负数=越训越差）

**校准失效定理**（对我们最重要）：conformal margin 的 exchangeability 前提——heldout set 与后续样本同总体。**用 verifier score 过滤 rollout 或训练 policy 都会破坏这个前提**：分布被推向 verifier 出错的区域，一次校准下一轮失效。frozen policy 上成立的检测器，用它训练的 policy 上减弱。

## 二、一手源核实

| 综述论断 | 核实 | 依据 |
|---------|------|------|
| No Free Checker 权衡规律 | ✅ 综述原创总结 | 四类 150 篇的分布规律，逻辑自洽 |
| conformal prediction exchangeability 前提 | ✅ | 共形预测标准理论（Vovk 等）；优化破坏分布是已知结果 |
| reward hacking 在 LLM 已充分研究 | ✅ | scaling laws for reward model overoptimization（Gao et al.）真实存在 |
| SAFE/ThriftyDAgger/HGDAgger/Eureka/RoboArena 等代表工作 | ✅ 抽查 6 项 | 均为真实知名工作（Stanford/Berkeley/CMU 系） |
| RoboMonkey 幂律下降 / RECAP 吞吐翻倍 | ⚠️ 未逐字核到原论文数字 | 方向可信，标注为综述转述 |
| CBF 神经近似需独立验证（So 等人未做） | ⚠️ 合理批评 | 综述对原始论文的批评性审读 |

**核实结论**：框架性论断与已知理论一致，代表工作抽查无幽灵；具体数字多为综述转述（标注）。

## 三、批判性审视

1. **Availability-Credibility 权衡是经验规律非定理**：文中用"物理世界很难同时拥有"表述，但混合架构（如 rule-based 校验 learned verifier 的 ensemble）正是在曲线上移动的方法——综述自己在 §6.4 的 panel 协议就是一例。**权衡是默认态，不是宿命**
2. **150 篇文献的覆盖偏差**：robot manipulation 为主（LIBERO/CALVIN 系），legged locomotion 的 verifier（我们 microduck 场景）覆盖薄——运动任务的 success 定义比操纵更模糊，恰是难点
3. **human verifier 的 Credibility 被理想化**：文中承认主观性/不一致，但 §2.1-2.4 全部把 human verdict 当 gold standard——§6.1 自己指出"human 标注自身 error rate 很少被报告"，两处立场有张力
4. **面板协议的成本被低估**：Proxy gain 协议需要"一组 policy 从未见过的 verifiers"——维护独立 panel 的成本在工程上不低，综述未讨论
5. **领域映射（航空）**：CBF 不变证书 = 适航符合性验证方法（MC0-MC9 中的分析类验证）；goal predicate = 功能试验合格判据；**"predicate 出错直接改变 policy ranking" = 试验判据错误导致错误适航结论**——适航审查之所以要求多手段交叉（分析+试验+检查），本质就是 No Free Checker 的工程应对

## 四、Hermes Evals 体系映射（我们已在曲线上）

| 我们的组件 | 综述分类 | Availability | Credibility | 缺口 |
|-----------|---------|-------------|-------------|------|
| notes_eval_gate 六项 | rule-based | 高（零成本跑） | 中（curl 200 ≠ 内容好） | 内容深度判不了（正是放弃项） |
| content-judge rubric | learned | 高 | 低-中 | 无独立 panel 校验 |
| 用户审查（论文/发布） | human | 低 | 最高 | 抽样率低 |
| watchdog / 确定性巡检 | rule-based（formal） | 高 | 高（前提：指标定义贴合真实健康） | 指标错=整链失效（predicate 风险） |
| **golden set** | §6.1 固定集一致性协议 | — | — | **已实现！**（11 篇+周检=verifier 自身的 error 度量） |

**关键自检结论**：我们自发建成的 golden set + 周检 = 综述 §6.1 的第一类 metric（固定 rollout 集 + reference judgment + 一致性比率）。**缺的是 §6.3 的对抗维度**——没有任何机制检测"笔记作者（我）学会讨好门禁"（如写长凑 G1、堆出处凑 G4）。这是诚实的下一步候选，暂不动手。

## 五、microduck / RL 直接映射

| 综述概念 | 我们的实战 |
|---------|-----------|
| ep_len/奖励曲线 = model-intrinsic score（高可用低可信） | 用户铁律"验收看鸭子位移非代理指标" = 拒绝 model-intrinsic verifier |
| 栈内 rollout 评估 = rule-based（真机闭环） | "ONNX 验收=训练 forward 对比+真机闭环"双锚点 |
| Proxy gain 协议 | **3 seed × 4 env（n=12）看 mean±std** = 多 verifier 面板的简化版 |
| reward hacking（重心站 3.4 分 ≠ 走得好） | 站桩 reward-hack 防陷阱 = 我们的血泪教训，综述理论化 |
| ACCEL 任务选择（value loss 驱动 curriculum） | 地形课程扩展可借鉴：优先训 policy 误判的环境 |

## 六、金句提取

> "No Free Checker。"
>
> "判定来源越靠近被评估模型，verification signal 获取成本越低，但证明 signal 反映真实 task performance 的证据就越难获取。"
>
> "policy benchmark 会报告 policy success rate，但这套检测逻辑自身的 error rate 很少被报道。"
>
> "用 verifier score 训练 policy，会改变 verifier 未来接收的数据分布。verifier 把分布推向 verifier 出错的区域。"
>
> "对于 model 识别不到的 failure，model 依旧输出高 score。"
>
> "完成更多 task 的 policy，并不会自动变得更 safe。"

## 七、局限性

1. 微信文是英文综述的中文转述，术语间距（如 satisfaction margin/robustness 混用）可能有损；原综述 PDF 未直接核对（150 篇文献级别，逐篇核对超本笔记范围——已抽查 6 项代表工作）
2. 具体数字（RECAP 翻倍、8% 差距、3.8 个百分点）为转述，未回原论文
3. legged locomotion 覆盖薄（批判章已述）
4. 第四五章领域映射为本笔记扩展
5. 图片为示意图已略（图 1-5 为分类图/表格图，正文已完整转述其内容）

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一、六 | **原文忠实还原**（js_content 提取 34KB，7 节结构完整） |
| 二 | **一手源核实**（conformal 理论 + 6 项代表工作抽查；数字标注转述） |
| 三、四、五 | **批判性审视 + 体系映射**（本笔记扩展） |
