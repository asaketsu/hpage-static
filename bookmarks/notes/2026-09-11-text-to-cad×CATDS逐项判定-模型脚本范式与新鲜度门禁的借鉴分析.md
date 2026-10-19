# text-to-cad（cadgen）× CATDS 逐项判定：技能库架构、模型脚本范式与新鲜度门禁的借鉴分析

> **来源**：GitHub earthtojake/text-to-cad（13.7k stars / 1.4k forks / 970 commits / MIT）2026-09-10 主线
> **原文链接**：https://github.com/earthtojake/text-to-cad（skills/cad/SKILL.md 17KB 全文精读）
> **对照项目**：~/uclaw/project/CATDS（CATIA NL→JSON→pycatia COM，B1-B7 工程严谨层 09-10 刚落地）
> **抓取方式**：GitHub web + raw SKILL.md 全文 + CATDS AGENTS.md 交叉
> **笔记日期**：2026-09-11
> **关联笔记**：《2026-09-10-CAD-Agent-Hub对比借鉴方案》（B1-B7 来源，已完成落地）

---

## 零、结论先行

**四分判定：已满足 2 项（关闭）、新增主线 1 项（最小动作+验收门）、增强阶段 3 项（带触发条件）、明确不做 3 项（给理由）。** text-to-cad 与 CATDS 是同赛道不同层：它是 **agent skill 库**（给 Claude/Codex 用的 CAD 生成技能包，内核 build123d+cadgen），我们是 **独立应用**（CATIA COM 语义建模）。最大可借鉴的三点：①**"模型即脚本"范式**（生成无 CLI——纯 Python 脚本+装饰器声明输出，与我们 NL→JSON→COM 的 JSON 中间层对照出"第三范式"）②**内容寻址 store + 新鲜度门禁**（增量构建的 DAG 契约）③**SKILL.md 的默认假设节**（建模默认值的显式契约——单位/原点/平面/壁厚/孔径全部写成 skill 契约）。

## 一、text-to-cad 是什么（忠实还原）

### 1.1 定位与规模

**"A library of agent skills for CAD, CAE and CAM"**——不是应用，是给 coding agent（Claude Code/Codex/Grok Build）安装的技能包。11 个 skill：cad/cad-viewer/step-parts（找现货件 STEP）/dxf/urdf/srdf（MoveIt）/sdf（仿真）/sendcutsend（钣金下单前置检查）/gcode（切片）/bambu-labs（打印作业）/implicit-cad（GLSL SDF，实验性）。

**从文本到制造的完整链**：CAD 建模 → STEP/STL/3MF/GLB → DXF 切割图 → SendCutSend 钣金下单 → G-code 切片 → Bambu 打印。加 URDF/SRDF/SDF 的机器人描述族——**CAD→CAE→CAM 的 agent 化全覆盖**。

### 1.2 架构核心：cadgen 运行时 + 模型脚本范式

**"生成无 CLI"**——模型就是一个 Python 脚本：

```python
from cadgen import build123d as bd
from cadgen import step

@step                      # 装饰器声明输出：STEP
def bracket():
    return bd.Box(10, 10, 10)   # 返回裸 build123d Shape

if __name__ == "__main__":
    bracket()               # 调用才构建；导入永不构建
```

规则（每条由装饰器或构建强制）：
- **装饰器只声明，调用才构建**；无 `__main__` 调用的文件永不构建
- **模型无参数**——参数化几何在工厂函数里，"另一个配置=另一个模型文件，如同两个零件号是两个零件"
- 返回裸 Shape（solid/compound/带标签装配复合体）——**绝不 dict、绝不绝不路径**
- 装饰器参数永不改几何，只决定输出位置/网格容差/运动学 sidecar
- **组合=调用**：父模型 import 兄弟模型并调用，得到子几何；父结果 LINK 子结果（存储一次，全体父共享）

### 1.3 内容寻址 store + 新鲜度门禁（最精巧的部分）

- `~/.cache/cadgen`：objects/（不可变、内容寻址的组件与树）+ index/（每模型记录：gate 读的记录/op memo/网格台账）——**只存派生结果**
- **新鲜度 gate 逐子句裁决**：`cadgen store why model.py` 打印 record/closure 文件/常量/每个子模型 pinned-vs-current 树/输出——"模型该重建没重建时先跑 why"
- 依赖是**拉式**的：子重建不更新用它的装配——重建父才拾取子的变更
- **环境不是输入**：模型代码不从 os.environ/cwd/当前时间/随机源取参——gate 看不见的东西改变几何会留下"读作 current 的 stale 结果"
- **每次构建并行**：子调用提交构建立即返回，兄弟在各自 worker 上建，父首次读几何时等（通常在收尾的 `bd.Compound`）；暖 daemon 默认开，每核一个构建
- 三档重置从小到大：`--force`（单模型）→ `store forget`（丢记录）→ `rm -rf store`（**永远安全**——全部读 stale 重建，不碰项目文件）
- 流分离：stdout 结果 / stderr 进度时序失败——`2>/dev/null` 得干净可解析输出

