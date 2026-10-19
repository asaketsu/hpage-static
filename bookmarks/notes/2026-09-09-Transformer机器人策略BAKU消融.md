# Transformer 机器人策略消融：BAKU 的架构证据与 history 损失设计陷阱

> 2026-09-09 夜间自学习笔记
> 来源：BAKU (NeurIPS 2024, NYU)、MSTA (ICRA 2025)、IsaacLab issue #2636
> 关联项目：DUCK-Pi_5 t2048 Transformer 策略（当前实验：MLP velstand 0.52m 最优 vs Transformer t2048 0.43m，12 样本评估口径）

## 核心结论（一句话版）

**Transformer 不是免费午餐：trunk 换 Transformer 只 +0.09，但 history 配错损失函数直接崩盘（0.90→0.54）；history 上做多步动作预测损失才能兑现收益（0.90→0.90 且 Meta-World +0.03）；小数据场景 10M 参数是甜点，114M 反而崩溃到 0.19。**

---

## 1. BAKU 架构三要素

BAKU（NYU, NeurIPS 2024）是离线模仿学习多任务策略架构，在 129 个仿真任务 + 30 个真机任务上验证。三个设计支点：

| 组件 | 做法 | 作用 |
|---|---|---|
| FiLM 条件化视觉编码器 | 任务指令调制视觉特征 | 同一编码器适配多任务表征 |
| Transformer observation trunk | 融合多模态编码结果 + 时序上下文 | 替代 MLP 拼接 |
| 解耦 action head | 预测头与观测编码分离，即插即用（MLP/GMM/BeT/VQ-BeT/Diffusion） | 观测表征与动作生成解耦 |

成果：LIBERO-90 上 90% 成功率（较此前 SOTA +36% 绝对值）；真机 30 任务平均仅 17 条示教/任务，成功率 91%。

## 2. 消融实验全量数据（Table 3 照录）

这是最有价值的部分——**每个数字都是一次架构决策的代价/收益**：

| 类别 | 变体 | LIBERO-90 | Meta-World | DMC |
|---|---|---|---|---|
| Observation Trunk | MLP | 0.81 | 0.78 | 0.68 |
| | **Transformer** | **0.90** | 0.79 | 0.70 |
| 模型规模 | 4.4M | 0.85 | 0.78 | 0.68 |
| | **10M** | **0.90** | 0.79 | **0.70** |
| | 31M | 0.87 | **0.81** | 0.70 |
| | 114M | **0.19（崩溃）** | 0.81 | 0.68 |
| Action Head | MLP | **0.90** | **0.79** | **0.70** |
| | GMM | 0.84 | 0.65 | 0.67 |
| | BeT | 0.89 | 0.78 | 0.60 |
| | VQ-BeT | 0.90 | 0.78 | 0.70 |
| | Diffusion | 0.89 | 0.45 | 0.61 |
| Action Chunking | ✗ | 0.76 | 0.78 | **0.74** |
| | ✓ | **0.90** | **0.79** | 0.70 |
| Observation History | 不用 | **0.90** | 0.79 | 0.70 |
| | 用+last-step loss | **0.54（崩盘）** | **0.08（崩盘）** | **0.37（崩盘）** |
| | 用+multi-step loss | **0.90** | **0.82（+0.03）** | 0.68 |

## 3. 四条关键洞见（与因果解释）

### 洞见1：Transformer trunk 收益有限且场景依赖

+0.09（LIBERO）/+0.01/+0.02——多模态融合复杂度高的任务收益大，纯本体感受任务收益小。**MLP 在单一模态任务上仍是强基线**。

### 洞见2：⚠️ history + last-step loss 是灾难陷阱

naive 使用观测历史、但只在最后一个时间步算动作预测损失 → 三大基准全面崩盘（0.54/0.08/0.37）。原因： Transformer 需要对历史中**每个**观测都输出预测并计算损失，否则监督信号稀释、表征退化。multi-step loss（对历史所有时间步算损失）不仅恢复还带来 Meta-World +0.03 增益。
**这正是 DuckTransformerModel 类架构需要自查的点：训练时滑窗内是否所有位置都有监督信号。**

### 洞见3：模型规模与数据量强耦合

