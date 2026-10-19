# 同花顺(THS)自动交易系统深度研究报告

> 研究日期：2026年5月17日  
> 研究方法：GitHub 仓库探索、开源项目代码分析、技术文档提取

---

## 一、研究概述

本报告通过系统性搜索和深入分析 GitHub 开源项目、技术文档和社区资源，全面梳理了同花顺(THS)自动交易系统的最新技术方案。研究发现，同花顺自动交易主要存在三条技术路线：**UI自动化模拟操作**、**iFinD数据API+券商交易接口**、以及**MiniQMT量化接口**。以下按路线逐一展开。

---

## 二、核心发现

### 核心发现 1：easytrader —— 最成熟的开源同花顺自动交易框架

**项目地址**: https://github.com/shidenggui/easytrader  
**Star数**: 9,700+ | **Fork数**: 3,000+ | **最近更新**: 2026年2月

easytrader 是当前最成熟、社区最活跃的同花顺客户端自动化交易框架。其核心架构如下：

**支持的券商客户端**:
- 同花顺通用客户端（`universal_clienttrader`）
- 华泰证券（`ht_clienttrader`）
- 国金证券（`gj_clienttrader`）
- 银河证券（`yh_clienttrader`）
- 五矿证券（`wk_clienttrader`）
- 国发证券（`gf_clienttrader`）

**核心模块结构**:
```
easytrader/
├── api.py                      # 核心API入口
├── clienttrader.py             # 客户端交易基类
├── universal_clienttrader.py   # 通用客户端（同花顺）
├── grid_strategies.py          # 网格数据读取策略
├── refresh_strategies.py       # 刷新策略
├── server.py                   # 远程服务模式
├── miniqmt/                    # MiniQMT量化接口
├── follower.py                 # 策略跟随基类
├── joinquant_follower.py       # 聚宽策略跟随
├── ricequant_follower.py       # RiceQuant策略跟随
├── xq_follower.py              # 雪球策略跟随
└── pop_dialog_handler.py       # 弹窗处理
```

**关键技术原理**: 使用 `pywinauto` 的 UIA (UI Automation) 后端，通过 Windows 句柄操作同花顺下单程序（`xiadan.exe`），模拟键鼠操作完成买卖、撤单、查询等交易动作。数据读取采用 `WMCopy` 网格策略，通过剪贴板读取表格数据。

---

### 核心发现 2：iFinD API —— 同花顺官方数据接口体系

**项目参考**: https://github.com/reskfa/wind2ths  
**发现日期**: 2025年

iFinD（同花顺金融数据终端）提供了完整的 Python SDK（`iFinDPy`），是同花顺官方的数据查询接口。虽然 iFinD 本身主要是**数据接口**而非交易接口，但它是构建量化交易系统的重要数据层。

**iFinD Python SDK 核心 API 映射**:

| 功能场景 | iFinD API 函数 | 说明 |
|---------|---------------|------|
| 日线行情 | `THS_HistoryQuotes()` | 获取历史K线数据 |
| 截面数据 | `THS_BD()` | 获取PE/PB等基本面数据 |
| 实时行情 | `THS_Snapshot()` / `THS_RQ()` | 获取实时行情快照 |
| 分钟K线 | `THS_HF()` | 高频分钟级数据 |
| 成分股/板块 | `THS_DataPool()` | 指数成分股、行业板块 |
| 宏观经济 | `THS_EDBQuery()` | 宏观经济指标 |
| 交易日历 | `THS_DateQuery()` | 交易日查询 |
| 日期偏移 | `THS_DateOffset()` | 交易日偏移计算 |

**认证与连接方式**:
```python
import os
from iFinDPy import *

# 登录认证
THS_iFinDLogin(os.environ.get('THS_ACCOUNT'), os.environ.get('THS_PASSWORD'))

# 查询日线行情
data = THS_HistoryQuotes("600519.SH", "close;open;high", "CPS:1", "2023-01-01", "2023-01-31")
df = THS_Trans2DataFrame(data)

# 登出
THS_iFinDLogout()
```

