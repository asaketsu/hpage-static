# 同花顺 xdotool 自动化下单的稳定性与容错 — 深度分析

> 摘要：基于 ths-auto-trader 项目源码（xdotool_broker.py、broker.py、calibrate.py、config.yaml）及架构设计文档的本地知识蒸馏。分析 xdotool 在金融交易场景下的 5 大稳定性瓶颈、现有代码的 7 处具体缺陷，以及分阶段加固方案。核心结论：当前实现是**开环控制**——模拟点击后无法验证委托是否真正生效，这在金融场景中不可接受。

---

## 核心发现

### 发现 1：开环执行 — 最致命的架构缺陷

`XdotoolBroker.buy()` / `sell()` 调用 `_fill_order()` 后直接返回一个虚构的 order_id：

```python
# xdotool_broker.py:215-245
def _fill_order(self, code, price, amount, side):
    # ... 模拟点击输入 ...
    return f"ORDER-{code}-{price}-{amount}"  # 虚构 ID，从未验证
```

**问题链条**：
1. `xdotool type` 发送了键击事件 → 不保证目标窗口收到
2. `xdotool click` 发送了点击事件 → 不保证按钮被点击
3. 即使按钮被点击 → 不保证同花顺处理了委托
4. 即使同花顺处理了 → 不保证委托成功（可能被拒：涨跌停/资金不足/权限）
5. 返回的 `ORDER-000001-10.50-100` 是纯字符串拼接，**与同花顺内部的委托编号完全无关**

**对比 EasyTraderBroker**（Windows 版）：
```python
# broker.py:81-84 — easytrader 返回真实 entrust_no
result = self._trader.buy(code, price=price, amount=quantity)
order_id = str(result.get("entrust_no", ""))  # 真实委托编号
```

**金融安全铁律**：假阳性比假阴性危险 100 倍。报告成功但未成交 → 策略认为已持仓 → 重复下单 → 双倍风险敞口。正确做法是**宁可超时失败，不可误报成功**。

**修复方案 — 三级验证**：
```python
class VerifiedXdotoolBroker(XdotoolBroker):
    def _verify_order_submitted(self, expected_code: str, timeout: int = 10) -> str:
        """截图 + OCR 验证委托已提交"""
        for attempt in range(3):
            # 1. 截图委托确认区域
            screenshot = self._capture_region("order_confirm")
            # 2. OCR 提取委托编号
            text = ocr_extract(screenshot)
            entrust_no = re.search(r'委托编号[：:]\s*(\d+)', text)
            if entrust_no:
                return entrust_no.group(1)
            # 3. 检查错误提示（资金不足/涨跌停等）
            error = self._detect_error_popup(screenshot)
            if error:
                raise OrderRejectedError(error)
            time.sleep(3)
        raise OrderTimeoutError(f"委托验证超时: {expected_code}")
```

### 发现 2：坐标漂移 — 窗口尺寸变化导致全部操作失效

当前坐标系统是**固定像素值**，校准于 2026-05-15：

```yaml
# config.yaml — 固定坐标
broker:
  coords:
    input_code: [200, 100]    # 股票代码输入框
    input_price: [200, 120]   # 价格输入框
    input_amount: [200, 200]  # 数量输入框
    btn_buy: [757, 753]       # 买入按钮
```

校准时的窗口尺寸是 1261×1000（见 `get_window_geometry` 的注释）。**任何导致窗口尺寸改变的操作都会使所有坐标失效**：

| 触发场景 | 概率 | 影响 |
|----------|------|------|
| 用户拖拽窗口边框调整大小 | 高 | 全部坐标偏移 |
| 分辨率/缩放比例变化 | 中 | 全部坐标按比例偏移 |
| 同花顺界面改版 | 低 | 部分坐标失效 |
| 多显示器切换 | 中 | 窗口位置重置 |
| 远程桌面(VNC)重连 | 中 | 窗口位置/尺寸可能变化 |

`connect()` 方法记录了窗口位置但**未记录窗口尺寸**，也未做尺寸校验：
```python
# xdotool_broker.py:182 — 只存了 x, y，丢弃了 w, h
self._window_x, self._window_y, _, _ = self.xdotool.get_window_geometry()
```

**修复方案 — 自适应坐标映射**：

CEF（Chromium Embedded Framework）渲染界面通常是等比缩放的，可以将固定坐标转为比例坐标：