10M 最优；31M 在 Meta-World 反超（+0.02）说明更大模型需要更多任务数据喂饱；114M 在 LIBERO-90 上 0.19 崩溃 = **小数据 + 大模型 = 过拟合灾难**。离线模仿 17 demos/任务的量级下，10M 是安全上限。

### 洞见4：action chunking 在操作任务收益大（+0.14），但对连续控制未必

✗→✓ 在 LIBERO +0.14，但 DMC（连续控制）反而 -0.04。chunking 适合离散抓放动作序列，纯 locomotion 连续控制要单独评估。

## 4. 补充证据

### 4.1 MSTA（ICRA 2025）：Transformer 抗观测缺失

masked sensory-temporal attention 做传感器泛化：完整观测下 GRU/Transformer/普通策略差距 <2%；**观测不完整时 Transformer 显著优于 GRU**（能更准确重建机器人状态）。这解释了 Transformer 策略的真实价值场景——不是常态更强，而是**退化场景更稳**（传感器掉线/噪声/部分可观测）。

### 4.2 IsaacLab issue #2636：ONNX 导出的 action_scale 语义

社区高频踩坑：RSL-RL 导出 ONNX 后输出超出 [-1,1]，开发者困惑"action_scale 到底在图内还是图外"。与本项目 09-08 实锤的 ONNX 导出 span 语义 bug（compat 版 pad_mask 全 True = 未来帧泄漏，diff 0.3-0.6 假 PASS；修复=显式传 span=W，diff=2.8e-07）属同类问题：**导出图的语义必须与训练 rollout 前向严格对齐，同源随机输入对比不足以验证**，必须用真 obs 窗口回放训练 forward 对比。

## 5. 对 DUCK-Pi_5 的落地建议

| # | 建议 | 依据 | 成本 |
|---|---|---|---|
| 1 | 检查 t2048 训练循环中滑窗监督信号设计：若只有 last-step 损失，改 multi-step（对窗口内全部位置算动作损失）重训 | 洞见2，三大基准 0.54/0.08/0.37 崩盘证据 | 重训 1 次 |
| 2 | t2048 参数量核对：若显著 >10M 量级且数据量未同步放大，考虑缩到 10M 甜点区 | 洞见3，114M→0.19 崩盘 | 改 hidden_dims 重训 |
| 3 | 不必因 MLP 当前更优而否定 Transformer 路线：收益兑现在多模态/退化场景（后续加视觉时 Transformer 优势才展开） | 洞见1+MSTA | 0（认知校准） |
| 4 | 后续尝试 action chunking 需谨慎：locomotion 连续控制上 DMC 反而 -0.04，先做 2-4 帧小 chunk 消融 | 洞见4 | 实验性 |
| 5 | 任何新导出必须保留"真 obs 窗口回放 vs 训练 forward"验证步骤（已写入 docs/43 SOP 第 3 步，维持） | issue #2636 + 自家 span bug 实锤 | 0（已固化） |

## 6. 查询拓展：围绕本主题的延伸问题

### 6.1 rsl_rl 训练 Transformer 时滑窗监督信号怎么查？

检查训练循环中 actor 的损失计算位置：若 policy 只对窗口最后一个时间步的预测计算损失（last-step loss），按 BAKU 证据三大基准全面崩盘（0.54/0.08/0.37）。修复方式：让 Transformer 对窗口内所有时间步输出动作预测并求损失（multi-step loss）。在 rsl_rl 5.0.1 外挂注入架构下（resolve_callable 零 fork），这需要自定义 actor 的 forward 返回全窗口预测、在 loss 计算处展开。注意 microduck 的 DuckTransformerModel 当前实现是否已经这样设计需要核对源码——**训练时能收敛不代表监督信号设计最优**。

### 6.2 ONNX 导出语义验证的通用检查单

从自家 span bug + IsaacLab #2636 归纳：
1. 同源对比（随机输入，onnx vs onnx wrapper）→ 只验图完整性，不充分
2. 训练 forward 对比（真 obs 窗口回放）→ 验语义正确性（span/pad_mask/action_scale）
3. 真机闭环（锁指令位移）→ 最终验收
任何"导出即部署"都缺第 2 步，都是裸奔。

### 6.3 Transformer 策略什么时候值得上？

