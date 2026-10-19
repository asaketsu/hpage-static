# WAM设计空间三轴分类-NVIDIA官方系统综述与VLA路线对决

> **来源**：NVIDIA Developer Blog《Pretrained to Imagine, Fine-Tuned to Act: The Rise of World-Action Models》（Moritz Reuss, Seattle Robotics Lab, 2026-06-15）
> **原文链接**：https://developer.nvidia.com/blog/pretrained-to-imagine-fine-tuned-to-act-the-rise-of-world-action-models
> **记录日期**：2026-08-28
> **系列**：WAM/VLA 系统跟踪第 9 篇（前序：08-12 三路线 / 08-14 分界判据 / 08-15 WorldPilot / 08-23 五方向全景）
> **性质**：技术研究笔记（官方博客全文精读 + 系列增量定位）

**标签**：#WAM #世界动作模型 #VLA #具身智能 #机器人基础模型 #视频底座 #RoboArena #DreamZero

---

## 一句话总纲

> **NVIDIA 官方判定：WAM（世界动作模型）已成为机器人基础模型与 VLM-based VLA 并列的第二大主流配方——其设计空间可用三轴正交分解（预测范式 × 动作集成 × 架构组合）完整刻画；真实世界实证 DreamZero（WAM）在 RoboArena 达 1750 Elo 超过 Pi-0.5 的 1622，但代价是 7.4 倍训练算力与 3-4 倍推理延迟；最终赢家既非纯 VLA 也非纯 WAM，而是 Motus 式混合体。**

---

## 二、内容整理

### 2.1 背景：为什么 WAM 现在起飞

2025-10 时 WAM 还只是 VLA 研究的小子领域；2026 年成为每日出现的新关键词。驱动因素三层：

1. **VLM-based VLA 撞墙（grounding wall）**：VLM 预训练带来互联网级知识，但"语言→动作"的接地映射仍必须从机器人数据学起。VLM2VLA 直接把 VLM→VLA 转变定性为**灾难性遗忘**；Knowledge Insulation（NeurIPS 2025）通过隔离 flow-matching 动作专家与 VLM 主干的梯度来保住预训练语言/视觉能力
2. **视频底座成熟且开放**：DiT 架构（Wan/Cosmos）取代 CNN 级联，时间压缩、flow-matching 目标、精选网络级视频数据全面超越；且开放权重——研究者可以直接微调而不必自己付 167 ZFLOPs 级的预训练成本（UniPi 时代 Imagen Video 级 CNN 视频底座必须从头训，这是当年无法复现的根本原因）
3. **动作侧同步成熟**：现代系统用 transformer/flow-matching 头预测 **action chunk**（一次策略调用输出 k 步动作序列），取代早期逐步 MLP 头

### 2.2 核心假设（作者明确标注为"假设而非结论"）

| # | 假设 | 支持证据 |
|---|------|---------|
| H1 | 预测未来世界变化与生成必要动作相关——逆动力学比直接动作生成更容易 | Pi-0.7 视觉子目标实验：给定期望未来图像时动作预测更直接、训练收敛更快 |
| H2 | 视频预训练提供语言↔物理变化的接地先验 | 视频模型学到文本→视觉结果映射，若迁移成功可减少对机器人演示的依赖 |
| H3 | 视频数据正则化机器人策略 | DreamZero 与 Fast-WAM 均显示：动作学习与视频预测目标**共同训练**时 WAM 表现最佳 |

### 2.3 Veo 3.1 零样本实验（前沿视频模型的操纵先验探测）

给 Veo 3.1 单帧 DROID 烤面包机任务上下文 + 自然语言指令（推杆→再拿起左侧橙子，组合扩展超出原演示）：

