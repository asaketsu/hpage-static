# Hermes Agent 自治运维体系 — 本地知识蒸馏
> 探索日期: 2026-05-31 | 方法: 本地知识蒸馏（外部搜索全部不可用） | 来源: 10个运维Skill + Hermes源码

## 核心发现

### 发现一：五层自治运维架构 — 从感知到进化的闭环

Hermes Agent 的运维不是简单的"监控+告警"模式，而是一套借鉴控制论（Cybernetics）的五层自治体系：

1. **感知层（Sensor Grid）**：统一传感器调度，分三级检测——Tier 1 实时传感器（任务执行时触发）、Tier 2 周期传感器（cron 定期触发）、Tier 3 增量传感器（漂移检测）。传感器只检测不修复，输出信号到统一报告。

2. **诊断层（Watchdog）**：每30分钟扫描所有 cron job 健康状态，自动修复常见故障（NFS挂载、文件缺失、模型限流、进程挂掉）。采用"自愈优先"原则——能修就修，修不了才报告。

3. **修复层（Self-Healing Gateway）**：Gateway 自诊断与自修复，检测 model/provider/fallback 问题并自动修复。核心原则是"Agent 有权且有责任自行重启 gateway"——restart 导致的会话中断是正常行为，不是"自杀"。

4. **进化层（Evolver）**：错误模式分析→规则沉淀→经验闭环。五步管道：COLLECT→IDENTIFY→GENERATE→VALIDATE→RECORD。关键创新是经验闭环机制（借鉴交易员思维）：决策留痕→定时复盘→AI自复盘→经验调取。

5. **协调层（Exchange Protocol）**：双机经验交换协议，通过共享文件系统上的 JSONL 追加式经验池实现准实时经验流动。支持 skill 互推、协作任务、心跳检测、宕机接管。

```python
# 控制论闭环示意
# 目标 → 控制器(AI) → 被控系统(代码/文档/配置) → 传感器(Sensor Grid) → 反馈回路(Memory/Skill/Rules)
```

**架构洞察**：这五层不是简单堆叠，而是形成了正反馈循环——传感器检测偏差→Evolver 修复→修复效果再被传感器验证→合格则沉淀为 Skill，不合格则继续迭代。这种"自愈+自进化"组合是 Hermes 区别于普通 AI Agent 的关键特征。

### 发现二：Cron 调度系统 — Gateway 内置的轻量级调度器

Hermes 的 cron 系统不是依赖外部 crontab，而是**内置在 Gateway 进程中**的轻量调度器：

```python
# cron/scheduler.py 核心设计
class CronPromptInjectionBlocked(Exception):
    """当组装的 prompt 触发注入扫描时抛出"""

# tick() 每60秒由 Gateway 后台线程调用
# 使用文件锁 (~/.hermes/cron/.tick.lock) 防止多进程重叠执行
# 支持 fcntl (Unix) 和 msvcrt (Windows) 双平台文件锁
```

**关键设计决策**：
- 文件锁而非数据库锁：避免引入额外依赖，NFS 环境下可靠
- tick 间隔 60 秒：在实时性和资源消耗间取得平衡
- 注入扫描防护：Cron prompt 经过注入检测，防止恶意指令通过 cron 执行
- 子进程隔离：每个 cron job 在独立子进程中运行，故障不影响 Gateway 主进程

**与 Watchdog 的协作模式**：
```
Gateway 启动 → 后台线程每60s tick() → 检查到期 job
  → 子进程执行 job prompt → 记录 last_status
  → Watchdog 每30min 扫描 last_status → error 则自动修复
  → 修复后可能重启 Gateway → 新 Gateway 恢复 cron 调度
```

### 发现三：内存监控与关闭取证 — 长期运行稳定性保障

Gateway 是长期运行进程，会积累内存（Agent 实例、会话记录、工具 Schema、Memory Provider、MCP 连接等）。Hermes 采用了两个关键机制：

**内存监控（memory_monitor.py）**：
```python
# 设计原则（借鉴 cline/cline#10343）
# 1. 每 N 分钟（默认5分钟）输出一行 [MEMORY] 结构化日志
# 2. 启动时记录基线快照
# 3. 关闭时记录最终快照（"exit 前最后一次 RSS"）
# 4. 守护线程，不阻塞进程退出
# 5. 优先用 resource 模块（Linux/macOS），回退到 psutil（Windows）
```

**关闭取证（shutdown_forensics.py）**：
```python
# 信号处理流程
# SIGTERM/SIGINT → shutdown_signal_handler
#   → snapshot_shutdown_context() （<10ms，非阻塞）
#   → spawn_async_diagnostic() （fire-and-forget ps walk）
#   → 日志记录谁/什么触发了关闭
#
# 支持的信号：SIGTERM, SIGINT, SIGHUP, SIGQUIT, SIGUSR1, SIGUSR2
```

