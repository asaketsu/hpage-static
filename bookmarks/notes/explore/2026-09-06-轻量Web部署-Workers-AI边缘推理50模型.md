# 轻量 Web 部署：Workers AI 边缘推理 — 50+ 模型目录、Neurons 计价与两种调用面

> 探索日期 2026-09-06 | 兴趣等级 L3 | 来源 6 篇 | 类型 auto-explore（嗅探队列）
> 前序笔记：2026-08-31-Workers全栈部署 / 09-03-Smart-Placement / 09-04-V8-isolate / 09-04-KV-vs-DO
> 本篇是「轻量Web部署」领域关键词表最后一项（Workers AI 边缘推理），至此全领域闭环

## 摘要

Workers AI 是 Cloudflare 边缘网络上的推理即服务：50+ 托管模型（实测目录约 80 个）跑在 200+ 城市的 GPU 上，按统一单位 Neurons 计价，免费层每天 10,000 Neurons（UTC 00:00 重置），超出后 $0.011/千 Neurons。核心价值不是"又一个 LLM API"，而是与 Workers 生态的同构集成——`env.AI.run()` 一行绑定调用、AI Gateway 统一治理（还能反代 OpenAI 等非 CF 模型）、Vectorize 向量库 + R2 组成完整 RAG 栈。模型面覆盖 LLM（Llama/Gemma/GLM-Flash/Kimi K2.6/DeepSeek-R1 蒸馏）、FLUX 文生图、Whisper/Deepgram 语音、BGE-M3 嵌入。定位是**高频低延迟的日用品模型**，不是前沿模型替代品。

---

## 一、模型目录全景（关键发现 1）

> 官方口径"50+ models in 200+ cities"，第三方实测（2026-06 校验）约 80 个可用模型，分四大族 + 专用模型：

```
┌─ 文本 LLM ─────────────────────────────────────────┐
│  Llama 3.x/4 · Mistral · Qwen · Gemma 4 (26B-A4B)  │
│  GPT-OSS · DeepSeek-R1 蒸馏 · GLM-4.7-Flash        │
│  Kimi K2.6 (工具+视觉) · Granite 4.0 Micro         │
├─ 图像生成 ─────────────────────────────────────────┤
│  FLUX.1 [schnell] · FLUX.2 [klein] 4b/9b (26-01新) │
│  Stable Diffusion · Leonardo Phoenix/Lucid         │
├─ 语音 ─────────────────────────────────────────────┤
│  Whisper (含 tiny-en 批处理) · Deepgram Aura-2 TTS │
│  Deepgram Flux (WebSocket 实时 ASR, 语音Agent向)   │
├─ 嵌入/专用 ────────────────────────────────────────┤
│  BGE-M3 · 翻译 · 重排(rerank) · 文本分类           │
└────────────────────────────────────────────────────┘
```

- 目录更新快，弃用同样快：`llama-3-8b-instruct` 系 2026-05-30 已弃用，官方迁移指引是 `@cf/zai-org/glm-4.7-flash`（快速工具调用）/ `@cf/google/gemma-4-26b-a4b-it` / `@cf/moonshotai/kimi-k2.6`
- 支持 BYO LoRA：上传 LoRA 适配器做微调推理，不必重写全量参数

## 二、Neurons 计价模型（关键发现 2）

> 把 token/tile/step/音频分钟全部折算成一个单位，只看一个数字。

- 免费层：10,000 Neurons/天，全模型共享（非每模型独立额度），UTC 00:00 重置
- 超额行为：**请求直接失败，不产生隐藏账单**——超限即 fail，想继续须升级 Workers Paid（$0.011/千 Neurons）
- 速率限制按任务类型设置：文本生成默认 ~300 req/min（单模型 150-1,500）
- 价格锚点（验证成本直觉用）：
  - Llama-3.1-8B-AWQ：$0.123/M in + $0.266/M out
  - GLM-4.7-Flash：$0.060/M in + $0.400/M out（131K 上下文）
  - FLUX.1-schnell：4.8 Neurons/512px tile + 9.6 Neurons/step
- 大模型烧额度远快于小模型——Neuron 成本随模型差异极大，免费层选小模型能跑很久

## 三、两种调用面 + Batch API（关键发现 3）

**Workers 绑定（首选，同进程零网络开销）：**

```ts
// 流式对话
const answer = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  prompt: '...',
  stream: true,
});
return new Response(answer, {
  headers: { 'content-type': 'text/event-stream' },
});
```

**REST API（任意后端可调，OpenAI SDK 兼容）：**

```bash
curl https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/meta/llama-3.1-8b-instruct \
  -H "Authorization: Bearer $API_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "..."}'
```

