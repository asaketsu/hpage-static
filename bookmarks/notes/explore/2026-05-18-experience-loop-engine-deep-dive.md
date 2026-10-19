# 经验闭环引擎：从错误到肌肉记忆的自动化系统

> 2026-05-18 | proactive-learn 深度研究 | Topic: Agent 自我进化与自治
> 方法：本地知识蒸馏 — 基于 Hermes 现有 5 大进化子系统 + 29 条错误案例 + 行业模式分析
> 字数: ~4200 | 难度: L4（架构设计级）

---

## 一、核心发现（5 个关键发现）

### 发现 1：经验闭环 ≠ 错误记录，而是 5 阶段自动管道

大多数人把"经验闭环"理解为记录错误日志。这只是第一步。真正的经验闭环引擎是一个 5 阶段管道：

```
COLLECT → IDENTIFY → ROOT_CAUSE → ENCODE → PREVENT
  采集     识别模式    根因分析     编码规则    自动防复发
```

**Hermes 现状对比**：

| 阶段 | 理想状态 | Hermes 现状 | 差距 |
|------|---------|------------|------|
| COLLECT | 全信号源自动采集 | error-case-library + feedback.md + cron logs | 🟢 基本覆盖 |
| IDENTIFY | 自动模式识别 | evolver-scan.sh 手动触发，阈值≥2次/7天 | 🟡 半自动 |
| ROOT_CAUSE | 结构化根因分析 | 人工写入 root_cause 字段 | 🔴 纯手动 |
| ENCODE | 自动生成规则/Skill/脚本 | evolver pipeline 有定义但 cron 不执行 | 🔴 管道断裂 |
| PREVENT | 主动拦截+自动防复发 | 无主动拦截机制 | 🔴 缺失 |

**核心洞察**：COLLECT 和 IDENTIFY 已有基础，但 ROOT_CAUSE → ENCODE → PREVENT 三段是断裂的。这就像人类只有痛觉（感受到错误）但没有肌肉记忆（自动规避）。

### 发现 2：根因分析是最大瓶颈 — 需要分层策略

分析 29 条错误案例，根因可以分 4 层：

| 层级 | 根因类型 | 占比 | 可自动化程度 | 典型案例 |
|------|---------|------|------------|---------|
| L1 语法/配置 | 拼写错误、路径错误、格式错误 | 31% (9/29) | 🟢 高 | EC-001 包名不一致、EC-003 cron路径 |
| L2 逻辑/边界 | 边界条件、空值、类型假设 | 34% (10/29) | 🟡 中 | EC-010 NaN传播、EC-012 高价股0交易 |
| L3 架构/设计 | 架构决策失误、抽象不当 | 21% (6/29) | 🔴 低 | EC-004 飞书bot消息结构差异、EC-009 空chunks |
| L4 环境/时序 | 竞态条件、环境差异、时序依赖 | 14% (4/29) | 🔴 低 | EC-013 .pyc缓存、EC-005 日志时间戳解析 |

**关键模式识别**：

1. **NaN 传播链**（EC-010, EC-011）：pandas 中 NaN 的算术和比较行为。根因相同（未处理 NaN），出现在不同模块。这是典型的"一个根因，多种症状"模式。
2. **误报链**（EC-005, EC-006, EC-007）：auto-diagnose-fix 系统自身的检测逻辑问题。根因模式相同：检测条件太宽泛或格式不匹配。
3. **初始化链**（EC-009, EC-014）：Python 变量初始化和 ABC 抽象方法。根因模式：假设前置条件一定满足。

**自动化策略**：
- L1：模式匹配即可（正则检测常见语法/路径/格式错误）
- L2：需要语义理解（LLM 辅助分析边界条件）
- L3/L4：需要人类参与（Agent 标记为"需人工分析"）

### 发现 3：防复发机制需要"主动拦截"，不是"被动查阅"

当前 error-case-library 的设计是**被动查阅**：遇到错误→查库→匹配→复用。这依赖 Agent 每次都主动查库，但实际上：

- Agent 在遇到错误时，优先用自己的推理能力解决，不会先查库
- 即使查库，关键词匹配的召回率有限（同义表述、不同表述的同一问题）
- 新 session 没有"上次犯了什么错"的记忆