**EX_TEMPFAIL（exit code 75）**：Gateway 使用 `GATEWAY_SERVICE_RESTART_EXIT_CODE = 75` 请求服务管理器重启。这来自 sysexits.h 的 EX_TEMPFAIL，语义是"临时故障，请重试"——让 s6-overlay 或 systemd 自动拉起 Gateway。

### 发现四：Hook 系统 — 轻量级事件驱动架构

```python
# gateway/hooks.py — 事件钩子系统
# 支持的事件：
#   gateway:startup    — Gateway 进程启动
#   session:start      — 新会话创建
#   session:end        — 会话结束
#   session:reset      — 会话重置完成
#   agent:start        — Agent 开始处理消息
#   agent:step         — 工具调用循环中每一步
#   agent:end          — Agent 完成处理
#   command:*          — 任意斜杠命令执行（通配符匹配）

# Hook 发现机制：
# ~/.hermes/hooks/ 目录 → 每个 hook 包含：
#   HOOK.yaml   (元数据: name, description, events list)
#   handler.py  (Python handler: async def handle(event_type, context))
#
# 关键设计：错误在 hook 中被捕获和记录，永远不阻塞主管道
```

**实践启发**：这个 Hook 系统使得可以在不修改 Gateway 核心代码的情况下注入行为。例如可以在 `agent:step` 事件上挂载 token 计数器，在 `session:end` 上挂载会话质量评分器。这比修改核心代码安全得多。

### 发现五：双机协作的高可用设计

Exchange Protocol 的设计展现了几个重要的分布式系统思想：

1. **JSONL 追加写入天然无锁**：experience-pool 和 announcements 使用 JSONL 格式，追加写入不需要锁协调
2. **原子替换避免半写**：task-queue 和 sync-marker 使用 write tmp → mv 模式确保原子性
3. **时间错开避免并发**：jbot 整点 :00 执行，ubot 半点 :30 执行，错开30分钟
4. **心跳+宕机接管**：heartbeat.py 检测对端存活，failover-manifest.json 定义可接管任务

```python
# 双机身份映射
# jbot  → jc-desktop (192.168.2.221)
# ubot  → ubot       (192.168.2.223)
# ⚠️ 必须通过 registry.json 映射，禁止 hostname 字符串匹配
```

**Pitfall 记录**：hostname 映射曾出 bug——heartbeat.py 只写了 `jc-desktop` 和 `jc-server`，但实际 hostname 是 `ubot`，导致 `PEER_ID = "unknown"`。修复后 registry.json 成为唯一身份来源。

## 技术细节与代码示例

### Gateway 重启流程

```bash
# Step 1: 检查当前 model 状态
head -6 ~/.hermes/config.yaml

# Step 2: 诊断问题
# 如果 model 429 → 检查 fallback 配置
# 如果 provider 403 → 检查 API key
# 如果 fallback 循环 → 修复 primary 配置

# Step 3: 修复配置后重启
# Gateway 使用 EX_TEMPFAIL(75) 请求重启
# s6-overlay 或 systemd 自动拉起新进程
# 重启时优雅排空（drain）进行中的请求
```

### Watchdog 自动修复模式

```
Watchdog 巡检（每30分钟）
├── Phase 1: Cron Job 健康扫描
│   ├── last_status == "error" → 检查错误时间 vs Gateway 重启时间
│   │   ├── 重启前发生的错误 → 可能已修复，标记观察
│   │   └── 重启后仍在报错 → 进入修复流程
│   ├── NFS 挂载问题 → remount
│   └── 模型限流 → 降级到备选模型
├── Phase 2: 进程健康检查
│   └── Gateway 进程挂掉 → 自动重启
└── Phase 3: 文件完整性检查
    └── 关键配置文件缺失 → 从备份恢复
```

### Evolver 经验闭环

```json
// 经验标签格式（experience-log.jsonl）
{
  "id": "exp_001",
  "timestamp": "2026-04-30T10:00:00",
  "domain": "devops",
  "context_tags": {"skill": "watchdog", "error_type": "NFS_mount"},
  "prediction": "remount 会修复 NFS 问题",
  "actual": "remount 成功，NFS 恢复",
  "verdict": "CORRECT",
  "lesson": "NFS 挂载失效时，先检查 mount 命令输出再 remount",
  "applicability_conditions": ["NFS 环境", "Linux 服务器"]
}
```

### Sensor Grid 三级巡检

```
快速巡检（30秒）:
  Memory 容量 → usage% 
  笔记索引 → glob vs index.md 
  配置漂移 → config.yaml 关键值

标准巡检（3分钟）:
  快速巡检 + 最近任务质量 + cron 状态 + evolver 运行状态

深度巡检（10分钟）:
  标准巡检 + agent-health-check + curator status + memory 漂移分析
```

## 实践启发

