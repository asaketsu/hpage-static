# Dual-Agent Sync 深度分析：协议、CRDT 与多 Agent 状态同步

> 📅 2026-06-01 | 🏷️ #dual-agent-sync #CRDT #A2A #多Agent #状态同步 #OR-Set #LWW-Register #Hermes
> 🔍 来源：本地知识蒸馏 — 5篇已有笔记 + 3个SKILL.md + DDG搜索结果交叉综合
> 📊 Topic: dual-agent-sync (Agent系统 L4 子领域)

---

## 一、核心发现

### 发现1：多 Agent 同步的三层架构已成型

2025-2026年，多 Agent 系统的同步问题形成了清晰的三层架构：

| 层级 | 关注点 | 代表协议/模式 | 状态 |
|------|--------|--------------|------|
| **协议层** | Agent 间如何发现、通信、委派任务 | A2A Protocol (Google/Linux Foundation) | 生产就绪，150+组织 |
| **状态层** | 共享状态的并发安全 | CRDT (OR-Set, LWW-Register, G-Counter) | 理论成熟，实践演进 |
| **应用层** | 具体业务场景的同步策略 | Hermes exchange-protocol, subtask-lifecycle | 自研实践 |

**关键洞察**：这三层互相独立但必须协同设计。协议层决定了"怎么找到对方"，状态层决定了"怎么不冲突"，应用层决定了"同步什么"。

A2A 协议在2026年4月满一周年，已从50+组织增长到150+组织，并入 Linux Foundation，三大云（Google/Microsoft/AWS）深度集成。ACP（IBM Research）已于2025年8月正式合并入 A2A，Agent 协议层从"四国演义"收敛为"三足鼎立"——MCP（工具层）、A2A（协作层）、AG-UI（交互层）。

### 发现2：CRDT 是多 Agent 共享状态同步的理论基础

多 Agent 系统的核心难题是**并发写入冲突**——当两个 Agent 同时修改同一份数据时，如何保证最终一致性？

**CRDT（Conflict-Free Replicated Data Types）** 提供了数学证明的解决方案：

| CRDT 类型 | 适用场景 | Agent 系统应用 | 复杂度 |
|-----------|----------|---------------|--------|
| **OR-Set** (Observed-Remove Set) | 去重集合 | `absorbed_by` 标记、已处理条目集合 | 中 |
| **LWW-Register** (Last-Writer-Wins) | 单值最新状态 | heartbeat.json、config 单值 | 低 |
| **G-Counter** (Grow-Only Counter) | 单调递增计数 | 经验池条目数、同步水位线 | 低 |
| **PN-Counter** (Positive-Negative) | 可增减计数 | 任务队列大小、活跃连接数 | 中 |
| **LWW-Map** | 键值映射 | registry.json、Agent 能力注册表 | 中 |

**OR-Set 的核心原理**（最常用类型）：

1. 每个元素带唯一标识：`{agent_id}:{entry_id}:{timestamp}`
2. 维护两个集合：`added`（添加记录）和 `removed`（删除记录）
3. 合并时取并集，元素存在当且仅当在 `added` 中且不在 `removed` 中
4. **合并顺序无关**：任意顺序合并结果一致（数学可证明）

这意味着两个 Agent 可以完全独立地操作，不需要锁或协商，最终合并时结果一定正确。这是多 Agent 系统去中心化协作的理论基石。

### 发现3：Hermes exchange-protocol 是 CRDT + A2A 思想的务实实践

Hermes 的双机交换协议（ubot ↔ jbot）虽然早于 A2A 规范发布，但其设计暗合了 A2A 和 CRDT 的核心思想：

**A2A 对应关系**：
| A2A 概念 | Hermes 实现 | 对齐度 |
|----------|------------|--------|
| Agent Card | registry.json + SKILL.md frontmatter | ⭐⭐⭐ 高 |
| Task Lifecycle | subtask-lifecycle 状态机 | ⭐⭐⭐ 高 |
| JSON-RPC 通信 | JSONL 追加写入 | ⭐⭐ 中（更简单） |
| OAuth/mTLS | NFS4 文件权限 + 内网隔离 | ⭐⭐ 中（轻量安全） |
| SSE 流式推送 | 心跳 + 同步水位线 | ⭐⭐ 中 |