### 1.4 SKILL.md 的工程契约（skill 写作范本）

- **默认假设节**：单位 mm/原点按零件型/XY 基面/Z 挤出/封闭正体积/**小塑料壳壁 2-3mm**/**装饰圆角 1-3mm**/**M3/M4/M5 常规间隙孔 3.4/4.5/5.5mm**——第一轮建模默认值全部写成契约
- **何时用/何时不用**：明确排除 render-only 概念图/CAM 刀轨/工程认证/FEA 结论/建筑 BIM
- **只问一个聚焦的澄清问题**：仅当缺信息使模型不可能/配合关键/安全关键/合规绑定——否则带着显式假设继续
- `cadgen doctor` 验证安装版本匹配 skill 钉住的版本（"docs 在不匹配的安装上静默漂移"）
- 命令从拥有工件的工作区跑、传 cwd 相对路径——"项目 CAD 文件永不误解析到 skill 目录下"

## 二、逐项对照判定（CATDS 现状 × text-to-cad 机制）

| # | text-to-cad 机制 | CATDS 现状 | 判定 | 理由与动作 |
|---|----------------|-----------|------|-----------|
| 1 | **模型即脚本（无 CLI 生成）** | NL→JSON→COM 三层，JSON 是中间契约 | ✅ **已满足，关闭** | 我们的用户面是 NL 不是代码；JSON 中间层是 B1 契约层的地基，换脚本范式=推翻 B1-B7。**保留现状** |
| 2 | **默认假设节（建模默认值契约）** | 分散：custom_rules.json 规则 18 板类比例/提示词规则 3 语序/适配层默认值 | 🟡 **增强阶段**（触发：下次用户改默认值行为时） | 现状可用但分散三处——集中成一节显式契约文档（docs/NN_默认值契约.md），审计友好。工作量 0.5 天。**吸收原则不吸收实现** |
| 3 | **内容寻址 store + 新鲜度 gate** | catia_experience.db/catia_history.db（经验与历史，无构建缓存） | ⏸️ **增强阶段**（触发：CADDS 出现"改了参数没重建/重建了没生效"类 bug ≥2 次） | 我们的执行是 COM 命令流（每次全量执行），无增量构建场景——**门禁解决的是我们没有的问题**。但"store why 逐子句裁决"的思想可入 error-case：拓扑快照失效时打印逐原因链 |
| 4 | **cadgen doctor 版本门禁** | compatibility.py（CATEnv 探测+能力矩阵+tool_gate）B4 已落地 | ✅ **已满足，关闭** | 我们比它更严（CATIA 版本×COM 能力双维），B4 就是我们的 doctor |
| 5 | **组合=调用 + LINK 子树** | composite 串 mcp 子步骤（语义分解）+ multi-body 积木 | ⏸️ **增强阶段**（触发：装配级项目出现在 roadmap 时） | 单零件场景 JSON 内嵌已够；装配 DAG 增量是 text-to-cad 的主场不是我们的 |
| 6 | **流分离（stdout 结果/stderr 进度）** | GUI 日志面板混流 | 🟡 **增强阶段**（低成本高收益） | 无人消费 stdout（GUI 应用），但**日志分级**（用户可读 vs 诊断）可借鉴——GUI 已有看板，加"诊断流"开关 0.5 天 |
| 7 | **SKILL.md 保守职责边界（"何时不使用"）** | AGENTS.md 有运行约定，无"何时不用 CATDS" | 🟢 **新增主线**（最小动作） | 加"能力边界声明"到 AGENTS.md 顶部：CATDS 管 PartDesign 语义建模，不做 FEA/渲染/刀轨/公差认证——**防用户期望漂移，也防 LLM 越界承诺**。0.5 天，B1-B7 契约层的精神延伸 |
| 8 | step-parts（现货件检索） | 无 | ⏸️ **增强阶段**（触发：用户提"用现成件"需求时） | 飞机设计企业场景有 MC0-MC9/标准件库概念——但当前无此需求信号 |
| 9 | URDF/SRDF/SDF 机器人描述族 | 无关 | ❌ **明确不做** | CATIA 场景与机器人描述文件无交集；那是 DUCK-Pi_5/HoverDuck 生态的事 |
| 10 | G-code/SendCutSend/Bambu 制造链 | 无关 | ❌ **明确不做** | 我们止步于 CAD 几何；CAM 下单/打印在用户工作流外（适航资料场景无此环节） |
| 11 | GLSL SDF 隐式建模（实验性） | 无关 | ❌ **明确不做** | 实验性且与 CATIA B-rep 内核范式冲突 |

## 三、三个最值得吸收的思想（判定之外的增量）

### 3.1 "另一个配置=另一个模型"的参数化哲学

text-to-cad 拒绝参数化模型（模型无参数），把配置变体当作独立文件——**用文件系统管理配置空间**。CATDS 的 modify_feature_parameter（改参非重建）走的是相反路：CATIA 参数化是第一公民。**两者不冲突，但提示我们**：经验库的"模板"（learned_specs）本质就是"配置变体的持久化"——与 cadgen 的"工厂函数+多模型文件"是同构问题的两种解。已满足，但这个视角值得记录。

### 3.2 "环境不是输入"的确定性契约

> "Model and lib/ code takes no parameter from os.environ, the working directory, the current time or a random source."

这是**可复现构建的硬约束**——gate 靠 hash 追踪源，看不见的环境输入会留下"读作 current 的 stale"。CATDS 的 COM 执行天然受环境影响（CATIA 会话状态），我们的对策是拓扑快照失效（B2 verification）。**同一思想两种实现**：它 hash 源码，我们快照拓扑。已满足。

### 3.3 SKILL.md 作为"运行时契约"的写作范本

这个 SKILL.md 是我们见过的**最严格的 agent skill 文档**：默认值契约/职责边界/澄清策略/版本钉住/路径纪律全部显式。我们的 lark-skill-maker/auto-skill 产出的 SKILL.md 与之差距是数量级的——**吸收进 skill 写作标准**：新 skill 评审时对照"有没有默认假设节、有没有何时不用节、有没有版本钉住"。

## 四、批判性审视

1. **13.7k stars 的含金量**：赛道正确（agent skill 化是 2026 主旋律）+ 执行严格（970 commits/CI/CONTRIBUTING/SECURITY 齐备）——但 stars ≠ 生产验证，STEP 质量在复杂航空结构件上的表现未知
2. **build123d/OpenCascade 内核 vs CATIA**：开源 B-rep 内核与 CATIA 的 CGM 内核在容差/缝合/曲面质量上有代差——text-to-cad 的经验不能直接平移到"CATIA 语义建模"的坑（我们的 ZX 草图轴映射坑就是 CATIA 特有）
3. **skill 库 vs 独立应用的分野**：它假设用户有 coding agent（Claude/Codex），我们假设用户是 CATIA 工程师——**用户模型不同，交互范式不可互换**；我们曾评估过的 B7（零依赖 MCP STDIO）已经把"agent 可调用"的桥建好了
4. **cadgen 的复杂度成本**：暖 daemon/并行 worker/内容寻址 store——为 CAD 内核导入 2.5s 的代价做了整套基础设施；CATDS 的 COM 单线程约束下这套并行机制无立足点
5. **GitHub README 的安装陷阱自述**（update 静默漏新 skill/旧版 Codex 静默跳过插件）说明其分发链也有坑——不影响内核评价

## 五、落地决策（待用户拍板，本分析零代码改动）

| 优先级 | 动作 | 工作量 | 触发 |
|--------|------|--------|------|
| **主线（建议做）** | #7 能力边界声明进 AGENTS.md 顶部 | 0.5 天 | 无条件——B1-B7 精神延伸 |
| 增强 | #2 默认值契约文档集中化 | 0.5 天 | 下次改默认值行为时 |
| 增强 | #6 GUI 诊断流分级开关 | 0.5 天 | 低成本高收益，可排期 |
| 增强 | #3 store why 思想 → 拓扑失效逐原因链 | 1 天 | 改参/重建类 bug ≥2 次时 |
| 观察 | #5 装配 DAG / #8 现货件 | — | roadmap 信号 |

**执行原则**：本分析阶段零代码改动（吸收分析零破坏纪律）；拍板后按"决策固化三件套"落地（项目 docs/NN_*.md + git 提交 + 笔记落盘）。

## 六、局限性

1. skills/cad/SKILL.md 精读 17KB，其余 10 个 skill 只读 README 摘要——URDF/G-code 等深度未挖（与 CATDS 判定无关）
2. cadgen 源码（distribution 本体）未读——store/gate 实现质量以 SKILL.md 契约为准
3. CATDS 侧对照基于 AGENTS.md 71KB 与 docs/ 目录结构，未逐文件核对 B1-B7 之外的新增
4. Windows 真机验收（B1-B7）仍在待办——本判定的"已满足"均为设计层关闭非运行时验证
5. text-to-cad 的 STEP 输出质量无独立基准可查（无排行榜）

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一 | **原文忠实还原**（GitHub README + skills/cad/SKILL.md 全文） |
| 二、三 | **对照判定与增量提炼**（本笔记核心，基于 CATDS AGENTS.md 交叉） |
| 四 | **批判性审视**（本笔记扩展） |
| 五 | **落地决策**（待拍板，零代码改动） |
