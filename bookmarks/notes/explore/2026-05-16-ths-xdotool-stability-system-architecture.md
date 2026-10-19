# 同花顺 xdotool 自动化下单：交易引擎架构与系统级容错深度研究

> **主题**: ths-auto-trader — 交易引擎、行情数据源、策略交叉验证、状态持久化、通知系统  
> **日期**: 2026-05-16  
> **类型**: 本地知识蒸馏（源码精读 + 架构分析）  
> **字数**: ~3500 字  
> **素材来源**: `~/uclaw/project/ths-auto-trader/` 项目源码（trading_engine.py, risk_manager.py, config.py, market/data_source.py 等）

---

## 摘要

前两篇笔记聚焦于 xdotool 适配层的稳定性（窗口定位、坐标漂移、原子操作）。本文从**系统架构层面**深入分析交易引擎的 Tick 循环、行情数据源可靠性、多策略信号交叉验证、状态持久化与断点恢复、通知系统可靠性等五个关键维度。核心结论：xdotool 适配层的不稳定性只是冰山一角，交易引擎的**竞态条件、数据源降级、信号冲突处理、状态恢复**等系统级问题同样需要工业级容错设计。

---

## 核心发现一：交易引擎 Tick 循环的竞态条件与状态污染

### 源码现状分析

`TradingEngine._tick()` 是系统的核心循环（每 5 秒执行一次）：

```python
async def _tick(self):
    try:
        # 1. 获取账户状态
        account = self.broker.get_account()
        positions_list = self.broker.get_position()
        positions = {p.code: p for p in positions_list}

        # 2. 获取行情数据
        market_data = await self._fetch_market_data(list(positions.keys()))

        # 3. 更新风控状态
        if account.total_assets > 0:
            today_pnl = (account.total_assets - self.cfg.risk.initial_capital) / self.cfg.risk.initial_capital
            self.risk_manager.update_daily_pnl(today_pnl)

        # 4. 生成信号
        signals = self.portfolio.run_all_strategies(market_data, account, positions)

        # 5. 逐信号处理
        for signal in signals:
            await self._process_signal(signal, account, positions)
    except Exception as e:
        logger.error(f"Tick error: {e}", exc_info=True)
        await notifier.send(Notification(title="系统异常", body=str(e), level="error"))
```

**发现的竞态条件**：

| 场景 | 问题描述 | 风险等级 |
|------|---------|---------|
| **账户状态污染** | Tick N 读取的 `account` 在 Tick N+1 处理信号时可能已过时（同花顺账户余额已变化） | 🟡 中 |
| **持仓状态不一致** | Tick N 的 `positions` 在 Tick N+1 可能已变化（前一 tick 已下单成交） | 🟡 中 |
| **信号重复执行** | 多策略同时发出同一股票的买入信号，风控只拦截一次，可能导致重复下单 | 🔴 高 |
| **风控状态漂移** | `self.risk_manager._daily_trades` 在信号处理中递增，但 `_tick()` 外层异常时未回滚 | 🔴 高 |
| **通知风暴** | 5 秒内多个信号触发多个通知，飞书/微信可能限流 | 🟡 中 |

### 竞态条件详细分析

**问题1：账户/持仓状态的时间窗口**

```
Tick T0: 读取 account(cash=100000), positions={600000: qty=0}
Tick T0: 策略生成买入 600000 @ 10.50, qty=1000
Tick T0: 风控检查通过（可用资金充足）
Tick T0: 执行买入 → xdotool 点击
Tick T1 (5s后): 同花顺实际已扣款，account(cash=98950)
Tick T1: 策略再次生成买入 600000 @ 10.50
Tick T1: 风控检查 → 可用资金 98950，但风控用的是 Tick T0 的 account（cash=100000）
Tick T1: 风控误判通过 → 重复下单！
```

**改进方案：信号处理前重新读取账户状态**

```python
async def _process_signal(self, signal: Signal, account: Account, positions: dict):
    """处理单个信号：风控 → 执行 → 记录 → 通知"""
    
    # 关键修复：处理前重新读取最新账户状态
    fresh_account = self.broker.get_account()
    fresh_positions = {p.code: p for p in self.broker.get_position()}
    
    # 使用最新状态进行风控检查
    reject = self.risk_manager.check_signal(signal, fresh_account, fresh_positions)
    if reject:
        logger.warning(f"信号被风控拦截（最新状态）: {signal.code} {signal.direction.value} → {reject}")
        return
    
    # 重新计算数量（基于最新可用资金）
    quantity = self._calc_quantity(signal, fresh_account)
    if quantity <= 0:
        return
    
    # ... 继续执行
```

