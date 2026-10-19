# FastMCP Python SDK 深度精读（v1.27.1 源码级）

> 日期: 2026-05-26
> 来源: mcp Python SDK v1.27.1 源码精读（已安装在 Jetson Orin 本地）
> 相关技能: mcp-integration, native-mcp

## 核心发现

### 发现1: FastMCP 三层架构 — Tool/Resource/Prompt 装饰器模式

FastMCP 的核心设计是**装饰器驱动的声明式 API**，将 MCP 协议的三大原语（Tool、Resource、Prompt）映射为 Python 装饰器：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

# 1. Tool — 最常用，可注入 Context
@mcp.tool()
def analyze_data(query: str, ctx: Context) -> str:
    ctx.info(f"Processing: {query}")  # 日志回传客户端
    return f"Result for {query}"

# 2. Resource — 数据提供者（类似 REST GET）
@mcp.resource("resource://config")
def get_config() -> str:
    return json.dumps({"version": "1.0"})

# 3. Resource Template — 参数化资源
@mcp.resource("resource://{symbol}/price")
def get_price(symbol: str) -> str:
    return f"Price of {symbol}: 100.5"

# 4. Prompt — 提示模板
@mcp.prompt()
def analyze_table(table_name: str) -> list[dict]:
    return [{"role": "user", "content": f"Analyze {table_name}"}]
```

**关键洞察**: Resource Template 自动检测 URI 中的 `{param}` 与函数参数的匹配关系，不匹配直接抛 ValueError。这是编译期检查，不是运行时。

### 发现2: Context 对象 — 工具与服务器的双向通信桥梁

Context 是 FastMCP 最强大的特性之一，注入方式是**纯类型标注驱动**（参数名任意，只要标注为 `Context` 类型即可）：

```python
@mcp.tool()
async def smart_tool(query: str, context: Context) -> str:
    # 1. 日志 — 回传到客户端
    await context.info("Starting analysis...")
    
    # 2. 进度报告 — 支持进度条
    await context.report_progress(50, 100, message="Halfway done")
    
    # 3. 读取其他资源 — 跨组件访问
    data = await context.read_resource("resource://config")
    
    # 4. Elicitation — 向用户请求额外信息（MCP 2025 新特性）
    from pydantic import BaseModel
    class ConfirmInput(BaseModel):
        approved: bool
        comment: str | None = None
    
    result = await context.elicit("Do you approve?", ConfirmInput)
    if result.action == "accept":
        print(result.data.approved)  # True/False
    
    # 5. URL Elicitation — 敏感信息收集（OAuth、支付等）
    url_result = await context.elicit_url(
        message="需要授权 Google 账号",
        url="https://accounts.google.com/oauth/...",
        elicitation_id="google-auth-001"
    )
    
    return "Done"
```

**Elicitation 的革命性意义**: 传统 MCP 工具是单向的（LLM 调用 → 结果返回），Elicitation 打破了这一限制，允许工具在执行中**暂停并请求人类输入**。这使 MCP 工具可以安全处理需要人类确认的操作（如：交易确认、敏感数据访问）。

**Elicitation Schema 限制**: 只允许原始类型（str/int/float/bool）和 list[str]，不支持嵌套模型。这是设计决策，不是技术限制——确保所有客户端都能渲染表单。

### 发现3: 三种传输模式与生产部署架构

```python
# 开发模式 — stdio（默认）
mcp.run(transport="stdio")

# 生产模式1 — SSE（Server-Sent Events）
mcp.run(transport="sse")  # 启动 uvicorn HTTP 服务器