```python
class AdaptiveCoords:
    """基于比例的自适应坐标系统"""
    # 校准基准尺寸
    BASE_WIDTH = 1261
    BASE_HEIGHT = 1000
    
    # 元素位置占窗口比例（宽%, 高%）
    ELEMENTS = {
        "input_code":   (0.159, 0.100),  # 200/1261, 100/1000
        "input_price":  (0.159, 0.120),  # 200/1261, 120/1000
        "input_amount": (0.159, 0.200),  # 200/1261, 200/1000
        "btn_buy":      (0.601, 0.753),  # 757/1261, 753/1000
        "btn_confirm":  (0.527, 0.283),  # 665/1261, 283/1000
    }
    
    def get_coords(self, element: str) -> tuple[int, int]:
        """根据当前窗口尺寸计算实际坐标"""
        _, _, w, h = self.xdotool.get_window_geometry()
        rx, ry = self.ELEMENTS[element]
        return (int(rx * w), int(ry * h))
```

**更根本的方案**：用 OpenCV 模板匹配或 OCR 替代固定坐标，直接在截图上定位按钮位置。Jetson Orin 有 GPU（67 TOPS），可以运行轻量级 CV 模型做实时元素检测。

### 发现 3：窗口定位的三级降级有误匹配风险

`find_window()` 的降级链：名称 → 类 → Chromium：

```python
# xdotool_broker.py:59-92
def find_window(self):
    # 1. 按名称 "同花顺"
    result = xdotool search --name "同花顺"
    
    # 2. 按类 "HevoNext.B2CApp"
    result = xdotool search --class "HevoNext.B2CApp"
    
    # 3. 备选：Chromium — ⚠️ 危险！
    result = xdotool search --class "Chromium"
```

**问题**：第三级搜索 `--class "Chromium"` 会匹配系统中所有 Chromium 窗口，包括：
- Chrome 浏览器（class 也包含 Chromium）
- Electron 应用（VS Code、Discord 等）
- 其他基于 CEF 的应用

在金融交易中，**向错误窗口发送键击是灾难性的** — 想象 xdotool 把股票代码和价格输入到了 VS Code 的终端里，或者更糟，输入到了另一个网页交易界面。

**修复方案 — PID 验证 + 多重校验**：
```python
def find_window_strict(self) -> int:
    """严格窗口查找：名称 + PID + 标题关键字"""
    # 1. 获取同花顺进程 PID
    ths_pid = self._get_ths_pid()  # pgrep -f HevoNext.B2CApp
    
    # 2. 搜索所有候选窗口
    candidates = subprocess.check_output(
        ["xdotool", "search", "--name", "同花顺"]
    ).decode().strip().split()
    
    # 3. 对每个候选窗口验证 PID
    for wid in candidates:
        win_pid = subprocess.check_output(
            ["xdotool", "getwindowpid", wid]
        ).decode().strip()
        if win_pid == ths_pid:
            # 4. 最终验证窗口标题
            name = subprocess.check_output(
            ["xdotool", "getwindowname", wid]
        ).decode().strip()
            if "同花顺" in name:
                return int(wid)
    
    raise XdotoolError("未找到可信的同花顺窗口")
```

### 发现 4：异常处理 5 大盲区

逐行审计 `_fill_order()` 的异常场景：

| # | 场景 | 代码覆盖 | 实际风险 | 后果 |
|---|------|----------|----------|------|
| 1 | 窗口消失/崩溃 | ❌ | 🔴 高 | xdotool 命令静默失败，方法返回虚构 order_id |
| 2 | 弹窗遮挡（确认/验证码/广告） | ❌ | 🔴 高 | 点击/输入命中弹窗，非目标控件 |
| 3 | 输入法干扰 | ❌ | 🟡 中 | fcitx 可能拦截 xdotool type 的键击 |
| 4 | 同花顺版本更新改版 | ❌ | 🔴 高 | 坐标全部失效，无运行时检测 |
| 5 | 网络断开（同花顺到券商） | ❌ | 🔴 高 | 点击买入但委托未达券商，无反馈 |

**弹窗处理**是最紧迫的问题。同花顺在以下情况会弹窗：
- 委托确认对话框（每次交易必有）
- 验证码（异常登录/频繁操作）
- 系统公告/升级提醒
- 网络异常提示
- 资金不足/涨跌停拒绝提示

