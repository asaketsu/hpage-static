# 同花顺 xdotool 自动化下单：稳定性与容错架构深度研究（源码级分析）

> **主题**: ths-auto-trader — 基于 xdotool 的 GUI 自动化交易容错  
> **日期**: 2026-05-16  
> **类型**: 本地知识蒸馏（源码精读 + 深度分析）  
> **字数**: ~3500 字  
> **素材来源**: `~/uclaw/project/ths-auto-trader/` 项目源码

---

## 摘要

本文基于 ths-auto-trader 项目实际源码，深度分析 xdotool 自动化下单方案的**稳定性瓶颈**与**容错架构设计**。项目已实现完整的多层 Broker 抽象（xdotool/easytrader/paper）、五层风控引擎、异常体系，但在 xdotool 适配层仍存在关键的可靠性短板：**无操作确认闭环**、**窗口状态感知缺失**、**坐标硬编码的脆弱性**。本文从源码出发，逐一拆解这些问题并提出工业级改造方案。

---

## 核心发现

### 发现一：xdotool_broker.py 的「开环执行」问题 — 操作无确认即视为成功

**问题定位**：`XdotoolBroker.buy()` 方法（源码第 247-258 行）的核心流程为：

```python
def buy(self, code: str, price: float, quantity: int) -> str:
    if not self._connected:
        self.connect()
    try:
        self.open_buy_window()
        order_id = self._fill_order(code, price, quantity, "buy")
        logger.info(f"BUY submitted: {code} x{quantity} @ {price}, order={order_id}")
        return order_id
    except Exception as e:
        raise XdotoolError(f"买入失败: {e}")
```

**关键缺陷**：`_fill_order` 执行完 `click_at` 后直接返回一个虚构的 `order_id`（`ORDER-{code}-{price}-{amount}`），**从未验证同花顺是否真正接收到了这笔委托**。这是一个典型的「开环控制」问题：

1. **模拟点击 ≠ 实际生效**：xdotool 的 `click` 命令返回 0 仅表示"成功发送了点击事件"，不代表目标应用处理了该事件
2. **弹窗阻断**：同花顺可能在点击后弹出验证码、资金不足提示、涨跌停提示等，xdotool 无法感知
3. **窗口焦点丢失**：如果在执行过程中用户切换了窗口，后续所有操作都发到了错误窗口
4. **网络延迟**：同花顺的网络请求可能超时，但代码已返回"成功"

**工业级改造方案**：引入「操作确认闭环」，每次关键操作后必须验证结果：

```python
def buy_with_confirm(self, code: str, price: float, quantity: int) -> str:
    """带确认的买入：执行 → 截图 → OCR验证 → 返回真实委托号"""
    if not self._connected:
        self.connect()
    
    # 1. 执行买入操作
    self.open_buy_window()
    self._fill_order(code, price, quantity, "buy")
    
    # 2. 等待确认弹窗（最多 3 秒）
    time.sleep(1.5)
    
    # 3. 截图 + OCR 验证
    confirm_region = self._get_confirm_region()
    screenshot = self._capture_region(confirm_region)
    ocr_text = pytesseract.image_to_string(screenshot, lang='chi_sim')
    
    # 4. 匹配确认模式
    if "委托已报" in ocr_text or "成功" in ocr_text:
        # 尝试提取委托编号
        order_no = re.search(r'委托号[：:]\s*(\d+)', ocr_text)
        if order_no:
            return order_no.group(1)
        return f"CONFIRMED-{code}-{int(time.time())}"
    
    # 5. 检查错误弹窗
    if "资金不足" in ocr_text:
        raise OrderRejected("资金不足")
    if "涨停" in ocr_text:
        raise OrderRejected("涨停板无法买入")
    
    # 6. 未知状态 → 安全失败
    raise OrderTimeout(f"无法确认委托状态，OCR文本: {ocr_text[:100]}")
```

这个改造的关键点在于：**宁可超时失败，不可误报成功**。在金融交易中，假阳性（报告成功但实际未成交）比假阴性（报告失败但实际已成交）危险得多——后者最多错过一次机会，前者可能导致重复下单。

---

### 发现二：窗口定位的三级降级策略 — 从源码看实际实现

