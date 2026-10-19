# easytrader 同花顺接口深度调研

> 本地知识蒸馏 | 2026-05-17 | Topic: ths-auto-trader
> 来源：GitHub 项目文档 + 已有探索笔记整合 + 技术社区经验
> 难度: L3（深度探索）| 字数: ~3500

---

## 一、核心结论（5 个关键发现）

### 发现 1：easytrader 是目前散户 A 股自动化交易的最佳开源方案，但有明确天花板

easytrader（shidenggui, GitHub 3000+ stars）是 Python 编写的 A 股自动化交易库，通过 GUI 自动化方式控制券商客户端：

| 维度 | 评估 |
|------|------|
| **核心原理** | pywinauto（Windows Accessibility API）→ 识别控件树 → 模拟用户操作 |
| **支持券商** | 同花顺（THS）、华泰（htzq）、国金（gj）、通用客户端 |
| **下单延迟** | 200-500ms（从 API 调用到客户端发出委托） |
| **稳定性** | ⭐⭐⭐⭐（比 xdotool 坐标方案稳定一个量级） |
| **平台限制** | **Windows Only**（核心依赖 pywinauto + Win32 API） |
| **维护状态** | 社区维护，主要更新来自 PR，原作者活跃度下降 |

**核心优势**：
- 控件级定位（不依赖屏幕坐标），跨分辨率/DPI 适应
- API 简洁：`user.buy(code, price, amount)` 即可下单
- 3000+ stars 社区生态，常见问题有现成解答

**核心限制**：
- 依赖 Windows + 完整 GUI 环境（无法 headless 运行）
- 同花顺客户端更新后控件结构可能变化，需要更新 easytrader
- 不支持港股/期权/融资融券等复杂操作
- 下单延迟 200-500ms，不适合高频（日内 T+0 级别）
- 无法获取 L2 行情数据

### 发现 2：easytrader 内部架构与工作原理

```
easytrader 架构
┌──────────────────────────────────────────┐
│ 用户 Python 代码                           │
│  user.buy("600519", price=1800, amount=100) │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│ easytrader API 层                          │
│  - buy/sell/cancel/position/balance        │
│  - 参数校验、价格格式化                      │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│ 平台适配层（Platform Adapter）              │
│  - ths_trader.py（同花顺）                  │
│  - htzq_trader.py（华泰）                  │
│  - 每个券商一套控件标识映射                   │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│ pywinauto 底层                              │
│  - Windows Accessibility API              │
│  - 获取控件树、模拟键盘/鼠标事件              │
│  - 读取控件文本属性（非 OCR）                │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│ 同花顺客户端（THS GUI）                      │
│  - 实际下单通过券商交易通道                    │
└──────────────────────────────────────────┘
```

**关键代码示例**：

```python
import easytrader

# 初始化
user = easytrader.use("ths")  # 选择同花顺
user.connect()                 # 连接客户端（需先打开 THS 并登录）

# 基础交易
user.buy("600519", price=1800.00, amount=100)
user.sell("600519", price=1850.00, amount=100)

# 查询
positions = user.position     # 持仓列表
balance = user.balance        # 资金余额
today_entrusts = user.entrust # 当日委托
today_trades = user.deal      # 当日成交

# 撤单
user.cancel_entrust(entrust_no)

# 自动打新
user.auto_ipo()
```

**控件定位原理**：

```python
# easytrader 内部（简化版）
from pywinauto import Application

app = Application().connect(title_re=".*同花顺.*")
main_window = app.window(title_re=".*同花顺.*")

# 定位买入按钮（通过控件类名和标题）
buy_button = main_window.child_window(
    title="买入[B]",
    control_type="Button"
)

# 定位股票代码输入框
code_edit = main_window.child_window(
    automation_id="股票代码输入框"
)

# 读取持仓表格
grid = main_window.child_window(class_name="CVirtualGridCtrl")
# 通过控件属性读取文本，非 OCR
```

### 发现 3：easytrader vs xdotool 实战对比

