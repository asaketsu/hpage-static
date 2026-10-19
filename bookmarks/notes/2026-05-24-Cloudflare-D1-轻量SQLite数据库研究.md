# Cloudflare D1 轻量 SQLite 数据库研究

> **来源**：Cloudflare 官方文档 + 社区评测 · 2026-05-24
> **笔记ID**：d1-sqlite-research-2026
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **评分**：⭐4/5

## 摘要

Cloudflare D1 是基于 SQLite 的无服务器 SQL 数据库，深度集成 Workers/Pages 生态。单库 10GB、免费额度慷慨（日读 500 万行）、Time Travel 30 天回滚、全局读复制（Beta），是轻量网站部署的理想选择。主要竞争者为 Turso（libSQL 边缘数据库），两者各有侧重。本文梳理 D1 核心特性、定价、限制、竞争对比及实际部署架构。

## 核心内容

### 1. D1 是什么

D1 是 Cloudflare 基于 SQLite 引擎构建的托管关系数据库，直接从 Workers 脚本通过绑定（Binding）访问，无需独立连接池或驱动。核心卖点：

- **零运维**：无服务器，按行计费，空闲不花钱
- **SQLite 兼容**：标准 SQL，支持 ORM（Drizzle/Prisma 等）
- **Time Travel**：自动保留 30 天操作历史，可回滚到任意时间点
- **全局读复制（Beta）**：通过 Sessions API 实现就近读取，顺序一致性保证
- **迁移系统**：wrangler migrations 管理版本化 schema

### 2. 定价与免费额度

| 维度 | Free 计划 | Workers Paid（$5/月起） |
|------|-----------|------------------------|
| 读行数 | 500 万/天 | 250 亿/月 含 |
| 写行数 | 10 万/天 | 5000 万/月 含 |
| 存储 | 5 GB 总计 | 单库 10 GB，账户 1 TB |
| 数据库数 | 10 个 | 50,000 个 |
| 每次调用查询数 | 50 | 1,000 |
| 超额读 | - | $0.001/百万行 |
| 超额写 | - | $1.00/百万行 |
| 超额存储 | - | $0.75/GB/月 |

**关键洞察**：Free 计划对小型网站足够。500 万行日读 + 5GB 存储能支撑日均几千 PV 的站点。Paid 计划 $5/月起步，含 250 亿行月读，性价比极高。

### 3. 技术限制

- **单库上限 10GB**：超过需分库（per-tenant sharding）
- **行级计费**：全表扫描代价高，索引是必须的
- **写入延迟**：主库单点写入，读复制仅限读
- **Workers 绑定模型**：只能从 Workers/Pages 访问，不能外部直连
- **CPU 限制**：单次调用最多 50/1000 查询
- **Time Travel 仅保留 30 天**：长期归档需导出到 R2

### 4. D1 vs Turso 对比

| 维度 | Cloudflare D1 | Turso |
|------|--------------|-------|
| 引擎 | SQLite | libSQL（SQLite 分支） |
| 部署 | Workers 专属 | 任意平台（HTTP API） |
| 免费额度 | 500 万读/天，5GB | 9GB 存储，500 数据库，10 亿行读/月 |
| 单库上限 | 10 GB | 无明确上限 |
| 全局复制 | 读复制 Beta | 原生边缘复制，30+ 区域 |
| 数据导入 | dump SQL 后导入 | CLI 直接上传 .sqlite 文件 |
| 外部访问 | 仅 Workers | HTTP API，任何语言可连 |
| 定价 | $5/月起 | 免费层更慷慨，Scalable $29/月 |
| 嵌入式副本 | 不支持 | 支持嵌入式副本（本地读） |
| 生态 | Cloudflare 全家桶 | 独立，跨平台 |

**结论**：如果网站已经部署在 Cloudflare（Workers/Pages），D1 是最无缝的选择。如果需要跨平台或更强的边缘复制，Turso 更优。

### 5. 部署架构建议

轻量网站推荐的 Cloudflare 全家桶架构：

```
用户请求 → Cloudflare CDN
         → Workers（Edge 计算）
           → D1（SQLite 数据库）
           → R2（对象存储/静态资源）
           → KV（配置缓存）
```

