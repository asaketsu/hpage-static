# Orbien — Rust+Tokio 轻量内网穿透工具

> 来源：https://github.com/orbien-org/orbien
> 日期：2026-08-14
> 版本：v2.1.0 | License: Apache-2.0 | 语言: Rust

---

## 一、项目定位

**Orbien 是一个轻量、高性能、安全的内网穿透工具**，对标 frp，但用 Rust 重写，二进制体积仅 ~5MB（服务端+客户端各一个二进制）。

核心卖点：
- **Rust + Tokio** 异步运行时，零 GC、内存极低且稳定
- **5MB 二进制**（对比 frp Go 编译 ~10MB+）
- **四种传输协议**：TCP / QUIC / KCP / WebSocket
- **四种代理协议**：TCP / UDP / HTTP / HTTPS
- **Tauri 桌面客户端** <10MB（替代 CLI）
- **服务端 Web 管理界面**

---

## 二、技术架构

### 2.1 项目结构

```
orbien/
├── core/           # 核心库（协议、隧道、加密、多路复用）
├── client/         # 客户端二进制
├── server/         # 服务端二进制（含 Web Dashboard）
├── server-ui/      # 服务端 Web 界面（前端）
├── desktop/        # Tauri 桌面客户端（Rust + Web前端）
├── client-java/    # Java 客户端（Android 平台）
├── docker/         # Docker 部署文件
├── docs/           # 文档站
├── pack/conf/      # 示例配置
└── scripts/        # 构建/发布脚本
```

### 2.2 技术栈深度解析

基于 Cargo.toml workspace 依赖分析：

| 层级 | 依赖 | 用途 |
|------|------|------|
| **异步运行时** | tokio 1 (full) + tokio-util 0.7 | 核心异步 I/O 引擎 |
| **多路复用** | yamux 0.13 | 单连接多路复用（多隧道共享一条 TCP） |
| **QUIC 传输** | quinn 0.11 + rustls 0.23 | QUIC 协议栈（基于 rustls 加密） |
| **TLS 加密** | rustls 0.23 (ring) + tokio-rustls 0.26 | TLS 1.2/1.3，ring 后端（非 OpenSSL） |
| **证书生成** | rcgen 0.13 | 自动生成自签名证书 |
| **WebSocket** | tokio-tungstenite 0.26 | WebSocket 传输层 |
| **KCP 传输** | kcp-tokio 0.7 | KCP 协议（可靠 UDP，低延迟） |
| **HTTP 解析** | httparse 1 | HTTP 代理协议解析 |
| **Web 框架** | axum 0.8 | 服务端 Dashboard API |
| **静态资源** | rust-embed 8 | 将前端文件嵌入二进制 |
| **序列化** | serde + serde_json + toml | 配置文件解析 |
| **CLI** | clap 4 (derive) | 命令行参数解析 |
| **日志** | tracing + tracing-subscriber | 结构化日志 |
| **认证** | md-5 + hex + base64 + uuid | Token 认证体系 |

### 2.3 传输协议对比

| 协议 | 底层 | 适用场景 | 特点 |
|------|------|---------|------|
| **TCP** | TCP | 通用 | 最稳定，默认选择 |
| **QUIC** | UDP (quinn) | 高延迟/丢包网络 | 0-RTT 建连、多路复用、前向纠错 |
| **KCP** | UDP (kcp-tokio) | 游戏/实时低延迟 | 可靠 UDP，牺牲带宽换延迟 |
| **WebSocket** | TCP (tungstenite) | HTTP 代理后/CDN穿透 | 伪装成 HTTP 流量 |

### 2.4 编译优化策略

```toml
[profile.release]
opt-level = 3       # 最高优化
lto = true           # 链接时优化（跨 crate 内联）
codegen-units = 1   # 单代码生成单元（最大优化空间）
strip = true         # 去除调试符号
panic = "abort"      # panic 直接 abort（省 unwind 代码）

[profile.release-size]  # 极致体积优化
inherits = "release"
opt-level = "z"      # 最小体积优化
```

