# BitBang CLI：把你的机器变成一个 URL

> **来源**: [github.com/richlegrand/bitbang-cli](https://github.com/richlegrand/bitbang-cli)
> **作者**: Rich Legrand
> **许可证**: MIT
> **Stars**: 152 | **Forks**: 13 | **语言**: Go
> **创建**: 2026-04-23
> **日期**: 2026-07-31
> **标签**: `BitBang` `WebRTC` `远程访问` `P2P` `零配置` `反向代理` `SSH替代`

---

## 核心结论

BitBang CLI 是一个**单文件 Go 静态二进制远程访问多功能工具**。运行 `bitbang serve` 一条命令，打印一个 URL，在任何浏览器打开即可获得：**终端 Shell + 文件浏览传输 + Web 代理**。核心卖点：**无需端口转发、无需配置、无需账号、无需在连接端安装任何东西**。基于 WebRTC P2P + 端到端加密。

---

## 一、解决什么问题？

### 传统远程访问的痛点

| 痛点 | 传统方案的问题 | BitBang 的解法 |
|------|-------------|---------------|
| **NAT/CGNAT 穿透** | 需要端口转发/Tailscale/VPN | WebRTC P2P，无需开端口 |
| **需要账号** | ngrok/Cloudflare Tunnel 需注册 | **无需账号** |
| **连接端需装客户端** | SSH 需客户端+密钥 | **浏览器即可** |
| **配置复杂** | SSH 需启用+配密钥 | 6 位配对码，电话里念 |
| **代理 Web 应用** | SSH 逐个隧道 | **通用代理，连接时指定** |

### 为什么不用 SSH？

BitBang 命令映射与 SSH 一致，但传输层用 WebRTC 替代 TCP：

| SSH | BitBang |
|-----|---------|
| `sshd` | `bitbang serve` |
| `ssh` | `bitbang connect` |
| `scp` | `bitbang cp` |

> 对于你已能舒适 SSH 的机器，BitBang 优势不大。它的价值在于：**SSH 进不去的网络环境**（CGNAT/蜂窝/Starlink/企业网/大学网），以及**不想装客户端只想用浏览器**的场景。

---

## 二、核心功能

### 2.1 三合一 URL

```bash
bitbang serve
# 打印一个 URL，浏览器打开即可获得:

1. Shell    — 浏览器内的完整终端（颜色/调整大小/复制粘贴）
2. Files    — 浏览/预览/下载/上传文件
3. Proxy    — 输入 LAN 地址即可访问该机器网络上的 Web 应用
```

### 2.2 分模式服务

```bash
bitbang serve                    # 全部：shell + files + proxy
bitbang serve shell              # 仅 shell
bitbang serve files ~/share      # 仅文件（-upload 允许上传）
bitbang serve proxy              # 代理（浏览器里选目标）
bitbang serve proxy localhost:8080  # 固定单个目标
```

### 2.3 CLI 连接

```bash
bitbang connect <url>                         # 交互式 shell
bitbang connect <url> -- tail -f /var/log/syslog  # 一次性命令
bitbang cp <url>:/var/log/app.log ./app.log   # 复制文件（scp 风格）
bitbang cp - <url>:/tmp/firmware.bin < firmware.bin  # stdin/stdout
```

### 2.4 设备记忆

```bash
# 每次连接/配对自动保存到 ~/.bitbang/devices.json
bitbang connect nas1    # 之后用短名即可
```

---

## 三、配对码机制（类似 Magic Wormhole）

当无法粘贴 URL 时（如电话中/隔空喊话），`bitbang serve` 会打印一个 **6 位配对码**：

```
配对流程:
1. serve 端打印 5 分钟有效配对码（如 482731）
2. 对方打开 bitba.ng/482731（或 bitbang connect 482731）
3. 对方屏幕显示第二个 6 位数
4. 对方念给你听，你输入确认
5. 配对完成，保存设备凭据

安全原理:
  中间人（MITM）的指纹必然不同 → 两端数字无法匹配 → MITM 无法得逞
  类似 Magic Wormhole 的安全介绍协议（SAS）
```

---

## 四、安全设计

| 特性 | 说明 |
|------|------|
| **自认证身份** | 首次运行生成 RSA 密钥对，设备 UID 从公钥派生——冒充设备 = 找到 UID 的第二原像 |
| **密钥不碰服务器** | 访问码在 URL fragment（`#…`）中，浏览器不发送——`bitba.ng` 服务器永远看不到凭证 |
| **端到端加密** | 全部流量走 WebRTC DTLS；信令服务器只看到公钥/UID/元数据 |
| **验证配对** | 念出来的数字 = 短认证字符串（SAS），从 DTLS 指纹 + 两个 nonce 独立计算 |
| **URL = 持有者凭证** | 谁有 URL 就有访问权，谨慎分享 |
| **可选 PIN** | `--pin` 用于永久/无头设置 |
| **一次性模式** | `-ephemeral` 每次运行全新身份 |

---

## 五、与其他工具对比

| 维度 | ngrok | Cloudflare Tunnel | Tailscale | **BitBang** |
|------|-------|-------------------|-----------|-------------|
| **需要账号** | ✅ 是 | ✅ 是 | ✅ 是 | **❌ 否** |
| **连接端安装** | ❌ 否 | ❌ 否 | ✅ 是 | **❌ 否（浏览器）** |
| **端到端加密** | 默认否 | ❌ 否 | ✅ 是 | **✅ 是** |
| **数据路径** | 其服务器 | 其服务器 | P2P | **P2P** |
| **可自部署** | ❌ | ❌ | ❌ | **✅ 是** |
| **首次使用前** | 账号+token | 账号+DNS | 账号+登录 | **一条命令** |

---

## 六、安装

```bash
# 一行安装（自动检测架构 amd64/arm64/armv7，SHA-256 验证）
curl -sSfL bitba.ng/install | sh

# 指定版本/路径
curl -sSfL bitba.ng/install | sh -s -- --version v0.5.0
curl -sSfL bitba.ng/install | sh -s -- --prefix /usr/local/bin

# 审查脚本后安装
curl -sSfL bitba.ng/install -o install.sh && less install.sh && sh install.sh

# 构建
git clone https://github.com/richlegrand/bitbang-cli.git
cd bitbang-cli && go build
```

> macOS/Windows 构建正在开发中。目前支持 Linux（amd64/arm64/armv7）。

---

## 七、技术架构

```
┌──────────────────────────────────────────────────────┐
│                 BitBang 工作原理                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  机器 A (serve 端)                                    │
│  ┌────────────────┐                                  │
│  │ bitbang serve  │ → 生成 URL + 配对码               │
│  │ (RSA 密钥对)   │                                  │
│  └───────┬────────┘                                  │
│          │                                           │
│          │ 信令（公钥/UID/连接元数据）                  │
│          ▼                                           │
│  ┌────────────────┐    信令介绍    ┌────────────────┐│
│  │ bitba.ng 信令   │──────────────→│ 浏览器 / CLI    ││
│  │ 服务器          │               │ (connect 端)   ││
│  │ (介绍后退出)    │←──────────────│                ││
│  └────────────────┘    信令应答    └────────────────┘│
│                                                      │
│          ┌───────────────────────────┐               │
│          │ WebRTC DTLS P2P 直连       │               │
│          │ (端到端加密，服务器看不到)   │               │
│          │                           │               │
│          │ 如果直连失败:              │               │
│          │   TURN relay (仅传密文)    │               │
│          └───────────────────────────┘               │
│                                                      │
│  连接后提供:                                          │
│    • Shell (PTY)                                     │
│    • Files (浏览/上传/下载)                           │
│    • Proxy (Web 应用代理)                             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### install URL 原理

```
bitba.ng/install 是一个 302 重定向（不是托管脚本）:
1. curl 请求 bitba.ng/install → 302 到 GitHub 仓库的 install.sh
2. 脚本检测 OS+架构
3. 从 GitHub Releases 下载二进制
4. 获取 checksums.txt，验证 SHA-256
5. 安装到 ~/.local/bin
```

---

## 八、使用场景

| 场景 | 怎么用 |
|------|--------|
| **远程协助** | 把 URL 发给对方，浏览器直接获得受限 Shell |
| **CGNAT 环境访问** | Starlink/蜂窝网络无需端口转发 |
| **临时文件分享** | `serve files` 浏览器传文件 |
| **内网 Web 应用代理** | `serve proxy` 访问局域网设备 |
| **无头设备初始配置** | 树莓派首次配置（SSH 未启用时） |
| **机器人现场调试** | 现场浏览器直接连机器人 Shell |
| **跨网络运维** | 无需 VPN，浏览器即可运维 |

---

## 九、与现有笔记/项目的关联

| 关联项目 | 关系 |
|---------|------|
| **位置共享系统** | BitBang 可用于该系统的远程调试/运维（无端口转发） |
| **ESP-Claw** | ESP32 机器人现场调试时，BitBang 可提供浏览器 Shell |
| **Hermes Agent** | 远程管理 Hermes 服务器，无需 VPN/端口转发 |
| **本地大模型部署** | 远程调试 Jetson/工控机上的本地 LLM |
| **Zenoh vs DDS** | BitBang 解决的是"人到机器"的远程访问，Zenoh/DDS 解决的是"机器到机器"的通信 |
| **FDE 工程师** | FDE 现场部署时的利器——客户现场浏览器直接调试 |
