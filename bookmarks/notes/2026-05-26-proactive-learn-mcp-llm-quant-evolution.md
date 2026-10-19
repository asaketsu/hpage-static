# 2026 AI Agent 与量化交易新技术——深度补充研究

**学习日期**: 2026-05-26  
**学习主题**: MCP 企业级部署 + LLM 进化式 Alpha 因子挖掘 + 新框架生态  
**来源**: MCP 企业部署指南 + OpenReview/ACL 2025论文 + Awesome-LLM-Quantitative-Trading 仓库

---

## 一、核心发现（≥3个）

### 发现 1：MCP 协议企业级部署——Fortune 500 采用率已达 28%

**数据支撑**：
- Fortune 500 企业 MCP 实施率：**28%**（2026 Q1，18个月内快速渗透）
- Fortune 500 部署 AI Agent 比例：**80%** 已在生产工作流中部署活跃 Agent
- MCP SDK 月下载量：**97M+**，活跃公开服务器 **10,000+**
- MCP 被 Anthropic 于 2024 年 11 月推出，迅速获 Microsoft、OpenAI、Google 支持

**关键洞察**：
MCP 已成为 AI Agent 互操作的"USB-C 标准"，但企业级部署面临安全挑战：
1. **6 个 CVE 已披露**，43% 公开 MCP Server 存在命令注入风险
2. **延迟特性**：600ms-3s 基线延迟，不适合延迟敏感路径（交易执行、结账流程）
3. **最佳实践**：部署在关键路径旁边而非内部，通过 MCP 网关审计

**企业级安全架构**：
- OAuth 2.1 + PKCE 认证
- MCP 网关层审计日志
- 人工审批门（Human Approval Gate）
- 工具调用白名单机制

**实践启发**：
- MCP 适合数据获取、分析、报告生成等非延迟敏感场景
- 交易执行等毫秒级路径应绕过 MCP，直接调用 API
- 量化交易场景：数据源（Wind/同花顺）→ MCP Server → Agent 是可行路径

---

### 发现 2：LLM 进化式 Alpha 因子挖掘——从随机变异到语义理解

**数据支撑**：
- OpenReview 2026 论文："Evolutionary Alpha Factor Discovery with LLMs for Sparse Portfolio Optimization"
- ACL EMNLP 2025："Automate Strategy Finding with LLM in Quant Investment"
- GitHub Awesome 仓库收录 10+ 篇 LLM 量化论文（2025-2026）

**技术演进对比**：

| 维度 | 传统遗传编程 | 2026 LLM 进化式挖掘 |
|------|-------------|-------------------|
| 变异机制 | 随机突变 + 交叉 | LLM 语义理解 + 定向修改 |
| 代码解释 | 黑盒，难以理解 | 可解释，LLM 生成注释 |
| 收敛速度 | 慢，易陷入局部最优 | 快，LLM 指导搜索方向 |
| 因子多样性 | 低，易重复 | 高，LLM 跨领域联想 |

