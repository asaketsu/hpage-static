# 竞品吸收笔记：AutoClaw（智谱）& OfficeClaw（华为云）

> 日期: 2026-04-17
> 来源: 微信公众号文章 × 2，猫仔团队竞品分析
> 状态: 已落地吸收，6 个新 Skill 已创建 ✅

---

## 一、竞品概览

| 维度 | AutoClaw（智谱） | OfficeClaw（华为云） |
|------|-----------------|---------------------|
| 定位 | AI 个人助手 SaaS | 企业级 AI 办公平台 |
| 核心卖点 | 自进化 + GLM Office Skills | Harness Engineering 框架 + 规模化 Skill 生态 |
| 技术底座 | 智谱 GLM 系列 | 华为盘古 + GLM |
| Skill 数量 | 专家共创数十个 | 声称 33,614 个 |
| 多 Agent | 命名 Agent 协同 | Alice/Bob/Charlie/Eve 四角色 |
| 目标用户 | C 端/小 B | 企业客户 |

---

## 二、功能对比矩阵（vs 猫仔/Hermes）

| 能力维度 | 竞品（AutoClaw/OfficeClaw） | 猫仔（Hermes） | 裁定 |
|----------|---------------------------|---------------|------|
| 多 Agent 协同 | ✅ 内置命名 Agent | ✅ delegate_task 子代理 + 4喵团队角色 | **打平** |
| PPT 深度生成 | ✅ 逐页 HTML→PPTX | ✅ ppt-generator + html-slides + powerpoint 三技能联动 | **打平** |
| 风格系统 | ✅ 5种预设（华为/Apple/Claude/NVIDIA） | ✅ html-slides 12种预设 + 自定义 Skin | **我们更多** |
| PDF 解析 | ✅ 423页→90KB Markdown | ✅ web_extract PDF + ocr-and-documents | **打平** |
| 调研能力 | ✅ 联网搜索+抓取 | ✅ web_search + web_extract + Tavily（微信文章绕反爬） | **打平** |
| 任务规划 | ✅ 自动6阶段拆解 | ✅ plan + task-executor + planning-with-files | **打平** |
| 自验证/QA | ✅ stage 校验 | ✅ doc-qa 层（5层校验） | **打平** |
| XLSX 生成 | ⚠️ 部分（GLM Office） | ✅ xlsx-generator（openpyxl 专业级） | **我们优** |
| 多文档联动 | ⚠️ 逐个生成 | ✅ office-pipeline 一键出 PPT+DOCX+XLSX | **我们优** |
| 人物建模 | ✅ 女娲 Skill | ✅ persona-modeler | **打平** |
| 深度分析 | ✅ 横纵分析法 | ✅ deep-analysis（6步+交叉验证） | **打平** |
| 进化控制 | ✅ 对话中审批卡片 | ✅ evolution-control（质量评估+审批） | **打平** |
| 微信文章提取 | ❌ 未提及 | ✅ Tavily 绕反爬 | **我们独有** |
| 飞书集成 | ❌ 未提及 | ✅ 飞书 Gateway 已上线 | **我们独有** |
| 品牌风格预设 | ✅ 华为/Apple/Claude/NVIDIA 等 | ⚠️ 有12种 html-slides 预设但缺品牌名 | **可吸收** |

---

## 三、吸收动作（已完成 ✅）

从竞品分析中提炼了 6 个可落地 Skill，已创建完毕：

### 3.1 persona-modeler（研究类）
- **来源**: AutoClaw 女娲 Skill
- **路径**: `research/persona-modeler/SKILL.md`
- **核心**: 输入人名 → 多源调研 → 提炼决策模型/表达DNA/心智模型 → 生成可复用 persona 文件
- **5步流程**: 信息采集 → 结构化提炼 → 决策模拟器 → 生成 persona → 验证
- **输出**: `~/uclaw/personas/{人物名}.md`

### 3.2 deep-analysis（研究类）
- **来源**: AutoClaw 横纵分析法
- **路径**: `research/deep-analysis/SKILL.md`
- **核心**: 多源检索 → 交叉验证 → 结构化归纳 → 带引用深度报告
- **6步流程**: 定义框架 → 多源检索（≥3类源）→ 交叉验证 → 结构化归纳 → 生成报告 → 质量自检
- **验证规则**: 三源一致=确证, 双源=较可靠, 单源=待验证, 矛盾=争议点