- **合格面**：动作平滑、背景稳定、遵循任务顺序（先杆后橙）
- **失败面**：未完全按下杆、夹爪"变形"成四指手、固定底座机械臂被重想象为另一个自由度更少的机器人
- **定性结论**：视频模型对"机器人-物体交互应该长什么样"有有用先验，但尚不足以可靠控制——WAM 微调正是把零样本想象力转化为可靠控制的尝试

### 2.4 三轴设计空间（本文核心贡献）

**轴一：预测范式（模型预测什么，视频如何用于生成动作）**

| 范式 | 机制 | 代表（早期→现代） | 要点 |
|------|------|------------------|------|
| **逆动力学** | 先生成未来视频，再从视频反推动作 | UniPi 2023 → LingBot-VA 2026 | 把难的 language-grounding 移到视频阶段；LingBot-VA 用 Wan 2.2-5B + 16k 小时跨体预训练，因果式闭环 rollout（非开环），MoT 架构，视频↔动作双向条件 |
| **联合预测** | 单模型一次输出视频+动作 | GR-1 2024 → DreamZero 2026 | DreamZero 从 Wan 2.1-I2V-14B 出发，单一单体 DiT 内**共同去噪视频 token 与动作 token**，无独立逆动力学模块——动作只是同一去噪过程中的另一种生成模态 |
| **纯表示** | 视频底座仅作表征，推理时**跳过视频生成** | Fast-WAM 2026 | 推理快数倍；在仿真基准上逼近 LingBot-VA（且无需 16k 小时大规模机器人预训练）。但目前公开证据少，作者持保留态度 |

GR-1 的历史意义：首次把视频用于学**策略级表征**而非仅图像级视觉表征——CALVIN ABC→D 上平均完成子任务从 <1.0 提到 3.06/5。

**轴二：动作集成（动作如何进入模型）**

| 方式 | 机制 | 代表 | 风险/收益 |
|------|------|------|----------|
| **默认动作 token** | 加动作 token + 动作头，动作作为与视频并列的模态 | UniPi/GR-1/DreamZero/LingBot-VA/VPP/Fast-WAM | 模态失配：动作 chunk 与预训练视觉 token 性质不同，需在动作微调中适应表征 |
| **动作即图像** | 把动作编码为视频模型原生可去噪的视觉/潜空间目标 | GENIMA 2024（SD 画关节目标）→ Cosmos Policy 2026（动作/本体感受/价值目标编码为**合成潜帧**，推理时空间维平均解码回动作向量） | 不扰动预训练视频表征，主干保持原生去噪空间 |
| **潜动作/潜计划** | 行为压缩为潜计划或潜动作作为条件 | Play-LMP 2019（先验/后验潜计划）→ Genie/LAPA（无标注视频学潜动作）→ Being-H0.7 2026 | Being-H0.7：后验分支用冻结 V-JEPA2.1 压缩未来为 K 个嵌入，先验分支学习从上下文预测之；测试时移除后验分支走快速潜接口；200k 小时第一人称人类视频 + 15k 小时机器人演示 |

**轴三：架构组合**

| 架构 | 机制 | 代表 | 权衡 |
|------|------|------|------|
| **分层管道** | 视频模块在前、动作模块在后，单向信息流 | UniPi / VPP / mimic-video / Pi-0.7（BAGEL 子目标+完整 VLA 动作专家） | 最灵活（动作头完全模块化）但视频↔动作耦合弱 |
| **单体 transformer** | 同一栈内共同去噪视频+动作 | DreamZero / Cosmos Policy | 耦合最强；风险是双优化负担（稠密视觉 token vs 稀疏动作目标） |
| **MoT（Mixture-of-Transformers）** | 模态专属专家参数 + 共享自注意力 | Pi-0/Pi-0.5（VLA 侧）/ LingBot-VA / Fast-WAM | 模块化与耦合的实用折中——作者预测将成为 WAM 主导架构 |

### 2.5 模型对照总表（原文 Table 4 完整收录）