**CRDT 对应关系**：
| CRDT 模式 | Hermes 使用场景 | 当前实现 | 改进空间 |
|-----------|----------------|---------|---------|
| OR-Set | `absorbed_by` 标记 | 简单列表（有覆盖风险） | 应升级为正式 OR-Set |
| LWW-Register | heartbeat.json | 原子替换 | 已对齐 |
| JSONL 追加 | experience-pool.jsonl | 天然无锁追加 | 已对齐 |
| 原子替换 | task-queue.json | write-tmp-then-mv | 已对齐 |

**关键差距**：`absorbed_by` 字段当前使用简单列表，两个 Agent 同时标记同一条目时存在后写覆盖先写的风险。这正是 OR-Set CRDT 要解决的问题——crdt-concurrent-safety skill 已提供实现但尚未集成到 exchange-protocol 中。

### 发现4：增量心跳 + Dead Letter Queue 构成健壮的同步管线

多 Agent 系统的可靠性不仅依赖冲突解决，还需要故障检测和消息恢复机制。

**增量心跳模式**（Hermes 实践）：
- 每个 Agent 每30分钟写入心跳时间戳到 `heartbeat.json`
- 对端读取心跳判断存活状态
- 超过阈值（如2小时未更新）触发 failover 流程
- 心跳数据用 LWW-Register 语义：每机只写自己的时间戳，取最后写入者

**Dead Letter Queue 模式**：
- 处理失败的消息不丢弃，转入 DLQ
- DLQ 条目包含：原始消息、失败原因、重试次数、下次重试时间
- 定期扫描 DLQ，对可重试的消息执行指数退避重试
- 超过最大重试次数的消息标记为"永久失败"，通知人工处理

**组合效果**：
```
Agent-A 发消息 → Agent-B 接收 → 成功 → 确认
                              → 失败 → DLQ → 重试 → 成功/永久失败
Agent-A 心跳 → Agent-B 检测 → 存活 → 正常
                           → 超时 → failover → 接管关键任务
```

### 发现5：协议组合策略决定系统复杂度上限

实践证明，**不是所有 Agent 系统都需要全套 A2A + CRDT**。按规模分层的实用策略：

| 规模 | 推荐方案 | 复杂度 | 适用场景 |
|------|---------|--------|---------|
| **单机双 Agent** | JSONL追加 + 原子替换 + 心跳 | 低 | Hermes 双机（当前） |
| **小团队（3-10 Agent）** | A2A-lite + OR-Set + DLQ | 中 | 内部团队 AI 协作 |
| **企业级（10-100 Agent）** | 完整 A2A + CRDT 全套 + 服务发现 | 高 | 跨部门 AI 编排 |
| **开放网络** | A2A + ANP + 零信任安全 | 极高 | Agent 市场/开放生态 |

**Hermes 当前定位**：单机双 Agent 级别，JSONL + NFS 方案已足够。但随着 subagent 数量增加（delegate_task 的并发子 Agent），内部可能需要 CRDT 来管理 subtask 注册表。

---

## 二、技术细节

### 2.1 A2A Protocol 核心架构（2026 Q1 更新）

```
┌───────────────────────────────────────────────────────┐
│                  A2A Protocol Stack                   │
├───────────────────────────────────────────────────────┤
│  UCP (商业交易层) — AP2 支付扩展                        │
│  - Agent 电商/支付能力注册                               │
├───────────────────────────────────────────────────────┤
│  A2A (协作层) — Signed Agent Cards                     │
│  - Task Lifecycle: submitted→working→completed/failed  │
│  - 多模态消息: 文本/文件/结构化数据                       │
│  - 安全: OAuth 2.0 + mTLS + Signed Cards               │
├───────────────────────────────────────────────────────┤
│  Transport: HTTPS + JSON-RPC 2.0 + SSE                 │
├───────────────────────────────────────────────────────┤
│  Agent Card (.well-known/agent.json)                   │
│  - 能力描述、输入输出 schema、认证方式                    │
└───────────────────────────────────────────────────────┘
```