**关键技术细节**:
- 字段分隔符使用**分号**（`;`）而非逗号
- 日期格式为 `YYYY-MM-DD`
- 认证方式为显式登录（需账号密码）
- 返回值通过 `THS_Trans2DataFrame()` 转为 DataFrame
- 复权参数使用 `CPS:1`（不复权为 `CPS:0`）

---

### 核心发现 3：HTTP API 服务化 —— 将同花顺交易封装为远程接口

**项目地址**: https://github.com/lantian555666/ths_auto_trade  
**Star数**: 20 | **Fork数**: 63

该项目将 easytrader 封装为 Flask HTTP API 服务，实现了同花顺交易的**远程化部署**：

**核心架构**: Flask Web Server + easytrader + 钉钉通知

**API 接口设计**:
```
# 查询余额
GET /api/balance?token=xxx

# 查询持仓
GET /api/position?token=xxx

# 查询当日成交
GET /api/orders/today?token=xxx

# 查询当日委托
GET /api/orders/filled?token=xxx

# 买入
POST /api/buy
# 参数: token, code, amount, price, is_market

# 卖出
POST /api/sell
# 参数: token, code, amount, price, is_market

# 撤单
GET /api/cancel?entrust_no=xxx&token=xxx
```

**关键技术实现**:
```python
import easytrader
from easytrader import refresh_strategies, grid_strategies

client_path = 'C:/ths/xiadan.exe'
user = easytrader.use('universal_client')
user.connect(client_path)
user.refresh_strategy = refresh_strategies.Toolbar(refresh_btn_index=4)
user.grid_strategy = grid_strategies.WMCopy
user.enable_type_keys_for_editor()
```

**风控设计**: 
- 3秒间隔限流（`interval_call` 装饰器）
- Token 认证保护
- 线程锁防止并发操作
- 钉钉机器人实时通知交易状态

---

### 核心发现 4：Streamlit 量化交易系统 —— 现代化 Web UI 方案

**项目地址**: https://github.com/yayale-lgtm/Happy-the-Year-of-the-Horse  
**Star数**: 16 | **最近更新**: 2026年1月

"马到成功量化交易系统 v3.0" 是一个基于 Python + Streamlit 的现代化量化交易系统，集成了四大模块：

1. **账户总览**: 连接交易客户端实时监控资金、持仓、盈亏
2. **策略回测**: 全市场历史数据回测，可视化收益曲线、夏普比率、最大回撤
3. **实盘控制**: 一键扫描选股+自动下单，含时间过滤（仅09:30-11:30, 13:00-14:55）、防重复买入、T+1检查、滑点控制
4. **策略工坊**: 在线策略开发编辑器，支持热加载

**目录结构**:
```
├── app.py                # Streamlit 主入口
├── data/                 # 数据持久化
│   ├── stock_pools.json  # 股票池配置
│   └── user_strategy.py  # 自定义策略代码
├── quant_system/         # 量化核心库
│   ├── core/             # 数据管理、账户管理
│   ├── strategy/         # 策略基类与内置策略
│   ├── backtest/         # 回测引擎
│   └── live/             # 实盘调度
└── jqktrader-main/       # 同花顺交易对接
```

**策略开发接口**:
```python
class MyStrategy(StrategyBase):
    def filter_universe(self, universe_ctx):
        """选股逻辑：每天调用一次，返回选中股票代码列表"""
        return pool
    
    def on_bar(self, context):
        """交易逻辑：返回 Signal.BUY / Signal.SELL / Signal.HOLD"""
        return Signal.HOLD
```

---

## 三、技术细节与代码示例

### 3.1 pywinauto 直连同花顺（底层方案）

**项目地址**: https://github.com/please-call-119/autotrader

这是最底层的实现方案，直接使用 `pywinauto` 操作同花顺下单程序的 Windows 句柄：

