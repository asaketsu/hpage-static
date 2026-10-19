# Jev 式 LLM 单 token 概率传感器：一个 prompt + logprobs 代替专用分类器

> 来源：@yibie 推文（x.com/yibie/status/2104024011692753228）+ Allan Riordan Boll 博客（allanrbo.blogspot.com，2026-09-25）
> URL: https://allanrbo.blogspot.com/2026/09/a-jev-like-wrapper-for-llms-including.html
> 阅读日期：2026-09-27 | 评分：★★★★☆（4/5，小而美的技术技巧，对 Hermes 传感器体系有直接可抄性）
> tag: #LLM #logprobs #Jev #传感器 #不确定性量化 #vision #llama.cpp #提示工程

## 一、核心技巧（一个 prompt 模板 + 三个 API 参数）

把"判断题"变成单 token 生成，再读 LLM 的 token 概率分布——**一个通用 LLM 顶一排专用分类器**：

```
State: 我的订单到货时损坏了，我想退款。
Question: 应该哪个团队处理？
[A] billing
[B] shipping
[C] returns
Answer with the letter of the best option only.
```

API 参数：`max_completion_tokens: 1` + `logprobs: true` + `top_logprobs: 20`。返回最优字母的同时附上各候选 token 的对数概率——**不仅知道答案，还知道模型的置信度分布**。

三种题型统一收敛为字母选项：
| 题型 | 选项形态 | 输出 |
|------|----------|------|
| choice（多选一） | criteria 字典 → 字母 | 胜选项 + 全概率分布 |
| noul（布尔/是非） | true/false | P(true) 百分比 |
| score（序数评分） | criteria 列表 → 编号 | 期望分值（概率加权） |

## 二、工程细节（正文代码的精华）

1. **单 token 生成的经济学**：只生成 1 token 避免长回答，快；但输入处理仍花时间——**多问题共享 state 前缀可 KV-cache**（后端支持时）
2. **视觉也通**：作者给 Jev 格式加了 `attachments` 字段（base64 JPEG），vision 模型同样读 logprobs——摄像头帧→"有人吗/室内外/亮度"三连问
3. **性能实测**：Gemma 4 12B QAT @ RTX 3090 + llama.cpp ≈ **1 FPS**（每帧 3 问）；OpenAI gpt-6-luna ≈ 0.2 FPS（没做连接复用，每问每帧新连接）
4. **API 分叉**：llama.cpp 走 Chat Completions（top_logprobs 1024），OpenAI 走 Responses API + `top_p=1`（防剪枝掉候选）
5. **缺失选项的守门逻辑**：被 API 省略的 token 不能反超已返回的最末候选——缺失项合并概率 ≥1e-6 就报错拒绝输出，防"假完整分布"
6. **温度 0 + reasoning_effort none**：要的是分布读数不是创作

## 三、评论区最重要的一条（比正文更值钱）

Anonymous 09-26 评论：**"当前 transformer 只 attend 过去 token——把选项放输入之前，state 的每个词就能带着选项上下文被处理；这样还能关掉 reasoning 省时省钱，结果可能根本性改善。"**

这是对 prompt 结构的因果性修正：选项后置 = 模型读 state 时还不知道要判断什么（信息浪费）；选项前置 = 每个词的表征都朝判断任务对齐。**作者的模板（State→Question→Options→Answer）在这点上可能次优。**

## 四、💡 对我们的价值分析

### ✅ 已在做的（印证方向）
- **Hermes 传感器体系**（sensor-grid/proactive-sensor 五类传感器）都是"代码采集"型——本技巧给了"LLM 判断型"传感器的最廉价实现路径
- **content-judge**（LLM-as-Judge 评分卡）与本技巧同构，但走的是完整生成路径——本方案单 token + logprobs 快一个数量级

### ⚠️ 可改进的（差距）
- 我们的判断类调用（新闻筛选/内容评分/异常判读）全部生成完整文本再解析，**既慢又丢掉了置信度信息**——重大升级点
- 飞书推送决策、error-case 分诊、笔记质量门禁，都可以改成"字母选项+概率分布"形态

