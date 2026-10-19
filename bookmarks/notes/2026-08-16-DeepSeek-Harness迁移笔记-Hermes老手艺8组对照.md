# DeepSeek Harness（dsh）迁移笔记：Hermes 老手艺的 8 组对照与 3 个新概念

> **出处**：@ChrisWangwy（老爸的AI联萌）X 长文 2026-08-16《我用了半年 Hermes，换 DeepSeek Harness 只花了一个下午》；CLI 输出均为作者 2026-08-15 本地实测
> **原文链接**：https://x.com/i/status/2088960776363192402
> **记录日期**：2026-08-16

**标签**：#DeepSeek-Harness #dsh #Hermes #Agent框架 #Cordis #插件化 #迁移指南

---

## 一、原文核心内容（完整还原）

### 1.1 dsh 是什么

- **Model + Harness = Agent**：模型是大脑，Harness 是手脚（文件/终端/浏览器接口）
- DeepSeek Harness 2026-08-13 开源，一天 3 万星（deepseek-ai/deepseek-harness，MIT 协议）
- 版本迭代极快：rc.5（13 日）→ rc.6（15 日），官方明示预览期有破坏性变更
- 底层跑在 Cordis 插件框架上，核心哲学：**Everything is a Plugin**——模型适配、工具、会话、沙箱、存储、后台任务、Agent 主循环本身全是插件
- **背景细节**：开源 Harness 同日 V4-Pro API 涨价（8 月 16 日生效，峰值输出 4.6×）——"送免费的壳，收更贵的脑"

### 1.2 8 组对照迁移地图（全文核心）

| # | Hermes | dsh | 关键差异 |
|---|--------|-----|----------|
| 1 | Profile（养几个长期员工） | Profile + **Agent Preset**（标准/PTC/极简/创造四工种） | dsh 一个进程可同时开三种模式会话 |
| 2 | /goal（同一个人接着干） | Goal + **Ralph**（三班倒：干完→改工作区→留交接→换新人） | Ralph 适合超长任务，长期状态写进项目文件+结构化交接 |
| 3 | execute_code | **PTC**（Programmatic Tool Calling：模型写 TypeScript 编排工具，run_code 一次执行） | 同一思想：让 Agent 写程序组织工具调用，中间结果留在执行环境 |
| 4 | delegate_task | Subagent + **Workflow** | dsh 多了持续管理（list_agents/send_message/interrupt_agent）和多人编排 |
| 5 | 后台进程 | Background Jobs（job_list/output/kill） | 贴心设计：任务完成可唤醒空闲 Agent（有防自激边界） |
| 6 | Cron | Schedule（after_seconds/at/every_seconds） | ⚠️ **千万别画等号**：dsh 是 session-local，会话关了没有外部常驻调度 |
| 7 | Skill | Skill（.dsh/skills、.agents/skills） | 几乎原样迁移；新增调用边界声明（disable-model-invocation） |
| 8 | 上下文管理 | **Spill + Compaction** 两道防爆墙 | Spill 防"单次工具调用拉爆"（存全文只给首尾），Compaction 防"慢性膨胀" |

### 1.3 真正要重新学的三样

1. **Trajectory（全程留痕）**：系统提示词/思维链/每次工具调用与返回全部写入只增不改日志，可回放对质——"真抓取还是脑补，翻记录就知道"。HN 最响好评，被称为 killer feature（对比美国厂商隐藏这层数据=信任优势）
2. **Session Fork**：会话像 Git 一样开分支——从历史节点拉新分支继续，不污染原会话（实验/比方案利器）
3. **Dynamic Cordis**：Agent 运行时检查甚至改造自己的插件组合/运行时——"Agent 自己给自己加装手脚"，想象力的天花板

### 1.4 实测配置要点（dump-default-config）

- 默认模型 deepseek-v4-flash（性价比款）
- 默认权限 workspace-write（非全开）
- Windows 自动关 bash 沙箱、启用 PowerShell 沙箱（平台适配细）
- 遥测默认 DISABLED
- 自我定义："ordered stack of plugin-bundle patch layers"（按序叠加的插件补丁层）

### 1.5 社区争议与硬数据

- **正方**：稳定核心与长尾集成严格隔离，插件是正确解法
- **反方**：社区插件生态 = 头六个月很好，之后不兼容/过时/治理噩梦（Eclipse、VS Code 前车之鉴）
- **变局**：AI 能帮写插件——甚至不需要社区，Agent 自己造
- **门槛**：Node.js + 终端 + API Key 对普通用户不友好；文档工程向；v0.1 长任务跑 30min+ 是常态
- **硬数据**：同一 V4-Flash 接 8 种 harness 测 30 项任务——最好 20 项 vs 最差 14 项，**模型相同结果差三成**："模型划定能力上限，Harness 决定兑现多少"
- 热评（UBsoft）："Hermes 优势是有人打理，DSH 生态太新没有核心主理人——大部分人不可能每天花四小时打理"

