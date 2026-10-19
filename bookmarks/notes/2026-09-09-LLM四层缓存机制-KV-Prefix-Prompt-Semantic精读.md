# LLM 四层缓存机制：KV / Prefix / Prompt / Semantic——Avi Chawla 长文精读 + 一手源核实 + Hermes 体系对照

> **来源**：X/Twitter @_avichawla（Avi Chawla，Daily Dose of Data Science 联合创始人，ex-Mastercard AI Engineer）2026-08-28 长文（X Article）
> **原文链接**：https://x.com/_avichawla/status/2093265776266637739 （文章本体 https://x.com/i/article/2093210840468189184）
> **数据**：浏览 1,274,496 / 收藏 2,377 / 赞 1,285 / 转发 176（病毒级传播的技术深度文）
> **一手源核实**：CacheBlend = arXiv:2405.16444（Yao et al., EuroSys 2025），TTFT 2.2-3.3× / 吞吐 2.8-5× / F1 损失 <0.02 全部确认
> **笔记日期**：2026-09-09
> **关联笔记**：《AI工程化终极路线图》《AI后思考时代的投入决策》

---

## 零、结论先行

这篇 21.5KB 的长文做了一件业界急需的事：**把四个都被叫做"caching"的东西一次性讲清**——它们存在 LLM 栈的不同位置、存储不同对象、失效条件不同、风险等级完全不同。

**一句话总结四层**：
| 层 | 存什么 | 匹配方式 | 错了会怎样 |
|---|--------|---------|-----------|
| KV cache | 单请求的注意力张量 | ——（请求内机制） | 不适用 |
| Prefix cache | KV 张量（跨请求，服务端） | token ID 哈希链，**精确前缀** | miss = 花钱+延迟 |
| Prompt cache | 同上（厂商计费版） | 同上 | 同上 |
| Semantic cache | **完成的响应字符串** | 嵌入余弦相似度，**模糊** | **200 状态码 + 错误答案** |

**最有价值的洞察**：前三层是 correctness-neutral（只影响成本不影响正确性），第四层 semantic cache 是唯一会**自信地返回错误答案**的层——hit rate 对它根本不是正确指标。这个"四层风险不对称"框架比任何单层教程都值钱。

---

## 一、原文四层机制忠实还原

### 1. KV Cache：请求内的注意力状态

- **prefill 阶段**：模型为每个 prompt token 在每层计算 key/value 向量并存储；**decode 阶段**在这些向量上做注意力，每个新 token 只追加一对 KV——避免每步重算整个序列
- **为什么只缓存 K/V 不缓存 Q**：因果掩码下，query 向量只在处理该 token 那一步用一次；而 K/V 会被其后每个 token 读取
- 效果：decode 从 matrix-matrix 乘法（全序列）降为 matrix-vector 乘法（单 token）
- **代价**：每步都要从 HBM 加载整个缓存 → **decode 从 compute-bound 变为 memory-bandwidth-bound**，GPU 大部分时间在等内存
- **大小决定并发容量**：70B 模型 BF16 下，单个 128K 上下文的 KV cache ≈ 40GB——相当于整个 4-bit 模型
- **压缩手段**：GQA（组内共享 KV 头）/ MLA（DeepSeek 系，压成潜在向量）/ 缓存量化（容量翻倍，短上下文反而更慢）
- **关键限制：缓存随请求释放**——20 轮对话的第 20 轮要按全价重新 prefill 前 19 轮。自己持有 `past_key_values` 传回可跨轮复用，但**只有当第 2 轮的 token 序列与第 1 轮逐 bit 前缀一致时才有效**

### 2. Prefix Caching：跨请求的服务端复用

- 机制：请求结束后引擎**不释放** KV 块，留在共享池供后续请求查找
- **vLLM 的哈希链**：默认 16 token 一块，每块 key = hash(父块哈希 + 块内 token IDs)——块 5 的 key 编码了块 1-5 的全部信息，天然实现前缀查找
- 调度器按序匹配，**第一个 miss 即停**（后续块的 key 依赖前面的块，跳过没有意义）；命中块引用计数 +1 防驱逐
- **salt 参数**：多租户隔离——per-tenant salt 改变首块哈希，同文本不同租户落不同块（牺牲内存和命中率换隔离）
- **四个坑**：
  1. 只省 prefill，decode 时间不变——把整体加速归功于缓存会夸大
  2. 哈希本身有成本，全独特 prompt 流量下实测**吞吐反而回退**
  3. 驱逐降低命中率：缓存和运行批次共享同一 GPU 内存池，长共享前缀占用最多块、损失最疼
  4. **RAG 是重灾区**：检索块每次不同且顺序变化，链式哈希下两个检索相同文档但顺序不同的请求**零共享**
