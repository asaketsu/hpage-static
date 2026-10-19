# ROLT 稳健运动 Transformer——足式机器人 OOD 泛化的网络结构路线（MLP vs Transformer 判据）

#强化学习 #足式机器人 #transformer #sim-to-real
> 探索日期 2026-09-17 ｜ 兴趣等级 L3 ｜ 来源 4 篇 ｜ 前序：2026-09-15-rl-policy-architecture-selection（本篇为其文献补充：Transformer vs MLP 的实证边界）

## 核心问题

DUCK 正在跑 G8T/G9T（Transformer 策略）与 G8/G9（MLP 策略）的四路对照。mlp 和 transformer 哪个"更好"是个错误问题——正确问题是**在什么失效模式下 transformer 的结构归纳偏置换成 MLP 换不来的鲁棒性**。ROLT（arXiv 2507.04039，IROS 2025 相关工作线）给出了目前最清晰的实证答案之一：不是更快收敛、不是更高 reward，而是**OOD 动态与感知噪声下的泛化**。

## 核心发现（5 条）

1. **Body Tokenization 实现跨肢体知识共享——"举一反三"实证**。每条腿一个 token（含该腿 10 步观测历史：关节位置/速度/上一步动作+基座 IMU），A1 四足仅在"右前腿跛行"单一故障下训练，测试时换任意其他腿跛行仍能走（20s 行走距离 14.28m vs RMA 1.83m，首摔时间全部 20s 满格）。MLP/RMA 结构上做不到：跛行经验锁死在训练过的那条腿的参数里。
2. **位置信息不用可学习 PE，用 action token 数据依赖查询**。传统给腿 token 加 learnable position embedding 会让各腿策略异化（Module PE 消融成绩掉到接近 RMA）。ROLT 把上一步动作线性嵌入为 action token，腿 token 通过 attention 从它推断自身空间位置——位置信息随数据流动，不写死进参数。这是跨腿迁移的关键机关。
3. **Consistent Dropout：rollout 和 update 用同一 mask，使大 dropout 率在 RL 中可用**（feature dropout 0.1 + PE dropout 0.75）。PE dropout 0.75 意味着训练时 75% 的地图 patch 位置嵌入被换成单一共享向量——逼着网络靠本体感觉与外感的 attention 交互推断地形，而不是死记 patch 坐标。干净观测训练，测试时直接抗高频/低频感知噪声。
4. **真机零样本迁移三个 OOD 场景全胜 RMA**（Go1）：电机弱化+锁腿 2.8m vs 0.0m、拖箱 1.5m vs 0.4m、前脚绑旱冰鞋 4.8m vs 1.2m。训练只见过一种腿故障。**网络结构设计可以替代 elaborate 域随机化的一部分**——训练分布有限、结构泛化兜底。
5. **工程上极其轻量：2 层 encoder、hidden 160、单卡 3090 训练 4 小时（A1）/6 小时（六足）**。与"transformer 策略=大模型=训得慢"的直觉相反——DUCK 实测 Trans~10 it/min vs MLP~6.4 it/min（Trans 反而快），ROLT 证明轻量 transformer 在足式上完全可行。但注意 UniLegs 的对照审稿：宣称 transformer 蒸馏稳定优于 MLP 的证据与噪声不可区分——**单任务无 OOD 需求时 MLP 仍是默认安全选择**。

## 关键概念

### ROLT 架构（token 化细节）

```
腿 token:  e_li = MLP(s_li)           # s_li = 第 i 条腿 10 步观测历史
action token: e_a = W_a·a_{t-1} + b_a  # 数据依赖的"位置查询"
本体 token 序列: e_prop = [e_l0..e_l{L-1}, e_a]
外感 patch: 高度图切 12 patch → 线性投影 + patch PE（训练时 75% 被 dropout）
输入: E0 = [e_prop, e_h]  →  2 层 transformer encoder（hidden 160）
输出: 腿 token 线性解码 → 各腿关节目标角 → PD 控制器
```

### 训练配置

- PPO，IsaacGym legged_gym，4096 并行环境，400M 模拟步
- 奖励表（与 DUCK 高度同构）：xy 速度跟踪 1.5 / yaw 0.5 / z 速度 -2 / action rate -0.01 / 关节力矩 -2e-4 / 足部腾空 +1 / 关节偏离默认姿态 -0.04
- A1 训练含健康行走+右前腿跛行（锁小腿关节）；六足训练随机禁用 3 个指定关节之一（力矩置零）

### 与 DUCK 的结构性对照

| 维度 | DUCK G8/G9 (MLP) | DUCK G8T/G9T (Trans) | ROLT 启示 |
|---|---|---|---|
| 架构 | 61→512→256→128→14 MLP | Transformer 变体 | G8T/G9T 若是整帧观测（非 per-leg token），跨腿共享的机关不存在，T 的优势只剩时序注意力 |
| OOD 场景 | 换执行器域（3025 vs xl330）已实证零迁移 | 同左 | ROLT 的 token 化是结构化域共享；换电机=全肢体同变，token 化收益待验证 |
| 感知噪声 | 观测基本干净 | 同左 | 若真机 IMU 噪声大，consistent dropout 是免费保险 |
| 首要收益证据 | 站立/速度课程 | 待 G9T 数据 | MLP 已够用则 T 是负债（UniLegs 教训） |

## 与现有工作的关联（改进建议）