| 维度 | xdotool（Linux） | easytrader（Windows） |
|------|------------------|---------------------|
| **元素定位** | 坐标/图像匹配 | Win32 控件树 |
| **延迟** | 500-1200ms | 200-500ms |
| **跨分辨率** | ❌ 不支持 | ✅ 自动适应 |
| **多显示器** | ⚠️ 部分支持 | ✅ 支持 |
| **依赖环境** | Linux + X11 | Windows + GUI |
| **OCR 需求** | 需要（验证码/文本） | 不需要（控件属性） |
| **稳定性** | ⭐⭐（坐标漂移） | ⭐⭐⭐⭐（控件稳定） |
| **客户端更新后** | 可能需要重新截图模板 | 需要更新控件映射 |
| **延迟来源** | GUI 渲染 + 搜索匹配 | 控件树遍历 + API 调用 |
| **适用场景** | Linux 环境、跨软件协同 | Windows 专用、A 股自动化 |

**结论**：对于 A 股自动化交易，easytrader 在 Windows 环境下明显优于 xdotool。核心优势在于**控件级定位**消除了坐标漂移问题。

### 发现 4：混合架构是 Jetson/Linux 用户的最佳实践

由于 ths-auto-trader 项目运行在 Jetson Orin（Linux/ARM）上，而 easytrader 仅支持 Windows，推荐混合架构：

```
┌──────────────────────────────────────┐
│ Jetson Orin Nano（Linux/ARM）          │
│  - 策略引擎（信号生成）                 │
│  - 行情数据处理（akshare/tushare）      │
│  - 风控模块                            │
│  - SQLite 存储交易记录                  │
│  - 定时调度（cron）                     │
│                                        │
│  HTTP API 发送交易信号 ↓               │
├──────────────────────────────────────┤
│ Windows PC/VM（执行节点）               │
│  - easytrader + 同花顺客户端            │
│  - Flask HTTP Server 接收信号          │
│  - 执行下单 → 返回结果                  │
│  - 状态心跳上报                         │
└──────────────────────────────────────┘
```

**通信协议设计**：

```python
# --- Linux 策略端 ---
import requests, hmac, hashlib, time

class TradeExecutor:
    def __init__(self, executor_url, secret_key):
        self.url = executor_url
        self.secret = secret_key

    def _sign(self, payload):
        return hmac.new(
            self.secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    def send_order(self, code, direction, price, amount):
        timestamp = int(time.time())
        payload = f"{code}{direction}{price}{amount}{timestamp}"
        resp = requests.post(
            f"{self.url}/trade",
            json={
                "code": code,
                "direction": direction,
                "price": round(price, 2),
                "amount": amount,
                "timestamp": timestamp,
                "signature": self._sign(payload)
            },
            timeout=10
        )
        return resp.json()
```

```python
# --- Windows 执行端 ---
from flask import Flask, request, jsonify
import easytrader

app = Flask(__name__)
trader = easytrader.use("ths")
trader.connect()

@app.route("/trade", methods=["POST"])
def execute():
    data = request.json
    if data["direction"] == "BUY":
        result = trader.buy(data["code"], data["price"], data["amount"])
    else:
        result = trader.sell(data["code"], data["price"], data["amount"])
    return jsonify(result)

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"status": "alive", "balance": trader.balance})

app.run(host="0.0.0.0", port=8080)
```

### 发现 5：easytrader 的 6 大坑与解决方案

| 坑 | 症状 | 解决方案 |
|----|------|----------|
| **控件 ID 变更** | THS 更新后 `child_window()` 找不到控件 | 使用 `print_control_identifiers()` 重新抓取；写容错 fallback |
| **编码问题** | 股票名/持仓含中文乱码 | 设置 UTF-8 编码 + Windows 系统编码为 UTF-8 |
| **多账户混淆** | 同时打开多个客户端时操作错窗口 | `connect()` 时指定窗口标题精确匹配 |
| **超时异常** | 网络慢时操作超时导致状态不一致 | 所有操作加 try-except + 持仓对账 |
| **价格精度** | 传 `1800.5` 而非 `1800.50` 被拒绝 | `price = round(float(price), 2)` |
| **登录状态丢失** | THS 长时间运行后 session 过期 | 定时心跳 + 自动重连机制 |