1. **"Agent 有权重启自己"** 是一个范式转变。传统运维认为进程重启是"故障"，但在 Agent 语境下，重启是"修复动作"。这个认知差异影响了整个自修复策略的设计。

2. **传感器只检测不修复** 是好的关注点分离。检测逻辑稳定可预测，修复逻辑复杂有风险。分开后可以独立测试和升级。

3. **JSONL 追加写入** 是最简单可靠的并发模式。在共享文件系统上比任何数据库锁方案都更健壮。

4. **五类失败分类**（CONTENT_STALE / MISSELECT / GAP / TOOL_ERROR / MODEL_BASELINE）为自动化进化提供了清晰的决策树——不同类型的失败触发不同的修复策略。

5. **Cron prompt 注入扫描** 是容易被忽视的安全细节。Cron job 的 prompt 由系统组装，如果用户输入能影响 prompt 内容，就可能被注入恶意指令。

## 知识缺口

1. **Gateway 会话状态持久化**：session.py 的 reset policy 如何决定何时重置会话？当前只知道有 `session:start/end/reset` 事件，但不清楚具体的策略算法。

2. **Memory Monitor 的 GC 集成深度**：memory_monitor.py 记录了 Python GC stats，但不清楚是否根据 GC 统计自动触发垃圾回收或内存优化。

3. **Hook 系统的性能影响**：在 agent:step 事件上挂载 handler 会影响每次工具调用的延迟吗？有无性能预算？

4. **双机 Failover 的实际切换时间**：从 heartbeat 检测到宕机到完成任务接管需要多长时间？failover-state.json 的状态机有哪些状态？

5. **Evolver 的 VALIDATE 阶段实现**：confidence ≥ 80% 的判断标准是什么？是 LLM 自评还是有独立的验证器？

6. **s6-overlay 集成细节**：Gateway 如何注册到 s6-overlay？日志如何轮转？资源限制如何配置？

7. **Cron Scheduler 的 job prompt 构建**：`_build_job_prompt` 方法如何组装 prompt？注入扫描的具体规则是什么？

8. **分布式一致性**：双机通过 NFS 共享文件，如果 NFS 短暂中断又恢复，两个 Agent 同时写入 JSONL 会怎样？有校验和或一致性检查吗？

## 来源列表

1. `~/.hermes/skills/devops/self-healing-gateway/SKILL.md` — Gateway 自诊断与自修复
2. `~/.hermes/skills/devops/watchdog/SKILL.md` — 实时监控 + 自动修复
3. `~/.hermes/skills/devops/evolver/SKILL.md` — 自我进化引擎（含经验闭环、PRM评分）
4. `~/.hermes/skills/devops/sensor-grid/SKILL.md` — 统一传感器调度层
5. `~/.hermes/skills/devops/exchange-protocol/SKILL.md` — 双机经验交换协议
6. `~/.hermes/skills/devops/hermes-upgrade/SKILL.md` — 系统升级流程
7. `~/.hermes/skills/devops/hermes-disaster-recovery/SKILL.md` — 防灾容灾体系
8. `~/.hermes/skills/devops/cron-bulk-management/SKILL.md` — Cron 批量管理
9. `~/.hermes/skills/devops/auto-defense-check/SKILL.md` — 自动防御检查
10. `~/.hermes/skills/devops/hermes-system-audit/SKILL.md` — 系统审计
11. `~/.hermes/hermes-agent/gateway/run.py` — Gateway 运行器源码
12. `~/.hermes/hermes-agent/gateway/hooks.py` — Hook 系统源码
13. `~/.hermes/hermes-agent/gateway/memory_monitor.py` — 内存监控源码
14. `~/.hermes/hermes-agent/gateway/shutdown_forensics.py` — 关闭取证源码
15. `~/.hermes/hermes-agent/gateway/restart.py` — 重启常量源码
16. `~/.hermes/hermes-agent/cron/scheduler.py` — Cron 调度器源码
17. `~/.hermes/hermes-agent/gateway/session.py` — 会话管理源码

---
*注：本次学习为本地知识蒸馏模式，外部搜索全部不可用（Tavily 432 限流、zhipu MCP 配额耗尽）。内容完全基于已有 Skill 文档和 Hermes Agent 源码。*


## 相关笔记
- [Hermes Agent（NousResearch）— 竞品分析笔记](../2026-04-05-Hermes-Agent-competitor-analysis.md)
- [Hermes Agent Deep Dive — 进化路线图](../2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md)
- [Hermes Agent vs OpenClaw：Agent框架的路径之争](../2026-04-13-hermes-agent-vs-openclaw.md)
- [Hermes Agent 四层记忆架构 — 深度分析与进化笔记](../2026-05-22-Hermes-Agent四层记忆架构深度分析.md)
- [Hermes Agent v0.10.0 发布分析：启示与可取之处](../2026-04-18-Hermes-Agent-v0.10.0-insight.md)
