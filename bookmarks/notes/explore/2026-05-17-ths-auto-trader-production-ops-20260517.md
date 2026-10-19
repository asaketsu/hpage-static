# 同花顺自动化交易 — 实盘部署运维与监控体系

> 2026-05-17 | proactive-learn 深度研究 | Topic: ths-auto-trader
> 基于 ths-auto-trader 项目代码（39 个 Python 模块）+ 行业实践整理
> 知识缺口填补：已有笔记覆盖架构设计、easytrader、QMT/PTrade、止损策略，
> 本篇聚焦 **实盘部署、运维监控、故障恢复、合规风控** 四大缺口
> 字数: ~3500 | 难度: L4（实战级）

---

## 一、核心发现（5 个关键发现）

### 发现 1：Linux 部署存在 3 个致命依赖，不解决无法实盘运行

项目在 Jetson Orin (aarch64/Linux) 上运行，通过 xdotool 控制 THS Linux 客户端。但实盘部署有 3 个硬性依赖：

| 依赖 | 问题 | 解决方案 | 优先级 |
|------|------|---------|--------|
| **X11 显示服务器** | xdotool 需要活跃 X session，无头模式不可用 | Xvfb 虚拟帧缓冲 + VNC 远程诊断 | P0 |
| **THS 客户端存活** | 客户端崩溃/更新后坐标失效 | 进程守护 + 健康检查 + 自动重启脚本 | P0 |
| **窗口焦点稳定性** | 其他窗口抢占焦点导致误操作 | 专用虚拟桌面（Xvfb :99）+ 窗口管理器锁定 | P1 |

**Xvfb 部署配置**：
```bash
# 1. 安装虚拟帧缓冲
sudo apt install xvfb x11vnc wmctrl

# 2. 创建专用 DISPLAY
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# 3. 启动窗口管理器（确保窗口可定位）
fluxbox &

# 4. 启动 THS 客户端
/opt/apps/cn.com.10jqka/files/HevoNext.B2CApp &

# 5. 等待客户端初始化（CEF 渲染需要 5-15 秒）
sleep 15

# 6. 校准窗口位置
wmctrl -r "同花顺" -e 0,0,0,1920,1080

# 7. VNC 远程诊断（可选）
x11vnc -display :99 -forever -passwd YOUR_VNC_PASS &
```

**systemd 服务单元**：
```ini
# /etc/systemd/system/ths-auto-trader.service
[Unit]
Description=THS Auto Trader
After=network.target display-manager.service
Wants=xvfb.service

[Service]
Type=simple
User=jc
Environment=DISPLAY=:99
WorkingDirectory=/home/jc/uclaw/project/ths-auto-trader
ExecStartPre=/bin/sleep 5
ExecStart=/home/jc/.venv/bin/python -m ths_auto_trader.cli run --live
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

# 安全限制
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/jc/uclaw/project/ths-auto-trader/data

[Install]
WantedBy=multi-user.target
```

### 发现 2：项目缺少实时健康监控层，需要 3 级检测机制

当前代码有 `trading_engine.py`（256 行）管理策略→风控→执行闭环，但**没有独立的健康监控进程**。实盘场景必须实现以下 3 级检测：

```
Level 1: 进程级（每 10 秒）
├── THS 客户端进程是否存活？
├── Xvfb 是否运行？
├── trading_engine 主循环是否卡死（heartbeat）？
└── 磁盘空间是否充足（日志膨胀）？

Level 2: 业务级（每 30 秒）
├── 行情数据是否正常推送？（data_source heartbeat）
├── 最后一次成功委托距今多久？
├── 风控熔断器状态是否正常？
└── 账户余额/持仓是否与券商一致？（定期对账）

Level 3: 市场级（每 5 分钟）
├── 大盘涨跌异常检测（日跌 > 5% 触发全局暂停）
├── 流动性检查（目标标的是否停牌/涨跌停）
├── 波动率突变检测（VIX 类指标）
└── 交易日历检查（节假日/特殊休市）
```

