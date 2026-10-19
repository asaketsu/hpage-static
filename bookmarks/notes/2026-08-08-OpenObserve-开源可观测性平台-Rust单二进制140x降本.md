# OpenObserve — 开源可观测性平台（Rust 单二进制，140x 存储成本降低）

> **来源**：[github.com/openobserve/openobserve](https://github.com/openobserve/openobserve)
> **官网**：[openobserve.ai](https://openobserve.ai)
> **Stars**：20.6K · **Forks**：988 · **License**：AGPL-3.0
> **语言**：Rust（后端）+ TypeScript（前端）
> **创建日期**：2023-02-02 · 最后更新：2026-08-08

---

## 一句话定义

> **开源的 Datadog/Splunk/Elasticsearch 替代品**——统一日志、指标、链路追踪、前端监控和 LLM 可观测性。Rust 单二进制部署，比 Elasticsearch 存储**成本低 140 倍**，10 倍易用性，PB 级规模。

---

## 一、核心特性

### 1.1 功能矩阵

| 功能 | 描述 | 对标产品 |
|------|------|---------|
| **日志** | SQL + 全文检索，PB 级日志搜索 | Elasticsearch / Splunk / Loki |
| **指标** | Prometheus 兼容采集和存储 | Prometheus / Mimir |
| **链路追踪** | 分布式追踪，OpenTelemetry 兼容 | Jaeger / Tempo |
| **前端监控 (RUM)** | Real User Monitoring，会话回放+错误追踪 | Datadog RUM / Sentry |
| **LLM 可观测性** | Prompt/Token/延迟/成本追踪 | LangFuse / Helicone |
| **Dashboard** | 交互式仪表盘 | Grafana |
| **告警** | 条件告警 + 多渠道通知 | AlertManager |
| **Pipeline** | 无代码数据摄取管道，摄入时转换和路由 | Logstash / Vector |

### 1.2 核心优势

| 优势 | 说明 | 技术实现 |
|------|------|---------|
| **140x 存储成本降低** | 相比 Elasticsearch | Rust 列式存储 + 压缩 |
| **单二进制部署** | 一个文件启动 | Rust 编译为单一可执行文件 |
| **10x 易用性** | 相比 ELK Stack | 内置 UI + Web 管理界面 |
| **PB 级规模** | 单节点和 HA 两种模式 | 分离存储（本地/S3/MinIO） |
| **SIMD 优化** | AVX512 (Intel) / NEON (ARM) | SIMD 加速查询 |

---

## 二、架构设计

### 2.1 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| **后端** | Rust | 高性能、内存安全 |
| **前端** | TypeScript + Vue | 管理界面 |
| **存储** | 本地/S3/MinIO/GCS/Azure Blob | 分离存储架构 |
| **摄取** | OpenTelemetry / Prometheus / curl / Filebeat | 多协议摄入 |
| **查询** | SQL + 全文检索 | 内置 SQL 引擎 |

### 2.2 部署模式

| 模式 | 适用场景 | 架构 |
|------|---------|------|
| **单节点** | 开发/测试/小规模生产 | 单二进制 + 本地存储/S3 |
| **高可用 (HA)** | 生产环境 | EKS/AKS/GKE 多副本 + 共享存储 |

### 2.3 数据流

```
数据源 → OpenTelemetry/Prometheus/curl
  → 摄取层（HTTP API / OTLP）
  → Pipeline（可选：转换/过滤/路由）
  → 存储层（本地/S3/MinIO，列式压缩）
  → 查询层（SQL + 全文检索）
  → 可视化（Dashboard/告警/搜索）
```

---

## 三、快速部署

### 3.1 单二进制部署（最简）

```bash
# Linux/macOS
ZO_ROOT_USER_EMAIL="root@example.com" \
ZO_ROOT_USER_PASSWORD="Complexpass#123" \
./openobserve

# 访问 http://localhost:5080
```

### 3.2 Docker 部署

```bash
docker run -v $PWD/data:/data \
  -e ZO_DATA_DIR="/data" \
  -p 5080:5080 \
  -e ZO_ROOT_USER_EMAIL="root@example.com" \
  -e ZO_ROOT_USER_PASSWORD="Complexpass#123" \
  o2cr.ai/openobserve/openobserve-enterprise:latest

# ARM 优化版（带 NEON SIMD）
# 使用 latest-simd tag
```

### 3.3 Kubernetes 部署

```bash
kubectl create namespace openobserve
kubectl apply -f https://raw.githubusercontent.com/zinclabs/openobserve/main/deploy/k8s/statefulset.yaml
kubectl -n openobserve port-forward svc/openobserve 5080:5080
```

### 3.4 摄取数据

```bash
# 加载示例 K8s 日志
curl -L https://zinc-public-data.s3.us-west-2.amazonaws.com/zinc-enl/sample-k8s-logs/k8slog_json.json.zip -o k8slog_json.json.zip
unzip k8slog_json.json.zip

# 推送到 OpenObserve
curl -u "root@example.com:Complexpass#123" \
  -H "Content-Type: application/json" \
  http://localhost:5080/api/default/default/_json \
  -d "@k8slog_json.json"

# 返回: {"code":200,"status":"ok","records":1000}
```

### 3.5 查询数据

```sql
-- 在 Web UI 的 Logs 中运行 SQL
-- 全部日志
SELECT * FROM default LIMIT 100

-- 按级别过滤
SELECT * FROM default WHERE level='error'

-- 全文检索
match_all('error')

-- 时间聚合
SELECT histogram(_timestamp, '1 minute') AS bucket, count(*) AS cnt
FROM default GROUP BY bucket ORDER BY bucket
```

---

## 四、与竞品对比

| 维度 | OpenObserve | Elasticsearch | Datadog | Grafana LGTM |
|------|-------------|---------------|---------|-------------|
| **存储成本** | 1x | 140x | SaaS 定价 | 中等 |
| **部署复杂度** | 单二进制 | 多组件集群 | SaaS | 多组件 |
| **统一日志+指标+追踪** | ✅ 原生 | 需分别搭建 | ✅ | ✅ (Loki+Mimir+Tempo) |
| **LLM 可观测性** | ✅ 内置 | ❌ | ✅ (附加产品) | ❌ |
| **前端监控 (RUM)** | ✅ 内置 | ❌ | ✅ | ❌ |
| **Pipeline** | ✅ 无代码 | 需 Logstash | ✅ | 需 Vector |
| **SQL 查询** | ✅ | ❌ (DSL) | ✅ | LogQL/PromQL |
| **开源协议** | AGPL-3.0 | Elastic License | 闭源 | Apache-2.0 |
| **语言** | Rust | Java | — | Go |
| **ARM/SIMD 优化** | ✅ NEON | 部分 | — | 部分 |

---

## 五、LLM 可观测性（特色功能）

OpenObserve 内置了 LLM 应用监控，无需额外工具：

| 监控维度 | 说明 |
|---------|------|
| **Prompt 追踪** | 记录每次 LLM 调用的 prompt 和 completion |
| **Token 用量** | 输入/输出 token 数和成本 |
| **延迟** | 首字延迟(TTFT)和完整响应延迟 |
| **错误率** | API 调用失败率和重试 |
| **模型对比** | 不同模型的成本和性能对比 |

这对 Hermes Agent 这样的 LLM 应用非常有价值——可以实时追踪每次 LLM 调用的 token 消耗和成本。

---

## 六、与 Hermes Agent 的结合价值

### 6.1 可直接使用的场景

| 场景 | 实现方式 |
|------|---------|
| **Hermes 日志统一** | 将 Hermes Gateway 日志推送到 OpenObserve，替代 grep + journalctl |
| **Agent 可观测性** | 追踪每个 Agent 的工具调用链路（Traces） |
| **LLM 成本监控** | 通过 LLM Observability 追踪每次模型调用的 token 和成本 |
| **Cron 任务监控** | Cron 执行日志推送到 OpenObserve，设置告警 |
| **Homepage/CDN 监控** | RUM 监控前端加载性能 |

### 6.2 部署建议（Jetson Orin Nano 环境）

| 维度 | 评估 |
|------|------|
| **CPU** | ARM64 原生支持（NEON SIMD） |
| **内存** | 单节点模式 1-2GB 足够 |
| **存储** | 可用本地 NVMe 或挂载 NFS（Jetson 已有 NFS） |
| **部署方式** | Docker 或单二进制 |
| **资源消耗** | Rust 单二进制非常轻量 |

### 6.3 对比现有方案

| 现有方案 | OpenObserve 优势 |
|---------|-----------------|
| `journalctl` + grep | 全文搜索 + SQL + Dashboard |
| `cron-log-analysis` Skill | 实时告警 + 可视化 |
| `observability-dashboard` Skill | 统一日志+指标+追踪 |
| `error-monitoring` Skill | 结构化错误追踪 + 告警 |

---

## 七、结合最新研究与技术变化

### 1. 与 YC QM 多人 Agent 工作台的关联

QM 的 `audit` 模块负责审计所有 Agent 操作。OpenObserve 可以作为 QM 的**可观测性后端**——将 Agent 的 `execute` 工具调用推送到 OpenObserve，实现端到端的操作追踪。

### 2. 与 Coding Agent Harness 解剖学的关联

Mastra 文章分析 Coding Agent 的 27 分钟架构中提到"可观测性是 Harness 工程的核心"。OpenObserve 的 Traces + LLM Observability 正好满足这个需求——追踪 Agent 的每一步决策链路。

### 3. 与 Hermes 可观测性 Skill 的关联

Hermes 已有 `observability-dashboard` 和 `error-monitoring` Skill，但缺少一个统一的存储和查询后端。OpenObserve 可以作为这个后端——把分散的日志分析能力统一到一个平台。

---

## 八、学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **LLM 可观测性内置** | 在 Hermes 中追踪每次 LLM 调用的 token/cost | 高 |
| **Rust 单二进制** | 性能敏感组件可考虑 Rust | 中 |
| **无代码 Pipeline** | 数据摄取管道可视化 | 中 |
| **SQL 查询日志** | 比 grep 更强大的日志分析 | 高 |
| **140x 存储优化** | 列式存储 + 压缩对 Hermes 日志同样适用 | 中 |

---

## 九、趋势判断

1. **可观测性市场正在被 Rust 重写**——OpenObserve 用 Rust 实现了 ELK Stack 的核心功能，存储成本低 140x
2. **LLM 可观测性是新刚需**——随着 Agent 应用爆发，追踪 LLM 调用链路和成本成为标配
3. **统一平台替代碎片化工具栈**——一个平台覆盖日志+指标+追踪+RUM+LLM，而非分别搭建 ELK+Prometheus+Jaeger+Sentry
4. **单二进制部署降低门槛**——Rust 编译的单文件部署比 JVM 生态更轻量
5. **ARM 原生支持**——OpenObserve 的 SIMD 镜像明确支持 NEON (ARM)，对边缘部署友好

---

## 📎 关键资源

| 资源 | 链接 |
|------|------|
| 官网 | [openobserve.ai](https://openobserve.ai) |
| 文档 | [openobserve.ai/docs](https://openobserve.ai/docs/) |
| 快速开始 | [Quickstart](https://openobserve.ai/docs/quickstart/) |
| Cloud | [cloud.openobserve.ai](https://cloud.openobserve.ai) |
| 下载 | [openobserve.ai/downloads](https://openobserve.ai/downloads) |
| Slack 社区 | [short.openobserve.ai/community](https://short.openobserve.ai/community) |
| GitHub | [github.com/openobserve/openobserve](https://github.com/openobserve/openobserve) |

---

## 相关笔记

- [Codex接GitHub-仓库监控飞书机器人](2026-08-06-Codex接GitHub-仓库监控飞书机器人.md)
- [AI-Agent自进化与记忆系统全景](2026-08-08-AI-Agent自进化与记忆系统全景.md)
- [Agent可观测性仪表盘](../../uclaw/bookmarks/notes/2026-06-28-Agent可观测性仪表盘.md)

---

*笔记创建：2026-08-08 · 来源：OpenObserve GitHub + 官方文档*