**问题2：信号去重与合并**

当前 `PortfolioManager.run_all_strategies()` 返回所有策略的信号列表，**没有任何去重或合并逻辑**：

```python
signals = self.portfolio.run_all_strategies(market_data, account, positions)
for signal in signals:
    await self._process_signal(signal, account, positions)
```

如果 MA_Trend 和 Momentum 同时发出 600000 的买入信号，系统会执行两次下单。

**改进方案：信号聚合层**

```python
from collections import defaultdict

def aggregate_signals(signals: list[Signal]) -> list[Signal]:
    """聚合同方向同标的信号：取最大数量或加权平均"""
    grouped = defaultdict(list)
    
    for s in signals:
        key = (s.code, s.direction)  # (股票代码, 买卖方向)
        grouped[key].append(s)
    
    aggregated = []
    for (code, direction), sigs in grouped.items():
        if direction == Direction.BUY:
            # 买入：取最大数量（保守策略）或加权平均
            max_qty = max(s.quantity or 0 for s in sigs)
            avg_strength = sum(s.strength for s in sigs) / len(sigs)
            avg_price = sum(s.price for s in sigs) / len(sigs)
            aggregated.append(Signal(
                code=code, direction=direction,
                quantity=max_qty, price=avg_price,
                strength=avg_strength, strategy="aggregated"
            ))
        else:
            # 卖出：取最小数量（避免过度卖出）
            min_qty = min(s.quantity or 0 for s in sigs)
            aggregated.append(Signal(
                code=code, direction=direction,
                quantity=min_qty, strategy="aggregated"
            ))
    
    return aggregated
```

---

## 核心发现二：行情数据源的可靠性与降级链

### 当前数据源架构

`MarketDataSource` 依赖 `akshare` 获取行情数据：

```python
from .market.data_source import MarketDataSource
ds = MarketDataSource()
for code in codes:
    try:
        df = ds.get_daily(code)
        if not df.empty:
            data[code] = df
    except Exception as e:
        logger.warning(f"获取 {code} 行情失败: {e}")
```

**问题**：`akshare` 是第三方爬虫库，存在以下不稳定因素：

| 风险 | 说明 | 影响 |
|------|------|------|
| 接口变更 | 同花顺/东方财富网页改版导致爬虫失效 | 🔴 高 |
| 反爬限制 | IP 被封或请求频率限制 | 🔴 高 |
| 数据延迟 | 爬虫获取的是历史 K 线，非实时行情 | 🟡 中 |
| 无降级 | 单个股票获取失败不影响其他，但无备用数据源 | 🔴 高 |

### 工业级降级链设计

```python
class ResilientDataSource:
    """行情数据源降级链：akshare → 备用源 → 缓存 → 空"""
    
    def __init__(self):
        self.sources = [
            ("akshare", self._fetch_akshare),
            ("tushare", self._fetch_tushare),  # 备用：需要 token
            ("cache", self._fetch_cache),       # 降级：使用最近一次成功数据
        ]
        self._cache: dict[str, pd.DataFrame] = {}
    
    def get_daily(self, code: str) -> Optional[pd.DataFrame]:
        """按优先级尝试各数据源"""
        for source_name, fetch_func in self.sources:
            try:
                df = fetch_func(code)
                if df is not None and not df.empty:
                    self._cache[code] = df  # 更新缓存
                    return df
            except Exception as e:
                logger.warning(f"[{source_name}] 获取 {code} 失败: {e}")
                continue
        
        # 所有源都失败，返回缓存（如果有）
        if code in self._cache:
            logger.warning(f"[cache] {code} 使用缓存数据（可能过时）")
            return self._cache[code]
        
        return None
    
    def _fetch_akshare(self, code: str) -> Optional[pd.DataFrame]:
        import akshare as ak
        return ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20200101")
    
    def _fetch_tushare(self, code: str) -> Optional[pd.DataFrame]:
        import tushare as ts
        ts.set_token(self.cfg.market.tushare_token)
        pro = ts.pro_api()
        return pro.daily(ts_code=f"{code}.SH" if code.startswith("6") else f"{code}.SZ")
    
    def _fetch_cache(self, code: str) -> Optional[pd.DataFrame]:
        return self._cache.get(code)
```

---

## 核心发现三：策略引擎的信号冲突与权重融合

### 当前策略架构

`PortfolioManager` 运行多个策略并返回所有信号：

