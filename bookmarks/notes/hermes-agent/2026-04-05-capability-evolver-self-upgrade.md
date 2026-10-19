# OpenClaw 自我升级：capability-evolver 技能解析

来源：微信公众号
链接：https://mp.weixin.qq.com/s/CxMtFW3gfGZMlPpYVO8NMw
日期：2026-04-05
评分：⭐⭐⭐⭐（4/5）

## 核心内容
capability-evolver 是 ClawHub 下载量第一的技能（35000+ 安装），定位"元技能"——不帮做具体事，而是帮 AI 提升做所有事的能力。

**原理**：定期让 OpenClaw 回顾近期对话，找出规律，自动更新行为规则文件（CLAUDE.md）。用户不用手动写规则，AI 自己从纠正行为中归纳。

**三个场景**：
1. 写作者：自动学习文字风格偏好（短句、不用列表格式等）
2. 开发者：自动学习技术偏好（TypeScript only、函数式风格等）
3. 坏习惯修复：从纠正行为中归纳并一次性修掉（如"当然！"开头、绕弯子）

**机制**：默认每 50 轮对话触发一次自我分析，可调。修改项目根目录 CLAUDE.md。

## 与我们 evolver 的对比

| 维度 | capability-evolver | 我们的 evolver |
|------|-------------------|----------------|
| 规则文件 | CLAUDE.md（单文件） | rules/ 多文件（10个） |
| 触发方式 | 每 N 轮对话 | cron 扫描（每日4次日梦） |
| 检测范围 | 对话中的纠正模式 | 7天重复错误≥2次 + rules库存 |
| 输出 | 行为规则（风格偏好） | 进化规则（错误模式+改进） |
| 安装量 | 35k+ | 自研，无公开数据 |

## 启发与借鉴

1. **轮数触发机制 → 补充我们的 cron 触发**：我们只靠 cron 定时扫描，缺少对话轮次触发。可以在记忆 cron 中增加"连续 N 次被纠正同类问题后立即触发 evolver"，不等到日梦扫描
2. **CLAUDE.md 单文件模式 → 轻量级偏好积累**：他们直接改单文件更简单。我们的 rules/ 更结构化但更重。可以考虑在 permanent/user.md 中增加一个"自动积累的偏好"区域，由 evolver 自动维护，类似轻量版
3. **"不做说明书"理念验证**：我们已经在做这件事（SOUL.md Hook 1 自动捕获），但他们的 35k 下载量证明这个方向是对的——用户确实不想手写规则
→ 相关：2026-04-05-Karpathy-LLM-Wiki第二大脑.md（知识编译+月度编译cron）
→ 相关：2026-04-05-Hermes-Agent竞品分析.md（闭环学习/skill自动创建竞品对标）
→ Related: 2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md

→ 相关：2026-04-09-SKILL.md模式-AI智能体技能.md
→ 相关：2026-04-06-AI-Scientist-v2.md（自主科研Agent对比）

## 相关笔记
- [SelfImproving-Agent-CLI-infra](2026-04-05-SelfImproving-Agent-CLI-infra.md)
- [SkillClaw-analysis](2026-05-02-SkillClaw-analysis.md)
- [Mnemosyne-零依赖AI记忆系统](2026-05-05-Mnemosyne-零依赖AI记忆系统.md)