**人类肌肉记忆的类比**：人类不需要每次都"回忆"怎么骑自行车——大脑已经把运动模式编码成了反射弧。经验闭环引擎需要类似机制：

```
被动模式:  遇错 → 查库 → 匹配 → 复用解法
主动模式:  操作 → 触发规则 → 自动检查 → 阻断/修正
```

**实现方案 — 三级防复发**：

| 级别 | 机制 | 示例 | 触发点 |
|------|------|------|--------|
| **编译期** | skill pitfalls 注入 | "pandas rolling 必须设 min_periods=1" 写入 skill | skill_view 加载时自动注入 |
| **运行期** | pre-hook 检查 | 写 pandas 代码前自动检查 NaN 处理 | 工具调用前拦截 |
| **验证期** | post-hook 验证 | 代码运行后检查结果是否有 NaN | 工具调用后验证 |

**Hermes 的最佳切入点**：编译期。每次 skill_view() 加载 skill 时，pitfalls 部分就是"肌肉记忆"。当前 evolver 已经在 skill 中有 pitfalls 段落，但缺乏从错误案例自动生成 pitfalls 的管道。

### 发现 4：进化闭环的"最后一公里"断裂 — 从学到用的转化率

分析 evolution-log.jsonl，发现一个关键问题：

```
学习产出 → 评估 → 写笔记 ✅ (100% 完成)
笔记 → Skill/Memory 更新 ✅ (~60% 完成)
Skill/Memory → 实际使用 ❌ (~20% 完成)
```

**原因分析**：

1. **Skill 创建后无使用触发**：创建了 skill 但没有场景主动调用它
2. **Memory 写入后无检索优化**：写入的记忆在下次遇到类似场景时不一定被检索到
3. **规则沉淀后无执行保障**：skill 中的 pitfalls 是"建议"而非"强制"

**解决方案 — 进化闭环完整性指标**：

```python
class EvolutionCompleteness:
    """衡量经验闭环的完整性"""
    
    def measure(self, experience_id: str) -> dict:
        return {
            # 阶段1：经验采集
            "collected": True,  # 有错误案例？
            "root_caused": bool,  # 有根因分析？
            
            # 阶段2：知识编码
            "encoded_as_skill": bool,  # 写入 skill pitfalls？
            "encoded_as_memory": bool,  # 写入 memory？
            "encoded_as_script": bool,  # 有自动修复脚本？
            
            # 阶段3：实际使用（关键）
            "skill_loaded_count": int,  # skill 被加载次数
            "pitfall_triggered_count": int,  # pitfalls 被触发次数
            "same_error_reoccurred": bool,  # 同类错误是否再次出现？
            
            # 最终指标
            "completeness_score": 0.0  # 0-1, 1=完整闭环
        }
```

**目标**：completeness_score ≥ 0.7 才算"经验已内化"。

### 发现 5：现有 5 大子系统的整合缺口

Hermes 目前有 5 个与经验闭环相关的子系统，但它们之间缺少统一的编排层：

| 子系统 | 角色 | 输入 | 输出 | 触发方式 |
|--------|------|------|------|---------|
| **error-case-library** | 错误记录 | 错误事件 | JSONL 案例 | 手动/Watchdog |
| **evolver** | 进化引擎 | 反馈+模式 | 规则/Skill/脚本 | Cron/手动 |
| **agent-reflection** | 反思机制 | 会话上下文 | 修正建议 | Session End/启发式 |
| **sensor-grid** | 传感器层 | 系统信号 | 偏差报告 | 定时/事件 |
| **active-learning** | 学习框架 | 兴趣队列 | 笔记+进化 | 时间/事件 |

**缺口**：

1. **无统一编排**：5 个系统各自运行，无统一调度器
2. **无闭环追踪**：没有"经验 ID"贯穿全链路，无法追踪从错误到防复发的完整路径
3. **无反馈量化**：不知道某个规则沉淀后是否真的减少了同类错误
4. **信号去重缺失**：同一错误可能被 error-case-library 和 agent-reflection 同时记录，无去重

---

## 二、技术架构设计：经验闭环引擎 v1.0

### 2.1 核心数据模型

