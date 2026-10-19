# Firefox 告别 asm.js：WebAssembly 完全胜利

> **来源**：Ryan Hunt · SpiderMonkey Blog (Mozilla) · 2026-05-20
> **原文**：https://spidermonkey.dev/blog/2026/05/20/saying-goodbye-to-asmjs.html
> **评分**：⭐4/5
> **标签**：#WebAssembly #asm.js #Firefox #浏览器 #JavaScript #SpiderMonkey

## 摘要

Firefox 148 起，SpiderMonkey 引擎默认禁用 asm.js 优化，计划在未来版本完全移除。asm.js 是 2013 年 Mozilla 提出的"用 JavaScript 子集实现接近原生性能"的方案，为 Unity 和 Unreal 引擎首次登陆 Web 铺平道路。如今 WebAssembly 已完全成功，asm.js 的历史使命完成。引擎内部代号 OdinMonkey 将退役，但其血脉延续在 WebAssembly 优化编译器 BaldrMonkey 中。

## 核心内容

### 1. asm.js 的历史贡献

  2013 年 Firefox 22 首次发布 asm.js 支持
  让 Unity 和 Unreal 的 C/C++ 代码库首次能在浏览器运行
  Epic Citadel 演示仅用 4 天就移植到 Web
  证明了"仅用 Web 技术就能接近原生速度"

### 2. 为什么现在关闭

  WebAssembly 已完全取代 asm.js 的角色
  维护 asm.js 路径消耗开发时间
  asm.js 增加了 VM 的攻击面
  WebAssembly 管线比 asm.js 更先进：更快执行 + 更小二进制

### 3. 平滑过渡

  asm.js 代码不会崩溃——它就是普通 JavaScript，退化为普通 JIT 执行
  建议重新编译为 WebAssembly 获得更好性能
  无破坏性变更

### 4. 诗意命名（北欧神话主题）

  OdinMonkey → 退役（被 Fenrir 狼吞噬）
  BaldrMonkey → WebAssembly 优化编译器（OdinMonkey 的血脉）
  RabaldrMonkey → WebAssembly 基线编译器
  Ragnarök → 追踪 OdinMonkey 退役的 Bug 代号

## 关键概念

  asm.js：JavaScript 的严格类型化子集，引擎可识别并编译为原生代码
  OdinMonkey：SpiderMonkey 的 asm.js 编译器，以 Odin 命名
  WebAssembly：asm.js 的继任者，标准化的二进制指令格式
  BaldrMonkey：OdinMonkey 演化出的 WebAssembly 优化编译器

## 能力边界

  仅影响 Firefox，其他浏览器有各自的 asm.js 实现
  退役是渐进式的：先禁用优化，再完全移除代码
  对已有 asm.js 内容零影响（退化为普通 JS 执行）

## 最佳实践

  仍在使用 asm.js 的项目应迁移到 WebAssembly
  WebAssembly 管线提供更快执行和更小二进制
  迁移成本通常很低（重新编译即可）

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|---|---------|---------------|---------|
| 1 | 技术退役策略 | 先禁用优化→完全移除代码，零破坏性 | Hermes skill 退役应采用渐进策略 | 在 skill-curator-review 中加入渐进退役流程 |
| 2 | 命名传承 | OdinMonkey → BaldrMonkey，血脉延续 | 代码重构时保留历史脉络命名 | 重构核心模块时保留演化记录 |
| 3 | 证明可行性再标准化 | asm.js 证明概念 → WebAssembly 标准化 | 新功能先用 spike 验证再固化 | 强化 spike skill 的验证报告模板 |
| 4 | 攻击面管理 | 移除旧代码减少 VM 攻击面 | 定期清理废弃 skill 和脚本 | 在 auto-dream 中加入废弃代码清理检查 |

## 🔗 RAG / Wiki 联动

### 当前状态
- Wiki 中已有 WebAssembly 相关条目
- 浏览器技术演进历史已有基础覆盖

### 改进方案
1. 在技术退役流程中加入"概念验证→标准化"的演化记录
2. 为 skill 系统设计版本化退役机制

### 已执行操作
- ✅ 笔记已写入


## 相关笔记
- （暂无强关联笔记）
