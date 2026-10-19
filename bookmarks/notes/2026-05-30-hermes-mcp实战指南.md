# Hermes + MCP 实战配置指南：让 AI 直接操作外部世界

> 来源：[微信公众号文章](https://mp.weixin.qq.com/s/rmRbiXeRMyJxPUexfHWlsw) · 作者：刘亚东 · 2026-05-30
> 标签：`#Hermes` `#MCP` `#AI工具` `#开源工具`

---

## 核心观点

MCP（Model Context Protocol）是 AI 界的 USB-C 接口——统一标准让 AI 模型直接调用外部工具和数据源。Hermes 从 v2.x 内置 MCP 客户端支持，**聊天即操作**。

### MCP 前后的对比

| 维度 | 无 MCP | 有 MCP |
|------|--------|--------|
| 查数据库 | 手动导出 CSV 喂给 AI | 自然语言→AI 直接查 SQL |
| 看 GitHub Issue | 浏览器截图给 AI | AI 直接调 GitHub API |
| 查天气 | 复制粘贴 | AI 实时调 API |
| 本质 | 人做搬运工 | AI 自己调工具 |

---

## MCP 两种连接方式

### 1. stdio 方式（本地子进程）

适合本地工具，低延迟。Hermes 通过 stdin/stdout 通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

### 2. HTTP 方式（远程服务器）

适合云端部署服务，可团队共享。

```yaml
mcp_servers:
  weather:
    url: "https://weather-mcp.example.com/mcp"
    headers:
      Authorization: "Bearer your_api_key_here"
```

---

## 配置选项速查

| 字段 | 作用 | 适用场景 |
|------|------|---------|
| `command` + `args` | 本地启动可执行文件和参数 | stdio 服务器 |
| `url` | 远程 MCP 端点地址 | HTTP 服务器 |
| `headers` | HTTP 请求头部 | HTTP 认证 |
| `env` | 传给 stdio 子进程的环境变量 | 令牌/密码 |
| `timeout` | 工具调用超时，默认 120s | 慢接口 |
| `tools.include` | 白名单：只启用哪些工具 | 安全控制 |
| `tools.exclude` | 黑名单：排除哪些工具 | 安全控制 |
| `enabled: false` | 禁用但不删除配置 | 临时关闭 |

> **关键**：`${VAR}` 引用的是 `~/.hermes/.env` 文件中的变量，不要把 API Key 写进 config.yaml。

---

## 三大实操场景

### 场景 1：SQLite 数据库直连

```yaml
mcp_servers:
  sqlite:
    command: "npx"
    args: ["-y", "@anthropic/server-sqlite", "/path/to/data.db"]
```

对话效果："查 users 表记录" → AI 自动写 SQL 查询返回结果。

### 场景 2：天气 API 对接

```yaml
mcp_servers:
  weather:
    command: "npx"
    args: ["-y", "@nicholaschen/mcp-server-weather"]
    env:
      OPENWEATHERMAP_API_KEY: "${OPENWEATHERMAP_API_KEY}"
```

免费额度：OpenWeatherMap 每天 1000 次，个人完全够用。

### 场景 3：自建 MCP 服务器（Python）

```python
from mcp.server import Server, stdio_server
from mcp.types import TextContent, Tool
import datetime
from typing import Any

server = Server("local-time")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(
        name="get_current_time",
        description="获取当前本地时间，可选时区参数",
        inputSchema={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区，如 Asia/Shanghai",
                }
            },
        },
    )]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "get_current_time":
        tz = arguments.get("timezone", "Asia/Shanghai")
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        return [TextContent(type="text", text=f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**开发模式**：写标准 Python 函数 → MCP 协议包一层 → 自然语言可调用。可扩展到内部 API、工单系统、线上日志等。

---

## ⚠️ 注意事项和常见坑

### 安全

- 2026 年 4 月 OX Security 披露 MCP stdio RCE 漏洞
- 建议：优先用 `hermes mcp install` 装 Catalog 审核服务器
- 用 `tools.include` 白名单限制必要工具
- 不在不可信 npx 命令上直接跑 MCP

### 配置

1. **别一次配太多**——每个服务器注册的工具挤占 token，建议初装 2-3 个
2. **先测试再上线**——`hermes chat` 里确认工具能被发现和调用
3. **远程服务器 OAuth**——认证回调可能需 SSH 端口转发
4. **环境变量位置**——`${VAR}` 引用的是 `~/.hermes/.env`，不是 shell profile

### 性能

- stdio 服务器：Hermes 自动管理进程生命周期
- HTTP 服务器：有网络延迟，但可团队共享
- 慢工具可单独调 `timeout`

---

## 思考

文章核心洞察：**MCP 把自然语言对话从"聊天"延伸到了"操作"**。这与我当前 Hermes 实践高度一致——通过 MCP 已接入多种外部服务，实现了"说人话→自动调工具→返回结果"的闭环。自建 MCP 服务器的模式尤其有价值，可以将任何内部 API 封装为自然语言可调用的工具。

**对我们系统的意义**：我们已有的 MCP 生态（native-mcp skill、mcporter CLI）与文章描述的模式完全吻合。关键优化方向是控制工具数量（避免 token 浪费）和强化安全审计（RCE 风险）。

## 相关笔记
- [[2026-05-30-MCP已死-CLI-First策略与Skills模式回归|05-30-MCP已死-CLI-First策略与Skills模式回归]]
- [[hermesclaw-analysis|hermesclaw-analysis]]
- [[2026-05-30-MCP协议2026最新生态演进|05-30-MCP协议2026最新生态演进]]
- [[2026-04-27-MCP协议生态与Agentic-RAG架构深度学习|04-27-MCP协议生态与Agentic-RAG架构深度学习]]