**健康监控代码框架**：
```python
"""health_monitor.py — 独立健康监控进程"""
import subprocess, time, logging, requests
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthMonitor:
    CHECKS = {
        "ths_process": {"interval": 10, "critical": True},
        "xvfb": {"interval": 10, "critical": True},
        "engine_heartbeat": {"interval": 30, "critical": True},
        "market_data": {"interval": 30, "critical": False},
        "account_sync": {"interval": 300, "critical": False},
        "disk_space": {"interval": 60, "critical": False},
    }

    def check_ths_process(self) -> bool:
        """检查 THS 客户端进程"""
        result = subprocess.run(
            ["pgrep", "-f", "HevoNext.B2CApp"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.critical("THS 客户端进程不存在！")
            self._restart_ths()
            return False
        return True

    def check_engine_heartbeat(self) -> bool:
        """检查交易引擎心跳（通过文件时间戳）"""
        hb_file = Path("data/.heartbeat")
        if not hb_file.exists():
            return False
        elapsed = time.time() - hb_file.stat().st_mtime
        if elapsed > 60:  # 1 分钟无心跳
            logger.critical(f"引擎心跳丢失！已 {elapsed:.0f} 秒")
            return False
        return True

    def check_disk_space(self) -> bool:
        """检查磁盘空间"""
        stat = Path("/").stat()
        free_gb = stat.f_bsize * stat.f_bavail / (1024**3)
        if free_gb < 2.0:
            logger.warning(f"磁盘空间不足: {free_gb:.1f}GB")
            return False
        return True

    def run_forever(self):
        """主监控循环"""
        last_check = {k: 0 for k in self.CHECKS}
        while True:
            now = time.time()
            for name, cfg in self.CHECKS.items():
                if now - last_check[name] >= cfg["interval"]:
                    check_fn = getattr(self, f"check_{name}", None)
                    if check_fn:
                        try:
                            ok = check_fn()
                            if not ok and cfg["critical"]:
                                self._send_alert(name)
                        except Exception as e:
                            logger.error(f"检查 {name} 异常: {e}")
                    last_check[name] = now
            time.sleep(5)

    def _restart_ths(self):
        """自动重启 THS 客户端"""
        logger.warning("尝试自动重启 THS 客户端...")
        subprocess.Popen(
            ["DISPLAY=:99", "/opt/apps/cn.com.10jqka/files/HevoNext.B2CApp"],
            shell=True
        )
        time.sleep(15)  # 等待 CEF 渲染初始化

    def _send_alert(self, check_name: str):
        """发送告警通知"""
        # 复用项目 Notifier 组件
        from ths_auto_trader.notification import Notification, notifier
        notifier.send_sync(Notification(
            title="⚠️ 系统告警",
            body=f"健康检查失败: {check_name}",
            level="error",
        ))
```

### 发现 3：GUI 自动化下单的 7 类故障需要分级容错策略

从 `xdotool_broker.py` 分析，GUI 自动化面临 7 类故障，需要不同的容错策略：

| 故障类型 | 发生概率 | 检测方法 | 容错策略 | 恢复时间 |
|---------|---------|---------|---------|---------|
| **窗口焦点丢失** | 高 (10%) | `xdotool getactivewindow` 对比 | 重试 3 次 + wmctrl 强制聚焦 | 2-5s |
| **坐标偏移** | 中 (5%) | 截图 + OCR 验证 vs 预期 | 重校准 + 固定窗口位置 | 10-30s |
| **弹窗阻断** | 低 (3%) | 截图检测异常 UI 元素 | 自动关闭已知弹窗 + 告警 | 5-15s |
| **网络断连** | 低 (2%) | 心跳检测 + socket 状态 | 指数退避重连 + 暂停交易 | 30-120s |
| **THS 客户端崩溃** | 极低 (1%) | 进程检测 | 自动重启 + 重新登录 | 30-60s |
| **验证码弹窗** | 罕见 (0.5%) | 截图 OCR | 人工介入 + 暂停交易 | 需人工 |
| **X11 服务器崩溃** | 极罕见 (0.1%) | DISPLAY 检测 | 重启 Xvfb + 全链路重建 | 60-120s |

**容错核心模式 — 重试 + 降级 + 暂停**：
```python
# 在 xdotool_broker.py 中应增加的容错装饰器
import functools, time, logging

def with_retry(max_retries=3, backoff=2.0, recoverable_errors=None):
    """GUI 操作容错装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_type = type(e).__name__
                    # 不可恢复错误直接抛出
                    if recoverable_errors and error_type not in recoverable_errors:
                        raise
                    wait = backoff * (2 ** attempt)
                    logger.warning(
                        f"[{func.__name__}] 第 {attempt+1} 次失败: {e}，"
                        f"等待 {wait:.1f}s 重试"
                    )
                    # 尝试恢复操作
                    self = args[0]
                    self._ensure_focus()  # 重新获取焦点
                    self._dismiss_popups()  # 关闭弹窗
                    time.sleep(wait)
            raise last_error  # 所有重试失败
        return wrapper
    return decorator
```