当前代码**完全没有弹窗检测机制**，`click_at()` 可能点击到弹窗上，`type_text()` 可能输入到弹窗的文本框里。

**修复方案 — 弹窗守卫**：
```python
class PopupGuard:
    """弹窗检测与自动处理"""
    POPUP_PATTERNS = {
        "确认": self._click_confirm,
        "验证码": self._alert_human,
        "公告": self._close_popup,
        "网络异常": self._retry_or_stop,
    }
    
    def check_popup(self, window_id: int) -> bool:
        """截图检测是否有弹窗遮挡"""
        screenshot = capture_window(window_id)
        for pattern, handler in self.POPUP_PATTERNS.items():
            if ocr_contains(screenshot, pattern):
                return handler(screenshot)
        return False
```

### 发现 5：风控熔断配置形同虚设

`config.yaml` 定义了完整的风控参数，但代码中大量未使用：

```yaml
# config.yaml — 定义了但未使用
risk:
  order_timeout: 60           # ❌ 无代码引用
  consecutive_loss_pause: 3   # ❌ 无代码引用
  daily_loss_limit: 0.03      # ❌ 未验证是否在引擎中使用
```

搜索源码：
- `order_timeout: 60` — 设计用于单笔委托超时自动撤单，但 `_fill_order()` 没有总超时参数
- `consecutive_loss_pause: 3` — 设计用于连续亏损 3 次暂停策略，但无 `CircuitBreaker` 状态机实现
- `exceptions.py` 中定义了 `CircuitBreakerTripped` 和 `SystemLocked` 异常，但从未被 raise

**熔断器标准实现（缺失）**：
```python
class CircuitBreaker:
    """交易熔断器 — closed → open → half_open → closed"""
    
    def __init__(self, failure_threshold=3, cooldown=1800):
        self.state = "closed"
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.last_failure_time = 0
    
    def record_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            raise CircuitBreakerTripped(
                f"连续 {self.failure_count} 次失败，熔断 {self.cooldown}s"
            )
    
    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure_time > self.cooldown:
                self.state = "half_open"
                return True  # 试探性放行一次
            return False
        return True  # half_open
```

---

## 实践启发

### 1. 分层防护架构（推荐）

从 L1 到 L4 逐层加固，每层独立生效：

```
L4: 人工确认层 — 高风险操作（首笔实盘、大额、新股）需人工确认
L3: 熔断器层 — 连续失败自动暂停，冷却期后试探恢复
L2: 操作验证层 — 每步操作后截图+OCR 确认预期结果
L1: 窗口守卫层 — 窗口存在+焦点正确+无弹窗遮挡
```

**实施优先级**：L1（2 天） → L2（3 天） → L3（1 天） → L4（1 天）

### 2. xdotool 替代方案对比

| 方案 | 可靠性 | 开发量 | 适用性 | 备注 |
|------|--------|--------|--------|------|
| xdotool + OCR 验证 | 中高 | 中 | ✅ 当前首选 | 短期内最现实 |
| AT-SPI 辅助功能 | 高 | 高 | ⚠️ 需验证 | Avalonia 可能不支持 AT-SPI |
| Wine + easytrader | 高 | 中 | ⚠️ ARM64 兼容性 | Jetson ARM64 跑 Wine 可能有性能问题 |
| 券商 API (QMT/PTrade) | 最高 | 高 | ⭐ 终极方案 | 需券商开通权限，门槛高 |
| TTS 穿透式 | 最高 | 极高 | ❌ 开发成本过大 | 仅机构可承担 |
| Selenium Web 版 | 低 | 低 | ❌ 反爬严格 | 同花顺 Web 版限制多 |

**推荐路线**：短期 xdotool+OCR → 中期 AT-SPI 验证/Wine → 长期 QMT API

### 3. 关键操作的安全模式

