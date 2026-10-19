# HyperWorks MCP 源码精读 — FastMCP 工具面、安全门与 Qt 主线程活桥的 CAE Agent 架构

#MCP #HyperWorks #FastMCP #CAE #Agent工具 #Tcl安全门 #Qt主线程 #localhost认证桥 #检查点回滚 #方法白名单 #Codex #CAEAgentHub

## 出处

- 原文：GitHub 仓库 Cai-aa/CAE-Agent-Hub `/MCP/HyperWorks` 目录（v0.10.0，2026 年）
- 定位：面向 Altair HyperWorks 的**本地 FastMCP 服务**——以独立工作区为安全边界，提供可审计的建模/网格/求解/后处理能力
- 研究方式：git clone 全仓 + 源码精读（server 1462 行 + extension 2962 行 + 各服务模块共约 7K 行 Python）
- 笔记日期：2026-09-07 | 指令语义：**研究 MCP 是如何写和发挥作用的，详细记入笔记**

## 一、内容详细整理

### 1.1 总体架构：外部 MCP 服务 + HyperWorks 内嵌 Extension 的混合模式

```text
Codex / MCP client
        |
        v
FastMCP typed tools (65 个工具)
        |
        +-- live bridge client     -> authenticated 127.0.0.1 JSON requests
        |                                  |
        |                                  v
        |                          HyperWorks Extension（内嵌进程）
        |                                  |
        |                    Qt main-thread hm / hw / hw.hv API
        +-- installation discovery -> HyperMesh / HyperStudy / solver capability matrix
        +-- project service        -> workspace-bounded input, scripts, output, runs
        +-- Tcl safety gate        -> rejects OS/process escape and runner-owned quit
        +-- HyperMesh Batch        -> isolated asynchronous hmbatch jobs
        +-- HyperStudy API         -> typed MCP-generated study setup via hstpy
        +-- solver adapter         -> staged OptiStruct / Radioss jobs
        +-- process registry       -> status, bounded logs, cancellation, artifacts
        +-- GUI launcher           -> HyperMesh / HyperView launch only
```

**关键设计决策**：**不开放任意 Python、Tcl、Shell、PowerShell 或 `eval`**——所有能力都是类型化工具。

### 1.2 MCP 服务端怎么写：FastMCP 最小骨架

入口只有 17 行（`server.py`）——把 `src` 加进 `sys.path` 后转发：

```python
SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from hyperworks_mcp.server import main, mcp

if __name__ == "__main__":
    main()
```

核心在 `src/hyperworks_mcp/server.py`：

```python
mcp = FastMCP("hyperworks", instructions=INSTRUCTIONS)
```

**INSTRUCTIONS 是给 LLM 的系统级使用说明**（这是 MCP server 写作的最佳实践之一）——摘录关键规则：
> Use get_environment before launching anything. Prefer HyperMesh batch Tcl for repeatable pre-processing... Solver and GUI launches are side effects. Ask for approval before launching a GUI, starting a solver, or cancelling a job. **Never infer mesh quality, convergence, solver availability, or successful completion; read the actual job status and logs.** ... The live bridge never exposes arbitrary Python or Tcl execution.

工具注册是纯装饰器模式，类型签名即 schema：

```python
@mcp.tool()
def get_environment() -> dict:
    """Detect HyperMesh GUI/batch, HyperStudy, OptiStruct, Radioss, and capabilities."""

@mcp.tool()
def create_project(name: str) -> dict:
    """Create an isolated HyperWorks project with input, scripts, output, and runs folders."""
```

还注册了 MCP resource（`@mcp.resource("hyperworks://environment")`）——环境信息可作为资源被客户端拉取。

### 1.3 工具面全景：65 个工具分七类