**源码分析**：`XdotoolClient.find_window()` 方法（第 59-92 行）实现了三级窗口查找：

```python
def find_window(self) -> int:
    # Level 1: 按窗口名称搜索
    result = subprocess.run(["xdotool", "search", "--name", window_name], ...)
    if result.returncode == 0 and result.stdout.strip():
        return int(result.stdout.strip().split()[0])
    
    # Level 2: 按窗口类名搜索
    result = subprocess.run(["xdotool", "search", "--class", window_class], ...)
    
    # Level 3: 备选 — 搜索 Chromium（同花顺基于 CEF）
    if result.returncode != 0 or not result.stdout.strip():
        result = subprocess.run(["xdotool", "search", "--class", "Chromium"], ...)
    
    if result.returncode != 0 or not result.stdout.strip():
        raise XdotoolError("未找到同花顺窗口")
```

**设计分析**：

| 层级 | 搜索策略 | 稳定性 | 适用场景 |
|------|---------|--------|---------|
| L1: 窗口名称 | `--name "同花顺"` | 🟡 中 | 窗口标题可能包含股票名称，如"同花顺 - 600000" |
| L2: 窗口类名 | `--class "ThsClient"` | 🟢 高 | 类名通常不会随版本变化，但需确认实际值 |
| L3: Chromium 回退 | `--class "Chromium"` | 🔴 低 | 可能匹配到浏览器窗口，产生误操作风险 |

**关键风险**：Level 3 的 Chromium 回退极其危险。如果用户同时打开了 Chrome/Chromium 浏览器，xdotool 可能操作到浏览器窗口而非同花顺，导致**在错误的窗口中输入股票代码甚至执行交易操作**。

**改进建议**：

```python
def find_window_safe(self) -> int:
    """安全窗口查找：多策略 + 严格验证"""
    candidates = []
    
    # 收集所有可能的窗口
    for strategy, arg in [
        ("--name", self.cfg.broker.window_name),
        ("--class", self.cfg.broker.window_class),
    ]:
        result = subprocess.run(
            ["xdotool", "search", strategy, arg],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for wid in result.stdout.strip().split('\n'):
                if wid.strip():
                    candidates.append(int(wid.strip()))
    
    # 对候选窗口进行验证
    for wid in candidates:
        # 检查窗口是否可见且尺寸合理（排除最小化/系统托盘）
        try:
            geom = subprocess.run(
                ["xdotool", "getwindowgeometry", str(wid)],
                capture_output=True, text=True, timeout=2
            )
            if geom.returncode == 0:
                # 解析尺寸，排除过小窗口
                geom_match = re.search(r'Geometry:\s*(\d+)x(\d+)', geom.stdout)
                if geom_match:
                    w, h = int(geom_match.group(1)), int(geom_match.group(2))
                    if w >= 800 and h >= 600:  # 同花顺窗口通常 >= 800x600
                        return wid
        except Exception:
            continue
    
    raise XdotoolError("未找到有效的同花顺窗口")
```

**核心改进**：不再盲目使用 Chromium 回退，而是对候选窗口进行**尺寸验证**，确保操作的是一个正常大小的应用窗口。

---

### 发现三：坐标系统的脆弱性与自适应校准

**源码现状**：坐标通过 `config.yaml` 配置，支持相对坐标偏移：

```python
# 已校准坐标（2026-05-15 实测验证）：
# - 搜索框: (200, 65)
# - 股票代码输入框: (200, 100)
# - 买入按钮: (757, 753)
# - 确认按钮: (665, 283)
```

```python
def _abs_coords(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
    """相对坐标转绝对坐标"""
    return (self._window_x + rel_x, self._window_y + rel_y)
```

**脆弱性分析**：

1. **单点校准**：坐标仅在特定日期（2026-05-15）校准一次，窗口大小变化后全部失效
2. **无缩放适配**：同花顺窗口大小改变（如全屏/半屏切换）后，按钮位置按比例变化，但坐标不会自适应
3. **DPI 缩放问题**：Linux 高分辨率屏幕（如 Jetson 连接 4K 显示器）的 DPI 缩放会导致坐标偏移

**自适应方案**：基于窗口几何的比例映射：

