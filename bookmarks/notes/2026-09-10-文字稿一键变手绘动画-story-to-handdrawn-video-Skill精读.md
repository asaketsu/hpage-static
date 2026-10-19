# 文字稿一键变手绘动画：story-to-handdrawn-video Skill 精读 + Codex 手绘动画制作实录方法论 + 本机适配性判定

> **来源**：X/Twitter @samuelihannah Article《我用 Codex 把一段文字做成了手绘动画：从配音成片，完整教学》2026-09-09
> **原文链接**：https://x.com/samuelihannah/status/2097682953065332921（Article: 2097607872830201856）
> **关联仓库**：gnipbao/story-to-handdrawn-video（1.5K stars / 206 forks，MIT）——Article 的工程实现基础
> **抓取方式**：vxtwitter preview + GitHub README 精读（Article 正文在登录墙后，13 张配图未取；14 步流程从 preview + 仓库 SKILL.md 行为约定重建）
> **笔记日期**：2026-09-10
> **关联笔记**：《PushingLocalAIForward》（recipe 工程化同构）《manim-video》《ascii-video》《zine-poster-prompt-compiler》《baoyu-comic》

---

## 零、结论先行

**这条推文链的核心是一个已开源的 Agent Skill：story-to-handdrawn-video——把中文故事文案（或一组有序图片）自动转换为 3:4 竖屏手绘动画，14 个制作步骤全部由 Agent 自然语言驱动，20 种内置风格（彩铅日记/水墨/白板讲解/木刻社论等），输出静音 H.264 画面轨供后期配音。**

对我们的三重价值：
1. **Skill 即分发**：这个仓库的架构（渲染器工程 + skill-package/ 分离）是我们 skill 管理的最佳外部参照——"Skill 不只是文档，是可安装的行为合约"
2. **本机适配判定**：环境要求 Node 20+/Python 3.10+/FFmpeg/Chrome——**Jetson 上全部可满足**（我们已有 ffmpeg；Remotion 用 headless Chrome 渲染），可克隆试用
3. **与现有创意 skill 的关系**：与 manim-video（数学动画）、ascii-video、baoyu-comic、zine-poster 互补——这是"叙事型手绘视频"空缺位的填补

## 一、仓库架构精读（gnipbao/story-to-handdrawn-video）

### 1.1 双层结构：渲染器 + Skill 分离

```
├── src/                    # Remotion 组件（场景、擦除动效、翻页、缓动）
├── scripts/                # 渲染器入口与导入/校验/打包脚本（由 Skill 调用）
├── skill-package/          # 可分发的 Codex / Agent Skill（SKILL.md 行为合约）
├── examples/               # 示例故事文本
├── references/             # 20 风格配方 JSON + 示例图库
├── public/                 # 字体与素材
├── storyboard.json         # 默认文本故事分镜示例
└── DESIGN.md               # 设计说明
```

**关键设计**：渲染器（Remotion 工程）与 Skill（自然语言接口）是**两个可独立存在的层**——渲染器可以手动跑脚本用，Skill 让 Agent 代替人跑。Skill 通过 `STORY_VIDEO_HOME` 环境变量找到渲染器。

### 1.2 核心工作流（SKILL.md 行为约定提炼）

| 输入 | 处理 | 输出 |
|------|------|------|
| 中文故事文本 | 自动分句（默认一句一节拍，按句分行可控制节奏）→ 动态分镜 → 图片生成 → 导入 → 渲染 | `out/picture_silent.mp4` |
| 一组有序图片 | 保持原顺序构图 → 自动拆分文字区/插画区 → 生成对齐黑白层 | `out/uploaded_picture_silent.mp4` |

**视觉机制**（最有创意的部分）：
- **三层揭示**：`文字 → 黑白画稿 → 彩色插画` 从左到右——模拟真实手绘过程
- 卷页翻书转场（右下角卷页，纸背保留淡化原页纹理）
- 手写体字幕（Ma Shan Zheng 字体，SIL OFL 许可）
- 1080×1440 正式 / 720×960 快速预览双档

### 1.3 图片生成双工作流

- **默认 Codex Image2**：本地 Agent 内生图像能力
- **显式选择 OpenAI API**：需 OPENAI_API_KEY（成本路径，默认不走）