| 模型 | 范式 | 动作集成 | 底座 | 架构 | 年份 |
|------|------|---------|------|------|------|
| Play-LMP | —（前 WAM） | 潜计划 | Transformer+LSTM（从零） | 分层 | 2019 |
| UniPi | 逆动力学 | 默认动作 token | CNN 视频扩散 1.7B | 分层 | 2023 |
| GR-1 | 联合预测 | 默认动作 token | Transformer（从零） | 统一 Transformer | 2024 |
| GENIMA | 逆动力学 | 动作即图像 | Stable Diffusion/ControlNet | 分层 | 2024 |
| Seer | 逆动力学 | 默认动作 token | 视觉/动作 token Transformer | 统一 | 2025 |
| VPP | 逆动力学 | 默认动作 token | Stable Video Diffusion | 分层 | 2025 |
| mimic-video | 逆动力学 | 默认动作 token | Cosmos 视频扩散 | 分层 | 2025 |
| **DreamZero** | 联合预测 | 默认动作 token | Wan 14B | 单体 DiT | 2026 |
| LingBot-VA | 逆动力学 | 默认动作 token | Wan 2.2-5B | MoT | 2026 |
| Cosmos Policy | 联合预测 | 动作即图像 | Cosmos | 单体 DiT | 2026 |
| Being-H0.7 | 联合预测（潜） | 潜计划/潜动作 | MoT（从零，200k+15k 小时数据） | MoT | 2026 |
| Fast-WAM | 纯表示 | 默认动作 token | Wan 5.5B | MoT | 2026 |

### 2.6 真实世界实证：RoboArena 2026-04 榜单

| 模型 | Elo | 路线 | 关键差异 |
|------|-----|------|---------|
| **DreamZero** | **1750** | WAM | 仅用 DROID 训练，无额外大规模跨体机器人训练阶段 |
| Pi-0.5 | 1622 | VLA | VLM 协同训练+梯度隔离 |
| Pi-FAST | 1592 | VLA | 同 Pi-0-DROID 底座，离散 FAST token 替代 flow |
| Pi-0 | 1475 | VLA | 原始 flow 动作头 |

三个可读信号：

1. **DreamZero > Pi-0.5（128 Elo）**：WAM 配方潜力的正面信号（尚非"WAM 更优"的证明）
2. **Pi-FAST > Pi-0（117 Elo）**：离散动作 token 化保住更多预训练能力——支持"VLM 侧避免 flow 干扰"的配方主张
3. 首批配对基准（Zhang et al.）：LingBot-VA / Cosmos Policy / Pi-0.5 在 LIBERO-Plus 与 RoboTwin 2.0-Plus 匹配扰动下对比，WAM 无需 VLA 级广谱数据混合即可达强鲁棒性——但仅限仿真

### 2.7 算力账本（ZFLOP 下界估计，C≈6NT）

| 训练项 | 估计 | 说明 |
|--------|------|------|
| VLA Foundry 动作阶段 | ~0.56 ZFLOPs | 1.65B 可训参数，不含上游 LLM/VLM |
| Pi-FAST DROID 微调 | ~0.77 ZFLOPs（240k 步） | 100k 步 OpenPI 配置约 0.32 |
| VLA Foundry 全栈（LLM→VLM→VLA） | ~6.9 ZFLOPs | 1-2B 开放配方，800B token LLM 阶段主导 |
| **DreamZero WAM 动作调优** | **~8.6-9.0 ZFLOPs** | 100k 步 batch 128、8.0-8.4k token/序列；不含 Wan 本体 |
| MolmoAct2 全栈到 DROID | ~9.8 ZFLOP | 9216 H100-hours，不含 Molmo2/Qwen3/SigLIP2 |
| **Wan-14B 完整 WAM 栈（示意）** | **~51 ZFLOPs** | 视频预训练代理 + DreamZero 式调优 |
| Summer-22B 视频预训练 | ~66 ZFLOPs | 500B token 从零训参考点 |

