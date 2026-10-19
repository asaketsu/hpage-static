# 同花顺 xdotool 自动化下单的稳定性与容错

> **摘要**：基于 ths-auto-trader 项目源码的本地知识蒸馏，深度分析 xdotool GUI 自动化交易系统在 Linux 环境下面临的稳定性挑战、现有容错机制的不足，以及可落地的改进方案。本文覆盖窗口定位、坐标漂移、操作原子性、异常恢复、风控熔断五个核心维度。

---

## 核心发现一：窗口定位的三级降级策略及其脆弱性

当前 `XdotoolClient.find_window()` 实现了三级降级查找：

```python
# 第1级：按窗口名称搜索
xdotool search --name "同花顺"
# 第2级：按窗口类搜索
xdotool search --class "HevoNext.B2CApp"
# 第3级：搜索 Chromium（同花顺基于 CEF）
xdotool search --class "Chromium"
```

**问题分析**：

1. **同花顺窗口标题是动态的**。实测发现同花顺 Linux 版（基于 CEF/HevoNext.B2CApp）的窗口标题随股票代码切换而变化，如 `"同花顺 - 600519"` 或 `"同花顺(2026版)"`，导致 `--name` 精确匹配不稳定。
2. **Chromium 备选误伤风险高**。如果用户同时开了 Chrome 浏览器，`--class Chromium` 可能返回浏览器窗口而非同花顺。
3. **无窗口唯一性验证**。`find_window()` 返回第一个匹配，但如果存在多个同名窗口（如多开），可能操作错误窗口。

**改进方向**：

- 用 `--name` 模糊匹配：`xdotool search --name "同花顺"` 实际支持部分匹配（包含即可），比精确匹配更健壮。
- 增加 PID 验证：通过 `xdotool getwindowpid` 确认窗口属于同花顺进程。
- 多窗口时按 `--onlyvisible --screen 0` 过滤活跃窗口。
- 增加窗口标题快照验证：找到窗口后截图或获取标题确认是同花顺交易界面。

```python
def find_window_robust(self) -> int:
    """健壮的窗口查找：名称→类→PID→标题验证"""
    candidates = []
    
    # 级别1: 名称模糊匹配
    for pattern in ["同花顺", "10jqka", "HevoNext"]:
        result = subprocess.run(
            ["xdotool", "search", "--name", pattern],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            candidates.extend(result.stdout.strip().split())
    
    # 去重 + 验证
    seen = set()
    for wid in candidates:
        if wid in seen:
            continue
        seen.add(wid)
        # 验证窗口标题包含同花顺关键词
        title = subprocess.run(
            ["xdotool", "getwindowname", wid],
            capture_output=True, text=True, timeout=3
        )
        if "同花顺" in title.stdout or "10jqka" in title.stdout:
            self.window_id = int(wid)
            return self.window_id
    
    raise XdotoolError("未找到同花顺窗口")
```

---

## 核心发现二：坐标漂移是最大的稳定性杀手

`XdotoolBroker` 的核心操作完全依赖**预校准的相对坐标**：

```yaml
# config.yaml
coords:
  search_box: [200, 65]
  input_code: [200, 100]
  input_price: [200, 120]
  input_amount: [200, 200]
  btn_buy: [757, 753]
  btn_confirm: [665, 283]
```

坐标校准通过 `scripts/calibrate.py` 交互式完成——手动移动鼠标到每个控件位置按 Enter 记录。这种方式有致命缺陷：

1. **窗口缩放敏感**。同花顺窗口大小变化时，所有坐标失效。系统没有窗口尺寸断言。
2. **分辨率依赖**。在不同分辨率显示器间切换时坐标全部偏移。
3. **无运行时校验**。代码在操作前不检查窗口几何是否与校准时一致。
4. **点击精度问题**。`xdotool mousemove` 默认跳转到像素中心，但 CEF 渲染的 HTML 控件有 padding/margin，可能点到控件边缘外。

**改进方案：窗口尺寸守卫 + 自适应坐标**

