# Grok Bot 云电脑跑 Claude Code：Tailscale 组网与自愈架构全解

> 来源: X @app_sail (Asa) · 2026-10-09 · 56万views · [原文](https://x.com/app_sail/status/2108523630900748335)
> 作者: Asa — Partner @chuhaiqu @tuttihq · ex-Zhihu · AI Builder/LLM Agent 开发者
> 读法: 本文是"把文章丢给 Grok Bot 让它自己执行"的可执行教程——人类只做 6 件确认类动作，其余全由 agent 完成

`#ClaudeCode` `#GrokBot` `#Tailscale` `#Orca` `#自愈架构` `#Agent工程` `#云端开发机`

## 归纳总结

在 Grok Bot 自带的美国云电脑（8核/16GB/无 systemd）上搭建 7×24 在线 Claude Code 环境的完整工程方案：三层架构=云电脑跑 Claude Code + Tailscale 组网（主机名配对）+ Orca Remote Server 会话管理（6768 端口仅 tailnet 内可达），Mac/手机随时接入同一会话。核心哲学：**与其伪装环境骗风控，不如让环境本身名副其实**（真美国机器+美国出口+美国时区，注册到使用全程在这台机器）。工程核心是**自愈三件套对抗平台换实例**：Grok Bot 自动更新会换全新实例（home 外全清），解法=凡装在 home 外的东西，home 内必留安装包+恢复脚本+定时拉起任务。附 8 个真坑的根因与修法，以及一套写给 agent 的执行规约（每步停报/人不代做/幂等/不杀活进程/密钥不进对话）。

## 内容整理：三层架构与四步搭建

```
[Mac/iPhone Orca 客户端] ──Tailscale(MagicDNS: grok-bot)──> [云电脑 orca serve :6768]
                                                              └─ Claude Code (~/.claude/ 登录态)
[Grok Bot 对话框] ──orca CLI──> 同一批会话（看/催/派活/汇总）
```

| 步骤 | 内容 | 谁做 |
|---|---|---|
| 1. Tailscale | 现成 Bot 一键装：装 tailscale+SSH、看门狗、5min 自愈定时任务、密钥 21 天过期提醒、ACL 锁死仅自己设备 | Bot（人点授权+贴 ACL） |
| 2. Claude 注册订阅 | 全程在云电脑浏览器完成（不碰本机网络）；官方脚本装 Claude Code 到 ~/.local（home 内，更新后还在） | 人（Grok Bot 开页面交控制权） |
| 3. Orca | AppImage 放 home；6768 防火墙三规则（lo 放行/tailscale0 放行/DROP）；每 10min 定时拉起 | Bot |
| 4. 设备接入 | Mac 粘配对链接，手机扫专用码（两种凭据不可混用） | 人 |

**日常形态**：人在外只跟 Grok Bot 说话 → 它用 `orca worktree ps / terminal send / wait --for tui-idle / read` 指挥云电脑上的 Claude Code 干活并回传三行总结。

## 内容整理：自愈架构（本文最高工程价值）

**平台事实**：Grok Bot 自动更新=换新实例，无预告。apt 包、/opt、/usr/local/bin、/var/lib/tailscale、开机脚本改动全清；home 里 root-only 文件也不回来；正在干活的 agent 被直接打断。

**对策模式**（home 内自愈三件套）：
1. 安装包留在 home（官方脚本装 ~/.local 而非 npm -g；AppImage 而非 .deb）
2. 恢复脚本在 home（bootstrap-tailscale.sh / orca-serve.sh，均幂等可重复执行）
3. 定时任务拉起（Tailscale 5min / Orca 10min；更新后通常几分钟自动恢复同一节点同一 IP）

**配对用主机名不用 IP**（Tailscale 重登录=新节点=IP 变，主机名 grok-bot 不变则免重新配对）。

## 内容整理：8 个真坑速查

| 坑 | 根因 | 修法 |
|---|---|---|
| Mac 连不上 | Tailscale 重登录→IP 变，配对存的旧 IP | 用主机名配对+保登录态 |
| 更新后全没 | 换新实例，home 外全清 | 自愈三件套；备份改 box 所有 600 权限（root-only 文件快照不还原） |
| 新看门狗起不来 | flock 锁 fd 被 orca serve 继承，锁不释放 | 子进程启动加 `9>&-` 关锁 fd |
| 每天掉线数次 | 沙箱网络特性，控制面报离线 | 看门狗查"控制面认为在线"而非只查进程 |
| Orca 里又让登录 | 命令行登录≠交互向导走完 | `~/.claude.json` 的 `hasCompletedOnboarding=true`（先备份） |
| 更新后 6768 裸奔 7 分钟 | iptables 是装 Tailscale 时带装的，跟它一起没了 | 脚本自己 apt 装 iptables；**规则设不好宁可不起 serve（fail-closed）** |
| pkill -f orca 团灭 | 一个进程管所有会话 | 只用 `orca-serve.sh --restart` |
| AppImage 直接跑留死挂载 | 无 /etc/mtab | 用 `orca-serve.sh --version` 或解包后二进制 |

零碎但值钱：改运行中的脚本要原子替换（bash 边读边执行，先写临时文件再 mv -f）；pgrep -f 会把执行命令的 shell 自己数进去；开机钩子不能加在脚本末尾（后面有 exec/wait 永不执行）。

## 内容整理：写给 agent 的执行规约（可复用的 agent 工程范式）

1. 按序执行，每步完成停下汇报，等"继续"再做下一步
2. 标"需要人"的事不代做不绕过（授权/订阅/配对/扫码），把链接交给用户然后等
3. 先看现状再动手；所有脚本幂等，重复执行不破坏
4. 不杀运行中的 orca serve/tailscaled，不动别的 agent 的终端
5. 端口不暴露公网（6768 仅 tailnet 内）
6. 附录脚本原样保存，不重写不"顺手优化"；报错就交输出给人，不改了硬跑
7. 与文章描述不符就停下来问（找不到文件/无免密 sudo/系统不对），不猜替代方案
8. 汇报不贴配对码/密钥/状态文件内容

日常用法四条：派活流程存成 skill（免得每次解释"找终端→发指令→等空闲→读回"）；多 bot 只留一个总管分派汇总；**事先写明"调研/起草/测试/整理自动跑，发送/发布/花钱/改生产必须回到人"**；每天自动查 `claude auth status` + 随机时刻发 hello 探活记账。

## 💡 价值分析：对我们的启发

### ✅ 已在做的（交叉验证）
- **权限边界同构**："发送/发布/花钱/改生产必须回到人"= 我们的 [ACTION REQUIRED] 生产授权红线——两个独立系统的同一结论
- **fail-closed**：iptables 设不好宁可不起 serve = 今天刚修的"数据拿不到≠空仓"（DATA_DEGRADED）同款思想
- **看门狗+定时拉起** = 我们的 hermes-disaster-recovery / monitor_script 模式；"查控制面在线而非只查进程"= 健康检查要查真值不只查进程存在
- **pgrep -f 自计数坑**我们踩过两次（memory 在案），本文独立复证——通用坑
- **每步停报等确认** = 我们真机测试的"动作前告知+目视确认"铁律

### 🔥 重点行动
1. **检查我们的 flock 看门狗**：e29_watchdog.sh 等用 flock 的脚本，子进程是否继承了锁 fd（9>&- 缺失=看门狗死后新看门狗起不来）——今天就该查
2. **"环境名副其实"哲学迁移**：与其对抗风控不如消除伪装面——对我们的启示是免费 API 四线的账号健康管理（每日探活+auth status 检查的自动化）
3. **agent 执行规约收编**：这 8 条比我们很多 skill 里的散规约更精炼，值得作为"委托执行类任务"的标准前导词模板
4. **原子替换运行中脚本**：我们的 cron 脚本热更新场景（launch heredoc 重写）适用"临时文件+mv -f"

### ⚠️ 保持怀疑的
- 共享出口 IP（Cloudflare 弗吉尼亚）已有评论区反馈注册秒封——"环境名副其实"降低了伪装风险但没消除 IP 信誉风险，作者自己也承认没法替别人验证
- Grok Bot 16GB 内存开 3-4 个 Claude Code 会话已用 12GB——承载上限低，重度多项目要 VPS
- 平台随时换实例+随时打断任务——**生产级工作不适合**，作者也把"重要代码及时推 git"列为铁律

## 📊 趋势判断

这篇文章标记了 2026 年 agent 环境工程的新形态：**算力普惠让"云电脑+组网+自愈"取代"本地主机+配置"成为 agent 的默认载体**——Grok Bot 白费送美国云电脑只是开头，竞争会从模型能力转向"谁送的托管环境更可用"。三个信号：①教程以"丢给 agent 自己执行"为默认读法（人类只做 6 个确认动作）——执行主体已经换人；②自愈架构对抗平台不可控性成为标准功课（类似早期 Heroku dyno 重启文化）；③Orca/Tailscale 这类"会话层+组网层"中间件兴起，agent 的接入界面从终端变成聊天框。风险面：平台条款的灰色地带（Grok Bot 云电脑跑竞家 Claude）与共享 IP 信誉是悬顶之剑。

## 🔍 查询拓展

- Orca 的 orchestration 多 agent 协调（一文里"多模型设计评审团"玩法）
- Tailscale ACL 语法与 tailnet 最小权限配置
- AppImage 无 systemd 环境的服务化管理模式对比（flock+cron vs supervisor）
- Claude Code 的 ~/.claude/ 登录态结构与多设备会话语义
- Grok Bot 云电脑实例快照机制（哪些目录 guaranteed 还原）

## 🛠️ 指南分析

- 复刻路径：加 Tailscale Bot → 云电脑内注册订阅 → AppImage 装 Orca → 设备配对，四步约 1-2 小时（人的动作 6 个）
- 排障顺序：先跑 check-after-update.sh（只读自检逐项 ✅/❌ 带修复命令）→ 看 serve.log 的 Advertised endpoint → 看门狗日志
- 升级 Orca：覆盖 AppImage + `--restart`，挑无任务跑时做（后台终端守护进程续用旧版直到自重启）
- 迁移 VPS：四步不变，看门狗换 systemd 服务，更稳

## 🔗 拓展应用推荐

- 我们的 watchdog 系脚本今天做 9>&- 缺陷排查（flock fd 继承）
- "每日 auth 探活+记账"模式移植到免费 API 四线的账号健康 cron
- agent 执行规约 8 条作为 delegate_task 委托模板的标准 context 前导
- Orca 式"会话可视层"思路：我们的 session 状态展示（谁在干活谁在等）可借鉴 worktree ps 的粒度

## 关联分析

本文与我们系统的四层互证：①权限哲学——"发送/发布/花钱/改生产回到人"与 [ACTION REQUIRED] 红线同构；②自愈工程——home 内三件套 vs 我们的 hermes-disaster-recovery（进程守护+自动备份+一键恢复），共同教训是"平台不可控性必须用幂等恢复脚本+定时拉起消化"；③坑库互证——pgrep -f 自计数/原子替换脚本/fail-closed 三坑双方独立踩到，说明是 agent 环境的通用地雷而非个案；④agent 规约——每步停报等确认=真机测试目视确认铁律。差异面：我们单机自管（Jetson+pi5）vs 作者平台托管（Grok Bot 云电脑），他们的核心风险是平台换实例，我们的核心风险是硬件断电/SD 损坏——自愈对象不同但模式同构。

## 相关笔记

→ 相关：2026-10-14-Gemini4Argon深度实测-写作强于代码的百万输出模型.md（三巨头格局的第三块拼图：xAI 生态的云电脑能力）
→ 相关：2026-10-11-AI-Agent生产化十套范式（agent 执行规约与生产化范式同频）