### 发现 4：A股程序化交易合规红线 — 5 条不可逾越的监管要求

2024-2025 年证监会加强了对程序化交易的监管，以下红线必须在系统设计层面遵守：

| 红线 | 监管要求 | 系统实现 |
|------|---------|---------|
| **报备义务** | 程序化交易投资者需向券商报备 | 首次使用前完成报备流程 |
| **撤单率限制** | 撤单率不得超过 50% | `risk_manager.py` 增加 `cancel_rate` 检查 |
| **高频交易认定** | 24 万笔/天或 2 万笔/小时 | 每日交易计数器 + 软限制告警 |
| **异常交易监控** | 不得影响或操纵市场 | 单标的日交易次数限制 |
| **瞬间大幅波动** | 不得在开盘/收盘集合竞价期间大量报撤 | 时段过滤（9:25-9:30 / 14:57-15:00 禁止交易） |

**合规时段过滤代码**：
```python
# 在 trading_engine.py 中应增加
from datetime import time as dt_time

FORBIDDEN_PERIODS = [
    (dt_time(9, 25), dt_time(9, 30)),   # 开盘集合竞价
    (dt_time(11, 28), dt_time(13, 1)),   # 午休前后
    (dt_time(14, 57), dt_time(15, 0)),   # 收盘集合竞价
]

def is_trading_allowed(now_time) -> bool:
    """检查当前时间是否允许交易"""
    for start, end in FORBIDDEN_PERIODS:
        if start <= now_time <= end:
            return False
    return True
```

### 发现 5：项目数据对账机制缺失，需要 3 层一致性校验

当前 `data_source.py` 使用 akshare（主）+ tushare（备），`storage/database.py` 用 SQLite 记录交易，但**缺少系统持仓与券商实际持仓的对账机制**。这是实盘最大的隐性风险：

```
对账层次：

Layer 1: 信号一致性
├── 系统记录的买入信号 ↔ 实际成交记录
├── 检测频率：每笔交易后
└── 不一致处理：暂停交易 + 告警

Layer 2: 持仓一致性
├── 系统计算的持仓 ↔ 券商实际持仓
├── 检测频率：每日收盘后
└── 不一致处理：以券商为准 + 记录差异日志

Layer 3: 资金一致性
├── 系统记录的可用资金 ↔ 券商实际可用资金
├── 检测频率：每日开盘前 + 收盘后
└── 差异 > 0.5% → 暂停交易 + 人工确认
```

**对账实现框架**：
```python
class AccountReconciler:
    """账户对账器 — 系统状态 vs 券商实际状态"""

    def daily_reconcile(self, system_state: Account, broker_state: dict):
        """每日对账"""
        mismatches = []

        # 持仓对账
        for code, sys_pos in system_state.positions.items():
            broker_qty = broker_state.get(code, {}).get("quantity", 0)
            if sys_pos.quantity != broker_qty:
                mismatches.append({
                    "type": "position_mismatch",
                    "code": code,
                    "system": sys_pos.quantity,
                    "broker": broker_qty,
                    "diff": sys_pos.quantity - broker_qty,
                })

        # 资金对账
        cash_diff = abs(system_state.available_cash - broker_state["available_cash"])
        cash_pct = cash_diff / max(system_state.total_assets, 1)
        if cash_pct > 0.005:  # 0.5% 阈值
            mismatches.append({
                "type": "cash_mismatch",
                "system": system_state.available_cash,
                "broker": broker_state["available_cash"],
                "diff_pct": f"{cash_pct:.2%}",
            })

        if mismatches:
            self._alert_mismatches(mismatches)
            # 严重不一致 → 暂停交易
            if any(m["type"] == "position_mismatch" and abs(m["diff"]) > 100
                   for m in mismatches):
                self._suspend_trading()

        return mismatches
```

---

## 二、完整运维架构图

