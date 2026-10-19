# CATIA CAA 开发：Addin — Workbench 与交互式命令完整流程

> 日期: 2026-07-09 | 来源: 嗅探队列 auto-explore | 类型: 技术深化
> 增量来源: maruf.ca CAADoc 镜像（The CAA Command Model + Getting Started with State Dialog Commands 官方用例）

## 摘要

今日聚焦 Addin 开发中此前 skill/笔记**完全缺失**的一环：**如何让 Addin 中的命令在 CATIA 界面上真正可用**（Workbench → Interactive Command → Dialog Engine）。之前笔记已覆盖 RADE/mkmk（06-29）和 .dico 注册（07-03），但"开发完命令后怎么出现在工具栏"这条链路未打通。本次补齐 Command Model 的三种类型、命令树/焦点管理、以及 State Dialog Command 从零实现的完整步骤。

## 关键发现

### 1. CAA 命令的三种类型（命令类型学）

CAA 命令是 `CATCommand` 的派生实例，分三类：

- **One-shot 命令**（直接继承 `CATCommand`）：一次用户交互即跑完，无中间选择，如"导出"按钮。
- **Dialog Box 命令**（继承 `CATDlgDialog`）：弹出参数对话框，OK/Apply/Cancel 模式。
- **State Dialog Command**（继承 `CATStateCommand`）：状态机驱动的交互式命令——最常用也最复杂。每个状态让用户选对象/输参数，满足条件后自动切换状态。官方 Line 命令用例（CAADegGeoCommands.m 模块）即此类。

### 2. 命令树与焦点管理（Command Selector 机制）

运行时刻所有命令构成一棵树，根节点是 `CATCommandSelector`（由 V5 应用创建）。关键机制：

- 每条命令有父命令（`SetFather`），形成树形通知传播结构。
- 同一时刻只有一条**active command**（有焦点），Selector 管理焦点。
- 运行模式三种：Exclusive（排他，清空栈）、Shared（共享，可共存）、Undefined（不进入栈，与 active 并行，state command 不可用此模式）。
- 生命周期三方法：`Activate`（取焦点时）、`Desactivate`（被共享命令覆盖时）、`Cancel`（被排他命令抢占或完成时）。State command 的 `BuildGraph` 不应含命令主体，主体逻辑在状态转换的 Action 中。

### 3. State Dialog Command 完整开发步骤（Line 命令用例）

这是 Addin 中最常用的交互模式，官方给出了完整样板：

**Step 1 — 设计状态机（Statechart）**：用 UML 状态图描述。Line 命令的状态流：`初始态 → [选起点]状态1 → [选终点]状态2 → 终态`，每条转移有 Guard 条件 + Action。

**Step 2 — 声明类**：
```
class CAADegCreateLineCmd : public CATStateCommand {
  CATDeclareClass;
  CmdDeclareResource(CAADegCreateLineCmd, CATStateCommand);  // 声明资源
  virtual void BuildGraph();                                  // 状态机实现入口
  // Guard 方法
  CATBoolean CheckStartPoint(void *); CATBoolean CheckEndPoint(void *);
  // Action 方法
  CATBoolean CreatePoint(void *); CATBoolean CreateLine(void *);
  // 对话框代理
  CATIndicationAgent * _daIndication;   // 鼠标点击检测
};
```

**Step 3 — 管理生命周期**：构造函数中 `CATStateCommand(id, CATCommandModeExclusive)` 声明为排他模式（修改文档的命令必须排他）；实现 `Activate/Desactivate/Cancel`。

**Step 4 — 定义用户输入**：用 `CATIndicationAgent` 检测鼠标点选并返回位置，在 `BuildGraph` 中关联到对应状态。

**Step 5 — 连接状态并提供行为**：`BuildGraph` 中创建状态、转移（触发事件 + Guard + Action）。

**Step 6 — 提供资源文件**：
- `.CATNls`（msgcatalog 目录）：每条命令的 Title/ShortHelp/Help/LongHelp，键名为 `CommandHeader类名.命令ID.Title`
- `.CATRsc`（graphic/icons 目录）：图标映射 `Icon.Normal = "I_EduLine"`

**Step 7 — 集成命令 Header**：创建 `CATCmdHeader` 类（包含命令类名 + DLL 库路径），并做资源注册——这是命令从代码"出现在菜单/工具栏"的关键桥接。

### 4. 与已学内容的衔接（完整 Addin 链路）

```
.
├── mkmk/RADE         ← 06-29 笔记：构建系统、Framework/Module 组织
├── .dico 注册         ← 07-03 笔记：CATImplementClass、TIE 时序、字典格式
├── Command Header    ← 今日：命令注册到菜单/工具栏的桥接
├── State Dialog Cmd  ← 今日：交互式命令的状态机实现
└── Dialog Engine     ← 今日：CATDlgDialog / CATIndicationAgent 交互层
```

## 对工作的价值

- 补齐了 Addin 开发知识栈的**最后一公里**：之前只懂"如何写组件"，现在打通"如何让用户在 CATIA 界面上找到并点击它"。
- 官方 Line 用例是**可直接复用的模板**，后续 CATIA CAA skill 可直接引用此步骤序列。
- Command Selector / 焦点管理是调试"命令响应异常/状态错乱"的核心工具。

## 行动建议

- 将本笔记步骤序列写入 catia-caa skill 的"Addin 交互式命令开发"章节（当前 skill 仅点到类型分类，未展开实现步骤）。
- 下轮可补：Dialog Engine 高级用法（CATDlgDialog 对话框组件、动态 UI 布局），或 CAA 3DEXPERIENCE 迁移注意事项。

## 相关笔记
- [CATIA_CAA开发-V5_V6](./explore/2026-07-07-CATIA_CAA开发-V5_V6.md)
- [CATIA_CAA开发-批量Body处理](./explore/2026-07-04-CATIA_CAA开发-批量Body处理.md)
- [CAA_Command_StateMachine](./explore/2026-06-19-CATIA_CAA_Command_StateMachine.md)
- [CATIA-CAA-开发-Addin](./explore/2026-06-19-CATIA-CAA-开发-Addin.md)
- [CAA-RADE](./explore/2026-06-29-CATIA_CAA开发-CAA-RADE.md)

## 相关笔记

- [CATIA CAA开发-Command工作台 (07-10)](./2026-07-10-CATIA_CAA开发-Command工作台.md) — Command生命周期、多Sheet限制、State Dialog实现