- **P0 — 检查 G8T/G9T 的策略网络是否做了 per-leg tokenization（✅ 已验证 2026-09-17 04:15）**：读了 `duck-p3-pilot/duck_p3_pilot/models/transformer_model.py`——`DuckTransformerModel` 是**整帧 temporal attention**：61D obs `input_proj` 线性投影 → 64 帧滑窗（50Hz 下 1.28s）temporal attention，每帧一个 token；另有 height_scan/command token 经 cross-attention 的试点变体（§331）。**没有任何 per-leg / per-limb tokenization，ROLT 式跨肢体共享机关不存在**。结论：①G8T/G9T vs G8/G9 的对照差异只能落在"时序历史建模"维度（对标 Radosavovic causal transformer 路线，非 ROLT 路线）；②"单踝故障泛化"（id5 损坏场景）的 token 化结构优势在当前 T 变体上不成立；③若未来做 id5 类故障鲁棒，需改 token 化——把左右腿 5 关节各自成 token 是一个 2-token 起步的最小改动。
- **P1 — V5+ 配方加 consistent dropout 消融**：feature dropout 0.1 成本为零（PPO 已有 rollout/update 双阶段），对真机 IMU 噪声鲁棒性是 DUCK sim-to-real 的明确短板（STS 舵机 + 滑齿漂移的观测噪声）。rolt 的 PE dropout 不适用（DUCK 无高度图），feature dropout 适用。
- **P1 — action token 数据依赖位置查询模式可移植**：DUCK 双腿对称结构（左腿故障时右腿经验可复用）是 token 化的天然受益体，id5 损坏后"右腿带左腿"的场景即 ROLL stiffness test 的镜像。
- **P2 — 更新 rl-policy-architecture-selection skill**：补 ROLT 实证边界——"MLP 默认；需要跨肢体/跨故障泛化或感知噪声鲁棒时选 token 化 transformer；整帧 transformer 无结构性收益证据"。

## Actionable Insights

1. **架构选型三问**（从 ROLT+UniLegs 综合）：有无跨肢体泛化需求？有无感知噪声风险？单任务性能是否已达标？三问全否 → MLP；任一是 → token 化 transformer（不是任意 transformer）。
2. 轻量 transformer（2 层/160 hidden/4-6h 单卡）在足式的成本被高估，DUCK 的 Trans~10 it/min 与此吻合。
3. "训练分布有限+结构泛化兜底"是域随机化之外的第二条 sim-to-real 路线——对 DUCK 这种无法穷举真机故障模式（滑齿/过流/断电漂移）的场景尤其相关。

## 关键风险与盲点

- 【官方验证级，但范围有限】ROLT 的 OOD 全部是"腿故障/外感噪声"两类；对 DUCK 的核心 gap（执行器域差 kp/力限/电压）未覆盖——token 化共享解决"哪条腿坏"，不解决"每条腿都变了"。
- 【社区复现级】UniLegs 审稿指出同方向"transformer 优于 MLP"的中心结论与噪声不可区分（种子方差大）；ROLT 未报多种子下的统计显著性细节，damage 表中部分格 ROLT 与 Module PE 差距在一个标准差内。
- ROLT 依赖高度图外感 token；DUCK 纯本体感觉，PE dropout 机制不迁移，只有 feature dropout 迁移。

## 一页速查

> **ROLT = body tokenization（每腿一 token，10 步历史）+ action token 位置查询（弃 learnable PE）+ consistent dropout（feature 0.1/PE 0.75）**
> **核心证据**：单故障训练→任意腿故障测试 14.28m vs RMA 1.83m；真机三 OOD 全胜；2 层/160 hidden/单卡 4-6h
> **机制**：位置信息数据依赖化→跨腿共享；同 mask rollout/update→大 dropout 可用→抗未见噪声
> **选型判据**：跨肢体泛化/感知噪声→token 化 Trans；否则 MLP（整帧 Trans 无结构收益）
> **DUCK 落地**：①查 G8T/G9T 是否 per-leg token 化（P0）②V5+ 加 feature dropout 消融③双腿对称=id5 故障的天然 token 受益体

## 待深入

- G8T/G9T 的 actor 代码确认 tokenization 形态（P0 行动项）
- ROLT 开源实现（legged_gym 生态）与 microduck 栈的兼容性
- 六足 damage 表中 ROLT 与 Module PE 差距 <1σ 的格子做二次验证

## 来源列表

1. Generalized Locomotion in Out-of-distribution Conditions with Robust Transformer (ROLT) — arXiv 2507.04039v1（全文精读：架构+消融+真机三实验）
2. UniLegs: Universal Multi-Legged Robot Control through Morphology-Agnostic Policy Distillation — arXiv 2507.22653 + Pith 审稿（transformer 蒸馏优势与噪声不可区分——反证对照）
3. Body Transformer: Leveraging Robot Embodiment for Policy Learning — arXiv 2408.06316（body tokenization 前作，按身体拓扑做注意力掩码）
4. Attention-Based Map Encoding for Learning Generalized Legged Locomotion — arXiv 2506.09588（attention 地图编码选落脚点的并行路线）



## 相关笔记

- [RL训练失败模式与RewardHacking自动检测](./2026-09-17-RL训练失败模式与RewardHacking自动检测.md) — 同日DUCK四路对照另一翼：结构泛化 vs 训练作弊检测
- [Sim2Real本体感知分布匹配](./2026-09-04-Sim2Real本体感知分布匹配-无动捕残差执行器学习.md) — sim-to-real 执行器域匹配实证
- robot-policy-learning-2026-wam-aac-frontier（~/explore，09-15）— 机器人策略学习 2026 前沿，本篇前序架构选型的同族母篇
