# CATIA CAA Command 工作台开发 — 学习笔记

> 学习日期：2026-07-10 | 来源：PLM Coach + Eng-Tips + 3DS Community

---

## 摘要

CATIA CAA（Component Application Architecture）是基于 C++ 的原生定制 API，用于在 CATIA V5 / 3DEXPERIENCE 上扩展工作台（Workbench）、命令（Command）和用户界面。本文梳理了 Command 的核心机制、生命周期管理以及在多 Sheet 场景下的已知限制。

---

## 关键发现

### 1. CAA 定制能力对比
- CATIA Knowledgeware：低门槛，但无法扩展 PPR（私有属性集）
- CATIA Automation（VBA）：中等成本，可脚本自动化，依赖 CATIA 许可证
- CATIA CAA 定制：开发成本高，但可完全扩展工作台/PPR，是唯一能做深度定制的路线

### 2. CAA Workspace 结构
- 层次：Workspace → Framework → Module → 源文件
- 两套视图：Build Time（源码 + Imake.mk + IdentityCard XML）与 Run Time（Dico 字典、CATNls、CATRsc 资源文件）
- 依赖管理通过 `mkGetPreq` 定义前置 Workspace，头文件路径 = Workspace + Framework + Module

### 3. Command 生命周期与模式
- Command 通过 `CATStateCommand` 构造函数控制模式：默认独占（Exclusive），可设 shared 模式
- UI-activation（菜单/按钮激活命令）会触发工作台和 Workshop 切换
- **已知限制**：在 Drafting 等工作台，切换 Sheet 时命令 UI 会被终止。这是 CAA 设计行为，无法直接绕过。
- 替代方案：使用 Toolbar + CATIAfrPaletteOptions / CATIAfrPaletteOptions，而非命令模式

### 4. RADE 开发环境
- CAA - C++ Interactive Dashboard (CID) 是 Windows 上的 RADE 环境，支持 UNIX 平台代码自动生成
- 内置 C++ Unit Test Manager 和 CAA Source Checker (CSC)

---

## 对工作的价值

1. 理解 Command 生命周期是定制 CATIA 工作台的根基——尤其在多文档/多 Sheet 场景需特别注意
2. 工作台扩展只能走 CAA 路线，自动化/脚本场景可选 VBA
3. UI-activation 导致的工作台切换行为是常见坑点，提前规划 UI 架构可避免后期返工
4. RADE 环境（CID）支持跨平台编译，适合 UNIX 环境部署

---

## 行动建议

1. 梳理现有需求，判断使用 Command 还是 Toolbar/Palette 方案
2. 建立 CAA Workspace 样板结构（Workspace + Framework + Module）
3. 在多 Sheet 场景优先测试 shared 模式，若仍不满足则考虑 Toolbar 替代
4. 收集更多 CAA Command 实战案例（Dialog Engine、Object Modeler）

## 相关笔记

- [CATIA CAA开发-Addin (07-09)](./2026-07-09-CATIA_CAA开发-Addin.md) — Workbench/Addin注册流程，命令上工具栏的完整链路
