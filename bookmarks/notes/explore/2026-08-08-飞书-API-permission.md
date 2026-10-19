# 飞书 Permission API — 云文档权限管理

> 来源：飞书开放平台官方文档 + 火山引擎 ArkClaw 权限清单
> 日期：2026-08-08

## 摘要

飞书云文档权限系统由**权限成员**（所有者 + 协作者）和**权限设置**（分享/复制/评论/链接等）两部分组成，通过 `/drive/v1/permissions/:token/` 路径下的 member 和 public 两组接口进行管理。权限设置已升级到 v2，增加了组织维度和协作者维度的协作者管理权限区分。

## 关键发现

### 1. 权限成员角色（三级）
- `view`（可阅读）：只能看
- `edit`（可编辑）：可改内容
- `full_access`（可管理）：可改内容 + 管理权限（妙记不支持 full_access）

### 2. 协作者类型（四种）
- 普通用户（user）
- 文档应用（机器人，openid）
- 群组（chat）
- 部门（department）— **tenant_access_token 不支持添加部门协作者**

### 3. 核心 API 端点清单
- 添加协作者：`POST /drive/v1/permissions/:token/members`
- 批量添加协作者：`POST /drive/v1/permissions/:token/members/batch_create`（限频 100/min）
- 更新协作者权限：`PUT /drive/v1/permissions/:token/members/:member_id`
- 移除协作者：`DELETE /drive/v1/permissions/:token/members/:member_id`
- 判断协作者是否有某权限：`POST /drive/permission/member/permitted`
- 获取协作者列表：`POST /drive/permission/member/list`
- 转移所有者：`POST /drive/permission/member/transfer`
- 获取权限设置（v1）：`GET /drive/v1/permissions/:token/public`
- 更新权限设置（v1）：`PATCH /drive/v1/permissions/:token/public`
- 获取/更新权限设置（v2 推荐）：`/drive/v2/permissions/:token/public`

### 4. 权限设置字段
- `external_access`：允许分享到组织外
- `share_entity`：谁可以添加协作者（组织维度）
- `invite_external`：允许非管理员分享到组织外
- `link_share_entity`：链接分享范围
- `anyone_readable` / `anyone_editable`：互联网获得链接的人可读/可编辑
- 复制/创建副本/打印/下载 控制
- 评论开关

### 5. 所需 Scope 权限
- `docs:permission`（权限管理总开关）
- `docs:permission:member:create`（添加/修改/删除协作者）
- `docx:document`（文档读写）
- `drive:drive`（云空间文件读写）
- `wiki:wiki`（知识库编辑/成员管理）
- `wiki:wiki:readonly`（知识库只读）

### 6. 常见错误码
- **1063002 Permission denied（403）**：最常见。身份不是协作者或权限不足
  - tenant_access_token → 需在文档页面「添加文档应用」入口授权
  - user_access_token → 需在「分享」入口为当前用户添加权限
- **1063001 Invalid parameter（400）**：token 与 type 不匹配、协作者不存在
- **Invalid operation（400）**：协作者数量达上限、企业管控策略限制、可见性限制

### 7. 高频踩坑
- **机器人创建文档默认所有者是机器人**：用户无法编辑，需调用转移所有者接口或主动添加用户为协作者
- **多维表格高级权限**：即使有 docx 权限，多维表格开启高级权限后仍需单独添加"可管理"角色
- **知识库节点（wiki type）的特殊参数 `perm_type`**：`container`（当前页+子页面）vs `single_page`（仅当前页）
- **transfer owner 接口**：仅限文档所有者调用
- **频率限制**：协作者相关操作 100次/分钟，权限设置查询 1000次/分钟

## 对工作的价值

1. **解决 Hermes 飞书机器人创建文档后用户无权编辑的问题**：创建文档后自动调用 `POST /permissions/:token/members` 添加用户为 `full_access` 协作者，或直接调用 transfer owner 转移所有权
2. **批量权限管理**：用 `batch_create` 接口一次性为多人授权，效率比循环单条调用高 100 倍
3. **权限审计**：用 `member/list` 获取协作者列表，结合 `permitted` 判断接口，可做权限合规检查
4. **lark-cli 已封装**：现有 lark-cli Skills 中的 permission 相关命令可直接调用，无需手写 curl

## 行动建议

- [ ] 在 lark-doc / lark-drive Skill 中补充：创建文档后自动调用添加协作者接口，把用户设为 full_access
- [ ] 验证 lark-cli 是否已封装 permission member 的 CRUD 命令（预期应有 `lark-cli permission member create/list/update/delete`）
- [ ] 对 Issue #252（机器人创建文档归属问题）确认是否已通过权限接口解决
- [ ] 如需知识库节点权限管理，注意 perm_type 参数的 container vs single_page 选择


## 相关笔记

- [飞书 Permission API (08-09)](./2026-08-09-飞书-API-permission.md) — 后续补充版权限笔记，含 V2 API 重点
- [飞书 Bot API](./2026-08-07-飞书-API-bot.md) — Bot 自授权流程的权限基础
- [飞书 CardKit API](./2026-08-06-飞书-CardKit-v1-cards-api.md) — 卡片权限与文档权限协同
- [飞书权限模型三层审计 (explore)](../../explore/2026-08-01-feishu-permission-model-three-layer-scope-audit-oauth2.md) — OAuth2 scope 权限体系深度分析
- [飞书消息流 API (explore)](../../explore/2026-07-31-feishu-message-api-lifecycle-gateway-routing-identity-model.md) — 消息生命周期中的身份与权限路由