**v1.0 关键特性**：
1. Signed Agent Cards：加密签名防身份伪造
2. AP2 Extension：Agent Card 中注册支付能力，支持商业交易
3. 完整 Task 状态机：`submitted → working → completed / failed / canceled / input_required`
4. 医疗多 Agent Demo 展示跨框架协作（Claude/ADK/LangGraph/微软框架通过 A2A 互通）

### 2.2 OR-Set CRDT 完整实现（Python）

```python
import json, time
from typing import Set, Dict, Any

class ORSet:
    """OR-Set CRDT — 适用于多 Agent 去重集合场景"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.added: Set[str] = set()      # "{element}:{unique_tag}"
        self.removed: Set[str] = set()     # 已删除的 unique_tag
    
    def add(self, element: str) -> None:
        """添加元素，生成唯一标识确保并发安全"""
        tag = f"{element}:{self.agent_id}:{time.time_ns()}"
        self.added.add(tag)
    
    def remove(self, element: str) -> None:
        """移除元素（Observed-Remove: 只移除已观察到的添加记录）"""
        tags_to_remove = {t for t in self.added if t.startswith(f"{element}:")}
        self.removed |= tags_to_remove
    
    def merge(self, other: 'ORSet') -> 'ORSet':
        """合并两个 OR-Set（取并集，顺序无关）"""
        result = ORSet(self.agent_id)
        result.added = self.added | other.added
        result.removed = self.removed | other.removed
        return result
    
    def elements(self) -> Set[str]:
        """返回当前有效元素集合"""
        return {t.split(':')[0] for t in self.added if t not in self.removed}
    
    def to_json(self) -> str:
        return json.dumps({
            "added": list(self.added),
            "removed": list(self.removed)
        })
    
    @classmethod
    def from_json(cls, data: str, agent_id: str) -> 'ORSet':
        d = json.loads(data)
        inst = cls(agent_id)
        inst.added = set(d.get("added", []))
        inst.removed = set(d.get("removed", []))
        return inst


class LWWRegister:
    """LWW-Register — 最后写入胜出，适用于心跳、配置等单值场景"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.value = None
        self.timestamp = 0
    
    def set(self, value: Any, timestamp: float = None) -> None:
        ts = timestamp or time.time()
        if ts > self.timestamp:
            self.value = value
            self.timestamp = ts
    
    def merge(self, other: 'LWWRegister') -> 'LWWRegister':
        """合并：取时间戳更大的值"""
        result = LWWRegister(self.agent_id)
        if other.timestamp > self.timestamp:
            result.value = other.value
            result.timestamp = other.timestamp
        else:
            result.value = self.value
            result.timestamp = self.timestamp
        return result
```

### 2.3 Hermes 双机同步实战架构

```
┌─────────────────────┐          NFS4 共享文件系统          ┌─────────────────────┐
│   jbot (Desktop)    │◄──────── /uclaw/data/ ──────────►│   ubot (Server)     │
│                     │          hermes-exchange/          │                     │
│  cron :00 整点      │                                    │  cron :30 半点      │
│                     │  experience-pool.jsonl (追加)       │                     │
│  1. 写入经验 ───────┼──► JSONL 天然无锁 ◄─────── 读取经验 │                     │
│  2. 更新心跳 ───────┼──► LWW-Register ◄──────── 检测心跳 │                     │
│  3. 发布任务 ───────┼──► 原子替换(tmp+mv) ◄──── 消费任务  │                     │
│  4. 标记已吸收 ─────┼──► OR-Set (待升级) ◄────── 标记已吸收│                     │
└─────────────────────┘                                    └─────────────────────┘
防冲突规则:
  - JSONL 追加：天然无锁，不会冲突
  - 原子替换：write-tmp + rename，避免读到半写状态
  - cron 错开：jbot :00，ubot :30，减少同时操作概率
  - 文件大小限制：单条 entry ≤ 4KB
```

---

## 三、实践启发

### 3.1 对 Hermes 系统的即时改进建议

