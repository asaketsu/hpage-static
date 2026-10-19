# 飞书 CardKit v1 Cards API 增量深度研究 — 卡片实体资源模型/组件级 API/流式集成进展

> **增量来源**: 8-05 笔记覆盖了 streaming_config V7.23 和延时更新，但未深入 CardKit v1 的**独立卡片实体资源模型**。本轮从官方 Card resource overview + Create card entity API + GitHub issue #16084 + 社区 PR #25202 定向补全。
> **学习日期**: 2026-08-06
> **触发**: sniff-auto 队列 s23072611「飞书 API: card」
> **前置笔记**:
> - `~/explore/2026-07-30-feishu-card-2.0-architecture-components-streaming-hermes-integration.md`（Card 2.0 架构/组件/streaming 基础）
> - `~/explore/2026-08-04-feishu-card-2.0-callback-protocol-form-container-variables-deep-dive.md`（回调/Form/变量）
> - `~/explore/2026-08-05-feishu-message-flow-api-streaming-config-v723-slash-commands-incremental.md`（消息流/streaming_config/延时更新）

---

## 0. 增量研究范围

8-05 笔记的知识缺口：CardKit v1 API 被提及但未系统梳理其**独立于 Message API 的资源模型**。本轮通过官方 `Feishu Card resource overview` + `Create card entity` API 文档 + GitHub issue #16084（8 条评论）+ 4 个社区 PR 的实现细节定向补全。

**核心认知刷新**：CardKit v1 不是 Message API 的子功能，而是飞书 Open Platform 的**独立资源层**，有自己的 CRUD 端点、权限模型、速率限制。

---

## 核心发现 1：CardKit v1 卡片实体资源模型 — 独立于 Message 的两层架构

### 1.1 两个核心资源：Card + Component

飞书 CardKit v1 API 围绕两个独立资源展开，与 Message API（`im/v1/messages`）完全分离：

| 资源 | 描述 | API 前缀 |
|------|------|----------|
| **Card（卡片实体）** | 可嵌入聊天消息、群置顶、链接预览的结构化卡片内容 | `/cardkit/v1/cards` |
| **Component（组件）** | 卡片内部的容器/展示/交互组件，可独立增删改 | `/cardkit/v1/cards/:card_id/elements` |

**关键认知**：传统流程是「构造完整 Card JSON → 作为 `interactive` msg_type 发送」。CardKit v1 引入了新范式：「先创建 card entity → 拿到 card_id → 再通过 component API 精细化操作 → 最后绑定到消息」。

### 1.2 Card 级 API 矩阵（4 个端点）

| 方法 | 端点 | 用途 |
|------|------|------|
| `POST` | `/cardkit/v1/cards` | **创建卡片实体**，支持 card_json 或 template 两种类型 |
| `PUT` | `/cardkit/v1/cards/:card_id` | **全量更新**卡片实体（整体替换） |
| `PATCH` | `/cardkit/v1/cards/:card_id/settings` | **更新卡片设置**（如 streaming 模式开关） |
| `POST` | `/cardkit/v1/cards/:card_id/batch_update` | **批量更新**卡片实体 |

### 1.3 Component 级 API 矩阵（4 个端点）

| 方法 | 端点 | 用途 |
|------|------|------|
| `POST` | `/cardkit/v1/cards/:card_id/elements` | **添加组件**到卡片 |
| `PUT` | `/cardkit/v1/cards/:card_id/elements/:element_id` | **全量更新**组件 |
| `PATCH` | `/cardkit/v1/cards/:card_id/elements/:element_id` | **更新组件属性** |
| `PUT` | `/cardkit/v1/cards/:card_id/elements/:element_id/content` | **流式更新文本**组件内容（LLM 逐 token 追加） |

**所有端点统一要求**：仅支持 Card JSON 2.0 结构（`schema: "2.0"`），`tenant_access_token` 鉴权，权限范围「Create and update card」。Store 应用和自建应用均可用。

---

## 核心发现 2：Create Card Entity API 深度规范

### 2.1 请求规范

```
POST https://open.feishu.cn/open-apis/cardkit/v1/cards
Rate Limit: 1000 次/分钟 + 50 次/秒
```

请求体核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | `card_json`（JSON 代码构建）或 `template`（CardKit 工具构建的模板） |
| `data` | string | 与 type 一致的卡片数据，**必须转义为字符串**；card_json 模式必须含 `schema: "2.0"` |

### 2.2 关键限制（官方文档明确）