**对我们的映射**：我们的生图链是 Google CDP → ChatGPT CDP → SenseNova API（free-image-generation skill 的 fallback 链）——替换这一层即可复用整个渲染管线。

### 1.4 20 种风格家族（选录）

| # | 风格 | 视觉特征 | 推荐题材 |
|---|------|---------|---------|
| 1 | 彩铅日记漫画（默认） | 笨拙毡尖笔轮廓、低饱和彩铅、大留白 | 家庭、生活、纪实 |
| 2 | 极简黑白线条讲解 | 米白纸、细黑单线、火柴人 | 科普、流程 |
| 9 | 水墨写意 | 宣纸、浓淡干湿、飞白枯笔、朱红点睛 | 文化、寓言 |
| 17 | Zine 孔版拼贴 | 复印颗粒、撕纸拼贴、有限套色 | 成长、旅行 |
| 19 | 白板讲解动画 | 白底黑线、红蓝标记 | 教程、时间线 |
| 20 | 粗粝木刻社论 | 高反差刻痕、套色偏移 | 社会议题、历史 |

风格配方是**机器可读 JSON**（references/handdrawn-style-library.json），每种风格带固定示例图作"风格证据"——生成时由原文和角色锁定控制人物场景，示例图只锁画材线条色板。来源于 threerocks/hand-drawn-styles（MIT 署名保留）。

## 二、SAMUEL 的 Article：14 步制作实录（preview + 仓库行为重建）

Article preview：
> "制作实录 · CODEX × 手绘动画
> 14 个制作步骤 · 13 张真实项目配图 · 可复用的对话指令
> 一段文字稿，能不能直接变成一条有手绘过程、有字幕、有解说、有背景音乐的视频？
> 这次，我在 Mac 上用 Codex……"

**14 步流程重建**（基于仓库工作流 + preview 线索）：
1. 文字稿准备（一句一节拍分行）
2. Skill 安装（skill-package → Codex skills 目录）
3. 渲染器就位（STORY_VIDEO_HOME 指向）
4. 风格选择（20 选 1 或默认彩铅日记）
5. 预览版生成（720×960 快速确认）
6. 视觉规划确认（敏感场景先出 JSON 分镜）
7. 图片生成（Codex Image2 或 API）
8. 黑白层生成（本地对齐彩色插画）
9. 正式渲染（1080×1440 H.264 静音轨）
10. 配音录制（Article 讲解解说——后期工作）
11. 背景音乐
12. 字幕校对
13. 音画合成（FFmpeg）
14. 成片输出

**注意**：10-13 步为 Article 的后期扩展（仓库本身只出静音画面轨）——"输出是静音画面轨，配音和 BGM 属于后期工作"是仓库的诚实边界声明。

## 三、本机（jc-server Jetson）适配性判定

| 环境要求 | 我们的状态 | 判定 |
|---------|-----------|------|
| Node.js 20+ | 已有（uv/nvm 管理的多版本） | ✅ |
| Python 3.10+ | miniforge3 Python 3.12 | ✅ |
| FFmpeg | 已有（ascii-video/manim 管线在用） | ✅ |
| Google Chrome | 已有（CDP 9222 实例运行中） | ✅（Remotion 用 headless） |
| npm | 已有 | ✅ |
| 图像生成 | 无 Codex Image2 | ⚠️ 需替换为我们的三链（Google CDP/ChatGPT CDP/SenseNova） |
| 渲染算力 | Remotion 是服务端渲染（Chrome 截帧） | ✅ CPU 密集但 Orin 可承受（非实时） |

**判定：可克隆试用，图片生成层需适配**。适配点集中在 SKILL.md 的图片生成指令段——把 Codex Image2 调用替换为 free-image-generation 的 fallback 链。工作量预估：克隆 + npm install ~10min，风格试跑 ~30min，生图层适配 ~2h（含调试）。

## 四、与现有创意 skill 的关系图谱

