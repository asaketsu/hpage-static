# THS Auto Trader（同花顺自动交易系统）深度技术笔记

> 📅 研究日期：2026-05-19
> 🏷️ 标签：`量化交易` `同花顺` `Python自动化` `pywinauto` `SuperMind` `API交易`
> 📊 信息来源：GitHub/Gitee 开源项目、PyPI、同花顺 SuperMind 官方文档、知乎/CSDN 技术博客、行业分析报告

---

## 一、核心发现

### 核心发现 1：同花顺自动化交易存在两条截然不同的技术路径

同花顺自动化交易在 2025-2026 年形成了两条清晰的技术路线：

**路径 A：GUI 自动化（客户端模拟操作）**
- 代表项目：`easytrader`、`jqktrader`、`THSAutoTrader`、`ths_trade`、`QFF`
- 核心原理：通过 Windows UI 自动化框架（`pywinauto`）模拟用户在同花顺 `xiadan.exe` 客户端上的鼠标键盘操作
- 技术栈：Python + `pywinauto` + Tesseract OCR（验证码识别）+ Windows API
- 优点：无需券商额外开通权限，任何已安装同花顺的用户均可使用
- 缺点：极度依赖客户端 UI 布局，版本更新可能导致失效；本质是"按键精灵"，无法保证 100% 成功率

**路径 B：官方量化平台 API（SuperMind / i问财）**
- 代表平台：同花顺 SuperMind（原 MindGo）
- 核心原理：通过同花顺官方提供的 Python SDK 和 `TradeAPI` 接口，在云端/本地直接进行策略回测和实盘交易
- 技术栈：Python + `tick_trade_api` + SuperMind 研究环境 + 券商通道
- 优点：官方支持、合规稳定、支持分钟级/tick级回测、算法交易（TWAP/VWAP）
- 缺点：需要付费版本才能实盘；部分功能仅限机构用户

**关键洞察**：2024-2025 年间，GUI 自动化路线的项目（如 jqktrader）已陆续停止维护，作者明确建议转向 QMT/PTrade 等专业量化交易软件。这标志着"野生自动化"正在向"官方合规化"过渡。

---

### 核心发现 2：THSAutoTrader 代表了 GUI 自动化路线的最新演进

`linlb/THSAutoTrader` 是截至 2026 年最活跃的同花顺自动化交易开源项目（144 commits），其技术架构值得深入分析：

**架构亮点：**

1. **闪电下单模式**：不像早期项目直接操作主窗口，而是利用同花顺内置的"闪电下单"窗口，这是一个更快、更简洁的下单界面，减少了 UI 操作步骤
2. **REST API 服务化**：将所有交易操作封装为 HTTP API 端点，实现了与策略引擎的解耦
3. **可视化 GUI 界面**：提供图形操作界面，降低使用门槛
4. **完整的交易生命周期覆盖**：下单→确认→撤单→查持仓→查成交→查资金

**API 端点设计分析：**

```
GET /                    # 健康检查
POST /order              # 下单接口（code, status, amount）
POST /confirm            # 订单确认（自动点击刷新按钮解决资金同步问题）
POST /cancel             # 撤单接口（支持全撤/分类撤/指定撤）
GET  /holdings           # 获取当前持仓
GET  /trades             # 获取今日成交
GET  /balance            # 获取资金余额
POST /click              # 模拟鼠标点击（自动激活 THS 窗口）
GET  /send_key?key=      # 模拟键盘输入（key=21+ENTER 触发闪电下单）
GET  /screenshot         # 获取当前页面截图
```

**关键工程细节：**
- 资金同步问题：确认接口内置了"自动点击刷新按钮"的逻辑，解决下单后资金余额不同步的问题——这是一个典型的生产环境 bug workaround
- 经纪商兼容性：持仓和成交的返回格式因券商不同而异，需要用户自行处理解析
- 使用 Poetry 管理依赖，PyInstaller 打包为独立可执行文件

