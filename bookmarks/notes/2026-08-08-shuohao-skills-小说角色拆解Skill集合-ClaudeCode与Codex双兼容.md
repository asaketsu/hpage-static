# shuohao-skills — AI 编码 Agent 的 Skill 集合（小说角色拆解 novel-characters）

> **来源**：[github.com/eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills)
> **Stars**：277 · **Forks**：33 · **License**：Apache-2.0
> **语言**：JavaScript（零 npm 依赖，纯标准库）
> **运行环境**：Claude Code + Codex 双兼容
> **创建日期**：2026-08-06 · 最后更新：2026-08-08

---

## 一句话定义

> **给 AI 编码 Agent 用的 Skill 集合**，首发 Skill `novel-characters`——丢一本小说进去，自动拆出角色设定集：人物画像、形象提示词、音色提示词、角色设定图（半身像+三视图+细节条）。产出 JSON + Markdown + 可交互 report.html。零依赖、零 API key、用当前会话额度。

---

## 一、novel-characters Skill 详解

### 1.1 输入输出

**输入**：一篇小说/短故事的 `.txt` 文件

**输出**：每个角色的完整设定

| 产出 | 内容 | 格式 |
|------|------|------|
| **角色表** | 谁出场了、主角还是龙套、跨章节称呼归并 | JSON |
| **人物画像** | 性别、年龄、身份、外貌、性情、动机、人物弧光、关系网，每条附**原文逐字引文** | JSON + MD |
| **形象提示词** | 半写实厚涂路线，双语出图 prompt + negative prompt + 风格标签，直接喂 Midjourney/SD/GPT-Image | JSON |
| **音色提示词** | 音色、音高、语速、口音、情绪，双语 voice-design prompt，直接喂 Qwen3-TTS/ElevenLabs | JSON |
| **角色设定图** | 16:9 横构图：左 34% 半身像（面部基准）+ 右上三视图 + 右下细节特写 | PNG |
| **report.html** | 双击即开的可交互角色设定报告 | HTML |

### 1.2 角色设定图版面

```
┌──────────┬────────────────────────────┐
│  半身像   │   正视    侧视    背视       │
│ （证件照） ├────────────────────────────┤
│  面部基准  │  细节 · 细节 · 细节 · 细节   │
│   ~34%   │            16:9            │
└──────────┴────────────────────────────┘
```

**两条硬要求**：
1. 三视图的脸必须与半身像一致（否则一张图两个长相）
2. 三个全身像的比例必须一致

### 1.3 出图风格

| 风格 ID | 说明 |
|---------|------|
| `realistic`（默认） | 半写实厚涂，皮肤有毛孔和肌理，布料有织纹磨损 |
| `ghibli` | 吉卜力式手绘赛璐璐，等宽墨线、单层柔和阴影、平涂色块 |

> 换风格是整套换——每个预设自带 render/surface/lighting/negative/tags 五块，整块取用不混搭。

### 1.4 报告语言

```bash
/novel-characters ./book.txt --lang en    # 英文报告
/novel-characters ./book.txt --lang ja    # 日文报告
/novel-characters ./book.txt --style ghibli  # 吉卜力画风
```

- 内置中文/English/日本語三套界面文案
- 其他语言（法语/韩语/西班牙语）现场翻译界面文案
- **两条不跟随语言**：出图和 TTS 提示词永远英文（引擎吃英文最稳）；原文引文永远保持原文语言（翻译了就不是证据了）

---

## 二、工作流（两趟扫描架构）

### 2.1 为什么分两趟

长文本一次性塞进上下文会丢角色。所以拆成**两趟**：

```
小说文本 → 分块(14k字符重叠块) → 第一趟扫描(每块抽角色) → 归并(名字+别名收敛)
  → 选角(前N位) → 第二趟出卡(完整角色卡) → 校验(四类硬规则) → 出图(可选)
```

### 2.2 第一趟：扫描（便宜）

- 按段落切成 14k 字符的**重叠块**（重叠让切口上的角色两边都能看见）
- 每块并发抽「角色名 + 别名 + 该块里的具体描写 + 逐字引文」
- 支持子代理并发（Claude Code 的 Task、Codex 的 subagent）

### 2.3 归并

- 按名字和别名建索引
- `陆行远` / `陆` / `姑娘` 这类跨块不同叫法收敛成同一个人
- 按出现块数当**戏份权重**排序

### 2.4 第二趟：出卡

- 只对戏份最重的 N 位生成完整角色卡
- 同批角色**互相知道对方名字**（避免长相和声线撞车）
- 每条画像附原文逐字引文作为证据

