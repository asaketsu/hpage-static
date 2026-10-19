# 同花顺自动交易系统 — 全栈架构方案

> 2026-05-17 | proactive-learn Phase 3 整合产出 | Topic: ths-auto-trader
> 基于 5 份已有探索笔记的深度整合 + 本地知识蒸馏
> 难度: L4（架构级）| 字数: ~4500

---

## 一、核心结论（5 个关键发现）

### 发现 1：A 股零售量化存在 3 条技术路径，适用场景完全不同

| 路径 | 代表方案 | 延迟 | 资金门槛 | 适用策略 | 可靠性 |
|------|---------|------|---------|---------|--------|
| **GUI 自动化** | xdotool / easytrader | 200-1200ms | 0 | 日线/小时线趋势 | ⭐⭐-⭐⭐⭐⭐ |
| **券商 API** | QMT(xtquant) / PTrade | 10-50ms | 30-50万 | 分钟线/事件驱动 | ⭐⭐⭐⭐⭐ |
| **柜台直连** | 恒生 TTS / 金证 KCBP | 1-10ms | 100万+ | 高频/做市 | ⭐⭐⭐⭐⭐ |

**关键洞察**：对 ths-auto-trader 项目（Jetson Orin + Linux 环境），推荐路径：
- **短期**：xdotool（已验证可用，Linux 原生支持）
- **中期**：QMT + xtquant（需 Windows VM 或远程券商 API 服务）
- **长期**：PTrade 程序化交易（券商直连，最低延迟）

### 发现 2：Jetson Orin (Linux/ARM64) 环境的特殊约束

Jetson Orin Nano Super 运行 Ubuntu (aarch64)，这带来几个关键约束：

1. **同花顺 Linux 版本**：THS 提供了 Linux 客户端（deb 包），但功能受限，缺少部分 Windows 版本的量化功能
2. **easytrader 不可用**：依赖 pywinauto（Windows Accessibility API），Linux 无法运行
3. **xdotool 是唯一 GUI 方案**：Linux 下自动化只能用 xdotool/xdg/AT-SPI
4. **容器化限制**：THS 客户端需要 X11 显示环境，Docker 内运行需要 Xvfb + VNC
5. **ARM 兼容性**：tushare/akshare 纯 Python 无问题，但 numpy/pandas 在 ARM64 上性能略低于 x86

**环境优化建议**：
```bash
# 确保 X11 转发正常（SSH 访问时）
export DISPLAY=:0
# 或使用 VNC/XRDP 远程桌面

# THS Linux 客户端安装
sudo dpkg -i ths_linux_*.deb
sudo apt-get install -f  # 修复依赖

# 验证 xdotool 可操作性
xdotool search --name "同花顺"
```

### 发现 3：完整量化系统需要 5 层架构，不是"下单脚本"

一个可用的自动交易系统不只是 GUI 自动化，需要完整 5 层：

```
┌─────────────────────────────────────────────────┐
│ Layer 5: 风控层 (Risk Management)                 │
│  - 最大回撤限制、单票仓位上限、止损规则              │
│  - 异常检测（闪崩、涨跌停、停牌）                    │
├─────────────────────────────────────────────────┤
│ Layer 4: 策略层 (Strategy Engine)                 │
│  - 信号生成（北向因子 + 技术指标 + 基本面）          │
│  - 调仓逻辑（频率、滑点预算、冲击成本估算）          │
├─────────────────────────────────────────────────┤
│ Layer 3: 回测层 (Backtest Engine)                 │
│  - 历史数据回放、手续费模型、滑点模拟               │
│  - Walk-Forward 验证、参数敏感性分析               │
├─────────────────────────────────────────────────┤
│ Layer 2: 数据层 (Data Pipeline)                   │
│  - AKShare/Tushare 数据源适配                      │
│  - 北向资金/主力资金/行情/基本面 多源融合            │
│  - 数据缓存（SQLite/Parquet）、增量更新             │
├─────────────────────────────────────────────────┤
│ Layer 1: 执行层 (Execution Engine)                │
│  - xdotool GUI 自动化（Linux/Jetson 方案）         │
│  - 订单状态管理（pending/filled/canceled）          │
│  - 成交确认、部分成交处理                           │
└─────────────────────────────────────────────────┘
```

**现有 ths-auto-trader 项目的状态**：
- Layer 1: ✅ xdotool 基础下单已验证
- Layer 2: ⚠️ AKShare 数据获取已探索，但未整合到系统
- Layer 3: ⚠️ BacktestEngine 框架已有，但北向因子未接入
- Layer 4: ❌ 策略信号生成逻辑未实现
- Layer 5: ❌ 风控层未实现

### 发现 4：xdotool 下单的容错必须覆盖 7 类异常

基于已有笔记整合，xdotool 方案需要处理的 7 类异常：

