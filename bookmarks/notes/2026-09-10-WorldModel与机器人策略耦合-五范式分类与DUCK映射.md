# World Model 与机器人策略耦合范式：五范式分类与 DUCK-Pi_5 映射

> 探索日期 2026-09-10（夜间自学习） | 兴趣等级 L4 | 来源 4 篇 | 前序笔记：`2026-09-09-BAKU消融`、`2026-09-09-通用模型与机器人模型正在收敛`、`2026-09-08-Zero-WAM`

## 核心问题

纯反应式 VLA 策略在长时程任务上撞墙：compounding errors、时序 credit assignment、对物理先验的缺失。补救路线是把**预测性结构**（world model）重新装回策略里——但"怎么装"分化出了五条架构范式。本篇基于 NTU-MARS 的 World Model for Robot Learning 综述（arXiv 2605.00080，147K 字符全文精读）提炼分类框架，并逐条映射到 DUCK-Pi_5 的 MLP-based RL 栈，回答"我们该不该上 world model"。

## 核心发现（5 条）

1. **统一概率视角：五类模型是同一个联合分布的不同查询**。综述最锋利的一刀：p(未来观测, 未来动作 | 当前观测, 指令) 这个联合分布，边缘化掉观测得 policy，边缘化掉动作得 passive world model（=视频生成），条件化于动作得 controllable world model，反着查得 inverse dynamics model（IDM）。**它们不是五种架构，是一种预测控制分布的四种问法**——这解释了为什么 world model 和 policy 天然可耦合。

2. **五范式耦合光谱**（从松到紧）：

```
解耦 IDM 式 ──► 单骨干共享 ──► MoE/MoT 融合 ──► 统一 VLA 联训 ──► 潜空间内化
 UniPi/VPP    UVA/Cosmos    Motus/F1       GR-1/WorldVLA    VLA-JEPA/WoG
 视频先rollout 预测+动作同塔  专家分工融合     图像预测与动作   只潜变量预测,
 再反推动作    joint训练      推理时按需启用   共同训练目标     推理零视频开销
```

   关键工程判据是**推理时未来生成是否保留**：Fast-WAM 训练时用视频、推理时跳过（视频是训练期的脚手架）；WoG/VLA-JEPA 把预测压进潜变量，推理开销≈0。

3. **IDM 式（解耦）适合数据富但动作贫的场景**：UniPi 路线先用视频生成模型 rollout 未来画面，再用逆动力学模型从"想象的未来"反推可执行动作。优点是可复用海量视频预训练；缺点是两段式误差累积。**这是 DUCK-Pi_5 最不可能走的路线**（我们动作数据不缺，缺的是算力）。

4. **World model 作为模拟器是独立价值轴**：综述第二条主线——world model 不耦合进策略，而是充当学习到的仿真器，用于 RL post-training、候选动作排序、甚至与策略共演化（co-evolution）。GigaBrain-0.5M 用世界模型 RL 缩放到 VLA 适配；WMPO 强调 pixel-space imagination + on-policy GRPO。**对真机 1831g vs XML 1604.6g 的 +14.1% 质量差，"学习到的修正仿真器"是比重训更便宜的思路**。

5. **评估共识：视觉逼真 ≠ 可用**。综述 8.6 节明确：视觉上 plausible 的未来可能不保动作条件一致性；反之视觉粗糙也不妨碍规划效用。需要的指标是 function-aware 的——任务成功率、policy-ranking 保真度、可执行性诊断。**这与用户"验收看真实功能指标（鸭子位移）非代理指标"的铁律同构**。

## 关键概念

### 联合分布四种查询（式 5-8 简化）

```
Policy:          p(a|o,l) = ∫ p(o',a'|o,l) do'     ← 边缘化未来观测
Passive WM:      p(o'|o,l) = ∫ p(o',a'|o,l) da'    ← 边缘化动作（视频生成）
Controllable WM: p(o'|o,a')                         ← 条件化于动作
Inverse Dyn:     p(a'|o...o')                       ← 从未来反推动作
```

### 策略侧两条表示路线（2.2 节）

| 路线 | 代表 | 动作表示 | 优劣 |
|------|------|---------|------|
| 离散 token | RT-2 / OpenVLA / FAST(DCT压缩) | 动作量化进词表 | 复用 next-token 能力；高频控制精度损失 |
| 连续生成 | Diffusion Policy / π 系 flow matching | 条件生成动作块 | 多模态分布完整；采样开销 |

> FAST 的 DCT 压缩动作块把离散路线的高频精度短板补上了——对高频关节控制（50Hz 步态）这是离散化路线的唯一可行形态。DUCK-Pi_5 目前是确定性 MLP 回归 + chunk（span），属于"最简连续路线"，理论上损失多模态性，但步态任务的多模态需求低，够用。

### 推理时开销决策树

```
需要实时控制(≥50Hz)?
 ├─ 是 → 潜空间内化(WoG/VLA-JEPA)或 Fast-WAM(训练用视频/推理跳过)
 │        DUCK-Pi_5 ONNX @50Hz 属于此列——纯 MLP 前向，零生成开销
 └─ 否(可容忍100ms+)
    → 单骨干联合输出(Cosmos Policy: 动作/状态/价值并行头)或 IDM 解耦
```

## 与现有工作的关联（DUCK-Pi_5 映射）

### 五范式 × DUCK-Pi_5 适用性

