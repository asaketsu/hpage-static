# CATIA CAA mkmk 编译器 Skill 创建指南

> **来源**: 沃德天衲 / CATIA开发者指南
> **链接**: https://mp.weixin.qq.com/s/pXQrXSDPAA7rD9SkfFXw5g
> **日期**: 2026-05-25
> **关联**: [[2026-05-24-CATIA-CAA命令与工作台接入_bamboo.md]] [[2026-05-21-catia-v6-custom-feature-development.md]]

---

## 摘要

系统讲解如何为 CATIA V5 CAA 二次开发创建面向 mkmk 构建体系的 AI Skill。不是重新实现编译器，而是把 CAA 的 mkmk、Imakefile.mk、IdentityCard、前置框架、运行时视图和常见错误诊断规则封装成可被 AI 编程助手按需加载的领域技能。

---

## 一、mkmk 构建体系核心模型

### 1.1 层级结构

```
Workspace → Framework(s) → Module(s) (*.m)
                ↓                    ↓
          IdentityCard.xml     Imakefile.mk
          (framework prerequisites)  (module build rules)
```

### 1.2 关键文件/命令

| 文件/命令 | 作用 |
|-----------|------|
| `IdentityCard/IdentityCard.xml` | 声明 framework 类型、前置 framework、访问级别 |
| `*.m/Imakefile.mk` | 声明 BUILT_OBJECT_TYPE、LINK_WITH、平台条件 |
| `mkmk` | 四阶段：identity card → 公开头文件列表 → build-time data → 编译链接 |
| `mkGetPreq / mkPrintPreq` | 建立或检查 workspace 对其他 framework 的依赖可见性 |
| `mkCreateRuntimeView` | CNext 资源 → 运行时文件树（CATIA 只认 runtime view） |
| `mkrun` | 在正确环境下执行命令 |
| `mkRemoveDo` | 清理派生对象 |

### 1.3 IdentityCard vs LINK_WITH

这是 CAA 新手最容易混淆的点：

| 维度 | IdentityCard | LINK_WITH |
|------|-------------|-----------|
| 级别 | Framework 级 | Module 级 |
| 作用 | 解决可见性和前置关系 | 解决链接关系 |
| 陷阱 | 头文件能找到 ≠ 链接能过 | 链接库存在 ≠ prerequisite 合理 |

## 二、Skill 设计方法论

### 2.1 触发场景（不应泛化为 C++ 助手）

- 编译 CAA framework/module
- 解释/修复 mkmk 输出错误
- 维护 Imakefile.mk 的 BUILT_OBJECT_TYPE、LINK_WITH
- 维护 IdentityCard prerequisites
- mkGetPreq / mkCreateRuntimeView 操作
- 处理找不到头文件、未解析外部符号、资源未进 runtime view

### 2.2 不应覆盖的范围

- CAA 架构设计 → 独立 skill
- COM 接口设计 → 独立 skill
- Feature Modeler 建模 → 独立 skill
- 命令状态机设计 → 独立 skill（如 catia-caa-command-skill）

### 2.3 推荐目录结构

```
.github/skills/catia-mkmk-compiler/
├── SKILL.md                          # 最小可用版
├── references/
│   ├── mkmk-diagnosis-checklist.md
│   ├── imakefile-patterns.md
│   └── identitycard-prerequisites.md
└── templates/
    ├── Imakefile-shared-library.mk
    └── Imakefile-load-module.mk
```

### 2.4 Frontmatter 关键

```yaml
name: catia-mkmk-compiler
description: "Use when: compiling CATIA V5 CAA C++ projects with mkmk,
  diagnosing Imakefile.mk, IdentityCard prerequisites, mkGetPreq,
  mkPrintPreq, mkCreateRuntimeView, mkrun, LINK_WITH, missing headers,
  unresolved externals, CAA runtime view, RADE build errors."
```

注意：description 必须含真实触发词，不能写太抽象（如"CAA helper"不会被自动命中）。

## 三、构建诊断流程

```
定位当前路径层级 → 找到关键文件 → 读取 mkmk 输出 → 分类故障 → 最小修复
```