```python
from pywinauto import Application
from pywinauto.keyboard import send_keys
import pytesseract

class ThsTrader:
    def __init__(self, exe_path, account, password):
        try:
            # 尝试连接已存在的交易程序
            self.app = Application(backend="uia").connect(path=exe_path)
            win_name = self.app.top_window().set_focus().texts()[0]
            if win_name == '网上股票交易系统V6.9':
                self.main_window = self.app.window(
                    title="网上股票交易系统V6.9", 
                    control_type="Window"
                )
            else:
                self.login_exe(account, password)
        except Exception:
            self.start_exe(exe_path, account, password)
    
    def login_exe(self, account, password):
        login_windows = self.app['用户登录']
        login_windows.set_focus()
        
        # 输入账号
        account_win = login_windows.children()[0]
        account_win.type_keys(account)
        
        # 输入密码
        password_win = login_windows.children()[1]
        password_win.type_keys(password)
        
        # OCR识别验证码
        auth_code_png_win = login_windows.children()[3]
        auth_code_png = auth_code_png_win.capture_as_image()
        auth_code = pytesseract.image_to_string(
            auth_code_png, config="--psm 6 digits"
        )
        
        # 输入验证码并登录
        auth_code_win = login_windows.children()[2]
        auth_code_win.type_keys(auth_code)
        login_windows.children()[4].click_input()
```

**依赖环境**:
```
Python 3.9.7
pywin32==300
pytesseract==0.3.9
pillow==8.4.0
pywinauto==0.6.8
tesseract-ocr 3.05.02
券商同花顺客户端 V6.9
```

### 3.2 THSTrader API（简化封装）

**项目地址**: https://github.com/zhangshoug/THSTrader

```python
from THS.THSTrader import THSTrader

trader = THSTrader(r"C:\同花顺软件\同花顺\xiadan.exe")

# 获取资金
balance = trader.get_balance()
# 返回: {'资金余额': 198577.0, '可用金额': 197264.69, ...}

# 获取持仓
position = trader.get_position()
# 返回: [{'证券代码': 162411, '证券名称': '华宝油气', '股票余额': 2600, ...}]

# 买入
result = trader.buy(stock_no="162411", amount=100, price=0.541)
# 返回: {'success': True, 'entrust_no': '873674677', ...}

# 卖出
result = trader.sell(stock_no="162411", amount=100, price=0.62)

# 撤单
trader.cancel_entrust(entrust_no="873674677")
```

### 3.3 easytrader 使用方法

```python
import easytrader

# 方式1：使用通用客户端
user = easytrader.use('universal_client')
user.connect(r'C:\同花顺\xiadan.exe')

# 买入/卖出
user.buy('162411', price=0.5, amount=100)
user.sell('162411', price=0.6, amount=100)

# 市价买卖
user.market_buy('162411', amount=100)
user.market_sell('162411', amount=100)

# 查询
balance = user.balance
position = user.position
today_entrusts = user.today_entrusts
today_trades = user.today_trades

# 撤单
user.cancel_entrust('entrust_no')
```

---

## 四、技术方案对比

| 维度 | UI自动化 | iFinD API + 券商接口 | MiniQMT |
|------|-------------|---------------------|---------|
| **稳定性** | 低（依赖UI版本） | 高 | 高 |
| **速度** | 慢（秒级） | 快（毫秒级） | 快（毫秒级） |
| **门槛** | 低（免费） | 中（需iFinD账号） | 高（需QMT权限） |
| **适用场景** | 个人散户/学习 | 机构/专业量化 | 专业量化 |
| **数据获取** | 无（仅交易） | 完整金融数据 | 行情+交易 |
| **部署要求** | Windows桌面 | 任意OS | Windows + QMT客户端 |
| **维护成本** | 高（版本更新需适配） | 低 | 低 |
| **代表性项目** | easytrader, THSTrader | wind2ths, iFinDPy | easytrader miniqmt模块 |

---

## 五、实践启发

