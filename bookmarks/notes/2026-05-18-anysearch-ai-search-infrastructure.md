# AnySearch — AI Agent 搜索基础设施深度分析

> 日期: 2026-05-18 | 分类: [[竞品分析]] [[AI搜索]] [[Agent基础设施]]
> 来源: https://github.com/anysearch-ai | https://anysearch.com

## 摘要

AnySearch 是 2026 年 5 月新发布的 AI Agent 专用搜索平台。核心定位不是给人用的搜索引擎，而是给 AI Agent 提供结构化、高质量信息的 API 基础设施。匿名免费可用，支持 23 个垂直领域，通过 Skill/MCP/API 三种方式集成。Benchmark 显示准确率 76.4%（Brave 58-68%），延迟比 Brave 快 31%。

## 项目画像

| 维度 | 内容 |
|------|------|
| 组织 | anysearch-ai (GitHub) |
| 仓库 | anysearch-skill (297⭐) + anysearch-mcp-server (288⭐) |
| 总星 | 585 |
| 团队 | 4 人联合创始人（Guanqun/CEO, Morecry/CTO, Grant/VPE, Aiden/CISO） |
| 注册地 | 香港 |
| 发布日 | 2026-05-11 (PRNewswire) |
| 官网 | https://anysearch.com |
| 定价 | 免费匿名层 + 付费 API Key |

## 核心架构

```
AI Agent / 人类
    │
    ├─ Skill (CLI) ──→ JSON-RPC 2.0 ──→ api.anysearch.com/mcp
    │
    ├─ MCP Server ──→ Streamable HTTP ──→ api.anysearch.com/mcp
    │                  SSE (via proxy)
    │                  stdio (via proxy)
    │
    └─ REST API ──→ POST /v1/search ──→ api.anysearch.com
                          │
                          ▼
                   Smart Intent Router
                   (自动路由到最优数据源)
                          │
                 ┌────────┼────────┐
                 ▼        ▼        ▼
             通用搜索  垂直搜索  URL提取
             (web)    (23域)   (extract)
```

## 技术细节

### API 端点

| 端点 | 协议 | 用途 |
|------|------|------|
| `POST /v1/search` | REST | 搜索（匿名/认证） |
| `POST /mcp` | JSON-RPC 2.0 | MCP 协议（搜索+提取+批量） |
| `POST /v1/extract` | REST | URL 内容提取 |

### 请求参数

| 参数 | 说明 |
|------|------|
| query | 搜索查询（必填） |
| max_results | 结果数 1-100（默认 10） |
| domains | 域过滤 ["code","academic"] |
| tags | 子域标签 {domain}.{sub_domain} |
| content_types | 类型过滤 ["web","news","code"] |
| zone | 区域: cn / intl |
| freshness | 时效: day/week/month/year |
| constraint.from/to | 时间范围 (RFC3339) |

### 响应格式

```json
{
  "results": [{
    "title": "...",
    "url": "...",
    "description": "摘要",
    "content": "全文",
    "score": 0.87,
    "quality_score": 0.95,
    "source": "web",
    "published_at": "2024-02-06T00:00:00Z"
  }],
  "metadata": {
    "total_results": 1,
    "search_time_ms": 342,
    "routes_queried": 2,
    "request_id": "req_abc123"
  }
}
```

### 23 个垂直领域

code, tech, fashion, travel, home, ecommerce, gaming, film, music, finance, academic, legal, business, ip, security, education, health, religion, geo, environment, energy, ugc + 通用搜索

### Skill 多语言 CLI

| 优先级 | 运行时 | 文件 | 依赖 |
|--------|--------|------|------|
| 1 | Python 3.6+ | anysearch_cli.py | requests |
| 2 | Node.js 12+ | anysearch_cli.js | 无（内置 https） |
| 3 | PowerShell 5.1+ | anysearch_cli.ps1 | 无 |
| 4 | Bash 4+ | anysearch_cli.sh | curl/jq |

## Benchmark 数据

### 准确率（300 题，LLM: glm-5.1）

| 数据集 | AnySearch | Brave | Parallel |
|--------|-----------|-------|----------|
| FreshQA | 80.0% | - | - |
| WebwalkerQA | 65.2% | 46.8% | 61.0% |
| Frames | - | - | - |
| 总体 | 76.4% | ~60% | ~65% |

### 延迟

| 数据集 | AnySearch | Brave | Parallel |
|--------|-----------|-------|----------|
| WebwalkerQA | 76.5s | 133.0s | 145.6s |
| 总体 | 47.8s | 68.9s | 74.4s |