```python
class XdotoolBroker:
    def __init__(self):
        self._calibrated_size = None  # 校准时的窗口尺寸 (w, h)
        self._scale_x = 1.0
        self._scale_y = 1.0
    
    def connect(self):
        # ... 原有连接逻辑 ...
        _, _, w, h = self.xdotool.get_window_geometry()
        self._calibrated_size = (w, h)
        
        # 如果窗口尺寸与校准时不同，按比例缩放坐标
        cfg_w = self.cfg.broker.get("calibrated_width", w)
        cfg_h = self.cfg.broker.get("calibrated_height", h)
        self._scale_x = w / cfg_w
        self._scale_y = h / cfg_h
    
    def _scaled_coord(self, key: str) -> Tuple[int, int]:
        """根据窗口尺寸缩放坐标"""
        x, y = self._get_coord(key)
        return (int(x * self._scale_x), int(y * self._scale_y))
    
    def _abs_coords(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        """相对坐标转绝对坐标（含缩放）"""
        scaled_x = int(rel_x * self._scale_x)
        scaled_y = int(rel_y * self._scale_y)
        return (self._window_x + scaled_x, self._window_y + scaled_y)
```

更根本的方案是**图像识别辅助定位**：用 `xdotool screenshot` 截取窗口区域，通过 OpenCV 模板匹配或 OCR 定位输入框和按钮，彻底消除坐标依赖。

---

## 核心发现三：操作缺乏原子性和回滚机制

当前的下单流程 `_fill_order()` 是一个线性序列：

```python
def _fill_order(self, code, price, amount, side):
    # 1. 点击代码输入框 → 清空 → 输入代码
    # 2. 点击价格输入框 → 清空 → 输入价格
    # 3. 点击数量输入框 → 清空 → 输入数量
    # 4. 点击买入/卖出按钮
    return f"ORDER-{code}-{price}-{amount}"
```

**核心问题**：

1. **无操作确认**。输入代码后没有验证输入框确实显示了正确的代码。xdotool `type` 命令可能在焦点不在输入框时丢失字符。
2. **无超时控制**。`click_at` 和 `type_text` 的 `subprocess.run` 有 timeout，但整个 `_fill_order` 流程没有总超时。如果中间某步卡住，系统会无限等待。
3. **无回滚**。如果步骤3（输入数量）失败，前面的代码和价格已经填了，但无法撤销。更危险的是，如果步骤2失败后重试，可能意外填入了错误的价格。
4. **清空操作不可靠**。`clear_input()` 用 `Ctrl+A → Delete`，但如果输入框已有选中状态或焦点不对，可能无法清空，导致新输入拼接到旧内容后面。

**改进方案：操作确认 + 原子事务**

```python
class OrderTransaction:
    """订单填写事务 — 要么全部完成，要么全部回滚"""
    
    def __init__(self, broker: XdotoolBroker):
        self.broker = broker
        self.steps_completed = []
    
    def execute(self, code, price, amount, side):
        try:
            # Step 1: 填写代码 + 验证
            self._fill_and_verify("input_code", code, "code")
            self.steps_completed.append("code")
            
            # Step 2: 填写价格 + 验证
            self._fill_and_verify("input_price", f"{price:.2f}", "price")
            self.steps_completed.append("price")
            
            # Step 3: 填写数量 + 验证
            self._fill_and_verify("input_amount", str(amount), "amount")
            self.steps_completed.append("amount")
            
            # Step 4: 确认按钮
            self.broker.xdotool.click_at(...)
            
        except Exception:
            self._rollback()
            raise
    
    def _fill_and_verify(self, coord_key, expected, field_name):
        """填写输入框并验证（通过截图OCR）"""
        for attempt in range(3):
            self.broker.xdotool.click_at(...)
            self.broker.xdotool.clear_input()
            time.sleep(0.2)
            self.broker.xdotool.type_text(expected)
            time.sleep(0.3)
            
            # 验证：截图 → OCR → 比对
            actual = self._read_field_via_ocr(coord_key)
            if actual.strip() == expected.strip():
                return
            logger.warning(f"字段 {field_name} 验证失败: "
                          f"期望 '{expected}', 实际 '{actual}' (attempt {attempt+1})")
        
        raise XdotoolError(f"字段 {field_name} 填写验证失败，3次重试后仍不正确")
    
    def _rollback(self):
        """回滚：清空所有已填写的字段"""
        for step in self.steps_completed:
            coord_key = f"input_{step}"
            self.broker.xdotool.click_at(...)
            self.broker.xdotool.clear_input()
```

