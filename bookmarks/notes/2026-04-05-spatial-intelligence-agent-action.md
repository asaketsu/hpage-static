# 空间智能视角下 Agent 要补足哪些缺失来完成「Action」？

来源：机器之心 PRO 会员通讯
链接：https://mp.weixin.qq.com/s/PC6wv232ZY7iPYg8BUWuSg
日期：2026-04-05
评分：⭐⭐⭐⭐（4/5）

## 核心论文
AtlasPro AI（2026.02）《From Perception to Action: Spatial AI Agents and World Models》
- 梳理 2000+ 篇文献（2018-2026），引用 742 篇核心论文
- 提出 Spatial AI Agent 三轴分类：Spatial Task / Agentic Capability / Spatial Scale

## 行业动态
- **World Labs（李飞飞）**：16个月融资13亿美元，Marble 多模态世界模型 + World API（标准化3D漫游接口）
- **空间超感知（2025.11）**：LeCun/李飞飞/Rob Fergus 联合提出，时空特征细粒度建模
- **具身推理（2026.03）**：李飞飞+贾佳俊，Reflective Test-Time Planning（反思式测试时规划）
- **G²VLM（上海AI Lab）**：3D重建+高级空间推理融合

## 三个关键改进方向
1. **层级记忆体系** — 场景记忆、任务记忆、动作记忆的分层分工
2. **GNN-LLM 集成** — 图神经网络+大语言模型处理空间关系
3. **世界模型** — 提升智能体对行动后果的预测精度

## 核心瓶颈
学界对空间智能探索分散于不同任务场景，未将智能体能力和空间任务统一整合。从被动观察转向主动行动是核心挑战。

## 启发与借鉴（待尊上判断）
1. **层级记忆 → 记忆架构升级**：我们当前四分类（user/feedback/project/reference）是平铺结构。可借鉴层级记忆思想，在 permanent/ 中建立层级关系（如 reference.md 下按主题分组，project.md 按项目分组）
2. **反思式规划 → 任务执行增强**：Reflective Test-Time Planning 的"行动前模拟+行动后复盘"思路，可融入 task-executor skill（执行前预估风险，执行后对比预期）
3. **三轴分类 → 项目分类框架**：Spatial Task/Agentic Capability/Spatial Scale 的多维度分类法，可借鉴用于我们的项目/知识管理分类
→ 相关：2026-04-07-OpenClaw摄像头RTSP本地视觉模型智能家居.md
→ Related: 2026-04-07-tactile-multimodal-fusion-embodied-intelligence-survey.md


## 相关笔记
- [[2026-04-07-email-not-revival-agent-needs-it]] (关键词: agent)
- [[2026-04-13-4-ai-agent-frameworks-comparison]] (关键词: agent)
- [[2026-04-13-hermes-agent-vs-openclaw]] (关键词: agent)
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: agent)
- [[hermes-agent-源码拆解自我进化机制]] (关键词: agent)