综合 BAKU（+0.09 LIBERO）与 MSTA（完整观测 <2% 差距、缺失观测显著优势）：**单体感受、单一任务、观测完整** → MLP 足够；**多模态融合、多任务、传感器可能退化** → Transformer。DUCK-Pi_5 当前是单体感受单任务，MLP 0.52m 最优是符合文献预期的结果，不是失败。

## 7. 归纳总结

**一句话**：Transformer trunk 在多模态复杂任务上比 MLP +0.09，但这不是主要收益来源；真正要命的是 history 配 last-step loss 直接崩盘（0.90→0.54）、大模型小数据崩溃（114M→0.19）；history 的正确打开方式是 multi-step loss，10M 是小数据甜点。

因果链三层：
1. **为什么 history+last-step 会崩**：监督信号只覆盖窗口末端 → 前面位置的表征没有梯度约束 → 表征退化扩散到全窗口（包括末端），比不用 history 还差
2. **为什么 multi-step loss 有效**：每个位置都有动作预测约束 → Transformer 被迫学时序动态 → Meta-World +0.03 兑现收益
3. **为什么 114M 崩盘**：17 demos/任务的数据量撑不起大模型 → 过拟合训练分布 → 泛化崩溃。模型规模必须与数据量匹配，不是越大越好

## 8. 趋势判断

| 判断 | 依据 | 置信度 |
|---|---|---|
| Observation trunk 从 MLP → Transformer 成为机器人策略默认起点 | BAKU/DayDreamer 系/RT-1 全线采用；MSTA 证明退化场景优势 | 高 |
| Action chunking 仍是操作任务标配，locomotion 谨慎 | BAKU 操作 +0.14 vs DMC -0.04；ACT 系延续 | 高 |
| 端到端 ONNX/TensorRT 部署链成为 sim2real 标配 | IsaacLab 官方导出链 + ddtrobot 等社区项目全用 ONNX→TRT；语义对齐验证是主要风险点 | 高 |
| 10M-30M 参数量级是机器人策略的稳定甜点区 | BAKU 消融；PACT/BoT 同量级 | 中高 |
| next-token prediction 形式统一机器人控制（Radosavovic） | 行动序列即 token 序列，预训练-微调范式迁移 | 中 |

## 9. 关联分析

- **与本地 t2048 实验闭环**：BAKU Table 3 的 history+last-step loss 崩盘模式，正是 t2048 需要自查的第一嫌疑——若 DuckTransformerModel 训练时只对末端算损失，这可能是 t2048 系（0.43m）不敌 MLP 系（0.52m）的架构级根因，优先级高于调 reward 权重。
- **与 09-08 ONNX span bug 笔记**：同属"导出语义对齐"问题族。IsaacLab #2636（action_scale 在图内还是图外）与自家 span（banded causal vs 全注意力）都验证：**同源随机输入对比不充分，必须真 obs 回放**。
- **与 microduck reward 分解笔记（09-08）**：reward 重心在站立系（3.4）远超速度追踪（2.1）是训练目标问题；BAKU 消融是架构问题——两者叠加时先修架构监督信号（影响所有任务），再调 reward（影响特定行为）。
- **与 12 样本评估铁律（09-08）**：BAKU 的结论全部基于多任务多基准统计，单任务单 seed 的架构对比同样不可信。

## 10. 拓展应用推荐

| 应用 | 场景 | 具体做法 | 优先级 |
|---|---|---|---|
| t2048 滑窗监督自查 | 排查 Transformer 系落后根因 | 读 DuckTransformerModel 训练循环，确认 loss 覆盖窗口所有位置还是仅末端 | ★★★ 立即 |
| 参数量核对 | 排查过拟合 | 核对 t2048 实际参数量 vs 10M 甜点；hidden_dims=(512,256,128) 量级估算 | ★★★ 立即 |
| multi-step loss 重训 | 若确认 last-step 设计 | 修改 actor forward 输出全窗预测 + loss 展开，重训对照 | ★★ 短期 |
| 2-4 帧小 chunk 消融 | locomotion chunking 探索 | DMC 反例警示下先做小步实验 | ★ 中期 |
| 导出验证门禁固化 | 防语义泄漏 | 已写入 docs/43 SOP 第 3 步（真 obs 回放对比），维持执行 | ✅ 已固化 |