---

### 核心发现 3：2026 年行业趋势——AI Agent + MCP 正在重构量化交易生态

根据同花顺官方量化平台 2026 年发布的行业分析，三个关键趋势正在重塑交易自动化：

**趋势 1：API 消费者从人类转向 AI Agent**
- 数据显示 50% 的 API 调用已来自 AI Agent（而非人类开发者）
- 预计到 2027 年，30% 的金融交易将由代表消费者行为的自主 Agent 发起
- MCP（Model Context Protocol）正在金融数据 API 领域快速普及

**趋势 2：从 REST 到"机器原生"数据消费**
- iTick 等服务商已推出 MCP API，不再从 REST 生成，而是专门为 AI 机器消费重建
- 专注于结构化输出、可预测格式、可直接使用的数据
- OpenClaw 框架将金融行情技能封装为 AI Agent 可调用的能力模块

**趋势 3：量化交易平民化加速**
- OpenClaw + 腾讯云轻量服务器（2核4G），个人投资者可搭建 24/7 量化分析系统
- 整个流程：数据源（行情API）→ AI 分析引擎 → 策略输出 → 推送通知
- 无需手写交易代码，AI 完成从数据采集到决策输出的全链路

---

## 二、技术细节与代码示例

### 2.1 GUI 自动化核心：pywinauto 操作 xiadan.exe 的技术原理

同花顺的独立下单程序 `xiadan.exe` 是一个标准的 Win32 GUI 应用。GUI 自动化的核心流程如下：

```python
# 核心依赖链
# pywinauto → 获取窗口句柄 → 识别控件 → 发送消息/模拟操作

from pywinauto import Application
import time

# 1. 连接到已运行的同花顺下单程序
app = Application().connect(path=r'C:\同花顺\xiadan.exe')

# 2. 获取主窗口
main_window = app.window(title='网上股票交易系统')

# 3. 输入股票代码 — 通过向编辑框发送键盘消息
main_window.Edit1.set_text('000001')  # 输入股票代码

# 4. 设置买卖方向 — 点击"买入"/"卖出"标签
main_window.TabCtrl.select(0)  # 0=买入, 1=卖出

# 5. 输入数量
main_window.Edit3.set_text('100')

# 6. 点击下单按钮
main_window.Button1.click()

# 7. 处理弹窗确认
confirm_dialog = app.window(title='确认')
confirm_dialog.Button1.click()  # 确认
```

**关键技术挑战及解法：**

| 挑战 | 解法 |
|------|------|
| 验证码识别 | Tesseract OCR 自动识别，需训练同花顺专用字库 |
| 客户端超时锁定 | 设置"界面不操作超时时间=0"（系统设置→界面设置） |
| 控件定位不稳定 | 智能按钮定位（ths_trade 的升级方案）：基于控件属性而非固定坐标 |
| 资金不同步 | 下单后自动触发"刷新"按钮（THSAutoTrader 的方案） |
| 多策略并发 | ths_trade 实现了交易下单自动排队机制，支持多策略发单 |

### 2.2 SuperMind 官方 TradeAPI 实盘交易

```python
# SuperMind 实盘交易核心代码
from tick_trade_api import TradeAPI

# 初始化 TradeAPI — 选择下单策略
# MarketPolicy: 市价下单; LimitPolicy: 限价下单
trade_api = TradeAPI('69271711', order_policy=MarketPolicy)

# 策略源码（可替换为自定义策略）
source_code = """
def init(context):
    pass

def before_trading(context):
    pass

def handle_bar(context, bar_dict):
    # 简单买入示例
    order_id = order('000001.SZ', 100)
    print(get_orders())

    # 撤单
    try:
        cancel_order(order_id)
    except:
        print('撤单失败')

    # 获取当日委托和成交
    print(get_open_orders())
    print(get_tradelogs())
    print(context.portfolio.stock_account)
    print(context.portfolio.positions)
"""

# 启动研究环境实盘
rtrade = research_trade(
    '研究环境策略',
    source_code,
    frequency='MINUTE',   # 按分钟频率执行
    trade_api=trade_api,
    signal_mode=False,
    recover_dt='today'
)
```