```python
# strategy/registry.py
STRATEGY_REGISTRY = {
    "ma_trend": MATrendStrategy,
    "bollinger_revert": BollingerRevertStrategy,
    "momentum": MomentumStrategy,
}

def run_all_strategies(self, market_data, account, positions):
    signals = []
    for name, strategy_cls in STRATEGY_REGISTRY.items():
        strategy = strategy_cls(self.cfg.strategy)
        signals.extend(strategy.generate_signals(market_data, account, positions))
    return signals
```

**问题**：
1. **权重配置未使用**：`config.py` 定义了 `trend_weight=0.40, revert_weight=0.35, momentum_weight=0.25`，但 `run_all_strategies()` 未使用这些权重
2. **无信号冲突处理**：MA_Trend 发出买入，Bollinger 发出卖出，系统如何处理？
3. **无信号强度融合**：所有信号平等对待，未考虑策略置信度

### 改进方案：加权信号融合

```python
class SignalFusionEngine:
    """多策略信号加权融合"""
    
    def __init__(self, config: StrategyConfig):
        self.weights = {
            "ma_trend": config.trend_weight,
            "bollinger_revert": config.revert_weight,
            "momentum": config.momentum_weight,
        }
    
    def fuse(self, signals: list[Signal]) -> list[Signal]:
        """按股票+方向聚合，加权计算综合信号"""
        # 按 (code, direction) 分组
        groups: dict[tuple[str, Direction], list[Signal]] = defaultdict(list)
        for s in signals:
            groups[(s.code, s.direction)].append(s)
        
        fused = []
        for (code, direction), sigs in groups.items():
            # 加权平均价格
            total_weight = sum(self.weights.get(s.strategy, 0.25) for s in sigs)
            weighted_price = sum(
                s.price * self.weights.get(s.strategy, 0.25) for s in sigs
            ) / total_weight if total_weight > 0 else sigs[0].price
            
            # 加权平均强度
            weighted_strength = sum(
                s.strength * self.weights.get(s.strategy, 0.25) for s in sigs
            ) / total_weight if total_weight > 0 else sigs[0].strength
            
            # 数量：取加权平均或最大（保守）
            weighted_qty = int(sum(
                (s.quantity or 100) * self.weights.get(s.strategy, 0.25) for s in sigs
            ) / total_weight / 100) * 100 if total_weight > 0 else sigs[0].quantity
            
            fused.append(Signal(
                code=code,
                direction=direction,
                price=weighted_price,
                quantity=weighted_qty,
                strength=weighted_strength,
                strategy="fused",
                source_strategies=[s.strategy for s in sigs],
            ))
        
        # 冲突检测：同一股票同时有买入和卖出信号
        buy_codes = {s.code for s in fused if s.is_buy}
        sell_codes = {s.code for s in fused if not s.is_buy}
        conflicts = buy_codes & sell_codes
        
        for code in conflicts:
            buy_signal = next(s for s in fused if s.code == code and s.is_buy)
            sell_signal = next(s for s in fused if s.code == code and not s.is_buy)
            
            # 策略：保留强度高的信号
            if buy_signal.strength > sell_signal.strength:
                fused.remove(sell_signal)
                logger.info(f"[冲突] {code}: 保留买入 (强度 {buy_signal.strength:.2f} > {sell_signal.strength:.2f})")
            else:
                fused.remove(buy_signal)
                logger.info(f"[冲突] {code}: 保留卖出 (强度 {sell_signal.strength:.2f} >= {buy_signal.strength:.2f})")
        
        return fused
```

---

## 核心发现四：状态持久化与断点恢复机制

### 当前状态管理

系统**没有持久化任何运行时状态**：
- `TradingEngine._running` 仅内存变量
- `RiskManager._daily_trades`、`_daily_loss_pct` 仅内存变量
- `PortfolioManager` 的策略状态仅内存变量

**后果**：系统崩溃或重启后，所有状态丢失：
1. 当日交易次数重置 → 可能突破 `max_daily_trades` 限制
2. 当日盈亏重置 → 风控无法正确判断是否触发熔断
3. 策略连亏计数重置 → 连亏暂停机制失效

### 改进方案：状态持久化层

