# CATIA KnowledgeWare 知识工程

来源：CATIA KnowledgeWare 项目文档整理
链接：~/uclaw/project/catia-knowledgeware/
日期：2026-05-26
评分：⭐4/5
标签：#CAD #参数化设计 #知识工程 #CATIA #EKL

## 摘要

CATIA KnowledgeWare 是达索系统的参数化与规则引擎模块，将设计经验、企业标准和工程规则转化为可复用的知识对象嵌入 3D 模型。核心由五大模块组成：KWA（知识顾问，基础层）、KWE（知识专家，企业级）、PKT（知识模板，批量复用）、BKT（业务知识模板，PLM集成）、PEO（产品工程优化器，变型设计）。EKL 是其专用规则语言，强类型、必须带单位、支持 if-else/while 循环。

## 核心内容

### 1. 五大模块架构

模块层级关系：KWA（基础）→ PKT（封装复用）→ KWE（企业级扩展）→ PEO（变型优化）+ BKT（PLM集成）

- KWA：所有知识对象的基础创建环境，核心对象有 Parameter、Formula、Rule、Check、Design Table、Law、Reaction
- KWE：面向知识工程师，支持完整 EKL + 类型系统、专家规则、知识库、PLM 集成
- PKT：Power Copy（同零件复用）→ UDF（跨零件复用）→ Knowledge Pattern（批量实例化）→ Document Template（文档级模板）
- PEO：多场景配置、设计空间探索、约束优化
- BKT：与 PLM 集成的企业级参数化模板

### 2. EKL 语言核心语法

- 数值必须带单位（5mm、30deg、10kg），这是铁律
- 注释用 `--`，不支持 /* */ 风格
- 变量引用用反斜杠路径：`PartBody\Hole.1\Diameter`
- 条件：if/elseif/else/endif
- 循环：while/endwhile、for/next（部分版本）
- 字符串拼接用 `&` 或 `\(变量)` 插值
- Check 结果只有三种：Pass/Fail/Warning
- Reaction 是 Check 失败时的自动修正脚本

### 3. 关键内置函数

- 消息：Message()、MessageBox()
- 数学：sin/cos/tan/sqrt/abs/max/min/power/log/exp
- 参数：GetParameter()、SetParameter()
- 字符串：Len/Left/Right/Mid/Trim/Str/Val

### 4. 工作流（8步闭环）

创建参数 → 建立公式 → 编写规则（EKL）→ 设置检查（合规性验证）→ 配置反应（失败自动修正）→ 封装为模板（Power Copy/UDF/PKT）→ 批量实例化（Knowledge Pattern）→ 集成企业知识库（KWE+PLM）

## 关键概念

- KBE（Knowledge Based Engineering）：知识驱动设计的总称
- Parameter：驱动模型的所有变量，是 KWA 的原子对象
- Formula：参数间的数学关系 y=f(x,z,...)
- Rule：基于 EKL 的逻辑规则，含条件判断和循环
- Check：设计合规性验证，输出 Pass/Fail/Warning
- Reaction：Check 失败时触发的自动修正或通知
- Design Table：Excel/文本驱动的参数配置表，支持多规格切换
- Law：数学函数关系 y=f(x)，用于变截面、渐变曲率等
- UDF（User Defined Feature）：可复用的参数化特征，跨零件可用
- Knowledge Pattern：批量实例化 UDF 的机制

## 能力边界

- 面向普通设计师，不需要编程背景（区别于 CAA RADE 需要 C++）
- EKL 功能有限，不支持面向对象、异常处理、文件 I/O
- 知识对象绑定在 CATIA 模型内部，脱离 CATIA 环境无法独立运行
- 复杂优化（如拓扑优化、多物理场耦合）仍需专门工具
- 大规模知识库管理依赖 KWE + PLM（Enovia），中小企业部署成本高

## 最佳实践

1. 所有数值必须带单位 — EKL 的铁律，不带单位必报错
2. 参数命名要有业务含义 — 避免 A1、Param1 等无意义命名
3. 复杂规则拆分为多个小规则 — 便于调试和维护
4. 先用 Message 输出调试信息 — EKL 没有 debugger，靠 Message 定位问题
5. 善用 Design Table 做规格管理 — 比硬编码参数值灵活得多
6. Knowledge Inspector 查依赖关系 — 修改参数前先看影响范围
7. 参数锁定防止误改 — 关键参数 Lock 后变灰不可编辑

## 🔍 借鉴学习进化点（必填）

1. **规则引擎的分层架构** — KWA(基础)→KWE(企业)→PLM(平台)的分层思路，可迁移到 Agent 系统的 Skill 分层：基础Skill→领域Skill→平台Skill
2. **Check+Reaction 自动修正模式** — 设计验证+自动修正的闭环，对应 Agent 系统的 auto-defense-check + evolver 的自愈闭环
3. **Design Table 的数据驱动** — 参数配置与逻辑分离，用表格驱动行为。对应 Hermes 的 config.yaml + .env 分离模式
4. **Knowledge Pattern 批量实例化** — 一个模板批量生成多个实例的模式，对应 delegate_task 的批量子任务派发
5. **知识对象全绑定在模型中** — 知识和模型不分离，任何拿到模型的人都能用。对应 Skill 的自包含设计（SKILL.md + scripts 一体）

## 🔗 RAG / Wiki 联动（必填）

### 当前状态
- wiki-kb：暂无 CATIA/CAD 相关条目
- RAG：无相关索引
- Memory：DroneBridge/ESP32 项目有嵌入式开发记录，CAD 领域空白

### 改进方案
1. 将此笔记加入 wiki-kb 的 engineering 类别
2. EKL 语法参考可作为编程语言参考卡收录

### 已执行操作
- ✅ 笔记已写入 ~/uclaw/bookmarks/notes/
- ⏳ wiki-kb 类别待后续扩展


## 相关笔记
- [[2026-04-19-处理大模型幻觉的工程心得.md|处理大模型幻觉的工程心得]]
- [[2026-05-04-雨哥Cloudflare五件套AI周刊自动化.md|雨哥向前冲：Cloudflare 五件套白嫖全自动AI科技周刊]]
- [[2026-04-03-Claude-Code四层记忆架构.md|2026-04-03-Claude-Code四层记忆架构]]
