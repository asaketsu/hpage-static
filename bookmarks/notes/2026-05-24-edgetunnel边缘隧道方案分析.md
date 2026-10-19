# edgetunnel 分析笔记 — CF Workers/Pages 边缘隧道方案

> **来源**：渡边君(@JiaweiShen2568) · X/Twitter · 2026-05-20
> **原文**：https://x.com/JiaweiShen2568/status/2057065604197355981
> **关联项目**：https://github.com/cmliu/edgetunnel
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动
> **关联**：[[2026-05-24-html-ppt-skill分析融合]] [[network-protocol-attacks]]

## 摘要

渡边君在推文推荐了 edgetunnel 项目（35k⭐，32k forks），这是一个基于 Cloudflare Workers/Pages 的边缘隧道解密方案。推文核心观点："通过域名免费翻墙，油管轻松4K"——不需要 VPS，只需一个域名 + CF 免费套餐即可搭建代理节点，支持 VLESS/Trojan/Shadowsocks 协议，内置管理面板和订阅系统。

## 核心内容

### 1. 推文要点

渡边君原文大意：之前买了 RD 家 VPS（22刀/年，3T/月），觉得已经够划算了。结果在 GitHub 发现 edgetunnel，只要有域名就能基于 CF 搭建免费翻墙节点，油管轻松 4K。

### 2. edgetunnel 技术架构

**定位**：CF Workers/Pages 平台的边缘计算隧道方案（非传统 VPS 部署）

**核心设计**：
- 单文件 `_worker.js`（约 1 个超大文件，全量逻辑内联）
- CF Workers 运行时，无需服务器
- WebSocket / gRPC / XHTTP 三种传输协议
- VLESS + Trojan + Shadowsocks 协议栈
- KV 存储管理面板配置和日志
- 内置订阅生成器（Clash/Sing-box/Surge 适配）

**部署方式**（三选一）：
1. Workers 部署 — 粘贴 _worker.js + 绑定 KV + 自定义域
2. Pages 上传（推荐）— 上传 main.zip + KV + CNAME
3. Pages + GitHub — Fork 后自动部署

**关键技术参数**：
- 上行合包 16KB，队列最大 16MB / 4096 条目
- Grain 协议下行 32KB 包，TCP 并发拨号 4 路
- 支持 ProxyIP / SOCKS5 / HTTP 链式代理
- 中文变量名（非主流但功能性强）

### 3. 项目热度与生态

| 指标 | 数值 |
|------|------|
| Stars | 35,006 |
| Forks | 32,324 |
| 创建时间 | 2023-12-27 |
| 最近更新 | 2026-05-18 |
| 语言 | JavaScript |
| 版本 | 2.1 (2026-05-17) |
| 提交数 | 1,260 |
| 文件数 | 仅 9 个 |

fork 数接近 star 数（92%），说明大量用户 fork 后自行部署，是非常典型的"实用工具型"项目。

### 4. 技术亮点

**a) 零成本运行**
- CF Workers 免费套餐：10 万请求/天
- CF Pages 无限静态部署
- 唯一成本：一个域名（甚至可以用免费域名）

**b) 管理面板**
- 内置 Web 管理后台（/admin）
- Cookie 认证 + MD5 哈希
- 实时配置修改、日志查看、流量统计
- CF Usage 查询集成

**c) 订阅系统**
- 自动生成多客户端订阅（Clash/v2ray/Surge/Sing-box）
- URL 路径动态切换代理方案（proxyip= / socks5= / http=）
- BEST_SUB 模式：优选订阅生成器

**d) 伪装能力**
- 默认伪装为 CF 错误页面
- 可自定义伪装 URL
- URL 变量设为 `1101` 时返回 CF 1101 错误

### 5. 代码质量观察

**值得关注的设计**：
- 单文件架构：所有逻辑在 `_worker.js`，简单粗暴但部署方便
- 中文变量名：`管理员密码`、`反代IP`、`缓存SOCKS5白名单` 等，降低中文用户阅读门槛
- 代码头部有大段多语言"安全声明"（明显是为了绕过自动化检测）
- 全局状态管理：大量 `let` 顶级变量，Worker 隔离实例模式

**安全注意事项**：
- 项目头部有免责声明："仅供教育、科学研究及个人安全测试"
- 代码中的多语言安全声明看起来是为了对抗 CF 的代码审查/自动检测
- 管理员密码通过环境变量传递，Cookie 认证用 MD5 哈希（非最强方案）
- 中文变量名让代码审计工具可能遗漏

## 能力边界

**适用**：个人使用、低流量场景（CF 免费套餐限制）、临时需求
**不适用**：高并发、企业级、需要稳定 IP 的场景
**风险**：CF 可能随时封禁此类用途、协议安全性依赖 VLESS/Trojan 实现

## 最佳实践

1. 优先 Pages 上传部署（最稳定）
2. 绑定 KV 用于持久化配置和日志
3. 设置强 ADMIN 密码
4. 配置 ProxyIP 优化延迟
5. 用 BEST_SUB 模式生成优选订阅

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | 边缘计算架构 | CF Workers/Pages 免费运行代理 | Serverless 平台可用于多种隧道/代理场景，理解 CF Workers API 设计模式 | 知识储备，理解 CF Workers fetch handler 模式 |
| 2 | 订阅系统设计 | 自动生成多客户端订阅（Clash/v2ray/Surge） | 多客户端适配的订阅生成模式可借鉴到其他配置分发场景 | 知识储备 |
| 3 | 管理面板内置 | Web 管理后台 + KV 存储 + Cookie 认证 | 理解 Serverless 环境下的轻量管理面板设计 | 知识储备 |
| 4 | 链式代理 | ProxyIP / SOCKS5 / HTTP 多层代理 | 代理链降级策略可借鉴到我们的搜索降级链设计 | 概念映射 |
| 5 | 伪装能力 | CF 错误页面伪装 + 自定义 URL | Serverless 函数伪装技巧，可用于 red-team 场景 | 关联 red-teaming skills |

**三问自检**：
1. **有无可复用方法？** — CF Workers 的 fetch handler + KV 模式有参考价值，但不直接适用当前系统。链式代理降级概念可映射到搜索降级链。
2. **有无可优化配置？** — 暂无，与当前 Agent 系统无直接配置关联。
3. **有关键事实？** — edgetunnel 项目定位和技术方案作为知识储备记入笔记。

## 🔗 RAG / Wiki 联动

### 当前状态
- 本笔记为纯知识分析，与 red-teaming skills 中 network-protocol-attacks / tunneling-and-pivoting 概念相关
- 与我们系统的搜索降级链设计有概念映射（链式代理 → 降级链）

### 改进方案
1. 链式代理降级概念可映射到 search-fallback-chain skill 的多级降级策略
2. CF Workers 运行时模式可参考用于 future edge deployment 场景

### 已执行操作
- ✅ 知识分析完成，无直接系统改动
- ✅ 笔记归档

## 相关笔记
- [网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [网络安全-security-automation](2026-05-15-网络安全-security-automation.md)
- [网络安全-security-automation](2026-05-18-网络安全-security-automation.md)
- [Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测](2026-05-23-Domain-Camouflaged-Injection-Attacks-域伪装注入绕过多Agent检测.md)