```python
from pathlib import Path
import json
from datetime import datetime

class StatePersistence:
    """运行时状态持久化：JSONL 追加写入"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_risk_state(self, risk_manager: RiskManager):
        """保存风控状态"""
        record = {
            "type": "risk_state",
            "timestamp": datetime.now().isoformat(),
            "daily_trades": risk_manager._daily_trades,
            "daily_loss_pct": risk_manager._daily_loss_pct,
            "is_locked": risk_manager._is_locked,
            "lock_reason": risk_manager._lock_reason,
            "strategy_losses": risk_manager._strategy_losses,
        }
        self._append(record)
    
    def save_order_state(self, order_id: str, signal: Signal, status: str):
        """保存订单状态"""
        record = {
            "type": "order",
            "timestamp": datetime.now().isoformat(),
            "order_id": order_id,
            "code": signal.code,
            "direction": signal.direction.value,
            "price": signal.price,
            "quantity": signal.quantity,
            "strategy": signal.strategy,
            "status": status,  # submitted | filled | rejected | cancelled
        }
        self._append(record)
    
    def _append(self, record: dict):
        with open(self.db_path, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def restore_risk_state(self) -> dict:
        """从最新记录恢复风控状态"""
        if not self.db_path.exists():
            return {}
        
        # 读取最后 100 条记录
        records = []
        with open(self.db_path) as f:
            for line in f:
                records.append(json.loads(line.strip()))
        
        # 找到最新的 risk_state
        for r in reversed(records):
            if r.get("type") == "risk_state":
                return r
        
        return {}
    
    def get_today_orders(self, date_str: str) -> list[dict]:
        """获取今日所有订单"""
        orders = []
        if not self.db_path.exists():
            return orders
        
        with open(self.db_path) as f:
            for line in f:
                r = json.loads(line.strip())
                if r.get("type") == "order" and r.get("timestamp", "").startswith(date_str):
                    orders.append(r)
        
        return orders
```

**恢复逻辑**：

```python
async def start(self):
    # 恢复昨日状态
    persistence = StatePersistence(self.cfg.storage.db_path)
    risk_state = persistence.restore_risk_state()
    
    if risk_state:
        self.risk_manager._daily_trades = risk_state.get("daily_trades", 0)
        self.risk_manager._daily_loss_pct = risk_state.get("daily_loss_pct", 0.0)
        self.risk_manager._is_locked = risk_state.get("is_locked", False)
        self.risk_manager._lock_reason = risk_state.get("lock_reason", "")
        self.risk_manager._strategy_losses = risk_state.get("strategy_losses", {})
        
        # 如果系统处于锁定状态，需要人工解锁
        if self.risk_manager._is_locked:
            logger.warning(f"⚠️ 系统处于锁定状态: {self.risk_manager._lock_reason}")
            logger.warning("请确认安全后调用 unlock() 解锁")
    
    # ... 继续启动
```

---

## 核心发现五：通知系统的可靠性与告警疲劳

### 当前通知架构

```python
class Notifier:
    def __init__(self):
        self.channels: list[NotifierChannel] = []
    
    def add_channel(self, channel: NotifierChannel):
        self.channels.append(channel)
    
    async def send(self, notification: Notification):
        for channel in self.channels:
            try:
                await channel.send(notification)
            except Exception as e:
                logger.error(f"通知渠道 {channel.__class__.__name__} 发送失败: {e}")
```

**问题**：
1. **无通知去重**：5 秒内可能发送多个相同股票的通知
2. **无频率限制**：高频交易场景下通知风暴
3. **无优先级路由**：错误通知和交易通知同等对待
4. **无发送确认**：不知道通知是否真正送达

### 改进方案：通知管理器

```python
from collections import deque
import time

class NotificationManager:
    """通知管理器：去重 + 限流 + 优先级路由"""
    
    def __init__(self, config: NotificationConfig):
        self.channels: list[NotifierChannel] = []
        self.config = config
        self._recent_notifications: deque = deque(maxlen=100)  # 最近 100 条
        self._rate_limit: dict[str, float] = {}  # channel -> last_send_time
        self._rate_limit_interval = 5.0  # 同渠道 5 秒内不重复发送
    
    async def send(self, notification: Notification):
        # 1. 去重检查
        if self._is_duplicate(notification):
            logger.debug(f"[通知去重] {notification.title}")
            return
        
        # 2. 频率限制
        if self._is_rate_limited(notification.level):
            logger.debug(f"[通知限流] {notification.title} (level={notification.level})")
            return
        
        # 3. 优先级路由
        if notification.level == "critical":
            # 紧急通知：所有渠道 + 不限流
            await self._send_to_all(notification, skip_rate_limit=True)
        elif notification.level == "trade":
            # 交易通知：仅通知配置中允许的交易通知
            if "trade_filled" in self.config.notify_on:
                await self._send_to_all(notification)
        elif notification.level == "error":
            # 错误通知：所有渠道
            await self._send_to_all(notification)
        
        # 4. 记录发送
        self._record_send(notification)
    
    def _is_duplicate(self, notification: Notification) -> bool:
        """检查是否重复（同标题 + 同内容摘要）"""
        key = (notification.title, notification.body[:50])
        return key in self._recent_notifications
    
    def _is_rate_limited(self, level: str) -> bool:
        """检查频率限制"""
        if level == "critical":
            return False  # 紧急通知不限流
        
        now = time.time()
        for channel in self.channels:
            last = self._rate_limit.get(channel.__class__.__name__, 0)
            if now - last < self._rate_limit_interval:
                return True
        return False
    
    async def _send_to_all(self, notification: Notification, skip_rate_limit=False):
        for channel in self.channels:
            if not skip_rate_limit:
                self._rate_limit[channel.__class__.__name__] = time.time()
            try:
                await channel.send(notification)
            except Exception as e:
                logger.error(f"通知发送失败 [{channel.__class__.__name__}]: {e}")
    
    def _record_send(self, notification: Notification):
        self._recent_notifications.append((notification.title, notification.body[:50]))
```