| 类别 | 工具（代表） | 作用 |
|------|-------------|------|
| **环境/项目** | get_environment / configure_installation / create_project / get_project_summary / import_project_file | 安装探测（hmbatch/hstbatch/optistruct/radioss 四件套路径）+ 工作区隔离 |
| **Tcl 批处理** | write_tcl_script / run_hmbatch / launch_hypermesh | 可重复前处理走 batch Tcl；GUI 只显式启动 |
| **分析模板** | prepare_optistruct_cantilever_analysis / prepare_radioss_block_impact_analysis / list_analysis_templates / prepare_analysis_template | 悬臂梁线静力/块体冲击显式两验证模板 + 注册库模板复用 |
| **求解作业** | submit_solver_job / get_job_status / tail_job_log / cancel_job / list_jobs / list_job_artifacts | 异步求解+状态+有界日志+取消+产物管理 |
| **后处理** | get_solver_result_artifacts / audit_radioss_explicit_job / postprocess_solver_result_in_hyperview / extract_solver_time_history_in_hypergraph / generate_solver_job_report | 结果读取+Radioss 审计（终止/能量/添加质量/时间步/负体积/穿透六信号）+云图 PNG+时程 CSV+HTML/JSON 报告 |
| **活桥查询** | get_live_bridge_status / get_live_capabilities / get_live_session_info / get_live_model_summary / list_live_entities / get_live_entity | 活会话内实体级查询 |
| **活桥操作** | 30+ 个 create_live_* / set_live_entity_attributes / select_live_entities_interactively / import_live_cad / automesh_live_surfaces / solid_map_live_solids / tetra_mesh_live_solids / repair_live_mesh_quality / create_live_cylindrical_ogrid / get_live_mesh_quality / create_live_checkpoint / rollback_live_checkpoint / load_live_model / refresh_live_view / save_live_model | 活 HyperMesh 会话内的建模/网格/连接/求解卡/载荷/几何全操作 |

**工具命名纪律**：batch 路径与 live 路径严格分离（`run_hmbatch` vs `create_live_nodes`）——LLM 不会混淆两条执行通道。

### 1.4 安全设计：五层防御（本 MCP 最值得学的部分）

**第一层：Tcl 安全门（security.py）**

正则黑名单拦截 OS/进程逃逸命令：

```python
_BLOCKED_TCL = (
    (re.compile(r"(^|[;\n\[])\s*exec\b", re.IGNORECASE), "exec"),
    (re.compile(r"(^|[;\n\[])\s*socket\b", re.IGNORECASE), "socket"),
    (re.compile(r"(^|[;\n\[])\s*load\b", re.IGNORECASE), "load"),
    (re.compile(r"(^|[;\n\[])\s*open\b", re.IGNORECASE), "open"),
    (re.compile(r"(^|[;\n\[])\s*file\b", re.IGNORECASE), "file"),
    (re.compile(r"(^|[;\n\[])\s*(cd|pwd|glob)\b", re.IGNORECASE), "filesystem navigation"),
    (re.compile(r"(^|[;\n\[])\s*(package|interp)\b", re.IGNORECASE), "dynamic Tcl runtime"),
    (re.compile(r"(^|[;\n\[])\s*exit\b", re.IGNORECASE), "exit"),
    (re.compile(r"(^|[;\n])\s*source\b", re.IGNORECASE), "source"),
    (re.compile(r"(^|[;\n])\s*\*quit\b", re.IGNORECASE), "*quit"),
    (re.compile(r"(?i)(?:^|[^A-Za-z0-9_])[A-Za-z]:[\\/]"), "absolute Windows path"),
    (re.compile(r"(?:^|[\s\"'{])\\\\"), "UNC path"),
    (re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)"), "parent path traversal"),
    (re.compile(r"(?i)(?:\$|::)env(?:\(|\b)"), "environment access"),
)
```

**防御细节**：
- `(^|[;\n\[])` 前缀——只匹配**语句开头**（不误伤变量名包含 exec 的正常代码）
- 拦绝对 Windows 路径/UNC 路径/`..` 穿越/环境变量访问——**Tcl 只能在项目文件夹内活动**
- NUL 字节拒绝 + 2MB 大小上限——防解析器歧义与资源滥用
- README 诚实声明："The Tcl filter is defense in depth, **not an operating-system sandbox**"——正则过滤是纵深防御的一层，不是沙箱