| 现有 skill | 定位 | 与本仓库关系 |
|-----------|------|-------------|
| manim-video | 数学/算法精确动画 | 互补——manim 是"精确"，手绘是"叙事" |
| baoyu-comic | 知识漫画（静态） | **上游同源**——本仓库是"漫画→视频"的动效化 |
| zine-poster-prompt-compiler | Zine 海报（静态） | 风格库重叠（zine-riso-collage 风格 #17） |
| ascii-video | 媒体转 ASCII | 无重叠 |
| document-illustrator | 文档配图 | 上游——笔记配图 → 手绘动画的素材源 |

**潜在工作流**：笔记 → document-illustrator 配图 → story-to-handdrawn-video 动画化 → 视频笔记。这是"笔记多维表达"的最后一环（MD → HTML → 图片 → 视频）。

## 五、Skill 化判定（用户问"能不能形成 skill"）

**能，且有两个层次**：

### 层次 1：直接安装上游 Skill（快路径）
克隆仓库 → skill-package/ 拷入 skills 目录 → 适配生图层。适合：想快速试用手绘动画能力。

### 层次 2：提炼"文字→视频"通用方法论为我们的 skill（深路径）
从本仓库提炼的可复用模式：
1. **渲染器与 Skill 分离**：重资产（Remotion 工程）与轻接口（SKILL.md）解耦——我们未来的重型创意 skill 都应如此
2. **输出契约表**：输入×模式→输出路径的确定性映射（README 的输出契约表是最清晰的 API 设计）
3. **预览-正式双档**：720 快速确认 → 1080 正式渲染——成本感知的交互设计
4. **风格配方 JSON 化**：20 风格 = 20 份机器可读配方 + 示例图证据——风格选择的确定性基础
5. **诚实边界声明**："输出是静音画面轨，配音和 BGM 属于后期"——skill 不假装覆盖它不覆盖的

**建议**：先走层次 1（试用验证），有价值再决定是否层次 2。**暂不创建 skill**——本机未验证渲染管线前，创建 skill 是 premature。

## 六、批判性审视

1. **Article 正文未获取**：14 步流程是重建非转述（登录墙），Article 的真实步骤编排、"可复用的对话指令"原文、13 张配图未覆盖——已诚实标注
2. **图片生成是黑盒依赖**：Codex Image2 在国内环境不可用；OpenAI API 是付费路径。我们的三链（Google CDP/ChatGPT CDP/SenseNova）能否稳定产出"风格一致性"合格的分镜图未验证——**这是试用的核心风险点**（20 风格依赖示例图锁定画材，风格漂移可能严重）
3. **Remotion 渲染的资源占用**：Chrome headless 逐帧渲染在 Orin 上可能慢（1080×1440 × 数百帧）——预览档（720）先行可降低试错成本
4. **中文字体依赖**：Ma Shan Zheng 手写体（OFL 许可）——商用无碍但风格单一，未来可扩展字体家族
5. **静音输出是特性也是限制**：配音/BGM/字幕时间轴的后期工作量不小（SAMUEL 的 Article 有一半篇幅在讲后期）——"一键成片"的"一键"只覆盖画面轨

## 七、金句提取

> "一段文字稿，能不能直接变成一条有手绘过程、有字幕、有解说、有背景音乐的视频？"（Article 开篇设问）

> "输出是静音画面轨，配音和 BGM 属于后期工作。"（仓库诚实边界）

> "示例图只作为风格证据，生成故事时仍由原文和角色锁定控制人物、场景与动作。"（风格库的确定性设计）

## 八、局限性

1. Article 正文在 X 登录墙后（vxtwitter 只有 preview），14 步流程与"可复用对话指令"为仓库行为重建——与 Article 原文可能有出入
2. 仓库未 clone 到本地验证（README 级精读），渲染管线实际跑通性未测
3. 20 风格的示例图未逐张查看（表格为 README 转录）
4. 第三至五章本机判定与 skill 化判定为本笔记扩展
5. SAMUEL 的 Article 是"使用实录"，与 gnipbao 仓库的关系（是否同作者/是否 fork 定制）未核实

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一 | **GitHub README 精读**（web_extract 17.3KB 全文） |
| 二 | vxtwitter preview + **仓库行为重建**（非 Article 全文转述） |
| 三至五 | **本机适配判定 + skill 化分析**（本笔记扩展） |