**算法交易支持（SuperMind TradeAPI 高级功能）：**

```python
# TWAP（时间加权平均价格）算法交易
twap_api = trade_api.NEW_TWAP(
    start_time='09:30',
    end_time='15:00',
    order_interval=60,        # 每60秒下一笔
    rechase_interval=30,      # 追单间隔
    min_order_number=100,     # 最小单笔数量
)
twap_api.order(symbol='000001.SZ', amount=100, price=0.01, pricetype=3)

# VWAP（成交量加权平均价格）算法交易
vwap_api = trade_api.NEW_VWAP(
    start_time='09:30',
    end_time='15:00',
    order_interval=60,
    sampledays=30,            # 采样30天历史成交分布
)
```

### 2.3 ths_trade 的 WEB API 服务框架

`skyformat99/ths_trade` 项目提供了一个完整的 WEB API 服务框架，核心特点：

```
架构层次：
┌─────────────────────────────┐
│     多策略引擎（策略A/B/C...）│
├─────────────────────────────┤
│     交易指令排队队列          │  ← 关键：自动排队避免并发冲突
├─────────────────────────────┤
│     WEB API 服务层            │  ← HTTP REST 接口
├─────────────────────────────┤
│     智能按钮定位引擎          │  ← 图像识别 + 控件匹配
├─────────────────────────────┤
│     同花顺 xiadan.exe        │  ← 实际交易执行
└─────────────────────────────┘
```

- **交易下单自动排队**：多个策略同时发送交易指令时，系统自动排队执行，避免 GUI 操作冲突
- **实时回报查询**：支持查询委托状态、成交回报
- **智能按钮定位**：不是基于固定坐标，而是基于按钮文本/属性智能匹配，增强了版本兼容性

### 2.4 MyTT 指标库：通达信/同花顺公式到 Python 的桥梁

`mpquant/MyTT` 项目实现了将通达信、同花顺、文华麦语言等指标公式最简移植到 Python：

```python
import pandas as pd
from MyTT import *

# 数据准备 — 只需要标准的 OHLCV 格式
CLOSE = df.close.values
OPEN  = df.open.values
HIGH  = df.high.values
LOW   = df.low.values

# 直接使用通达信风格的指标函数
MA5 = MA(CLOSE, 5)       # 5日均线
MA10 = MA(CLOSE, 10)     # 10日均线

# 金叉判断
CROSS(MA(CLOSE, 5), MA(CLOSE, 10))  # 5日均线上穿10日均线

# 涨停天数计算
BARSLAST(CLOSE / REF(CLOSE) >= 1.1)  # 上一次涨停到今天的天数

# MACD
DIF, DEA, MACD_VAL = MACD(CLOSE)

# KDJ
K, D, J = KDJ(CLOSE, HIGH, LOW, N=9, M1=3, M2=3)

# 布林带
UPPER, MID, LOWER = BOLL(CLOSE, N=20, P=2)
```

这个库的精妙之处在于：核心仅百行代码，纯 Python 实现（不依赖 talib），全部基于 numpy/pandas 封装，性能出色。

---

## 三、实践启发

### 3.1 项目选型决策树

```
你的需求是什么？
├── 快速验证策略想法
│   └── SuperMind 线上回测（免费、零部署）
├── 个人实盘自动化交易（预算有限）
│   ├── 能接受手动登录 → THSAutoTrader（REST API + GUI）
│   ├── 需要多策略 → ths_trade（排队机制）
│   └── 追求稳定 → 升级到 QMT/PTrade
├── 机构级量化（合规要求高）
│   └── SuperMind 付费版 + 本地 SDK + 券商专线
└── AI 驱动的量化分析
    └── OpenClaw + MCP + iTick API（2026 新范式）
```

