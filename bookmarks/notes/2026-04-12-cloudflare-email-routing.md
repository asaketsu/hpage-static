# Cloudflare Email Routing + Resend + Gmail 免费域名邮箱方案

> 来源: https://x.com/i/status/2042445928808972600 (sitinme)
> 日期: 2026-04-12

## 核心方案

独立开发者免费邮件架构：
- **Resend** → 发件（系统通知、Newsletter），免费3000封/月
- **Cloudflare Email Routing** → 收件（客服、商务），完全免费
- **Gmail Send As** → 回复时显示域名邮箱

## 关键配置步骤

1. Cloudflare Email Routing 把 support@ 转到 Gmail
2. Gmail 筛选器转发副本到飞书邮箱（存档/团队查看）
3. Gmail Send As 用 Resend SMTP 配域名邮箱发件身份
  - SMTP: resend 服务器，端口465 SSL，用户名 resend，密码=API Key

## 踩坑记录

- Cloudflare Done 按钮点不了 → 域名权限问题，需域名所有者账号
- 旧 MX 记录冲突 → 先删旧记录再开 Email Routing
- 飞书/企微邮箱不支持第三方 SMTP 别名 → 只能用 Gmail 配 Send As
- Send As 验证顺序：先配好 Cloudflare 转发 + Gmail 筛选器，再验证 Send As

## 成本

全免费。Cloudflare 无限制，Resend 免费3000封/月。

## 相关笔记
- [2026-04-17-cloudflare-mesh-tutorial](2026-04-17-cloudflare-mesh-tutorial.md) - Cloudflare Mesh 组网教程（WARP+Workers VPC）
