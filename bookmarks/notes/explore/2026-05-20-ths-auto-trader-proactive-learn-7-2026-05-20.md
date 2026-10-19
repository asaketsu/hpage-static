# THS Auto Trader 深度学习笔记 #7 — 量化交易生态全景 2026.05

> 来源: proactive-learn phase | 2026-05-20
> 主题: 同花顺自动交易系统 — 工具链、AI Agent 框架、通达信生态、合规新动向

---

## 核心发现

### 发现1: jqktrader — easytrader 的现代替代品日趋成熟

jqktrader 在 2026 年初获得大量关注，核心改进点：

- **底层升级**: 从老旧的 `pywinauto` 基础升级，补全 easytrader 长期缺失的关键依赖
- **OCR 验证码**: 集成 Tesseract OCR，通过 `utils/captcha.py` 自动处理交易验证码
- **性能监控**: `utils/perf.py` 模块提供交易性能追踪
- **API 兼容**: 与 easytrader API 兼容，可 drop-in 替换

```python
import jqktrader

trader = jqktrader.Trader()
trader.connect(
    r'D:\同花顺软件\同花顺\xiadan.exe',
    r'D:\Tesseract-OCR\tesseract.exe'
)
# 查询持仓
positions = trader.get_positions()
print(f"当前持仓: {positions}")
```

**实践意义**: 对于 UI 自动化路线，jqktrader 已成为 easytrader 的首选替代。但需注意仍依赖 Windows + 同花顺客户端。Jetson Linux 环境不适用。

### 发现2: TradingAgents-CN — A 股多智能体交易框架进入实用阶段

TradingAgents-CN (GitHub 66K+ stars) 是首个面向中文用户的多智能体 LLM 金融交易框架：

**七角色架构** (模仿真实交易公司):
1. **基本面分析师** — 财务数据、估值模型
2. **情绪分析师** — 社交媒体、舆情
3. **新闻分析师** — 财经新闻过滤与评估
4. **技术分析师** — K线、指标、形态
5. **研究员 (Bull/Bear)** — 多空观点对立辩论
6. **交易员** — 综合决策，执行买卖
7. **风险经理** — 敞口监控、仓位控制

**技术栈**: Python 3.10+ | LangChain | Streamlit | MongoDB | Redis

**LLM 支持 (v0.1.13)**:
- OpenAI (原生)
- Google AI (Gemini 2.5/2.0 系列，9 个模型)
- DeepSeek V3
- 阿里百炼
- OpenRouter (60+ 模型)

**数据源**: Tushare | AkShare | FinnHub | Yahoo Finance | pytdx (A 股)

**部署方式**: Docker Compose 一键部署，支持 ARM 架构 (docker-compose.hub.nginx.arm.yml)

```bash
# Docker 部署
docker-compose up -d
# 访问 http://localhost:8501
```

**关键局限**:
- 定位为**学习与研究**平台，不提供实盘交易指令
- 运行较卡（实测反馈）
- 需要消耗大量 LLM token

**对 Hermes 的启发**: 可以借鉴其多角色辩论机制，构建轻量版 A 股分析 Agent。无需 MongoDB/Redis 全套，用 Hermes 本身的 delegate_task 即可编排多 Agent 讨论。

### 发现3: 通达信 TdxQuant — 正式版发布，新竞争者入局

通达信 2025-2026 推出 TdxQuant Python 量化框架 (v1.0.4)，成为 QMT 的竞品：

**核心特点**:
- 基于 C++ 底层架构，策略执行高效
- Python 插件系统 (`tqcenter` / `tdxquant`)
- 需动态注入 `sys.path` 连接通达信进程

```python
import sys, os
tdx_install_path = r"D:\new_tdx"
pyplugins_user_path = os.path.join(tdx_install_path, "PYPlugins", "user")
sys.path.insert(0, pyplugins_user_path)

import tqcenter as tq
tq.initialize(__file__)  # 建立通信桥梁

data = tq.get_market_data(
    field_list=['Open', 'High', 'Low', 'Close', 'Amount'],
    stock_list=['SH600000', 'SZ000001'],
    start_time='20250101',
    end_time='20251231'
)
```

**数据清洗痛点**: `get_market_data` 返回宽表 (Wide Format)，需转换为长表：

```python
def wide_to_long(raw_data, field_list):
    first_field = field_list[0]
    first_df = raw_data.get(first_field, {})
    df_list = []
    for stock_code in first_df.columns:
        stock_data = {}
        for field in field_list:
            field_data = raw_data.get(field, {})
            if isinstance(field_data, pd.DataFrame) and stock_code in field_data.columns:
                stock_data[field] = field_data[stock_code].values
        stock_df = pd.DataFrame(stock_data)
        stock_df['stock_code'] = stock_code
        df_list.append(stock_df)
    return pd.concat(df_list, ignore_index=True)
```

**对比 MiniQMT**:
- TdxQuant 免费、轻量、C++ 高效
- MiniQMT 生态更成熟 (xtquant 已上架 PyPI)
- 两者都仅支持 Windows

