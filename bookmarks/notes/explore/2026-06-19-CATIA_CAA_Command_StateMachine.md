# CATIA CAA 开发：Command 工作台与状态机机制深度解析

> 学习日期：2026-06-19 | 来源：达索官方 CAADoc（CAADegGraph / CAADegGettingStarted）+ catia-caa Skill 实践沉淀
> 主题：CATStateCommand 状态机命令开发

## 一、摘要

CATIA CAA 的交互命令核心是 **CATStateCommand 状态机模型**：把"用户交互流程"建模为一组**状态（State）+ 迁移（Transition）+ 对话代理（Dialog Agent）**，在 `BuildGraph()` 方法中声明式构建。命令由 **Addin 注册工具栏头（CmdHeader）触发**，通过 **Dialog 对话框**提供表单输入，三者构成 Addin→Command→Dialog 三层架构。Command 层负责捕获鼠标点击/选择/键盘输入并驱动业务逻辑，是 CAA 二次开发交互功能的"发动机"。

## 二、关键发现

### 1. 状态机三要素在 BuildGraph 中声明

状态机的全部逻辑集中在重写的 `BuildGraph()` 方法里，按固定顺序构建：

- **状态（State）**：`CATDialogState` 实例，承载用户输入窗口
  - 初始状态：`GetInitialState("id")` — 自动激活，永不显式创建
  - 中间状态：`AddDialogState("id")`
  - 终止状态：`AddTransition(..., NULL, ...)` 中用 `NULL` 表示
  - 取消状态：`GetCancelState()` — 命令被打断时进入
- **对话代理（Dialog Agent）**：把用户交互翻译成输入信号，用 `AddDialogAgent()` 插到状态上
- **迁移（Transition）**：`AddTransition(源状态, 目标状态, 条件, 动作)`

### 2. 四类核心 Dialog Agent

| Agent 类型 | 用途 | 取值方式 |
|-----------|------|---------|
| `CATIndicationAgent` | 捕获鼠标点击坐标（2D/3D） | `GetValue()` 返回 `CATMathPoint2D` |
| `CATPathElementAgent` | 选择已有对象（面/边/特征） | 可 `AddElementType()` 限定类型 |
| `CATDialogAgent` | 通用通知（右键、快捷键） | `AcceptOnNotify()` 监听 |
| `CATPathElementAgent`（多选） | 批量选择 | `SetBehavior(CATDlgEngMultiAcquisition)` |

关键设置：
- `CATIndicationAgent::SetMathPlane(Plane)` — 为 3D 取点设定投影平面
- `CATPathElementAgent::AddElementType(ClassId())` — 限定可选对象类型
- `AddCSOClient(agent)` — 让 Agent 响应当前选择集（CSO）
- `SetBehavior(CATDlgEngWithPSOHSO)` — 高亮预选/当前选择对象

### 3. Transition 的条件与动作（声明式编程）

迁移不是 if-else，而是**声明式条件链**，用工厂函数包装：

```cpp
AddTransition(
    stStart, stEnd,
    AndCondition(
        IsOutputSetCondition(_daAgent),          // Agent 有输出
        Condition((ConditionMethod)&Cmd::Check)  // 自定义守卫
    ),
    Action((ActionMethod)&Cmd::DoSomething)      // 迁移时执行
);
```

- **条件工厂**：`Condition()`、`IsOutputSetCondition()`、`IsLastModifiedAgentCondition()`、`AndCondition()`/`OrCondition()`
- **守卫方法**返回 `CATBoolean`，签名为 `CATBoolean CheckXxx(void* iUsefulData)`
- **动作方法**签名同为 `CATBoolean DoXxx(void* iUsefulData)`
- **同源多迁移顺序敏感**：`AddTransition` 的书写顺序决定优先级匹配，先写更具体的条件

### 4. AcquisitionFilter — 输入预过滤

在 Agent 上挂过滤器，提前剔除非法输入，提升交互体验：

```cpp
CATAcquisitionFilter* pFilter = Filter(
    (FilterMethod)&Cmd::TestCtrlPoint, NULL);
_PointAgent->SetFilter(pFilter);
```

### 5. 命令生命周期四回调

| 回调 | 触发时机 | 典型用途 |
|------|---------|---------|
| 构造函数 | 创建命令 | 设 `CATCommandModeExclusive`（独占模式） |
| `Activate` | 命令获得焦点 | 初始化数据（多数用默认即可） |
| `Desactivate` | 被其他共享命令抢占 | 暂存状态 |
| `Cancel` | 命令结束或被独占命令打断 | 清理：删除已创建的临时几何、Release 对象 |

`Cancel` 返回 `CATStatusChangeRCCompleted` 表示清理完成。

### 6. 与 Addin / Dialog 的衔接

- **Addin**：在 `CreateToolbars()` 中用 `NewAccess` 建工具栏，`SetAccessCommand(header, "CmdClass")` 绑定命令，必须 `CATImplementBOA` + `TIE_CATICmdContainer`
- **Dialog**：`CATDlgDialog` 派生，用 `CATDlgEditor`/`CATDlgLabel` 布局；命令可通过对话框事件触发状态迁移
- **资源文件**：`.CATNls` 定义 Title/Help/ShortHelp，`.CATRsc` 定义图标和 Category

## 三、对工作的价值

1. **ai-catia-kbe 项目直接可用**：项目里需要实现交互式特征创建命令（如参数化选型），状态机模型是标准范式，避免用低层 API 硬编码交互逻辑
2. **结构化封装现有 Skill**：本次补充了 catia-caa Skill 中 Command 层较薄弱的状态机细节（Agent 类型、Transition 工厂函数、生命周期回调），形成可复用的开发模板
3. **降低调试成本**：掌握"同源多迁移顺序敏感""Agent 必须 RequestDelayedDestruction""必须 Exclusive 模式"等坑点，可避免大量反复重启 CATIA 的调试周期

## 四、行动建议

1. **P1 — 补强 catia-caa Skill**：将本次 Command 状态机完整模板（BuildGraph 四步法 + Agent 类型表 + Transition 工厂函数）写入 Skill 的 Command 章节，当前仅有简略骨架
2. **P2 — 生成可运行脚手架**：基于状态机模型产出一份"取两点画线"最小示例的完整代码骨架（.h/.cpp/CATNls/CATRsc），作为 ai-catia-kbe 项目交互命令的起点
3. **P2 — 建立 Transition 调试清单**：把"迁移不触发""命令不自动销毁""Agent 取不到值"等常见故障的排查步骤固化为排查脚本

---

*笔记自动归档 — MeowBot 嗅探队列学习系统*

## 相关笔记
- [CATIA 知识工程深度研究](2026-05-22-CATIA知识工程深度研究.md) (关键词: CATIA, 知识工程, 参数化)
- [CATIA Knowledgeware 使用步骤指南](2026-05-22-CATIAKnowledgeware使用步骤指南.md) (关键词: CATIA, Knowledgeware, 规则)
- [CATIA V6 自定义特征开发](../2026-05-21-catia-v6-custom-feature-development.md) (关键词: CATIA, CAA, 二次开发)
- [开源 3D 设计 AI: OpenSCAD+LLM](2026-06-12-开源3D_设计AI-OpenSCAD+LLM.md) (关键词: CAD, 参数化建模, LLM)
