# Awesome Journal Skills — 4152 个按期刊定制的 AI 投稿工作流（Stanford REAP × CoPaper.AI）

> **来源**：[github.com/brycewang-stanford/Awesome-Journal-Skills](https://github.com/brycewang-stanford/Awesome-Journal-Skills)
> **Stars**：931 · **Forks**：116 · **License**：MIT
> **维护方**：[CoPaper.AI](https://copaper.ai) × [Stanford REAP](https://reap.fsi.stanford.edu/)
> **引擎**：[StatsPAI](https://github.com/brycewang-stanford/StatsPAI)（900+ 因果推断函数）
> **创建日期**：2026-05-25 · 最后更新：2026-08-08

---

## 一句话定义

> **按期刊定制的 AI 投稿工作流索引**——743 本期刊/会议、299 个 Skill Pack、4152 个 Skill。核心理念：同一篇文章在 AER 卡在识别策略，在《管理世界》卡在缺中国制度背景，在《经济研究》卡在缺经典理论文献——**一套泛泛的"学术写作"助手永远学不会这种差异**，需要为每本期刊单独编码编委偏好、格式红线和审稿文化。

---

## 一、核心设计

### 1.1 为什么按期刊做 Skills

| 痛点 | AJS 的解法 |
|------|-----------|
| 通用"学术写作"助手无法区分期刊差异 | 为每本期刊单独编码编委偏好、格式红线和审稿文化 |
| 投稿前不知道"该投哪本" | 跨刊选刊工具包 `research-toolkit-skills` 从 743 本刊/会排出 reach/match/safe 三档 |
| 复制包/数据可得性要求各刊不同 | 每个 skill 覆盖论文生命周期一个环节 |

### 1.2 论文生命周期 6 环节

每个深度包（12 skills）覆盖：
1. **选题**——选题方向与期刊偏好的匹配
2. **定位核心进展**——识别该领域的关键文献和空白
3. **识别策略**——因果推断方法选择（IV/RDD/DiD/RCM 等）
4. **表格与图件规范**——按刊定制的格式标准
5. **复制包/数据可得性准备**——按刊要求的 replication package
6. **投稿与修改回复**——审稿回复策略和 cover letter

### 1.3 三层结构

| 层级 | 描述 | 示例 |
|------|------|------|
| **根目录期刊入口**（200 个） | 只负责导航，不含 SKILL.md | `Economic-Research-Journal-Skills/` |
| **深度包**（~30 个） | 单刊全流程 9-13 个 skills | Science, Nature, Cell, AER, QJE, 《经济研究》 |
| **广度合集**（9 个） | 每 venue 一个轻量 fit-and-house-style skill + router | `English-NaturalScience-Journal-Skills/` |

---

## 二、覆盖范围（11 个学科板块）

| 板块 | 子领域数 | 代表 venue | 形态 |
|------|---------|-----------|------|
| 🌐 综合·交叉 | 5 | Science, PNAS, Nature Communications | 深度包 + 广度合集 |
| 💼 经管与商科 | 8 | AER, QJE, JPE, Econometrica, JF, AMJ, TAR, MISQ | 深度包 + 中英文合集 |
| 🧭 社会科学 | 9 | ASR, AJS, APSR, AJPS, JPSP | 深度包 + 合集 |
| 🏛 人文学科 | 6 | AHR, PMLA, Mind, Critical Inquiry | 深度包 + 合集 |
| 📐 数学与物理 | 6 | Annals of Math, PRL, Nature Physics, JACS | 深度包 + 合集 |
| 🧬 生命科学 | 8 | Cell, Cancer Cell, Neuron, Immunity, eLife | 深度包 + 合集 |
| 🩺 医学与健康 | 8 | NEJM, The Lancet, JAMA, BMJ, JCO | 深度包 + 合集 |
| ⚙️ 工程与技术 | 9 | Proc. IEEE, TAC, Automatica, Optica | 广度合集 |
| 🤖 CS 与 AI | 12 | NeurIPS, ICML, ICLR, CVPR, ACL, ICRA | CS/AI 深度包 + 会议合集 |
| 🌱 农业环境地球 | 11 | ES&T, GRL, Nature Climate Change | 深度包 + 合集 |
| 🏅 体育科学 | 4 | 《体育科学》, 《北体大学报》 | 中文广度合集 |

**总计**：743 本刊/会，299 个 pack，4152 个 skill

### 2.1 CS/AI 顶会覆盖（155 个会议）

NeurIPS · ICML · ICLR · AAAI · IJCAI · AISTATS · UAI · COLT · MLSys · KDD · WebConf · WSDM · SIGIR · CVPR · ICCV · ACL · EMNLP · ICRA · CHI · SOSP · OSDI · IEEE S&P · ACM CCS · ICSE · NAACL · ECCV · PLDI · SIGMOD · STOC · NSDI · USENIX Security · NDSS · FOCS · SODA · POPL · OOPSLA · VLDB · CIKM · EuroSys · ASPLOS · UIST · CSCW · ISCA · MICRO · RSS · CoRL · INTERSPEECH · COLM · HPCA · IROS · ICDE · ICDM · RecSys · MobiCom · ACM MM · ICASSP · SIGCOMM · EACL · AAMAS · WACV · MobiSys · SenSys · ISSTA · FSE · ASE · PODS · CoNEXT · IMC · IPSN · VIS · ICSME · ECAI · ATC · FAST · PPoPP · CAV · ICALP · PODC · SIGMETRICS · PerCom · SIGGRAPH · INFOCOM · ITCS · HRI · SoCC · DAC · EDBT · TACAS · FAccT · ICDT + 155 个会议

---

## 三、安装与使用

### 3.1 安装方式（Claude Code / Codex）

```bash
# 1) 添加 marketplace（一次即可）
/plugin marketplace add https://github.com/brycewang-stanford/awesome-journal-skills

# 2) 安装目标期刊的 pack（以 QJE 为例）
/plugin install qje-skills
/reload-plugins
```

### 3.2 使用示例

```text
# 已确定目标期刊
用 qje-workflow 评估我这份稿子离 QJE 的发表标准还差什么

# 未确定目标期刊
用 rt-journal-match：这是我的摘要，该投哪几本、按什么顺序投？
```

### 3.3 选刊路由（跨刊工具包）

`research-toolkit-skills` 从 743 本刊/会索引排出 **reach / match / safe** 三档，并提前写好改投阶梯。选刊检索经过实测验证（见 `shared-resources/journal-selection/eval/RESULTS.md`）。

---

## 四、Skill Pack 结构深度解析

### 4.1 深度包结构（以 Science-Skills 为例）

```
Science-Skills/
├── SKILL.md                    # 主入口
├── skills/
│   ├── science-topic-finding/  # 选题方向
│   ├── science-positioning/    # 核心进展定位
│   ├── science-method/         # 方法学指导
│   ├── science-tables/         # 表格规范
│   ├── science-figures/        # 图件规范
│   ├── science-submission/     # 投稿流程
│   ├── science-revision/       # 修改回复
│   ├── science-replication/    # 复制包准备
│   ├── science-identification/ # 识别策略
│   ├── science-house-style/    # 格式红线
│   ├── science-cover-letter/   # Cover letter
│   └── science-peer-review/    # 审稿文化
├── .claude-plugin/
│   └── plugin.json             # 插件清单
└── marketplace.json            # 市场注册
```

### 4.2 广度合集结构（Router + 轻 Skill）

```
English-NaturalScience-Journal-Skills/
├── skills/
│   ├── nature/                 # 每刊一个轻量 skill
│   ├── nature-communications/
│   ├── nature-physics/
│   └── ...                     # 154 本期刊
├── router/                     # 选刊路由
└── SKILL.md
```

### 4.3 质量门槛

收录到索引的质量要求：
1. ✅ 必须按期刊定制（不是通用 pack）
2. ✅ 中英文双语 README（针对中国相关期刊）
3. ✅ 至少有一个 `*-workflow` 路由 skill
4. ✅ 含 plugin manifest（`.claude-plugin/plugin.json` + `marketplace.json`）
5. ✅ MIT 协议

---

## 五、与 Hermes Agent 的适配分析

### 5.1 能否形成 Hermes Skill？

**结论：能，但需要适配层**。AJS 原生为 Claude Code/Codex 插件系统（`.claude-plugin/plugin.json`），与 Hermes Skill 格式（SKILL.md frontmatter）不同。有两种适配路径：

| 方案 | 工作量 | 适用场景 |
|------|--------|---------|
| **A. 下载并转格式** | 高（4152 个 skill） | 需要完整本地化的学术团队 |
| **B. 创建元 Skill** | 低（1 个路由 Skill） | 按需下载特定期刊包 |

**推荐方案 B**——创建一个 `journal-skill-router` Skill，功能：
1. 输入论文摘要 + 目标领域 → 调用 AJS 的 venue-index.tsv 排出 reach/match/safe
2. 选定期刊后 → 按需下载该期刊的 SKILL.md 并解析为 Hermes 可用的上下文
3. 提供"论文体检"功能——对照目标期刊的编委偏好逐项检查

### 5.2 可借鉴的设计模式

| AJS 的设计 | Hermes 可借鉴到 | 说明 |
|-----------|----------------|------|
| **按领域定制而非通用** | Skill 粒度设计 | 通用 Skill 解决不了领域差异 |
| **选刊路由 (rt-journal-match)** | 领域路由 Skill | 给出 reach/match/safe 分层 |
| **Plugin Marketplace** | Skill 分发机制 | `hermes skill import <git-url>` |
| **CI 硬门槛检查** | Skill 质量管理 | frontmatter/canonical skill 计数/克隆检测 |
| **深度包 vs 广度合集** | Skill 分层策略 | 重要领域深做、次要领域薄做 |

---

## 六、结合最新研究与技术变化

### 1. 与 Scholar-Assist Skill 的关联

Hermes 已有 `scholar-assist`（论文全链路助手），但缺少**按期刊定制的方法论**。AJS 的价值在于补充了这个维度——同一个 paper 在不同期刊的退稿点完全不同。

### 2. 与 Paper-Review-Auditor 的关联

`paper-review-auditor` 用 10 指令框架审计论文创新点。AJS 的深度包更进一步——编码了**特定期刊的审稿文化**（如《经济研究》重经典理论、《管理世界》重中国制度背景），这是通用审计框架做不到的。

### 3. 与 Agent Card Protocol 的关联

AJS 的每个 Pack 有标准化的 plugin manifest，类似 Hermes 的 `agent-card-protocol`——为每个 Skill 生成标准化自描述。

### 4. 与 Skill 工程趋势的关联

AJS 的 4152 个 skill / 299 个 pack 展示了一个趋势：**Skill 正在从"个人工具"演变为"领域知识库"**——编码的不再是"怎么做"，而是"某领域专家的判断标准"。

---

## 七、学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **按领域定制而非通用** | Skill 设计原则 | 高 |
| **选刊路由 reach/match/safe** | 领域路由模式 | 高 |
| **深度包 vs 广度合集分层** | Skill 分层策略 | 中 |
| **CI 硬门槛（克隆检测 threshold=0.90）** | Skill 质量自动化 | 高 |
| **venue-index.tsv 机读表** | Skill 索引标准化 | 中 |
| **"同一篇文章退稿点不同"** | 领域上下文不可省略 | 高 |

---

## 八、趋势判断

1. **Skill 正在从工具进化为领域知识库**——4152 个 skill 编码的是"专家判断标准"而非"操作步骤"
2. **按期刊定制是学术 AI 的正确方向**——通用写作助手无法替代领域专家的判断
3. **Stanford REAP 的背书提升可信度**——不是 AI 公司的通用产品，而是学术团队的方法论沉淀
4. **Plugin Marketplace 是 Skill 分发的未来**——从手动安装到一键安装
5. **因果推断是经济学 Skill 的核心**——StatsPAI 的 900+ 函数是 AJS 的技术底座

---

## 📎 关键资源

| 资源 | 用途 |
|------|------|
| [CATALOG.md](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/main/CATALOG.md) | 全部 743 本刊/会，每本标注插件名 |
| [catalog.json](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/main/catalog.json) | 机读目录 |
| [venue-index.tsv](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/main/shared-resources/journal-selection/venue-index.tsv) | 289 刊机读表 |
| [eval/RESULTS.md](https://github.com/brycewang-stanford/Awesome-Journal-Skills/blob/main/shared-resources/journal-selection/eval/RESULTS.md) | 选刊评测结果 |
| [StatsPAI](https://github.com/brycewang-stanford/StatsPAI) | 因果推断引擎（900+ 函数） |
| [CoPaper.AI](https://copaper.ai) | 端到端实证研究 AI 助手 |

---

## 相关笔记

- [RW-Research-Skill科研投稿自动化](2026-08-07-RW-Research-Skill科研投稿自动化.md)
- [AI-Agent自进化Skill系统-EvoSkills框架](2026-06-22-AI-Agent自进化Skill系统-EvoSkills框架.md)
- [Awesome-LLM-Apps与AI-Harness课程](2026-08-07-Awesome-LLM-Apps与AI-Harness课程.md)

---

*笔记创建：2026-08-08 · 来源：Stanford REAP × CoPaper.AI Awesome Journal Skills*