**第二层：工作区边界（projects.py）**
- 所有文件/作业/脚本限制在 `HYPERWORKS_MCP_WORKSPACE`
- 外部输入文件必须**显式点名**后才拷入项目
- CAD 导入只接受项目内 STEP/IGES/Parasolid

**第三层：活桥协议安全（live_bridge.py ↔ bridge.py）**
- **只绑 127.0.0.1**——不暴露网络面
- 每请求随机 token（≥32 字符）认证——`hmac.compare_digest` 防时序攻击
- 请求 1MB / 响应 4MB 上限
- 请求-响应 ID 配对校验
- **方法白名单 dispatch**：`self.methods.get(method)` 不存在直接 `ValueError("Method is not allowlisted")`——没有 eval 类通道

**第四层：Qt 主线程纪律（bridge.py 最精妙的 30 行）**
> The socket thread never invokes the HyperWorks API. A Qt timer drains requests and invokes `hm`, `hw`, and `hw.hv` from the application's main thread.

实现：
```python
self.requests = queue.Queue(maxsize=100)   # socket线程只入队
self.timer = QTimer()
self.timer.setInterval(25)                  # 25ms 轮询
self.timer.timeout.connect(self._drain_requests)

def _drain_requests(self):
    for _ in range(8):                      # 每tick最多8个，防饿死GUI
        pending = self.requests.get_nowait()
        result = self.registry.dispatch(pending.method, pending.params)
        pending.completed.set()             # 事件通知socket线程取结果
```
**为什么必须这样**：HyperWorks 的 hm/hw API 只能从 **Qt 主线程**调用——socket 线程直接调会崩 GUI。请求队列 + QTimer 排水 + `threading.Event` 应答，三件套把网络并发转成主线程串行。

**第五层：副作用审批 + 检查点回滚**
- INSTRUCTIONS 明确规定 GUI 启动/求解器启动/取消作业前**必须先请求批准**
- 所有模型修改/网格操作**先写 `.hm` 检查点**，失败自动回滚
- `load_model` 必须 `replace_current=true` 显式确认
- `overwrite` 必须 `overwrite=True` 显式确认

### 1.5 活桥请求全链路（一次 save_live_model 的旅程）

```python
# MCP 工具层（src/server.py L1408）
@mcp.tool()
def save_live_model(project_id, output_name, model_name=None, overwrite=False, ...) -> dict:
    output = projects.root(project_id) / "output" / Path(output_name).name  # 路径限制在项目内
    if output.suffix.lower() != ".hm":
        output = output.with_suffix(".hm")                                   # 强制.hm后缀
    return live.call("save_model", {...}, timeout=300)
```

```python
# MCP 客户端（live_bridge.py）
config = self._config()                       # 读bridge.json，校验host=127.0.0.1+token≥32
request = {"id": uuid4().hex, "token": ..., "method": "save_model", "params": {...}}
socket.create_connection((host, port))        # TCP连接→发送JSON行
# 等待\n结尾的响应→ID配对→ok字段校验
```

```python
# Extension 端（bridge.py）
_BridgeRequestHandler.handle():
    token校验(hmac.compare_digest) → method/params类型校验
    → queue.put(PendingCall)       # 入队(maxsize=100，满则QUEUE_FULL)
    → pending.completed.wait(timeout)  # 阻塞等主线程结果

# QTimer 25ms tick（Qt主线程）
_drain_requests() → registry.dispatch("save_model", params) → hm API 实际保存
→ pending.completed.set() → socket线程写回响应
```

### 1.6 "MCP 如何发挥作用"：LLM 视角的完整工作流

以 README 能力清单串起来，一个 CAE Agent 的典型任务流：

