# The Book of Secret Knowledge — 系统运维与安全工具百科

- 📅 2026-05-24
- ⭐ 4.5/5 — 运维/安全领域最全面的开源工具索引，211KB 纯手工精选
- 🏷️ #运维 #安全 #工具集 #CLI #Shell #渗透测试
- 📰 GitHub
- 🔗 https://github.com/trimstray/the-book-of-secret-knowledge

## 摘要

trimstray/the-book-of-secret-knowledge 是一个纯 README 驱动的知识库项目，收录了 914 个精选链接，覆盖系统运维、网络安全、渗透测试、Shell 技巧等领域。整个仓库只有一个 README.md（4442 行，211KB），零代码，纯手工策展。1,069 次提交，社区活跃度高，PR 审核严格（"not everything but only good quality stuff"）。

## 内容结构

| 章节 | 行范围 | 核心内容 | 链接数(估) |
|------|--------|----------|-----------|
| **CLI Tools** | L111-380 | Shell/编辑器/网络/安全/审计/数据库 | ~130 |
| **GUI Tools** | L382-442 | 终端模拟器/网络工具/密码管理/加密通信 | ~30 |
| **Web Tools** | L443-710 | SSL检测/DNS/编码/性能/漏洞库/暗网搜索引擎 | ~120 |
| **Systems/Services** | L711-765 | 安全操作系统(HTTP/DNS/加固指南) | ~25 |
| **Networks** | L766-786 | 网络工具/实验室 | ~10 |
| **Containers/Orchestration** | L787-834 | Docker/K8s CLI+Web工具/安全/最佳实践 | ~25 |
| **Manuals/Tutorials** | L835-1016 | Shell/Python/Sed/Awk/加固/Web安全/电子书 | ~80 |
| **Inspiring Lists** | L1017-1095 | SysOps/DevOps/安全/开发 awesome lists | ~40 |
| **Blogs/Podcasts/Videos** | L1096-1230 | 安全播客/视频博客/Twitter账号 | ~60 |
| **Hacking/Pentesting** | L1231-1480 | 渗透工具集/后门/字典/Bug Bounty/CTF平台 | ~120 |
| **Daily Knowledge/News** | L1481-1518 | RSS/IRC/安全新闻源 | ~20 |
| **Cheat Sheets** | L1519-1660 | DNS服务器/Burp扩展/WAF绕过/浏览器技巧 | ~40 |
| **Shell One-liners** | L1661-4345 | 58个工具的实用命令行技巧 | ~250 |
| **Shell Tricks/Functions** | L4346-4442 | 反弹Shell清理/域名解析/ASN查询 | ~5 |

## 精华提炼

### 🎯 值得收藏的 One-liners

**进程诊断类：**
```bash
# 查看进程打开的所有文件
lsof -p PID

# 查看哪个进程占用了端口
lsof -i :PORT

# 追踪进程的系统调用
strace -p PID -e trace=network

# 限制进程CPU使用率
cpulimit -p PID -l 50
```

**网络诊断类：**
```bash
# 抓取HTTP流量并提取URL
tcpdump -s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'

# 快速端口扫描（不需要nmap）
timeout 1 bash -c '</dev/tcp/TARGET/PORT && echo PORT_OPEN || echo PORT_CLOSED' 2>/dev/null

# DNS区域传输尝试
dig axfr DOMAIN @NAMESERVER

# SSL证书信息
echo | openssl s_client -connect HOST:443 2>/dev/null | openssl x509 -noout -text
```

**安全工具类：**
```bash
# Nmap快速扫描Top 100端口
nmap -T4 --top-ports 100 -sV TARGET

# GPG加密文件
gpg -c FILENAME                          # 对称加密
gpg -d FILENAME.gpg                      # 解密

# 安全删除文件
dd if=/dev/urandom of=FILE bs=$(stat -c%s FILE) count=1 conv=notrunc
```

### 🔑 WAF绕过技巧（IP缩短）

```
http://1.0.0.1 → http://1.1
http://127.0.0.1 → http://127.1
http://192.168.0.1 → http://192.168.1
http://0xC0A80001 → 192.168.0.1（十六进制）
http://3232235521 → 192.168.0.1（十进制）
```