- **仅支持 Card JSON 2.0 结构** — 不接受旧版 `{config, header, elements}` 顶层格式
- **不支持独占卡片模式** — 不能设置 `update_multi: false`
- **卡片实体有效期 14 天** — 过期后无法操作
- **一个卡片实体只能发送一次** — 发送后不可复用
- **卡片大小上限 30 KB** — 超限报错 200860

### 2.3 错误码速查

| HTTP | Error Code | 含义 | 排查 |
|------|-----------|------|------|
| 400 | 10002 | 请求参数无效 | 检查输入参数 |
| 400 | 200860 | 卡片内容超限 | 控制在 30KB 内 |
| 400 | 300301 | 组件 element_id 重复 | 检查组件 ID 唯一性 |
| 400 | 300302 | `update_multi` 为 false | streaming 模式必须设为 true |
| 400 | 300303 | 非 schema 2.0 | 必须声明 `schema: "2.0"` |
| 400 | 200220 | 卡片生成失败 | 检查 JSON 结构完整性 |

**与 feishu-card-table Skill 的对应**：Skill 中记录的 230099（unsupported tag）、200912（table column width invalid）等错误码是 Message API（im/v1）层面的；CardKit v1 API 用 300xxx 系列错误码，语义更清晰。

---

## 核心发现 3：Card Entity 与 Message 的绑定关系

### 3.1 发送 Card Entity 到消息

CardKit v1 创建的 card entity 不能直接出现在聊天中，需要通过 Message API 绑定：

```
im/v1/message.create(msg_type="interactive",
    content={"type":"card","data":{"card_id":"<cardkit返回的card_id>"}})
```

**这是 issue #16084 提出的核心流程**：先 `cardkit.v1.card.create` → 拿 card_id → 再 `im.v1.message.create` 投递。

### 3.2 Card Entity 的三大使用场景

官方 overview 明确卡片实体可嵌入：

1. **聊天消息（Chat messages）** — 最常见，通过 `im/v1/message` 发送
2. **群置顶消息（Group pinned messages）** — 置顶卡片
3. **链接预览（Link previews）** — 会话中的链接自动展开为卡片预览

**链接预览场景是此前 4 篇笔记完全未覆盖的能力**：飞书卡片可与 Open Platform 的链接预览能力关联，让会话消息和群置顶中的特定链接通过卡片实现内容预览，用户无需跳转即可直观了解链接内容。这对 Hermes 的外部资源推送（如笔记链接、文档链接）有直接价值。

---

## 核心发现 4：Hermes 集成 CardKit Streaming 的进展全景（issue #16084）

### 4.1 问题背景

当前 Hermes Gateway Feishu adapter 在 `streaming.enabled: true` 时，回退到 `im.v1.message.update`（纯消息编辑）模拟流式输出，产生三个问题：
- 每次刷新显示灰色「已编辑」标记
- 速率限制严格（~50 QPM/消息）
- 全量重渲染而非逐 token 追加

飞书 CardKit 提供了专为 LLM token 流式设计的 first-class API：打字机效果 + 原生「AI 生成中」指示器 + 无「已编辑」标记。

### 4.2 社区实现方案对比（2026-04 ~ 2026-08）

| 方案 | 类型 | 状态 | Stars/测试 | 核心特点 |
|------|------|------|-----------|----------|
| **PR #25202** (PNGTRID) | 核心 PR | open，未合并 | 21 单元测试 | 三级降级（CardKit v2 → im.message.patch → 新消息）+ `streaming_card: true/false` 开关 + 专用 `send_streaming_card()` |
| **PR #23488** (LetTTGACO) | 核心 PR | closed，未合并 | — | 早期 CardKit 支持 |
| **PR #6365** | 核心 PR | open，未合并 | — | streaming cards 打字机效果 |
| **PR #10311** | 核心 PR | open，未合并 | — | Card Kit 2.0 流式 |
| **baileyh8/hermes-feishu-streaming-card** | Sidecar 插件 | 活跃维护 v3.4.0 | 588 stars，2026-08-06 更新 | 独立进程，hook 补丁 gateway/run.py |

### 4.3 issue #16084 提案的标准实现流程

```
streaming.enabled: true && platform == feishu:
1. 首 chunk: cardkit.v1.card.create（含 streaming text element）
            → im.v1.message.create(msg_type="interactive", card_id)
2. 后续 chunks: cardkit.v1.card_element.content（追加，非替换）
3. 流结束: cardkit.v1.card.settings（关闭 streaming 模式，finalize）
4. 出错降级: im.v1.message.update 原路径
```

**性能对比**：Feishu CardKit 接受 5+ QPS/card，而 message edit 只有 ~50 QPM（即 <1 QPS），吞吐提升 5 倍以上。

### 4.4 lark_oapi SDK 已支持