### 2.5 校验（⛔ 不能跳）

```bash
node novel-characters.mjs validate cast.json book.txt --lang zh
```

| 规则 | 为什么 | 检查方式 |
|------|--------|---------|
| `evidence` 必须是原文**逐字连续**片段 | 防编造 | 脚本比对原文 |
| 出图 prompt **不许出现人名** | 图像模型对人名偏见极重 | 脚本正则 |
| 字段**语言分工**（人类字段跟随 lang、出图/TTS 永远英文） | 模型会漂 | 脚本检查 |
| **风格与反向提示词匹配**（realistic 不能禁 photorealistic、ghibli 必须禁） | 搞反整批图就废 | 脚本检查 |

> 这四条不是拍脑袋定的——是模型输出真的违反过、被校验脚本当场抓住才立起来的。

---

## 三、Skill 工程最佳实践

### 3.1 仓库结构约定

```
skills/<skill-name>/
├── SKILL.md              给 agent 读的工作流（必需）
├── README.md             给人读的说明
├── scripts/
│   ├── <name>.mjs        确定性工具，零依赖
│   └── selftest.mjs      自测，不调模型（必需）
├── references/           按需加载的详细指令
├── examples/             自带样例，同时当测试夹具
└── assets/               截图
```

### 3.2 两条硬要求

1. ✅ 每个 skill 必须有 `SKILL.md`
2. ✅ 每个 skill 必须有 `scripts/selftest.mjs`，**不调用模型、不花额度**，覆盖全部确定性逻辑

### 3.3 安装方式（软链 + 自动检测）

```bash
git clone https://github.com/eternityspring/shuohao-skills.git
cd shuohao-skills
./scripts/install.sh

# 只装某一个
./scripts/install.sh novel-characters

# 只装到 codex
./scripts/install.sh --codex

# 取消软链
./scripts/install.sh --uninstall
```

自动检测 Claude Code 或 Codex，把所有 skill **软链**过去——`git pull` 后立即生效，不用重装。

### 3.4 命令行直接用（不需要 Agent）

```bash
node scripts/novel-characters.mjs chunk book.txt /tmp/wk        # 切块
node scripts/novel-characters.mjs merge /tmp/wk                 # 归并
node scripts/novel-characters.mjs validate cast.json book.txt   # 校验
node scripts/novel-characters.mjs render cast.json --html       # 出 report.html
node scripts/novel-characters.mjs slug "胡二爷"                  # 安全文件名
node scripts/novel-characters.mjs styles                        # 查看风格预设
node scripts/novel-characters.mjs ui-template fr                # 翻译骨架
```

---

## 四、SKILL.md frontmatter 设计

```yaml
---
name: novel-characters
version: 1.4.0
description: |
  从小说或短故事里拆出角色表、人物画像、形象提示词、音色提示词，
  并给主要角色出角色设定图（左半身像 + 右全身三视图 + 细节条），
  产出 JSON + Markdown + 可交互的 report.html。
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - Glob
triggers:
  - novel-characters
  - 拆角色
  - 小说角色
  - 人物画像
  - 角色卡
  - 三视图
metadata:
  license: Apache-2.0
  requires:
    bins:
      - node          # >= 18，只用标准库，无 npm 依赖
    optional:
      - codex         # 有才出三视图
  runtimes:
    - claude-code
    - codex
---
```

---

## 五、与 Hermes Agent 的适配分析

### 5.1 Skill 工程模式对比

