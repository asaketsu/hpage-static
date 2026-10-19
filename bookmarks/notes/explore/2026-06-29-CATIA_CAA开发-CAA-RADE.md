# CATIA CAA 开发：CAA RADE 深度学习

> 2026-06-29 | auto-explore | 知识来源：内部 catia-caa skill（Tavily/maruf.ca 镜像本日均 432 不可用，已降级）

## 摘要

RADE（Rapid Application Development Environment）是达索 CATIA V5 二次开发 CAA 框架的**官方集成开发环境层**。它不是独立 IDE，而是构建在 Visual Studio 之上的定制工具集，由四大支柱组成：mkmk 构建系统、Framework/Module/Interface 工程组织约定、代码向导（CAA Wizard）、运行时视图（Runtime View）管理。理解 RADE 的关键是认清它**重新定义了"构建"这一动作**——mkmk 处理 identity card、公开头文件列表生成、build-time data 更新、运行时资源复制四件普通 make/CMake 不会做的事。

## 关键发现

### 一、RADE 的本质：构建约定 + 环境，而非语言

- CAA（Component Application Architecture）是**架构**（组件、接口、扩展的编程范式）
- RADE 是**开发环境**（在 Windows + VS 之上，提供工程骨架、构建器、向导、运行时视图）
- 两者关系：CAA 程序用 RADE 提供的工具链来组织、编译、部署；脱离 RADE（如纯 CMake）虽可行，但需自行复刻其约定

### 二、mkmk 构建系统的四个关键阶段（RADE 核心）

mkmk 不是普通 make，每次构建按固定顺序完成四件事：

1. 编译 framework 的 IdentityCard（声明 framework 类型、前置依赖、访问级别）
2. 生成 framework 对外公开的头文件列表（PublicInterfaces 暴露范围）
3. 检查并更新模块 Imakefile.mk 对应的 build-time data
4. 执行真正的编译与链接（共享库分阶段处理库间链接关系）

常用命令：
- `mkmk` — 编译当前模块；`mkmk -a` — 编译所有相关目标
- `mkmk -u` — prerequisite 变更后刷新 build-time data（最高频救命命令）
- `mkCreateRuntimeView` — 把 CNext 资源复制到运行时文件树（**CATIA 运行时只认 runtime view**，改资源后必跑）
- `mkrun <cmd>` — 在正确的 PATH/library path/CAA 环境变量下执行命令
- `mkPrintPreq -l -f <Framework>` — 查看 framework 直接和间接 prerequisites

### 三、工程组织的核心概念（RADE 视角）

- **Framework**：最大组织单元，含 IdentityCard 声明前置依赖
- **Module（.m）**：框架内的可编译单元，含 Imakefile.mk（声明 BUILT_OBJECT_TYPE、LINK_WITH）
- **三层 Interface 目录**：PublicInterfaces（对外暴露）/ ProtectedInterfaces / PrivateInterfaces
- **CNext/**：资源目录（.CATNls 字符串、.CATRsc 资源、图标），构建后复制进 runtime view

**易混淆点**：IdentityCard 解决的是 **framework 级可见性与前置关系**；Imakefile.mk 的 LINK_WITH 解决的是 **module 级链接关系**。两者级别不同，不能互相替代——"头文件能找到"不等于"链接能过"。

### 四、CMake 替代构建路径（脱离 RADE 的可行方案）

CAA Mate 插件验证了用 CMake 替代 mkmk 的方案，适合 CI/CD 与自动化：
- CAA 概念映射：LOAD MODULE→add_executable，SHARED LIBRARY→add_library(SHARED)，ARCHIVE→add_library(STATIC)
- 必须定义：`-D_WINDOWS_SOURCE -D_ALLOW_KEYWORD_MACROS -D_AFXDLL`
- 许可证处理：排除 mkCAAV5Licensing.cpp，用 CAA5Licensing_stub.cpp 替代
- 默认补充 CATSysTS 库（覆盖 CATString 等基础类型链接）

### 五、最高频故障模式（RADE 诊断）

- **编译过了但 CATIA 里看不到工具栏** → 最常见，忘跑 `mkCreateRuntimeView` + 重启 CATIA
- **找不到头文件** → IdentityCard 未声明前置 Framework，需 `AddPrereqComponent` + `mkmk -u`
- **链接报未解析符号** → Imakefile.mk 的 LINK_WITH 缺库
- **在运行中的 CATIA 反复卸载/加载 DLL** → 不可预测崩溃，改了已加载模块后必须重启 CATIA

## 对工作的价值

1. **软著材料准备**（项目署名麻子淳）：理解 RADE 工程结构可正确拆分源代码文档，按 Framework/Module 组织符合版权保护中心审查要求
2. **模板生产**：RADE 的工程骨架（IdentityCard + Imakefile.mk + 三层 Interface + CNext 资源）是生成 CAA 项目脚手架的标准范式
3. **故障定位能力**：掌握 mkmk 四阶段 + IdentityCard vs LINK_WITH 区分，可系统性定位"编译过/运行不见"这类新人最高频踩坑

## 行动建议

- **本机不执行**：CATIA V5 CAA/RADE 是 Windows-only，当前 Linux/Jetson 主机无法编译运行，仅作模板与架构指导用途
- **Windows + RADE 环境准备**：真正开发前需安装 RADE 工具集 + 配置 workspace，IdentityCard 前置框架管理是首要工作
- **CI/CD 前景**：若需脱离 RADE 做自动化构建，评估 CAA Mate 的 CMake 生成路径，先在 stub 许可证下空跑验证

## 参考

- 内部 skill：software-development/catia-caa（含 mkmk 体系、工程结构、CMake 路径、故障决策树完整章节）
- 达索官方 CAADoc 镜像（maruf.ca/files/caadoc/，本日 Tavily 432 不可用，待恢复后可抓取 CAABtlMANMkmk.htm / CAABtlFAQ.htm 补充）

## 相关笔记

- [CATIA CAA 开发 CAA-RADE（06-30）](2026-06-30-CATIA_CAA开发-CAA-RADE.md)
- [CATIA CAA 开发 Addin（06-28）](2026-06-28-CATIA_CAA开发-Addin.md)
- [CATIA CAA 开发 V5_V6（06-26）](2026-06-26-CATIA_CAA开发-V5_V6.md)
- [CATIA CAA Command StateMachine](2026-06-19-CATIA_CAA_Command_StateMachine.md)