issue 确认 pinned 的 `lark_oapi` SDK 已包含所需 API：
- `lark_oapi.api.cardkit.v1.resource.card` — `create_card`, `settings`
- `lark_oapi.api.cardkit.v1.resource.card_element` — `content_card_element`（追加 chunk）, `create_card_element`, `update_card_element`

**DingTalk adapter 已有参考实现**：`gateway/platforms/dingtalk.py` 的 `_streaming_cards` 状态机（~9 个调用点），可作为 Feishu 侧的蓝本。

### 4.5 当前阻塞

截至 2026-08-06，issue #16084 仍 open，4 个核心 PR 均未合并。社区已形成两个成熟方案（PR #25202 + sidecar v3.4.0），但维护团队尚未采纳。issue #33854 提议整合两个方案的最佳特性。

---

## 核心发现 5：组件级流式更新的精确语义

### 5.1 card_element.content 端点（PUT）

`PUT /cardkit/v1/cards/:card_id/elements/:element_id/content` 是**组件级文本流式更新**的专用端点。与 8-05 笔记记录的 PATCH `/cardkit/v1/cards/update_async` 不同：

- **update_async**：整卡延时更新，返回 token 用于异步刷新（审批回调场景）
- **card_element.content**：单组件文本追加，LLM 逐 token 流式场景专用

### 5.2 streaming 模式的全局约束

从错误码 300302 确认：streaming 更新模式下，卡片全局属性 `update_multi` **必须为 true**（即非独占模式）。这意味着同一卡片可被多用户同时查看，且流式更新对所有可见者生效。

---

## 实践启发与对 Hermes 生态的影响

### 可立即采纳

1. **feishu-card-table Skill 补充 CardKit v1 API 知识**：当前 Skill 的所有踩坑记录基于 Message API（im/v1），应补充 CardKit v1 的 300xxx 错误码系列和 14 天有效期约束
2. **深度分析报告用 CardKit 分段更新**：当前用 `im.v1.message.update` 全量替换超长内容易触发速率限制（50 QPM），CardKit 的组件级更新（5+ QPS）可支撑更流畅的渐进式报告展示

### 需要追踪（L4）

1. **PR #25202 合并状态**：一旦合并，可直接启用 `streaming_card: true` 获得 native 打字机效果，消除「已编辑」标记
2. **issue #33854 整合方案**：sidecar 的并发 PATCH 序列化、img_key 解析、cron card 投递等特性可能被纳入核心
3. **链接预览卡片**：CardKit overview 提及的链接预览场景，Hermes 笔记推送（bookmark-reader）可用此能力让用户在群聊中直接预览笔记内容

### 不建议立即采纳

- **部署 sidecar baileyh8 方案**：虽然 v3.4.0 成熟（588 stars），但「hook 补丁 gateway/run.py 在 Hermes 更新时脆弱」+「额外进程监控开销」+「配置重复」，不如等核心 PR 合并

---

## 知识缺口（下一轮可补）

1. **Component API 的 element_id 生成规则** — 官方文档未明确 element_id 是自动生成还是调用方指定
2. **batch_update 的原子性保证** — 部分组件更新失败时是否回滚
3. **链接预览卡片的注册流程** — 如何将特定 URL pattern 关联到卡片模板
4. **card entity 的 14 天过期对长会话的影响** — Hermes 多轮对话中引用旧 card_id 的降级处理

---

## 参考来源

- Feishu Card resource overview — https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/cardkit-v1/feishu-card-resource-overview （2025-06-26）
- Create card entity API — https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/cardkit-v1/card/create （2025-07-02）
- Feishu card release notes — https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/feishu-card-release-notes （2025-03-13）
- GitHub issue #16084 — https://github.com/NousResearch/hermes-agent/issues/16084 （8 条评论，2026-04-26 创建）
- PR #25202 — CardKit v2 streaming cards with typewriter effect
- Sidecar repo — https://github.com/baileyh8/hermes-feishu-streaming-card （588 stars，2026-08-06 更新）

## 相关笔记

- `2026-07-30-feishu-card-2.0-architecture-components-streaming-hermes-integration.md` — Card 2.0 架构/组件体系/streaming 基础
- `2026-07-31-feishu-message-api-lifecycle-gateway-routing-identity-model.md` — Message API 12 种 msg_type/Gateway 路由
- `2026-08-04-feishu-card-2.0-callback-protocol-form-container-variables-deep-dive.md` — 回调协议/Form/变量系统
- `2026-08-05-feishu-message-flow-api-streaming-config-v723-slash-commands-incremental.md` — 消息流 API/streaming_config V7.23/延时更新