**Batch API（非阻塞）：** 请求加 `?queueRequest=true` 拿 `request_id`，再 POST 同端点轮询取结果——适合 embeddings 批量灌库等离线任务。

## 四、生态位：AI Gateway 是隐藏主角（关键发现 4）

> `env.AI.run()` 的第三参数可以挂 `gateway: { id: "default" }`——这一步把推理流量纳入 AI Gateway 的统一缓存/限流/日志/计费治理。

- 关键能力：同一个 `env.AI.run()` 还能跑 `openai/gpt-4.1-mini` 等**非 Cloudflare 模型**——AI Gateway 作为统一代理层，多供应商推理收拢到一处监控
- RAG 全家桶一次配齐：Workers（逻辑）+ Workers AI（生成/嵌入）+ Vectorize（向量库）+ R2（文档湖）+ Durable Objects（会话态）
- 第三方评测结论（2026-03）：Cloudflare 是当时最便宜的推理选项之一，"sub-penny-per-request"；适合高频/低延迟/日用品模型，**不适合**前沿模型、专域深度需求、重微调场景

## 五、对现有工作的价值

- 与本地推理互补：Jetson Orin 跑本地模型（nexa/ollama），Workers AI 可作为**零边际成本的云端备援**——10K Neurons/天免费层足够低频任务的兜底与 PoC 验证，且无需维护 GPU
- 可并入 free-model-apis 免费四线（智谱/HF/GitHub Models）作第五线：优势是免费层无信用卡、超限即断不扣费，风险见下
- hpage.top 轻量工具升级路径：若笔记站需要摘要/嵌入/配图等 AI 能力，Workers 单文件即可挂上，与已深学的 KV/DO/D1 架构同域
- 对量化/盯盘工具的价值有限（无实时数据能力），但对 Content 线（生图/转录/翻译）直接可用

## 六、关键风险与盲点

- **目录弃用频繁**（官方标注来源）：llama-3-8b 系已弃用、kimi-k2.5→k2.6 强制别名且涨价——生产引用模型名必须订阅 changelog，否则某天直接 404
- **免费层 10K Neurons 是共享池**（社区复现）：大模型一次长上下文请求可能烧掉数千 Neurons，多模型混用会互相挤占
- 边缘 GPU 无预留容量保证：突发流量下延迟波动比专属 GPU 服务大（推理排队）
- 第三方"最便宜"结论有时效性，2026-03 数据，须以官方 pricing 页实时为准

## 七、行动建议

1. 【低成本】注册 Workers Free 层，用 REST API 跑一次 GLM-4.7-Flash 冒烟测试，验证免费层可用性与实际 Neuron 消耗（30 分钟）
2. 【工具链】把 Workers AI REST 端点补进 free-model-apis skill 的备援清单（作为第五线，标注"超限即断"特性）
3. 【不急】生图/转录类需求优先试 FLUX.1-schnell + Whisper tiny（免费层最省 Neuron 的两个）

## 一页速查

> - 调用：`env.AI.run('@cf/xxx/模型名', {prompt, stream})` 或 REST `/accounts/{id}/ai/run/{model}`，OpenAI SDK 兼容
> - 计价：统一 Neurons；免费 10K/天全模型共享；超额 fail 不扣费；付费 $0.011/千
> - 选型锚：便宜文本=GLM-4.7-Flash/Granite Micro；生图=FLUX.1-schnell；嵌入=BGE-M3；实时 ASR=Deepgram Flux
> - 治理：AI Gateway 第三参数挂 `gateway.id`，统一缓存/限流/日志，可反代 OpenAI
> - 红线：模型名会弃用（订阅 changelog）；免费层是共享池，大模型烧得快；无容量保证

## 来源列表

1. developers.cloudflare.com/workers-ai/platform/pricing（官方定价，Neurons 表）
2. developers.cloudflare.com/workers-ai/models（官方模型目录）
3. developers.cloudflare.com/workers-ai/configuration/bindings（官方绑定 API）
4. developers.cloudflare.com/workers-ai/changelog（弃用与迁移通知）
5. pricepertoken.com/endpoints/cloudflare/free（第三方免费层实测，2026-06 校验）
6. deploybase.ai/articles/cloudflare-ai-pricing（第三方性价比评测，2026-03）


## 相关笔记

- [2026-09-04-轻量Web部署-V8-isolate冷启动1ms](./2026-09-04-轻量Web部署-V8-isolate冷启动1ms.md) — 系列前序，运行时层
- [2026-09-04-轻量Web部署-KV-60s最终一致vs-DO串行](./2026-09-04-轻量Web部署-KV-60s最终一致vs-DO串行.md) — 系列前序，存储层
- [2026-09-05-AI基础设施商业模式-推理经济学](./2026-09-05-AI基础设施商业模式-推理经济学.md) — 边缘vs中心化推理经济学