### 发现4: 2026 量化软件排名格局变化

2026 年量化交易软件 Top 10 排名反映了行业趋势：

| 排名 | 软件 | 定位 | Python 支持 |
|------|------|------|------------|
| 1 | QMT | 专业量化开发 | ✅ VBA + Python |
| 2 | PTrade | 云端策略执行 | ✅ Python |
| 3 | MiniQMT | 极简量化 | ✅ xtquant |
| 4 | 通达信量化 | 轻量级 | ✅ TdxQuant |
| 5 | SuperMind | 云端研究+回测 | ✅ |

**趋势**: MiniQMT 用户保有量已不逊于 QMT 和 PTrade，成为入门首选。

### 发现5: R&D-Agent-Quant 生态持续演进

微软 R&D-Agent (GitHub 12,000+ stars) 量化版:
- **NeurIPS 2025 接收**
- 与 Qlib 深度集成
- 五步闭环: 假设生成 → 代码实现 → 真实回测 → 反馈分析 → 迭代进化
- 端到端成本 < $10
- **IC≈0.0532, ARR≈14.21%, IR≈1.74** (沪深300基准)

教程资源已丰富化，zhichai.net 提供从安装到自定义的完整指南。

---

## 技术细节

### xtquant 架构深度剖析

```
MiniQMT 客户端 (XtMiniQmt.exe)
    ↕ TCP 本地通信
xtquant Python 包
    ├── xtdata (行情模块)
    │   ├── K线数据 (日/分钟/Tick)
    │   ├── 财务数据
    │   ├── 合约基础信息
    │   └── 板块/行业分类
    └── xttrader (交易模块)
        ├── 报单/撤单
        ├── 查询资产/委托/成交/持仓
        └── 主推消息回调 (资金/委托/成交变动)
```

**Python 版本支持矩阵**: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 — 不同版本自动切换 whl

### pytdx — 纯 Python 行情接口

通达信行情数据接口，不依赖 C++ 扩展：

```python
from pytdx.hq import TdxHq_API

api = TdxHq_API()
if api.connect('119.147.212.81', 7709):
    # 获取日K线
    df = api.to_df(api.get_security_bars(9, 0, '000001', 0, 100))
    # 9=日线, 0=深市, 股票代码, 起始位置, 数量
    print(df[['open', 'close', 'high', 'low', 'vol']])
    api.disconnect()
```

**特点**: 纯 Python、线程安全、心跳包机制、支持 Python 2.7+/3.5+

### TradingAgents-CN 实战部署

**Docker Compose 部署**:
```yaml
# docker-compose.yml 核心配置
services:
  trading-agents:
    image: tradingagents-cn:latest
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_URI=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis
  mongo:
    image: mongo:7
  redis:
    image: redis:7
```

**使用流程**:
1. 启动 → 浏览器访问 `http://localhost:8501`
2. 侧边栏配置 LLM 提供商与模型
3. 输入股票代码 (如 `000001`)
4. 设定研究深度 (1-5 级)
5. 点击「开始分析」→ 查看多 Agent 协作过程
6. 导出报告 (Markdown/Word/PDF)

---

## 实践启发

### 1. 轻量级 A 股分析 Agent 方案

**不需要** MongoDB/Redis/Docker 全套，利用 Hermes 现有能力：

```
用户输入股票代码
    ↓
Hermes delegate_task 编排多 Agent:
    ├── Agent-1: web_search 搜索新闻/公告
    ├── Agent-2: pytdx 获取行情数据 → 技术指标计算
    ├── Agent-3: AkShare 获取财务数据 → 基本面分析
    └── Agent-4: 综合辩论 → 最终建议
```

**关键**: 不做实盘交易，只做分析辅助。合规风险最低。

### 2. 多工具选型决策树

```
是否需要实盘自动下单？
├── 是 → 在 Windows 机器上
│   ├── 低频 → jqktrader / easytrader
│   └── 中频 → miniQMT + xtquant
├── 否 (仅分析)
│   ├── 有 iFinD 账号 → iFinD API
│   ├── 无账号 → pytdx (免费) + pywencai (免费)
│   └── AI 辅助 → TradingAgents-CN (学习) / Hermes Agent (定制)
└── 在 Jetson Linux 上
    └── pytdx + AkShare + pywencai → 纯分析/回测
```

### 3. 合规红线提醒

2026 年监管动态:
- **所有程序化交易需向券商报备** — 包括 LLM 驱动的交易决策
- **AI Agent 交易报备** — 2026 年度监管报告首次将 AI Agent 列为新兴关注点
- 撤单率 <50%，集合竞价禁止交易
- 高频认定: ≥300 笔/秒 或 ≥20000 笔/日

---

## 知识缺口

