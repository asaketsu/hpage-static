# Hermes Agent Skills 闭环系统源码深度拆解

> 来源：微信公众号「腾讯云开发者」
> 链接：https://mp.weixin.qq.com/s/yHva-zLaRTxe8b4HSUr86Q
> 日期：2026-04-15

## 核心定位

Nous Research Hermes Agent（71.8K Stars）Skills 闭环系统的完整源码级拆解——从经验提取到知识存储到智能检索到自动改进的 7 模块闭环，是当前开源 Agent 框架中唯一内置自学习机制的实现。

## 01 闭环全景：7 模块数据流

```
[经验提取] → [原子写入+扫描] → [两层缓存索引]
     ↑                                      ↓
[Fuzzy Patch 更新] ← [User Message 注入] ← [条件激活]
```

本质：让 AI Agent 像人类专家一样积累经验——把成功做法写成 SOP，使用中持续修订，可分享。

## 02 Skill 创建：经验蒸馏

### 自主触发条件（System Prompt 编码）

```python
SKILLS_GUIDANCE = (
    "After completing a complex task (5+ tool calls), fixing a tricky error, "
    "or discovering a non-trivial workflow, save the approach as a "
    "skill with skill_manage so you can reuse it next time.\n"
    "When using a skill and finding it outdated, incomplete, or wrong, "
    "patch it immediately with skill_manage(action='patch') — don't wait to be asked. "
    "Skills that aren't maintained become liabilities."
)
```

**哲学**：过时 Skill 比没有 Skill 更危险（liabilities）。

### 七道安全关卡

| 关卡 | 检查内容 |
|:---|:---|
| 1. 名称验证 | 小写/数字/连字符，≤64字符，FS 安全 |
| 2. 分类验证 | 单层目录，无路径穿越 |
| 3. Frontmatter 验证 | YAML 头必须有 name + description |
| 4. 大小限制 | ≤100,000 字符（≈36K tokens） |
| 5. 名称冲突 | 跨所有目录去重 |
| 6. 原子写入 | tempfile + os.replace() 防崩溃损坏 |
| 7. 安全扫描 | 90+ 威胁模式，失败则整个目录回滚删除 |

### 两个关键工程决策

1. **原子写入**：先写 tempfile 再 `os.replace()` 原子替换——崩溃不会出现写一半的损坏文件
2. **写入后扫描**（非扫描后写入）：避免 TOCTOU 竞态，扫描的是文件系统最终状态

### Skill 文件格式

YAML Frontmatter + Markdown Body（agentskills.io 社区标准）：
- Frontmatter：`platforms`、`requires_toolsets`、`fallback_for_toolsets`、`config` 驱动条件激活
- Body：触发条件、执行步骤、常见陷阱、验证方法

## 03 索引构建：两层缓存

| 缓存层 | 命中耗时 | 场景 |
|:---|:---|:---|
| Layer 1: 进程内 LRU (max=8) | ~0.001ms | 热路径：同一对话内多次访问 |
| Layer 2: 磁盘快照 (mtime+size manifest) | ~1ms | 冷启动：进程重启但 Skill 没变 |
| 全扫描 | 50-500ms | Skill 文件变化后首次访问 |

缓存键是五元组：`(skills_dir, external_dirs, available_tools, available_toolsets, platform_hint)`

**磁盘快照验证**：不对比内容（太慢），而是对比每个 SKILL.md 的 mtime + size。

## 04 条件激活：智能可见性控制

```python
# fallback_for: 主工具可用时隐藏 fallback skill
# requires: 依赖工具不可用时隐藏 skill
def _skill_should_show(conditions, available_tools, available_toolsets):
    for ts in conditions.get("fallback_for_toolsets", []):
        if ts in available_toolsets: return False
    for t in conditions.get("requires_tools", []):
        if t not in available_tools: return False
    return True
```

还有平台过滤：`platforms: [macos]` 的 Skill 在 Linux Gateway 不显示。

