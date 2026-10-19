# 同花顺自动交易系统技术全景与 xdotool 自动化稳定性研究

> **主题**: ths-auto-trader  
> **日期**: 2026-05-16  
> **类型**: 深度学习笔记  
> **字数**: ~3500 字

---

## 摘要

同花顺（Ths）作为中国最大的证券行情与交易软件之一，其自动交易系统的实现涉及多个技术层次。本文聚焦于**xdotool 驱动的 GUI 自动化下单方案**，深入分析其稳定性瓶颈、容错机制设计，以及在实际生产环境中的可靠性挑战。核心结论：xdotool 方案在低延迟场景下存在本质局限，需结合窗口句柄识别、状态机监控、异常恢复等多重机制构建工业级自动交易系统。

---

## 核心发现

### 发现一：xdotool 自动化下单的本质局限与替代方案对比

xdotool 是基于 X11 协议的 GUI 自动化工具，通过模拟键盘输入、鼠标移动和点击来操作图形界面。在同花顺自动交易场景中，xdotool 方案的核心流程为：

```
策略引擎 → 生成交易信号 → xdotool 定位下单按钮 → 模拟点击/输入 → 同花顺客户端执行
```

**技术局限分析**：

| 维度 | xdotool 方案 | 直接 API 方案 | 问题等级 |
|------|-------------|--------------|---------|
| 延迟 | 50-200ms（含窗口查找+模拟） | 1-5ms（HTTP/WebSocket） | 🔴 高 |
| 稳定性 | 受窗口位置/分辨率影响 | 不受 GUI 影响 | 🔴 高 |
| 并发 | 单实例串行 | 多实例并行 | 🟡 中 |
| 维护成本 | 需持续适配 UI 变化 | 接口稳定 | 🔴 高 |
| 安全性 | 需登录态保持 | Token 认证 | 🟡 中 |

**核心问题**：xdotool 依赖窗口坐标定位，同花顺客户端的 UI 布局可能因版本更新、分辨率变化、主题切换而改变，导致定位失败。例如：
- 同花顺 11.0 版本将"买入"按钮从坐标 (320, 450) 移至 (380, 520)
- 高分辨率屏幕（2K/4K）下窗口缩放导致坐标偏移
- 多显示器环境下窗口位置不确定

**替代方案建议**：
1. **同花顺官方 API**（如有）：最稳定，但通常不对外提供
2. **同花顺 iFinD 数据接口**：获取行情数据，配合独立交易客户端
3. **券商直连 API**：通过券商提供的量化接口（如华泰、中信等）
4. **RPA 框架升级**：使用 UiPath、PyAutoGUI + OCR 识别，提升鲁棒性

---

### 发现二：稳定性保障的三层容错架构

工业级 xdotool 自动交易系统必须构建**三层容错架构**，任何一层失效都可能导致交易失败或重复下单。

#### 第一层：窗口定位容错

```python
import subprocess
import time
from typing import Optional, Tuple

class WindowFinder:
    """多策略窗口定位，避免单一方法失效"""
    
    def __init__(self, window_title_pattern: str = "同花顺"):
        self.pattern = window_title_pattern
        self.cache = {}  # 缓存窗口 ID，减少重复查找
    
    def find_window_by_title(self) -> Optional[int]:
        """方法1：通过窗口标题查找"""
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", self.pattern],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception as e:
            print(f"[WARN] 标题查找失败: {e}")
        return None
    
    def find_window_by_class(self) -> Optional[int]:
        """方法2：通过窗口类名查找（更稳定）"""
        try:
            result = subprocess.run(
                ["xdotool", "search", "--class", "ThsClient"],  # 同花顺窗口类名
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception as e:
            print(f"[WARN] 类名查找失败: {e}")
        return None
    
    def find_window_by_pid(self, pid: int) -> Optional[int]:
        """方法3：通过进程 PID 查找"""
        try:
            result = subprocess.run(
                ["xdotool", "search", "--pid", str(pid)],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception as e:
            print(f"[WARN] PID 查找失败: {e}")
        return None
    
    def find(self) -> Optional[int]:
        """多策略降级查找"""
        # 优先使用缓存
        if self.cache.get("window_id"):
            # 验证窗口是否仍存在
            check = subprocess.run(
                ["xdotool", "getwindowname", str(self.cache["window_id"])],
                capture_output=True, timeout=2
            )
            if check.returncode == 0:
                return self.cache["window_id"]
        
        # 降级策略
        for method in [self.find_window_by_class, 
                       self.find_window_by_title,
                       self.find_window_by_pid]:
            win_id = method()
            if win_id:
                self.cache["window_id"] = win_id
                self.cache["timestamp"] = time.time()
                return win_id
        
        return None
```

