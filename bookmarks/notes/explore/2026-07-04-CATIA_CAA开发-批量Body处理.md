# CATIA CAA 开发：批量 Body 处理（增量补充）

> 来源：auto-explore 学习 · 2026-07-04
> 关联：本主题已于 2026-06-20 完整学习（见 `2026-06-20-CATIA_CAA开发-批量Body处理.md`），核心 API 链、七大坑点、黄金法则均已整合进 `catia-caa` skill。本轮为增量补充，聚焦 Automation API 对照视角。

## 摘要

批量 Body 处理的 CAA（C++）方案已在前期笔记中完备。本轮调研发现，同一需求存在 **Automation API（VBScript/pycatia）** 的替代路径，二者在架构选择上互补。本文补充跨技术栈对比与 VBScript 侧的实战代码模式。

## 关键发现：CAA vs Automation 双路径对照

| 维度 | CAA（C++，前期已覆盖） | Automation API（VBScript/pycatia，本轮补充） |
|------|----------------------|---------------------------------------------|
| 遍历入口 | `CATIPartRequest::GetOrderedBodies()` | `part.Bodies` / `part.HybridBodies` 集合 |
| Body 类型鉴别 | `CATIBody` / `CATIMmiGeometricalSet` 接口探测 | `.Type` 属性或 `TypeOf(name)` |
| 布尔运算 | `CATIPrtBooleanFactory::CreateAdd()` | `part.ShapeFactory.AddNewAdd()` |
| 批量导出独立 Part | DocSession + Clone + SaveAs | Selection.Copy → 新 Part Selection.Paste |
| Update 粒度 | 批量后单次 `CATIPrtPart::Update()` | 批量后单次 `part.Update()` |
| 适用场景 | 工作台集成插件、深度定制 | 脚本/宏、跨进程批处理、无 RADE 环境 |

## VBScript 侧实战模式：1 Body = 1 CATPart 拆分

> 来源：eng-tips 论坛 cilici 的解决方案

```vb
' 选择性 Body 处理（非全部，用户选哪些处理哪些）
Dim myBodies as Collection
Set myBodies = new Collection
for i = 1 to myPartDocument.Selection.Count
    myBodies.add myPartDocument.Selection.Item(i).Value
next
myPartDocument.Selection.Clear

for each myBody in myBodies
    Activdocu.Selection.Clear
    Activdocu.Selection.Add myBody
    Activdocu.Selection.Copy     ' 复制选中 Body
    Activdocu.Selection.Clear
    ' 新建 Part → 粘贴 → 保存 → 关闭
    Dim PartNeu As Product
    Set PartNeu = ProductNeu.products.AddNewComponent("Part", CStr(myBody.Name))
next
```

**核心思路**：用 Selection 对象做 copy-paste 中转，绕开 CAA 的 Clone API。无需 RADE 编译，CATIA 直接跑宏即可。

## Hybrid Body 分离处理

VBScript 宏实战中，普通 Body 和 Hybrid Body 必须分开处理：

- `part.Bodies` — 实体 Body 集合
- `part.HybridBodies` — 几何图形集（GS）集合
- 二者 API 方法不同，混用会报错

这与 CAA 侧用 `GetSolidBodies()`（仅实体）vs `GetOrderedBodies()`（含 GS）的区分逻辑一致。

## Body 名称清洗技巧

VBScript 宏中发现的名称处理经验：

```vb
' CATIA Body 名称可能含特殊字符（反斜杠等），需清洗后再做文件名
KoerperName = Replace(KoerperName, "\", "_")
If Right(KoerperName, 1) = "\" Then
    KoerperName = Left(KoerperName, Len(KoerperName) - 1)
End If
```

适用于 Body → 独立文件导出时的文件名生成场景。

## 对工作的价值

- **技术栈选型依据**：批量 Body 拆分为独立 Part 的需求，若无需深度定制，Automation 宏比 CAA 插件成本低一个数量级（无需 RADE 环境、无需编译）
- **现有项目复用**：`~/uclaw/project/catia-automation/`（pycatia 封装）可直接实现上述 VBScript 逻辑的 Python 版本，比 VBScript 更易维护
- **补充对照表**：catia-caa skill 已有 CAA 完整方案，本轮补充 Automation 对照，覆盖用户混淆两种技术栈的场景