```python
@dataclass
class Experience:
    """经验闭环核心实体"""
    id: str              # EXP-YYYY-NNN
    created: datetime
    category: str        # 错误类别
    
    # 阶段1：采集
    symptoms: list[str]  # 可观测症状
    context: dict        # 发生时的上下文（工具、文件、参数）
    
    # 阶段2：根因
    root_cause: str       # 根因描述
    root_cause_layer: str # L1/L2/L3/L4
    confidence: float     # 分析置信度 0-1
    
    # 阶段3：编码
    encoded_as: list[str] # ["skill:pitfall", "memory", "script:fix"]
    encoded_at: datetime
    
    # 阶段4：防复发
    prevention_type: str  # "compile"/"runtime"/"validate"
    triggered_count: int  # 被触发次数
    last_triggered: datetime
    
    # 阶段5：验证
    reoccurred: bool      # 同类错误是否再出现
    verified_at: datetime
    
    # 元数据
    related_cases: list[str]   # 关联的 EC-YYYY-NNN
    evolution_log_ids: list[str]  # 对应的进化日志条目
```

### 2.2 自动根因分析管道

```python
class RootCauseAnalyzer:
    """分层自动根因分析"""
    
    # L1 规则库（模式匹配，高自动化）
    L1_PATTERNS = {
        "ModuleNotFoundError": "import 路径与目录结构不匹配",
        "FileNotFoundError.*cron": "cron 环境 PATH 隔离，需绝对路径",
        "json.loads.*YAML": "用 json 解析了 YAML 格式文件",
        "UnboundLocalError": "循环/条件内赋值变量未初始化",
        "TypeError.*abstract": "ABC 抽象方法未实现",
    }
    
    # L2 规则库（语义匹配，中等自动化）
    L2_PATTERNS = {
        "NaN.*False|NaN.*True": {
            "root_cause": "NaN 参与比较运算结果恒为 False",
            "fix": "比较前 fillna(0) 或 dropna()",
            "auto_fixable": True
        },
        "rolling.*NaN|min_periods": {
            "root_cause": "pandas rolling 默认 min_periods=window",
            "fix": "设置 min_periods=1",
            "auto_fixable": True
        },
    }
    
    def analyze(self, error: dict) -> dict:
        """自动分析根因，返回结构化结果"""
        
        # Step 1: L1 模式匹配
        for pattern, cause in self.L1_PATTERNS.items():
            if re.search(pattern, error.get('message', '')):
                return {
                    "layer": "L1", "confidence": 0.95,
                    "root_cause": cause, "auto_fixable": True
                }
        
        # Step 2: L2 语义匹配
        for pattern, analysis in self.L2_PATTERNS.items():
            if re.search(pattern, error.get('message', '')):
                return {
                    "layer": "L2", "confidence": 0.8,
                    **analysis
                }
        
        # Step 3: L3/L4 标记需人工分析
        return {
            "layer": "L3+", "confidence": 0.3,
            "root_cause": "需人工分析", "auto_fixable": False,
            "suggestion": self._generate_analysis_hints(error)
        }
```

### 2.3 自动防复发注入器

```python
class PreventionInjector:
    """将经验编码为防复发规则，注入到各层级"""
    
    def inject(self, experience: Experience):
        """根据根因层级选择注入方式"""
        
        if experience.root_cause_layer == "L1":
            # 编译期：写入 skill pitfalls
            self._inject_to_skill_pitfalls(experience)
            
        elif experience.root_cause_layer == "L2":
            # 运行期：创建 pre-hook 检查
            self._inject_runtime_check(experience)
            
        elif experience.root_cause_layer in ("L3", "L4"):
            # 验证期：添加 post-task 验证
            self._inject_post_validation(experience)
    
    def _inject_to_skill_pitfalls(self, exp: Experience):
        """将经验注入到相关 skill 的 pitfalls 段落"""
        # 1. 找到受影响的 skill
        affected_skills = self._find_affected_skills(exp.category)
        
        for skill_name in affected_skills:
            # 2. 读取当前 skill
            skill = skill_view(skill_name)
            
            # 3. 生成 pitfall 条目
            pitfall = f"- **{exp.root_cause}**：{exp.symptoms[0]}。修复：{exp.fix}"
            
            # 4. 注入到 pitfalls 段落
            skill_manage(
                action='patch',
                name=skill_name,
                old_string='## Pitfalls',
                new_string=f'## Pitfalls\n\n{pitfall}'
            )
```