# 生产模式2 — StreamableHTTP（推荐新方案）
mcp.run(transport="streamable-http")  # 基于 Starlette 的 ASGI 应用
```

**StreamableHTTP vs SSE 对比**:
- SSE: 长连接，服务器推送，旧方案
- StreamableHTTP: 无状态友好（`stateless_http=True`），支持 EventStore 持久化，支持 JSON 响应模式（`json_response=True`），更适合云部署

**DNS Rebinding 防护**: FastMCP 在 localhost 模式下自动启用 `TransportSecuritySettings`，只允许 127.0.0.1/localhost/[::1] 来源。这是安全默认配置。

**自定义路由**: FastMCP 支持在 MCP 协议之外添加自定义 HTTP 端点：

```python
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok"})
```

### 发现4: ClientSessionGroup — 多服务器聚合客户端

这是 **SDK 级的多 MCP 服务器统一客户端**，解决了「一个 Agent 连接多个 MCP 服务器」的核心问题：

```python
from mcp.client.session_group import ClientSessionGroup, StdioServerParameters
from mcp.client.session_group import StreamableHttpParameters

async with ClientSessionGroup(
    component_name_hook=lambda name, info: f"{info.name}_{name}"
) as group:
    # 连接多个服务器
    await group.connect_to_server(
        StdioServerParameters(command="npx", args=["-y", "mcp-server-sqlite"])
    )
    await group.connect_to_server(
        StreamableHttpParameters(url="http://localhost:8080/mcp")
    )
    
    # 自动聚合所有工具
    tools = group.tools  # dict[str, Tool]
    
    # 直接调用，自动路由到正确的服务器
    result = await group.call_tool("sqlite_query", {"sql": "SELECT 1"})
    
    # 动态断连
    await group.disconnect_from_server(session)
```

**命名冲突解决**: `component_name_hook` 允许自定义命名策略（如 `{server_name}.{tool_name}`），避免多服务器工具名冲突。Hermes 的 native-mcp 用前缀 `mcp_{server}_{tool}` 实现了类似逻辑。

### 发现5: OAuth2 认证体系 — 企业级安全

FastMCP 内建完整的 OAuth2 授权服务器支持：

```python
from mcp.server.auth.provider import OAuthAuthorizationServerProvider
from mcp.server.auth.settings import AuthSettings

mcp = FastMCP(
    "secure-server",
    auth_server_provider=MyOAuthProvider(),
    auth=AuthSettings(
        issuer_url="https://my-server.com",
        required_scopes=["read", "write"],
    ),
)
```

两种认证模式:
- `auth_server_provider`: 完整 OAuth2 授权服务器（自己管理 token）
- `token_verifier`: 外部 token 验证（如使用 Auth0/Clerk 等）

### 发现6: Experimental Tasks — 异步长时间任务支持

SDK 内置了实验性的 Task 系统（`mcp.server.experimental`），支持：
- `ServerTaskContext.elicit()`: 任务执行中请求用户输入
- `ServerTaskContext.create_message()`: 任务中调用 LLM sampling
- `TaskStatusNotification`: 异步状态推送（WORKING → INPUT_REQUIRED → COMPLETED）
- `TaskStore` + `Resolver`: 任务持久化和解析

这是 MCP 协议向「长时间异步任务」扩展的关键基础设施。

## 技术细节

### 环境变量配置

所有 FastMCP 设置可通过 `FASTMCP_` 前缀的环境变量配置：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| FASTMCP_DEBUG | false | 调试模式 |
| FASTMCP_LOG_LEVEL | INFO | 日志级别 |
| FASTMCP_HOST | 127.0.0.1 | HTTP 监听地址 |
| FASTMCP_PORT | 8000 | HTTP 端口 |
| FASTMCP_SSE_PATH | /sse | SSE 端点路径 |
| FASTMCP_STREAMABLE_HTTP_PATH | /mcp | StreamableHTTP 端点 |
| FASTMCP_JSON_RESPONSE | false | JSON 响应模式 |
| FASTMCP_STATELESS_HTTP | false | 无状态 HTTP 模式 |

### Structured Output 支持

```python
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    score: float
    recommendation: str

@mcp.tool(structured_output=True)
def analyze(text: str) -> AnalysisResult:
    return AnalysisResult(score=0.95, recommendation="Buy")
```

`structured_output` 三态:
- `None`（默认）: 自动检测返回类型注解
- `True`: 强制结构化输出（需 Pydantic 返回类型）
- `False`: 强制非结构化（返回纯文本/ContentBlock）

### ToolAnnotations — 工具元信息

```python
from mcp.types import ToolAnnotations

