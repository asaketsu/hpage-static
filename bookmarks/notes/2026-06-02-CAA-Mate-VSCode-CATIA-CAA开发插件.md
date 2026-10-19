# CAA Mate：让 VS Code 成为 CATIA CAA 开发的新入口

> 来源：微信公众号「CATIA开发者指南」
> 原文：https://mp.weixin.qq.com/s/Lbun1fdM1v-t6Xz--e8Zmg
> 收录：2026-06-02

## 核心定位

CAA Mate 是面向 CATIA / CAA 二次开发工程的 VS Code 开发辅助插件。**不是替代 Visual Studio 或 RADE**，而是提供一个更轻量、更方便的 CAA 开发入口。

## 已有功能

### 工程识别
- 自动识别 CAA Workspace / Framework / Module 结构
- 识别 `IdentityCard.xml`、`Imakefile.mk`、`CMakeLists.txt`
- 侧边栏树形展示工程结构

### RADE/mkmk 原生命令
- 对 Module 执行 `mkmk`
- 工程根目录 `mkmk -u -nobuild`
- 调用 `mkCreateRuntimeView`
- 编译输出 → Output Channel，可解析错误 → Problems 面板

### CMake 构建路径
- 脱离 RADE 的 CMake 构建流程
- 关键映射规则：

| CAA 概念 | CMake 映射 |
|----------|-----------|
| LOAD MODULE | `add_executable()` |
| SHARED LIBRARY | `add_library(... SHARED)` |
| ARCHIVE | `add_library(... STATIC)` |

- SDK 库目录：`${CAA_INSTALL_PATH}/win_b64/code/lib`
- 默认宏：`_WINDOWS_SOURCE`、`_ALLOW_KEYWORD_MACROS`、`_AFXDLL`
- 许可证处理：排除 `mkCAAV5Licensing.cpp`，使用 `CAA5Licensing_stub.cpp`

### CMakeLists.txt 生成
- 从现有工程自动生成，读取：
  - `Imakefile.mk` / `IdentityCard.xml`
  - `ImportedInterfaces/win_b64/HeaderDir.txt`
  - Module `src` / `LocalGenerated/win_b64`
  - Framework 三级接口目录

### 最小工程骨架创建
- 输入 Project / Framework / Module / 类型 → 生成完整目录结构
- 包含 CMakeLists.txt、IdentityCard、stub 文件、基础 main.cpp

### 错误诊断
- MSVC 编译错误（`fatal error C1083`）
- Linker 错误（`LNK2019`、`LNK1104`）
- CMake 错误/警告
- gcc/clang 格式错误
- 点击跳转源码位置

## 开发计划

1. 完善 RADE/mkmk 命令入口
2. 增强脱离 RADE 的工程创建
3. 沉淀 CMake 构建路径
4. 扩展错误解析覆盖面
5. 补齐测试，发布正式版

## 💡 对我们的价值分析

### ✅ 已在做的
- 我们有 `catia-caa` Skill 覆盖 CAA/RADE 二次开发知识

### ⚠️ 可借鉴的
- **CMake 构建路径**：CAA 传统构建工具链 (`mkmk`) 非常封闭，CAA Mate 展示了一条可行的 CMake 替代路线
- **工程结构识别**：树形展示 + 自动解析 IdentityCard/Imakefile 的模式，可借鉴到其他封闭工程体系
- **错误解析器设计**：多格式统一解析（MSVC + Linker + CMake + gcc/clang）的思路通用

### 🔥 重点行动
- 更新 `catia-caa` Skill：补充 CMake 构建路径、CMakeLists.txt 生成、CAA-to-CMake 映射规则等新知识
- 关注 CAA Mate 发布进度，评估是否集成到 AERIS-10 项目工具链

## 标签

`#CATIA` `#CAA` `#VSCode` `#插件` `#CMake` `#二次开发` `#工程工具`

→ 相关：[[2026-05-25-CATIA-CAA-mkmk编译器Skill创建指南.md]] | [[2026-05-26-CATIA-KnowledgeWare知识工程.md]] | [[2026-05-24-CATIA-CAA命令与工作台接入.md]]

## 相关笔记
- [CATIA-CAA-mkmk编译器Skill创建指南](2026-05-25-CATIA-CAA-mkmk编译器Skill创建指南.md)