---

## 核心发现四：异常处理粒度不足，缺少关键场景的恢复策略

分析异常体系（`core/exceptions.py`）和实际异常处理：

| 异常场景 | 是否覆盖 | 当前处理 | 风险等级 |
|---------|---------|---------|---------|
| 窗口消失（同花顺崩溃/关闭） | ❌ | 无处理 | 🔴 高 |
| 弹窗遮挡（升级提示、广告） | ❌ | 注释说需人工干预 | 🔴 高 |
| 网络断开（行情数据源） | ✅ | try-catch + 日志 | 🟡 中 |
| 下单超时 | ❌ | config有`order_timeout:60`但代码未使用 | 🟡 中 |
| 输入法干扰 | ❌ | 未考虑 | 🟡 中 |
| 涨跌停无法成交 | ❌ | 无价格校验 | 🟡 中 |
| 验证码/安全确认 | ❌ | 需人工干预 | 🔴 高 |
| 同花顺版本更新UI变化 | ❌ | 坐标全部失效 | 🔴 高 |

**关键缺失1：弹窗检测与处理**

```python
def detect_and_dismiss_popup(self, timeout: float = 2.0) -> bool:
    """检测并关闭意外弹窗"""
    # 1. 检查是否有新窗口出现
    result = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--class", "HevoNext.B2CApp"],
        capture_output=True, text=True, timeout=5
    )
    windows = result.stdout.strip().split()
    
    if len(windows) > 1:
        # 有新窗口，尝试按 Escape/Enter 关闭
        for wid in windows:
            if int(wid) != self.window_id:
                subprocess.run(["xdotool", "windowactivate", wid], timeout=3)
                time.sleep(0.5)
                subprocess.run(["xdotool", "key", "Escape"], timeout=3)
                time.sleep(0.5)
                return True
    return False
```

**关键缺失2：重连机制**

`TradingEngine._tick()` 在外层 try-catch 捕获所有异常，但只记录日志和发通知，没有重连逻辑：

```python
async def _tick(self):
    try:
        # ... 正常处理 ...
    except Exception as e:
        logger.error(f"Tick error: {e}", exc_info=True)
        # 缺少：自动重连 broker
        # 缺少：窗口健康检查
```

改进：

```python
async def _tick(self):
    try:
        # 0. 窗口健康检查
        if isinstance(self.broker, XdotoolBroker):
            self.broker.health_check()  # 窗口还在吗？
        # ... 正常处理 ...
    except XdotoolError as e:
        # xdotool 错误：尝试重连
        logger.warning(f"xdotool 错误，尝试重连: {e}")
        try:
            self.broker.disconnect()
            await asyncio.sleep(5)
            self.broker.connect()
            logger.info("重连成功")
        except Exception as re:
            logger.error(f"重连失败: {re}")
            # 通知人工介入
            await notifier.send(Notification(
                title="需要人工干预",
                body=f"xdotool 自动重连失败: {re}",
                level="critical"
            ))
            self._running = False  # 停止引擎，避免错误操作
    except Exception as e:
        # 其他错误：记录 + 通知
        logger.error(f"Tick error: {e}", exc_info=True)
```

---

## 核心发现五：风控熔断与交易引擎的集成缺口

风控配置非常完善（`config.yaml` 的 `risk` 部分）：

```yaml
risk:
  daily_loss_limit: 0.03      # 单日亏损 3% 暂停
  max_daily_trades: 20         # 每日最多 20 笔
  max_position_pct: 0.2        # 单股最大 20% 仓位
  max_total_pct: 0.8           # 总仓位不超过 80%
  stop_loss_pct: 0.05          # 5% 止损
  take_profit_pct: 0.1         # 10% 止盈
  price_deviation_limit: 0.02  # 价格偏离 2% 报警
  consecutive_loss_pause: 3    # 连亏 3 次暂停
  order_timeout: 60            # 委托超时 60 秒
```

异常体系也定义了 `CircuitBreakerTripped`、`SystemLocked` 等熔断异常。但在 `trading_engine.py` 中：

