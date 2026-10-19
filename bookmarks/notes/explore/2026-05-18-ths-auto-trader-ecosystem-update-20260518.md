# THS Auto Trader 生态更新笔记 (2026.05)

> 主题: ths-auto-trader | 类型: 技术动态更新 | 日期: 2026-05-18

---

## 核心发现

### 1. ths_trade: 新一代 WEB API 服务框架（GitHub skyformat99/ths_trade）

ths_trade 是一个值得关注的新项目，与 easytrader/jqktrader 的 UI 自动化路线不同：

- **WEB API 服务框架**：提供 HTTP API 接口，支持远程调用
- **交易下单自动排队**：多策略并发下的队列管理，解决了 easytrader 的并发冲突问题
- **多策略支持 + 实时回报查询**：策略层面的隔离和回报追踪
- **智能按钮定位**：升级版模拟点击，比传统坐标定位更稳定
- **多年实盘稳定运行**：生产验证过的项目
- **支持通达信**：不仅限同花顺，覆盖更多券商客户端

**对比 easytrader/jqktrader**：

| 维度 | easytrader | jqktrader | ths_trade |
|------|-----------|-----------|-----------|
| 自动化方式 | pywinauto UI | pywinauto + OCR | WEB API + 智能按钮 |
| 并发支持 | 差（单线程） | 改进 | 好（内置队列） |
| 远程调用 | 需额外封装 | 需额外封装 | 原生 HTTP API |
| 多策略 | 不支持 | 不支持 | 原生支持 |
| 部署复杂度 | 低 | 中 | 中 |

**实践启发**：ths_trade 的 WEB API + 队列架构与现有 Skill 中已设计的 RemoteQMTBroker HTTP 中转方案思路一致，但 ths_trade 是开箱即用的。建议在 Skill 中补充 ths_trade 作为"中频实盘 HTTP API 方案"的新选项。

### 2. jqktrader: easytrader 现代替代方案

jqktrader 针对 easytrader 的痛点做了全面升级：

- **升级 pywinauto 框架**：解决了 easytrader 长期存在的兼容性问题
- **补全关键依赖**：easytrader 很多依赖已过时，jqktrader 重新整理
- **验证码识别集成**：内置 OCR 验证码处理，减少手动干预
- **API 兼容 easytrader**：迁移成本低，可 drop-in replacement

**关键代码模式**：
```python
import jqktrader

# API 兼容 easytrader，迁移简单
user = jqktrader.use('universal_client')
user.connect(r'C:\同花顺\xiadan.exe')
user.buy('162411', price=0.5, amount=100)
```

### 3. pywencai: 同花顺问财数据自动化

pywencai 是问财平台的自动化数据获取工具：

- **自动获取问财选股结果**：从"i问财"平台提取选股结果
- **Python 接口**：编程化获取，支持批量
- **免费**：不需要 iFinD 付费 API
- **适用场景**：选股策略回测、因子筛选

```python
import pywencai

# 获取问财选股结果
result = pywencai.get('连续3天涨停的股票')
```

**实践启发**：pywencai 可作为 iFinD API 的免费替代方案，适合个人研究阶段。但稳定性和数据完整性不如 iFinD。

### 4. iTick: 免费实时行情 API

2025-2026 年行情数据领域的新玩家：

- **永久免费套餐**：基础实时行情（报价、涨跌幅、成交量）
- **毫秒级延迟**：WebSocket 实时推送
- **RESTful + WebSocket 双协议**
- **覆盖 A 股/港股/美股/外汇/加密货币**
- **15 年历史 K 线数据**

**对 THS 生态的影响**：iTick 可以作为 iFinD 的免费替代，用于策略开发和回测数据源。但需要注意数据精度和可靠性。

### 5. SuperMind 实盘直通（同花顺官方）

同花顺 SuperMind 平台的最新动态：
- **实盘直通功能**：策略开发完直接对接实盘
- **云端运行**：无需本地 Windows 环境
- **Python 支持**：完整的 Python 策略开发环境
- **数据 + 交易一体化**：解决了数据源和交易通道的割裂问题

---

## 技术细节

### ths_trade WEB API 架构

```
交易策略/信号源 → HTTP POST → ths_trade API Server → 交易队列 → 同花顺客户端 → 交易所
                                      ↓
                               WebSocket 推送回报
```

关键特性：
- **请求排队**：多个策略同时发单时自动排队，避免冲突
- **回报推送**：成交/委托状态通过 WebSocket 实时推送
- **Token 认证**：API 级别的安全控制

### jqktrader vs easytrader 技术差异

| 模块 | easytrader | jqktrader |
|------|-----------|-----------|
| UI 框架 | pywinauto (旧版) | pywinauto (最新) |
| 表格读取 | WMCopy 剪贴板 | WMCopy + OCR 备选 |
| 验证码 | 需额外集成 | 内置 OCR |
| 维护状态 | 低活跃 | 活跃维护 |
| 依赖健康 | 多处过时 | 全部更新 |

---

## 实践启发

1. **方案矩阵更新**：ths_trade 填补了"中频实盘 + HTTP API"的空白，应加入 Skill 方案选择矩阵
2. **EasyUp AI Agent 选股**：三角色辩论框架（猎手/账房/守夜人）适合 Hermes delegate_task 实现
3. **pywencai + iTick 组合**：免费数据链路，适合策略研究阶段
4. **合规注意**：ths_trade 和 jqktrader 都是 UI 自动化方案，本质上仍受同花顺客户端限制

---

## 知识缺口

1. **ths_trade 实测性能**：下单延迟、稳定性、并发上限需实测
2. **jqktrader 验证码识别率**：OCR 方案的实际成功率
3. **pywencai 反爬机制**：问财平台的请求频率限制
4. **iTick 数据精度**：与 Wind/iFinD 对比的数据准确性
5. **SuperMind 实盘 API 规范**：官方文档是否公开
6. **ths_trade Linux 部署可行性**：服务端是否可跑在 Linux，仅 Windows 端跑同花顺客户端

---

*生成时间: 2026-05-18 19:10 | 自动学习 Phase 3*

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
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