**核心差距**：完整 WAM 栈（51）对高效 VLA 配方（6.9）约 **7.4 倍**。WAM 用算力换机器人数据效率；且对视频数据质量敏感（DreamZero 主张视频生成质量↔策略性能正相关），数据过滤/caption/潜表示/生成预训练全部成为策略配方的一部分——VLA 侧无此清晰关联（VLM4VLA 发现通用 VLM 能力是下游 VLA 性能的弱预测器）。

### 2.8 推理速度

Fast-WAM 参考值：联合预测与全视频生成逆动力学两种 WAM 推理模式 **590-800ms/动作 chunk**，对比 Pi-0.5 约 **190ms**——**3-4 倍减速**，对实时控制致命。出路：跳过视频生成（Fast-WAM 纯表示路线）与 DreamZero 论文内的加速技巧。

### 2.9 VLA 阵营的反攻配方（现代 SOTA 四件套）

1. **离散动作 token 化**（FAST/BEAST）：把动作变成 VLM 可学的新"语言"，规避交叉熵↔flow-matching 的优化张力
2. **VLM 保持协同训练**：Pi-0.5 式 VLM 数据+机器人数据共训
3. **梯度隔离**（Knowledge Insulation）：flow 头梯度不回传污染 VLM 主干
4. **更广数据混合**

即便如此 grounding 墙仍在：语言是欠指定的目标表达，杂乱场景中文本指令难以锁定具体物体实例与期望物理状态——Pi-0.7 报告的"仅语言提示 vs 目标图像条件"差距佐证。

### 2.10 收敛预测：两条路终将合一

Motus（统一潜动作世界模型）与 BagelVLA（交错视觉-语言-动作生成长程操纵）代表第三条路：**理解/VLM 塔 + 视频生成塔 + 动作专家塔**，各塔专属权重、共享自注意力（常为非对称模式），Dense transformer 或 MoE 路由均可实现同一高层思想。

---

## 三、查询拓展

### 3.1 "为什么现在"的时间线考古

UniPi（2023）已有完整逆动力学配方却未爆发，根因是**工具链缺位**：CNN 级联视频扩散必须从头预训练（~167 ZFLOPs 估计）远超一般机器人实验室预算。这构成本系列 08-14 篇"分界判据"的工程注脚——范式成败不只取决于思想，还取决于**可复现的基础设施成本**。类比：LLM Agent 的 tool-use 范式同样在函数调用接口标准化（2023-06）后才真正起飞。

### 3.2 与本系列前序笔记的三轴映射

| 前序笔记框架 | 本文三轴对应 |
|-------------|-------------|
| 08-12 三路线（VLA/WAM/类脑） | WAM 内部再按预测范式细分三支 |
| 08-14 分界判据 | "是否复用视频/世界模型底座"仍是第一判据；本文补上动作集成与架构两个正交维度 |
| 08-23 五方向全景 | 五方向可重排进三轴立方体（如"算好了再动"=逆动力学，"边想边动"=联合预测） |
| 08-15 WorldPilot 双通道 | 属于"WAM 先验引导 VLA"的混合路线，正对本文收敛预测 |

### 3.3 潜动作学派的谱系澄清

Play-LMP（2019）的先验/后验潜计划结构在被 Being-H0.7 以基础模型规模重演——证明**接口设计可以比具体模型长寿**。Genie 证明潜动作可从无标注网络视频学到（无需真值机器人动作），LAPA 把它推向 VLA 式训练——这条"从视频自监督获得行为抽象"的路线与逆动力学（需配对视频-动作数据）的监督路径差异是理解 DreamDojo 等 action-conditioned 世界模型的关键。

---

## 四、归纳总结

### 4.1 三轴速查图

