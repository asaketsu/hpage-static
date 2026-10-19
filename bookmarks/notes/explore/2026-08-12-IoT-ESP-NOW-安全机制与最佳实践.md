# IoT: ESP-NOW 安全机制与最佳实践

> ⚠️ 网络受限，基于多源信息整合整理。来源：Nozomi Networks深度分析 + Espressif官方文档 + Random Nerd Tutorials教程

---

## 摘要

ESP-NOW是乐鑫专为IoT设备对等通信设计的无握手协议，运行在Wi-Fi数据链路层，零连接延迟、低开销。但其默认安全机制存在重大隐患：**未加密传输模式下所有数据（含凭证）裸传空中；即使是AES-CCM加密模式也依赖预共享密钥的静态配置**。Nozomi Networks Labs指出，到2030年IoT设备将达400亿台（当前翻倍），其中大量设备无法打补丁且存在安全风险。

关键结论：ESP-NOW的"免配置易用性"是双刃剑——对于生产部署必须启用AES-128-CCM加密 + 定期轮换密钥 + MAC地址白名单三重防护。

---

## ESP-NOW 技术概览

### 核心特性

| 特性 | 数值/说明 |
|------|----------|
| 工作层 | 数据链路层（基于Wi-Fi action frames） |
| 典型距离 | 70-300米（开阔环境，取决于天线和功率） |
| 数据包大小 | 最大2450字节（加密前） |
| 功耗 | 极低（无需维持TCP/TLS连接） |
| 延迟 | < 10ms（比传统WiFi快约3倍） |
| 兼容SoC | ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2 |
| SDK支持 | ESP-IDF内建模块（esp_now.h） |
| 架构类型 | One-to-One / One-to-Many (Broadcast) / Many-to-One |

### 通信模式

```
One-to-One:    A → B          点对点（如遥控器→智能灯）
One-to-Many:   A → B,C,D...   一对多广播（如网关→传感器网络）
Many-to-One:   A,B,C → D      多对一汇聚（如传感器→云端网关）
```

---

## 安全架构详解（ESP-IDF v4.3+）

### 安全握手流程

```
Pairing阶段:
┌─────────┐   AES-128 encrypted   ┌─────────┐
│ Master  │ ◄── key exchange ───► │ Slave   │
│         │       (nonce+tag)      │         │
└─────────┘                       └─────────┘
        │                              │
Data阶段:                          Data阶段:
┌─────────┐   AES-CCM               ┌─────────┐
│ Master  │ ◄── authenticated ────► │ Slave   │
│         │     encryption/          │         │
└─────────┘     decryption           └─────────┘
```

### 关键API

```c
// 初始化安全上下文
esp_err_t espnow_sec_init(espnow_sec_t *sec);

// 设置预共享密钥 (APP_KEY_LEN = 16 bytes)
esp_err_t espnow_sec_setkey(espnow_sec_t *sec, uint8_t app_key[APP_KEY_LEN]);

// AES-CCM 认证加密 (tag附加在密文末尾)
esp_err_t espnow_sec_auth_encrypt(espnow_sec_t *sec, 
    const uint8_t *input, size_t ilen,
    uint8_t *output, size_t output_len,
    size_t *olen, size_t tag_len);

// AES-CCM 认证解密
esp_err_t espnow_sec_auth_decrypt(espnow_sec_t *sec,
    const uint8_t *input, size_t ilen,
    uint8_t *output, size_t output_len,
    size_t *olen, size_t tag_len);
```

### 安全数据结构

```c
typedef struct espnow_sec_s {
    int state;              // ESPNOW_SEC_UNFINISHED / ESPNOW_SEC_OVER
    uint8_t key[KEY_LEN];       // Secret key (通常16字节)
    uint8_t iv[IV_LEN];         // IV/nonce
    uint8_t key_len;            // Secret key length
    uint8_t iv_len;             // IV length
    uint8_t tag_len;            // Authentication tag length
    void *cipher_ctx;           // Cipher context
} espnow_sec_t;
```

---

## 已知安全风险

### R1: 默认无加密传输（高危）

**现象**：ESP-NOW初始配置不要求启用加密，使用`esp_now_send()`发送的明文数据可在空中被任何Wi-Fi接收器捕获和解读。

**攻击方式**：
- 旁观者嗅探：在相同信道使用Wi-Fi抓包工具直接截获数据
- 中间人重放：记录合法数据包后重复发送，触发重复操作

**缓解措施**：
- 生产环境强制启用`espnow_sec_init()` + `espnow_sec_setkey()`
- 使用AES-128-CCM认证加密（同时提供机密性和完整性保护）
- **绝不能**在未加密模式下传输敏感数据（密码、token、个人数据）

### R2: 静态预共享密钥轮换困难（中危）

**现象**：ESP-NOW使用固定的APP_KEY（16字节）。一旦密钥泄露，所有设备均可被欺骗。大规模部署时手动轮换N个设备的密钥不可行。

**风险场景**：
- 固件镜像泄漏导致密钥硬编码暴露
- 设备被物理获取后提取FLASH中的密钥
- 开发者在代码仓库中提交包含密钥的配置文件

**缓解措施**：
- 使用OTA动态更新密钥（通过安全通道）
- 为每个设备生成唯一密钥（而非全局共享）
- 将密钥存储在secure element或ESP32的RTC/Flash加密区域
- 定期轮换策略（建议每30-90天）

### R3: MAC地址可伪造（中危）