```python
class AdaptiveCoords:
    """自适应坐标系统：基于窗口实际尺寸动态计算"""
    
    def __init__(self):
        # 校准基准（在哪个窗口尺寸下校准的）
        self.base_width = 1261  # 校准时的窗口宽度
        self.base_height = 1000  # 校准时的窗口高度
        
        # 元素相对位置（占窗口尺寸的比例）
        self.elements = {
            "input_code":   (0.159, 0.100),   # 200/1261, 100/1000
            "input_price":  (0.159, 0.120),   # 200/1261, 120/1000
            "input_amount": (0.159, 0.200),   # 200/1261, 200/1000
            "btn_buy":      (0.601, 0.753),   # 757/1261, 753/1000
            "btn_confirm":  (0.527, 0.283),   # 665/1261, 283/1000
        }
    
    def get_coords(self, element: str, win_width: int, win_height: int) -> Tuple[int, int]:
        """根据当前窗口尺寸计算实际坐标"""
        ratio_x, ratio_y = self.elements[element]
        return (int(ratio_x * win_width), int(ratio_y * win_height))
```

这个方案的前提假设是同花顺的 UI 布局是**等比例缩放**的。实际测试中，CEF 渲染的界面通常是等比缩放，因此比例映射在大多数场景下有效。但仍需加入**边界检查**：计算出的坐标不应超出窗口范围。

---

### 发现四：异常体系的专业设计 — 从源码 exceptions.py 看

项目实现了分层的异常体系（86 行），这在金融系统中非常重要：

```
THSTraderError (基类)
├── RiskError (风控拦截)
│   ├── DailyLossLimitExceeded   — 单日亏损超限
│   ├── PositionLimitExceeded    — 仓位超限
│   ├── StopLossTriggered        — 触发止损
│   ├── CircuitBreakerTripped    — 熔断触发
│   ├── BlacklistStock           — 黑名单
│   ├── PriceDeviationError      — 价格偏离
│   └── TradeLimitExceeded       — 交易次数超限
├── BrokerError (交易通道)
│   └── BrokerConnectionError    — 连接失败
├── OrderError (委托)
│   ├── OrderTimeout             — 超时
│   └── OrderRejected            — 被拒
├── MarketDataError (行情)
│   └── DataAbnormal             — 数据异常
└── SystemError (系统)
    ├── ConfigError               — 配置错误
    ├── AuthenticationError       — 认证失败
    └── SystemLocked              — 系统锁定
```

**设计亮点**：
- **风控异常优先级最高**：`RiskError` 子类最丰富，覆盖了 7 种风控场景
- **可区分恢复策略**：`OrderTimeout` 可重试，`OrderRejected` 不可重试，`CircuitBreakerTripped` 需人工介入
- **缺失**：没有 `WindowLostError`（窗口消失）、`CoordinateDriftError`（坐标偏移）等 xdotool 特有异常

**建议补充**：

```python
class XdotoolStabilityError(THSTraderError):
    """xdotool 稳定性错误（基类）"""
    pass

class WindowNotFoundError(XdotoolStabilityError):
    """同花顺窗口未找到或已关闭"""
    pass

class WindowGeometryChanged(XdotoolStabilityError):
    """窗口尺寸发生变化，坐标可能失效"""
    pass

class OperationUnconfirmed(XdotoolStabilityError):
    """操作执行后无法确认结果"""
    pass

class PopupDetected(XdotoolStabilityError):
    """检测到弹窗（验证码/提示/错误）"""
    pass
```

---

### 发现五：Broker 抽象层的设计 — 多通道切换

`broker.py` 实现了工厂模式的 Broker 抽象：

```python
def create_broker() -> Broker:
    if cfg.broker.type == "xdotool":
        return XdotoolBroker()
    elif cfg.broker.type == "easytrader":
        return EasyTraderBroker()
    elif cfg.broker.type == "paper":
        return PaperBroker()
```

**架构分析**：

| 通道 | 稳定性 | 延迟 | 依赖 | 适用场景 |
|------|--------|------|------|---------|
| `xdotool` | 🔴 低 | 50-200ms | X11 + 坐标校准 | Linux 开发/测试 |
| `easytrader` | 🟡 中 | 30-100ms | Windows + Python | Windows 生产环境 |
| `paper` | 🟢 高 | <1ms | 无 | 策略回测/模拟交易 |