---

## 二、技术细节

### 2.1 容错与重试机制

```python
import time, logging
from functools import wraps

logger = logging.getLogger("easytrader_wrapper")

def with_retry(max_retries=3, delay=2):
    """操作重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result and result.get("success", False):
                        return result
                    logger.warning(f"Attempt {attempt+1}: {result}")
                except Exception as e:
                    logger.error(f"Attempt {attempt+1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class SafeTrader:
    def __init__(self):
        self.trader = easytrader.use("ths")
        self.trader.connect()

    @with_retry(max_retries=3, delay=2)
    def buy(self, code, price, amount):
        result = self.trader.buy(code, price=price, amount=amount)
        time.sleep(1)
        entrusts = self.trader.entrust
        for e in entrusts:
            if (e.get("证券代码") == code and
                e.get("操作") == "买入" and
                abs(float(e.get("委托价格", 0)) - price) < 0.01):
                return {"success": True, "entrust_no": e.get("委托编号")}
        return {"success": False, "reason": "委托未找到"}

    @with_retry(max_retries=3, delay=2)
    def sell(self, code, price, amount):
        return self.trader.sell(code, price=price, amount=amount)
```

### 2.2 与 ths-auto-trader 项目集成方案

ths-auto-trader 当前使用 xdotool 方案（Jetson Linux 环境限制）。推荐演进路径：

| Phase | 方案 | 适用条件 |
|-------|------|----------|
| Phase 1（当前） | xdotool + OCR | Linux 环境，低频交易（日频） |
| Phase 2 | 混合架构（Linux 策略 + Windows easytrader） | 需要更高稳定性 |
| Phase 3 | 券商 API（QMT/PTrade） | 资金量 >100 万，需要低延迟 |

**Phase 2 实施步骤**：
1. 在 Windows PC 安装 THS + easytrader
2. 部署 Flask 执行服务
3. Jetson 端部署 `TradeExecutor` 客户端
4. 内网通信（Jetson ↔ Windows 局域网）
5. 心跳监控 + 异常告警

---

## 三、实践启发

1. **easytrader 适合日频/周频策略**：200-500ms 延迟足够中低频量化，不适合日内高频
2. **Windows 是必要条件**：Jetson/Linux 用户必须走混合架构
3. **稳定性显著优于 xdotool**：控件定位比坐标定位可靠 10 倍以上
4. **社区活跃度是风险**：原作者维护减少，THS 大版本更新可能需要自行适配
5. **合规灰色地带**：GUI 自动化属于"模拟人工操作"，监管风险低于 API 直连

## 四、知识缺口

1. **easytrader 对 THS 2025/2026 版本的兼容性**：需实际测试
2. **华泰客户端支持状态**：华泰客户端改版后的适配情况
3. **并发能力**：多策略同时下单时的线程安全性
4. **错误恢复**：网络断开、客户端崩溃后的自动恢复方案
5. **与通达信自动化（pytdx + xdotool）的对比**：通达信协议更底层

## 五、升级路径评估

| 路径 | 门槛 | 延迟 | 稳定性 | 适合阶段 |
|------|------|------|--------|----------|
| xdotool（当前） | 低 | 500-1200ms | ⭐⭐ | Phase 1 验证 |
| **easytrader（推荐）** | 中 | 200-500ms | ⭐⭐⭐⭐ | Phase 2 升级 |
| QMT/PTrade API | 高 | 10-50ms | ⭐⭐⭐⭐⭐ | Phase 3 专业级 |
| 券商自研 SDK | 极高 | <10ms | ⭐⭐⭐⭐⭐ | 机构级 |

**建议**：ths-auto-trader 项目在 Phase 1（xdotool 验证）完成后，优先升级到 easytrader 混合架构，性价比最高。

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
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