| 维度 | shuohao-skills | Hermes Skills | 差异 |
|------|---------------|---------------|------|
| **Skill 格式** | SKILL.md + YAML frontmatter | SKILL.md + YAML frontmatter | ✅ 几乎相同 |
| **确定性脚本** | `.mjs`（Node 标准库零依赖） | `.py`（Python） | 语言不同但模式相同 |
| **自测** | `selftest.mjs`（必须，不调模型） | 无强制要求 | ⚠️ Hermes 可借鉴 |
| **校验** | validate 脚本（引文逐字/语言分工/风格匹配） | doc-qa / note-content-completeness | 方向一致 |
| **安装** | 软链 + 自动检测 | `skill_manage` API | 不同但思路相似 |
| **references/** | 按需加载的详细指令 | 相同模式 | ✅ 一致 |
| **examples/** | 自带样例同时当测试夹具 | 无标准做法 | ⚠️ 可借鉴 |

### 5.2 可直接借鉴的工程实践

| 实践 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **selftest 必须不调模型** | 每个 Skill 增加确定性自测脚本 | 高 |
| **examples/ 同时当测试夹具** | 每个 Skill 自带样例输入和预期输出 | 高 |
| **validate 校验模型输出** | 对 LLM 产出做脚本级确定性校验（不靠模型自觉） | 高 |
| **零依赖纯标准库** | Skill 脚本尽量不引入外部依赖 | 中 |
| **软链安装 + git pull 即生效** | Skill 分发方式 | 中 |
| **triggers 字段** | Skill 的多触发词列表 | 中 |
| **两趟扫描架构** | 处理长文本的分块→归并→精做模式 | 高 |

### 5.3 novel-characters 在 Hermes 中的可能用法

- **AI 短剧/有声书制作**：拆出角色 → TTS 音色提示词 → 语音克隆（与 LuxTTS 结合）
- **小说改编分析**：角色弧光和关系网分析 → 研究笔记
- **内容创作**：角色设定图 → 与 ComfyUI/ChatGPT-Image Skill 结合出图

---

## 六、结合最新研究与技术变化

### 1. 与 CodexLoom Agent Team 笔记的关联

shuohao-skills 的 novel-characters 两趟扫描架构（分块→并发子代理→归并→精做）是 CodexLoom 的 Responsible/Participant 模式在单 Skill 内的微缩版——第一趟是 Participant 并行扫描，归并是 Responsible 收口，第二趟是 Participant 精做。

### 2. 与 Awesome Journal Skills 的关联

两者都是 Claude Code/Codex 的 Skill Pack，但方向不同——AJS 面向学术投稿方法论，shuohao-skills 面向创意内容生产。

### 3. 与 AI 短剧分账笔记的关联

AI 短剧需要大量角色设定工作。novel-characters 可以将小说自动拆成角色设定集，是 AI 短剧制作流程的前置环节——角色拆解 → 场景设计 → 台词生成 → 语音合成 → 视频制作。

### 4. 与 SkillOpt（微软 Agent 技能优化器）的关联

SkillOpt 的 Propose→Verify→Compound 在 novel-characters 中体现为：第二趟 Propose（生成角色卡）→ validate Verify（四类硬规则校验）→ report Compound（整合输出）。校验脚本就是 SkillOpt 的 Verify 步骤。

---

## 七、学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 说明 |
|------|----------------|------|
| **selftest 不调模型不花额度** | Skill 质量基线 | 每个 Skill 必须有确定性自测 |
| **四类硬规则由脚本检查** | LLM 产出质量控制 | 不靠模型自觉，靠脚本拦截 |
| **两趟扫描架构** | 长文本处理 | 分块→归并→精做，避免上下文丢角色 |
| **重叠块** | 分块处理 | 重叠让切口上的内容两边都能看见 |
| **同批角色互知名字** | 避免冲突 | 生成时传入同批其他实体的名字 |
| **语言分工规则** | 多语言产出 | 人类字段跟随 lang，提示词永远英文 |
| **零依赖纯标准库** | 可移植性 | Skill 脚本尽量不引入外部依赖 |
| **examples 同时当测试夹具** | 测试复用 | 样例输入和预期输出合二为一 |

---

## 八、趋势判断

1. **Skill 正在从工具进化为流水线**——novel-characters 的两趟扫描+校验+渲染是一个完整的处理流水线，而非简单工具调用
2. **确定性校验是 Skill 质量的关键**——模型会犯的四类错误（编造引文/人名出图/语言漂移/风格反转）全部由脚本拦截
3. **Claude Code/Codex 双兼容成为标配**——Skill 不再绑定单一 Agent 平台
4. **零依赖是 Skill 的核心竞争力**——纯标准库、不需要 npm install、不需要 API key
5. **AI 短剧/有声书产业链正在形成**——角色拆解→TTS→视频制作的自动化流水线有了基础设施

---

## 📎 关键文件索引

| 文件 | 用途 |
|------|------|
| `SKILL.md` | Agent 工作流（9 步 + frontmatter） |
| `scripts/novel-characters.mjs` | chunk/merge/validate/render/slug/styles/ui-template |
| `scripts/selftest.mjs` | 220 项断言，不调模型 |
| `references/roster-pass.md` | 第一趟扫描指令 |
| `references/profile-pass.md` | 第二趟出卡指令（8 条硬规则） |
| `references/schema.md` | 角色卡结构 + 字段语言归属 |
| `references/sheet.md` | 角色设定图出图的 codex 调用契约 |
| `references/style-presets.md` | 出图风格预设 |
| `examples/渡口.txt` | 自带短故事，4 个角色 |
| `examples/渡口-cast.json` | 产出样例 + 校验夹具 |

---

*笔记创建：2026-08-08 · 来源：shuohao-skills GitHub + novel-characters SKILL.md*