```
WAM 设计空间 = 范式 × 动作集成 × 架构

范式：      逆动力学(先想后动) | 联合预测(边想边动) | 纯表示(只借表征)
动作集成：  默认动作token      | 动作即图像          | 潜动作/潜计划
架构：      分层管道           | 单体DiT             | MoT共享注意力
```

### 4.2 八条工程结论

1. WAM 是与 VLA 并列的第二配方，不是 VLA 的替代者
2. 真实世界信号：DreamZero 1750 > Pi-0.5 1622（RoboArena 2026-04）
3. 算力税：完整 WAM 栈约 7.4× VLA 高效配方（51 vs 6.9 ZFLOPs）
4. 延迟税：默认 WAM 推理 3-4× 慢（590-800 vs 190ms/chunk）
5. 视频生成质量是 WAM 的必要条件；VLM 能力是 VLA 的弱预测器——两阵营的数据质量敏感点不同
6. MoT 大概率成为双方共同主导架构（模块化×耦合的实用折中）
7. VLA 反攻四件套（离散 token/协同训练/梯度隔离/广数据）已把 Pi-0→Pi-0.5 差距拉到 147 Elo
8. 终局是混合体（Motus/BagelVLA 式三塔结构），纯路线之争是伪命题

---

## 五、趋势判断

### 趋势 1：机器人基础模型进入"双配方竞赛"而非单范式迭代

依据：NVIDIA 官方措辞从"VLA 是默认"转为"两大配方并列"；DreamZero/Cosmos Policy（NVIDIA 自家）与 GR00T/Pi 系（VLA）在同一个 RoboArena 榜单上直接对垒。类似 BERT↔GPT 双路线时期，工程资源将向两条线同时倾斜。

### 趋势 2：推理效率将成为 WAM 的下一主战场

依据：Fast-WAM（纯表示）以数倍推理加速逼近 LingBot-VA 性能且免 16k 小时预训练；作者明确"更快的 WAM 将成为更大的研究领域"。590-800ms 的控制延迟在真实产线不可接受，谁先把 chunk 延迟压到 200ms 级谁就拿到落地门票。

### 趋势 3：动作 token 化是跨阵营的通用收敛点

依据：VLA 侧 FAST/BEAST 离散化（Pi-FAST +117 Elo over Pi-0）；WAM 侧 action-as-image 本质是把动作伪装成视觉 token 进原生去噪接口；潜动作则是学出来的离散/连续抽象。三条路都在解决同一问题——**让预训练底座不必为连续控制重写表征**。

### 趋势 4：视频数据管线成为策略配方的一等公民

依据：DreamZero 主张视频生成质量↔策略性能正相关；过滤/captioning/潜预处理全部计入策略配方；Summer-22B 66 ZFLOPs 级预训练成为竞争门槛。机器人团队将需要视频-数据工程师而不仅是机器人-数据工程师。

---

## 六、关联分析

### 6.1 与本机 WAM/VLA 系列笔记（第 9 篇定位）

| 笔记 | 关系 |
|------|------|
| 2026-08-12 机器人大脑三条技术路线 | 本文为其 WAM 分支提供官方级系统化细分 |
| 2026-08-14 WAM与VLA分界判据解析 | 底座判据不变；本文新增动作集成/架构两轴 |
| 2026-08-15 WorldPilot-WAM先验引导VLA双通道融合 | 混合路线的具体案例，正对本文收敛预测 |
| 2026-08-23 WAM世界动作模型五方向全景 | 五方向与三轴可互相映射，本文含官方算力/榜单硬数据 |
| 2026-08-27 机器人（应用）-机器人仿真工具 | RoboArena/LIBERO 基准体系同源 |

### 6.2 与本地机器人技能栈

