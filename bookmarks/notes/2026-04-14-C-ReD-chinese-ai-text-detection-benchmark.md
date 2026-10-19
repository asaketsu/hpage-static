# C-ReD: 中文 AI 生成文本检测综合基准

- **论文**: [arXiv:2604.11796](https://arxiv.org/abs/2604.11796)
- **日期**: 2026-04-13
- **作者**: Chenxi Qing, Junxi Wu, Zheng Liu, Yixiang Qiu, Hongyao Yu, Bin Chen, Hao Wu, Shu-Tao Xia
- **领域**: NLP / AI 文本检测 / 中文基准
- **标签**: #论文 #AI检测 #中文NLP #benchmark

## 核心问题

LLM 生成的中文文本日益逼真，带来钓鱼、学术不端等风险。现有中文检测基准存在三大不足：
1. **模型多样性不足** — 只用少数 LLM 生成样本
2. **数据同质化** — 领域覆盖窄
3. **Prompt 不真实** — 用人工设计的 prompt，非真实场景

## 方法：C-ReD

- **C-ReD** = Chinese Real-prompt AI-generated Detection benchmark
- 基于**真实 prompt** 构建（非人工合成）
- 覆盖多种 LLM、多领域、多场景

## 核心发现

1. 域内检测可靠
2. 能泛化到**未见过的 LLM** 和外部中文数据集
3. 在模型多样性、领域覆盖、prompt 真实性上填补了此前中文检测基准的空白

## 趋势预判

- **AI 文本检测 vs 生成的军备竞赛将持续升级**：随着 LLM 输出越来越自然，检测方法必须同步进化，中文场景尤甚（中文语料研究相对滞后）
- **检测工具将标准化**：类似 C-ReD 的基准会推动行业形成统一评估标准，未来"AI 生成内容标注"可能成为法规要求
- **对抗性生成（绕过检测）也将成为研究热点**：检测基准的发布反过来会刺激更隐蔽的生成技术研究

## 与我们的关联

- 我们的 humanizer skill 正是为了降低文本的"AI 味"，C-ReD 可作为效果评估基准
- 作为 AI Agent 系统运营方，了解检测前沿有助于内容策略调整
- 数据集已开源，可用于训练/测试本地检测模型

## 参考

- GitHub: 论文中提到已开源资源（链接待确认）
- 相关项目: [CUDRT](https://github.com/TaoZhen1110/CUDRT)（中英双语 AI 文本检测基准，覆盖创建/更新/删除/改写/翻译五类操作）


## 相关笔记
- [[2026-04-06-AI-Scientist-v2]] (关键词: ai)
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: ai)
- [[2026-05-14-航空结构设计AI短期基础设施]] (关键词: ai)
- [[2026-04-09-SKILL-md-ai-agent-skills]] (关键词: ai)
- [[2026-04-13-rag-vs-mcp-architecture]] (关键词: ai)
