# 飞书 API 权限体系深度解析

> 📅 2026-08-05 | 类型: auto-explore | 来源: TinyFish Search + lark-shared skill 实战知识
> ⚠️ 飞书官方文档为 SPA 渲染，web_extract/TinyFish Fetch/mcp_reader 均无法提取正文，本笔记基于搜索摘要 + 本地 lark-cli 实战经验合成

## 摘要

飞书开放平台的 API 权限体系是一个三层架构：**Scope（能力粒度）× Identity（身份类型）× Authorization（授权流程）**。每个 API 调用必须同时满足正确的 scope 开通、正确的身份上下文、以及有效的 access_token 三个条件。权限遵循**最小可用原则**，自建应用和商店应用有不同审核流程。

## 关键发现

### 1. 权限三层模型

- **Scope 层**：应用粒度的权限单元，格式为 `模块:资源:操作`（如 `im:message:send_as_bot`、`calendar:calendar:readonly`）。每个 API 端点要求 N 选 1 的 scope 组合
- **Identity 层**：user（用户身份）或 bot（应用身份），决定了 token 类型和可访问资源范围
  - bot 只需后台开通 scope，无需 `auth login`
  - user 需后台开通 scope **且** 用户通过 OAuth 授权，两层缺一不可
- **Token 层**：`app_access_token`（应用级）vs `tenant_access_token`（租户级）vs `user_access_token`（用户级），不同 API 要求不同 token

### 2. 自建应用 vs 商店应用

- **自建应用**：企业内部使用，权限开通后立即生效，无强制审核
- **商店应用**：需通过飞书应用市场审核，权限变更需提交审批，审核周期较长
- **最小可用原则**：两类应用都应只申请必需的 scope，避免过度授权被拒

### 3. 权限不足的错误反馈机制

飞书 API 返回结构化错误，包含可操作的修复信息：

- `permission_violations`：列出缺失的 scope（N 选 1，满足任一即可）
- `console_url`：直接跳转飞书开发者后台权限配置页的链接
- `hint`：建议的修复命令

**lark-cli 实战**：当 lark-cli 调用返回权限错误时，应将 `console_url` 原样提供给用户，引导去后台开通。对 bot 身份**禁止**执行 `auth login`（bot 无需用户授权）。

### 4. 权限变更事件监听

飞书提供 `scope-change` 事件，当应用的权限范围发生变更时自动推送，可用于：
- 自动检测权限被回收导致的 API 失效
- 监控商店应用审核通过后的权限生效
- 触发自动化权限补全流程

### 5. 权限按模块组织

飞书 scope 按业务模块分类，主要包括：

- `im`：消息读写、群聊管理
- `doc` / `docx`：云文档
- `sheets`：电子表格
- `drive`：云空间/云存储文件操作
- `calendar`：日历日程
- `contact`：通讯录
- `task`：任务
- `wiki`：知识库
- `vc`：视频会议
- `approval`：审批
- `bitable`：多维表格

### 6. User 身份的增量授权

通过 `lark-cli auth login` 授权时，scope 会**累积**而非覆盖：

- `--scope "calendar:calendar:readonly"` — 按具体 scope 授权（推荐，最小权限）
- `--domain calendar` — 按业务域批量授权
- 多次 login 的 scope 自动叠加（增量授权模式）

Agent 代理场景下应使用 split-flow：`--no-wait` 立即返回 device_code + verification_url，将 URL 交给用户在浏览器完成授权，避免阻塞。

## 对工作的价值

1. **日常 lark-cli 使用**：理解 bot/user 权限边界，避免用错身份导致 `--as bot` 访问用户资源失败。核心原则：访问用户个人资源（日历/云盘）必须 `--as user`
2. **权限错误诊断**：看到 `permission_violations` 不要盲目重试，按 scope 列表精准补全。bot 缺权限 → 后台开通；user 缺权限 → 后台开通 + `auth login`
3. **新功能接入**：接入新飞书 API 时，先用 `lark-cli schema <service>.<resource>.<method> --format json` 查看 required scopes，提前在后台开通
4. **自动化场景**：scope-change 事件可用于构建权限健康监控系统，在权限被回收时提前预警

## 行动建议

- **短期**：在现有 lark-cli 工作流中，遇到权限错误时优先提取 `console_url` 而非手动猜测缺失 scope
- **中期**：为常用 lark-cli 操作建立 scope 清单对照表（im 发消息需哪些 scope、calendar 查日程需哪些），减少试错
- **长期**：考虑接入 scope-change 事件监听，实现权限变更自动通知和失效 API 预警

## 参考资料

- 飞书 API 权限介绍: https://open.feishu.cn/document/server-docs/application-scope/introduction
- Scope 完整列表: https://open.feishu.cn/document/server-docs/application-scope/scope-list
- scope-change 事件: https://open.feishu.cn/document/ukTMukTMukTM/uETNz4SM1MjLxUzM//event/scope-change
- 应用权限审批规则: https://www.feishu.cn/hc/en-US/articles/455824553396
- Lark 国际版权限说明: https://open.larksuite.com/document/home/introduction-to-scope-and-authorization/permission


## 相关笔记

- feishu-permission-model-three-layer-scope-audit-oauth2（~/explore）— 三层权限审计与 OAuth2 深度分析
- feishu-card-2.0-callback-protocol-form-container-variables（~/explore）— Card 2.0 回调协议与表单容器
- feishu-message-flow-api-streaming-config-v723（~/explore）— 消息流 API 与 Slash 命令
- feishu-message-api-lifecycle-gateway-routing-identity-model（~/explore）— 消息生命周期与身份路由
- feishu-card-2.0-architecture-components-streaming-hermes-integration（~/explore）— Card 2.0 架构与 Hermes 集成