---

## 实践启发

### 1. 系统级容错比适配层更重要

xdotool 适配层的不稳定性可以通过窗口守卫、操作验证、熔断器来缓解。但**交易引擎的竞态条件、数据源降级、信号冲突、状态恢复**等问题影响范围更广，需要架构级设计。

### 2. 状态持久化是底线

任何自动化交易系统必须持久化：
- 当日交易次数（防止突破日交易上限）
- 当日盈亏（防止突破日亏损熔断）
- 订单状态（防止重复下单）
- 策略连亏计数（防止连亏暂停失效）

### 3. 信号聚合是必须的

多策略系统必须有信号聚合层，处理：
- 同方向同标的信号合并（加权）
- 相反方向信号冲突（保留强度高者）
- 信号强度融合（置信度加权）

### 4. 通知系统需要智能调度

- 去重：同股票同方向不重复通知
- 限流：同渠道 5 秒内不重复发送
- 优先级：critical 级通知所有渠道 + 不限流
- 确认：记录发送状态，失败时重试

---

## 知识缺口

| 缺口 | 说明 | 优先级 | 补充方式 |
|------|------|--------|---------|
| 同花顺 WebSocket 行情 | 是否有官方 WebSocket 行情接口？可替代 akshare 爬虫 | 🔴 高 | 同花顺 API 文档调研 |
| 策略回测框架 | 是否有回测引擎验证策略有效性？ | 🟡 中 | `backtest/engine.py` 源码分析 |
| 数据库 schema | `ths_trader.db` 的表结构是什么？ | 🟡 中 | `storage/database.py` 源码分析 |
| 日志轮转策略 | 50MB 日志轮转是否足够？ | 🟢 低 | 实测验证 |
| 多账户支持 | 是否支持多账户并行交易？ | 🟡 中 | 架构扩展性分析 |
| 撤单功能实现 | `cancel()` 方法仅返回 True，未实际实现 | 🔴 高 | 校准撤单界面坐标 |
| 持仓查询实现 | `get_position()` 未实现，返回空列表 | 🔴 高 | OCR 读取持仓表格 |

---

## 相关笔记

- [同花顺 xdotool 自动化下单：技术全景与三层容错架构](./2026-05-16-ths-auto-trader-xdotool-stability.md)
- [同花顺 xdotool 自动化下单：稳定性与容错（源码级分析）](./2026-05-16-ths-xdotool-stability-fault-tolerance.md)
- [同花顺 xdotool 自动化下单：稳定性与容错架构深度研究](./2026-05-16-ths-xdotool-stability-deep-dive.md)
- [TradingAgents 深度分析](../2026-05-05-tradingagents-deep-analysis.md)

---

## 项目源码索引

| 文件 | 行数 | 核心内容 |
|------|------|---------|
| `trading_engine.py` | 256 | 交易引擎主循环 + 信号处理 |
| `risk/risk_manager.py` | 134 | 五层风控引擎 |
| `core/config.py` | 210 | Pydantic 配置模型 + 环境变量覆盖 |
| `execution/xdotool_broker.py` | 309 | xdotool 交易适配器 |
| `execution/broker.py` | 214 | Broker 抽象基类 + 工厂模式 |
| `market/data_source.py` | - | 行情数据源（需进一步分析） |
| `strategy/registry.py` | - | 策略注册表（需进一步分析） |
| `storage/database.py` | - | 数据库管理（需进一步分析） |