- **CacheBlend 解法**（LMCache 开源实现，已核实 arXiv:2405.16444）：不逐块拼接缓存，而是任意位置复用 + 只重算小部分 token——选"预计算值与全注意力结果偏差最大"的 token 子集重算，恢复跨块注意力并修复位置编码。TTFT 提升 2-3×，重算成本与慢速存储取块流水化

### 3. Prompt Caching：厂商计费版

- 对象仍是 KV 张量（不是你的文本），仍要求完全渲染上下文的精确前缀匹配
- **渲染上下文包含你从未写过的厂商侧系统内容**——这就是最小长度和失效规则从外面看似任意原因
- Anthropic 代码示例核心：`cache_control` 标记**位置决定覆盖范围**——写在哪个块，就为从请求开始到该块（含）写一条缓存条目。用户消息（每次变化）必须放在标记**之下**
- usage 计数器诊断法：首次调用 `cache_creation_input_tokens` 非零、读取为零；第二次相反（指令按 0.1× 计费）；**两者都零 = 前缀低于最小可缓存长度，请求根本没走缓存，且不报错**
- 经济账：Anthropic 写 1.25× / 读 0.1×；**回溯上限 20 块**——两次调用间插入超过 20 块对话，上次写入超出范围，命中停止

### 4. Semantic Caching：模糊匹配的响应缓存

- 机制：嵌入入站 prompt → 最近邻搜索 → 相似度超阈值直接返回存储的响应，**跳过模型**——所以省输出 token 也省输入
- 代价：**每个请求都要付嵌入往返成本，包括所有 miss**
- **生产化五个决策点**（原文代码 demo 逐条映射）：向量归一化（否则跨长度不可比）/ lookup 返回嵌入避免重复计算 / 规模化要换 ANN 索引（引入召回率参数）/ **store 只在 miss 路径调用，无任何机制验证存储答案的正确性**
- **致命实验**（原文最精彩处）：三对 prompt——真改写（该共享答案）/ 差一个否定词（该给相反答案）/ 差一个数值（该给不同答案）——**三者相似度分数挤在一起，改写与否定词差距 <0.01**。这个余量在真实流量下根本守不住
- 阈值困境：调高→命中率塌缩但嵌入费照付；调低→命中率与"自信错误率"一起涨。已发表默认值 0.75-0.97 不等——**它是流量属性，不是可抄的常数**。有些失败（嵌入表示本身的缺陷）任何阈值都拦不住
- **第五层彩蛋**：精确匹配响应缓存（byte-identical 才返回）——零误报风险，先量重复率再上嵌入

---

## 二、生产 Takeaways（原文总结 + 补充）

原文给出的五条生产失效点，每条都是真金白银：

1. **prompt 开头的任何变量（时间戳/请求 ID/用户名）都会使其后所有块失效**。稳定内容在前、变量在后、边界打标
2. **工具 schema 通常排在系统提示之前**——重排一次 = 整缓存作废
3. **渲染进 prompt 的设置项**：Anthropic 上切换 web search/citations/thinking config/tool_choice 都会重写 prompt 文本；**A/B 测试两种 reasoning effort = 缓存裂成两半**
4. **总结历史 = 重写前缀 = 下次调用按冷 token 全价**；原地截断工具输出保持前缀 byte-identical 缓存才活着
5. **缓存条目绑定模型**——路由到便宜模型仍要按冷费率 prefill 全部累积历史
6. （补充诊断法）**定位复用断点要比对 token IDs 而非日志文本**——日志里看起来相同的两个 prompt 可能差一个 BOS token/尾换行/重序列化的工具 schema。实测案例：第一轮没写 system message，chat template 填了模型默认值，两个 prompt 在 index 3 就分叉，零复用

**四层统一视角**（原文收尾）：前三层是同一个思想在三个范围的递进——KV cache 保一个请求内，prefix caching 保请求结束后，prompt caching 是厂商在自己硬件上跑 prefix caching 并对复用部分单独计价。Semantic cache 完全不同：存响应文本按嵌入相似度索引，命中跳过模型省双份 token——但命中可能错，且以正常 200 状态码返回。

---

## 三、一手源核实与扩展

