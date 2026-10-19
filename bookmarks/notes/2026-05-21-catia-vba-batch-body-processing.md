# CATIA VBA 批量实体处理：递归删除、同体积筛选、重心创建

来源：微信公众号「键盘造车手」（作者：安亭吴彦祖）
链接：https://mp.weixin.qq.com/s/oP8oqdqsNGrLPJlc-JQEOA
日期：2026-05-21
评分：⭐3.5/5
标签：#CATIA #VBA #CAD自动化 #3D建模 #宏编程 #实体处理

---

## 摘要

一篇 CATIA V5 VBA 宏编程实操文章，解决 STP 导入文件中批量处理零部件实体的问题。核心操作包括递归删除实体树、按体积筛选并删除同类实体、批量创建实体重心参考点。代码结构清晰，通过 Selection 对象统一操作，用递归遍历布尔运算子实体。

## 核心内容

### 解决的问题

STP 文件导入 CATIA 后，常产生大量重复/不需要的实体（小平面片、辅助体、零散零件）。手动逐一删除效率极低，需要批量自动化处理。

### 四个核心操作

**1. 递归删除实体（含子级）**

核心思路：从选中的 Body 出发，递归遍历所有 Boolean Operation 子实体，收集到列表后一次性 Selection.Delete。

关键代码 `recurBD2lst`：
- 递归终止条件：body 无 Shapes 子级
- 遍历 `ibd.Shapes.Item(i).Body`，通过 `TypeName(itm) = "body"` 判断是否为有效子实体
- 所有实体收集到列表后，通过 `Selection.Add` + `Selection.Delete` 批量删除

**2. 按体积筛选删除同类实体**

思路：选中一个参考实体，获取其体积（`meas.Volume * 1e9`，单位转换 mm³），然后遍历所有 Bodies，筛选体积差值 ≤ 0.0003 的实体批量删除。

筛选逻辑 `getpicklst`：
```
对每个 body:
  如果不在 Boolean Operation 中 且 有 Shapes:
    计算体积 (4位小数精度)
    如果 |体积 - 参考体积| ≤ 0.0003 → 加入删除列表
```

精度控制：`Round(value * 1000000000, 4)` + 容差 0.0003，处理 STP 导入的浮点精度问题。

**3. 批量创建重心点**

- `GetBodyCOG`：通过 `KCL.GetMeas(body).GetCOG` 获取重心坐标数组
- `CreatePt`：用 `HybridShapeFactory.AddNewPointCoord(x, y, z)` 创建点
- 所有重心点收集到一个 `HybridBody`（几何集）中，命名为 `cog_bodies`

**4. 实体复制**

直接用 Selection.Copy 批量复制筛选后的实体列表。

### 程序架构

完整的 `delwithBody` 模块通过 UI 控件分发到不同操作：

```
主入口 delwithBody()
├── initVar() — 初始化文档/Part/Selection/HSF/Bodies
├── UI 交互 — 5个按钮分发
│   ├── btn_delrecur → 递归删除
│   ├── btn_delbysel → 同体积删除
│   ├── btn_COG → 创建重心
│   ├── btn_copy → 实体复制
│   └── btncancel → 取消
├── getBdyLst() — 获取所有非布尔运算的实体列表
├── getpicklst() — 按条件筛选实体
├── CreateCOGby() — 批量创建重心点
├── recurBD2lst() — 递归遍历实体树
└── delinlst() — 统一删除接口
```

### 关键技术点

**KCL 公共模块**：文章使用了自定义 KCL 库（非 CATIA 原生），提供：
- `KCL.Initlst` — 初始化列表
- `KCL.GetMeas` — 获取测量对象
- `KCL.SelectItem` — 带类型过滤的交互选择
- `KCL.CatiaFreeze` — 冻结/解冻界面更新（性能优化）
- `KCL.get_workPartDoc` — 获取当前工作 PartDocument
- `KCL.IsNothing` — 空值判断

**Selection 操作模式**：所有增删操作统一通过 `CATIA.ActiveDocument.Selection`：
1. `Selection.Clear` 清空
2. `Selection.Add` 添加目标
3. `Selection.Delete` / `Selection.Copy` 执行操作
4. `Selection.Clear` 收尾

**CatiaFreeze 性能优化**：批量操作前冻结界面更新（`CatiaFreeze True`），操作完成后解冻（`CatiaFreeze False`），避免每次 Add/Delete 触发重绘。

## 关键概念

- **Body**：CATIA 中的实体容器，可包含 Shapes（特征）和子 Body（布尔运算结果）
- **Boolean Operation**：实体的交/并/差运算，产生父子层级关系，需递归遍历
- **HybridBody**：几何元素集（点/线/面），用于组织重心点等参考几何
- **SPAWorkbench**：CATIA 空间分析工作台，提供体积/质量等测量功能
- **InBooleanOperation**：Body 属性，标记是否为布尔运算的结果体

## 能力边界

1. **依赖 KCL 库**：代码无法独立运行，需要作者的 KCL 公共模块
2. **仅处理 Part 级别**：不处理 Product（装配体）级别的跨零件操作
3. **体积筛选精度固定**：容差 0.0003 是硬编码，不同模型尺度可能需要调整
4. **无错误恢复**：删除操作不可逆，没有 undo 机制
5. **STP 特定场景**：针对 STP 导入后的实体结构设计，对原生 CATIA 模型可能需要调整

## 最佳实践

1. **递归遍历实体树**：CATIA 布尔运算产生嵌套 Body 结构，必须递归处理
2. **批量操作前冻结界面**：`CatiaFreeze` 避免大量 UI 刷新，显著提升性能
3. **容差筛选而非精确匹配**：STP 导入的浮点精度问题，用容差（0.0003）代替 `==` 比较
4. **Selection 统一操作模式**：所有增删通过 Selection 对象，代码结构一致
5. **On Error Resume Next 防御式编程**：遍历 Shapes 时部分 Item 可能类型异常，需要静默跳过

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 可迁移思路 |
|---|-----|---------|-----------|
| 1 | 递归遍历树结构 | `recurBD2lst` 递归收集所有子实体 | 任何树形结构（文件系统/AST/Org Chart）的遍历模式相同：递归 + 列表收集 |
| 2 | 容差匹配 | 体积筛选用 0.0003 容差而非精确比较 | 浮点数比较的通用原则：永远不用 `==`，用 `|a-b| < ε` |
| 3 | 批量操作冻结 | `CatiaFreeze` 冻结 UI 提升性能 | 类比批量文件操作时关闭索引/监控，减少不必要的中间状态刷新 |
| 4 | Selection 统一接口 | 所有操作通过 Selection.Add/Delete | 命令模式（Command Pattern）：将操作封装为统一接口，支持批量/队列/撤销扩展 |
| 5 | 防御式编程 | `On Error Resume Next` + `TypeName()` 检查 | 处理异构集合时，先检查类型再操作，避免运行时崩溃 |

## 补充说明

文章已集成到作者的 Macro_menu 程序（CATIA 宏菜单工具），可通过界面操作直接调用，无需手动编写代码。联系方式：verysolecd@hotmail.com


## 相关笔记
- [[catia-automation.md]]
- [[catia_automation.md]]
- [[2026-05-21-catia-v6-custom-feature-development.md]]
- [[2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md]]
