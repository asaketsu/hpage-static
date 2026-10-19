# Zotero PDF2zh — 5.7k Star 学术 PDF 翻译插件：架构评估与"不建本地项目"的诚实判定

> **来源**：[guaguastandup/zotero-pdf2zh](https://github.com/guaguastandup/zotero-pdf2zh)（GitHub，5.7k Star / 226 Fork / 616 commits，AGPL-3.0）
> **核心引擎**：[PDF2zh](https://github.com/Byaidu/PDFMathTranslate) + [PDF2zh_next](https://github.com/PDFMathTranslate/PDFMathTranslate-next)
> **记录日期**：2026-08-23
> **项目裁定**：❌ **不建本地项目**（理由详见"判定章节"）；建笔记 + 沉淀可迁移的方法论

**标签**：#Zotero #PDF翻译 #学术工具 #插件工程 #LLM翻译

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 5 个标签 |
| 出处 | 头部出处行 | GitHub + 双引擎 |
| 内容整理 | 第一~三章 | 功能矩阵/技术架构/安装配置 |
| 查询拓展 | 第四章 | 对比 pdf2zh 系 + Zotero 插件生态 |
| 归纳总结 | 第五章 | 三层架构（Zotero 插件/Python server/自动化） |
| 趋势判断 | 第六章 | 2 条预测 |
| 关联分析 | 第七章 | 与本机笔记/翻译链路交叉 |
| 拓展应用推荐 | 第八章 | 可迁移的方法论 |
| 指南分析 | 第九章 | 工程质量 + 不建项目的诚实判定 |

---

## 一句话总纲

> **Zotero PDF2zh 是把上游 pdf2zh/pdf2zh_next PDF 翻译引擎接入 Zotero（7/8/9/10 四版本）的成熟学术翻译插件——5.7k star，AGPL，双语对照+保留公式+批量翻译+多 LLM，但当前正值全面重构（2026-08 公告），新贡献冻结。**

---

## 一、内容详细整理

### 1.1 功能矩阵

| 能力 | 描述 |
|------|------|
| **双版本 Zotero 兼容** | Zotero 7（稳定）、Zotero 8、Zotero 9、Zotero 10 beta 全支持 |
| **双语对照** | 原文/译文左右对照（Dual 模式） |
| **公式保留** | 基于 pdf2zh 的公式+排版保留（核心卖点） |
| **批量翻译** | 多 PDF 一次性翻译 |
| **裁剪阅读** | Crop 模式，只看感兴趣区域 |
| **多 LLM 支持** | OpenAI/DeepSeek/自定义；DeepSeek V4 默认不思考 |
| **GitHub/Gitee 双源更新** | 国内网络友好 |
| **Server 独立进程** | Python server（`server.py`）+ Windows exe 模式可选 |

### 1.2 技术架构（三层）

```
┌─ Zotero 插件层（XPI）────────────────────┐
│ 界面交互 / 任务调度 / 双语对照渲染           │
│ 兼容 Zotero 7/8/9/10 四版本                │
├─ Python Server 层（server.py）────────────┤
│ 上游 pdf2zh / pdf2zh_next 翻译引擎          │
│ uv / conda 自动识别 + pip 依赖管理          │
│ 支持本地 LLM API 调用                       │
├─ 自动化层（automation/）───────────────────┤
│ macOS: 右键翻译 + Zotero 监控 + Server 守护  │
│ Windows: 右键翻译 + Zotero 监控              │
│ Docker: 容器化部署（2.4.3 和主线两版）        │
└─────────────────────────────────────────────┘
```

### 1.3 安装核心命令

```bash
# 1) 安装 Python 3.12 + Zotero
# 2) 下载 server.zip → 解压到非系统盘（建议 D 盘）
# 3) 启动 server（uv 或 conda 自动识别）
python update_packages.py   # 更新翻译引擎依赖
python server.py            # 启动翻译服务
# 4) 安装 XPI 到 Zotero
# 5) Zotero 内配置：server 地址 + LLM 密钥 + 翻译模式
```

### 1.4 生命周期状态（关键事实）

> **重要通知（2026-08-19）**：本插件正在进行**全面重构**，预期九月份发布新版本，暂时不会在群里及时解答目前版本相关的问题，也请开发者暂时不要对本仓库提交贡献。

⚠️ 这意味着：**当前仓库是过渡期，贡献冻结，架构即将大变。**

### 1.5 自动化生态

| 平台 | 能力 |
|------|------|
| macOS | 右键菜单注册 → 翻译 → 自动放回到 Zotero |
| Windows | 右键菜单 + 任务计划程序监控 |
| Docker | 完整容器化（docker + docker2 两套） |
| Zotero 监控 | 自动监听 Zotero 新 PDF → 自动翻译 |

---

## 二、查询拓展

### 2.1 pdf2zh vs pdf2zh_next 的关系

| 项目 | 特点 |
|------|------|
| PDFMathTranslate/PDF2zh | 最早版本，公式保留基础 |
| PDFMathTranslate-next | 升级版，支持更多模型/排版 |
| zotero-pdf2zh | 把两个引擎接入 Zotero 的插件 |

pdf2zh 才是翻译引擎本体，zotero-pdf2zh 是**接入层**。

### 2.2 与本机"PDF 笔记"链路的对应关系

本机工作流：收到链接/论文 → `web_extract`/本地 PDF → Agent 阅读 → 写 MD+HTML 笔记。

zotero-pdf2zh 对应的是**第 2 步（阅读层）的辅助工具**——解决"英文 PDF 阅读障碍"，属于**阅读增强**而非笔记生成。

### 2.3 Zotero 插件生态

基于 `windingwind/zotero-plugin-template`，同生态的知名插件：
- Better BibTeX（引用管理）
- ZOTERO 中文插件
- Zotero PDF2zh（本仓库，翻译）

---

## 三、归纳总结

### 3.1 三层架构

```
Zotero 插件（XPI，兼容 4 版本）
    ↓ REST 调用
Python Server（server.py + pdf2zh 引擎）
    ↓ 可选
Automation（右键菜单 / 监控 / Docker）
```

### 3.2 关键事实矩阵

| 维度 | 状态 |
|------|------|
| Star | 5.7k（活跃） |
| Commit | 616（成熟） |
| License | AGPL-3.0（**严格 Copyleft，商业闭源不可用**） |
| 当前状态 | **重构中，贡献冻结** |
| 版本 | XPI 4.1.6（主线） |

---

## 四、趋势判断

### 趋势 1：学术阅读层正在从"人读"转向"LLM 读 + 人审"

> 依据：zotero-pdf2zh 5.7k star + 9 月大版本重构——说明市场在成熟。双语对照+保留公式+批量翻译的形态将成为学术文献阅读的标准形态。

### 趋势 2：PDF 翻译从"API 调用"走向"本地化自治"

> 依据：server.py 独立进程 + uv/conda 自动识别 + Windows exe + Docker 多形态部署——用户希望本地控制而非完全云端依赖（成本/隐私/网络）。

---

## 五、关联分析

### 5.1 与本机"每日论文阅读"链路的关联

本机已有 `daily-paper-reading`、`daily-paper-push` skills（选文+精读）。PDF2zh 可以嵌入这条链路的"阅读辅助"层——但只在**本地人读 PDF** 的场景有意义。

### 5.2 与 bookmark-reader skill 的关联

bookmark-reader 是"收到链接→笔记"的主入口。PDF2zh 对应的是**笔记之后的本地阅读体验**（在 Zotero 里双语对照读原文），属于阅读增强而非笔记生成。

### 5.3 与本机 PDF 处理工具链的对比

| 能力 | pdf2zh (pdf2zh引擎) | 本机工具链 |
|------|-------------------|------------|
| 翻译 | ✅ 保留公式 | ❌（依赖 LLM 阅读英文原文） |
| 公式保留 | ✅（核心优势） | ❌（Markdown 输出丢失公式） |
| 中文笔记 | ❌ | ✅（7 模块笔记生成） |
| 双语对照 | ✅ | ❌ |

两者互补：pdf2zh 做**阅读时的翻译辅助**，Hermes 做**笔记时的结构化产出**。

---

## 六、拓展应用推荐

### 6.1 可迁移的方法论（不建项目也能学）

1. **插件独立 Server 架构**：重型引擎（pdf2zh）放独立 Python 进程，Zotero 插件只做 HTTP 客户端——比在插件进程里跑 Python 稳定得多。类比本机的"llm 推理服务独立进程"模式。

2. **uv/conda 自动识别**：`update_packages.py` 自动检测现有虚拟环境，优先 uv，无环境时再建——优雅处理多用户环境。

3. **双语对照渲染的 UX 模式**：原文/译文左右面板同步滚动——阅读增强插件的标配交互。

4. **双源更新（GitHub+Gitee）**：国内网络友好。类比本机的模型/API 多源降级链思想。

5. **Zotero 4 版本兼容策略**：通过分支/构建时选择不同 UI API，一套代码多版本兼容。

### 6.2 如果真要用它（个人学习场景）

- 装 Zotero 7/8 + 本 XPI + server.py，本地 LLM（本机 Nexa Ollama）+ 自定义 API 地址接入
- 注意 AGPL-3.0：仅供个人学习研究

---

## 七、不建本地项目的诚实判定

**❌ 不建本地 project，理由：**

1. **依赖 Zotero GUI**——本机是 Linux server（headless），无桌面环境，XPI 插件无法运行；`server.py` 单独跑无意义（它只是上游 pdf2zh 的封装）。

2. **上游引擎才是核心**——pdf2zh/pdf2zh_next 是翻译本体，zotero-pdf2zh 只是接入层。真正的技术内容是上游的"公式保留+双语对照"，不是本仓库。

3. **当前重构冻结期**——2026-08 公告 9 月大版本重构，贡献冻结，当前代码是过渡态，不值得本地维护一份。

4. **本机无此工作流**——Hermes 的笔记生成是 Agent 阅读+结构化输出，不需要在 Zotero 里双语对照读原文（Agent 直接用 LLM 读英文）。pdf2zh 的价值在**人读时**，不是**Agent 读时**。

5. **Skill 也无需**——本机没有 Zotero 相关 workflow，建 skill 没有调用场景。

**✅ 建笔记的理由：**

- 5.7k star 的成熟项目值得沉淀方法论（三层架构、双语对照 UX、多版本兼容、多源更新）
- 与本机"阅读增强 vs 笔记生成"的边界认知有澄清价值
- 上游 pdf2zh 的公式保留技术是 LLM 时代的稀缺能力，值得跟踪

---

## 八、指南分析

### 8.1 工程质量

- **README 结构完整**：功能/安装/常见问题/自动化，四层
- **i18n 覆盖**：中/日/韩/意/法五语言
- **多版本维护**：Zotero 7/8/9/10 四版本徽章
- **CI 覆盖**：windows-env-ci、release 工作流

### 8.2 局限

- **AGPL-3.0** 严格 Copyleft——任何修改/分发必须开源
- **正在重构**：当前代码是过渡态，9 月会有大变动
- **依赖上游引擎**：核心翻译能力不在本仓库，更新受上游节奏影响

---

## 九、行动启示

- **笔记已建**：本文件（方法论沉淀）
- **不建 project**：理由如上，避免空壳项目堆积
- **跟踪上游 pdf2zh_next**：如果本机未来需要 Agent 端侧翻译（比如离线英文笔记翻译），再考虑
- **双语对照 UX 可借鉴**：如果未来做"笔记中英对照"功能（学术笔记的常见需求），可复用此交互模式

## 相关笔记

- [nativePDF-零OCR数字原生PDF结构化工具评析](./2026-08-25-nativePDF-零OCR数字原生PDF结构化工具评析.md) — PDF 工具链近邻，解析侧对照
- [OpenDataLoader PDF 解析器](./2026-08-07-OpenDataLoader-PDF-AI就绪PDF解析器.md) — 同属文档 AI 工具评估系列
