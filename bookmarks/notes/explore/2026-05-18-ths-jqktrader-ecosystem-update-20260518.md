# THS Auto Trader 生态更新 2026-05-18：jqktrader 与新工具链

> 增量学习笔记 | 补充 ths-auto-trader skill 已有内容

---

## 一、核心发现：jqktrader — easytrader 的现代替代

### 发现 1：jqktrader 解决了 easytrader 的三大痛点

| 痛点 | easytrader 现状 | jqktrader 方案 |
|------|----------------|---------------|
| pywinauto 版本陈旧 | 旧版，兼容性问题 | 升级至最新版 |
| 验证码识别缺失 | 需手动处理 | 集成 Tesseract OCR |
| 依赖不完整 | 缺 pytesseract/pypiwin32 | 补全所有关键依赖 |

**项目地址**：https://gitcode.com/gh_mirrors/jq/jqktrader

**核心使用方式**（与 easytrader 高度兼容）：
```python
import jqktrader

user = jqktrader.use()
user.connect(
    exe_path=r'D:\同花顺软件\同花顺\xiadan.exe',
    tesseract_cmd=r'D:\Program Files\Tesseract-OCR\tesseract.exe'
)

# API 与 easytrader 几乎一致
user.buy('600519', price=1500, amount=100)
user.sell('000001', price=10.5, amount=200)
position_info = user.position
balance = user.balance
user.cancel_entrust(entrust_no='123456')
```

### 发现 2：同花顺 SuperMind 平台升级

SuperMind 量化平台新增功能：
- **多账户智能交易** — 算法交易 + 篮子交易
- **因子研究监控分析** — 支持因子和策略的实时监控
- **极速策略交易** — 任务自动化执行

### 发现 3：同花顺 API 套餐体系

CSDN 文章解析了同花顺 API 的套餐分层（免费版到定制版），关键信息：
- Python 程序调用 API 实现自动化交易的环境搭建指南已有更新
- 环境搭建 → 交易功能实现 → 系统部署与运维的完整链路

---

## 二、对 ths-auto-trader Skill 的更新建议

### 应更新的知识缺口

1. **jqktrader 已纳入方案矩阵** — 作为 easytrader 的现代替代方案，Python 3.8-3.10 兼容
2. **同花顺客户端 UI 变更持续** — 2026 年多个 Issue 反映界面变化影响 GUI 自动化
3. **同花顺 → QMT 对接** — 无需 Python 知识的图形化对接方案（抖音教程热门）

### 方案选择矩阵增量

| 场景 | 新增方案 | 优势 |
|------|---------|------|
| easytrader 稳定性不足 | jqktrader | pywinauto 升级 + OCR 集成 |
| 不懂 Python 的用户 | 同花顺→QMT 图形化对接 | 零代码，动态板块 |
| 机构级多账户 | SuperMind | 算法交易 + 篮子交易 |

---

## 三、注意事项

- jqktrader **不维护登录状态**，需手动登录后使用
- **不能保证 100% 操作成功率**，实盘需设置风控
- 推荐 Python 3.8-3.10 获得最佳兼容性
- jqktrader 保持与 easytrader API 的兼容性，**迁移成本低**

---

## 参考

| 来源 | URL |
|------|-----|
| jqktrader 深度解析 | https://blog.csdn.net/gitblog_01077/article/details/160791864 |
| jqktrader 选择理由 | https://blog.csdn.net/gitblog_00122/article/details/160791772 |
| jqktrader 实战指南 | https://blog.csdn.net/gitblog_00286/article/details/160791896 |
| SuperMind 平台 | https://quant.10jqka.com.cn/activity/mgo-management.html |

---

*笔记字数：约 1200 字 | 类型：增量生态更新*

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
- [ths-auto-trader-production-ops-20260517](ths-auto-trader-production-ops-20260517.md)
- [ths-auto-trader-qmt-xtquant-tick-strategy-20260518](ths-auto-trader-qmt-xtquant-tick-strategy-20260518.md)
- [ths-auto-trader-update-20260519](ths-auto-trader-update-20260519.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