| 原文关键论断 | 核实结果 | 来源 |
|-------------|---------|------|
| CacheBlend TTFT 提升 2-3× | ✅ 精确匹配（论文 2.2-3.3×） | arXiv:2405.16444 |
| "重算偏差最大的小部分 token" | ✅ 机制确认：第一层全重算+第二层部分重算得准确 QKV，比较 V 矩阵偏差选 top-k token（HKVD 集合） | 同上 + CacheClip (arXiv:2510.10129) 引述 |
| "恢复跨块注意力+修复位置编码" | ✅ 确认：质量损失 F1/Rouge-L <0.02，多数场景质量超 full reuse 2×+ | 论文实验节 |
| Anthropic 写 1.25× / 读 0.1× | 与公开价格表一致（未逐字核对，标注为作者转述） | Anthropic docs |
| 20 块回溯上限 | 作者转述，未独立核实（标注） | Anthropic docs |
| 语义缓存相似度悖论 | 机制自洽（嵌入对否定不敏感是已知特性），无争议 | —— |

**领域演进补充**（核实中发现的增量，原文未提）：CacheBlend 之后该方向已形成研究线——CacheClip（arXiv:2510.10129）用小辅助模型近似 token 重要性降低选择成本；Adaptive KV Cache Reuse（arXiv:2605.24022）用频率引导的重要性建模替代 HKVD；Fusion RAG Cache 综述（arXiv:2601.12904）把这条线统称为 chunk-level KVCache reuse。**这个方向 2026 年仍在活跃产出**。

---

## 四、Hermes 体系对照与落地

| 四层 | Hermes 体系现状 | 对照结论 |
|------|----------------|---------|
| KV cache | 理论层已掌握（llm-inference-optimization skill 有 PagedAttention 章节） | 达标 |
| Prefix caching | Jetson 本地 ollama 未显式配置 prefix cache；AutoDL vLLM 部署时未调 block_size/salt | **可优化**：vLLM 部署 checklist 应加 prefix cache 配置项 |
| Prompt caching | **正在用**（config prompt_cache_ttl 已配，默认 300s/可选 3600s） | ✅ 但原文提醒了两个盲点：①压缩历史=前缀作废，compression 阈值 0.9 与 cache TTL 的交互要留意；②模型路由切换会裂缓存——fallback chain 跳模型时缓存全部作废，成本模型要算进去 |
| Semantic cache | 无 | 暂不需要——我们的流量是笔记生产（每次 prompt 天然唯一），不是 FAQ 型重复流量 |

**三条可落地动作**：
1. **系统提示的日期字段检查**：原文第 1 条失效点直指我们的架构——Hermes 系统提示含日期（byte-stable 设计刻意为之，见 system_prompt.py 注释），但任何会话级变量若被渲染进前缀就会裂缓存。值得做一次 token IDs 级前缀审计
2. **fallback 链的成本模型修正**：模型切换 = 缓存全作废 + 冷费率全量 prefill。现有 model-fallback-chain skill 的决策逻辑应把"缓存作废成本"计入切换阈值
3. **工具 schema 稳定性审计**：工具集按平台/会话启用（tools enable 后 /reset 生效）正是为了缓存稳定——与原文第 2 条完全同构，说明 Hermes 的设计正确，但值得把这条原理写进 skill 注释

---

## 五、局限性

1. **代码 demo 未实测**：原文声称全部代码可在单机 CPU + 360M 模型复现（transformers v5 API），本笔记未跑
2. **Anthropic 价格与 20 块上限**为作者转述，未逐字核对官方价格页
3. vLLM 哈希链细节基于原文引用的源码走读（block_hashes/schedule 方法），未直接读 vLLM 源码核对
4. 第四章 Hermes 对照基于架构推断，未做实际 token IDs 审计

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一、二 | **原文忠实还原**（X Article 全文 21.5KB，fxtwitter API 提取） |
| 三 | **一手源核实**（arXiv 论文交叉验证 + 领域演进补充） |
| 四 | **Hermes 体系对照**（本笔记扩展） |
| 五 | 局限性 |


## 相关笔记

- [LLM批处理三策略详解](./2026-09-01-LLM批处理三策略详解-静态动态连续与ChunkedPrefill.md) — 推理服务侧姊妹篇
- [量化LLM激活转向剂量响应与失败不对称](./explore/2026-09-09-量化LLM激活转向剂量响应与失败不对称.md) — 量化×推理效率交叉