| 异常类型 | 概率 | 检测方法 | 恢复策略 |
|---------|------|---------|---------|
| **窗口焦点丢失** | 高 | `xdotool getactivewindow` 验证 | 重新获取焦点 |
| **控件位置偏移** | 中 | 截图 + OCR 验证按钮文本 | 相对坐标重定位 |
| **网络超时** | 中 | 券商回报超时（>5s） | 重试（最多 3 次） |
| **价格涨停/跌停** | 低 | 盘口检查买一/卖一量 | 跳过该标的 |
| **余额不足** | 低 | 下单前查询 `balance` | 减少数量或跳过 |
| **客户端崩溃** | 极低 | 进程检测 `pgrep ths` | 自动重启客户端 |
| **交易时段外** | 周期性 | 时间校验 9:30-11:30/13:00-15:00 | 休眠等待 |

**推荐容错架构**：
```python
class RobustExecutor:
    """xdotool 下单容错执行器"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def execute_order(self, code, direction, price, amount):
        for attempt in range(self.MAX_RETRIES):
            try:
                # Pre-check: verify trading session
                if not self.is_trading_hours():
                    raise TradingHoursError()
                
                # Pre-check: verify THS client alive
                if not self.is_client_alive():
                    self.restart_client()
                    time.sleep(5)
                
                # Pre-check: verify window focus
                self.ensure_focus()
                
                # Execute: xdotool sequence
                result = self.xdotool_buy(code, price, amount)
                
                # Post-check: verify order submitted
                if self.verify_order_submitted(code, direction, amount):
                    return OrderResult(success=True, attempt=attempt+1)
                    
            except (FocusLostError, ClientCrashError) as e:
                self.log.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(self.RETRY_DELAY * (attempt + 1))
            except (BalanceError, PriceLimitError) as e:
                return OrderResult(success=False, reason=str(e))
        
        return OrderResult(success=False, reason="Max retries exceeded")
```

### 发现 5：数据层是系统成败的关键——多源融合方案

单一数据源会失败（API 限流、数据缺口、服务下线）。推荐双源热备：

```python
class DataSourceManager:
    """多数据源管理器 — 双源热备 + 自动降级"""
    
    PRIORITY = ['tushare', 'akshare']  # 优先级排序
    
    def get_northbound_flow(self, start_date, end_date):
        """获取北向资金流向 — 自动降级"""
        for source_name in self.PRIORITY:
            try:
                source = self.sources[source_name]
                data = source.fetch_northbound(start_date, end_date)
                if self.validate(data):
                    return data
            except Exception as e:
                self.log.warning(f"{source_name} failed: {e}, falling back...")
                continue
        
        # 全部失败 → 使用缓存
        return self.cache.get_northbound(start_date, end_date)
    
    def validate(self, data):
        """数据质量校验"""
        checks = [
            len(data) > 0,                          # 非空
            not data.isnull().all(axis=1).any(),     # 无全空行
            data['net_flow'].abs().max() < 1e6,      # 数值范围合理（亿元级）
        ]
        return all(checks)
```

**数据缓存策略**：
- 本地存储：Parquet 格式（压缩比高，读取快）
- 增量更新：每日收盘后自动拉取当日新数据
- 历史回补：首次运行时批量获取 3 年历史数据
- 存储位置：`~/ths-data/cache/`（预估 3 年数据 < 500MB）

---

## 二、技术深度：可落地的系统架构

### 2.1 推荐目录结构

```
~/ths-auto-trader/
├── config/
│   ├── strategy.yaml      # 策略参数（因子权重、调仓频率）
│   ├── risk.yaml          # 风控参数（止损线、仓位上限）
│   └── data_sources.yaml  # 数据源配置（API keys、缓存路径）
├── data/
│   ├── cache/             # Parquet 缓存
│   └── raw/               # 原始数据备份
├── engine/
│   ├── executor.py        # xdotool 执行器（含容错）
│   ├── data_manager.py    # 多源数据管理
│   ├── strategy.py        # 策略信号生成
│   ├── risk_manager.py    # 风控模块
│   └── backtest.py        # 回测引擎
├── factors/
│   ├── northbound.py      # 北向资金因子（4 维）
│   ├── technical.py       # 技术指标因子
│   └── fundamental.py     # 基本面因子
├── logs/                  # 运行日志
├── notebooks/             # Jupyter 研究笔记本
├── tests/                 # 单元测试
└── main.py                # 主入口（调度器）
```

### 2.2 日度运行调度

```python
# main.py — 日度调度器
import schedule
import time

# 08:50 — 启动前检查（数据更新、系统健康）
schedule.every().day.at("08:50").do(pre_market_check)

# 09:25 — 集合竞价后，生成当日信号
schedule.every().day.at("09:25").do(generate_signals)

# 09:30 — 开盘执行（首批订单）
schedule.every().day.at("09:30").do(execute_opening_orders)

# 10:30 — 盘中检查（风控巡检）
schedule.every().day.at("10:30").do(risk_check)
schedule.every().day.at("13:30").do(risk_check)

# 14:50 — 尾盘调仓
schedule.every().day.at("14:50").do(execute_closing_orders)

# 15:10 — 盘后结算（更新缓存、生成报告）
schedule.every().day.at("15:10").do(post_market_settle)
```