**目标**：控制索引膨胀，减少无关 Skill 的 token 消耗。

## 05 渐进式加载（Progressive Disclosure）

| 层级 | 内容 | Token 开销 |
|:---|:---|:---|
| Tier 1: System Prompt 索引 | 每个 Skill 一行（名称+描述，≈20 tokens） | 100 个 Skill ≈ 2000 tokens |
| Tier 2: skill_view() 按需加载 | 完整 SKILL.md 内容 | 仅加载时消耗 |
| Tier 3: 支撑文件按需加载 | references/、templates/、scripts/ | 按需消耗 |

**安全性**：
- Prompt Injection 检测（"ignore previous instructions" 等模式）
- 路径穿越防护（`../../.env` 被拦截）
- 环境变量依赖检查与交互式收集

## 06 注入策略：User Message 而非 System Prompt

**最关键的架构决策**：Skill 内容作为 User Message 注入，不修改 System Prompt。

**原因**：Prompt Cache。Anthropic 的缓存要求 System Prompt 在整个对话中不变。如果每次加载 Skill 就改 System Prompt，缓存失效 → 每轮重处理 → 成本数十倍增加。

**权衡**：User Message 指令跟随权重略低于 System Prompt，但通过 `[SYSTEM: ...]` 前缀标记 + System Prompt 中 "you MUST load it" 强制措辞弥补。

**铁律**（AGENTS.md）：`Do NOT alter past context mid-conversation, change toolsets mid-conversation, or reload memories or rebuild system prompts mid-conversation.`

## 07 自改进机制：闭环的闭合点

### 触发（System Prompt + Tool Schema）

```python
"If a skill you loaded was missing steps, had wrong commands, or needed
pitfalls you discovered, update it before finishing."
"patch it immediately"
```

### Fuzzy Match 引擎

LLM 回忆内容常有微小格式差异（空格/换行/缩进），fuzzy_find_and_replace 处理：
- 空白规范化
- 缩进差异
- 转义序列
- 块锚匹配（内容开头/结尾的特殊处理）

### 级联效应

Patch 成功 → 清除 LRU 缓存 + 磁盘快照 → 下一个对话加载更新版 Skill

**最终一致性模型**：
- 当前对话：用旧版 Skill，发现问题并 patch
- 下一个对话：缓存失效，加载更新版
- 后续对话：都用改进版

## 08 安全扫描：免疫系统

### 90+ 威胁模式

| 类别 | 示例 |
|:---|:---|
| 密钥外泄 | `curl ... $AWS_SECRET_ACCESS_KEY` |
| 越狱攻击 | DAN mode, "ignore previous instructions" |
| 配置窃取 | `~/.hermes/.env` 直接访问 |
| 隐形字符 | 零宽空格、RTL 覆盖等 18 种 Unicode |
| 二进制注入 | .exe/.dll/.so 等可疑扩展名 |

### 信任分级

| 来源 | safe | caution | dangerous |
|:---|:---|:---|:---|
| builtin（内置） | allow | allow | allow |
| trusted（官方仓库） | allow | allow | block |
| community（社区） | allow | block | block |
| agent-created（自创建） | allow | allow | ask |

### 结构性检查

- 文件数 ≤50 / 总大小 ≤1MB / 单文件 ≤256KB
- 符号链接逃逸检测（symlink 不能指向 Skill 目录外）

## 09 Skill vs Memory 分工

| 维度 | Memory | Skill |
|:---|:---|:---|
| 回答的问题 | "是什么"（事实/偏好/环境） | "怎么做"（流程/步骤/方法） |
| 更新频率 | 低（事实相对稳定） | 中（随使用迭代改进） |
| 格式 | 短文本声明 | 结构化文档（触发/步骤/陷阱/验证） |
| 检索方式 | 全量注入 System Prompt | 索引注入 + 按需加载 |

## 10 与 Voyager 的对照