### 5.1 分层架构是最佳实践
现代量化交易系统应采用**数据层（iFinD）+ 策略层（回测引擎）+ 交易层（easytrader/QMT）+ 表现层（Streamlit Web UI）**的分层架构。马到成功系统 v3.0 的 `quant_system/` 模块化设计值得参考。

### 5.2 HTTP API 封装实现跨平台部署
将交易能力封装为 REST API（如 `ths_auto_trade` 项目）是关键突破。这使得：
- 策略引擎可部署在 Linux 服务器
- 交易客户端运行在 Windows 桌面
- 通过 HTTP 通信解耦两个环境

### 5.3 风控机制不可忽视
- **时间过滤**: 仅在交易时段执行
- **防重复买入**: 检查已有持仓
- **T+1检查**: A股当日买入不可卖出
- **频率限制**: API 调用间隔限制（3秒）
- **滑点控制**: 自定义买卖滑点

### 5.4 OCR 验证码处理是关键挑战
同花顺登录时存在验证码，需使用 Tesseract OCR 识别。验证码识别的准确性直接影响自动化系统的可靠性。

---

## 六、知识缺口与未来方向

### 6.1 当前知识缺口

1. **iFinD Python SDK 安装与配置细节缺失**
   - iFinD SDK 不在 PyPI 公开发布，需通过同花顺官方渠道获取
   - 账号申请门槛和费用结构不透明
   - SDK 的线程安全和并发限制文档不足

2. **MiniQMT 量化接口缺乏开源文档**
   - easytrader 集成了 miniqmt 模块，但缺少详细使用文档
   - QMT 的券商开通条件和资金门槛未明确
   - MiniQMT 的 API 接口规范未公开

3. **同花顺客户端版本兼容性问题**
   - 客户端频繁更新导致 UI 元素句柄变化
   - 不同券商版本的 THS 客户端存在差异
   - 缺少版本兼容性矩阵

4. **实盘合规与安全性**
   - 自动化交易的法律合规性边界不清
   - 账号安全（密码存储、传输加密）最佳实践缺失
   - 券商风控触发机制和应对策略不明

5. **性能与可靠性数据缺失**
   - 各方案的下单延迟测试数据未公开
   - 高频场景下的稳定性评估不足
   - 异常恢复和容错机制不够完善

### 6.2 推荐后续研究方向

- 深入研究 MiniQMT 的 API 规范和使用方法
- 对比不同券商 QMT 的功能和限制
- 研究同花顺 WebSocket/HTTP 行情接口
- 探索 AI/ML 策略集成方案
- 调研合规的量化交易框架（如 QMT 官方方案）

---

## 七、关键资源索引

| 资源 | 链接 | 说明 |
|------|------|------|
| easytrader | https://github.com/shidenggui/easytrader | 最活跃的同花顺交易框架，9.7K stars |
| THSTrader | https://github.com/zhangshoug/THSTrader | 简化版THS交易API |
| autotrader | https://github.com/please-call-119/autotrader | pywinauto底层实现参考 |
| ths_auto_trade | https://github.com/lantian555666/ths_auto_trade | Flask HTTP API封装方案 |
| 马到成功v3.0 | https://github.com/yayale-lgtm/Happy-the-Year-of-the-Horse | Streamlit量化交易系统 |
| wind2ths | https://github.com/reskfa/wind2ths | Wind→iFinD API迁移工具 |
| easytrader文档 | https://easytrader.readthedocs.io/ | 使用文档 |

---

## 八、总结

同花顺自动交易系统的技术生态以 **easytrader** 为核心框架，通过 Windows UI 自动化技术（pywinauto）操控同花顺下单程序实现交易自动化。在数据层面，**iFinD API** 提供了完整的金融数据查询能力。在工程化方面，HTTP API 封装和 Streamlit Web UI 代表了现代化的发展方向。MiniQMT 作为券商官方量化接口，提供了更稳定高效的交易通道但门槛较高。当前最大的挑战在于客户端版本兼容性、OCR验证码识别准确率、以及合规安全性。

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
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
