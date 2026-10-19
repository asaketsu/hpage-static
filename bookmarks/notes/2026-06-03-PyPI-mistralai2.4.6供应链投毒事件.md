# PyPI mistralai 2.4.6 供应链投毒事件

- 📅 2026-06-03
- ⭐ 5/5 — **直接影响 AI 开发者环境，Hermes Agent 安全相关**
- 🏷️ #安全 #PyPI #供应链攻击 #mistralai #后门
- 📰 windom Yu / AI产品实践手记
- 🔗 https://mp.weixin.qq.com/s/F3MYY6a4rnf67GouLMJVBg

## 事件摘要

2026年5月11日，攻击者通过劫持 GitHub Actions 构建流程，在 PyPI 发布了一个**伪造的 mistralai 官方 SDK 版本 2.4.6**。该版本带有有效的 SLSA Build Level 3 签名，绕过所有安全校验。用户只要 `import mistralai` 即可触发后门。

**攻击团伙：TeamPCP**，属于 "Mini Shai-Hulud" 蠕虫攻击，共投毒 **170+ npm + PyPI 包**。

## 后门行为

| 阶段 | 行为 |
|------|------|
| 触发 | `import mistralai` 自动执行（无弹窗、无提示） |
| 下载 | curl 从硬编码 IP 下载 `/tmp/transformers.pyz`（伪装 HuggingFace 库名） |
| 执行 | 静默运行，stdout/stderr 全部丢弃，独立进程 |
| 扫描 | 凭据文件、数据库密钥、API Key、GitHub PAT、加密货币钱包、飞书/钉钉 bot token |
| 驻留 | 后台持续监听，非一次性窃取 |
| 自毁 | 地理围栏：IP 在以色列/伊朗境内，1/6 概率执行 `rm -rf /` |
| 死亡开关 | 创建 npm token，描述 "IfYouRevokeThisTokenItWillWipeTheComputerOfTheOwner" |

## 绕过机制

- **SLSA Build Level 3 来源证明**：签名真实，PyPI/npm 安全校验通过
- **OIDC token 劫持**：用被劫持的 GitHub Actions 凭证"合法"发布
- **GitHub 400+ 恶意仓库**：每仓库均标注 "Shai-Hulud: Here We Go Again"

## 环境排查（本机器结果）

```
pip show mistralai → 未安装 ✅
/tmp/transformers.pyz → 不存在 ✅
pip list mistral → 无相关包 ✅
```

**结论：本环境未中招。**

## 行动建议

### 立即执行（所有 AI 开发者）

1. **检查版本**：`pip show mistralai` — 若版本为 2.4.6 立即卸载
2. **检查后门文件**：`ls /tmp/transformers.pyz` — 若存在说明已中招
3. **中招后**：卸载包 + 删除文件 + **轮换所有凭据**（API Key、GitHub PAT、SSH 密钥、云凭证、bot token）

### 长期防御

| 措施 | 说明 |
|------|------|
| 锁定依赖版本 | requirements.txt 明确版本号，禁止模糊依赖 |
| 定期轮换密钥 | GitHub PAT、API Key 至少每90天轮换 |
| 隔离 Agent 环境 | Agent 运行环境使用最小权限，密钥不硬编码 |
| 记忆系统记录 | 将有毒包版本写入 Agent 记忆，跨会话自动预警 |
| 供应链审计 | 使用 `pip-audit` / `safety` 定期扫描依赖 |

## 💡 笔记者批注

1. **AI 开发者是高价值目标**：模型 API 密钥、Agent 配置、长期运行的服务器，攻击者明确知道这些值钱
2. **签名=安全 是错觉**：SLSA Level 3 签名被绕过，说明供应链攻击已从"伪造签名"升级到"劫持签名流程"
3. **Hermes Agent 的记忆系统正是防御利器**：将有毒包信息写入记忆，跨会话自动提醒，比人工记忆靠谱得多
4. **本事件验证了"分析学习进化"的价值**：安全情报必须被 Agent 吸收并转化为可执行的防御动作，而非仅停留在"知道"层面

## 相关笔记

- [[2026-05-21-GitHub仓库被恶意扩展入侵]] — 供应链安全同类事件
- [[2026-05-05-网络安全-AI安全自动化SOC]] — AI 安全防御体系
- [[2026-05-16-AI威胁检测突破2026]] — AI 威胁检测前沿