1. **探测**：`get_environment` → 知道本机有哪些求解器/活桥是否在线（LLM 被指示**任何启动前必查**）
2. **立项**：`create_project` → 独立工作区（input/scripts/output/runs 四目录）
3. **建模**（二选一或混合）：
   - batch 路：`write_tcl_script`（过安全门）→ `run_hmbatch`（隔离异步）
   - live 路：`create_live_solid_block` → `import_live_cad`（STEP）→ `automesh_live_surfaces` → `solid_map_live_solids`——每步自动 `.hm` 检查点
4. **求解卡与载荷**：`create_live_solver_card_entity`（Property/Loadcol/Loadstep/Set）→ `create_live_nodal_load` / `create_live_pressure_load`
5. **连接**：`create_live_rigid_link` / `create_live_rbe` / `create_live_weld` / `create_live_spot_weld`（RBE3 spider/点焊带 Property）
6. **提交**：`submit_solver_job`（staged OptiStruct/Radioss，CPU 数有界）→ `get_job_status` 轮询（INSTRUCTIONS 禁止 LLM 凭感觉推断成功——必须读实际状态与日志）
7. **审计**：`audit_radioss_explicit_job` → 六信号检查（终止/能量/添加质量/时间步/负体积/穿透）
8. **后处理**：`postprocess_solver_result_in_hyperview`（云图+PNG）→ `extract_solver_time_history_in_hypergraph`（时程 CSV+PNG）
9. **报告**：`generate_solver_job_report` → HTML/JSON 含真实任务状态+产物+质量审计

**发挥作用的核心机制**：MCP 把"CAE 工程师的手"拆成 65 个**类型化动词**，LLM 通过组合动词完成任务；每一步都有审计痕迹（检查点/日志/状态机），错误有回滚，危险操作有审批门——**LLM 获得了能力但被剥夺了越权通道**。

### 1.7 工程质量细节（值得照抄的做法）

- **能力探测矩阵**：`get_environment` 返回 capabilities dict——LLM 可根据能力决定走 batch 还是 live 路（降级思维内置）
- **`SUCCESS_MARKER`**：jobs.py 用显式成功标记判定作业完成——**不靠退出码猜测**（求解器退出码语义混乱是 CAE 老坑）
- **有界日志**：`tail_job_log` 只取尾部——防止 LLM 上下文被 10 万行求解日志撑爆
- **错误日志分离**：`bridge-errors.log` 独立于状态文件——排障路径清晰
- **pyproject + uv.lock**：可复现环境；`probe_environment.py`/`stdio_smoke.py`/四类 e2e smoke——分级自测（真实求解的 e2e 标注"消耗许可证，获得许可后才运行"）
- **PowerShell 注册脚本**：`register_codex_mcp.ps1` 一键注册到 Codex MCP 配置——降低使用者门槛
- **README 双语**：README.md + README.zh-CN.md 并行维护

## 二、查询拓展

- FastMCP 与官方 anthropic MCP SDK 的差异（装饰器 API 的演进）
- HyperWorks Extension 的 extension.xml 加载机制（load.py/unload.py 生命周期）
- hstpy（HyperStudy Python API）的 typed study 生成细节
- Codex MCP 配置格式（examples/codex_config.example.toml）
- Qt QTimer 单线程排水的延迟上限（25ms×队列深度 100 的最坏等待）
- CAE-Agent-Hub 仓库其他 MCP（仓内 MCP/ 目录是否还有 Abaqus/ANSYS 等）
- hm.entities 的 ENTITY_CLASS_NAMES 映射表全貌

## 三、归纳总结