> 这就是 5MB 二进制的秘密：LTO + single codegen-unit + strip + panic=abort + opt-level="z"。

---

## 三、与竞品对比

| 维度 | Orbien | frp | rathole | Cloudflare Tunnel |
|------|--------|-----|---------|-------------------|
| 语言 | **Rust** | Go | Rust | Go |
| 二进制 | **~5MB** | ~10MB | ~2MB | ~30MB |
| 传输协议 | TCP/QUIC/KCP/WS | TCP/KCP/WS | TCP | QUIC |
| UDP 代理 | ✅ | ✅ | ✅ | ❌ |
| 桌面客户端 | ✅ Tauri <10MB | ❌ | ❌ | ❌ |
| Web 管理 | ✅ 服务端 | ❌ | ❌ | ✅ SaaS |
| TLS | rustls (ring) | Go TLS | rustls | 内置 |
| 多路复用 | yamux | TCP 多路复用 | yamux | QUIC 原生 |
| 架构参考 | frp | 原创 | — | — |

---

## 四、快速部署

### 4.1 服务端（公网 VPS）

```bash
# 下载二进制
wget https://github.com/orbien-org/orbien/releases/download/v2.1.0/orbien-server-linux-amd64.tar.gz
tar xzf orbien-server-linux-amd64.tar.gz

# 启动
./orbien-server --config server.toml

# 访问 Dashboard
# http://YOUR_VPS_IP:7505 (默认端口)
```

### 4.2 客户端（内网机器）

```bash
# CLI 方式
./orbien-client --config client.toml

# 或桌面端（Tauri，<10MB）
# 从 GitHub Releases 下载 Orbien-Desktop
```

### 4.3 Docker 部署

```bash
# 项目提供 docker/ 目录
docker build -t orbien .
docker run -d -p 7000:7000 -p 7505:7505 orbien
```

---

## 五、性能分析

根据项目 Benchmark（本地回环测试）：

| 指标 | Orbien | 典型 frp |
|------|--------|---------|
| 内存占用 | **极低且稳定**（平线） | 波动较大 |
| CPU | Rust 零 GC | Go GC 间歇 |
| 并发隧道 | yamux 多路复用 | TCP 多路复用 |

**为什么内存低且稳定**：
1. Rust 无 GC — 无堆碎片膨胀
2. `bytes::Bytes` 零拷贝缓冲区
3. yamux 连接池复用 — 不为每个隧道新建连接
4. release profile 的 LTO + strip 去除冗余代码

---

## 六、对你 hpage.top 的影响

你的 hpage.top 目前走 Cloudflare CDN → GitHub Pages 路由，**不需要** 内网穿透工具。但 Orbien 在以下场景有价值：

| 场景 | 当前方案 | Orbien 方案 |
|------|---------|------------|
| 本地 Hermes Gateway 远程访问 | 无（需 SSH） | 暴露 8080 到公网 |
| Jetson 远程开发 | SSH + 端口转发 | QUIC 隧道，低延迟 |
| 本地 Web 服务调试 | cloudflared tunnel | 自建穿透，不依赖 CF |
| ESP32/WebRTC P2P | 无 | KCP 传输 + UDP 代理 |

---

## 七、技术亮点

1. **yamux 多路复用** — 所有隧道共享一条底层连接，避免端口爆炸
2. **四种传输层可选** — TCP 稳定 / QUIC 抗丢包 / KCP 低延迟 / WebSocket CDN 穿透
3. **rustls 替代 OpenSSL** — 更小、更快、更安全（ring 后端）
4. **Tauri 桌面端** — Rust 原生，比 Electron 小 10 倍（<10MB vs ~100MB+）
5. **极致编译优化** — LTO + opt-level="z" + panic=abort = 5MB
6. **Java 客户端** — 支持 Android 平台（client-java 模块）

## 相关笔记

- [局域网音响系统探查与控制方案](./2026-08-15-局域网音响系统探查与控制方案.md) — 内网设备探查实战场景
- [QuadRF 开源相控阵 SDR](./2026-08-14-QuadRF-开源相控阵SDR.md) — 开源网络硬件对照