**关键洞察**：xdotool 方案本质上是一种**妥协**——在 Linux 环境下无法使用 Windows 专有的 easytrader，只能通过 GUI 模拟实现。正确的架构决策是：**xdotool 仅用于验证和测试，生产环境切换到 easytrader（Windows）或券商直连 API**。

---

## 实践启发

### 1. xdotool 自动化的「三不原则」

基于源码分析，xdotool 自动化交易应遵循：
- **不信任**：每次操作后必须验证（截图 + OCR），不能假设成功
- **不重试**：失败后先查询状态，确认未生效再重试，避免重复下单
- **不无人值守**：xdotool 方案需要人在旁边监控，特别是处理弹窗和异常

### 2. 坐标管理是最大维护成本

从源码注释可以看到坐标是在 2026-05-15 校准的，这意味着：
- 同花顺每次更新 UI 都需要重新校准
- 窗口大小变化需要重新校准
- 建议实现自动化校准脚本（通过截图 + 模板匹配定位按钮）

### 3. 风控是安全底线

项目的五层风控引擎设计优秀：
- L1: 单票仓位限制
- L2: 价格偏离检查
- L3: 总仓位限制
- L4: 策略连亏暂停
- L5: 账户级熔断

xdotool 的不稳定性加上健全的风控，可以构成一个**容错边界**：即使自动化操作失败，风控系统也能防止灾难性损失。

### 4. Paper Trading 先行

项目已实现 `PaperBroker`，这是正确的开发路径：先用 Paper Trading 验证策略，再用 xdotool 在小资金上测试，最后才考虑切换到生产通道。

---

## 知识缺口

| 缺口 | 说明 | 优先级 | 补充方式 |
|------|------|--------|---------|
| OCR 确认模块 | 项目中尚未实现操作结果截图验证 | 🔴 高 | 集成 Tesseract/OpenCV |
| 弹窗检测 | 验证码/资金不足等弹窗的自动识别 | 🔴 高 | 截图 + 模板匹配 |
| 坐标自校准 | 按钮位置随 UI 版本自动适应 | 🟡 中 | OpenCV 模板匹配 |
| xdotool 延迟优化 | 当前固定 delay=0.2s，可动态调整 | 🟡 中 | 根据操作类型自适应 |
| 撤单功能 | `cancel()` 方法当前返回 True 但未实现 | 🔴 高 | 校准撤单界面坐标 |
| 持仓/账户查询 | `get_position()`/`get_account()` 未实现 | 🟡 中 | OCR 读取持仓表格 |
| 窗口重连 | 窗口关闭后自动重启同花顺并重连 | 🟡 中 | 进程管理 + 自动登录 |
| 多显示器支持 | 当前假设单显示器场景 | 🟢 低 | `--screen` 参数适配 |

---

## 相关笔记

- [同花顺自动交易系统技术全景](./2026-05-16-ths-auto-trader-xdotool-stability.md) — 前篇，覆盖技术全景与三层容错架构
- [TradingAgents 深度分析](../2026-05-05-tradingagents-deep-analysis.md) — 多 Agent 交易系统架构
- [RSI+布林带策略](./2026-05-06-rsi-bollinger-strategy.md) — 策略引擎参考
- [AI投资8层框架](../2026-05-04-AI投资8层框架v3.1深度解析.md) — 投资决策框架

---

## 项目源码索引

| 文件 | 行数 | 核心内容 |
|------|------|---------|
| `execution/xdotool_broker.py` | 309 | xdotool 客户端封装 + 交易适配器 |
| `execution/broker.py` | 214 | Broker 抽象基类 + 工厂模式 |
| `core/exceptions.py` | 86 | 分层异常体系（7 种风控异常） |
| `core/models.py` | 172 | 数据模型（Signal/Order/Position/Account） |
| `core/config.py` | 210 | 配置管理（含坐标配置） |
| `core/events.py` | 107 | 事件系统 |
| `risk/risk_manager.py` | 134 | 五层风控引擎 |