---

## 二、五要素展开

### 2.1 功能清单

| 功能 | dsh 对应 | 迁移成本 |
|------|----------|----------|
| 多角色配置 | Profile + Agent Preset ×4 | 概念换名 |
| 长任务持续 | Goal + Ralph 轮班 | 新学 Ralph |
| 代码编排工具 | PTC（TS 编排 + run_code） | 经验直接搬 |
| 子任务委派 | Subagent + Workflow | 心智无断层 |
| 后台任务 | Jobs 三命令 | 直接搬 |
| 定时任务 | Schedule（⚠️ session-local） | 预期要重设 |
| 技能沉淀 | Skill（目录+权限声明） | 几乎原样 |
| 上下文防爆 | Spill + Compaction | 拆得更细 |

### 2.2 使用性评估

**强项**：架构彻底性（一切皆插件=没有动不得的底盘）；Trajectory 透明度（对质幻觉的信任基建）；Ralph/PTC/Workflow 对长任务和批量任务的设计成熟度。

**短板**：v0.1 完成度粗糙（rc 两日一版=不稳定）；无常驻调度器（session-local Schedule 与 Hermes Cron 语义差距大）；生态无主理人（对比 Hermes"有人打理"）；上手门槛高。

**适用判断**：值得装一个 dsh 做技术雷达跟踪；生产自动化（无人值守 cron 体系）继续 Hermes；两者不是替代关系是生态位差异。

### 2.3 指导性意见

- **迁移策略**：8 组对照先搬 Skill/后台/上下文管理（零成本），再学 Ralph/PTC（低成本高收益），Schedule 预期必须重设
- **别急着迁移生产**：rc 版本两天一破坏性变更，等 1.0 再评估
- **最有价值的借鉴**（不换框架也该学）：①Trajectory 只增日志——Hermes 可通过 session 持久化+审计链对齐；②Spill 首尾截断——大工具输出落盘+预览，正是 context-compressor 思路；③Ralph 交接班——subtask-lifecycle 的交接信息结构化可借鉴
- **Hard 真相吸收**："模型相同，harness 不同，结果差三成"——harness 工程的价值有了量化锚点，投入 harness 优化的 ROI 被实证

### 2.4 案例可寻

- 作者实测三步：--version → CLI 自述 → --dump-default-config 打印插件树（可直接照抄的评估流程）
- "修整个测试套件"作为 Ralph 三班倒的典型场景
- npm test 20 万字日志作为 Spill 的典型场景
- 8 harness × 30 任务对比（20 vs 14）作为 harness 价值量化案例

### 2.5 使用方法借鉴

**评估任何新 Agent 框架的半天流程（从本文提炼）**：
```bash
# ① 版本与迭代速度
npx -y <pkg> --version
# ② 自我定义（架构哲学）
<cli> --help
# ③ 默认配置树（安全/模型/权限/遥测）
<cli> --profile headless --dump-default-config
# ④ 对照自己的 8 组常用能力找落点
# ⑤ 跑一个真实小任务验证
```

---

## 三、查询拓展

1. **Cordis 是什么**：DeepSeek 的插件运行时框架（文中"meta-framework of spatiotemporal composability"的抽象描述劝退不少人）——dsh 的一切皆插件建立在它之上，理解 dsh 深度定制的必经之路
2. **Ralph 与 Anthropic 协作的相通**：交接班模式=把长期状态外化到文件系统而非对话历史——与 planning-with-files（Manus 式文件规划）、我们的 harness-checkpoint 同一思想谱系
3. **PTC 与 MCP 的关系**：PTC 是"程序编排工具调用"，MCP 是"工具发现协议"——正交可组合：MCP 提供工具供给，PTC 提供调用编排
4. **Spill 与 context-compressor**：同构设计（全文落盘+首尾预览+按需 grep）——Hermes 已有此能力，dsh 把它做成了默认行为而非技能
5. **V4-Pro 涨价与开源 Harness 的组合拳**：壳免费+脑涨价的商业逻辑=降低迁移摩擦后提高边际收益——平台经济的标准打法，值得所有 Agent 从业者读的第二层

---

## 四、内容整理

