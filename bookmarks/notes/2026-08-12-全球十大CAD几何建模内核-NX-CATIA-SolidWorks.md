# 全球十大 CAD 几何建模内核：NX/CATIA/SolidWorks 背后的技术世界

> 来源：微信公众号文章
> URL: https://mp.weixin.qq.com/s/qV_hB1RZI1GivIrTvVKrKQ
> 主题：CAD 几何建模内核（Geometric Modeling Kernel）全景解析
> 评分：⭐⭐⭐⭐⭐ (5/5) — CAD 底层技术最系统性的中文综述，从 B-Rep 到行业格局

## 核心结论

**CAD 软件本身不负责"算几何"——真正把三维模型算出来的是隐藏在底层的几何建模内核。** 全球有无数 CAD 软件，但真正具有工业级影响力的几何内核只有不到十套。看懂内核，就看懂了 CAD 最难被替代的技术基础。

## 什么是几何建模内核？

### CAD 软件的分层结构

```
CAD 软件（用户界面 / 特征树 / 参数化）
    ↓
几何建模内核（几何计算引擎）  ← 本文的主角
    ↓
B-Rep 数据模型（点/边/面/体/拓扑）
```

### B-Rep（Boundary Representation，边界表示）

现代机械 CAD 的核心数据模型——一个实体不是保存为"很多三角形"，而是由具有数学精度的几何元素逐层构成：

```
Vertex → Edge → Wire → Face → Shell → Solid
```

**这是精确 CAD 模型与普通三角网格模型的本质区别。**

## 十大几何建模内核

### 第一梯队：广泛授权的商业内核

| 内核 | 归属 | 使用的 CAD 软件 | 特点 |
|------|------|----------------|------|
| **① Parasolid** | Siemens | NX, Solid Edge, **SolidWorks**, **Onshape** | 生态最大——不仅服务自家，还被大量第三方采用。近年扩展到 Mesh/Lattice/混合建模 |
| **② ACIS** | Dassault/Spatial | 大量 CAD/CAE/CAM | 与 Parasolid 并立数十年的老牌内核。**Autodesk ShapeManager 的技术祖先** |

### 第二梯队：大型 CAD 厂商自研内核

| 内核 | 归属 | 对应 CAD | 特点 |
|------|------|----------|------|
| **③ CGM** | Dassault | **CATIA**, 3DEXPERIENCE | 处理航空航天级复杂曲面/高阶 NURBS/极端 Boolean 稳定性 |
| **④ Granite** | PTC | **Creo** (原 Pro/E) | 强调 CAD 数据互操作，几何属性+模型结构一体化 |
| **⑤ ShapeManager** | Autodesk | **Inventor, Fusion 360** | 从 ACIS 演化而来，Autodesk 逐渐发展出自有体系 |

### 第三梯队：独立商业技术

| 内核 | 归属 | 特点 |
|------|------|------|
| **⑥ C3D Modeler** | C3D Labs (ASCON) | 从 KOMPAS-3D 内部走出的独立 SDK。含 Modeler + Solver(约束求解) + Converter |
| **⑦ Kubotek Kosmos** | Kubotek | 新一代内核，重视多线程/多核/云架构/现代部署 |
| **⑧ SMLib** | — | 强调 NURBS 和**非流形建模**（Non-Manifold），服务 CAE/几何分析 |

### 第四梯队：开源基础设施

| 内核 | 归属 | 特点 |
|------|------|------|
| **⑨ Open CASCADE (OCCT)** | 开源 (LGPL) | **开源 CAD 世界最重要的基础设施**。FreeCAD 的核心。大幅降低开发专业三维软件的门槛 |

### 历史祖先

| 内核 | 时代 | 意义 |
|------|------|------|
| **⑩ Romulus** | 1970s-80s | 现代几何内核的重要祖先。Shape Data → Parasolid → Siemens 体系 |

## 技术血缘图谱

```
早期计算几何研究
    │
  Romulus (1970s)
    │
  Shape Data
    │
  Parasolid ──────────────────────────┐
    │                                  │
  Siemens 体系                         │
    ├── NX                             │
    ├── Solid Edge                     │ 这些都用 Parasolid
    ├── SolidWorks ─────────────┐      │
    ├── Onshape                 │      │
    └── 第三方 CAD              │      │
                                │      │
ACIS ───────────────────────────┤      │
    │                           │      │
  Spatial (Dassault)           │      │
    ├── 大量第三方 CAD          │      │
    └── Autodesk ShapeManager ──┤      │
         ├── Inventor           │      │
         └── Fusion 360         │      │
                                │      │
CGM (Dassault 自研) ────────────┤      │
    ├── CATIA                   │      │
    └── 3DEXPERIENCE            │      │
                                       │
Granite (PTC 自研) ─────────────────────┘
    └── Creo (Pro/ENGINEER)

Open CASCADE (开源) ── FreeCAD, SALOME
```