### 2.4 闭环完整性追踪器

```python
class ExperienceTracker:
    """追踪经验闭环的完整性"""
    
    def __init__(self):
        self.log_path = "~/.hermes/experience-tracker.jsonl"
    
    def track(self, experience_id: str):
        """周期性检查经验是否形成了完整闭环"""
        
        exp = self._load_experience(experience_id)
        
        metrics = {
            "has_root_cause": bool(exp.root_cause),
            "has_encoding": len(exp.encoded_as) > 0,
            "skill_loaded": exp.triggered_count > 0,
            "prevented_reoccurrence": not exp.reoccurred,
        }
        
        completeness = sum(metrics.values()) / len(metrics)
        
        if completeness < 0.5:
            # 闭环不完整，触发补全动作
            self._trigger_completion(exp, metrics)
        
        return completeness
```

---

## 三、实践案例：从 Hermes 错误案例提炼防复发规则

### 案例 1：NaN 传播链（EC-010 + EC-011）

**根因模式**：pandas 中 NaN 参与算术/比较运算的行为不符合直觉

**自动编码为 skill pitfall**：

```
## Pitfalls (自动生成 from EXP-2026-001)

### pandas NaN 传播
- **症状**：rolling 均值/量比全 NaN，或 crossover 返回全 0
- **根因**：rolling 默认 min_periods=window，前期全 NaN；NaN 比较恒 False
- **修复**：rolling 设 min_periods=1；比较前 fillna(0)
- **强制检查**：所有 pandas 指标计算代码必须包含 NaN 处理
```

### 案例 2：误报链（EC-005 + EC-006 + EC-007）

**根因模式**：检测条件太宽泛，缺少精确匹配

**自动编码为设计规则**：

```
## Rules (自动生成 from EXP-2026-002)

### 故障检测精确性原则
1. 检测模式必须包含上下文关键词（不能只匹配 "error"）
2. 必须限定检测文件范围（不能扫描所有日志）
3. 时间窗口必须基于行内时间戳（不能只看文件 mtime）
4. 配置文件检查必须区分格式（JSON vs YAML vs TOML）
```

### 案例 3：初始化链（EC-009 + EC-014）

**根因模式**：假设前置条件一定满足

**自动编码为代码模板**：

```python
# 自动注入的防御性编程模板
def safe_iteration(items):
    """从 EC-009 提炼：循环前必须处理空输入"""
    if not items:
        return None  # 空输入提前返回
    result = None  # 初始化循环内变量
    for item in items:
        result = process(item)
    return result

def implement_abc_methods(cls):
    """从 EC-014 提炼：继承 ABC 必须实现所有抽象方法"""
    abstract_methods = getattr(cls, '__abstractmethods__', set())
    for method in abstract_methods:
        if not hasattr(cls, method):
            raise TypeError(
                f"{cls.__name__} must implement abstract method: {method}"
            )
```

---

## 四、整合方案：Experience Loop Engine 作为统一编排层

### 4.1 架构图

```
                    ┌─────────────────────────┐
                    │  Experience Loop Engine  │
                    │    (统一编排层 v1.0)      │
                    └─────────┬───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
   │ COLLECT  │          │ ENCODE    │         │ PREVENT   │
   │ Collector│          │ Encoder   │         │ Injector  │
   └────┬────┘          └─────┬─────┘         └─────┬─────┘
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
   │error-   │          │evolver    │         │skill      │
   │case-lib │          │agent-     │         │pitfalls   │
   │sensor-  │          │reflection │         │pre-hooks  │
   │grid     │          │active-    │         │post-hooks │
   │         │          │learning   │         │           │
   └─────────┘          └───────────┘         └───────────┘
```

### 4.2 统一事件总线

```python
class ExperienceBus:
    """经验闭环事件总线 — 贯穿全链路"""
    
    def __init__(self):
        self.bus = "~/.hermes/experience-bus.jsonl"
    
    def emit(self, event_type: str, data: dict):
        """发布事件"""
        event = {
            "id": f"EXP-{datetime.now():%Y%m%d}-{self._next_seq()}",
            "type": event_type,  # "error_detected" | "root_caused" | "encoded" | "prevented" | "reoccurred"
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        append_jsonl(self.bus, event)
        return event["id"]
    
    def trace(self, experience_id: str) -> list:
        """追踪一条经验的完整生命周期"""
        events = read_jsonl(self.bus)
        return [e for e in events if e["id"] == experience_id]
```