### 3.2 GUI 自动化路线的 5 个关键陷阱

1. **客户端版本绑定**：同花顺更新后 UI 可能变化，必须固定版本（如 QFF 推荐的 THS_9.20.40_20230613.exe）
2. **超时锁定**：必须设置"界面不操作超时时间=0"，否则长时间运行后客户端自动锁定
3. **屏幕分辨率敏感**：部分基于坐标的操作在不同分辨率/DPI 下会偏移
4. **验证码中断**：偶尔弹出的验证码需要 OCR 处理，识别失败会导致流程卡死
5. **市价单资金冻结**：实盘按"涨停价×1.005"冻结资金，实际可买数量可能远小于预期

### 3.3 合规性考量

- **GUI 模拟方式**：完全基于用户操作模拟，无修改或破解同花顺客户端，在法律层面处于灰色地带但不违法
- **SuperMind 官方 API**：完全合规，走正规券商通道，监管认可
- **QMT/PTrade**：券商提供的专业量化通道，合规性最高
- **数据获取**：自行爬取交易所数据违法；应使用 iTick（免费）/ SuperMind / Wind 等合规数据源

---

## 四、知识缺口

### 4.1 待深入研究的方向

1. **QMT/Ptrade 技术架构**：2024-2025 年多个项目作者建议迁移到 QMT/PTrade，但缺乏详细的对比分析和技术文档。需要研究：
   - QMT 的 Python API 与同花顺 xiadan.exe 自动化的具体差异
   - 券商开通 QMT 的门槛和流程
   - QMT 与 SuperMind 的功能对比

2. **SuperMind 本地 SDK**：官方提到支持本地 SDK 和数据落地，但具体技术文档不公开。需要了解：
   - 本地 SDK 的接口设计与 `tick_trade_api` 的关系
   - 数据落地的格式和频率
   - 机构版本的私有化部署方案

3. **MCP 协议在金融交易中的具体应用**：
   - MCP Server 如何与交易执行系统对接
   - AI Agent 自主交易的合规框架
   - 实际延迟和可靠性数据

4. **高频场景下的性能瓶颈**：
   - GUI 自动化路线的订单延迟实测（用户报告 800ms+）
   - SuperMind 实盘的实际延迟
   - 网络环境对延迟的影响（不同地区、不同带宽）

5. **风控系统集成**：
   - 自动化交易如何集成实时风控
   - 异常情况（网络断连、客户端崩溃）的恢复机制
   - 多策略之间的资金分配和冲突管理

---

## 五、技术生态图谱

```
同花顺自动化交易技术生态（2025-2026）

┌──────────────────────────────────────────────────┐
│                   数据层                           │
│  iTick API │ SuperMind数据 │ pytdx │ i问财接口     │
└────────┬──────────┬──────────┬──────────┬────────┘
         │          │          │          │
┌────────▼──────────▼──────────▼──────────▼────────┐
│                   策略层                           │
│  SuperMind │ MyTT指标库 │ 自定义Python │ AI Agent  │
└────────┬──────────┬──────────┬──────────┬────────┘
         │          │          │          │
┌────────▼──────────▼──────────▼──────────▼────────┐
│                   执行层                           │
│  xiadan.exe │ SuperMind │ QMT │ PTrade │ 券商API  │
│  (GUI自动化) │ (官方API)  │(专业)│(专业)  │(直连)    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│              新兴趋势（2026）                       │
│  MCP协议 │ AI Agent自主交易 │ OpenClaw框架          │
│  大模型策略生成 │ FAPI安全标准 │ Zero Trust          │
└──────────────────────────────────────────────────┘
```

---

## 六、关键项目对比