| 范式 | 代表 | 对 DUCK-Pi_5 适用性 | 判断 |
|------|------|-------------------|------|
| IDM 解耦 | UniPi/VPP | 需视频预训练骨干+两段推理 | ❌ 算力不允许 |
| 单骨干 | UVA/Cosmos Policy | joint 训练预测+动作，rsl_rl 栈需大改 | ⚠️ 侵入性强 |
| MoE/MoT | Motus/F1 | 多专家融合，小模型学不动门控 | ❌ 过重 |
| 统一 VLA | WorldVLA/GR-1 | 需 VLM 骨干 | ❌ 方向不符（我们是 MLP RL） |
| **WM 当模拟器** | GigaBrain/WMPO | **MuJoCo 已是完美模拟器** | ✅ 唯一有意义 |

**结论：DUCK-Pi_5 不该追 world model 耦合进策略。** 我们有 MuJoCo 精确物理，没有视频预训练算力，控制频率 50Hz 不留生成开销。五范式中唯一对齐的是"WM 作为模拟器"轴——而 MuJoCo 就是我们的 world model。**真正的 sim-to-real gap（真机 1831g vs XML 1604.6g）对应的是"域随机化不足"问题，其学术对应物是 learned residual simulator / co-evolution 路线**：用真机 rollout 数据修正 XML 惯性参数（system identification），比上 world model 便宜两个数量级。

### 按 P0/P1/P2 排序

- **P0 — 真机质量差用 system identification 而非 world model**：+14.1% 质量差 → 重测连杆质量/质心（MEMORY 已有"重训必做"结论），可用 5 分钟量程称重 + URDF 惯性张量重算完成，对应综述里"learned simulator correction"思想的最小实现。
- **P1 — obs 编码路线坚持 MLP+chunk**：综述 2.2 确认 action chunk 是抑制 compounding error 的主流策略（ACT/Diffusion Policy 共识），DUCK 已用 span chunk，方向正确无需改动。
- **P2 — 若未来上视觉**：直接选潜空间内化范式（WoG 式），推理零视频开销，适配 50Hz；不要碰 IDM 解耦（两段误差在真机上会被放大）。

## 关键风险与盲点

- **综述本身是地图不是证据**（来源级别：官方综述，二手）：五范式分类是组织性贡献，各范式间没有严格对比实验；引用具体方法（如 Cosmos Policy 并行头）效果时需回原论文核实。
- **World model RL 的算力门槛被低估**（来源级别：社区观察）：WMPO/GigaBrain 类方法均在多 GPU 集群训练视频生成器；Jetson 生态（本机禁跑重型 ML）完全不在射程内，笔记结论"不上 world model"部分是算力约束下的无奈，非学术最优。
- **评估指标缺失同样适用于我们**：综述指出领域缺 function-aware 指标——DUCK 的"鸭子位移"验收恰好是自发的 function-aware 指标，但也只有这一个维度，缺少 policy-ranking 保真度类指标（仿真内排名 vs 真机排名的一致性）。

## 一页速查

> - 五类模型 = 同一联合分布 p(o',a'|o,l) 的四种查询方式。
> - 耦合光谱：解耦 IDM → 单骨干 → MoE/MoT → 统一 VLA → 潜空间内化。
> - 推理时是否保留未来生成 = 关键工程判据；实时控制选潜空间/跳过式。
> - WM 第二价值轴 = 学习到的模拟器（RL post-training/候选排序/共演化）。
> - 评估铁律：视觉逼真 ≠ 动作一致可用；function-aware 指标才是硬通货。
> - DUCK-Pi_5 结论：MuJoCo 就是我们的 world model；质量差走 system identification；策略侧维持 MLP+chunk。
> - FAST(DCT) 是离散动作路线做高频控制的唯一形态，未来若换 token-based 头可参考。

## 待深入

1. Cosmos Policy（arXiv 2603.x，Kim et al.）单骨干并行输出动作/状态/价值头——与 rsl_rl actor-critic 结构的兼容性。
2. Learned simulator correction 最小实现：真机 rollout 惯性参数辨识文献（domain randomization vs sysid 对比）。
3. Policy-ranking fidelity 指标如何为 DUCK 设计：仿真内多 ckpt 排名与真机表现排名的 Spearman 相关。

## 来源列表

1. arXiv 2605.00080 — *World Model for Robot Learning: A Comprehensive Survey*（NTU-MARS, 2026-05, HTML 全文 147K 字符精读, 配套 repo: NTUMARS/Awesome-World-Model-for-Robotics-Policy）
2. arXiv 2503.13441 — *Humanoid Policy ∼ Human Policy*（HAT 统一状态-动作空间共训）
3. GitHub YanjieZe/awesome-humanoid-robot-learning（2.7k stars，2026.06 SUGAR/SplitAdapter 等最新条目扫描）
4. phospho.ai policy 文档（VLA/RL/模仿学习产业视角对照）


## 相关笔记

- [通用模型与机器人模型正在收敛-Astra启示与Dyna-2缩放律](./2026-09-09-通用模型与机器人模型正在收敛-Astra启示与Dyna-2缩放律.md) — 前序：缩放律视角论证收敛
- [Meshy去中心化SPMD的RL训练框架](./2026-09-09-Meshy去中心化SPMD的RL训练框架-OpenBMB开源论精读.md) — RL 训练基建侧搭档
- [GPO生长式策略优化](./2026-09-03-GPO生长式策略优化-足式机器人力矩控制新范式.md) — 足式策略优化范式
- [Microban与2026双足RL前沿](./2026-09-01-Microban与2026双足RL前沿-低成本平台同构与重训校准.md) — 低成本双足同构重训
- [FastSAC单卡Sim2Real](./2026-09-02-FastSAC单卡4090十五分钟人形Sim2Real-离策RL配方全解.md) — 离策 RL 配方
