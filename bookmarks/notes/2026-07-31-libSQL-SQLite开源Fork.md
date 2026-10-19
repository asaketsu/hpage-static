# libSQL：SQLite 的开源开放贡献 Fork

> **来源**: [github.com/tursodatabase/libsql](https://github.com/tursodatabase/libsql)
> **团队**: Turso
> **许可证**: MIT
> **Stars**: 17,025 | **Forks**: 515 | **语言**: C / Rust
> **官网**: [turso.tech/libsql](https://turso.tech/libsql)
> **日期**: 2026-07-31
> **标签**: `libSQL` `SQLite` `Turso` `嵌入式数据库` `Edge` `数据库`

---

## 核心结论

libSQL 是 Turso 创建的 **SQLite 开源开放贡献 Fork**。SQLite 虽然开源但不接受外部贡献、无行为准则，社区改进无法回流。libSQL 填补了这个空白：继承 SQLite 的稳定性，同时接受社区贡献，新增了**嵌入式副本（Embedded Replicas）、远程访问、WASM UDF** 等特性。17K+ Star，MIT 许可证。

> ⚠️ **重要区分**：libSQL（本项目，SQLite fork）≠ Turso database（Rust 全新重写，支持并发写入+双向同步，Beta 阶段）。新项目建议看 Turso。

---

## 一、为什么要 Fork SQLite？

| SQLite 的问题 | libSQL 的解法 |
|---|---|
| **不接受外部贡献** | ✅ 开放贡献，社区 PR 欢迎 |
| **无行为准则** | ✅ 明确 Code of Conduct |
| **社区改进无法回流** | ✅ 社区贡献可以合并 |
| **无法满足新场景** | ✅ 嵌入式副本/远程访问/WASM UDF |

> SQLite 几乎嵌入在所有计算设备中，开源且公共领域可用。但它不接受外部贡献，社区改进无法广泛享受。libSQL 旨在成为一个社区可以从多角度贡献的项目。

---

## 二、核心特性

| 特性 | 说明 |
|------|------|
| **嵌入式副本 (Embedded Replicas)** | 在应用内部拥有复制的数据库——本地读+远程同步 |
| **libSQL Server** | 远程 SQLite 访问，类似 PostgreSQL/MySQL 的服务端模式 |
| **ALTER TABLE 扩展** | 修改列类型和约束（原版 SQLite 不支持） |
| **随机化 ROWID** | 避免可预测的递增 ID |
| **WebAssembly UDF** | 用 WASM 编写用户自定义函数 |
| **虚拟 WAL 接口** | 可插拔的预写日志接口 |
| **多语言驱动** | Rust / JS / Go / Python / C / PHP |

### 嵌入式副本架构（核心差异化）

```
传统 SQLite:
  应用进程 ──→ 本地 .db 文件 (单机，无复制)

libSQL Embedded Replicas:
  应用进程 ──→ 本地 SQLite 副本 (毫秒级本地读)
                  ↕ (后台同步)
              libSQL Server / Turso 云 (远程主库)

  优势:
  • 本地读取零延迟（嵌入式）
  • 远程数据同步（分布式）
  • 离线可用（本地副本持续工作）
  • 上线后自动同步
```

---

## 三、与 SQLite 的兼容性承诺

| 维度 | 承诺 |
|------|------|
| **文件格式** | 永远能读写标准 SQLite 文件；加密/CRC 等扩展在未使用时仍生成标准格式 |
| **API** | 100% 兼容 SQLite C API，额外增加新 API |
| **嵌入式** | 始终可嵌入（进程内运行，无需网络），但分发方式可能从单 .c 文件改为 .o 目标文件 |

---

## 四、libSQL vs Turso Database

README 顶部明确区分了两个项目：

| 维度 | libSQL（本项目） | Turso database |
|------|-----------------|----------------|
| **性质** | SQLite 的 Fork | **Rust 全新重写** |
| **并发写入** | ❌ 继承 SQLite 单写者模型 | ✅ **支持并发写入** |
| **双向同步** | 单向（本地↔远程） | ✅ **双向同步 + 离线支持** |
| **状态** | 活跃维护 | **Beta** |
| **适用** | 已有 SQLite 生态 | **新项目首选** |

> 新功能正在 Turso 中开发。如果是全新项目，建议直接评估 Turso。

---

## 五、语言驱动生态

### 官方驱动

| 语言 | 驱动 | 状态 |
|------|------|------|
| **TypeScript / JS** | [libsql-client-ts](https://github.com/tursodatabase/libsql-client-ts) | ✅ 官方 |
| **Rust** | [libsql](libsql) (内置) | ✅ 官方 |
| **Go** | [go-libsql](https://github.com/tursodatabase/go-libsql) | ✅ 官方 (CGO) |
| **Go (无 CGO)** | [libsql-client-go](https://github.com/tursodatabase/libsql-client-go) | ✅ 官方 |

### 实验性驱动

| 语言 | 状态 |
|------|------|
| **Python** | 实验性 |
| **C** | 实验性 |

### 社区驱动

| 语言 | 说明 |
|------|------|
| PHP / D / Ring | 社区维护 |

### GUI 支持

| 工具 | 平台 |
|------|------|
| **Beekeeper Studio** | macOS/Windows/Linux |
| **Outerbase** | 浏览器 |
| **TablePlus** | macOS/Windows/Linux |
| **Dataflare** | 付费 |
| **libSQL Studio** | 浏览器 |

---

## 六、快速使用

### 构建

```sh
# 构建 SQLite 兼容的 C 库和工具
cargo xtask build
```

### SQL Shell

```sh
$ cd libsql-sqlite3 && ./libsql
libSQL version 0.2.1 (based on SQLite version 3.43.0)
libsql>
```

### Docker

```sh
# 参考 docs/DOCKER.md
```

---

## 七、使用场景

| 场景 | 为什么用 libSQL |
|------|----------------|
| **边缘计算** | 嵌入式 + 远程同步，边缘设备本地读零延迟 |
| **离线优先应用** | 本地副本持续工作，上线后自动同步 |
| **SQLite 生态升级** | 100% API 兼容，零迁移成本增加副本能力 |
| **Serverless / Edge** | Turso 云 + libSQL 本地，全球低延迟 |
| **AI Agent 记忆** | 嵌入式 SQLite 做短期记忆 + WASM UDF 扩展 |
| **机器人本地数据** | 嵌入式数据库，断网可用，上线同步 |

---

## 八、与同类数据库对比

| 维度 | SQLite | libSQL | Turso | DuckDB | PostgreSQL |
|------|--------|--------|-------|--------|------------|
| **类型** | 嵌入式 | 嵌入式 Fork | 分布式 Rust | 分析型嵌入式 | 服务端 |
| **开源贡献** | ❌ 不接受 | ✅ 开放 | ✅ | ✅ | ✅ |
| **远程访问** | ❌ | ✅ Server | ✅ 云原生 | ❌ | ✅ |
| **嵌入式副本** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **并发写入** | ❌ 单写 | ❌ 单写 | ✅ | 部分 | ✅ |
| **文件兼容** | — | ✅ SQLite | ✅ | ❌ | ❌ |
| **许可证** | 公共领域 | MIT | — | MIT | PostgreSQL |

---

## 九、关键术语速查

| 术语 | 说明 |
|------|------|
| **libSQL** | SQLite 的开源开放贡献 Fork |
| **Turso** | 团队名 + Rust 全新重写的数据库 |
| **Embedded Replicas** | 嵌入式副本——应用内本地副本 + 远程同步 |
| **libSQL Server** | 远程 SQLite 访问服务（类 PG/MySQL） |
| **WASM UDF** | WebAssembly 用户自定义函数 |
| **WAL** | Write-Ahead Log，预写日志 |
| **Single-writer** | SQLite 继承的单写者模型 |

---

## 十、与现有笔记/项目的关联

| 关联项目 | 关系 |
|---------|------|
| **Hermes Agent** | libSQL 可作为 Hermes 的嵌入式记忆/状态存储——SQLite 兼容 + 远程同步 |
| **位置共享系统** | 该项目用的 SQLite 可无缝升级到 libSQL，获得远程同步能力 |
| **ESP-Claw** | ESP32 边缘设备的本地数据存储候选（如未来有 SQLite 需求） |
| **本地大模型部署** | 机器人本地数据（位置/状态/传感器）可用 libSQL 存储+同步 |
| **学 Agent 正确顺序** | Phase 4 的状态管理可用 libSQL 做 Checkpoint 持久化 |

## 相关笔记
- [轻量Web部署-Turso-Embedded-Replic](explore/2026-08-16-轻量Web部署-Turso-Embedded-Replic.md)
- [Cloudflare-D1-轻量SQLite数据库研究](2026-05-24-Cloudflare-D1-轻量SQLite数据库研究.md)
- [SQLite就是你需要的全部-持久工作流的极简架构](2026-05-30-SQLite就是你需要的全部-持久工作流的极简架构.md)
