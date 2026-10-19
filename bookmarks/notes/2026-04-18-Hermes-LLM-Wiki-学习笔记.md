# Hermes Agent LLM Wiki 知识库 — 深度学习笔记

来源：微信公众号（Hermes 这个技能我一直没碰，跑完一遍后悔没早试）
链接：https://mp.weixin.qq.com/s/q6Q-0-9_sOjt29NTTPQO0g
关联笔记：[2026-04-05-Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)（Karpathy 原始理念详解）
日期：2026-04-18
评分：⭐⭐⭐⭐（4/5）
标签：#知识管理 #LLM-Wiki #Hermes #自进化 #最佳实践

---

## 一、文章核心内容

Hermes Agent 将 Karpathy 的 LLM Wiki 理念（PR #5100/#5635）落地为内置 Skill，是首个完整实现的 AI Agent。文章重点演示了**微信集成 + LLM Wiki 构建 + Obsidian 可视化**三大功能。

### 与我们已知内容的增量（对比 [2026-04-05-Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)）

之前笔记已覆盖三层架构和 Ingest/Query/Lint。本文新增：

| 新知 | 详情 |
|------|------|
| **hot.md 热缓存** | ~500词会话上下文持久化，占 <0.25% 上下文窗口，每次省 2-3K token |
| **Skill Config 接口** | LLM Wiki 是首个使用者，通过 `config.yaml → wiki.path` 配置 |
| **8 类 Lint 检查** | 孤立页/死链/矛盾/缺失/未链接/元数据/空白/过期索引 |
| **社区生态** | SwarmVault/agent-wiki/knowledge-pipeline/Cortex/ΩmegaWiki/qmd |
| **微信原生集成** | 扫码登录 → 私聊交互，长轮询无需公网端点 |
| **Obsidian 联动** | Graph View + Dataview + Marp + Git 版本历史 |

### Hermes 增强特性（超越 Karpathy 原始设计）

1. **Session 导向**：每次会话读 index.md 定位
2. **Tag 分类法**：YAML frontmatter 标签体系
3. **更新策略**：超 10 页面先确认再批量更新
4. **日志轮转**：log.md 自动管理
5. **归档工作流**：长期知识归档机制
6. **矛盾标记**：`[!contradiction]` 主动标记冲突

---

## 二、自我进化 — 可借鉴模式

### 🎯 模式 1: 知识复利增长（最重要）
传统方式：存了就存了，知识之间没有关联。
LLM Wiki 方式：**每次交互都让知识库更丰富**，摄入一个源 → 更新 10-15 个 Wiki 页面。

**→ 我们的行动**：
- ✅ 每篇新笔记必须关联已有笔记（`[[wikilink]]`）
- ✅ 分析完一个竞品/文章后，主动更新相关旧笔记
- ✅ 好的分析结论归档回知识库，不只是回复用户

### 🎯 模式 2: hot.md 热缓存
每次 session_search 要消耗 LLM token，而 hot.md 只需 ~500 词就能恢复上下文。

**→ 我们的行动**：
- 在 `~/uclaw/bookmarks/notes/` 创建 `hot.md`
- 每次会话结束时自动更新（当前在做什麽、下次从哪继续）
- 下次会话先读 hot.md，比 session_search 轻量 10 倍

### 🎯 模式 3: Lint 健康检查
定期检查笔记系统的"健康度"。

**→ 我们的行动**：
- 创建 `~/uclaw/bookmarks/notes/index.md` 索引文件
- 定期 cron 执行 Lint：检查孤立笔记、过时内容、缺失关联
- 每次写新笔记时自动更新 index.md

### 🎯 模式 4: 好答案归档
LLM Wiki 的洞察：好的答案应归档回 Wiki，让知识复利增长。

**→ 我们的行动**：
- 深度分析/竞品分析后，主动创建笔记而非仅回复
- 用户说"记住这个"时，不只是存 memory，还写笔记建立关联

---

## 三、具体执行计划

### Phase 1: 立即（本周）
1. 创建 `~/uclaw/bookmarks/notes/index.md` — 自动索引所有笔记
2. 创建 `~/uclaw/bookmarks/notes/hot.md` — 会话热缓存
3. 所有新笔记加入 `[[wikilink]]` 交叉引用和标签
4. 修正笔记路径：统一为 `~/uclaw/bookmarks/notes/`

### Phase 2: 短期（1-2 周）
5. 实现 Lint cron — 定期检查笔记系统健康
6. 每次深度分析后自动更新 index.md 和关联笔记
7. 探索 Obsidian 作为 `~/uclaw/bookmarks/notes/` 的可视化前端

### Phase 3: 中期（1 个月）
8. 实现 raw/ → notes/ → SCHEMA.md 三层架构
9. 知识图谱可视化（Obsidian Graph View）
10. 自动矛盾检测和关联推荐

---

## 四、引用
- Karpathy 原始 Gist (2026.4.4) — 见 [2026-04-05-Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- Hermes PR #5100 / #5635
- aivi.fyi 深度分析
- Vannevar Bush, "As We May Think" (1945) — Memex 理念源头

> "人类的工作是策展来源、指导分析、提出好问题、思考这一切的意义。LLM 的工作是其他一切。" — Karpathy

## 相关笔记
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [垂域LLM指导航空结构设计](2026-04-27-垂域LLM指导航空结构设计.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [Awesome-LLM-Apps-109K星应用模板库](2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](explore/2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](explore/2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](orphan/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](orphan/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](orphan/2026-05-16-表达清晰的5个训练.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
