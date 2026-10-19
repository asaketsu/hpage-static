# 飞书云文档 Permission API 深度梳理

> 来源：飞书开放平台官方文档 + lark-cli 实际验证
> 日期：2026-08-09

## 一、权限模型总览

飞书云文档权限由 **权限成员（Who）** + **权限设置（What can do）** 两层组成。

### 权限成员（Permission Members）

- **文档所有者（Owner）**：唯一，拥有 full_access，可转让
- **协作者（Collaborator）**：可多个，权限分三级：
  - `view` — 只读
  - `edit` — 可编辑
  - `full_access` — 可管理（含权限管理）

支持的角色实体：用户 / 文档应用 / 群组 / 部门

### 权限设置（Permission Settings）

分 v1 和 v2 两个版本：

**v1（旧版，仍可用）**
- 是否允许外部分享
- 是否允许复制/打印/下载
- 是否允许评论
- 谁能添加和管理协作者
- 链接分享设置

**v2（新版，推荐）**
- v1 全部功能 +
- 协作者维度的「谁能管理协作者」（更细粒度）
- 组织维度的「谁能管理协作者」

## 二、核心 API 列表

### 协作者管理（Permission Members）

1. **添加协作者**
   - `POST /open-apis/drive/v1/permissions/:token/members`
   - lark-cli: `lark-cli drive permission.members create`

2. **更新协作者权限**
   - `PUT /open-apis/drive/v1/permissions/:token/members/:member_id`

3. **移除协作者**
   - `DELETE /open-apis/drive/v1/permissions/:token/members/:member_id`

4. **判断是否有某权限**
   - `POST /open-apis/drive/permission/member/permitted`
   - lark-cli: `lark-cli drive permission.members auth`

5. **获取协作者列表**
   - `POST /open-apis/drive/permission/member/list`

6. **转移所有者**
   - `POST /open-apis/drive/permission/member/transfer`
   - lark-cli: `lark-cli drive permission.members transfer_owner`

### 权限设置（Permission Public）

7. **获取权限设置**
   - v1: `GET /open-apis/drive/v1/permissions/:token/public`
   - v2: `GET /open-apis/drive/v2/permissions/:token/public`
   - lark-cli: `lark-cli drive permission.public get`

8. **更新权限设置**
   - v1: `PATCH /open-apis/drive/v1/permissions/:token/public`
   - v2: `PATCH /open-apis/drive/v2/permissions/:token/public`
   - lark-cli: `lark-cli drive permission.public patch`

## 三、关键参数详解（以添加协作者为例）

```
路径参数:
  token — 云文档 token（与 type 匹配）
  type  — 文档类型: doc|docx|sheet|file|wiki|bitable|folder|mindnote|minutes|slides

请求体:
  member_type — ID 类型: email|openid|unionid|openchat|opendepartmentid|userid|groupid|wikispaceid|appid
  member_id   — 协作者 ID（与 member_type 对应）
  perm        — 权限级别: view|edit|full_access
  need_notification — 是否通知对方（仅 user_access_token 有效）

查询参数:
  need_notification — true/false
```

## 四、所需权限 Scope

调用 permission API 需满足以下权限之一（满足即可）：

- 查看、评论、编辑和管理云文档
- 查看、评论、编辑和管理云空间中所有文件
- 上传和下载云空间文件
- 查看、评论、编辑和管理电子表格
- 查看、编辑和管理知识库

凭证类型：`tenant_access_token` 或 `user_access_token` 均可。

## 五、对工作的价值

1. **批量权限管理自动化** — 可以脚本化处理「给一批人共享文档」「批量调整权限」等重复操作，免去手动逐个设置
2. **权限审计** — 定期拉取协作者列表，检测是否有离职人员残留权限、外部人员越权访问
3. **知识库安全治理** — 结合 wiki 节点权限，实现知识库的自动化安全巡检
4. **与其他 Skill 联动** — 可在创建文档（doc/drive）、发送消息（im）后自动配置权限，形成完整工作流

## 六、行动建议

1. **立即可用**：lark-cli 已封装全部核心 permission 接口，无需裸调 API
2. **常用命令速查**：
   - 查权限设置：`lark-cli drive permission.public get --params '{"token":"xxx","type":"docx"}'`
   - 加协作者：`lark-cli drive permission.members create --params '{"token":"xxx","type":"docx"}' --data '{"member_type":"email","member_id":"a@b.com","perm":"view"}'`
   - 查协作者列表：`lark-cli drive permission.members auth`（判断权限）
3. **注意 v1 vs v2**：新项目建议直接用 v2，粒度更细。旧文档兼容 v1
4. **安全提醒**：permission.members create 属于 high-risk-write，需 `--yes` 确认


## 相关笔记

- [飞书 API: card](./2026-08-11-飞书-API-card.md) — 飞书卡片能力，权限控制的下游消费方
- [飞书 API: card 增量](./2026-08-10-飞书-API-card-增量.md) — Card API 增量更新
- [飞书 API: permission](./2026-08-08-飞书-API-permission.md) — 前序 permission API 笔记
- [飞书 API: permission](./2026-08-05-飞书-API-permission.md) — 早期 permission 基础