| 项目 | 技术路线 | 维护状态 | 核心优势 | 核心局限 |
|------|---------|---------|---------|---------|
| `easytrader` | pywinauto GUI | ⚠️ 停更 | 支持多平台（THS/QMT/雪球） | 年久失修，依赖问题多 |
| `jqktrader` | pywinauto GUI | ❌ 已弃用 | 开箱即用，修复 easytrader 问题 | 作者建议转 QMT |
| `THSAutoTrader` | pywinauto + REST API | ✅ 活跃 | 闪电下单、GUI 界面、API 服务 | 仍依赖 GUI 操作 |
| `ths_trade` | GUI + WEB API 框架 | ✅ 活跃 | 多策略排队、智能定位、实时回报 | 复杂度高 |
| `QFF` | pywinauto GUI | ✅ 活跃 | 完整框架、CLI + 交互接口 | 需固定客户端版本 |
| SuperMind | 官方 API | ✅ 官方 | 合规、稳定、算法交易 | 付费才能实盘 |
| QMT/PTrade | 券商专业通道 | ✅ 官方 | 最专业、最稳定 | 开通门槛高 |

---

## 七、总结

同花顺自动交易系统在 2025-2026 年正处于一个关键的过渡期。传统的 GUI 自动化路线（`pywinauto` 模拟操作 `xiadan.exe`）虽然仍可用，但社区正在向两个方向分化：一是向券商官方的 QMT/PTrade 专业量化通道迁移，二是向 AI Agent 驱动的新范式（MCP + 大模型）演进。对于实践者而言，如果目标是快速验证策略，SuperMind 线上回测是最佳起点；如果目标是实盘自动化，THSAutoTrader 提供了最完整的 GUI 自动化方案，但长期应规划向 QMT 或 SuperMind 实盘 API 迁移。

---

*本笔记基于公开开源项目文档、官方平台资料及行业分析报告整理，仅供技术学习参考，不构成任何投资建议。*

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
- [rsi-bollinger-strategy](2026-05-06-rsi-bollinger-strategy.md)
- [板块轮动与北向资金流向](2026-05-06-板块轮动与北向资金流向.md)
- [技术指标组合策略-多指标确认](2026-05-09-技术指标组合策略-多指标确认.md)
- [动态止损策略对比](2026-05-17-动态止损策略对比.md)
- [北向资金主力资金流向指标有效性验证-深度研究](2026-05-17-北向资金主力资金流向指标有效性验证-深度研究.md)
- [北向资金主力资金流向指标有效性验证](2026-05-17-北向资金主力资金流向指标有效性验证.md)
- [实盘模拟vs真实交易技术差异](2026-05-17-实盘模拟vs真实交易技术差异.md)
- [ths-auto-trader-2025-2026-tech-ecosystem-update](2026-05-18-ths-auto-trader-2025-2026-tech-ecosystem-update.md)
- [VLA-AD视觉语言动作策略蒸馏](2026-05-19-VLA-AD视觉语言动作策略蒸馏.md)
- [ths-auto-trader-api-era-ecosystem](2026-05-19-ths-auto-trader-api-era-ecosystem.md)
- [板块轮动-北向资金](2026-05-19-板块轮动-北向资金.md)
- [板块轮动-概念轮动](2026-05-19-板块轮动-概念轮动.md)
- [easytrader-deep-dive-2026-05-17](easytrader-deep-dive-2026-05-17.md)
- [ths-auto-trader-2025-2026-ecosystem-update](ths-auto-trader-2025-2026-ecosystem-update.md)
- [ths-auto-trader-2026](ths-auto-trader-2026.md)
- [ths-auto-trader-20260517](ths-auto-trader-20260517.md)
- [ths-auto-trader-architecture-deep-dive-20260517](ths-auto-trader-architecture-deep-dive-20260517.md)
- [ths-auto-trader-deep-dive](ths-auto-trader-deep-dive.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