## 行动建议

1. catia-caa skill 的选型决策表（CAA vs Automation）已较完善，无需改动
2. 若后续有"多 Body 拆分装配"的实际需求，优先评估 catia-automation 项目能否用 pycatia 实现，避免新建 CAA 工程
3. 本轮为重复主题的增量补充，建议 sniff-auto 脚本对"已学习且已整合进 skill"的主题做去重

## 结论

批量 Body 处理主题已充分覆盖。CAA 侧（C++）方案完整，Automation 侧（VBScript/pycatia）方案作为低门槛替代路径已补充。两路径核心逻辑一致：遍历 → 操作 → 单次 Update；差异在 API 入口和执行环境。

## 相关笔记

- [[2026-06-20-CATIA_CAA开发-批量Body处理]] — 同主题首篇笔记，CAA 完整方案与七大坑点
- [[2026-07-02-CATIA_CAA开发-V5_V6]] — CAA V5/V6 架构与 RADE 工具链
- [[2026-07-01-CATIA_CAA开发-V5_V6]] — CAA 开发 V5/V6 深度探索前序笔记
- [[2026-06-30-CATIA_CAA开发-CAA-RADE]] — CAA RADE 开发环境与构建流程
- [[2026-06-26-CATIA_CAA开发-V5_V6]] — CAA V5/V6 平台迁移与对比


## 相关笔记

- [CATIA CAA Addin 插件机制(基础)](./2026-07-02-CATIA_CAA开发-Addin.md) — 三层分离架构：Addin→Command→Dialog
- [CATIA CAA Addin 深度补强](./2026-07-03-CATIA_CAA开发-Addin.md) — CATImplementClass/.dico/TIE 宏时序
- [CATIA V5 vs V6 命名澄清](./2026-07-04-CATIA_CAA开发-V5_V6.md) — 3DX平台化差异
- [批量Body处理 CAA增量](./2026-07-04-CATIA_CAA开发-批量Body处理.md) — Automation API对照视角
- [批量Body Automation侧](./2026-07-05-CATIA_CAA开发-批量Body处理.md) — pycatia/VBScript/C#路径
- [批量Body CAA侧](./2026-07-06-CATIA_CAA开发-批量Body处理.md) — CATIPartRequest遍历+工厂模式
- [CATIA CAA V5/V6 深度笔记](./2026-07-07-CATIA_CAA开发-V5_V6.md) — RADE环境+三层开发体系

## 相关笔记

- [CATIA CAA V5/V6 深度笔记](./2026-07-07-CATIA_CAA开发-V5_V6.md) — V5/V6 架构与 API
- [CATIA 批量 Body 处理（7/6）](./2026-07-06-CATIA_CAA开发-批量Body处理.md) — 批量 Body 处理实战
- [CATIA 批量 Body 处理（7/5）](./2026-07-05-CATIA_CAA开发-批量Body处理.md) — Automation API 多语言

## 相关笔记

- [CATIA 批量 Body 处理 Automation](./2026-07-05-CATIA_CAA开发-批量Body处理.md) — Automation API 多语言实战
- [CATIA 批量 Body 处理 核心版](./2026-07-06-CATIA_CAA开发-批量Body处理.md) — 接口文档与黄金法则
- [CATIA CAA开发 V5/V6](./2026-07-08-CATIA_CAA开发-V5_V6.md) — CAA 开发框架全景

## 相关笔记

- [CATIA CAA 开发：批量 Body 处理](./2026-07-06-CATIA_CAA开发-批量Body处理.md) — CAA C++ 完整版
- [CATIA 批量 Body 处理：Automation API 多语言实战](./2026-07-05-CATIA_CAA开发-批量Body处理.md) — Automation API 实战
- [CATIA CAA 开发 V5/V6](./2026-07-07-CATIA_CAA开发-V5_V6.md) — V5/V6 架构全景