### 3.3 xlsx-generator（生产力类）
- **来源**: AutoClaw GLM Office / OfficeClaw 表格能力
- **路径**: `productivity/xlsx-generator/SKILL.md`
- **核心**: openpyxl 专业级 Excel 生成，带格式/图表/公式/条件格式
- **样式**: 蓝底白字表头 + 隔行浅蓝 + 千分位分隔 + 冻结首行
- **依赖**: `pip install openpyxl`（已装）

### 3.4 office-pipeline（生产力类）
- **来源**: AutoClaw "一行命令出调研PPT+讲稿"
- **路径**: `productivity/office-pipeline/SKILL.md`
- **核心**: 一个指令 → 同时输出 PPT + DOCX + XLSX 多种格式
- **生成顺序**: XLSX（数据先行）→ DOCX（完整报告）→ PPT（汇报精简版）
- **调用关系**: xlsx-generator + ppt-generator/html-slides + doc-qa

### 3.5 evolution-control（DevOps 类）
- **来源**: AutoClaw 进化审批卡片
- **路径**: `devops/evolution-control/SKILL.md`
- **核心**: memory 写入前质量过滤 + 用户审批 + 进化摘要查询
- **质量评分**: 持久性(3) + 独特性(3) + 精确性(2) + 可操作性(2) = 满分10
- **阈值**: ≥7 高质量推荐保存, 4-6 需确认, ≤3 静默丢弃

### 3.6 doc-qa（DevOps 类）
- **来源**: OfficeClaw stage 校验
- **路径**: `devops/doc-qa/SKILL.md`
- **核心**: 通用文档质量校验，5层检查
- **5层**: 格式完整性 → 内容正确性 → 排版美观度 → 可交付性 → 交叉一致性
- **集成**: 被 ppt-generator/xlsx-generator/office-pipeline/nano-pdf 调用

---

## 四、待吸收/未来考虑

| 项目 | 来源 | 优先级 | 状态 |
|------|------|--------|------|
| 品牌风格预设包（华为/Apple/NVIDIA等） | OfficeClaw | 中 | 待开发 |
| 命名 Agent 品牌化（不只是 Dev-Meow） | OfficeClaw | 低 | 已有团队角色 |
| Skill 商店/社区生态 | AutoClaw | 远期 | agency-agents 147个模板备用 |
| Harness Engineering 框架借鉴 | OfficeClaw | 中 | 已在 skill 中体现约束/验证思想 |

---

## 五、关键洞察

1. **打平是常态** — 核心能力大家都有，差异在体验和生态
2. **我们的优势**: 微信生态（Tavily 绕反爬）、飞书集成、多格式联动 pipeline
3. **我们的劣势**: 品牌风格预设少（需补充知名品牌模板）、SaaS 化程度低
4. **竞品软文需警惕**: OfficeClaw "33,614 个 Skill" 和 "无模板味无 AI 感" 需打折看待
5. **agency-agents 备用**: 147 个中文 Agent prompt 模板已入库，可按需 convert 为 Hermes skill

---

## 六、Skill 调用速查

```
用户说"分析XX的思维/决策风格" → persona-modeler
用户说"深度分析/竞品分析/行业调研" → deep-analysis
用户说"生成Excel/做个表格/XLSX" → xlsx-generator
用户说"出一套/全套材料/同时生成" → office-pipeline
用户说"你最近学会了什么/进化记录" → evolution-control
生成任何办公文档后 → doc-qa 自动加载
```


## 相关笔记
- [智谱 AutoClaw 自进化 + Skill 商店：不需要研究 Hermes](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [竞品吸收笔记：OpenCLI — Universal CLI Hub & AI-Native Runtime](2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记：khazix-skills](2026-04-29-竞品吸收笔记-khazix-skills.md)
- [GenericAgent 竞品吸收笔记](竞品吸收笔记_GenericAgent.md)
- [竞品吸收笔记：Fokkyp/SoftwareCopyright-Skill](2026-05-10-softwarecopyright-skill-analysis.md)