1. **`order_timeout: 60` 未被任何代码使用**。`xdotool_broker.py` 中的 `subprocess.run` 有各自的 timeout（5-10秒），但没有全局委托超时控制。
2. **`consecutive_loss_pause: 3` 没有实现**。异常体系中定义了但风控管理器里是否有对应逻辑需要确认。
3. **熔断后无安全恢复**。触发 `CircuitBreakerTripped` 后应进入 `SystemLocked` 状态，但当前代码没有在 `_tick()` 中检查系统锁定状态。

**改进方案：委托超时 + 熔断状态机**

```python
class CircuitBreaker:
    """熔断状态机"""
    
    def __init__(self, config):
        self.state = "closed"  # closed → open → half_open → closed
        self.failure_count = 0
        self.last_failure_time = None
        self.config = config
    
    def record_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.config.consecutive_loss_pause:
            self.state = "open"
            logger.critical(f"熔断触发！连续 {self.failure_count} 次失败")
    
    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            # 冷却期 30 分钟
            if time.time() - self.last_failure_time > 1800:
                self.state = "half_open"
                return True  # 允许一次试探
            return False
        if self.state == "half_open":
            return True  # 试探中，允许一笔
        return False
```

---

## 实践启发

### 1. xdotool 自动化的本质风险
xdotool 是"盲操作"——它不知道屏幕上实际有什么，只知道"在这里点击/输入"。这种模式在自动化测试中勉强可用，但在金融交易场景中风险极高，因为：
- **操作不可逆**：错误的买入无法自动撤销
- **状态不可观测**：无法确认操作是否真正生效
- **环境不可控**：弹窗、输入法、网络抖动随时干扰

### 2. 推荐的分层防护架构

```
Layer 4: 人工确认 — 高风险操作（首笔实盘、大额委托）需人工确认
Layer 3: 熔断器 — 连续失败自动暂停，保护账户
Layer 2: 操作验证 — 每步操作后截图OCR验证结果
Layer 1: 窗口守卫 — 操作前确认窗口存在、焦点正确、无弹窗
```

### 3. 从 xdotool 迁移的路线图
- **短期**：添加窗口守卫 + 操作验证 + 熔断器（成本约 2-3 天）
- **中期**：用图像识别（OpenCV/OCR）替代固定坐标，提升鲁棒性（1-2 周）
- **长期**：迁移到 easytrader 或券商 API 接口，彻底消除 GUI 自动化风险

---

## 知识缺口

1. **同花顺 Linux 版的窗口层级结构**：不确定是否有隐藏的子窗口/overlay 遮挡交易界面，需要用 `xwininfo -tree` 深入分析。
2. **xdotool 输入法兼容性**：未测试 fcitx/ibus 输入法活跃时 `xdotool type` 是否受干扰。理论上 `xdotool type` 绕过输入法直接发送 X11 key events，但中文输入法可能拦截。
3. **同花顺 CEF 内部 DOM 可访问性**：如果能通过 Chrome DevTools Protocol（CDP）访问同花顺的 CEF 渲染层，就可以用 CSS 选择器定位元素，比 xdotool 坐标定位可靠几个数量级。需要测试同花顺是否开启了 `--remote-debugging-port`。
4. **`easytrader` 在 Linux 上的支持状态**：当前代码有 `EasyTraderBroker` 适配器，但 easytrader 主要支持 Windows。Linux 上能否通过 Wine + easytrader 方案运行？
5. **Jetson Orin 上的 GPU 加速 OCR**：本地已有 `suruOCR` 或类似工具吗？如果有，可以利用 Jetson 的 GPU 加速实现实时的屏幕文字识别，大幅提升操作验证的可靠性。

---

## 相关笔记

- `ths-auto-trader` 项目路径: `/home/jc/uclaw/project/ths-auto-trader/`
- 配置文件: `ths_auto_trader/config.yaml`
- xdotool 适配器: `ths_auto_trader/execution/xdotool_broker.py`
- 校准工具: `scripts/calibrate.py`
- 风控配置: `config.yaml → risk` section
- 异常体系: `ths_auto_trader/core/exceptions.py`
