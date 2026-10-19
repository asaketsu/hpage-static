# CATIA CAA 开发：Addin（工具栏/命令注册插件）

> 来源：CATIA CAA 官方文档 CAADoc 镜像（maruf.ca）+ 实战博客（sunjw.us、CSDN）+ 本地 `catia-caa` 技能库
> 日期：2026-06-19 | 类型：auto-explore

## 摘要

Addin 是 CATIA CAA 的**插件扩展机制**：通过实现 Workbench/Workshop 暴露的 add-in 接口，向已有工作台注入自定义工具栏和命令，而**无需修改工作台本身代码**。这是 CAA 二次开发三层架构（Addin → Command → Dialog）的最上层入口，决定"命令按钮出现在哪里"。

## 相关笔记

- [CATIA-CAA命令与工作台接入](../2026-05-24-CATIA-CAA命令与工作台接入.md) (关键词: CATIA, CAA, Workbench, Addin)
- [CATIA V5 CAA 零件设计接口全指南](../2026-06-18-CATIA-V5-CAA-零件设计接口全指南.md) (关键词: CAA, 接口, 零件设计)
- [CATIA CAA 开发: CAA-RAD](./2026-06-19-CATIA_CAA开发:-CAA-RAD.md) (关键词: CAA, RAD, 开发环境)
- [CATIA CAA Command StateMachine](./2026-06-19-CATIA_CAA_Command_StateMachine.md) (关键词: CAA, Command, Addin)

## 关键发现

**1. Addin 的本质——解耦扩展点**

官方定义：*"An add-in gathers commands to customize a workshop or a workbench without needing to modify the workshop or workbench's code. You simply need to implement the interface that the workshop or workbench exposes for add-ins."*

核心价值：插件式解耦。Addin 作为独立的 Component 编译成 DLL，通过 TIE 接口粘合到目标工作台，实现热插拔式功能扩展。

**2. 接口体系——Addin 统一派生自 CATIWorkbenchAddin**

- 所有 add-in 接口**派生自 `CATIWorkbenchAddin`**，对 Workshop 和 Workbench 通用
- 具体工作台暴露自己的 add-in 接口（如 `CATIAfrGeneralWksAddin`、`CATIPstWksAddin`）
- Addin 类继承 `CATBaseAddin` 并通过 TIE 粘合实现上述接口
- 必须宏绑定：`CATImplementBOA()` + `CATImplementClass()` + `TIE_CATICmdContainer()`，否则工具栏不注册

**3. 两个核心方法——CreateCommands + CreateToolbars**

Addin 类必须实现这两个方法：

- `CreateCommands()` —— 创建工具栏所需的全部命令头（Command Header）
- `CreateToolbars()` —— 创建工具栏容器并挂载命令头

命令头定义两种方式：
- `MacDeclareHeader` 宏（标准方式，声明式）
- 手动定义命令头类（需要 ENOVIA LCA 集成等特殊场景时使用）

**4. 两种实现路径**

- **标准 Addin 方式**：用 CAA 向导创建 Addin Component，在 TIE adhesion 处选择目标工作台的接口（如 `CATIAfrGeneralWksAddin`），然后实现 `CreateCommands()`/`CreateToolbars()`。推荐，插件化、可复用。
- **直接 Workbench 方式**：不建 Addin，直接在 Workbench 的 `Headers.h` 和 `Workshop.h` 中编写。适合一次性定制，丧失解耦优势。

**5. 常用工作台 Addin 接口对照**

- `CATIAfrGeneralWksAddin` —— 通用工作台
- `CATIPstWksAddin` —— Product Structure 工作台（注意：实现此接口可让工具栏在**所有 Product 工作台**生效，复用范围更大）
- 工作台标识符：`CATPrtBase`(Part Design)、`CATAssembly`(Assembly)、`CATDrw`(Drafting)、`CATSkc`(Sketcher)

**6. 工具栏注册代码模式**

```cpp
void MyAddin::CreateToolbars() {
    NewAccess(CATCmdContainer, pToolbar, "MyToolbar");
    NewAccess(CATCmdHeader, pCmdHeader, "MyCmdHeader");
    SetAccessCommand(pCmdHeader, "MyCommand");   // 绑定命令实现类
    AddAccessCommand(pToolbar, pCmdHeader);
    AddToolbarView("MyToolbar", 1, CATCmdContextRight);
}
```

## 对工作的价值

- **StructGen / AI-CATIA-KBE 项目落地**：要让自己的参数化设计命令出现在 CATIA 菜单栏，Addin 是唯一正规入口。掌握 CreateCommands/CreateToolbars 即掌握"功能可见化"的最后一公里。
- **插件化复用**：选择 `CATIPstWksAddin` 等工作台级接口，一次注册多工作台生效，避免为每个工作台重复开发。
- **解耦维护**：Addin 独立编译，CATIA 升级时工作台代码不变，只需重编译 Addin DLL，降低维护耦合。

## 行动建议

1. **固化模板**：将"标准 Addin 向导流程 + CreateCommands/CreateToolbars 骨架"沉淀到 `catia-caa` 技能的脚手架模板，下次新建项目直接套用。
2. **接口选择决策树**：在 StructGen 中明确——通用功能选 `CATIAfrGeneralWksAddin`，装配相关选 `CATIPstWksAddin`，零件建模选 Part Design 对应接口。
3. **坑点复查**：上线前确认三项——BOA 接口绑定、Command 设 `CATCommandModeExclusive`、构建后执行 `mkCreateRuntimeView`，否则 CATIA 中看不到工具栏。

## 参考资料

- CAADoc: Creating an Add-in (CAAAfrSampleAddin) — maruf.ca/files/caadoc/CAAAfrUseCases/CAAAfrSampleAddin.htm
- CAADoc: Adding a Toolbar to all Product Workbenches (CAAPuiPRDWorkshopAddin)
- Interface CATIWorkbenchAddin — q-solid.com CATIA Doc refman
- 太阳日志: Catia CAA Addin 正确的建立方法 — sunjw.us/blog/catia-caa-addin/
- 本地技能：`software-development/catia-caa`（含完整接口表、Command 状态机四步法、mkmk 构建）
