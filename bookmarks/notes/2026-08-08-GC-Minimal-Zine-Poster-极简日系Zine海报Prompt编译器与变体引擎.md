# GC Minimal Zine Poster — 极简日系 Zine 海报 Codex Skill（Prompt 编译器 + 变体引擎）

> **来源**：[github.com/LiamGvchi/gc-minimal-zine-poster](https://github.com/LiamGvchi/gc-minimal-zine-poster)
> **License**：MIT
> **Skill 名称**：`gc-minimal-zine-poster-v0-1`
> **平台**：Codex（可适配 Claude Code / Hermes）
> **标签**：海报设计、zine 风格、prompt 工程、图像生成

---

## 一句话定义

> 把任意主题/句子/情绪/文章构思变成**安静极简的日系 zine 风格编辑海报**——3:5 泛黄纸面画布、70%~90% 留白、一个小型视觉锚点、衬线/打字机字体、一个高饱和色彩锚、复印件/孔版印刷/半色调质感。核心是一个结构化的 **Prompt Compiler** + **5 轴变体引擎** + **Standard Color Engine**。

---

## 完整原文核心内容

### 视觉方向

| 元素 | 规范 |
|------|------|
| **画布** | 3:5 竖版泛黄纸面，无相框无样机 |
| **留白** | 70%~90% 纯纸面 |
| **视觉锚点** | 一个小主体，占画面 8%~25% |
| **字体** | 衬线/打字机/等宽小字，一句短语 |
| **色彩** | 纸色+灰黑支撑**一个高饱和度色彩锚** |
| **质感** | 复印/孔版印刷/半色调/活版印刷墨晕/扫描噪点 |
| **情绪** | 安静、诗意、怀旧、日记感、档案感、日韩独立 zine |

### Prompt Compiler — 9 个第一性原理渲染问题

每个 Standard Mode prompt 必须按此顺序回答：

| # | 问题 | 内容 |
|---|------|------|
| 1 | **Canvas** | 3:5 竖版手机海报；全幅泛黄纸面；无边框无样机 |
| 2 | **Attention Geometry** | 70%~90% 留白；一个视觉簇占 8%~25%；居中/上中/下中/左下/右上 |
| 3 | **Image Anchor** | 把主题转化为一个物体/碎片/照片裁切/标本/剪影/旧印刷插图/纹理窗口 |
| 4 | **Anchor Treatment** | 灰度照片+纸碎片用低对比/复印件柔和/撕裂边/半色调/扫描线/孔版颗粒/影印磨损/墨晕/轻微错版 |
| 5 | **Typography System** | 小号衬线/打字机/等宽；一句可读短语；可选微小日期/位置/天气+签名；半可读微文本或碎片字母 |
| 6 | **Color Logic** | 纸色+灰黑支撑一个高饱和度锚。优选钴蓝/群青；轮换青/紫/品红粉/柠檬黄/梨绿/橙/番茄红 |
| 7 | **Reproduction Texture** | 正射扫描纸面外观；哑光吸墨纸；漫射光；中低对比；无硬阴影无 3D 深度 |
| 8 | **Emotional Temperature** | 安静/诗意/怀旧/稀疏/日记感/档案感/遥远/记忆感 |
| 9 | **Hard Avoids** | 全出血场景/商业标题/产品广告/光亮样机/洁净 UI/电影光效/3D/霓虹/可爱卡通/密集拼贴 |

### Standard Prompt Shape（四段式结构）

| 段落 | 内容 |
|------|------|
| **第 1 段** | 画布 + 纸面 + 留白 + 视觉簇大小/位置 |
| **第 2 段** | 主体隐喻 + 锚点类型 + 锚点处理 |
| **第 3 段** | 字体 + 色彩策略 + 印刷瑕疵（声明精确高饱和色相、材质形态、视觉占比） |
| **第 4 段** | 平面扫描情绪 + 避免清单 |

### Variation Engine — 5 轴变体引擎

每次生成前从每个轴选一个选项。**随机性必须改变视觉语法，不只是位置**。

#### 轴 1：Layout Family（布局族）

| 选项 | 说明 |
|------|------|
| center-fragment | 中心微小图像/物体，周围大量空气 |
| lower-left-float | 左下象限小锚点，上方大量留白 |
| upper-right-block | 右上小色块/照片块+松散文字飘移 |
| dual-panel | 两个小型重叠或相邻面板 |
| irregular-cutout | 撕裂或有机纸形 |
| type-led | 字体为主视觉锚，图像次要或缺失 |
| dot-orbit | 点/字母/细线围绕小主体形成轨道 |
| single-specimen | 一个孤立物体，几乎无辅助图形 |

#### 轴 2：Image Anchor（图像锚点）

- tiny faded photo（微小褪色照片）
- torn-paper clipping（撕裂纸剪辑）
- flat silhouette（平面剪影）
- solid color block（纯色块）
- old printed illustration（旧印刷插图）
- object specimen（物体标本）
- translucent geometric overlay（半透明几何叠加）
- abstract texture window（抽象纹理窗口）

#### 轴 3：Typography Mode（字体模式）

- fragmented floating letters（碎片浮动字母）
- short phrase pressed against image edge（短语紧贴图像边缘）
- archive microtext with date/weather（档案微文本+日期/天气）
- diagonal scattered words（对角散布单词）
- low-contrast gray ghost text（低对比灰色幽灵文字）
- headline-as-object with rough letterpress（标题即物体+粗糙活版印刷）
- text inside a color block or cutout（色块/剪贴内文字）
- almost textless, only a tiny caption（几乎无文字，仅微小标注）

#### 轴 4：Texture Mode（质感模式）

- xerox softness（复印柔和）
- risograph grain（孔版印刷颗粒）
- letterpress ink bleed（活版墨晕）
- halftone degradation（半色调退化）
- film grain photo（胶片颗粒照片）
- scan noise and paper fibers（扫描噪点+纸纤维）
- aged paper mottling（陈旧纸面斑驳）
- soft motion blur on selected text（选定文字柔和动态模糊）

#### 轴 5：Mood Mode（情绪模式）

quiet / summer / solitude / childhood / seaside / afternoon / night / memory / slight surrealism

### Standard Color Engine（色彩引擎）

- 默认使用**一个明显饱和的不透明彩色墨水锚**
- 高饱和度区域占整个画面的 **0.8%~2.5%** 或视觉簇的 **15%~35%**
- 必须在缩略图尺寸下仍可见
- 色彩可以承载主体本身（彩色树/果实/贝壳/花/几何剪贴/窗口/海报碎片）
- 每张图只使用**一个主要高饱和色相**
- ❌ 不使用"近单色"/"弱强调"/"柔和强调"/"褪色强调"除非用户明确要求

### Negative Constraints（反向约束）

始终避免：
- 全出血主体或场景
- 商业海报标题层级
- 产品广告布局/logo/CTA/品牌活动感
- 洁净数字 UI 背景
- 光面纸样机或重纸阴影
- 3D 渲染/电影光效/硬阴影/景深/霓虹/赛博朋克
- 可爱卡通/动漫海报/时尚编辑戏剧感
- 过多物体/贴纸/颜色/标注/装饰纹理
- 高分辨率图库照片级写实
- 长而洁净的完美可读文本

### 工作流（6 步）

1. **确定模式** → Standard Mode
2. **解析用户内容** → 提取核心主体/情绪/精确文字/视觉隐喻
3. **选择变体配方** → 从 5 轴各选一个选项
4. **编写最终 prompt** → 四段式结构
5. **生成图像** → 默认出图，不停在 prompt-only
6. **返回图像 + prompt** → 附带变体配方和简短解读

---

## 能否形成 Hermes Skill 的分析

### 适配方案

| 维度 | 原版（Codex） | Hermes 适配 |
|------|-------------|-------------|
| **Prompt 编译器** | SKILL.md 内嵌规则 | ✅ 直接复用，平台无关 |
| **出图引擎** | Codex 内置 `$imagegen` | ✅ 调用 `chatgpt-image`/`comfyui`/`free-image-generation` |
| **变体引擎** | 5 轴随机选择 | ✅ 纯逻辑，Python 可实现 |
| **色彩引擎** | 规则约束 | ✅ 纯逻辑 |
| **触发方式** | `$gc-minimal-zine-poster-v0-1` | Hermes Skill 触发词 |

### 可复用的核心价值

| 组件 | 可复用到 Hermes | 说明 |
|------|----------------|------|
| **9 个渲染问题** | ✅ 任何图像生成的 prompt 结构化框架 | 第一性原理拆解 |
| **5 轴变体引擎** | ✅ 确保输出的视觉多样性 | 每轴 8~9 个选项 = 32768 种组合 |
| **Standard Color Engine** | ✅ 色彩策略约束 | 避免色彩失控 |
| **四段式 Prompt Shape** | ✅ Prompt 结构模板 | 确保一致性 |
| **Negative Constraints** | ✅ 反向提示词 | 通用约束 |

---

## 结合最新研究与技术变化

### 1. 与 shuohao-skills (novel-characters) 的关联

两者都是 Codex Skill，展示了 Skill 正在从"工具调用"进化为"风格化 prompt 编译器"——novel-characters 编译角色设定，gc-minimal-zine-poster 编译海报 prompt。共同模式：**结构化规则 → 变体引擎 → 校验 → 输出**。

### 2. 与数字人口播 Rachel Skill 的关联

Rachel Skill 的"固定流程+状态追踪+门禁确认"和 gc-minimal-zine-poster 的"变体引擎+色彩引擎+反向约束"都是把创意工作流程化。

### 3. 与 baoyu-infographic / document-illustrator 的关联

Hermes 已有信息图和文档配图 Skill，但都是**信息驱动**的。gc-minimal-zine-poster 是**情绪驱动**的——追求的不是信息传达效率，而是审美一致性。

### 4. 与 SkillOpt 的关联

gc-minimal-zine-poster 的 Standard Prompt Shape（四段式）是 SkillOpt 的"Propose→Verify→Compound"在创意领域的映射——每次生成是一个 Propose，缩略图检查是 Verify，变体引擎确保持续多样性。

---

## 学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **9 个渲染问题** | 图像 Skill 的 prompt 结构化 | 高 |
| **5 轴变体引擎** | 创意输出的多样性保证 | 高 |
| **Standard Color Engine** | 色彩约束避免失控 | 高 |
| **四段式 Prompt Shape** | Prompt 结构模板 | 高 |
| **缩略图检查** | 生成后验证（缩略图看色彩锚是否可见） | 中 |
| **Negative Constraints** | 反向提示词的标准做法 | 中 |
| **第一性原理拆解** | 把"风格"拆成可执行的渲染问题 | 高 |

---

## 趋势判断

1. **Codex Skill 正在覆盖创意设计领域**——从代码工具到角色拆解、数字人制作、海报设计
2. **Prompt 编译器是 Skill 的新形态**——不是调用 API，而是把设计规则结构化为可执行的 prompt 生成逻辑
3. **变体引擎确保创意多样性**——5 轴 32768 种组合避免"每次都一样"
4. **日系极简 zine 风格正在成为 AI 生图的独立品类**——与商业海报/动漫/写实并列
5. **Skill 之间的风格可组合**——novel-characters 出角色 → gc-minimal-zine-poster 做海报 → Rachel 做口播视频

---

## 📎 关键文件索引

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 完整 Skill 指令（12.9KB，含 Prompt Compiler + 5 轴变体引擎 + 色彩引擎 + 工作流） |
| `README.md` | 英文说明 + 安装指南 |
| `README.zh-CN.md` | 中文说明 |
| `README.ja.md` | 日文说明 |
| `examples/night-door.jpeg` | 示例：夜门 |
| `examples/yellow-step.jpeg` | 示例：黄色阶梯 |
| `examples/shore-pause.jpeg` | 示例：海岸停顿 |
| `examples/pause-map.jpeg` | 示例：停顿地图 |
| `examples/typhoon-memory.jpeg` | 示例：台风记忆 |
| `examples/moon-tide.jpeg` | 示例：月潮 |

---

*笔记创建：2026-08-08 · 来源：gc-minimal-zine-poster GitHub + SKILL.md*


## 相关笔记

- 暂无直接关联笔记 — 该 Skill 聚焦海报 Prompt 编译器与变体引擎，属独立创意工具类笔记。可关注后续图像生成/Zine 设计相关笔记。
