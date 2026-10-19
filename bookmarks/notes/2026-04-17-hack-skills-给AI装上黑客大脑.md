# hack-skills：给 AI 装上黑客大脑的结构化安全知识库

- 📅 2026-04-17
- ⭐⭐⭐⭐⭐ 5/5 — 高质量安全技能框架，可直接吸收为 skill
- 🏷️ #安全测试 #RedTeam #hack-skills #yaklang #AI安全 #渗透测试 #Skill设计
- 📰 公众号：攻防路
- 🔗 https://mp.weixin.qq.com/s/IlQV08opoZXB8gFiy0MaZg
- 📦 https://github.com/yaklang/hack-skills

## 核心内容

### 设计理念：不是字典，是"路由表"

传统 payload 字典的问题：LLM 面对新目标不知道先做什么，测到一半不会路由到合适的攻击面。

hack-skills 解决方案：三层结构 + 路由表

```
Master Entry（总入口 hack）
  └── Category Entries（6 个类别入口）
        └── Deep Topic Skills（100+ 专题技能）
```

**路由表设计**（这是最核心的创新点）：

| 观察到的现象 | 路由到的攻击方向 |
|---|---|
| 输入反射到 HTML/JS | XSS / SSTI |
| 服务端主动访问 URL | SSRF |
| 接收 XML / Office / SVG | XXE |
| 路径、文件名下载接口可控 | Path Traversal / LFI |
| API 中大量对象 ID | IDOR / BOLA / BFLA |
| 登录、找回密码、2FA | Auth Bypass / JWT / OAuth |
| 多步骤交易、优惠券、库存 | Business Logic |
| 命令行工具、图像处理、导入器 | Command Injection |
| Node.js `__proto__` 可控 | Prototype Pollution |
| 一次性操作（优惠券/重置） | Race Condition |
| `.git/.svn/.env` 路径可访问 | Insecure SCM |

### 覆盖范围（14 个安全领域）

- **Web 与 API 安全**: XSS, SQLi, SSRF, SSTI, XXE, 命令注入, 反序列化, JNDI, CRLF, HTTP Smuggling, Prototype Pollution
- **认证与授权**: JWT/OAuth 攻击, SAML SSO 伪造, IDOR/BOLA
- **基础设施与提权**: Linux/Win/Mac 提权, AD (Kerberoasting/ACL/AD CS ESC1-8), 容器逃逸, K8s, 横向移动
- **二进制与逆向**: Stack Overflow + ROP, 堆利用, 内核利用, V8, 沙箱逃逸, 符号执行
- **密码学攻击**: RSA (共模/低公钥/Coppersmith), 格密码分析, 哈希攻击
- **新兴领域**: LLM Prompt Injection, AI/ML 安全, 智能合约, DeFi 攻击

### 六个类别入口

1. `recon-for-sec` — 侦察与方法论
2. `api-sec` — API 安全
3. `auth-sec` — 认证与授权
4. `injection-checking` — 注入攻击
5. `file-access-vuln` — 文件与路径攻击
6. `business-logic-vuln` — 业务逻辑与会话

### 蒸馏原则（从海量资料到结构化技能）

知识来源：PayloadsAllTheThings, PentesterSpecialDict, Hello-CTF, ctf-wiki, hacktricks

关键区别：**不是镜像，是二次加工**
- 砍掉直接的 payload 字典复制
- 保留分类框架、边界条件描述、攻击链路逻辑
- 把"先想清楚方向，再按需取用"的框架给 Agent

### 安装方式

```bash
# 方式一：skills CLI
npx skills add yaklang/hack-skills

# 方式二：直接拉主入口
curl -fsSL https://raw.githubusercontent.com/yaklang/hack-skills/main/skills/hack/SKILL.md

# 方式三：克隆
git clone https://github.com/yaklang/hack-skills.git
```

## 关键洞察

**"路由表"思维**：安全测试的核心不是"知道多少 payload"，而是"面对一个场景知道该测什么"。路由表设计精准解决了 LLM 安全测试时"不知道先做什么"的问题。

**蒸馏 vs 镜像**：不是堆 payload，而是给 Agent 结构化方法论上下文。这个思路和我们的 Skill 体系完全一致 — SKILL.md 不是代码仓库，是操作指南。

**按需加载**：主入口 → 类别入口 → 深层专题，渐进式披露。避免一次性把所有 payload 倒进上下文窗口，降低推理质量。

## 启发与借鉴

1. **路由表模式可泛化**：不只安全领域，任何"面对复杂场景需要决策先做什么"的场景都适用路由表
2. **蒸馏原则**：知识管理不是"存下来"，而是"加工成可用的结构"
3. **三层结构**：入口 → 分类 → 深层，渐进式披露，与我们的 skill 层级天然契合
4. **与我们 red-teaming skill 互补**：godmode 专注越狱/安全绕过，hack-skills 专注攻击面识别和测试方法论

## 相关笔记
- [2026-04-09-SKILL-md-ai-agent-skills](2026-04-09-SKILL-md-ai-agent-skills.md) - SKILL.md 与 Agent Skills 设计
- [2026-04-02-Agent Skills才是关键抽象层](2026-04-02-Agent Skills才是关键抽象层.md) - Agent Skills 关键抽象层