**最小可行方案**：
- Pages 静态前端 + Workers API + D1 数据库
- wrangler 管理迁移和部署
- 本地开发用 `--local` flag，SQLite 文件在 `.wrangler/`

### 6. 关键操作命令

```bash
# 创建数据库
npx wrangler d1 create my-site-db

# 创建迁移
npx wrangler d1 migrations create my-site-db init_schema

# 本地执行迁移
npx wrangler d1 migrations apply my-site-db --local

# 远程执行迁移
npx wrangler d1 migrations apply my-site-db --remote

# 查询
npx wrangler d1 execute my-site-db --remote --command="SELECT * FROM users LIMIT 10"

# 导入 SQL
npx wrangler d1 execute my-site-db --remote --file=./seed.sql

# Time Travel 回滚
npx wrangler d1 time-travel restore my-site-db --timestamp="2026-05-20T10:00:00Z"
```

### 7. Workers 代码示例

```javascript
export default {
  async fetch(request, env) {
    // 简单查询
    const { results } = await env.DB.prepare(
      "SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC LIMIT 20"
    ).bind("published").all();

    return Response.json(results);
  }
};
```

wrangler.toml 配置：

```toml
name = "my-site"
main = "src/index.js"

[[d1_databases]]
binding = "DB"
database_name = "my-site-db"
database_id = "xxx-xxx-xxx"
```

## 关键概念

- **Binding（绑定）**：D1 通过 wrangler.toml 绑定到 Worker，代码中通过 `env.DB` 访问
- **Sessions API**：读复制场景下保证顺序一致性的 API，替代直接 prepare() 调用
- **Time Travel**：D1 内置的 PITR（Point-In-Time Recovery），自动记录 WAL 日志
- **Smart Placement**：Cloudflare 自动将 Worker 放置在离 D1 主库最近的位置以降低延迟
- **行级计费**：按查询实际扫描/写入的行数计费，非按请求

## 能力边界

**适合**：博客、CMS、小型 SaaS、API 后端、个人项目、内容站点
**不适合**：高并发写入（主库单点）、需要外部直连 DB 的场景、超过 10GB 的单库需求、复杂事务（SQLite 限制）

## 最佳实践

1. **建索引**：没有索引的全表扫描按行数计费，代价高
2. **用 prepared statements**：`.prepare().bind()` 防注入且可复用
3. **分库策略**：多租户按 tenant 分库，避开 10GB 限制
4. **读复制**：读多写少场景启用 Sessions API + 读复制
5. **本地开发**：`--local` 用本地 SQLite，`--remote` 操作线上
6. **迁移管理**：所有 schema 变更走 migrations，不手动改

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 行级计费模型 | D1 按扫描/写入行数计费，非按请求 | Hermes 工具调用的成本监控可借鉴"按实际消耗"思路 | 考虑在 token 消耗统计中加入行级成本估算 |
| 2 | Time Travel PITR | 30 天自动回滚，零配置 | 当前 memory/MEMORY.md 无版本回滚能力 | 可用 git 自动 commit 实现简易 PITR，cron 定期 commit |
| 3 | Binding 模式 | Worker 通过绑定访问 D1，零连接管理 | Hermes 的 MCP 工具发现机制类似，但更动态 | skill 加载可参考 binding 的声明式配置方式 |
| 4 | 迁移版本化 | SQL 文件版本化管理 schema 演进 | Memory 三层架构的 schema 变更需要类似机制 | Memory 架构实现中加入 schema version 字段 |
| 5 | Smart Placement | 自动将计算放到离数据最近的位置 | subagent 调度可借鉴"就近执行"思路 | delegate_task 可考虑按 task 类型选择最优模型 |

## 🔗 RAG / Wiki 联动

### 当前状态
- wiki-knowledge-base: 正常运行，PageIndex + RAG 双引擎
- RAG: 关键词+语义向量检索就绪
- Memory: 三层架构实现中（二层 blocked）

### 改进方案
1. 将本文核心技术参数写入 MEMORY.md（D1 定价/限制速查）
2. 后续建站时 D1 部署流程提炼为独立 skill
3. Turso vs D1 对比矩阵加入 Wiki 索引

### 已执行操作
- ✅ 研究完成，笔记已生成
- ⏳ 网站部署时提炼 skill
- ⏳ 核心参数写入 Memory

## 相关笔记