## 11. 指南分析：Transformer 策略自查三步法

> 本节为可直接执行的操作指南，针对 DUCK-Pi_5 t2048 系。

### 第一步：监督信号审计（10 分钟，零成本）
```bash
# 定位训练循环中 actor loss 的计算位置
grep -n "last\|final\|-1" ~/uclaw/project/duck-p3-pilot/models/transformer_model.py | head
# 关键问题：head(x[:, -1, :]) 只取末端帧 → 若 loss 也只在末端监督，即为 last-step 模式
```
判读：`head(x[:, -1, :])` 出现在**推理/导出路径**是正常的（当前帧动作）；若训练 rollout 也只用末端预测算 loss，则命中 BAKU 崩盘模式。

### 第二步：参数量核对（5 分钟）
```python
# 在含 torch 的环境执行
from duck_p3_pilot.models.transformer_model import DuckTransformerModel
from tensordict import TensorDict
obs_td = TensorDict({"actor": torch.zeros(1, 61)}, batch_size=[1])
m = DuckTransformerModel(obs=obs_td, obs_groups={"actor": ["actor"]}, obs_set="actor",
                         output_dim=14, hidden_dims=(512,256,128), obs_normalization=True)
print(sum(p.numel() for p in m.parameters()) / 1e6, "M params")
```
判读：>10M 且数据量未同步放大 → 过拟合风险（BAKU 114M→0.19 前车之鉴）；建议压 hidden_dims 或减层数重训。

### 第三步：对照实验设计
- 若第一步命中 last-step：改 multi-step loss 重训一轮（同 seed 同 iter 数），12 样本评估对比
- 若第二步命中参数过大：hidden_dims 减半重训对照
- 两个都命中：先修监督信号（影响表征学习全局），再修参数量
- 对照组：velstand MLP 系（0.52m 基线）不动，作为固定锚点

### 验收门
任何重训版本仍走 docs/43 七步 SOP：导出→span 验证→12 样本评估→传输→探针→手柄→入册。

## 12. 关键数字速查

| 发现 | 数值 | 来源 |
|---|---|---|
| Transformer vs MLP trunk | 0.90 vs 0.81（LIBERO-90） | BAKU Table 3 |
| history+last-step loss 崩盘 | 0.54/0.08/0.37 | 同上 |
| history+multi-step loss | 0.90/0.82/0.68 | 同上 |
| 模型规模甜点/崩溃 | 10M 最优；114M→0.19 | 同上 |
| 真机示教效率 | 17 demos/任务 → 91% 成功率 | BAKU |
| 完整观测下架构差距 | <2% | MSTA ICRA25 |
| 自家 span 修复 diff | 2.8e-07 PASS | 本地实测 09-08 |

## 出处

- 原文1：BAKU: An Efficient Transformer for Multi-Task Policy Learning, NeurIPS 2024, Haldar/Peng/Pinto (NYU)。PDF 全文提取存 ~/.hermes/cache/web/proceedings.neurips.cc-da06c9c79f.md，Table 3 消融数据忠实照录。
- 原文2：Masked Sensory-Temporal Attention for Sensor Generalization (ICRA 2025, tianweiz07.github.io/Papers/25-icra-2.pdf)
- 原文3：IsaacLab issue #2636（ONNX action_scale 语义问答）
- 增补范围：第 4.2 节末尾与自家 span bug 的技术对照、第 5-11 节（落地建议/查询拓展/归纳总结/趋势判断/关联分析/拓展应用推荐/指南分析）为结合 DUCK-Pi_5 本地实验现状的应用分析，非原文内容；其余为原文忠实整理。

## 相关笔记

- [2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例](./2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例.md) — xxPO 三组件框架对机器人 RL 的跨域迁移
- [2026-09-08-PPO算法通俗解析与RLHF对齐应用](./2026-09-08-PPO算法通俗解析与RLHF对齐应用.md) — PPO/GAE 基础与 BAKU 策略梯度训练同源
- Agent 记忆迁移性笔记（uclaw/notes/explore，09-08）— Transformer history token 与记忆损失同主题
- DUCK-Pi_5 训练复盘文档 ~/uclaw/project/DUCK-Pi_5/docs/ — 12 样本评估口径出处
