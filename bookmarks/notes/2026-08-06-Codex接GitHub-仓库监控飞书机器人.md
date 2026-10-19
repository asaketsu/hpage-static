# Codex 接 GitHub：从 0 搭一个会私聊你的「仓库监控机器人」

> **来源**：[@AdrianPunk115 的 X Article](https://x.com/AdrianPunk115/status/2085325067911835908)
> **作者**：Adrian Punk
> **发布日期**：2026-08-06
> **阅读量**：8.5K Views
> **核心标签**：GitHub Actions、飞书机器人、Codex、CI/CD 监控

---

## 背景与动机

最近同时在做几个团队协作项目，作者越来越受不了 GitHub 的通知方式：

- Issue 开了半天，刷仓库时才发现
- PR 已经等着 Review，群里没人提，进度就卡在那里
- 可把所有提醒全部打开，评论、机器人更新和代码同步又会把重要消息淹掉

**目标**：做一个值班机器人——GitHub 有新 Issue/PR/Release 时，飞书应用机器人自动私聊指定用户。

> **注意**：这次接的不是"飞书群自定义机器人 Webhook"。要创建一个**企业自建应用**，打开它的机器人能力，让 GitHub Actions 以这个机器人的身份发送消息。

### 完整链路

```
GitHub Issue / PR / Release
        ↓
GitHub Actions 自动运行
        ↓
飞书应用机器人
        ↓
机器人私聊指定用户
```

> "我不会写代码，但这篇文章里会有完整代码。你只需要照着创建应用、开权限、复制文件和验证结果；遇到报错，再把截图交给 Codex。"

---

## 内容整理

### 一、先决定监控什么，通知到哪

第一版只回答两个问题：
1. **监控什么**：新 Issue（opened/reopened）、新 PR（opened/reopened/ready_for_review/review_requested）、新 Release（published）
2. **通知到哪**：飞书应用机器人发送给指定用户（默认发给自己）

**重要坑**：同一个人在不同飞书应用下的 open_id 可能不同。不能随便从另一个应用或另一套 CLI 配置里复制一个 ou_ 开头的 ID。

**权限分三档（第一版只做只读监控）**：
- GitHub：contents:read, issues:read, pull-requests:read
- 飞书：只开 `im:message:send_as_bot`
- A 档跑稳之后，再考虑 needs-info、自动打标签和过滤 Bot
- **自动合并 PR、关闭 Issue、修改代码继续交给人判断**

### 二、最小可跑配置

整个机器人需要五样东西：
1. 一个 GitHub 测试仓库
2. 三个 Repository Secret（App ID、App Secret、Receive ID）
3. 一个工作流文件
4. 一次手动测试
5. 一条真实 Issue 验证

**GitHub 工作流只开三项读取权限：**

```yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
```

> 机器人只能看事件并发送飞书消息，不能修改仓库、关闭 Issue 或合并 PR。

### 三、飞书部分只做三件事

打开飞书开发者后台，按下面三步做：
1. 创建企业自建应用
2. 开启机器人能力
3. 配置权限和可用范围

发布后在飞书搜索这个机器人，能找到且你在可用范围内，这部分就完成了。

**接下来只拿走三个值：**
- App ID
- App Secret
- open_id（你的用户 ID）

> App Secret 直接存进 GitHub，不要发到聊天里，不要写进代码，截图前也要确认它已隐藏。

### 四~六、GitHub 配置步骤

**Step 1：建测试仓库** — 仓库名 `repo-monitor-demo`，勾选 Add a README file

**Step 2：存三个 Secret** — Settings → Secrets and variables → Actions → New repository secret

```
FEISHU_APP_ID
FEISHU_APP_SECRET
FEISHU_RECEIVE_ID
```

> 名字必须完全一致，不要加引号，不要在前后多粘贴空格。GitHub 保存后不允许回读 Secret。

**Step 3：创建工作流文件** — Add file → Create new file，文件名：

```
.github/workflows/repo-monitor.yml
```

### 七、完整工作流代码（原文照录）

```yaml
name: Repo Monitor

on:
  issues:
    types: [opened, reopened]
  pull_request_target:
    types: [opened, reopened, ready_for_review, review_requested]
  release:
    types: [published]
  workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: read

jobs:
  notify:
    runs-on: ubuntu-latest
    timeout-minutes: 3

    steps:
      - name: Build notification text
        id: message
        shell: bash
        env:
          EVENT_NAME: ${{ github.event_name }}
          REPOSITORY: ${{ github.repository }}
        run: |
          case "$EVENT_NAME" in
            issues)
              title=$(jq -r '.issue.title' "$GITHUB_EVENT_PATH")
              url=$(jq -r '.issue.html_url' "$GITHUB_EVENT_PATH")
              text="💡 新 Issue｜$REPOSITORY\n$title\n$url"
              ;;
            pull_request_target)
              title=$(jq -r '.pull_request.title' "$GITHUB_EVENT_PATH")
              url=$(jq -r '.pull_request.html_url' "$GITHUB_EVENT_PATH")
              text="🔀 PR 需要关注｜$REPOSITORY\n$title\n$url"
              ;;
            release)
              title=$(jq -r '.release.name // .release.tag_name' "$GITHUB_EVENT_PATH")
              url=$(jq -r '.release.html_url' "$GITHUB_EVENT_PATH")
              text="🚀 新 Release｜$REPOSITORY\n$title\n$url"
              ;;
            *)
              text="🧪 测试成功｜$REPOSITORY 的监控机器人已连通"
              ;;
          esac

          {
            echo 'text<<EOF'
            printf '%b\n' "$text"
            echo 'EOF'
          } >> "$GITHUB_OUTPUT"

      - name: Send as Feishu bot
        shell: bash
        env:
          FEISHU_APP_ID: ${{ secrets.FEISHU_APP_ID }}
          FEISHU_APP_SECRET: ${{ secrets.FEISHU_APP_SECRET }}
          FEISHU_RECEIVE_ID: ${{ secrets.FEISHU_RECEIVE_ID }}
          MESSAGE_TEXT: ${{ steps.message.outputs.text }}
        run: |
          for name in FEISHU_APP_ID FEISHU_APP_SECRET FEISHU_RECEIVE_ID; do
            if [ -z "${!name}" ]; then
              echo "缺少 $name，请先添加 Repository secret。"
              exit 1
            fi
          done

          token_body=$(jq -n \
            --arg app_id "$FEISHU_APP_ID" \
            --arg app_secret "$FEISHU_APP_SECRET" \
            '{app_id:$app_id,app_secret:$app_secret}')

          token_response=$(curl --silent --show-error \
            --retry 3 \
            --retry-all-errors \
            --header "Content-Type: application/json" \
            --data "$token_body" \
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal")

          if [ "$(jq -r '.code // -1' <<< "$token_response")" != "0" ]; then
            echo "获取 tenant_access_token 失败：$(jq -r '.msg // "unknown error"' <<< "$token_response")"
            exit 1
          fi

          tenant_token=$(jq -r '.tenant_access_token // empty' <<< "$token_response")
          if [ -z "$tenant_token" ]; then
            echo "飞书没有返回 tenant_access_token。"
            exit 1
          fi

          content=$(jq -nc --arg text "$MESSAGE_TEXT" '{text:$text}')
          message_body=$(jq -n \
            --arg receive_id "$FEISHU_RECEIVE_ID" \
            --arg content "$content" \
            '{receive_id:$receive_id,msg_type:"text",content:$content}')

          http_code=$(curl --silent --show-error \
            --output response.json \
            --write-out "%{http_code}" \
            --retry 3 \
            --retry-all-errors \
            --header "Authorization: Bearer $tenant_token" \
            --header "Content-Type: application/json" \
            --data "$message_body" \
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id")

          if [ "$http_code" != "200" ]; then
            echo "飞书发送接口返回 HTTP $http_code。"
            exit 1
          fi

          if [ "$(jq -r '.code // -1' response.json)" != "0" ]; then
            echo "机器人发送失败：$(jq -r '.msg // "unknown error"' response.json)"
            exit 1
          fi

          echo "飞书机器人通知发送成功。"
```

**代码说明**：
- 第一段把 GitHub 事件整理成中文消息
- 第二段获取短期 Token，再调用飞书发送消息接口
- **不会输出 App Secret 或 tenant_access_token**（安全设计）

### 八~十二、提交、测试、验证

**Step 5：提交工作流** — Commit message: `Add GitHub repository monitor`

**Step 6：手动跑一次** — Actions → Repo Monitor → Run workflow → Run workflow
- Actions 显示绿色对勾
- 飞书收到"🧪 测试成功"消息

**Step 7：创建真实 Issue** — 验证 Issue 能否自动触发（不手动 Run workflow）

**Actions 检查四项**：
1. 事件显示 `on: issues`
2. 触发者正确
3. Build notification text 步骤成功
4. Send as Feishu bot 步骤成功

**飞书最终收到的消息格式**：

```
💡 新 Issue｜adrianpunk/repo-monitor-demo
测试：GitHub Issue 是否会触发飞书监控
https://github.com/adrianpunk/repo-monitor-demo/issues/1
```

### 十三、三个必须提前知道的坑

**1. 权限** — GitHub 保持只读，飞书只开 `im:message:send_as_bot`。如果以后要让机器人自动评论 Issue，再单独增加 `issues: write`，**不要顺手开 write-all**。

**2. Rate limit** — 飞书 API 有频率限制，高频推送需要做队列和去重。

**3. open_id 和可用范围** — open_id 属于具体应用，必须在应用的可用范围内才能收到消息。不同应用的 open_id 不同，不能跨应用复制。

### 十四、下一版：机器人先准备，我只负责确认

作者的升级愿景——从"通知我"升级为"**准备执行方案，等我确认**"：

```
新的 Issue / PR / Release
        ↓
机器人自动读取上下文、归类并生成处理建议
        ↓
飞书私聊：准备执行什么、为什么、会改动哪里
        ↓
我选择：确认执行 / 修改建议 / 跳过
        ↓
确认后写回 GitHub，并把结果发回飞书
```

**给 Codex 的升级 Prompt（原文照录）**：

```
请把当前 GitHub → 飞书监控机器人升级成"人工确认后执行"的版本。

要求：
1. 机器人可以自动读取 Issue、PR 和 Release 上下文；
2. 自动生成处理建议和准备执行的 GitHub 动作；
3. 先把建议发送到飞书，展示"确认执行 / 修改 / 跳过"；
4. 只有收到我的确认，才允许评论、打标签、分配负责人或创建 Draft Release；
5. 每次执行后，把操作结果和 GitHub 链接发回飞书；
6. 默认禁止自动合并 PR、关闭 Issue、删除内容和修改代码；
7. 为每类写入操作单独配置最小 GitHub 权限，并记录审计日志。

请先给出权限清单、确认流程和安全边界，再生成完整代码。
```

### 报错排查 Prompt

如果复制后出现错误，把工作流和报错截图发给 Codex：

```
我在搭 GitHub → 飞书应用机器人监控。

请检查这份 repo-monitor.yml：
1. GitHub Actions YAML 缩进；
2. App ID / App Secret 换取 tenant_access_token 的请求；
3. receive_id_type=open_id；
4. 飞书消息 content 是否被正确转成 JSON 字符串；
5. 日志是否会泄露 Secret 或 Token。

请给我完整可替换版本，不要省略代码。
```

---

## 查询拓展

- `pull_request_target` vs `pull_request` 事件触发器的安全差异？为什么用 target？
- 飞书 `tenant_access_token` 的有效期是多少？工作流每次都重新获取是否有 Rate limit 风险？
- 如何扩展为多用户通知（不同 Issue 路由到不同负责人）？
- 飞书交互卡片（confirm/reject 按钮）如何回传给 GitHub Actions？
- 如何用 GitHub Actions 的 `repository_dispatch` 实现飞书→GitHub 的反向控制？

---

## 归纳总结

这是一篇**面向非程序员的完整实操教程**——从创建飞书自建应用、配置 GitHub Secrets、编写 Actions 工作流到端到端验证，每一步都有截图和完整代码。

核心架构很简单：GitHub 事件触发 Actions → bash 脚本格式化消息 → 飞书 API 发送私聊。但文章的价值在于：
1. **最小权限原则**：GitHub 只读 + 飞书只 `send_as_bot`，不贪开权限
2. **安全设计**：Secret 不回读、Token 不输出日志
3. **人机协作愿景**：从"通知我"到"准备方案等我确认"——这正是 Human-in-the-loop Agent 的实践

---

## 趋势判断

- **GitHub → IM 通知是团队协作的基础设施**：但大部分人还在用邮件或全量通知，精准路由到人的方案是刚需
- **飞书自建应用 > Webhook 机器人**：自建应用能私聊、能交互卡片、能回调，比 Webhook 功能强一个量级
- **Human-in-the-loop Agent 是生产级模式**：作者下一版的"确认后执行"思路，与确定性护栏和 Agent 安全治理是同一理念——Agent 准备、人类确认、最小权限
- **非程序员用 Codex 搭 CI/CD**：作者明确说"我不会写代码"，整个流程用 Codex 辅助调试，这代表了 AI 辅助开发的趋势

---

## 关联分析

- **与 Hermes Agent 飞书集成的直接关联**：Hermes 已经接入飞书，这篇文章的 GitHub→飞书监控链路可以直接用 Hermes 的 `lark-im` Skill 实现——Hermes 作为飞书自建应用接收 GitHub Webhook，比 Actions+bash 更灵活
- **与用户 webhook-subscriptions Skill 的关联**：用户已有 `webhook-subscriptions`（创建和管理 webhook 订阅）Skill。这篇教程是 GitHub→飞书 webhook 的具体实现案例
- **与确定性护栏的关联**：作者的"权限分三档""不贪开 write-all""默认禁止自动合并/关闭/删除"原则，与用户的 `deterministic-guardrails` 和 `agent-security-governance` 技能完全一致
- **与 Human-in-the-loop 的关联**：下一版的"确认后执行"是 steer-hook（用户中途介入调整方向）和审批模式的实践版本
- **与 FDE 的关联**：这套 GitHub→飞书监控是企业 DevOps 标准需求，FDE 帮企业搭建 CI/CD 监控是高频交付场景

---

*笔记创建：2026-08-06 · 来源：@AdrianPunk115 X Article · 含完整原文代码*

## 相关笔记

- [OpenObserve-开源可观测性平台-Rust单二进制140x降本](2026-08-08-OpenObserve-开源可观测性平台-Rust单二进制140x降本.md)
- [深入理解AIAgent-设计原理与工程实践](2026-08-07-深入理解AIAgent-设计原理与工程实践-10章92实验.md)

---