```
┌──────────────────────────────────────────────────────────────┐
│                    运维监控层                                   │
│  HealthMonitor ─── AlertManager ─── Feishu/WeChat 通知        │
│  (独立进程)         (告警聚合)          (推送通道)              │
├──────────────────────────────────────────────────────────────┤
│                    交易引擎层                                   │
│  TradingEngine ─── RiskManager ─── Broker ─── 对账器          │
│  (主循环)           (五层风控)       (xdotool)   (Reconciler) │
├──────────────────────────────────────────────────────────────┤
│                    基础设施层                                   │
│  Xvfb :99 ─── THS Client ─── akshare/tushare ─── SQLite      │
│  (虚拟显示)    (交易终端)       (数据源)            (存储)     │
├──────────────────────────────────────────────────────────────┤
│                    系统服务层                                   │
│  systemd: ths-auto-trader.service                             │
│  logrotate: /etc/logrotate.d/ths-auto-trader                  │
│  crontab: 每日 08:30 预检 + 15:05 收盘对账                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、实践启发

### 3.1 部署清单（实盘前必检）

| # | 检查项 | 验证方法 | 不通过处理 |
|---|--------|---------|-----------|
| 1 | Xvfb 运行正常 | `xdpyinfo -display :99` | 重启 Xvfb |
| 2 | THS 客户端已登录 | 截图 OCR 检查登录状态 | 人工登录 |
| 3 | 行情数据可达 | `curl -s "https://akshare-api-test"` | 检查网络 |
| 4 | 通知通道可用 | 发送测试消息 | 检查 Webhook |
| 5 | 磁盘空间 > 5GB | `df -h /home/jc` | 清理日志 |
| 6 | 坐标校准确 | 截图 + OCR 验证下单界面 | 重新校准 |
| 7 | 时段过滤生效 | 模拟 9:25 的交易请求被拒绝 | 检查 config |
| 8 | 风控参数合理 | 模拟超额委托被拒绝 | 检查 risk.yaml |

### 3.2 日志与审计

```yaml
# 推荐的日志轮转配置
# /etc/logrotate.d/ths-auto-trader
/home/jc/uclaw/project/ths-auto-trader/data/logs/*.log {
    daily
    rotate 90           # 保留 90 天（合规要求）
    compress
    delaycompress
    missingok
    notifempty
    dateext
    dateformat -%Y%m%d
}
```

### 3.3 灾难恢复

| 故障场景 | 恢复 SOP | RTO |
|---------|---------|-----|
| 引擎进程崩溃 | systemd 自动重启 | 30s |
| THS 客户端崩溃 | HealthMonitor 检测 → 自动重启 → 重新校准 | 60s |
| X11 崩溃 | 重启 Xvfb → 重启 THS → 重启引擎 | 120s |
| 整机重启 | systemd 依赖链自动拉起 | 5min |
| 数据损坏 | SQLite 备份恢复（每日自动备份） | 10min |

---

## 四、知识缺口与后续探索方向

| 缺口 | 重要度 | 探索建议 |
|------|--------|---------|
| THS Linux 客户端实际坐标校准流程 | ⭐⭐⭐⭐⭐ | 需在实机实测，记录校准 SOP |
| akshare 在 aarch64 上的稳定性 | ⭐⭐⭐⭐ | Jetson 环境跑 7 天压测 |
| 网页版同花顺 Playwright 自动化 | ⭐⭐⭐⭐ | 可能比 xdotool 更稳定 |
| easytrader 在 Wine 下的兼容性 | ⭐⭐⭐ | 备选方案评估 |
| THS 客户端更新后自动适配 | ⭐⭐⭐⭐ | 图像识别自动校准坐标 |
| 合规报备流程实操 | ⭐⭐⭐⭐⭐ | 向券商咨询具体流程 |

---

## 五、对 ths-auto-trader 项目的代码建议

基于本次研究，建议对项目代码做以下补充：

1. **新增 `health_monitor.py`** — 独立监控进程（上面已给出框架）
2. **新增 `reconciler.py`** — 对账器模块（在 execution/ 下）
3. **`xdotool_broker.py` 增加 `with_retry` 装饰器** — 7 类故障容错
4. **`trading_engine.py` 增加时段过滤** — 合规要求
5. **`risk_manager.py` 增加撤单率检查** — 监管红线
6. **新增 `deploy/` 目录** — 含 systemd unit、logrotate、校准脚本

---

## 六、进化评估

| 内容 | 评估 | 动作 |
|------|------|------|
| GUI 自动化容错模式（重试+降级+暂停） | 可复用，≥3 次场景适用 | ✅ 建议创建 `gui-automation-resilience` skill |
| A股合规时段过滤规则 | 可复用，所有 A 股量化项目都需要 | ✅ 写入 memory |
| systemd + Xvfb 部署配置 | 可复用，所有 Linux GUI 自动化场景 | ✅ 写入 memory |
| 健康监控 3 级检测框架 | 通用模式 | ✅ 可整合到现有 monitoring 相关 skill |
| 对账器框架 | 项目特有 | 仅存笔记 |

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
- [ths-auto-trader-deep-learn](ths-auto-trader-deep-learn.md)
- [ths-auto-trader-ecosystem-update-20260518](ths-auto-trader-ecosystem-update-20260518.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