1. **`absorbed_by` 升级为 OR-Set**：当前简单列表有覆盖风险，应替换为 OR-Set CRDT 实现（crdt-concurrent-safety skill 已有代码）
2. **Agent Card 标准化**：SKILL.md frontmatter 扩展为 A2A Agent Card 格式，增加 input/output schema 和 capability 声明
3. **subtask-lifecycle 对齐 A2A Task 状态机**：当前状态机 `PENDING→RUNNING→COMPLETED/FAILED` 与 A2A 的 `submitted→working→completed/failed` 高度一致，可直接对齐命名
4. **exchange-protocol 增加 Signed 消息**：借鉴 A2A v1.0 的 Signed Agent Cards，给经验池条目增加来源签名

### 3.2 通用多 Agent 同步设计原则

1. **追加优先于覆盖**：JSONL 追加天然无锁，优于全量替换
2. **去中心化优于中心化**：CRDT 让每机独立操作，合并时自动一致
3. **最终一致性优于强一致性**：Agent 系统容忍短暂不一致，但保证最终收敛
4. **故障隔离**：DLQ 确保单条消息失败不影响整体管线
5. **心跳分层**：秒级心跳太频繁，分钟级心跳用于健康检测，小时级心跳用于 failover 决策

### 3.3 技术选型决策树

```
需要多 Agent 同步？
├─ 只需要简单的任务委派 → subtask-lifecycle (当前够用)
├─ 需要共享状态 + 并发写入 → CRDT (OR-Set / LWW-Register)
├─ 需要跨框架 Agent 协作 → A2A Protocol
└─ 需要商业交易能力 → A2A + AP2 Extension
```

---

## 四、知识缺口

1. **A2A Protocol 2026 最新实现细节**：v1.0 的 Signed Agent Cards 和 AP2 支付扩展的具体实现代码尚未深入分析
2. **CRDT 性能基准测试**：OR-Set 在大规模场景（1000+ 并发条目）下的合并延迟和存储开销
3. **OACP（Open Agent Communication Protocol）**：在 sniff-interests 中提到但尚未深入研究
4. **CRDT 与 Vector Clock 的对比**：在多 Agent 场景下哪种因果关系追踪更合适
5. **跨网络 Agent 同步**：当前 Hermes 依赖 NFS 共享文件系统，跨网络（云-边-端）场景需要不同的同步策略
6. **CRDT 自动合并冲突检测**：当两个 Agent 对同一数据做语义冲突的修改时（如一个改"完成"另一个改"取消"），CRDT 只能保证语法一致性，语义冲突仍需上层解决
7. **跨云 Agent 同步延迟优化**：不同云厂商间的 Agent 通信延迟对实时协作的影响，以及边缘缓存策略在 Agent 系统中的适用性尚未充分探索

---

## 五、来源

**本地笔记**：
- 2026-05-08-ai-agent-protocol-wars-a2a-mcp.md（8882B）
- 2026-05-10-mcp-a2a-agent-ecosystem.md（8751B）
- 2026-05-13-AI-Agent架构-MCP-A2A协议栈.md（6083B）
- 2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md（10895B）
- google-a2a-protocol-multi-agent-2026-05-19.md（2068B）

**Skills**：
- exchange-protocol/SKILL.md（16727B）
- crdt-concurrent-safety/SKILL.md（3079B）
- subtask-lifecycle/SKILL.md（2757B）

**DDG 搜索结果**：
- "Announcing the Agent2Agent Protocol (A2A)" — Google Developers Blog
- "GitHub - a2aproject/A2A" — A2A 开源实现
- "CRDTs and Distributed State Synchronization for Multi-Agent AI Systems"
- "smartcrdt-fleet-sync — CRDT-Based Multi-Agent Fleet Sync" — GitHub
- "Conflict Resolution in Distributed Systems: From Last-Writer-Wins to..."

---

## 相关笔记
- [AI Agent 协议之战：A2A vs MCP vs Function Calling](2026-05-08-ai-agent-protocol-wars-a2a-mcp.md)
- [MCP vs A2A：AI Agent 协议生态深度分析](2026-05-10-mcp-a2a-agent-ecosystem.md)
- [Agent 协议生态 2026 最新进展](../2026-05-04-Agent协议生态2026最新进展-MCP-A2A深度融合.md)
- [Google A2A 协议：多 Agent 协作标准](google-a2a-protocol-multi-agent-2026-05-19.md)
- [AI Agent 架构演进：MCP/A2A 协议栈](2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