Voyager（NVIDIA 2023）提出 Skill Library 概念——Agent 在 Minecraft 中积累可复用技能函数。Hermes 将其工程化落地，解决真实世界问题：并发安全、成本控制、恶意输入防护、缓存一致性、文件系统原子性。

## 11 设计权衡总结

| 决策 | 收益 | 代价 |
|:---|:---|:---|
| User Message 注入 | 保护 Prompt Cache，降 90%+ 成本 | 指令跟随权重略低 |
| 写入后扫描 | 避免 TOCTOU | 需要回滚机制 |
| 两层缓存 | 热路径 ~0.001ms | 缓存一致性维护复杂 |
| Fuzzy Match | 减少 LLM patch 失败率 | 可能匹配到非预期位置 |
| 条件激活 | 控制索引膨胀 | Frontmatter 复杂度增加 |

### 改进方向

1. **缺少版本控制**：Patch 后旧版永久丢失，无法回滚
2. **安全扫描仅正则**：可被 Base64/Unicode 同形字绕过
3. **索引匹配依赖 LLM 判断**：缺少语义预过滤
4. **单机存储**：多设备无原生同步

## 💡 分析学习进化

### 🔍 与我们系统的对照审计

| 维度 | Hermes 官方 | 我们的实践 | 差距 | 行动 |
|:---|:---|:---|:---|:---|
| 创建触发 | ≥5 tool calls 自动创建 | ✅ 已在 System Prompt 中 | 一致 | — |
| 原子写入 | tempfile + os.replace | ✅ 已继承（底层工具） | 一致 | — |
| 安全扫描 | 90+ 威胁模式 | ✅ 已继承 | 一致 | — |
| 条件激活 | fallback_for / requires | ⚠️ 大部分 Skill 未声明 | **差距** | 为高频 Skill 补充 frontmatter 条件声明 |
| 渐进式加载 | 3 级披露 | ✅ 已实现 | 一致 | — |
| Fuzzy Patch | 9 策略模糊匹配 | ✅ 已继承 | 一致 | — |
| Prompt Cache 保护 | User Message 注入 | ✅ 已继承 | 一致 | — |
| 版本控制 | ❌ 缺失 | ❌ 同样缺失 | 一致 | 可加 .backup/ 自动保留最近 N 版 |
| 语义匹配 | ❌ 缺失 | ❌ 同样缺失 | 一致 | 低优先级 |
| Skill × Memory 分工 | 明确定义 | ✅ 已在 System Prompt | 一致 | — |

### ✅ 我们做得好的
- 完整继承了 Hermes 的核心闭环（7 关卡创建、Fuzzy Patch、条件激活、安全扫描）
- 自建了大量高质量 Skill（200+），覆盖 devops/research/productivity 等领域
- Skill 去重和合并机制（evolver、skill-review）比 Hermes 官方更成熟

### ⚠️ 可改进的
1. **frontmatter 条件声明**：我们大部分 Skill 缺少 `requires_toolsets` / `fallback_for_toolsets` 声明，导致索引可能比必要的大
2. **版本控制**：Patch 无回滚，与 Hermes 有相同的缺陷——可在 Skill 目录加 `.backup/` 自动存档
3. **provenance 追踪**：我们已有 `provenance` 字段（比 Hermes 更好），但可加强记录每次 patch 的触发原因

### 🔥 行动项
1. 为 top-20 高频 Skill 补充 `requires_toolsets` / `fallback_for_toolsets` 声明，减少无关索引
2. 设计 Skill 版本备份机制（.backup/ 目录保留最近 5 个版本）
3. 在 provenance 字段中增加 `last_patch_reason` 记录

→ 相关：[[2026-05-31-hermes-ops-自治运维体系深度蒸馏.md]]
→ 相关：[[2026-04-21-M-Flow联想记忆引擎.md]]

## 相关笔记
- [darwin-skill-2-evolver-absorption](2026-05-29-darwin-skill-2-evolver-absorption.md)