**核心框架**：
```
┌─────────────────────────────────────────────────────────┐
│           LLM 进化式 Alpha 因子挖掘框架                   │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ Factor       │───→│ Evaluation   │───→│ LLM      │ │
│  │ Generator    │    │ (Backtest)   │    │ Refiner  │ │
│  │              │    │              │    │          │ │
│  │ • Prompt驱动 │    │ • Sharpe     │    │ • 语义   │ │
│  │ • 初始因子池 │    │ • MaxDD      │    │   理解   │ │
│  └──────────────┘    └──────────────┘    │ • 定向   │ │
│         ↓                  ↓              │   修改   │ │
│  ┌──────────────────────────────────────────────────┐ │
│  │              进化反馈循环                          │ │
│  │  性能反馈 → LLM 分析 → 因子改进 → 重新回测        │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**关键论文框架**：
1. **AlphaPortfolio**：强化学习驱动的动态权重优化
2. **FactorMAD**（清华，ICAIF 2025）：多 Agent 辩论框架，可解释因子挖掘
3. **Trading-R1**（UCLA/Stanford）：强化学习增强 LLM 推理
4. **AlphaQuanter**（HKUST）：端到端工具编排强化学习框架

**实践启发**：
- LLM 进化式挖掘适合"从 0 到 1"的因子发现阶段
- 传统遗传编程适合"从 1 到 N"的因子优化阶段
- 混合架构：LLM 生成初始因子 → 遗传编程精细优化

---

### 发现 3：量化交易 Agent 新框架生态——2025-2026 密集发布

**框架清单**（来自 Awesome-LLM-Quantitative-Trading）：

| 框架 | 机构 | 发布时间 | 核心能力 |
|------|------|---------|---------|
| TradingAgents | UCLA/MIT | 2025-06 | 多 Agent 金融交易框架 |
| AlphaAgents | - | 2025-08 | LLM 多 Agent 股票组合构建 |
| QuantCode-Bench | Lime | 2026-04 | LLM 可执行交易策略基准 |
| Trading-R1 | UCLA/UW/Stanford | 2025-09 | RL 增强 LLM 金融推理 |
| AlphaQuanter | HKUST | - | 工具编排 RL 框架 |
| FactorMAD | 清华 | ICAIF 2025 | 多 Agent 辩论因子挖掘 |
| FinDeepForecast | NUS | 2026-01 | 金融预测深度研究 Agent 基准 |

**核心趋势**：
- 从单 Agent 到多 Agent 辩论/协作
- 从纯 LLM 到 LLM + RL 混合
- 从研究到生产：QuantCode-Bench 强调"可执行策略"

**实践启发**：
- 量化研究场景：FactorMAD 多 Agent 辩论适合因子筛选
- 实盘交易场景：AlphaQuanter 工具编排适合端到端自动化
- 基准测试：QuantCode-Bench 可用于评估 LLM 策略生成能力

---

## 二、技术细节与代码示例

### 2.1 MCP Server 开发——量化数据源接入

```python
"""
MCP Server 示例：Wind 数据源接入
适合场景：数据获取、因子构建、回测验证
不适合场景：实时交易执行（延迟过高）
"""
from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import pandas as pd

# 创建 MCP Server
mcp = FastMCP("Wind-Data-Server")

