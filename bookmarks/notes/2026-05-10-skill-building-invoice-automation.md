# 手把手从0搭建一个实用Skill：邮箱→报销单自动化实战

来源：微信公众号
链接：https://mp.weixin.qq.com/s/_Vh2wgKuKic52UmQpCOYDA
日期：2026-05-10
评分：⭐4.5/5
标签：#Claude-Code #Skill构建 #自动化 #发票处理 #实战 #方法论
关联：[himalaya](../../.hermes/skills/email/himalaya/SKILL.md) [verification-gate](../../.hermes/skills/software-development/verification-gate/SKILL.md) [2026-05-10-claude-learning-roadmap](2026-05-10-claude-learning-roadmap.md)

## 摘要

作者用 Claude Code 从零搭建发票自动化 Skill，解决每月底手动整理报销单的痛点。文章完整记录了从需求分析、架构设计、踩坑到端到端验证的全过程。核心价值不在发票场景本身，在于 Skill 构建的方法论和实战踩坑经验。

## 核心内容

### 1. 架构设计先行

关键决策在写代码前拍板：
- 拆成两个独立 Skill：qq-invoice-fetch（抓取）+ invoice-organize（整理）
- 理由：单一职责，换邮箱只改抓取不改善理
- 邮箱授权码存 .env + gitignore
- 跑完不自动接整理，先让用户确认落盘
- 链接型邮件自动跟，跟不到列 URL
- 落盘目录按 --since 的月份走

> 先聊架构再写代码，能省 80% 返工

### 2. 踩坑实录

**坑1：QQ IMAP SEARCH 括号 Bug**
- `(SINCE "01-Apr" BEFORE "26-Apr")` → 返回 9740 封（BEFORE 被吞）
- `SINCE "01-Apr"` `BEFORE "26-Apr"` → 返回 116 封（正确）
- 无文档的 bug，只能用脚本逐条试出来

**坑2：PDF/OFD 互相覆盖**
- 中国电子发票同一张有 PDF 和 OFD 两种格式，发票号相同
- 去重 key 用发票号 → PDF 全被 OFD 覆盖（OFD 读不了内容）
- 修复：去重 key 改成 (发票号, 扩展名)

**坑3：链接型邮件**
- 12306/滴滴/京东不发 PDF，发链接
- 处理链：解析 HTML → 找 a/iframe → 过滤关键词 → 带 UA 抓 → 验证 Content-Type → 跟 1 跳 → 跟不到列 URL
- 京东特殊：发 .xml 链接（电子发票全字段），需单独提示用户去 App 重发 PDF

### 3. PDF 信息抽取流程

用 Claude Code 的 Read 工具直接读 PDF（渲染成图+文字），逐张抽取：
- 发票号（去重主键）
- 开票日期/消费日期（铁路票常常不同）
- 销售方名称
- 项目名称（铁路票格式："中国铁路 + 车次 + 起止站"）
- 类别（交通/餐饮/住宿/办公用品/其他）
- 价税合计（取小写值，不用"合计"——后者不含税）

抽取结果 JSON → make_xlsx.py（openpyxl 模板）→ 蓝色表头/金额格式化/合计行红色加粗的 Excel

### 4. 强制规则

- 剔除个人抬头发票（购买方栏写人名而非公司）
- 自动识别 + 剔除，备注里逐张列出让用户知情

### 5. 端到端验证

3 个月实测数据：
363 封邮件 → 62 封候选 → 44 张唯一发票 → ¥8,861.69

月底两小时手敲 → 两条命令 + 一次 review

## 可进化内容（已融合到体系）

| 内容 | 融合位置 | 状态 |
|------|----------|------|
| Skill 拆分原则（单一职责） | memory: Skill构建方法论 | ✅ |
| 先聊架构再写代码 | memory: Skill构建方法论 | ✅ |
| 去重 key 设计思路 | memory: Skill构建方法论 | ✅ |
| 链接型内容处理链 | memory: Skill构建方法论 | ✅ |
| PDF 信息抽取模式 | memory: Skill构建方法论 | ✅ |
| QQ IMAP 括号 bug | skill: himalaya QQ邮箱坑点 | ✅ |
| PDF/OFD 去重坑 | skill: himalaya QQ邮箱坑点 | ✅ |

## 关键洞察

1. "先聊架构再写代码"不仅是建议，是 Skill 构建的铁律。作者花了整个下午，架构讨论占了一大半时间，但代码写得极快
2. 无文档 bug（QQ IMAP 括号问题）只能靠"写脚本逐条试"——这是 AI 辅助编程的真实场景，不是所有问题都能搜到答案
3. 去重 key 的设计反映了"什么算重复"这个问题的本质思考——不是越严越好
4. 强制规则（剔除个人抬头）体现了"让系统做用户不想做但必须做的事"的理念

## 对我们的启发

1. 我们的 himalaya skill 已有 QQ 邮箱坑点记录，这篇文章补充了 IMAP SEARCH 的坑
2. Skill 构建方法论与我们现有的 verification-gate（三级验证）互补：先规划→再实现→再验证
3. PDF 抽取模式可直接复用到任何需要从文档提取结构化数据的场景
4. 链接型内容处理链是一个通用模式，值得抽象成独立 skill（如果后续有类似需求）

## 预判

- 短期：QQ IMAP 括号 bug 这个知识点，未来如果用户需要邮件自动化会直接用到
- 中期：发票自动化 Skill 可作为模板，任何"定期重复→自动化"的场景都适用
- 长期：Skill 拆分+单一职责的方法论，会影响我们整个 Skill 体系的设计方向

## 相关笔记
- [softwarecopyright-skill-analysis](2026-05-10-softwarecopyright-skill-analysis.md)
- [nTop-Automate-CLI-完整测试文档](2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](2026-05-15-数据目录工具全景指南.md)
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