**原文信息架构**：dsh 是什么（一句话+实测版本）→ 8 组对照迁移地图（核心）→ 3 个新概念（Trajectory/Fork/Dynamic Cordis）→ 实测配置 → 社区争议+硬数据 → 结论（不用重学但要认识，方法比工具活得久）。

**本笔记重组**：对照表 → 可信度（作者一手实测，CLI 输出可复现）→ 不换框架的可借鉴清单（Spill/Ralph/Trajectory 思想）→ 生态位判断（Hermes=有人打理的常驻自动化 vs dsh=激进插件化实验场）。

**核心增量判断**：本文表面是迁移指南，实质是 **Agent 框架的能力坐标系**——8 组对照=成熟 Agent 的能力完备集；"模型定上限 Harness 定兑现率"+30% 差距数据是 harness 工程价值的首个量化锚点。

---

## 五、趋势判断

1. **Harness 层竞争白热化**：DeepSeek 官方下场（一天 3 万星）+ 8 harness 对照测试出现——2026 下半年 harness 会成为与模型同级的竞争维度
2. **"一切皆插件"会成为激进派标配**：Dynamic Cordis（Agent 自改运行时）如果被验证，会催生自进化 Agent 的实用化路径
3. **Trajectory 全程留痕会成为信任基建**：可回放对质能力从加分项变成企业采购必选项（尤其对幻觉敏感场景）
4. **session-local 是 dsh 当前最大软肋**：无常驻调度器使其暂时无法承接生产自动化——Hermes 类有常驻网关+cron 体系的框架守住企业场景
5. **"方法比工具活得久"是长期主义者的正确姿势**：Skill 沉淀/后台任务/上下文控制/子 Agent 委派这套方法论跨框架通用——投资方法论的复利高于投资单一工具

---

## 六、归纳总结

**一句话**：dsh 用"一切皆插件"重构了 Agent harness，Hermes 用户 8 组手艺半天可搬（唯 Schedule≠Cron 要警惕），真正的新东西是 Trajectory 留痕/Session Fork/Dynamic Cordis；"模型定上限，Harness 定兑现"有了 30% 差距的量化实证。

**结构记忆**：
- 一个公式：Model + Harness = Agent
- 八组对照：Profile/Goal/execute_code/delegate_task/后台/Cron/Skill/上下文
- 三个新概念：Trajectory（对质幻觉）/ Fork（会话分支）/ Dynamic Cordis（自改运行时）
- 一个警告：Schedule 是 session-local，别当 Cron 用
- 一个数据：同模型 8 harness，结果差 30%

---

## 七、关联分析

| 关联 | 关系 |
|------|------|
| Hermes Agent（自家框架） | 直接对照对象：本文是 Hermes 用户视角的 dsh 评估，8 组对照反向也是 Hermes 能力完备性的佐证 |
| harness-architecture skill | 六层 harness 架构与 dsh 插件栈设计互为印证——"ordered stack of plugin-bundle patch layers"是六层论的插件化实现 |
| context-compressor | Spill 的同构实现：全文落盘+首尾预览——dsh 把它默认化值得跟进 |
| subtask-lifecycle | Ralph 交接班模式的参照：长期状态外化到文件+结构化交接 |
| agent-primitive-architecture | Agents/Skills/Hooks 三原语与 dsh 一切皆插件的架构哲学对照 |
| 8×A100 体系（playbook/farm） | dsh 默认 v4-flash 与 DeepSeek 生态共用模型层——部署层笔记的框架侧延伸 |

---

## 八、行动清单

- [x] X 长文全文提取 + 7 模块笔记
- [ ] 本地 npx 试用 dsh（按本文五步评估流程跑一遍）
- [ ] Hermes 借鉴项评估：Trajectory 式审计日志 / Spill 默认化 / Ralph 交接结构
- [ ] 追踪 dsh 1.0 正式版（Schedule 是否补常驻调度）
- [ ] 8 harness × 30 任务对照测试的原始报告溯源

---

## 九、一句话总结

> 模型定上限，Harness 定兑现——同模型换 8 种 harness 结果差三成；dsh 的一切皆插件是激进实验场，Hermes 的常驻自动化是生产阵地，8 组手艺通用，方法比工具活得久。


## 相关笔记

- [AI4AI-at-TestTime-强到弱Harness能力转移](./2026-08-16-AI4AI-at-TestTime-强到弱Harness能力转移.md) — 同日姊妹篇，Harness 能力转移方法论
- [从RL到蒸馏到软蒸馏-Why-RL-Matters](./2026-08-16-从RL到蒸馏到软蒸馏-Why-RL-Matters.md) — 模型能力来源侧，与 Harness 兑现率互补
