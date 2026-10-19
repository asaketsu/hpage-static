# Cloudflare Workers 全栈部署：单 Worker 架构与生产实践

> 探索日期 2026-08-31 | 兴趣等级 L3 | 来源 5（Cloudflare 官方博客 + 官方最佳实践文档 + Digital Applied 2026 指南 + BenchLM 托管选型 + AI Gateway 对比）| 关联笔记：2026-08-30-轻量Web部署-SQLite-on-NFS、2026-08-17-Fly-LiteFS（同域）

## 摘要

Cloudflare Workers 在 2026 年已从边缘 API 处理器收敛为完整全栈平台：单个 Worker 内承载静态资产 + SSR 前端 + API 后端 + 数据库绑定，一次部署全局生效。技术基石是 V8 isolate（非容器）——冷启动 <1ms，300+ 边缘节点 TTFB <50ms。官方已明确"从 Workers 起步"，Pages 进入维护态，未来投资全部转向 Workers。配套存储矩阵（KV/D1/Durable Objects/R2/Hyperdrive）覆盖读缓存、关系型、强一致协调、对象存储、外接数据库池化五类场景。

## 关键发现

1. **Pages→Workers 收敛是官方路线，不是社区猜测**。Cloudflare 官方博客原文："您应从 Workers 着手……今后我们所有的投资、最佳化和功能工作都将专注于改善 Workers"。静态 `_headers`/`_redirects` 文件已支持，Pages 项目可零改动迁移（官方迁移指南）。新项目选 Pages = 主动登上弃船。
2. **V8 isolate 消灭冷启动是结构性优势**。Lambda 冷启动 100ms–1s（容器），Workers <1ms（isolate 已预载运行时，只加载代码）。代价是严格限制：CPU 50ms（免费）/30s（付费）、内存 128MB、无持久 TCP socket——重计算和长连接池化必须外移。
3. **单 Worker 全栈的关键拼图是 Hyperdrive**。Workers 无持久连接池，直连传统数据库是历史难题；Hyperdrive 作为 Cloudflare 网络与数据库间的连接池桥，配合 Smart Placement（Worker 自动向数据库靠近重定位）解决往返延迟。`postgres` + Hono 的 SSR+API 混合应用可在一个部署单元内完成。
4. **KV 最终一致 vs Durable Objects 强一致是硬边界**。KV 全球传播 ~60s，读 <5ms——适合特征开关/API 响应缓存/配置分发；需要协作编辑、游戏房间、限流计数等单实例串行语义时必须用 DO（单实例保证 + 串行请求 + 事务存储 10GB/object + WebSocket）。
5. **渐进发布（Gradual Deployments）进入生产标配**。Versions API 支持流量按 10%→50%→100% 逐步切换，配合 `wrangler deploy --env staging` 的 PR 预览部署，蓝绿/金丝雀在边缘平台原生可用——这是 Pages 时代"只能一次性全量推"的痛点补齐。

## 决策速查

```
选 Workers 还是别的？
├─ 边缘规模 + 长流式生成（LLM streaming） → Workers（BenchLM 2026-07 实测结论）
├─ 短期原型 + 预览 URL                  → Netlify（10s 流式上限）
├─ Agent/队列/超出请求生命周期的常驻进程 → Railway/Fly.io
└─ 重计算（>30s CPU）                    → 传统云

存储绑定怎么配？
├─ 读多写少 + 可容忍 60s 传播 → KV（cacheTtl + expirationTtl）
├─ 关系型 SQL                 → D1（或 Hyperdrive 桥接现有 Postgres/MySQL）
├─ 强一致协调/限流/实时       → Durable Objects（串行单实例）
└─ 大文件/训练数据            → R2（零出口费）
```

官方最佳实践四件套（缺一即埋雷）：

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2026-08-27"        # 新项目设当天，旧项目定期升
compatibility_flags = ["nodejs_compat"]  # node:crypto/buffer/stream，防运行时 import 报错
# secrets 用 `wrangler secret put` 注入，vars 只放非敏感配置
# Env 类型用 `wrangler types` 生成，不手写（防 config/code 漂移）
```

已知坑：Vitest 插件自动注入 `nodejs_compat`，测试通过 ≠ 部署配置正确——上线前必须肉眼确认 wrangler.jsonc 里有该 flag。

## 对工作的价值

- **轻量 Web 部署域补上 Workers 侧视图**：前序笔记聚焦数据层（D1/LiteFS/Turso），本篇补齐计算层，域内"边缘数据库 × 边缘计算"拼图完整。
- **本机 homepage（GitHub Pages）有了备选路径**：Workers 静态资产托管免费（仅 Worker 代码执行计费），若未来需要给笔记站加动态层（搜索 API/访问统计），无需迁移整站，`assets.directory` 直指现有 dist 即可。
- **AI Gateway 结论可复用**：搜索结果显示 Workers AI 适合轻量边缘推理（50+ 模型 REST 调用），但生产级 LLM 网关治理（RBAC/预算/审计）是短板——与 free-model-apis skill 的多线免费 API 策略互补：边缘做轻推理，重路由留本地。

## 行动建议

1. P2：下一个需要公网 URL 的轻工具（如天气 API 缓存代理）用 Workers 而非本机 cloudflared 隧道——免维护隧道进程，免费额度 10 万请求/天足够
2. P2：验证 Workers AI 免费额度内的轻推理可用性（embedding/小模型），作为 free-model-apis 的第四线候选
3. P3：homepage 若加动态功能，评估 `npm create cloudflare -- --framework=astro` 模板而非继续堆 GitHub Pages + 外挂服务

## 关键风险与盲点

- Workers AI 的 GPU 容量与限流政策随负载波动，"50+ 模型目录"≠ 稳定生产 SLA（来源级别：第三方对比文章，未官方验证）
- 免费档 CPU 50ms 限制对任何含正则回溯/JSON 深解析的请求都偏紧，付费档 30s 才接近传统 serverless（官方平台限制文档）
- BenchLM 托管选型含推广链接（Netlify partner link），Netlify 推荐结论打折看待；Workers 结论与多源一致，可信

## 来源

- https://blog.cloudflare.com/zh-tw/full-stack-development-on-cloudflare-workers（官方：前端+后端+数据库单 Worker 化）
- https://developers.cloudflare.com/workers/best-practices/workers-best-practices（官方生产最佳实践）
- https://www.digitalapplied.com/blog/edge-computing-cloudflare-workers-development-guide-2026（2026 开发指南，含 Lambda/Vercel 对比表）
- https://benchlm.ai/blog/posts/best-hosting-platforms-ai-apps（2026-07 AI 应用托管选型实测）
- https://www.cloudflare.com/products/workers-ai（Workers AI 官方产品页）


## 相关笔记

- [2026-08-30 SQLite on NFS 损坏规避](./2026-08-30-轻量Web部署-SQLite-on-NFS损坏规避-WAL陷阱与回滚日志方案.md) — 同系列，WAL 陷阱与回滚方案
- [2026-08-17 Fly LiteFS static-lease 单主](./2026-08-17-轻量Web部署-Fly-LiteFS-static-lease单主.md) — 同系列，边缘数据库主从
- [2026-08-16 Turso Embedded Replicator](./2026-08-16-轻量Web部署-Turso-Embedded-Replic.md) — 同系列，嵌入式同步
- [2026-08-18 Homepage 仪表盘多实例部署](./2026-08-18-Homepage-仪表盘-多实例部署.md) — 部署模式参考