```python
class SafeXdotoolBroker(XdotoolBroker):
    """安全增强版 xdotool broker"""
    
    def _safe_execute(self, operation_name: str, operation: callable, 
                      max_retries: int = 3, verify: callable = None):
        """安全执行框架：前置检查 → 执行 → 验证 → 异常处理"""
        for attempt in range(max_retries):
            try:
                # 前置检查
                self._guard.check_window_alive()
                self._guard.check_no_popup()
                self._guard.check_focus()
                
                # 执行操作
                result = operation()
                
                # 验证结果
                if verify and not verify(result):
                    raise VerificationError(f"{operation_name} 验证失败")
                
                # 成功 → 重置熔断器
                self._breaker.record_success()
                return result
                
            except (WindowNotFoundError, PopupDetectedError) as e:
                self._breaker.record_failure()
                if attempt < max_retries - 1:
                    self._recover()  # 自动恢复
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise  # 最终失败
```

### 4. 截图验证流水线

xdotool 本身无法读取屏幕内容，但可以配合截图 + OCR 构建闭环：

```bash
# 安装依赖
sudo apt install scrot tesseract-ocr tesseract-ocr-chi-sim
pip install pytesseract Pillow
```

```python
def capture_and_verify(window_id: int, region: str, expected_text: str) -> bool:
    """截图指定区域并 OCR 验证"""
    # 1. 获取窗口几何
    x, y, w, h = get_window_geometry(window_id)
    
    # 2. 截图窗口
    img = capture_region(x, y, w, h)
    
    # 3. 裁剪目标区域
    region_coords = VERIFY_REGIONS[region]  # 如 "委托确认" 的坐标
    cropped = img.crop(region_coords)
    
    # 4. OCR
    text = pytesseract.image_to_string(cropped, lang='chi_sim+eng')
    
    # 5. 验证
    return expected_text in text
```

---

## 知识缺口

1. **AT-SPI 可用性未验证** — Avalonia UI 框架是否实现了 Linux AT-SPI 辅助功能接口。如果支持，可以取代 xdotool 实现控件级自动化（不再依赖坐标），可靠性将大幅提升。需要运行 `accerciser` 或 `spy` 工具检测同花顺窗口的可访问性树。

2. **fcitx/ibus 输入法干扰** — 理论上 xdotool type 绕过输入法直接发送 X11 键击事件，但 fcitx5 在某些配置下可能拦截 KeySym 事件。需要在实际环境验证中文输入是否受影响（同花顺股票代码是纯数字不受影响，但价格含小数点可能受影响）。

3. **Jetson Orin GPU 加速 OCR 可行性** — Tesseract OCR 在 ARM64 上较慢（单次可能 500ms+），Jetson Orin Nano Super 有 1024 CUDA 核心的 GPU 和 40 TOPS 的 NPU。可以考虑用 PaddleOCR（支持 GPU 加速）或 suruOCR（轻量级）替代。

4. **Wine + easytrader 在 ARM64 上的可行性** — easytrader 底层用 pywinauto（Windows COM 接口），Wine 在 ARM64 上通过 WoW64 兼容层可以运行 x86 Windows 程序，但性能和稳定性未知。如果可行，可以绕过 xdotool 整条路径。

5. **同花顺 Web API 接口** — 是否存在隐藏的 Web 接口可以直接下单（类似东方财富的 push2 API）。如果存在，可以完全绕过 GUI 自动化。

6. **xdotool 线程安全** — 多策略并发下单时，xdotool 命令是否会互相干扰（如策略 A 正在输入代码时策略 B 点击了买入）。当前 XdotoolBroker 无任何并发控制，需要加操作队列或互斥锁。

---

## 相关笔记

- `xdotool-broker-reliability.md` — 5 大稳定性问题的详细分析（项目 references 目录）
- `ths-linux-client-automation.md` — 同花顺 Linux 客户端架构分析（Avalonia + CEF）
- `auto-trading-system-design.md` — A 股自动化交易系统整体架构设计（五层风控、策略插件、回测管线）
- `ths-auto-trader-implementation.md` — THS Auto Trader 实测验证的代码架构模式

## 核心结论

当前 xdotool 自动化下单系统处于 **MVP 阶段**，能演示基本流程但**不可用于实盘**。最大的两个风险点：

1. **开环执行**（无验证）— 可能误报成功导致重复下单
2. **坐标漂移**（无自适应）— 窗口尺寸变化即全部失效

短期（1 周内）应优先实现：L1 窗口守卫 + L2 截图验证 + 自适应坐标。中期（2-4 周）探索 AT-SPI 或 OpenCV 模板匹配替代固定坐标。长期目标是迁移到券商 API，彻底消除 GUI 自动化的不确定性。