1. **MCP 的本质是"把应用的手拆成类型化动词"**：65 个工具=65 个动词，LLM 组合动词完成任务——能力通过窄接口授予，越权通道（shell/eval/任意脚本）在设计层面就不存在
2. **INSTRUCTIONS 是 LLM 行为的第一道防线**：把"启动前必查环境/危险操作先请示/禁止凭感觉推断成功"写进 server instructions——**MCP 的安全不只在代码层，还在提示层**
3. **五层防御纵深**：Tcl 正则门→工作区边界→桥协议安全（localhost+token+白名单）→Qt 主线程纪律→审批+检查点回滚——**每层都自知不完美（"defense in depth, not a sandbox"）但叠加成可信整体**
4. **Qt 主线程桥是 GUI 应用 MCP 化的通用解**：socket 线程只入队+QTimer 25ms 排水+Event 应答——**网络并发转主线程串行**的三件套可移植到任何 Qt 系工业软件
5. **batch 路与 live 路分离是 CAE 场景的正解**：可重复前处理走 batch Tcl（便宜/可审计），交互式修改走 live 桥（即时反馈）——**INSTRUCTIONS 教 LLM 按场景选路**
6. **"禁止推断，必须读状态"是最重要的 LLM 纪律**：Never infer mesh quality, convergence... read the actual job status and logs——**CAE 没有幻觉的余地，一切结论必须有产物背书**
7. **检查点-回滚让破坏性操作可逆**：每个模型修改先写 .hm 检查点，失败自动回滚——**Agent 安全的经典模式（先备份再动手）落到文件粒度**
8. **异步作业管理是长任务 MCP 的标配**：submit/status/tail/cancel/artifacts 五件套——LLM 轮询而非阻塞，有界日志防上下文爆炸
9. **能力探测矩阵实现优雅降级**：get_environment 返回四求解器+活桥在线状态——LLM 据此降级（无 Radioss 就只跑 OptiStruct 模板）
10. **双语 README+分级 smoke 测试+uv 锁定**：工程完成度标杆——真实求解 e2e 显式标注许可证成本，诚实边界

## 四、趋势判断

1. **2026 下半年会出现"工业软件 MCP 化"浪潮**：HyperWorks/ABAQUS/ANSYS/STAR-CCM+ 各家都会出官方或社区 MCP——**本仓库的"外部服务+内嵌 Extension+localhost 桥"三段式会成为事实模板**
2. **Qt 主线程桥模式会被提炼成通用库**：QTimer 排水+Event 应答+方法白名单的组合有极强的可移植性——预计出现 `qt-mcp-bridge` 类通用包
3. **"类型化动词+审批门+检查点"会成 Agent 工具设计三原则**：越权通道设计层消除/危险操作提示层拦截/破坏性操作文件层回滚——三层结构会被 Agent 工程规范吸收
4. **CAE Agent 的竞争焦点从"能不能调 API"转向"审计与回滚"**：求解一次数小时数天的场景里，可审计性（日志/状态/报告）比速度更重要——本仓库的六信号审计+HTML 报告是正确方向
5. **MCP instructions 会从"使用说明"演进为"行为契约"**：禁止推断/必须请示/先查环境这类规则本质是 LLM 的行为契约——预计出现标准化的 side-effect 声明语法
6. **许可证经济成为 CAE Agent 的隐藏约束**：e2e smoke 标注"消耗许可证"——Agent 大规模调度 CAE 软件时许可证池管理会成为新问题

## 五、关联分析

> 关联对象：自有 Hermes MCP 生态 / mcp-server-development 技能 / agent-security-governance / ths-auto-trader（同花顺 UI 自动化）/ DUCK-Pi_5 vla-bridge