@mcp.tool(
    annotations=ToolAnnotations(
        title="数据分析工具",
        readOnlyHint=True,      # 只读操作
        destructiveHint=False,   # 非破坏性
        idempotentHint=True,    # 幂等
        openWorldHint=False,     # 封闭世界
    )
)
def analyze(query: str) -> str:
    ...
```

## 实践启发

1. **自定义 MCP Server 是 Agent 工具扩展的最佳路径**: Hermes 的 native-mcp 已实现客户端侧，但用 FastMCP 构建自定义 Server 可以将任何 Python 函数暴露为 Agent 工具——这对量化交易数据源接入特别有价值。

2. **Elicitation 是 Agent 安全操作的关键**: 对于需要人类确认的操作（如交易执行、文件删除），`ctx.elicit()` 提供了协议级的「人在环路」支持，比自定义确认逻辑更可靠。

3. **ClientSessionGroup > 手动多服务器管理**: 如果 Hermes 未来需要更复杂的多 MCP 服务器协调，可以直接使用 `ClientSessionGroup` 替代当前的 `mcp_servers` YAML 配置模式。

4. **StreamableHTTP + stateless_http=True 是无服务器部署的最佳选择**: 结合 EventStore 可以实现完全无状态的 MCP 服务器，适合部署在 Cloudflare Workers / AWS Lambda。

## 知识缺口

1. **Elicitation 客户端实现**: 当前 Hermes native-mcp 客户端是否支持响应 elicitation 请求？需要验证。
2. **Task 系统成熟度**: Experimental Tasks 仍是实验特性，协议规范可能变化，暂不建议生产使用。
3. **FastMCP vs gofastmcp.com 独立项目**: 源码中直接使用 `from mcp.server.fastmcp import FastMCP`，但 gofastmcp.com 似乎是一个独立增强项目——两者关系需厘清。
4. **Performance 特性**: 大量工具注册时的内存占用和工具发现延迟未测试。

## 代码示例: 量化数据源 MCP Server

```python
"""量化交易数据源 MCP Server 示例"""
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel

mcp = FastMCP(
    "quant-data-server",
    instructions="A股量化数据源，提供实时行情和历史数据",
)

class StockQuote(BaseModel):
    symbol: str
    price: float
    change_pct: float

@mcp.tool()
async def get_realtime_quote(symbol: str, ctx: Context) -> str:
    """获取股票实时行情"""
    await ctx.info(f"Fetching quote for {symbol}")
    await ctx.report_progress(50, 100)
    # 实际实现: 调用行情 API
    return f"Symbol: {symbol}, Price: 25.50, Change: +1.2%"

@mcp.tool()
async def execute_trade(symbol: str, side: str, amount: int, ctx: Context) -> str:
    """执行交易（需要人类确认）"""
    class TradeConfirm(BaseModel):
        confirmed: bool
        max_price: float | None = None
    
    result = await ctx.elicit(
        f"确认{side} {amount}股 {symbol}？",
        TradeConfirm
    )
    if result.action != "accept" or not result.data.confirmed:
        return "交易已取消"
    
    return f"已执行: {side} {amount}股 {symbol}"

@mcp.resource("resource://{symbol}/profile")
def get_stock_profile(symbol: str) -> str:
    """获取股票基本信息"""
    return f"Profile for {symbol}"

# 启动
if __name__ == "__main__":
    mcp.run(transport="stdio")

## 相关笔记

- [Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md) — Skills架构
- [OpenClaw最佳实践15条精华版](2026-04-03-OpenClaw最佳实践15条精华版.md) — 实践指南
- [Claude-Code四层记忆架构](2026-04-03-Claude-Code四层记忆架构.md) — 记忆分层
- [SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md) — Skill规范
- [Hermes-Agent-competitor-analysis](2026-04-05-Hermes-Agent-competitor-analysis.md) — 竞品对比
```