故障分类：
- **找不到头文件** → 查 IdentityCard + LINK_WITH
- **未解析外部符号** → 查 LINK_WITH（module 级）
- **找不到 DLL** → 查构建输出 + runtime view + mkrun
- **资源缺失** → 查 CNext/resources + mkCreateRuntimeView
- **build-time data 过期** → `mkmk -u`

## 四、常见坑

| 坑 | 解决方案 |
|----|---------|
| 把 mkmk 当普通 make | mkmk 处理 CAA 特有的 identity card/header list/build-time data/runtime view |
| IdentityCard 改了不刷新 | 重新管理 prerequisites + `mkmk -u` |
| 编译成功但 CATIA 里看不到 | 必须 `mkCreateRuntimeView` + 重启 CATIA |
| 运行中 CATIA 反复卸载/加载 DLL | 改了已加载模块后重启 CATIA（官方 FAQ 明确不建议反复卸载加载） |
| Windows OS 名称混乱（intel_a vs win_b64） | 以 `$MkmkOS_VAR` 或实际生成目录为准 |
| 盲目向 LINK_WITH 追加大量库 | 每个依赖必须可解释"为什么是这个 framework/module" |

## 五、CAA 官方文档位置

```
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlMANMkmk.htm        # mkmk 详解
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlMANMkThemIx.htm    # 周边命令汇总
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlMkHandBook.htm     # 快速参考
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlMkOthers.htm       # mkGetPreq 等
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlMkICEV5.htm        # mkICE 编辑器
CAADoc/Doc/online/CAABtlQuickRefs/CAABtlFAQ.htm            # 常见问题
```

## 六、核心洞察

1. **好的 mkmk skill = 把 CAA 老工程师脑子里的构建图显式写出来**：先看 workspace/framework/module 边界 → 再看 identity card 和 prerequisites → 再看 module 的 Imakefile.mk → 最后才看编译器和链接器命令本身

2. **Skill 的 description 是命中率关键**：必须包含开发者实际会说出的词（mkmk、Imakefile.mk、IdentityCard、LINK_WITH），抽象描述不会被命中

3. **mkmk 不是普通 make**：它有自己的四阶段流程、identity card、runtime view 等约定，不能套用 Makefile/CMake 经验

---

## 借鉴学习进化点

| 档次 | 借鉴点 | 落实动作 |
|------|--------|---------|
| ①有利进化 | mkmk 构建体系完整知识（命令/诊断/坑点/官方文档路径） | ✅ 已patch到 `catia-caa` skill |
| ③知识库 | Skill frontmatter 触发词设计方法论 | 仅笔记（已有 skill-authoring skill 覆盖） |
| ③知识库 | Skill scope 划分原则（不做泛化 C++ 助手） | 仅笔记 |

### 自检三问

1. **可复用方法**: mkmk 诊断流程五步法 + IdentityCard vs LINK_WITH 区分，可直接用于 AERIS-10 项目 CAA 构建问题排查
2. **可优化配置**: catia-caa skill 从"仅提及 mkmk 存在"扩展为完整构建体系章节
3. **关键事实**: "mkmk 不是普通 make"——四阶段流程 + runtime view 是 CATIA 特有的构建约定

---

## ✅ 落实情况

```
📋 借鉴点落实审计
├── ①有利进化 项：1个
│   └── mkmk构建体系 → skill_manage(patch catia-caa) ✅ (20处mkmk内容)
├── ②有价值 项：0个
└── ③知识库 项：2个 → 仅笔记 ✅
```

## 相关笔记
- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md)
- [机器人仿真工具选择指南](2026-05-22-机器人仿真工具选择指南.md)
- [150个任务30个Skill实测-7个反直觉结论](2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [html-ppt-skill分析融合](2026-05-24-html-ppt-skill分析融合.md)
- [html-anything-analysis](explore/2026-05-19-html-anything-analysis.md)
- [the-book-of-secret-knowledge-运维安全工具百科](explore/2026-05-24-the-book-of-secret-knowledge-运维安全工具百科.md)
- [voicebox-flow-matching-next-gen-heavyweight-tts](explore/2026-05-24-voicebox-flow-matching-next-gen-heavyweight-tts.md)

→ 相关：[[2026-06-02-CAA-Mate-VSCode-CATIA-CAA开发插件.md]]