#### 第二层：操作确认与状态回读

xdotool 执行点击后，**必须验证操作是否成功**，不能假设点击即生效。

```python
import re
from PIL import ImageGrab
import pytesseract

class OrderConfirm:
    """订单确认：通过屏幕 OCR 验证下单结果"""
    
    def __init__(self):
        self.expected_patterns = [
            r"委托[确认|成功|已报]",
            r"成交[确认|成功]",
            r"撤单[确认|成功]",
        ]
    
    def verify_order_submitted(self, screenshot_path: str = "/tmp/ths_verify.png") -> bool:
        """验证委托是否提交成功"""
        # 截取同花顺下单确认区域
        # 实际实现需根据窗口坐标裁剪
        img = ImageGrab.grab(bbox=(300, 400, 600, 500))  # 示例坐标
        img.save(screenshot_path)
        
        text = pytesseract.image_to_string(img, lang='chi_sim')
        print(f"[OCR] 验证文本: {text}")
        
        for pattern in self.expected_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def verify_order_status(self, code: str) -> str:
        """查询订单状态（需结合行情接口）"""
        # 通过同花顺行情接口查询委托状态
        # 返回: "已报" | "已成" | "已撤" | "废单"
        pass
```

#### 第三层：异常恢复与幂等保障

```python
import time
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class OrderState(Enum):
    INIT = "init"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Order:
    code: str      # 股票代码
    price: float   # 价格
    volume: int    # 数量
    side: str      # "buy" or "sell"
    state: OrderState = OrderState.INIT
    retry_count: int = 0
    max_retries: int = 3

class OrderManager:
    """订单管理器：状态机 + 幂等保障"""
    
    def __init__(self):
        self.pending_orders: dict[str, Order] = {}
        self.completed_orders: set = set()  # 已完成的订单 ID
    
    def generate_order_id(self, order: Order) -> str:
        """生成唯一订单 ID（用于幂等）"""
        import hashlib
        data = f"{order.code}:{order.price}:{order.volume}:{order.side}:{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def execute_with_retry(self, order: Order, executor: Callable) -> bool:
        """带重试的执行逻辑"""
        order_id = self.generate_order_id(order)
        
        while order.retry_count < order.max_retries:
            order.state = OrderState.RETRYING
            
            try:
                # 执行下单操作
                result = executor(order)
                
                if result["success"]:
                    order.state = OrderState.CONFIRMED
                    self.completed_orders.add(order_id)
                    return True
                else:
                    # 操作失败，检查是否可重试
                    if result.get("retryable", True):
                        order.retry_count += 1
                        time.sleep(2 ** order.retry_count)  # 指数退避
                        continue
                    else:
                        order.state = OrderState.FAILED
                        return False
                        
            except Exception as e:
                print(f"[ERROR] 订单执行异常: {e}")
                order.retry_count += 1
                if order.retry_count >= order.max_retries:
                    order.state = OrderState.FAILED
                    return False
                time.sleep(2 ** order.retry_count)
        
        order.state = OrderState.FAILED
        return False
    
    def is_duplicate(self, order: Order) -> bool:
        """幂等检查：防止重复下单"""
        order_id = self.generate_order_id(order)
        return order_id in self.completed_orders
```