### 4.3 与现有系统的集成点

| 现有系统 | 集成方式 | 变更量 |
|---------|---------|--------|
| error-case-library | case-add 时自动触发 ExperienceBus.emit("error_detected") | +3 行代码 |
| evolver | scan 结果通过 ExperienceBus 追踪，不再写独立日志 | 改输出格式 |
| agent-reflection | 微反思写入 ExperienceBus 而非 reflection-pending.jsonl | 改输出路径 |
| sensor-grid | Tier 1 传感器信号接入 ExperienceBus | +接口适配 |
| active-learning | 进化闭环评估使用 ExperienceTracker.measure() | +调用 |

---

## 五、知识缺口与未来方向

### 5.1 已识别的知识缺口

| # | 缺口 | 优先级 | 解决方案 |
|---|------|--------|---------|
| G1 | 根因分析 L3/L4 自动化率低 | P1 | 引入 LLM 辅助分析（Prompt 模板 + few-shot） |
| G2 | 无闭环完整性量化指标 | P1 | 实现 ExperienceTracker，cron 每日评估 |
| G3 | Skill pitfalls 无自动注入管道 | P2 | 实现 PreventionInjector |
| G4 | 经验去重/合并逻辑缺失 | P2 | 基于语义相似度的聚类 |
| G5 | 跨 session 经验传递依赖 memory 检索 | P3 | ExperienceBus 作为持久化事件流 |

### 5.2 与学术研究的关联

经验闭环引擎的设计与以下研究领域相关：

1. **Reinforcement Learning from Human Feedback (RLHF)**：将人类反馈（错误纠正）编码为奖励信号
2. **Case-Based Reasoning (CBR)**：基于案例的推理，与 error-case-library 直接对应
3. **Self-Supervised Learning**：从无标注的错误日志中自动发现模式
4. **Autonomic Computing**：IBM 提出的自计算系统（自我配置、自我修复、自我优化、自我保护）
5. **Muscle Memory in Robotics**：机器人运动技能的"肌肉记忆"编码，从 demonstration 中提取运动原语

### 5.3 实施路线图

| Phase | 内容 | 时间 | 产出 |
|-------|------|------|------|
| P0 | ExperienceBus + Experience 数据模型 | 1天 | 事件总线 + JSONL 追踪 |
| P1 | RootCauseAnalyzer L1/L2 规则库 | 2天 | 从 29 条案例自动提炼规则 |
| P2 | PreventionInjector (skill pitfalls 注入) | 1天 | 自动 patch skill |
| P3 | ExperienceTracker 闭环评估 | 1天 | 每日完整性报告 |
| P4 | 与现有 5 系统集成 | 2天 | 统一编排层上线 |

---

## 六、实践启发

1. **经验闭环的最大价值不在"记录"而在"预防"**：29 条错误案例如果只是记录在 JSONL 里，下次遇到同样问题时 Agent 未必会查。只有把经验编码成"强制检查"（pitfalls、pre-hooks），才能真正防复发。

2. **分层自动化是务实策略**：不是所有根因都需要 LLM 分析。L1 的模式匹配（31% 的错误）可以用正则自动完成，成本低、精度高。先把这部分自动化，再逐步扩展。

3. **闭环完整性需要量化**："我进化了"不能只靠进化日志数量衡量。需要追踪从错误到防复发的完整路径，completeness_score ≥ 0.7 才算"经验已内化"。

4. **现有系统的整合比重建更重要**：Hermes 已有 5 个相关子系统，不需要推翻重建。ExperienceBus 作为薄层编排，最小化变更量，最大化整合效果。

5. **"肌肉记忆"的本质是"被动→主动"的转变**：从"遇到问题查库"（被动）到"操作时自动检查"（主动）。这是经验闭环引擎的核心设计理念。

## 相关笔记
- [skill-lifecycle-management-deep-dive](explore/2026-05-18-skill-lifecycle-management-deep-dive.md)