## 为什么同一内核，CAD 软件却不同？

**核心洞察**：CAD 数据 = 几何结果 + 设计语义

| 数据层 | 内容 | 由谁负责 |
|--------|------|----------|
| **几何结果** | B-Rep 中的点/边/曲线/面/实体/拓扑 | 几何内核 |
| **设计语义** | 特征树/参数/表达式/装配约束/PMI/材料属性/历史顺序 | CAD 软件自身 |

> **所以：Parasolid 几何 ≠ NX 原生数据 ≠ SolidWorks 原生数据 ≠ Onshape 原生数据**
>
> 从 CAD A 导出 Parasolid `.x_t` → 导入 CAD B → **几何完整，但 Feature Tree 没了**。因为传过去的是"最终几何结果"而非"完整设计过程"。

## 为什么开发 CAD 内核这么难？

一个 Boolean 看似简单（A+B / A-B / A∩B），实际实现需要处理：

| 问题 | 说明 |
|------|------|
| 曲面求交 | 复杂 NURBS 曲面的精确交线求解 |
| 拓扑重构 | Boolean 后的面/边/点重新组合 |
| 容差（Tolerance） | 两条"理论重合"的边可能差 0.000001——算相交？相切？重合？独立？ |
| 极小边/退化面 | Boolean 产生的微观几何垃圾 |
| 数值误差 | 浮点精度 vs 工程精度 |
| 脏数据 | 现实世界的工业模型充满不完美数据 |

> **一个 Boolean 算法"能跑"不难。难的是：几十年里面对无数种工程模型和极端几何条件，依然能够稳定地跑。** 这就是成熟商业内核经过几十年积累后最难被复制的壁垒。

## 行业四大阵营

| 阵营 | 代表 | 特点 |
|------|------|------|
| **广泛授权的商业内核** | Parasolid, ACIS | 服务自己的同时大量第三方授权 |
| **厂商自研技术体系** | CGM, Granite, ShapeManager | 与自家 CAD 深度绑定 |
| **独立商业技术** | C3D, Kubotek, SMLib | 巨头之外的独立生态 |
| **开源技术** | Open CASCADE | 降低开发门槛的基础设施 |

## 未来趋势：内核竞争的新阶段

### 从单一 B-Rep 到混合几何

现代工程数据不再只有 B-Rep：

| 传统 | 新增 |
|------|------|
| 解析曲面、NURBS | 三角网格、扫描数据、点云 |
| 封闭实体 | Voxel、Implicit Geometry、Lattice（点阵） |
| 减材制造 | 拓扑优化结果、增材制造结构 |

**新问题**：B-Rep 怎么与 Mesh 共存？精确几何怎么与离散几何融合？

### 从桌面到云端

| 维度 | 过去 | 未来 |
|------|------|------|
| 运行环境 | 高性能 Windows 工作站 | 浏览器、云计算、移动设备、WebAssembly |
| 计算架构 | 单线程 | 多线程、多核、分布式、GPU |
| 竞争焦点 | "谁的 Boolean 更稳定" | "谁能更好地适应现代计算架构 + AI" |

## 💡 分析与借鉴

### 对航空结构设计/CATIA 的意义

| 内核 | 与用户研究的关系 |
|------|-----------------|
| **CGM (CATIA)** | 航空复杂曲面/高阶 NURBS/百万级 Boolean 稳定性——这是 CATIA 在航空航天占统治地位的底层原因 |
| **Parasolid (NX)** | 与 CATIA 并列航空两大主力，技术血缘不同 |
| **Open CASCADE** | 如果要做 CAD 二次开发或原型验证，OCCT 是零成本入门的唯一选择 |

### 关键认知

1. **CAD 数据交换的真相**：`.x_t` / `.step` 只传几何结果，设计语义丢失。这是跨 CAD 协作的根本痛点
2. **内核是 10 年+ 壁垒**：不是算法问题而是工程积累——几十年的极端 case 处理经验不可速成
3. **AI CAD 的底层挑战**：AI 生成 CAD 模型最终也要落到 B-Rep + 设计语义两层，内核层无法绕过

## 关联

- → 相关：2026-04-27-垂域LLM指导航空结构设计.md
- → 相关：2026-06-18-PTC-Cloude-Onshape-AI-生成工程级CAD模型深度解析.md（项目 catia-caa）
- → 相关：text-to-cad-自然语言驱动参数化CAD深度分析.md

## 相关笔记
- [text-to-cad开源CAD技能集](2026-05-20-text-to-cad开源CAD技能集.md)
- [text-to-cad-自然语言驱动参数化CAD深度分析](2026-05-14-text-to-cad-自然语言驱动参数化CAD深度分析.md)
- [AI+CAD五大方向全景分析](2026-06-24-AI+CAD五大方向全景分析.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [WHUCAD-全球首个CAD工业软件智能核心开源项目](2026-07-24-WHUCAD-全球首个CAD工业软件智能核心开源项目.md)