### 2.3 风控模块核心逻辑

```python
class RiskManager:
    """风控模块 — 独立于策略，最高优先级"""
    
    def __init__(self, config):
        self.max_drawdown = config.get('max_drawdown', 0.15)      # 最大回撤 15%
        self.max_position = config.get('max_position', 0.10)       # 单票上限 10%
        self.daily_loss_limit = config.get('daily_loss_limit', 0.03) # 日亏损上限 3%
        self.stop_loss = config.get('stop_loss', 0.07)              # 个股止损 7%
    
    def check_before_order(self, portfolio, order):
        """下单前风控检查"""
        # 1. 单票仓位检查
        current_pct = portfolio.get_position_pct(order.code)
        if current_pct + order.amount * order.price / portfolio.total_value > self.max_position:
            return RiskResult(reject=True, reason="单票仓位超限")
        
        # 2. 日亏损检查
        daily_pnl = portfolio.get_daily_pnl()
        if daily_pnl / portfolio.total_value < -self.daily_loss_limit:
            return RiskResult(reject=True, reason="日亏损超限，暂停交易")
        
        # 3. 总仓位检查
        if portfolio.get_total_position_pct() > 0.80:
            return RiskResult(reject=True, reason="总仓位超过 80%")
        
        # 4. 回撤检查
        if portfolio.get_drawdown() > self.max_drawdown:
            return RiskResult(reject=True, reason="回撤超限，停止开新仓")
        
        return RiskResult(reject=False)
    
    def check_stop_loss(self, portfolio):
        """检查止损"""
        positions = portfolio.get_all_positions()
        to_stop = []
        for pos in positions:
            pnl_pct = (pos.current_price - pos.cost_price) / pos.cost_price
            if pnl_pct < -self.stop_loss:
                to_stop.append(pos)
        return to_stop
```

---

## 三、实践启发

### 3.1 开发优先级建议（Roadmap）

| 阶段 | 任务 | 预估工时 | 依赖 |
|------|------|---------|------|
| **P0** | 数据层（AKShare + 缓存 + 北向因子） | 2-3 天 | 无 |
| **P0** | xdotool 执行器（含容错） | 1-2 天 | 已有基础 |
| **P1** | 回测引擎接入北向因子 | 1-2 天 | P0 数据层 |
| **P1** | 策略信号生成（三因子融合） | 2-3 天 | P0 + P1 |
| **P2** | 风控模块 | 1 天 | 无（独立） |
| **P2** | 日度调度器 | 0.5 天 | P0-P1 |
| **P3** | 实盘模拟运行 | 1 周 | P0-P2 |

### 3.2 关键风险

1. **监管风险**：中国限制散户全自动交易，xdotool 方案处于灰色地带。建议：仅用于自有账户，不推广
2. **技术债务**：xdotool 方案的天花板在 500ms+ 延迟，长期需要迁移到 QMT
3. **数据成本**：AKShare 免费但限速，Tushare Pro 年费 500-5000 元（按积分）
4. **过拟合风险**：策略参数过多（4 个北向因子 + 多种窗口），必须 Walk-Forward 验证

---

## 四、知识缺口

1. **THS Linux 客户端版本**：控件树结构与 Windows 版差异？xdotool 定位是否需要适配？
2. **QMT 远程 API**：能否在 Linux 上通过 HTTP/WebSocket 调用 Windows 端 QMT？有人做过类似方案吗？
3. **北向因子的行业轮动效果**：东方证券研报提到但未详述，需要独立验证
4. **Jetson GPU 加速因子计算**：能否用 CUDA 加速 numpy/pandas 计算？实际提速比？
5. **实时行情推送**：AKShare 是否支持 WebSocket 实时推送？还是只能轮询？

---

## 五、参考资料

1. 已有探索笔记（5 份）：
   - `ths-auto-trader-20260517.md` — THS 平台概览
   - `easytrader-deep-dive-2026-05-17.md` — easytrader 架构分析
   - `xdotool-trading-automation-deep-dive.md` — xdotool 方案深度
   - `QMT-PTrade-量化接口调研-20260517.md` — 券商 API 对比
   - `2026-05-17-北向资金主力资金流向指标有效性验证-深度研究.md` — 因子验证
2. AKShare: https://github.com/akfamily/akshare
3. xtquant 文档: https://dict.thinktrader.net/nativeApi/start_now.html
4. Backtrader: https://www.backtrader.com/

---

*笔记生成时间：2026-05-17 16:15 | 整合了 5 份已有笔记 + 架构设计*
*下一步：在 ths-auto-trader 中实现数据层（AKShare + 缓存）*

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
- [ths-auto-trader-deep-dive](ths-auto-trader-deep-dive.md)
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