| 对照项 | HyperWorks MCP 做法 | 自有体系现状 | 判定 |
|--------|--------------------|--------------|------|
| **工具面设计** | 65 个类型化动词+能力矩阵+降级 | mcporter/native-mcp 生态 | ✅ 借鉴：工具按"探测/立项/执行/审计"分层命名，而非按软件菜单平铺 |
| **安全门** | Tcl 正则黑名单+白名单 dispatch+localhost 桥 | agent-security-governance 零信任框架 | ✅ 借鉴：方法白名单+compare_digest 认证可直接抄进自有 MCP server |
| **Qt 主线程桥** | QTimer 25ms 排水+Event 应答 | 无 GUI 软件桥接场景 | ⏸️ 备用：若未来接 CATIA/同花顺客户端这类 Qt/COM 系软件，此模式直接可用 |
| **审批+检查点** | INSTRUCTIONS 审批门+.hm 检查点回滚 | Hermes 权限分级（生产部署二次确认） | ✅ 对齐：自有"Strict Authorization"与审批门同构；检查点模式可加给破坏性 terminal 操作 |
| **审计报告** | 六信号审计+HTML/JSON 报告 | observability-dashboard 事件日志 | ✅ 借鉴："作业级产物报告"比"流式日志"更适合 LLM 消费 |
| **ths-auto-trader** | — | UI 自动化驱动交易软件 | ✅ 亲缘：同花顺客户端本质也是"外部 Agent 操作 GUI 软件"——HyperWorks 的桥接思路（内嵌 Extension > 外部模拟点击）是**更稳的路线** |
| **vla-bridge（DUCK-Pi_5）** | localhost 桥+token+方法白名单 | vla_rpcd RPC 守护 | ✅ 对齐：小鸭的 RPC 层与活桥同构——可补 token 认证与请求 ID 配对 |

**最大启示**：HyperWorks MCP 证明了**"内嵌 Extension > 外部 UI 模拟"**——与其让 Agent 模拟人类点菜单（脆弱/慢/难审计），不如在应用内开一个受控 API 面（稳定/快/可审计）。这对自有 ths-auto-trader（模拟点击路线）是路线级启发：**同花顺若开放类似扩展接口，应优先走内嵌路线**。

## 六、指南分析

| 场景 | 查哪节 |
|------|--------|
| MCP server 怎么起步 | §1.2 最小骨架+装饰器工具 |
| 工具面怎么规划 | §1.3 七类 65 工具的分层 |
| 安全怎么设计 | §1.4 五层防御 |
| GUI 软件怎么桥接 | §1.4 第四层+§1.5 全链路 |
| LLM 行为怎么约束 | §1.2 INSTRUCTIONS+§1.6 工作流 |
| 什么样的工程质量算好 | §1.7 八个细节 |
| 给自有体系的借鉴 | §五 对照表 |

**核心口诀**：应用的手拆成类型化动词 / INSTRUCTIONS 是行为契约 / 五层防御叠加成可信 / socket 入队 Qt 排水 / 白名单 dispatch 无 eval / 先检查点后动手 / 禁止推断必读状态 / batch 与 live 分路 / 探测矩阵支持降级 / 报告为 LLM 而生。

## 七、拓展应用推荐

- **给 mcp-server-development 技能**：并入"五层防御"检查清单（正则门/工作区/桥协议/主线程纪律/审批回滚）与"类型化动词分层命名"规范
- **给 agent-security-governance 技能**：补"方法白名单 dispatch + hmac.compare_digest 认证 + 请求 ID 配对"三件套为 MCP server 标配
- **给 ths-auto-trader 技能**：吸收"内嵌 Extension > 外部 UI 模拟"路线判断——长期看客户端扩展接口优先于模拟点击
- **给 DUCK-Pi_5 vla_rpcd**：补 token 认证与请求 ID 配对（当前 RPC 无认证，本机场景风险低但习惯值得养成）
- **延伸阅读**：FastMCP 文档 / Model Context Protocol 规范 / CAE-Agent-Hub 仓库其他模块 / Altair HyperWorks Extension 开发文档 / hstpy API

---

→ 相关：[[2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计.md]]（审批边界设计对照——本仓库的审批门+检查点是同类思想在 CAE 域的落地）
→ 相关：[[2026-09-06-Karpathy五级阶梯与Graph工程全景-从LLM到Graph的系统化进路.md]]（MCP 工具面=Graph 工程的边集——类型化动词是 Graph 节点间契约）
→ 相关：[[2026-09-07-国产开源VLA三路分化-XR1数据账LingBot本体账与TurboVLA实时账.md]]（vla-bridge 命令入口的 OOD 过滤升级——白名单 dispatch 同构）
→ 相关技能：mcp-server-development / agent-security-governance / ths-auto-trader / mcporter
