# 竞品吸收笔记：Fokkyp/SoftwareCopyright-Skill

> 日期：2026-05-10
> 来源：https://github.com/Fokkyp/SoftwareCopyright-Skill
> Stars: 1.1k | Forks: 200 | License: MIT
> 定位：Codex（OpenAI）平台的软著申请材料生成 Skill

---

## 1. 项目画像

| 维度 | 内容 |
|------|------|
| 平台 | OpenAI Codex（非 Hermes） |
| 语言 | Python 脚本 + SKILL.md 指令 + .NET DOCX 工具 |
| 核心功能 | 从真实项目 → 分析 → 生成全套软著申请 DOCX/TXT |
| 特色 | 强制人工门禁、去 AI 味操作手册、代码真实性保证 |

## 2. 核心架构：11步流水线

```
环境检查 → 定位项目 → 分析项目 → 业务理解 → 确认字段
→ 代码文件选择 → Markdown草稿 → 截图选择 → 用户确认
→ 生成正式DOCX/TXT → 三轮验证
```

每步之间有**强制人工门禁**（confirm_stage.py），必须用户确认才能继续。

## 3. 与我们现有能力的对比

| 能力 | 我们（jbot） | Fokkyp | 差距 |
|------|-------------|--------|------|
| 源代码注释规范化 | ✅ 10条规则+去AI化 | ❌ 不做注释规范化 | **我们领先** |
| DOCX 页眉页脚域码 | ✅ 完整XML方案 | ✅ .NET docx-toolkit | 各有方案 |
| 业务理解先行 | ❌ 直接写 | ✅ 先理解→再写 | **需学习** |
| 操作手册去AI味 | ❌ 无自检流程 | ✅ 3轮自检+记录 | **需学习** |
| 代码选择引导 | ❌ 手动筛选 | ✅ 候选→模型选→用户确认 | **需学习** |
| 强制门禁机制 | ❌ 无 | ✅ confirm_stage.py | **需学习** |
| 申请表字段管理 | ❌ 无 | ✅ 完整字段管理 | **需学习** |
| 截图集成 | ❌ 无 | ✅ MCP/Computer Use/手动 | **需学习** |
| 前后30页规则 | ✅ 有 | ✅ 有 | 持平 |
| PDF生成 | ✅ reportlab方案 | ❌ 只出DOCX | **我们领先** |

## 4. 可借鉴模式

### 4.1 业务理解先行模式（高优先）

流程：脚本收集证据 → 模型研判行业/用户/价值 → 生成业务理解 JSON → 用户确认 → 才写手册/申请表

**价值**：避免"代码有什么就写什么"的泛泛描述，写出有针对性的材料。

### 4.2 操作手册3轮自检（高优先）

- 第1轮：章节完整性、内容厚度
- 第2轮：按项目真实流程扩写
- 第3轮：去制式表达和AI味
- 后续轮次直到问题清零

**价值**：系统化的去AI味流程，有记录可追溯。

### 4.3 强制门禁机制（中优先）

每个关键节点必须用户确认（confirm_stage.py），JSON记录确认内容和时间。

**价值**：防止"一口气生成"导致材料写偏。

### 4.4 代码选择引导（中优先）

候选文件清单 → 模型选择+理由 → 用户确认 → 才抽取

**价值**：确保抽取的代码最能体现软件功能。

### 4.5 申请表字段集中管理（中优先）

20个字段统一生成到 `申请表信息.txt`，官网填报时对照复制。

**价值**：减少官网填报时的遗漏和错误。

## 5. 不应借鉴的部分

- .NET docx-toolkit：我们用 python-docx 方案已足够，引入 .NET 增加复杂度
- Codex 特有的 Computer Use 集成：我们用 Hermes browser 工具
- vendor 目录（600KB+ 的 OpenXML 百科）：过度工程化

## 6. 融合计划

1. **立刻**：将"业务理解先行"和"3轮自检"模式融入 software-copyright-pdf skill
2. **立刻**：添加申请表字段管理流程
3. **短期**：添加代码选择引导流程
4. **暂缓**：门禁机制（我们的工作模式不同，用户实时交互即可）

## 相关笔记
- [skill-building-invoice-automation](2026-05-10-skill-building-invoice-automation.md)
- [nTop-Automate-CLI-完整测试文档](2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](2026-05-15-数据目录工具全景指南.md)
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
