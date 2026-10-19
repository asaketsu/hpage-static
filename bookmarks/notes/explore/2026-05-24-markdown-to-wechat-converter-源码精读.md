# markdown-to-wechat-converter 源码精读

- 📅 2026-05-24
- ⭐ 3.5/5 — 功能完整的浏览器端微信排版工具，架构清晰但无模块化
- 🏷️ #微信排版 #前端工具 #Markdown #开源分析
- 📰 GitHub
- 🔗 https://github.com/LizabethLi/markdown-to-wechat-converter

## 摘要

markdown-to-wechat-converter 是一个纯前端、零依赖的 Markdown 转微信公众号排版工具。核心能力包括：基于 marked.js 的自定义渲染器、hljs 语法高亮内联化（抵抗微信 CSS 清理）、MathJax 公式渲染、Mermaid 流程图 SVG 内联计算、可插拔模板系统、OpenRouter 翻译集成、多渠道输出（WeChat/Substack/GitHub）。

## 核心架构

```
index.html（单页应用，无构建工具）
├── config.js           → 全局配置（7套主题色 + 语法高亮配色 + 翻译设置）
├── template-manager.js → 插件式模板注册表（register/setActive/list/getStyles）
├── wechat-styles.js    → 默认样式函数集（compact/standard双模式）
├── templates/          → 5套可插拔模板（default/minimal/magazine/notebook/winter）
├── math-renderer.js    → MathJax：占位符保护 → SVG渲染 → 微信SVG优化
├── markdown-converter.js → 核心渲染管线
│   ├── marked.js 自定义renderer（heading/paragraph/code/table/blockquote等）
│   ├── hljs高亮 → DOM遍历 → computedStyle内联（抗微信CSS清理）
│   ├── Mermaid：异步render → DOMParser解析 → 逐属性内联 → 移除<style>标签
│   └── [lead] 段落标记 → 主题色背景块
├── translator.js       → OpenRouter/代理翻译（MATHBLOCK/CODEBLOCK占位符保护）
├── channel-converter.js → 多渠道（Substack HTML双语 / GitHub Markdown双语）
└── ui-controller.js    → UI交互 + localStorage持久化
```

## 技术亮点

### 1. hljs→内联样式策略（抗微信CSS清理）

微信编辑器会清除 `<style>` 标签和 CSS class。该项目的解决方案：

1. hljs 高亮后，HTML 中只有 class（如 `hljs-keyword`）
2. 创建临时 DOM 容器，解析高亮 HTML
3. 遍历所有元素，对每个 class 查预定义的颜色映射
4. 将颜色写入 `style` 属性（内联）
5. 最终输出只含 inline style，不依赖 class 或 `<style>`

关键代码在 `applyInlineSyntaxStyles()` 中，约 60 行，涵盖 keyword/string/comment/number/function/variable 等 20+ hljs class。

### 2. Mermaid SVG 内联计算

Mermaid 渲染出的 SVG 依赖 `<style>` 标签中的 CSS 规则，微信粘贴后会丢失。解决方案：

1. `mermaid.render()` 生成 SVG
2. DOMParser 解析 SVG
3. 创建隐藏 scratch div，挂载到 document.body
4. `getComputedStyle()` 获取每个元素的 27 种视觉属性
5. 将 computed style 写入 element.style
6. 移除所有 `<style>` 节点
7. 调整 SVG 根元素为 `max-width:100%; height:auto`

约 180 行代码（`prepareMermaidSvgMarkup()`），是项目中最复杂的函数。

### 3. 占位符保护翻译

翻译前将代码块和公式替换为占位符：

```
$$E=mc^2$$ → MATHBLOCK0PLACEHOLDER
`code` → CODEINLINE0PLACEHOLDER
```

翻译 API 只看到纯文本+占位符，不会改动代码/公式。翻译后按占位符还原。

### 4. 可插拔模板系统

```js
// 注册接口
TemplateManager.register({
  id: 'my-template',
  name: '我的模板',
  getStyles(mode, themeColor) { return { h1, h2, h3, ... }; }
});
```

模板必须提供与 WechatStyles 兼容的函数集（sectionNumber/h1/h2/...共15个函数），主题色通过 `{{THEME_COLOR}}` 占位符 + `applyTheme()` 替换实现。

### 5. [lead] 自定义段落标记

在 Markdown 中写 `[lead] 内容`，renderer 检测到 `[lead]` 前缀后渲染为主题色浅背景块（`THEME_TINT_BG`，12% 不透明度混合白色）。

## 与我们 wechat-pb 的对比

| 维度 | markdown-to-wechat-converter | wechat-pb (knowwhythat) |
|------|------|------|
| 运行方式 | 浏览器端，实时渲染 | Go CLI，命令行 |
| 模板系统 | JS 函数集，可插拔注册 | Go 模板引擎，31套主题 |
| 高亮内联 | DOM遍历+computedStyle | chroma库+premailer |
| 公式支持 | MathJax SVG | 无 |
| 翻译集成 | OpenRouter API 内置 | 无 |
| 部署依赖 | 零（开浏览器即用） | Go 编译 |
| 输出渠道 | WeChat + Substack + GitHub | WeChat only |

**结论：互补关系。** 浏览器端做实时预览+公式+翻译，CLI 做批量渲染+主题+发布。

## 🔍 借鉴点

### ① 有利进化（2项，评估后判定：已有替代方案）

- hljs→内联样式策略 → 我们 wechat-pb 已有 premailer 内联方案覆盖
- 占位符保护翻译 → 我们的 execute_code 翻译管线已有类似保护逻辑

### ② 有价值备用（2项）

- Mermaid SVG 内联计算模式 → 如未来需要浏览器端排版工具
- 插件式模板注册表 → 如需动态扩展样式方案

### ③ 知识库（3项）

- [lead] 自定义标记设计
- compact/standard 双模式参数化
- 全内联CSS无模块化架构的权衡

## 🔗 关联性

- [[wechat-pb SKILL]] — 我们现有的微信排版工具
- [[note-dual-format SKILL]] — 双格式输出流程
- [[html-quality-standards SKILL]] — HTML 输出质量标准

## 💡 启发

- 浏览器端实时预览 + 一键复制粘贴的工作流对用户非常友好，wech\-pb 可以考虑增加 web UI
- 占位符保护是 LLM 翻译代码/公式类内容的标准模式，值得在其他翻译场景复用
- Mermaid SVG 内联计算的思路可推广到任何需要"保留渲染结果但剥离CSS依赖"的场景

## 🔮 预判

- 短期：项目会继续增加模板和主题，但架构上缺乏模块化会成为瓶颈
- 中期：marked.js v3 旧 API 会被迫升级，可能触发 breaking change
- 长期：如果作者增加服务端渲染能力（Node.js），可以和我们 wechat-pb 形成前后端互补方案

## ✅ 落实情况

📋 借鉴点落实审计
├── ①有利进化 项：2个
│   ├── hljs内联样式 → 已有 premailer 替代，不重复实现 ✅
│   └── 占位符保护翻译 → 已有 execute_code 管线替代 ✅
├── ②有价值 项：2个 → memory 写入 ✅
└── ③知识库 项：3个 → 仅笔记 ✅

## 相关笔记
- [wechat-pb-formatting-tool_feishu-publish-notes](2026-04-13-wechat-pb-formatting-tool_feishu-publish-notes.md)
- [wechat-pb-formatting-tool](creative/2026-04-13-wechat-pb-formatting-tool.md)