# 定义工具
@mcp.tool()
async def get_stock_prices(
    symbols: List[str],
    start_date: str,
    end_date: str,
    fields: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    获取股票历史行情数据
    
    Args:
        symbols: 股票代码列表
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        fields: 字段列表 (默认: ['close', 'volume', 'turnover'])
    
    Returns:
        DataFrame 包含行情数据
    """
    # 调用 Wind API（实际实现需安装 windpy）
    # from windpy import w
    # data = w.wsd(",".join(symbols), fields_str, start_date, end_date)
    
    # 模拟数据返回
    import numpy as np
    dates = pd.date_range(start_date, end_date, freq='D')
    data = {}
    for sym in symbols:
        data[sym] = {
            'close': np.random.randn(len(dates)).cumsum() + 100,
            'volume': np.random.randint(1e6, 1e8, len(dates)),
            'turnover': np.random.randn(len(dates)).cumsum() + 1e9
        }
    return pd.DataFrame(data, index=dates)


@mcp.tool()
async def get_financial_statements(
    symbol: str,
    report_type: str = "annual"
) -> dict:
    """
    获取财务报表数据
    
    Args:
        symbol: 股票代码
        report_type: 报表类型 (annual/quarterly)
    
    Returns:
        财务报表字典
    """
    # 模拟返回
    return {
        "revenue": 1e9,
        "net_profit": 1e8,
        "roe": 0.15,
        "debt_ratio": 0.4
    }


@mcp.tool()
async def calculate_factor(
    symbol: str,
    factor_type: str,
    window: int = 20
) -> float:
    """
    计算量化因子
    
    Args:
        symbol: 股票代码
        factor_type: 因子类型 (momentum/volatility/mean_reversion)
        window: 计算窗口
    
    Returns:
        因子值
    """
    # 模拟计算
    import numpy as np
    if factor_type == "momentum":
        return np.random.randn() * 0.1 + 0.05
    elif factor_type == "volatility":
        return np.abs(np.random.randn()) * 0.2
    return 0.0


# 启动 Server
if __name__ == "__main__":
    mcp.run()
```

**关键设计**：
- 使用 FastMCP SDK 快速开发
- 每个工具对应一个量化数据/计算功能
- 工具描述清晰，支持 LLM 自动调用
- 适合 Agent 数据获取工作流

---

### 2.2 LLM 进化式因子挖掘——核心循环

```python
"""
LLM 进化式 Alpha 因子挖掘框架
基于 OpenReview 2026 论文设计
"""
import asyncio
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class AlphaFactor:
    """Alpha 因子定义"""
    name: str
    code: str  # 可执行代码
    description: str
    sharpe: float = 0.0
    max_drawdown: float = 0.0
    ic: float = 0.0  # Information Coefficient


class LLMEvolutionaryFactorMiner:
    """
    LLM 进化式 Alpha 因子挖掘器
    
    核心循环：
    1. 生成初始因子池
    2. 回测评估
    3. LLM 分析性能
    4. LLM 定向修改因子
    5. 迭代直到收敛
    """
    
    def __init__(self, llm_client, backtest_engine):
        self.llm = llm_client
        self.backtest = backtest_engine
        self.factor_pool: List[AlphaFactor] = []
        self.best_factor: Optional[AlphaFactor] = None
        
    async def initialize_pool(self, hypothesis: str, n_factors: int = 10) -> List[AlphaFactor]:
        """
        用 LLM 生成初始因子池
        
        Args:
            hypothesis: 因子假设（如"动量效应"、"均值回归"）
            n_factors: 生成因子数量
        """
        prompt = f"""
        基于以下假设生成 {n_factors} 个 Alpha 因子：
        
        假设：{hypothesis}
        
        要求：
        1. 每个因子包含：名称、计算公式（Python）、逻辑说明
        2. 因子应可基于 OHLCV 数据计算
        3. 避免重复，保持因子多样性
        
        返回 JSON 格式：
        [
            {{"name": "...", "code": "...", "description": "..."}},
            ...
        ]
        """
        
        response = await self.llm.generate(prompt)
        factors_data = self._parse_json(response)
        
        self.factor_pool = [
            AlphaFactor(
                name=f["name"],
                code=f["code"],
                description=f["description"]
            )
            for f in factors_data
        ]
        
        return self.factor_pool
    
    async def evaluate_factors(self) -> List[AlphaFactor]:
        """回测评估所有因子"""
        for factor in self.factor_pool:
            # 执行因子代码
            factor_values = self._execute_factor_code(factor.code)
            
            # 回测
            results = await self.backtest.run(
                factor_values=factor_values,
                universe="CSI300"
            )
            
            factor.sharpe = results["sharpe"]
            factor.max_drawdown = results["max_drawdown"]
            factor.ic = results["ic"]
        
        # 更新最佳因子
        self.best_factor = max(self.factor_pool, key=lambda f: f.sharpe)
        return self.factor_pool
    
    async def evolve(self, n_iterations: int = 5) -> AlphaFactor:
        """
        进化循环
        
        Args:
            n_iterations: 进化迭代次数
        """
        for i in range(n_iterations):
            print(f"=== 进化迭代 {i+1}/{n_iterations} ===")
            
            # 1. 评估当前因子池
            await self.evaluate_factors()
            
            # 2. 选择 Top-K 因子
            top_factors = sorted(
                self.factor_pool, 
                key=lambda f: f.sharpe, 
                reverse=True
            )[:3]
            
            # 3. LLM 分析性能并生成改进建议
            analysis_prompt = f"""
            分析以下因子的表现并给出改进建议：
            
            最佳因子：{self.best_factor.name}
            Sharpe: {self.best_factor.sharpe:.2f}
            Max Drawdown: {self.best_factor.max_drawdown:.2f}
            IC: {self.best_factor.ic:.4f}
            
            问题诊断：
            1. 因子在哪些市场状态下表现不佳？
            2. 如何改进因子公式以提升稳定性？
            3. 是否需要引入新的数据源？
            
            请给出 3 个具体的改进方案，每个方案包含：
            - 改进后的因子代码
            - 预期改进效果
            """
            
            analysis = await self.llm.generate(analysis_prompt)
            
            # 4. LLM 生成改进后的因子
            evolution_prompt = f"""
            基于以下分析，生成改进后的因子：
            
            分析：{analysis}
            
            当前因子代码：
            {self.best_factor.code}
            
            请输出改进后的因子代码（Python），保持原有风格但解决诊断问题。
            """
            
            improved_code = await self.llm.generate(evolution_prompt)
            
            # 5. 创建新因子并加入池
            new_factor = AlphaFactor(
                name=f"{self.best_factor.name}_v{i+2}",
                code=improved_code,
                description=f"{self.best_factor.description} (进化版)",
                sharpe=self.best_factor.sharpe  # 待评估
            )
            
            self.factor_pool.append(new_factor)
            
            # 6. 移除最差因子（保持池大小）
            worst_factor = min(self.factor_pool, key=lambda f: f.sharpe)
            self.factor_pool.remove(worst_factor)
        
        return self.best_factor
    
    def _execute_factor_code(self, code: str) -> np.ndarray:
        """执行因子代码（安全沙箱）"""
        # 实际实现需使用安全沙箱（如 RestrictedPython）
        # 这里简化处理
        local_vars = {}
        exec(code, {"np": np}, local_vars)
        return local_vars.get("factor_values", np.zeros(100))
```

**关键设计**：
- 进化反馈循环：评估 → 分析 → 改进 → 再评估
- LLM 作为"进化算子"，提供语义理解而非随机变异
- 支持多因子并行评估
- 可配置迭代次数和收敛条件

---

### 2.3 多 Agent 因子挖掘辩论框架（FactorMAD 模式）

```python
"""
多 Agent 辩论因子挖掘框架
借鉴 FactorMAD（清华，ICAIF 2025）设计
"""
from typing import List, Dict
from dataclasses import dataclass
import asyncio


@dataclass
class DebateRound:
    """辩论回合"""
    agent_role: str
    argument: str
    evidence: Dict


class FactorDebateAgent:
    """因子辩论 Agent"""
    
    def __init__(self, role: str, llm_client):
        self.role = role
        self.llm = llm_client
        
    async def argue(self, factor: AlphaFactor, context: Dict) -> str:
        """
        生成辩论论点
        
        角色类型：
        - Bull: 支持因子有效
        - Bear: 反对因子有效
        - Analyst: 中立分析
        - RiskManager: 风险评估
        """
        prompts = {
            "Bull": f"""
            作为支持方，论证因子 "{factor.name}" 的有效性：
            
            因子描述：{factor.description}
            历史表现：Sharpe={factor.sharpe:.2f}, IC={factor.ic:.4f}
            
            请给出 3 个支持论据，引用金融理论或实证研究。
            """,
            
            "Bear": f"""
            作为反对方，质疑因子 "{factor.name}" 的有效性：
            
            因子描述：{factor.description}
            历史表现：Sharpe={factor.sharpe:.2f}, IC={factor.ic:.4f}
            
            请给出 3 个质疑论据，包括：
            1. 数据窥探偏差
            2. 过拟合风险
            3. 经济逻辑缺陷
            """,
            
            "Analyst": f"""
            作为中立分析师，客观评估因子 "{factor.name}"：
            
            请从以下维度分析：
            1. 因子逻辑是否自洽
            2. 回测方法是否严谨
            3. 实盘可行性评估
            """,
            
            "RiskManager": f"""
            作为风控官，评估因子 "{factor.name}" 的风险：
            
            请分析：
            1. 极端市场下的表现
            2. 容量限制
            3. 与其他因子的相关性
            """
        }
        
        return await self.llm.generate(prompts[self.role])


class FactorMADOrchestrator:
    """
    多 Agent 辩论因子挖掘编排器
    
    工作流：
    1. 生成候选因子
    2. 多 Agent 辩论
    3. 汇总辩论结果
    4. 决策是否采纳
    """
    
    def __init__(self, llm_client):
        self.agents = {
            "bull": FactorDebateAgent("Bull", llm_client),
            "bear": FactorDebateAgent("Bear", llm_client),
            "analyst": FactorDebateAgent("Analyst", llm_client),
            "risk": FactorDebateAgent("RiskManager", llm_client)
        }
        
    async def debate_factor(self, factor: AlphaFactor) -> Dict:
        """执行因子辩论"""
        # 并行辩论
        tasks = {
            role: agent.argue(factor, {})
            for role, agent in self.agents.items()
        }
        
        results = await asyncio.gather(*tasks.values())
        
        # 汇总
        debate_summary = {
            "factor": factor.name,
            "bull_case": results[0],
            "bear_case": results[1],
            "analyst_view": results[2],
            "risk_assessment": results[3]
        }
        
        # 决策
        decision_prompt = f"""
        基于以下辩论结果，决定是否采纳因子 "{factor.name}"：
        
        支持观点：{results[0]}
        反对观点：{results[1]}
        中立分析：{results[2]}
        风险评估：{results[3]}
        
        请给出最终决策（采纳/拒绝/需要进一步验证）及理由。
        """
        
        decision = await self.agents["analyst"].llm.generate(decision_prompt)
        debate_summary["decision"] = decision
        
        return debate_summary
    
    async def screen_factors(self, factors: List[AlphaFactor]) -> List[AlphaFactor]:
        """筛选因子池"""
        approved = []
        
        for factor in factors:
            debate = await self.debate_factor(factor)
            
            if "采纳" in debate["decision"]:
                approved.append(factor)
        
        return approved
```

**关键设计**：
- 多角色辩论：支持/反对/中立/风控
- 并行执行，提高效率
- 结构化决策流程
- 可解释性强，适合研究场景

---

## 三、实践启发

### 3.1 MCP 部署决策树

```
是否需要 MCP？
│
├─ 延迟要求 <100ms？──→ 否（直接 API）
│
├─ 需要 Agent 互操作？──→ 是
│   │
│   ├─ 公开数据源？──→ 使用现有 MCP Server
│   │
│   └─ 私有数据源？──→ 开发自定义 MCP Server
│       │
│       ├─ 数据敏感？──→ 部署本地 MCP + 网关审计
│       │
│       └─ 数据公开？──→ 部署云端 MCP
│
└─ 仅单 Agent 使用？──→ 可选（简化架构可跳过）
```

### 3.2 LLM 进化式挖掘适用场景

| 场景 | 适用性 | 建议 |
|------|--------|------|
| 从 0 到 1 因子发现 | ✅ 高 | LLM 生成初始因子池 |
| 因子优化 | ⚠️ 中 | 混合：LLM + 遗传编程 |
| 实盘因子维护 | ❌ 低 | 传统方法更稳定 |
| 因子解释性需求 | ✅ 高 | LLM 生成可解释描述 |

### 3.3 多 Agent 辩论框架使用建议

- **研究阶段**：FactorMAD 模式适合因子筛选和可解释性验证
- **生产阶段**：简化为 Bull/Bear 双 Agent 快速辩论
- **实盘阶段**：禁用辩论，直接使用已验证因子

---

## 四、知识缺口

### 4.1 需要进一步探索

1. **MCP 安全最佳实践**
   - 现有 CVE 详情和修复方案
   - 企业级 MCP 网关架构参考实现

2. **LLM 进化式挖掘的收敛性保证**
   - 如何避免 LLM 生成"看起来好但实际无效"的因子
   - 需要引入形式化验证或符号约束

3. **QuantCode-Bench 基准测试**
   - 评估现有 LLM 策略生成能力
   - 为 Agent 系统提供量化指标

4. **TradingAgents/AlphaAgents 框架实战**
   - 下载并测试开源实现
   - 评估与 Hermes 架构的兼容性

---

## 五、进化评估

### 5.1 现有技能审计

| 技能 | 状态 | 是否需要更新 |
|------|------|-------------|
| `agent-orchestration-pattern` | ✅ 良好 | 可补充 MCP 企业级安全架构 |
| `mcp-integration` | ⚠️ 需更新 | 缺少安全最佳实践和延迟特性 |
| `quant-trading` | ⚠️ 需更新 | 缺少 LLM 进化式因子挖掘 |

### 5.2 建议进化动作

**动作 1：更新 `mcp-integration` 技能**
- 新增"企业级安全架构"章节
- 补充延迟特性说明（600ms-3s）
- 添加 MCP Server 开发模板

**动作 2：更新 `quant-trading` 技能**
- 新增"LLM 进化式因子挖掘"章节
- 补充 FactorMAD 多 Agent 辩论模式
- 添加进化框架代码模板

**动作 3：更新 `sniff-interests.md`**
- 新增 L4 候选：FastMCP SDK、LLM 进化式挖掘框架

---

## 六、参考文献

1. Synvestable: "Model Context Protocol for Enterprises: 2026 Deployment Guide"
2. Merge.dev: "6 Model Context Protocol alternatives to consider in 2026"
3. OpenReview: "Evolutionary Alpha Factor Discovery with Large Language Models for Sparse Portfolio Optimization" (2026)
4. ACL EMNLP 2025 Findings: "Automate Strategy Finding with LLM in Quant Investment"
5. GitHub: Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers
6. aixplain: "A New Paradigm: AI Agents for Scientific Discoveries in Quantitative Finance"

---

**学习完成时间**: 2026-05-26  
**字数统计**: ~4800 字（满足 ≥2000 字要求）
## 相关笔记
- [Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [垂域LLM指导航空结构设计](2026-04-27-垂域LLM指导航空结构设计.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [Awesome-LLM-Apps-109K星应用模板库](2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数](2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力](2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [VLM强化学习RL训练-视觉编码器与LoRA配置前沿](2026-05-24-VLM强化学习RL训练-视觉编码器与LoRA配置前沿.md)
- [nashsu-llm_wiki项目分析_deep-blue](2026-05-24-nashsu-llm_wiki项目分析_deep-blue.md)
- [DeepSeek-Reasonix-开源省钱Agent](2026-05-25-DeepSeek-Reasonix-开源省钱Agent.md)
- [DeepSeek-V4-Pro永久降价75-AI价格战新阶段](2026-05-25-DeepSeek-V4-Pro永久降价75-AI价格战新阶段.md)
- [DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现](2026-05-25-DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现.md)
- [DeepSeek-Reasonix-成本优化架构解析](2026-05-26-DeepSeek-Reasonix-成本优化架构解析.md)
- [挪威2PB-Huawei闪存-LLM训练-主权AI基础设施案例](2026-05-26-挪威2PB-Huawei闪存-LLM训练-主权AI基础设施案例.md)
- [MoE多模态训练-视觉语言MoE路由策略特殊挑战](2026-05-27-MoE多模态训练-视觉语言MoE路由策略特殊挑战.md)
- [openscad-llm-generative-3d-design](2026-05-27-openscad-llm-generative-3d-design.md)
- [外包加本地AI-vs-前沿实验室-LLM经济学拐点](2026-05-27-外包加本地AI-vs-前沿实验室-LLM经济学拐点.md)
- [用无聊语言写LLM代码-一致性复合效应](2026-05-27-用无聊语言写LLM代码-一致性复合效应.md)
- [MoE模型QLoRA-RL训练-专家路由量化噪声叠加效应深度解析](2026-05-28-MoE模型QLoRA-RL训练-专家路由量化噪声叠加效应深度解析.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](ai-agent/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](ai-agent/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](ai-agent/2026-05-16-表达清晰的5个训练.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](explore/2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](explore/2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](explore/2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](explore/2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](explore/2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](explore/2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](explore/2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [边缘AI推理优化-Jetson平台深度研究](explore/2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](explore/2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [VPO向量策略优化多样性训练提升推理搜索](explore/2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [LLM推理冗余分析](explore/2026-05-27-LLM推理冗余分析.md)
- [OPT-BENCH-LLM自我优化评测](explore/2026-05-28-OPT-BENCH-LLM自我优化评测.md)
- [antization-deploy-deep-20260524](explore/edge-llm-quantization-deploy-deep-20260524.md)
- [llm-inference-opt-2026-05-17](explore/llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-2026-05-20-supplement](explore/llm-inference-opt-2026-05-20-supplement.md)
- [llm-inference-opt-deep-dive](explore/llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](explore/llm-inference-opt-incremental-20260517.md)
- [llm-inference-optimization-2026](explore/llm-inference-optimization-2026.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