### 实景评分（Claude Opus 4.6 评分）

| 场景 | AnySearch | Brave |
|------|-----------|-------|
| 安全工程师告警分析 | 9.5 | 8.2 |
| 开发项目代码搜索 | 9.5 | 7.8 |
| 商务旅行实时决策 | 8.0 | 5.5 |
| PM 竞品调研 | 9.2 | 8.2 |
| 公共卫生疾病负担 | 8.5 | 8.0 |
| 总分 | 8.9/10 | 7.5/10 |

## 与竞品对比

| 维度 | AnySearch | Tavily | Brave Search API | Serper |
|------|-----------|--------|-------------------|--------|
| 定位 | Agent 专用 | Agent 专用 | 通用+API | 通用 Google API |
| 免费层 | 匿名可用 | 1000次/月 | 2000次/月 | 2500次/月 |
| 垂直域 | 23个 | 无 | 无 | 无 |
| 结构化输出 | ✅ 原生 | ✅ | 部分 | 部分 |
| 质量评分 | quality_score | 无 | 无 | 无 |
| MCP 支持 | ✅ 原生 | ❌ | ❌ | ❌ |
| Skill 支持 | ✅ 4语言CLI | ❌ | ❌ | ❌ |
| URL 提取 | ✅ 内置 | ✅ | ❌ | ❌ |

## 验证结果

### 实测（2026-05-18, Jetson Orin）

```bash
# JSON-RPC 搜索（匿名）
curl -X POST https://api.anysearch.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search","arguments":{"query":"Python async framework comparison 2025","max_results":2}}}'

# 结果: ✅ 2 条高质量结果, 1528ms
# 内容: FastAPI vs Starlette vs Quart 详细对比 + 2025 Python 框架排行
```

## 核心洞察

### 1. Agent-Native 不是噱头

传统搜索返回 HTML + SEO 噪音。AnySearch 返回结构化 JSON，带 quality_score 和 source attribution。这对 Agent 来说确实减少了 token 浪费——不需要 Agent 自己解析 HTML、过滤广告、判断信息可信度。

### 2. 垂直域是护城河

23 个垂直域（金融、学术、法律、安全...）不是简单分类，而是每个域有专门的数据源、子域标识符（Stock:/CVE:/DOI:）、和优化后的检索策略。这是通用搜索做不到的。

### 3. 匿名免费是增长黑客

零门槛试用 → 依赖形成 → 付费转化。比 Tavily 的"注册才给 Key"更激进一步。

### 4. 多语言 CLI 是工程品味

Python > Node.js > PowerShell > Bash，自动检测 + runtime.conf 持久化。这个设计模式值得学习——不是所有 Agent 环境都有 Python。

## 借鉴点

### ① 已落实

| 借鉴点 | 落实动作 |
|--------|----------|
| AnySearch 作为搜索降级节点 | search-fallback-chain skill 新增 Layer 2.5 |
| 多语言 CLI 路由模式 | 参考设计，已有类似模式 |
| Agent-Native 搜索理念 | 写入笔记，搜索工具选型参考 |

### ② 有价值（备用）

- Smart Intent Routing 自动路由设计
- 23 垂直域分类法
- quality_score 质量评分机制
- runtime.conf 持久化模式

### ③ 知识库

- 公司信息（香港，4人团队）
- Benchmark 数据
- 竞品格局

## 关联

- [[搜索服务降级链]] — 已加入 AnySearch 作为 Layer 2.5
- [[AI Agent 工具生态]] — MCP/Skill 双模式集成
- [[Hermes 搜索工具]] — web_search/web_extract 的替代方案

## 预判

**短期（1-3月）**: Stars 突破 1000，社区初步形成。免费层吸引大量 Agent 开发者。

**中期（3-6月）**: 竞品跟进垂直域。定价模型分化（按量/按域/按并发）。MCP 协议成为标准集成方式。

**长期（6-12月）**: 面临 Brave/Tavily 直接竞争。护城河在于数据源质量和垂直域深度。如果团队只有 4 人，执行速度是风险。
\n## 相关笔记\n\n- [[2026-04-01-Ontology驱动的AI知识引擎]]\n- [[2026-04-02-Agent Skills才是关键抽象层]]\n- [[2026-04-05-Hermes-Agent-competitor-analysis]]\n- [[2026-04-05-Karpathy-LLM-Wiki-second-brain]]
