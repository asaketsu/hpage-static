# CATIA CAA 开发：Addin 深度补强

> 日期: 2026-07-03 | 来源: 嗅探队列 auto-explore | 类型: 技术深化
> 增量来源: maruf.ca 官方 CAAAfrGeoOperationAdn use case（CAADoc 镜像）

## 摘要

本次学习聚焦 CATIA CAA/RADE 的 **Addin（插件注册）层**，针对已有 catia-caa skill 中的薄弱点做精准补强。核心收获是三个此前 skill 中只点到未讲透的机制：**CATImplementClass 四参数精确语义**、**.dico 字典文件格式与主类名铁律**、**TIE 宏的实例化时序**。这三点恰好是工具栏"注册了却看不见"这一最高频坑的根因链。

## 关键发现

### 1. CATImplementClass 四参数语义（此前 skill 缺失）

官方 use case 明确了每个参数含义，消除了"照抄模板但不知所以然"：

```
CATImplementClass(CAAAfrGeoOperationAdn,  // 1. 扩展类名
                  DataExtension,          // 2. 扩展类型（Addin 用 DataExtension）
                  CATBaseUnknown,         // 3. 必须 CATBaseUnknown 或 CATNull（任何 extension 都如此）
                  CAAAfrGeoOperationAddin); // 4. late type name，绝不能与现有 C++ 类名/latetype 重复
```

- 参数 3 是"反直觉硬规则"：写 extension 时第三参不能是真实基类，只能是 CATBaseUnknown/CATNull。
- 参数 4 的唯一性是潜在崩溃源——与现有 latetype 撞名会引发难以定位的加载失败。

### 2. .dico 字典文件格式（关键增量）

字典文件位于 `CNext/code/dictionary/`，运行时由 `CATDictionaryPath` 环境变量拼接定位。格式为**单行三列**：

```
CAAAfrGeoOperationAddin  CAAIAfrGeoCreationWkbAddin  libCAAAfrGeoCreationWkbAddin
```

两条铁律：
- **第一列必须用组件主类名，绝不能用扩展类名**。这是最常见的注册失败原因——开发者填了 `CAAAfrGeoOperationAdn`（扩展类）而非 `CAAAfrGeoOperationAddin`（主类）。
- **第三列库名是包含 TIE 宏代码的库**。通常 TIE 宏写在扩展类源文件中，所以 TIE 库 = 实现库。当客户端请求接口时，框架先实例化 TIE 类，由它检索或创建扩展实例。

### 3. TIE 实例化时序（解释"为什么 TIE 库 = 实现库"）

```
Client QueryInterface(IXxx) 
  → 框架查 .dico 定位 TIE 类所在库
  → 实例化 TIE 类
  → TIE 类查找已有的扩展实例（复用）
  → 若无 → TIE 实例化扩展类
  → 返回接口指针给 Client
```

这解释了 skill 坑点诊断树里"TIE 粘合无效 → .dico 字典文件未注册"——字典错则整条链断裂，工具栏无法加载。

### 4. MacDeclareHeader 自动生成机制

`MacDeclareHeader(CAAAfrGeoOperationAdnHeader)` 一行宏完成三件事：
- 自动生成 Header 类的 .h 和 .cpp 文件（无需手写）
- 自动绑定资源文件 `CAAAfrGeoOperationAdnHeader.CATNls` 和 `.CATRsc`
- 命令头是命令的"商务名片"：工作台显示时只加载 Header（省内存），点击时才懒加载命令本体

### 5. Addin 创建四步法（官方标准化流程）

1. 创建 Addin 描述类（LocalInterfaces + src，继承 CATBaseUnknown + TIE 目标接口）
2. CreateCommands() 声明命令头（new XxxHeader(...)）
3. CreateToolbars() 编排工具栏/菜单布局
4. 提供资源文件（.CATNls + .CATRsc）

### 6. 文件清单（Addin 模块标准结构）

- `LocalInterfaces/XxxAdn.h` — 描述类头
- `src/XxxAdn.cpp` — 描述类实现（含 CATImplementClass + TIE + CreateCommands + CreateToolbars）
- `CNext/code/dictionary/Xxx.edu.dico` — 接口字典
- `CNext/resources/msgcatalog/XxxAdn.CATNls` — Addin 消息文件
- `CNext/resources/msgcatalog/XxxAdnHeader.CATNls/.CATRsc` — 命令头资源

## 对工作的价值

- **直接强化 catia-caa skill**：本次发现的 .dico 格式和 CATImplementClass 四参数语义，正好填补 skill 坑点诊断树中"确认格式正确"这句悬空指令——现在有精确格式可对照。
- **降低调试成本**：工具栏不显示时，.dico 主类名 vs 扩展类名混淆是高频根因，有了铁律可直接排查。
- **支撑后续项目**：struct-gen-agent 等 CATIA 相关项目若要做 CAA 插件集成，可直接复用这套补强后的模板。

## 行动建议

1. **已完成**：将 .dico 字典格式、CATImplementClass 四参数语义 patch 回 catia-caa skill（坑点诊断树 + Addin 注册章节）。
2. **后续**：当 struct-gen-agent 需要把选型结果做成 CATIA 原生工具栏时，以本次补强模板为骨架。
3. **注意**：CATIA CAA/RADE 为 Windows-only，本机 Linux/Jetson 无法编译验证，所有代码需在 Windows + RADE 环境测试。

## 参考来源

- maruf.ca CAADoc 镜像 — CAAAfrGeoOperationAdn use case（Dassault 官方文档镜像）
- 本地 catia-caa skill（references/addin-official-usecase.md 已含该 use case 代码，本次补强的是字典/参数语义）

## 相关笔记

- [[2026-07-02-CATIA_CAA开发-Addin]] — 前一篇 Addin 三层架构与 CreateCommands/CreateToolbars 详解，本篇是其增量补强
- [[2026-06-28-CATIA_CAA开发-Addin]] — 同系列早期笔记，Addin 注册机制基础
- [[2026-06-27-CATIA_CAA开发-Addin]] — 同系列，Addin 接口与工作台集成
- [[2026-07-02-CATIA_CAA开发-V5_V6]] — CATIA V5/V6 架构差异，Addin 在 V5 中的定位


## 相关笔记

- [CATIA CAA Addin 插件机制(基础)](./2026-07-02-CATIA_CAA开发-Addin.md) — 三层分离架构：Addin→Command→Dialog
- [CATIA CAA Addin 深度补强](./2026-07-03-CATIA_CAA开发-Addin.md) — CATImplementClass/.dico/TIE 宏时序
- [CATIA V5 vs V6 命名澄清](./2026-07-04-CATIA_CAA开发-V5_V6.md) — 3DX平台化差异
- [批量Body处理 CAA增量](./2026-07-04-CATIA_CAA开发-批量Body处理.md) — Automation API对照视角
- [批量Body Automation侧](./2026-07-05-CATIA_CAA开发-批量Body处理.md) — pycatia/VBScript/C#路径
- [批量Body CAA侧](./2026-07-06-CATIA_CAA开发-批量Body处理.md) — CATIPartRequest遍历+工厂模式
- [CATIA CAA V5/V6 深度笔记](./2026-07-07-CATIA_CAA开发-V5_V6.md) — RADE环境+三层开发体系