1. **TdxQuant vs xtquant 深度性能对比** — 延迟、稳定性、数据完整性实测
2. **jqktrader + Wine Linux 兼容性** — 理论可行但 pywinauto 依赖 Windows API
3. **TradingAgents-CN A 股回测精度** — pytdx 数据质量 vs 实际行情
4. **通达信 trade.dll / TradeX.dll 接口** — 私有交易接口的合规边界
5. **AI Agent 交易报备实操** — 具体报备流程、材料、时间节点
6. **xtquant 3.13 bug 修复进度** — `download_sector_data()` 是否已修复
7. **pywencai 反爬升级应对** — 2026 年问财反爬策略变化

---

## 进化闭环评估

| 内容 | 类型 | 采纳价值 | 决策 |
|------|------|----------|------|
| jqktrader 作为 easytrader 替代 | 工具更新 | 已在 Skill 中记录 | 无需新增 |
| TradingAgents-CN 多角色架构 | 新框架 | 借鉴思路，不引入依赖 | 仅存笔记 |
| TdxQuant 正式版发布 | 新工具 | Linux 不适用 | 仅存笔记 |
| pytdx 纯 Python 接口 | 可用工具 | Jetson 可直接用 | ⚡ 记录到 memory |
| AI Agent 交易报备合规 | 合规信息 | 未来必须关注 | ⚡ 更新 Skill 知识缺口 |
| xtquant Python 版本矩阵 | 版本信息 | 已在 Skill 中 | 无需新增 |
| 2026 量化软件排名 | 市场信息 | 了解即可 | 仅存笔记 |

**进化动作**:
- pytdx 免费行情接口 → memory (Jetson 可用)
- AI Agent 交易报备 → patch Skill 知识缺口

---

*字数: ~2800 字 | 核心发现: 5 个 | 代码示例: 6 个 | 知识缺口: 7 个*

## 相关笔记
- [wencai-stock-picker-notes](../2026-04-06-wencai-stock-picker-notes.md)
- [OpenClaw-4-things-persistent-tasks](../2026-04-10-OpenClaw-4-things-persistent-tasks.md)
- [stock-trading-discipline-washout](../2026-04-11-stock-trading-discipline-washout.md)
- [通达信tdxquant量化模拟交易封装](../2026-04-24-通达信tdxquant量化模拟交易封装.md)
- [LLM-Agent驱动量化交易系统前沿学习](../2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [MACD-KDJ共振策略](../2026-05-08-MACD-KDJ共振策略.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](../2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [RSI布林带组合策略](../2026-05-11-RSI布林带组合策略.md)
- [板块轮动资金流向分析](../2026-05-11-板块轮动资金流向分析.md)
- [板块轮动概念轮动](../2026-05-18-板块轮动概念轮动.md)
- [板块轮动-主力资金-2026年5月](../2026-05-20-板块轮动-主力资金-2026年5月.md)
- [rsi-bollinger-strategy](2026-05-06-rsi-bollinger-strategy.md)
- [板块轮动与北向资金流向](2026-05-06-板块轮动与北向资金流向.md)
- [技术指标组合策略-多指标确认](2026-05-09-技术指标组合策略-多指标确认.md)
- [A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研](2026-05-16-A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研.md)
- [动态止损策略对比](2026-05-17-动态止损策略对比.md)
- [北向资金主力资金流向指标有效性验证-深度研究](2026-05-17-北向资金主力资金流向指标有效性验证-深度研究.md)
- [北向资金主力资金流向指标有效性验证](2026-05-17-北向资金主力资金流向指标有效性验证.md)
- [实盘模拟vs真实交易技术差异](2026-05-17-实盘模拟vs真实交易技术差异.md)
- [ths-auto-trader-2025-2026-tech-ecosystem-update](2026-05-18-ths-auto-trader-2025-2026-tech-ecosystem-update.md)
- [VLA-AD视觉语言动作策略蒸馏](2026-05-19-VLA-AD视觉语言动作策略蒸馏.md)
- [ths-auto-trader-api-era-ecosystem](2026-05-19-ths-auto-trader-api-era-ecosystem.md)
- [板块轮动-北向资金](2026-05-19-板块轮动-北向资金.md)
- [板块轮动-概念轮动](2026-05-19-板块轮动-概念轮动.md)
- [VPO向量策略优化多样性训练提升推理搜索](2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [easytrader-deep-dive-2026-05-17](easytrader-deep-dive-2026-05-17.md)
- [ths-auto-trader-2025-2026-ecosystem-update](ths-auto-trader-2025-2026-ecosystem-update.md)
- [ths-auto-trader-2026](ths-auto-trader-2026.md)
- [ths-auto-trader-20260517](ths-auto-trader-20260517.md)
- [ths-auto-trader-architecture-deep-dive-20260517](ths-auto-trader-architecture-deep-dive-20260517.md)
- [ths-auto-trader-deep-dive](ths-auto-trader-deep-dive.md)
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-auto-trader-深度研究-2026-05-17](ths-auto-trader-深度研究-2026-05-17.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [动态止损策略深度研究-2026-05-17](动态止损策略深度研究-2026-05-17.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