### 🔥 重点行动
1. **Hermes 传感器 LLM 化试点**：挑一个高频判断场景（如 error-log 分诊 HIGH/MEDIUM/LOW），用 choice+logprobs 重写——本地 nexa/Ollama（Jetson 已有）即可跑，每条日志 1 token 出分诊+置信度
2. **不确定性显性化**：P(最佳) < 0.6 时降级人工/追问——把"模型拿不准"从隐性变显性，正好补 content-judge 的软肋
3. **选项前置 A/B**：按评论区建议做两组模板对照（选项前置 vs 后置），实测分布质量差异——顺手产出一条可复用 prompt 模板进 skill

## 五、内容整理（归纳总结与关联分析）

**归纳总结**：Jev 式 wrapper = 单 token 生成 + logprobs 读取 + 字母化选项统一三类判断题（choice/noul/score），一个通用 LLM（含 vision）替代一排专用分类器，且自带置信度分布。关键数字：3090 本地 1 FPS、缺失选项合并概率 1e-6 守门、llama.cpp top_logprobs 1024 vs OpenAI Responses API。

**关联分析**：与 [[2026-05-18-Agent元认知-LLM不确定性感知]] 直接接力——那篇讲"为什么需要不确定性感知"，本篇给出最轻的实现（logprobs 即免费的不确定性信号）；与 sensor-grid 的关系是"物理传感器→LLM 语义传感器"的补全；与 ROSClaw 笔记（09-21）呼应：Verifier 谓词返回"测量值+阈值+为什么"，logprobs 概率分布正是 LLM 侧的同类证据链——不是 true/false 而是带置信度的可审计判断。

## 六、查询拓展

- Jev / OpenJev / SemIf 项目本体（自托管 LLM 状态-问题格式的源头）
- OpenAI logprobs cookbook（官方单 token 技巧集）
- guidance/outlines（结构化生成的另一条路：语法约束 vs 概率读取）
- 校准（calibration）：logprobs 的概率分布准不准？温度缩放/isotonic regression 校准方法

## 七、趋势判断

1. **LLM 用法从"生成"向"感知"扩散**：单 token + logprobs 让 LLM 成为通用语义传感器——成本结构与专用小模型重合（1 token ≈ 分类头），但改条件只需改一句话
2. **置信度将成为 Agent 判断的标配输出**：裸答案（"是 HIGH"）会被带分布的答案（"HIGH 0.72/MEDIUM 0.21"）取代——下游才有降级/追问的依据
3. **prompt 结构的因果性优化会被系统性研究**：评论区"选项前置"这类 attention 因果分析，是 prompt engineering 走向 prompt science 的信号
4. **本地小模型 + 传感器化 = 端侧 Agent 基建**：Jetson 类设备跑 12B 判 1 FPS 视觉问答，机器人/家庭助理的"环境理解层"门槛大降

## 八、指南分析（怎么用这篇文章）

- 直接抄模板：第一节 prompt + 第二节 API 参数（注意 llama.cpp 与 OpenAI 的端点分叉）
- 落地顺序：先文本判断场景（日志分诊）后视觉场景（摄像头帧），本地 llama.cpp 起步零成本
- 避坑：缺失选项守门逻辑（1e-6）必须保留，否则分布是假的；温度 0 + 关 reasoning

## 九、拓展应用推荐

- 与 [[2026-05-18-Agent元认知-LLM不确定性感知]] 并读（理论→实现闭环）
- Hermes 行动项：error-log 分诊 LLM 化试点（第四节行动 1），可挂进 sensor-grid 体系
- DUCK 项目：训练曲线异常判读（reward 骤降/熵坍缩的分诊）也可字母化——六类异常各占一字母，巡检 cron 每 token 出判读+置信度


## 相关笔记

- [2026-05-18-Agent元认知-LLM不确定性感知](./2026-05-18-Agent元认知-LLM不确定性感知.md) — 理论侧（不确定性感知），与本篇构成理论→实现闭环

→ 相关：[Jev-Engineering决策层架构](2026-09-28-Jev-Engineering决策层架构.md)（Jev 双篇之架构篇：决策契约/置信度路由/权限铁律）