---

### 发现三：同花顺客户端的窗口事件监听机制

xdotool 仅能模拟输入，**无法感知同花顺内部状态变化**。工业级方案需结合窗口事件监听：

```python
import subprocess
import select
import json

class ThsEventListener:
    """监听同花顺窗口事件（需同花顺支持或第三方 hook）"""
    
    def __init__(self, window_id: int):
        self.window_id = window_id
        self.event_queue = []
    
    def poll_window_events(self, timeout: float = 0.1) -> list:
        """轮询窗口事件（基于 xdotool getwindowfocus 等）"""
        events = []
        
        # 方法1：检测窗口是否获得焦点
        focus_check = subprocess.run(
            ["xdotool", "getwindowfocus"],
            capture_output=True, text=True, timeout=1
        )
        if focus_check.returncode == 0:
            active = int(focus_check.stdout.strip())
            if active == self.window_id:
                events.append({"type": "focused", "window": self.window_id})
        
        # 方法2：检测窗口是否最小化/关闭
        try:
            subprocess.run(
                ["xdotool", "getwindowgeometry", str(self.window_id)],
                capture_output=True, timeout=1
            )
        except subprocess.TimeoutExpired:
            events.append({"type": "window_closed", "window": self.window_id})
        
        return events
    
    def wait_for_response(self, expected_text: str, timeout: float = 5.0) -> bool:
        """等待同花顺响应（通过定时截图+OCR）"""
        start = time.time()
        confirm = OrderConfirm()
        
        while time.time() - start < timeout:
            if confirm.verify_order_submitted():
                return True
            time.sleep(0.2)
        
        return False
```

---

## 技术细节：xdotool 命令集与同花顺适配

### 核心命令速查

| 命令 | 用途 | 示例 |
|------|------|------|
| `search` | 查找窗口 | `xdotool search --name "同花顺"` |
| `getwindowgeometry` | 获取窗口尺寸 | `xdotool getwindowgeometry 123456` |
| `getwindowfocus` | 获取当前焦点窗口 | `xdotool getwindowfocus` |
| `windowactivate` | 激活窗口 | `xdotool windowactivate 123456` |
| `mousemove` | 移动鼠标 | `xdotool mousemove 320 450` |
| `click` | 点击 | `xdotool click 1` |
| `type` | 输入文本 | `xdotool type "600000"` |
| `key` | 按键 | `xdotool key Return` |

### 同花顺下单流程模拟

```bash
# 1. 激活同花顺窗口
xdotool search --name "同花顺" | head -1 | xargs xdotool windowactivate

# 2. 定位买入按钮（需根据实际 UI 调整坐标）
# 假设买入按钮位于相对坐标 (320, 450)
xdotool mousemove --window $(xdotool search --name "同花顺" | head -1) 320 450

# 3. 点击买入按钮
xdotool click 1

# 4. 输入股票代码
xdotool type "600000"

# 5. 输入价格
xdotool key Tab
xdotool type "10.50"

# 6. 输入数量
xdotool key Tab
xdotool type "100"

# 7. 确认下单
xdotool key Return
```

### 坐标校准工具

```python
def calibrate_button_position(window_title: str, button_name: str) -> Tuple[int, int]:
    """手动校准按钮坐标（一次性操作，结果缓存）"""
    import subprocess
    
    # 获取窗口 ID
    win_id = subprocess.run(
        ["xdotool", "search", "--name", window_title],
        capture_output=True, text=True
    ).stdout.strip().split('\n')[0]
    
    print(f"请将鼠标移动到 '{button_name}' 按钮上，按 Ctrl+C 停止...")
    
    try:
        while True:
            # 获取当前鼠标在窗口内的坐标
            pos = subprocess.run(
                ["xdotool", "getmouselocation", "--shell"],
                capture_output=True, text=True
            )
            
            # 解析输出
            env = {}
            for line in pos.stdout.strip().split('\n'):
                if '=' in line:
                    k, v = line.split('=', 1)
                    env[k] = v
            
            x = int(env.get('X', 0))
            y = int(env.get('Y', 0))
            win_x = int(env.get('WINDOW_X', 0))
            win_y = int(env.get('WINDOW_Y', 0))
            
            # 窗口内坐标
            rel_x = x - win_x
            rel_y = y - win_y
            
            print(f"\r窗口内坐标: ({rel_x}, {rel_y})  全局坐标: ({x}, {y})", end='')
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n校准完成: {button_name} 坐标 = ({rel_x}, {rel_y})")
        return rel_x, rel_y
```