**现象**：ESP-NOW使用MAC地址作为设备标识进行配对和通信。攻击者可扫描并复制合法设备的MAC地址。

**缓解措施**：
- 启用ESP-IDF的MAC地址过滤白名单功能
- 结合应用层认证（如每次消息附带HMAC标签）
- 监控未知MAC地址连接请求并告警

### R4: 缺乏前向保密（低中危）

**现象**：AES-CCM不提供前向保密。如果长期密钥被破解，历史通信可全部回溯解密。

**缓解措施**：
- 对于高安全需求场景，考虑在ESP-NOW之上叠加TLS/DTLS
- 使用短暂会话密钥（需额外的密钥交换协议）
- 权衡：增加了延迟和复杂度，可能违背ESP-NOW的设计初衷

### R5: Broadcast模式的去中心化放大效应（中危）

**现象**：One-to-Many广播模式中，单个恶意节点可向全网发送畸形数据导致DoS。相比传统Wi-Fi，ESP-NOW缺少retransmission控制机制。

**缓解措施**：
- 实现速率限制（每设备每秒最大消息数）
- 应用层校验（消息格式验证 + 序号防重放）
- 关键指令采用确认机制（收到回复才认为操作成功）

---

## 与MQTT/CoAP的对比

| 维度 | ESP-NOW | MQTT over Wi-Fi | CoAP over UDP |
|------|---------|-----------------|---------------|
| 连接开销 | 零（直接发） | TCP连接 + MQTT握手 | UDP无连接 |
| 延迟 | < 10ms | 50-200ms | 20-50ms |
| 加密 | AES-CCM (L2) | TLS 1.3 (L7) | DTLS 1.2/1.3 |
| QoS | 无保证（单播可选ACK） | QoS 0/1/2 | ACK/NACK |
| 路由 | 仅局域网（一跳） | Broker中转（多跳） | 直连或中继 |
| 穿透能力 | 差（不支持路由器转发） | 好（走互联网） | 中等（UDP NAT traversal） |
| 适用场景 | 局域网内高速低功耗通信 | 跨网物联网平台 | 轻量级M2M |

**选型决策树**：
```
需要跨互联网？ ──YES──> MQTT/CoAP via Broker
        │
       NO
        ▼
需要实时性<50ms？ ──YES──> ESP-NOW
        │
       NO
        ▼
需要广播/组播？ ──YES──> ESP-NOW
        │
       NO
        ▼
常规M2M → MQTT
```

---

## 安全加固 checklist（生产部署用）

1. [ ] **始终启用AES-CCM加密** — 不调用`espnow_sec_init()`等于裸奔
2. [ ] **每设备独立密钥** — 禁止硬编码统一密钥到所有固件
3. [ ] **MAC白名单** — 拒绝未注册MAC地址的配对请求
4. [ ] **应用层HMAC** — 在AES之外叠加消息级完整性校验
5. [ ] **序号/Nonce管理** — 防止重放攻击，维护单调递增序列号
6. [ ] **密钥OTA更新机制** — 支持远程轮换而不需物理接触
7. [ ] **广播限流** — 单设备限制每秒发送次数（推荐≤5 msg/s）
8. [ ] **异常行为告警** — 检测信号强度突变、频率突增、非工作时间活动
9. [ ] **固件签名验证** — 防止恶意固件升级
10. [ ] **调试接口关闭** — 生产环境禁用JTAG/SWD，防止物理密钥提取

---

## 对具身智能机器人的借鉴意义

本项目涉及双MCU机器人架构（ESP32语音/WiFi + STM32视觉/导航），ESP-NOW的安全设计可直接映射：

### 1. MCU间 UART 桥接的安全意识

虽然当前使用UART而非ESP-NOW做MCU间通信，但安全原则相通：
- UART不应假定为"物理隔离就安全"——JTAG调试口可提取内存
- 未来若改用无线方案（BLE/NOW），上述R1-R5风险即时生效

### 2. 端云通信的分层安全

```
Device (ESP32) ──AES-CCM──> Local AP ──TLS 1.3──> Cloud
  ↑ L2加密                    ↑ L7加密               ↑ 持久化
  ← ESP-NOW安全               ← WiFi安全             ← API Auth
```

建议在ESP32与手机/云端之间采用两层加密：本地ESP-NOW用AES-CCM，上行MQTT用TLS 1.3，形成defense-in-depth。

### 3. OTA安全更新

鉴于R2静态密钥问题，应规划OTA安全更新机制，使后续能远程轮换来路不明的密钥或在发现漏洞时快速响应。

---

*参考链接：*
- *https://www.nozominetworks.com/blog/esp-now-the-double-edged-sword-of-iot-ease-of-use* (Nozomi Networks IoT安全分析)
- *https://docs.espressif.com/projects/esp-now/en/latest/esp32/api-reference/security/espnow_security.html* (Espressif官方Security API)
- *https://randomnerdtutorials.com/esp32-esp-now-encrypted-messages/* (Random Nerd Tutorials加密教程)
- *https://github.com/espressif/esp-now/blob/master/examples/security/README.md* (ESP-NOW安全示例代码)

## 相关笔记

- [ESP-VISION 乐鑫边缘AI视觉框架](./2026-07-08-ESP-VISION-乐鑫边缘AI视觉低代码框架分析.md) — 同为乐鑫生态，IoT 边缘计算
- [0基础AI做硬件从固件到PCB](./2026-07-16-0基础AI做硬件从固件到PCB工作流.md) — 嵌入式开发全栈实践
