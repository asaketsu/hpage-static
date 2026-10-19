# CATIA Knowledgeware 使用步骤指南

- 📅 2026-05-22
- ⭐ 5/5 — 从零到精通：每个功能都配有完整操作步骤
- 🏷️ #CATIA #Knowledgeware #KWA #KWE #知识工程 #参数化设计 #VBA
- 📰 基于官方文档 + YouTube 实战教程字幕 + 社区经验
- 🔗 视频教程：[Knowledge Advisor 23min](https://www.youtube.com/watch?v=cjusGNCU3SU) · [if-else 规则 17min](https://www.youtube.com/watch?v=NayOmojw9JM) · [Rules 6min](https://www.youtube.com/watch?v=yHAV6kXaOzY)

---

## 一、前置准备：启用参数显示

> ⚠️ **这是新手最常忽略的一步！** 默认情况下 CATIA 不显示参数，导致创建后看不到。

### 操作步骤

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Tools` → `Options` | 打开选项对话框 |
| 2 | `Infrastructure` → `Part Infrastructure` → `Display` | 切换到显示标签页 |
| 3 | 勾选 **Parameters** | 让参数显示在规格树中 |
| 4 | 勾选 **Relations** | 让公式/规则关系显示在规格树中 |
| 5 | 勾选 **Parameters and Relations**（子选项） | 完整显示 |
| 6 | `OK` 确认 | 设置生效 |

**验证：** 打开任意零件，规格树中应出现 `Parameters` 文件夹。

---

## 二、参数（Parameters）— 知识工程的基础

### 2.1 创建用户参数（User Parameter）

**场景：** 用一个参数控制圆孔阵列的数量，而不是每次手动改。

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | 激活 `Knowledge Advisor` 工作台（`Start` → `Mechanical Design` → `Knowledge Advisor`） | 切换工作台 |
| 2 | 点击 `f(x)` **Formula** 工具图标 | 打开公式编辑器 |
| 3 | 点击左下角 **`New Parameter of Type...`** 按钮 | 创建新参数 |
| 4 | 在 `New Parameter` 对话框中： | |
| 4a | `Type` 下拉框选择 **Integer**（整数类型） | 孔数是整数 |
| 4b | `Single Value`（单值模式） | 每个值独立 |
| 5 | 输入参数名：`Number_of_Holes` | 命名建议用英文 |
| 6 | 输入默认值：`5` | 初始值 |
| 7 | `OK` 确认 | 参数创建完成 |

**验证：** 在规格树 `Parameters` 文件夹下看到 `Number_of_Holes`，值为 5。

**关键技巧：**
- 参数类型选择：`Length`（长度）、`Angle`（角度）、`Real`（实数）、`Integer`（整数）、`String`（字符串）、`Boolean`（布尔）、`Feature`（特征引用）
- 整数类型适合计数类参数（孔数、齿数、层数）
- 实数类型适合无量纲数值（安全系数、比例因子）

### 2.2 将参数关联到几何特征

**场景：** 让 `Number_of_Holes` 驱动圆孔阵列的实例数量。

**操作步骤：**

| 步骤 | 操作 |
|------|------|
| 1 | 双击规格树中的 `Circular Pattern`（圆孔阵列特征） |
| 2 | 在对话框中找到 `Instances`（实例数）输入框 |
| 3 | **输入 `=` 然后回车** — 这是关键技巧！ |
| 4 | 在弹出的公式编辑器中，从规格树双击 `Number_of_Holes` 参数 |
| 5 | 公式栏显示：`Number_of_Holes` |
| 6 | `OK` 确认 |

**验证：**
- 修改 `Number_of_Holes` 的值（5→10）
- 点击工具栏 `Update`（刷新图标）或按 `Ctrl+U`
- 圆孔阵列自动更新为 10 个孔

---

## 三、公式（Formulas）— 参数间的数学关系

### 3.1 创建基本公式

**场景：** 板厚 = 内径 × 压力系数 / 材料强度

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Knowledge Advisor` 工作台 → 点击 `f(x)` **Formula** | 打开公式编辑器 |
| 2 | 点击 `New Parameter of Type...` → 选择 `Length` 类型 | 创建目标参数 |
| 3 | 命名：`Wall_Thickness`，默认值 `10mm` | |
| 4 | 在公式编辑器左侧 `Formulas` 列表中，选中 `Wall_Thickness` | |
| 5 | 点击右侧 `Edit Formula` 按钮 | |
| 6 | 在公式输入框中： | |
| 6a | 从规格树双击需要的参数（如 `Inner_Diameter`、`Pressure`） | 参数自动插入 |
| 6b | 输入运算符：`/`、`*`、`-`、`+` | |
| 7 | 公式示例：`(Inner_Diameter * Pressure) / (2 * Allowable_Stress) + Corrosion_Allowance` | |
| 8 | `OK` → `OK` 确认 | |

### 3.2 常用公式函数

| 函数 | 用途 | 示例 |
|------|------|------|
| `sin()`, `cos()`, `tan()` | 三角函数 | `sin(Angle_1)` |
| `sqrt()` | 平方根 | `sqrt(Area)` |
| `abs()` | 绝对值 | `abs(Delta)` |
| `round()`, `floor()`, `ceil()` | 取整 | `round(Length / 10mm)` |
| `min()`, `max()` | 极值 | `min(Dia1, Dia2)` |
| `length()` | 字符串长度 | `length(材料名)` |
| `concat()` | 字符串拼接 | `concat("M", int(Diameter), "-8.8")` |
| `distance()` | 测量距离 | `distance(Point1, Point2)` |
| `area()` | 测量面积 | `area(Sketch1)` |
| `GetVolume()` | 零件体积 | `PartBody.GetVolume()` |
| `GetMinimumThickness()` | 最小壁厚 | `PartBody.GetMinimumThickness()` |

### 3.3 数学表达式示例

```
// 齿轮模数选择
Module = if (Power <= 5kW) { 2 } else if (Power <= 20kW) { 3 } else { 4 }

// 螺栓直径选型
Bolt_Diameter = if (Load > 5000N) { 12mm } else { 8mm }

// 圆孔半径 = 直径的一半
Hole_Radius = Hole_Diameter / 2

// 安装孔间距
Mounting_Spacing = Case_Width - 2 * Margin

// 字符串拼接生成规格号
Specification = concat("M", int(Diameter/mm), "-", Grade)
```

---

## 四、规则（Rules）— 条件-动作逻辑

### 4.1 创建 Rule（手动触发规则）

**场景：** 根据载荷等级自动选择螺栓规格。

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Knowledge Advisor` → 点击 **`Rule`** 工具图标 | 打开规则编辑器 |
| 2 | 输入规则名：`Bolt_Selection_Rule` | |
| 3 | 点击 **`Let`** 按钮声明局部变量 | |
| 4 | 输入：`Bolt_Grade (String)` → `OK` | |
| 5 | 输入 `if` 关键字（或点击 `If` 按钮） | |
| 6 | 从规格树双击参数 `Load_Level` → 输入 `==` → 输入 `"轻载"` | |
| 7 | 在 `Then` 分支： | |
| 7a | 从规格树双击 `Bolt_Grade` → 输入 `=` → 输入 `"4.8"` | |
| 7b | 从规格树双击 `Bolt_Diameter` → 输入 `=` → 输入 `6mm` | |
| 8 | 输入 `else if` → 条件：`Load_Level == "中载"` | |
| 9 | 在 `Then` 分支：`Bolt_Grade = "8.8"`, `Bolt_Diameter = 10mm` | |
| 10 | 输入 `else` → 分支：`Bolt_Grade = "12.9"`, `Bolt_Diameter = 14mm` | |
| 11 | 输入 `EndIf` | |
| 12 | 最后：`Specification = concat("M", int(Bolt_Diameter/mm), "-", Bolt_Grade)` | |
| 13 | `OK` 确认 | |

**完整规则代码：**
```
Rule Bolt_Selection_Rule
  Let Bolt_Grade (String)
  If Load_Level == "轻载"
    Bolt_Grade = "4.8"
    Bolt_Diameter = 6mm
  Else If Load_Level == "中载"
    Bolt_Grade = "8.8"
    Bolt_Diameter = 10mm
  Else
    Bolt_Grade = "12.9"
    Bolt_Diameter = 14mm
  EndIf
  Specification = concat("M", int(Bolt_Diameter/mm), "-", Bolt_Grade)
EndRule
```

**执行规则：**
- 创建后规则不会自动执行
- 需要手动运行：`Knowledge Advisor` → `Update` → 选择规则执行
- 或在 VBA 中调用：`part.Update`

### 4.2 创建 Reaction（反应规则，自动触发）

**场景：** 当板厚被修改时，自动检查弯曲半径是否满足最小要求。

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Knowledge Advisor` → 点击 **`Reaction`** 工具图标 | |
| 2 | 输入名称：`Sheet_Metal_Check` | |
| 3 | 点击 `Let` → 声明：`Min_Bend_Radius (Length)` | |
| 4 | 输入：`Min_Bend_Radius = Sheet_Thickness * 2` | 最小弯曲半径 = 板厚×2 |
| 5 | 输入 `If` → 条件：`Bend_Radius < Min_Bend_Radius` | |
| 6 | 在 `Then` 分支： | |
| 6a | `Message("警告：弯曲半径小于最小值（板厚×2）")` | 弹出提示 |
| 6b | `Bend_Radius = Min_Bend_Radius` | 自动修正 |
| 7 | 输入 `EndIf` | |
| 8 | `OK` 确认 | |

**关键区别：**
- **Rule** = 手动触发，适合复杂逻辑分派
- **Reaction** = 参数变化时自动触发，适合联动更新和自动修正

### 4.3 规则语法速查

| 关键字 | 用途 | 示例 |
|--------|------|------|
| `Rule` | 定义规则 | `Rule 规则名` |
| `Reaction` | 定义反应规则 | `Reaction 反应名` |
| `Let` | 声明局部变量 | `Let 变量名 (类型)` |
| `If` | 条件判断开始 | `If 条件` |
| `Else If` | 多条件分支 | `Else If 条件` |
| `Else` | 默认分支 | `Else` |
| `EndIf` | 条件判断结束 | `EndIf` |
| `Message()` | 弹出消息 | `Message("提示内容")` |
| `concat()` | 字符串拼接 | `concat("M", int(Dia), "-8.8")` |
| `int()` | 转为整数 | `int(Diameter/mm)` |
| `EndRule` | 规则结束 | `EndRule` |
| `EndReaction` | 反应结束 | `EndReaction` |

---

## 五、检查（Checks）— 设计合规性验证

### 5.1 创建 Check

**场景：** 检查壁厚是否满足最小要求。

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Knowledge Advisor` → 点击 **`Check`** 工具图标 | |
| 2 | 输入名称：`Min_Wall_Thickness_Check` | |
| 3 | 在 `Condition` 行：输入 `Min_Thickness >= 2mm` | |
| 4 | 在 `Message` 行：输入 `"壁厚不足2mm，可能影响结构强度"` | |
| 5 | 在 `Severity` 行：选择 **2**（错误级别） | 0=信息, 1=警告, 2=错误 |
| 6 | `OK` 确认 | |

**完整 Check 代码：**
```
Check Min_Wall_Thickness_Check
  Condition = Min_Thickness >= 2mm
  Message("壁厚不足2mm，可能影响结构强度")
  Severity = 2
EndCheck
```

### 5.2 Check 严重级别

| Severity | 颜色 | 含义 | 典型用途 |
|----------|------|------|---------|
| 0 | 🔵 蓝色 | 信息（Info） | 提示性消息 |
| 1 | 🟡 黄色 | 警告（Warning） | 建议关注但不阻断 |
| 2 | 🔴 红色 | 错误（Error） | 严重违规，必须修复 |

### 5.3 生成诊断报告

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Knowledge Advisor` → `Generate Report` | |
| 2 | 选择报告格式：HTML 或 TXT | |
| 3 | 选择输出目录 | |
| 4 | `OK` 生成 | |

**报告内容示例：**
```
┌──────────────────────────┬──────┬──────────────────────────┐
│ 检查名称                 │ 状态 │ 消息                     │
├──────────────────────────┼──────┼──────────────────────────┤
│ Min_Wall_Thickness_Check │ ❌   │ 壁厚不足2mm...           │
│ Material_Compliance      │ ✅   │ AL6061-T6 合规           │
│ Draft_Angle_Check        │ ⚠️   │ 建议≥3°拔模              │
└──────────────────────────┴──────┴──────────────────────────┘
```

---

## 六、设计表（Design Tables）— Excel 驱动系列化设计

### 6.1 准备 Excel 表格

**Excel 表格结构（法兰系列）：**

| 参数名 | DN50 | DN80 | DN100 | DN150 |
|--------|------|------|-------|-------|
| DN | 50 | 80 | 100 | 150 |
| Outer_Diameter | 165 | 200 | 235 | 300 |
| Bolt_Hole_Count | 4 | 8 | 8 | 12 |
| Bolt_Hole_Diameter | 18 | 18 | 22 | 22 |
| Thickness | 20 | 24 | 26 | 30 |
| Seal_Diameter | 102 | 133 | 158 | 208 |

> ⚠️ **第一行必须是参数名**，与 CATIA 中的参数名完全一致（区分大小写）。

### 6.2 导入设计表

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Insert` → `Knowledge` → `Design Table` | 打开设计表对话框 |
| 2 | 选择 `From Excel File` 选项 | |
| 3 | 浏览并选择 Excel 文件 | |
| 4 | 在 `Associations` 标签页中，将 Excel 列映射到 CATIA 参数 | |
| 4a | 点击 `Add` → 选择 Excel 列 → 选择 CATIA 参数 | 逐一关联 |
| 5 | 勾选 `Activate` 启用设计表 | |
| 6 | `OK` 确认 | |

### 6.3 切换设计变体

| 步骤 | 操作 |
|------|------|
| 1 | 双击规格树中的 `Design Table` 节点 |
| 2 | 在对话框中选择要激活的行（如 DN100） |
| 3 | `OK` 确认 |
| 4 | 点击 `Update`（刷新） |

**高级用法：**
- **过滤条件：** 在 `Filter` 行输入 `(DN >= 50) and (DN <= 200)` 只加载符合条件的行
- **VBA 自动切换：** 遍历所有行自动生成所有变体
- **嵌套设计表：** 主表控制大类，子表控制子类

---

## 七、目录（Catalogs）— 可重用零件库

### 7.1 创建目录文件

**CATCatalogFile.catalog 格式：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Catalog>
  <Chapter Name="紧固件">
    <Family Name="螺栓">
      <Component Name="M6x20" File="bolt_M6x20.CATPart"/>
      <Component Name="M8x30" File="bolt_M8x30.CATPart"/>
      <Component Name="M10x40" File="bolt_M10x40.CATPart"/>
    </Family>
    <Family Name="螺母">
      <Component Name="M6" File="nut_M6.CATPart"/>
      <Component Name="M8" File="nut_M8.CATPart"/>
    </Family>
  </Chapter>
  <Chapter Name="轴承">
    <Family Name="深沟球轴承">
      <Component Name="6000" File="bearing_6000.CATPart"/>
    </Family>
  </Chapter>
</Catalog>
```

### 7.2 使用目录

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | `Tools` → `Options` → `General` → `Parameters and Measures` → `Catalogs` | |
| 2 | 点击 `Add` → 选择 `.catalog` 文件 | |
| 3 | 在装配体中：`Insert` → `Existing Component` → 选择目录 | |
| 4 | 浏览目录层级 → 选择零件 → 插入 | |

---

## 八、Power Copy — 可参数化复用特征组

### 8.1 创建 Power Copy

**场景：** 将"通孔 + 沉孔 + 倒角"打包为一个可复用模板。

**操作步骤：**

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | 在零件中创建完整的特征组（孔、沉孔、倒角） | 先做好原型 |
| 2 | 在规格树中选中所有相关特征（按住 Ctrl 多选） | |
| 3 | `Insert` → `Knowledge` → `Power Copy` | |
| 4 | 输入名称：`Counterbore_Hole_Template` | |
| 5 | **定义输入参考（Input References）：** | |
| 5a | 点击 `Input References` 标签 | |
| 5b | 选择需要用户指定的几何元素（如放置面、中心点） | 这些是插入时需要指定的 |
| 6 | **定义发布参数（Published Parameters）：** | |
| 6a | 点击 `Published Parameters` 标签 | |
| 6b | 勾选允许用户修改的参数（如孔径、深度、倒角角度） | 内部逻辑隐藏 |
| 7 | `OK` 确认 | |
| 8 | 保存到目录或单独文件 | |

### 8.2 使用 Power Copy

| 步骤 | 操作 |
|------|------|
| 1 | 在目标零件中：`Insert` → `Power Copy` → 选择模板文件 | |
| 2 | 根据提示指定输入参考（选择放置面、中心点等） | |
| 3 | 在对话框中修改发布参数 | |
| 4 | `OK` 确认 → 特征组自动生成 | |

---

## 九、User Feature（UDF）— 黑盒特征封装

### 9.1 与 Power Copy 的区别

| 特性 | Power Copy | User Feature |
|------|-----------|--------------|
| 内部可见性 | 完全可见 | 🔒 黑盒封装 |
| 参数暴露 | 全部可见 | 选择性暴露 |
| 编辑方式 | 编辑原始特征 | 仅修改暴露参数 |
| 保护性 | 无 | 内部逻辑受保护 |
| 适合场景 | 标准特征复制 | 专有设计封装 |

### 9.2 创建 UDF

| 步骤 | 菜单路径 | 操作 |
|------|---------|------|
| 1 | 设计并测试原始特征 | 确保功能正确 |
| 2 | `Insert` → `Knowledge` → `User Feature` | |
| 3 | 选中所有相关特征 | |
| 4 | 输入名称：`Heat_Sink_Array` | |
| 5 | **定义输入（Inputs）：** 参考几何（安装面、边界） | |
| 6 | **定义输出（Outputs）：** 结果几何 | |
| 7 | **定义发布参数（Publications）：** 齿数、齿高、齿间距 | |
| 8 | `OK` 确认 → 保存为 `.CATPart` | |

---

## 十、列表和循环（Lists & Loops）

### 10.1 列表操作

```
// 创建列表
Let myList (List)
myList = List(1, 2, 3, 4, 5)

// 列表操作
myList.Append(6)        // 添加元素
myList.Remove(2)        // 移除索引2的元素
myList.Size()           // 获取大小
myList.GetItem(3)       // 按索引获取
```

### 10.2 For 循环

```
// 创建等角度分布的孔
For i From 1 To Hole_Count
  Let angle (Angle)
  angle = 360deg / Hole_Count * (i - 1)
  // 在此角度处创建孔特征
EndFor
```

### 10.3 While 循环

```
Let count (Integer)
count = 0
While count < Max_Iterations
  count = count + 1
  // 迭代计算
EndWhile
```

---

## 十一、Knowledge Expert（KWE）— 企业级规则引擎

### 11.1 Rule Base 与 Rule Set 结构

```
Rule Base: 企业设计规范
├── Rule Set: 材料规范
│   ├── Rule: 材料选择规则
│   ├── Check: 材料合规检查
│   └── Rule Set: 有色金属子集    ← 可嵌套
│       └── Rule: 铝合金选型
├── Rule Set: 尺寸规范
│   └── Rule: 最小壁厚
└── Rule Set: 工艺规范
```

### 11.2 关键概念

| 概念 | 说明 |
|------|------|
| **Rule Base** | 顶层容器，一个 Part 可有多个 Rule Base |
| **Rule Set** | 逻辑分组（类似代码中的 package），可嵌套 |
| **Rule** | 产生式规则（If-Then），**可修改**参数值 |
| **Check** | 约束检查（布尔表达式 + 诊断），**不能**修改参数 |

### 11.3 求解模式

| 模式 | 执行逻辑 | 适用场景 |
|------|---------|---------|
| **Sequential**（顺序） | 从上到下逐条执行 | 规则间无冲突 |
| **Conflict Resolution**（冲突消解） | 优先级高的覆盖低的 | 多条规则影响同一参数 |
| **Propagation**（传播） | 变化沿依赖链传播 | 参数联动、级联更新 |

### 11.4 扩展语法

```
Rule 专家规则名
  Priority = 10          // 优先级（越高越先执行）
  NoLoop                 // 防止循环触发（必加！）
  
  Let 材料 (String)
  Let 应力 (Real)
  
  If PartBody\材料参数 == "Q235"
    if 屈服应力 > 235MPa
      PartBody\安全系数 = 1.5
    endif
  EndIf
EndRule
```

> ⚠️ **NoLoop 关键字**：修改参数的 Rule 必须加 `NoLoop`，否则可能导致 CATIA 无限循环甚至崩溃。

---

## 十二、VBA 自动化知识工程

### 12.1 创建参数的 VBA 代码

```vba
' 创建长度参数
Set partDoc = CATIA.ActiveDocument
Set partObj = partDoc.Part
Set parameters = partObj.Parameters

' 创建长度参数
Set paramLength = parameters.CreateLength("壁厚", 10)
paramLength.Value = 12

' 创建字符串参数
Set paramMaterial = parameters.CreateString("材料", "AL6061-T6")

' 创建整数参数
Set paramCount = parameters.CreateInteger("孔数", 4)
```

### 12.2 创建公式的 VBA 代码

```vba
' 创建公式：壁厚 = (压力 × 内径) / (2 × 许用应力)
Set formula = partObj.Formulas
formula.CreateFormula "壁厚公式", "壁厚", _
    "(Pressure * Inner_Diameter) / (2 * Allowable_Stress)", _
    Array("Pressure", "Inner_Diameter", "Allowable_Stress")
```

### 12.3 执行规则的 VBA 代码

```vba
' 执行所有规则
partObj.Update

' 执行特定规则（通过 Knowledge Advisor 接口）
Set kwe = partObj.KnowledgeExpert
Set ruleBase = kwe.RuleBases.Item("企业设计规范")
ruleBase.Update
```

---

## 十三、完整实战案例：螺栓选型系统

### 13.1 参数定义

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `Load` | Length | 3000mm | 载荷（用长度单位表示力） |
| `Load_Level` | String | "轻载" | 载荷等级 |
| `Bolt_Diameter` | Length | 6mm | 螺栓直径 |
| `Bolt_Grade` | String | "4.8" | 螺栓强度等级 |
| `Specification` | String | "M6-4.8" | 完整规格 |

### 13.2 规则代码

```
Rule Bolt_Selection_Rule
  Let Bolt_Grade (String)
  If Load_Level == "轻载"
    Bolt_Grade = "4.8"
    Bolt_Diameter = 6mm
  Else If Load_Level == "中载"
    Bolt_Grade = "8.8"
    Bolt_Diameter = 10mm
  Else
    Bolt_Grade = "12.9"
    Bolt_Diameter = 14mm
  EndIf
  Specification = concat("M", int(Bolt_Diameter/mm), "-", Bolt_Grade)
EndRule
```

### 13.3 检查代码

```
Check Bolt_Strength_Check
  Condition = (Bolt_Grade == "4.8" AND Load <= 3000N) OR _
              (Bolt_Grade == "8.8" AND Load <= 8000N) OR _
              (Bolt_Grade == "12.9" AND Load <= 15000N)
  Message("螺栓强度等级与载荷不匹配")
  Severity = 2
EndCheck
```

### 13.4 使用流程

1. 打开零件 → 设置 `Load_Level` 为 "中载"
2. `Knowledge Advisor` → `Update` → 执行 `Bolt_Selection_Rule`
3. 查看 `Specification` = "M10-8.8"
4. `Generate Report` → 检查 `Bolt_Strength_Check` 状态
5. 如需修改，直接改 `Load_Level` → 重新 Update

---

## 十四、常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 参数创建后看不到 | 参数显示未启用 | Tools → Options → Infrastructure → Display → 勾选 Parameters |
| 公式报错 "Invalid expression" | 参数名含空格或特殊字符 | 参数名用下划线替代空格，如 `Bolt_Diameter` |
| 规则执行后参数不变 | 规则未添加到 Update 队列 | 确保规则在 Knowledge Advisor 树中，执行 Update |
| 修改参数后模型不更新 | 公式未关联 | 双击特征 → 在输入框输入 `=` → 选择参数 |
| 设计表导入失败 | Excel 参数名与 CATIA 不一致 | 确保首行参数名完全一致（区分大小写） |
| Rule 导致 CATIA 崩溃 | 循环触发 | 添加 `NoLoop` 关键字 |
| Reaction 不自动触发 | 参数不在 Reaction 监听范围内 | 确保 Reaction 引用的参数已正确声明 |

---

## 十五、学习路径建议

| 阶段 | 目标 | 预计时间 |
|------|------|---------|
| **入门** | 掌握参数 + 公式 + 基本 Rule | 1-2 天 |
| **进阶** | 掌握 Check + Design Table + Power Copy | 3-5 天 |
| **高级** | 掌握 KWE Rule Base + UDF + 列表循环 | 1-2 周 |
| **专家** | VBA 自动化 + CAA API + 企业级 Rule Base | 1-3 月 |

---

## 参考资料

1. Dassault Systèmes — CATIA Knowledge Advisor (KWA) 官方文档
2. Dassault Systèmes — CATIA Knowledge Expert (KWE) 官方文档
3. [Knowledge Advisor 23min 教程](https://www.youtube.com/watch?v=cjusGNCU3SU) — CMU PDET
4. [if-else 规则 17min 教程](https://www.youtube.com/watch?v=NayOmojw9JM) — Nader Zamani
5. [Rules 6min 教程](https://www.youtube.com/watch?v=yHAV6kXaOzY) — CATIA Tutorials
6. [Check command 教程](https://www.youtube.com/watch?v=wrkz0Msblo0) — alina
7. CATIA CAA Encyclopedia — Knowledge Interfaces
8. [3DEXPERIENCE CATIA R2026x — AI-Driven Generative Experiences](https://www.3ds.com/products-services/catia/products/knowledgeware/)

## 相关笔记
- [CATIA知识工程深度研究](explore/2026-05-22-CATIA知识工程深度研究.md)
- [catia_automation](catia_automation.md)