- `dual-mcu-robot-architecture`（ESP32+STM32 分工）：WAM/VLA 均为"大脑"层；本机 590-800ms 级 WAM 延迟证实"小脑实时控制必须独立于大脑推理"的分层必要性
- `embodied-ai-control`（大脑-小脑分离+多层安全级联）：Pi-0.7 目标图像条件优于纯语言指令的发现，支持"视觉子目标作为中间表示"的级联设计
- Jetson 边缘约束：14B Wan 底座 + 8k token 序列在本地 GPU 不可运行（作者原话"good luck"），边缘侧只能走蒸馏/纯表示路线——与 07-24 端侧 VLA 8.66× 加速笔记的结论一致

### 6.3 与 AI Agent 架构的同构观察（克制映射）

仅一条：DreamZero"视频生成质量是策略性能的必要条件"与 Agent 领域"模型基础能力是 harness 上限"同构——底座质量无法被下游微调完全代偿。

---

## 七、拓展应用推荐

1. **系列聚合页（P0，呼应 MEMORY 待办）**：WAM/VLA 系列 9 篇 + 具身 2 篇 + 机器人 5 篇已具备建专题聚合页条件，建议以本文三轴分类为组织骨架（每篇笔记挂到立方体坐标上）
2. **机器人仿真选型参考**：RoboArena（真实世界开放式）/RoboLab（高保真仿真能力分析）/LIBERO（终身学习）三层基准体系可直接用于 embodied-ai-control 的仿真验证层选型
3. **潜接口设计借鉴**：Being-H0.7 的"后验压缩未来→先验预测潜 token→测试时移除后验"模式，对需要"昂贵规划器离线蒸馏为快速执行器"的任一系统（含 Agent 的 planner→executor 蒸馏）可复用
4. **跟踪清单**：DreamZero（2602.15922）/Fast-WAM（2603.16666）/Cosmos Policy（2601.16163）/Motus（2512.13030）四篇 arXiv 作为下一批精读候选

---

## 八、指南分析

**质量**：★★★★★——NVIDIA 官方出品但作者以研究者身份写作，三大突出优点：①三轴分类法是迄今对该领域最清晰的结构化地图；②ZFLOP 算力下界估计方法透明（C≈6NT，附完整 caveat 表）；③立场诚实——核心假设明确标注"假设而非结论"，对比表逐项注明"非干净对比"。
**局限**：①作者自认 WAM 分类非完美分类学（部分模型跨类）；②RoboArena 单点榜单存在时间敏感性；③对国内阵营（如 LingBot-VA 之外的国产路线）覆盖有限。
**与本系列关系**：官方级系统综述，作为系列第 9 篇的"骨架笔记"，后续单模型精读可直接挂载其三轴坐标。

---

## 九、出处

1. NVIDIA Developer Blog: Pretrained to Imagine, Fine-Tuned to Act: The Rise of World-Action Models — Moritz Reuss, 2026-06-15
   https://developer.nvidia.com/blog/pretrained-to-imagine-fine-tuned-to-act-the-rise-of-world-action-models
2. DreamZero — arXiv:2602.15922
3. Fast-WAM — arXiv:2603.16666
4. Cosmos Policy — arXiv:2601.16163
5. LingBot-VA — arXiv:2601.21998
6. Being-H0.7 — research.beingbeyond.com/being-h07
7. UniPi — Du et al., NeurIPS 2023
8. GR-1 — arXiv:2312.13139
9. Knowledge Insulation — NeurIPS 2025
10. Motus — arXiv:2512.13030；BagelVLA — arXiv:2602.09849
11. NTU Survey: World Model for Robot Learning — ntumars.github.io/wm-robot-survey/
12. RoboArena — arXiv:2506.18123 / robo-arena.github.io

## 相关笔记

- [2026-08-28-Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解](2026-08-28-Microduck开源双足机器鸭-Rust微服务与SimToReal全栈拆解.md) — 具身智能开源工程实践
- 2026-05-11-具身智能2026-世界模型VLA车企入局 — 行业趋势背景
- 2026-08-23-MjLabMicroban-30cm开源人形机器人RL训练与SimToReal — 同族对照实验