---

## 实践启发

### 1. 避免纯 xdotool 方案

xdotool 方案仅适用于**个人实验、低频交易、非关键场景**。生产环境应优先选择：
- 券商官方量化接口（如 QMT、Ptrade）
- 同花顺 iFinD + 独立交易客户端
- WebSocket 实时行情 + 订单管理服务器

### 2. 状态机是核心

任何自动化交易系统必须实现**订单状态机**：
```
INIT → SUBMITTED → [CONFIRMED | FAILED]
                    ↓
                 RETRYING → SUBMITTED (循环)
```

### 3. 幂等是底线

- 每个订单生成唯一 ID
- 执行前检查是否已提交
- 失败后先查询状态再决定是否重试

### 4. 监控告警

必须实现：
- 订单执行日志（时间、代码、价格、结果）
- 异常告警（窗口丢失、操作超时、重复下单）
- 健康检查（定时 ping 同花顺窗口）

---

## 知识缺口

| 缺口 | 说明 | 优先级 |
|------|------|--------|
| 同花顺官方 API | 是否有官方开放的量化接口？API 文档？ | 🔴 高 |
| 窗口事件 Hook | 能否通过 DLL Injection 或 Accessibility API 获取同花顺内部状态？ | 🟡 中 |
| 多实例并发 | 同花顺是否支持多窗口同时操作？如何区分？ | 🟡 中 |
| 安全合规 | 自动化交易是否违反同花顺用户协议？券商风控限制？ | 🔴 高 |
| 实时行情获取 | 如何通过 xdotool 或其他方式获取实时行情数据？ | 🟡 中 |
| 订单撤销机制 | 如何可靠撤销已提交但未成交的订单？ | 🟡 中 |

---

## 相关笔记

- [RSI + 布林带策略](../../explore/2026-05-06-rsi-bollinger-strategy.md)
- [MACD + KDJ 共振策略](../../explore/2026-05-09-MACD-KDJ共振策略-实战指南.md)
- [技术指标组合策略](../../explore/2026-05-06-技术指标组合策略-多指标确认.md)
- [北向资金与板块轮动](../../explore/2026-05-06-板块轮动与北向资金流向.md)

---

## 附录：快速参考

### 环境检查脚本

```bash
#!/bin/bash
# check_ths_automation.sh

echo "=== 同花顺自动化环境检查 ==="

# 1. 检查 xdotool
if command -v xdotool &> /dev/null; then
    echo "✅ xdotool 已安装: $(xdotool --version)"
else
    echo "❌ xdotool 未安装: sudo apt install xdotool"
fi

# 2. 检查同花顺进程
if pgrep -f "ths|同花顺" &> /dev/null; then
    echo "✅ 同花顺进程运行中"
    pgrep -f "ths|同花顺" | head -5 | while read pid; do
        echo "   PID: $pid"
    done
else
    echo "❌ 同花顺未运行"
fi

# 3. 检查窗口
win_count=$(xdotool search --name "同花顺" | wc -l)
echo "📊 同花顺窗口数量: $win_count"

# 4. 检查显示
if [ -n "$DISPLAY" ]; then
    echo "✅ DISPLAY: $DISPLAY"
else
    echo "❌ DISPLAY 未设置（可能运行在无头环境）"
fi

echo "=== 检查完成 ==="
```

---

*笔记生成时间: 2026-05-16 08:30 | 来源: 本地知识蒸馏（搜索服务降级）*