### 🧹 Shell反弹后清理技巧

拿到脏Shell后的标准化流程：
```bash
1) script /dev/null -c bash    # 启动干净shell
2) Ctrl-Z                       # 挂起
3) stty raw -echo; fg           # 恢复前台（获得pty）
4) reset                        # 重置终端
5) xterm                        # 设置终端类型
6) export TERM=xterm; export SHELL=bash
```

### 🔍 值得关注的工具（与Hermes体系相关）

| 工具 | 类别 | 与我们的关联 |
|------|------|-------------|
| **fzf** | Shell插件 | fuzzy finder，可用于Hermes skill搜索 |
| **fd** | 文件查找 | 替代find，更快更友好 |
| **ripgrep** | 内容搜索 | 已在用（Hermes search_files底层） |
| **nmap/RustScan** | 网络扫描 | 安全审计场景 |
| **jq** | JSON处理 | Hermes脚本中大量使用 |
| **httpie** | HTTP客户端 | 比curl更友好，API调试 |
| **ncdu** | 磁盘分析 | watchdog-full-system-check 可借鉴 |

### 📚 渗透测试学习路径（项目推荐）

1. **本地靶场**：DVWA、WebGoat、Juice Shop、Vulnhub
2. **在线CTF**：HackTheBox、TryHackMe、PentesterLab
3. **Bug Bounty平台**：HackerOne、Bugcrowd、Intigriti
4. **字典/Wordlists**：SecLists、fuzzdb

## 三档分类

### ① 有利进化（需落实）

- **Shell One-liners 中与运维/安全相关的高频命令** → 可抽取到 Hermes 安全/运维 Skill 的参考库
- **fzf/fd/ripgrep/jq 工具组合** → 已部分在用，确认可进一步集成到日常命令

### ② 有价值备用（Memory）

- **WAF绕过IP缩短技巧** → 安全测试场景备用
- **反弹Shell清理流程** → 红队场景备用
- **渗透测试靶场列表** → 未来安全学习路径参考

### ③ 知识库（仅笔记）

- CLI/GUI/Web工具索引 → 按需查阅
- Burp扩展推荐 → 专业渗透场景
- 浏览器/Firefox隐藏命令 → 日常效率

## 🔗 关联性

- [[red-teaming Skills]] — Hermes 已有的完整安全红队知识库（40+ Skill）
- [[watchdog-full-system-check]] — 系统健康检查，ncdu/磁盘分析可借鉴
- [[system-info]] — 系统信息展示

## 💡 启发

- 纯 README 知识库的策展模式：零代码、高信息密度、PR驱动质量把控，适合快速建立领域知识索引
- 58个Shell工具的 one-liner 按工具分类的组织方式，比按场景分类更适合速查
- 社区策展+严格审核（"only good quality stuff"）是维持大型工具索引质量的关键

## 🔮 预判

- 项目会继续膨胀（当前4442行/914链接），未来可能需要拆分为多文件
- 安全工具部分与 HackTricks 等新兴资源有重叠，但本项目侧重"列表索引"而非"教程详解"，定位不冲突
- Shell One-liners 段落是项目最有持久价值的部分，工具会过时但命令模式不会

## 相关笔记
- [Agent Skills才是关键抽象层](../2026-04-02-Agent Skills才是关键抽象层.md)
- [机器人仿真工具选择指南](../2026-05-22-机器人仿真工具选择指南.md)
- [150个任务30个Skill实测-7个反直觉结论](../2026-05-23-150个任务30个Skill实测-7个反直觉结论.md)
- [AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构](../2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md)
- [html-ppt-skill分析融合](../2026-05-24-html-ppt-skill分析融合.md)
- [CATIA-CAA-mkmk编译器Skill创建指南](../2026-05-25-CATIA-CAA-mkmk编译器Skill创建指南.md)
- [html-anything-analysis](2026-05-19-html-anything-analysis.md)
- [voicebox-flow-matching-next-gen-heavyweight-tts](2026-05-24-voicebox-flow-matching-next-gen-heavyweight-tts.md)
