# 同花顺自动交易系统 2026.05 技术动态更新

> 深度研究笔记 | 2026-05-19 | proactive-learn phase

---

## 核心发现

### 发现 1：MiniQMT 生态持续完善，xtquant 已支持 Python 3.13

**关键更新**:
- `xtquant` 250516.1.1 版本已上架 PyPI，支持 Python 3.6-3.13
- 但 Python 3.13 下 `xtdata.download_sector_data()` 存在卡住 bug，需降级到 2024 API (`client.down_all_sector_data()`)
- **Python 版本推荐**: 3.9/3.10/3.11/3.13 均可，**避免 3.12**（pkgutil 依赖问题），3.14 生态不完善
- Streamlit 不支持 Python 3.14

**新功能 (xtquant 250516 版本)**:
- 银证转账 API
- 北交所交易支持
- 下载板块数据 API 变更（需注意兼容性）

**架构要点**:
```
完整版 QMT (XtItClient.exe)  → 机构级，功能全面
   ↓ 简化版
极简版 MiniQMT (XtMiniQmt.exe) → 交易网关，Python 可外部调用
   ↓ Python 接口
xtquant = xtdata + xttrader
   ├─ xtdata: 行情数据（历史+实时）
   └─ xttrader: 交易执行
```

### 发现 2：QMT vs PTrade 定位清晰化，散户量化生态成熟

| 维度 | QMT | PTrade |
|------|-----|--------|
| 定位 | 专业量化玩家开发工具 | 散户友好策略执行器 |
| 开发 | Python + VBA，完全自定义 | 聚宽语法，模板化 |
| 数据源 | 支持通达信/同花顺/聚宽等外部数据 | 大部分券商仅 tushare |
| 隐私 | 策略本地运行 | 云端运行 |
| 编程门槛 | 高（需 Python 熟练） | 低（参数配置即可） |
| 量化类型 | 高频套利/ML模型均可 | 网格/趋势/条件单 |
| 佣金 | 部分券商低至万1 | 类似 |

**关键选择因素**:
- **QMT/MiniQMT**: 需要外部数据源、策略隐私、高频策略 → 选 QMT
- **PTrade**: 聚宽语法经验、轻度量化、不想写太多代码 → 选 PTrade
- **MiniQMT 限制**: 少部分券商完整支持，需绑定 MAC 地址，部分不支持虚拟机

### 发现 3：AI Agent + 量化交易融合加速

**pywencai + 同花顺问财** 简易量化系统架构：
```
同花顺问财 → pywencai (pip install) → 股票筛选
   ↓
apscheduler 定时任务 → 工作日 9:28 自动执行
   ↓
钉钉机器人 → 信号推送
```

这是**零交易接口**的轻量方案，仅做选股+推送，适合策略验证期。`pywencai` 是免费的 iFinD 替代品。

**腾讯 CodeBuddy Code** — AI 编程工具用于量化策略生成，降低编程门槛。国内 Claude 替代方案。

---

## 技术细节

### xtquant 安装与兼容性

```bash
# PyPI 安装（推荐）
pip install xtquant

# 版本: 250516.1.1
# Python: 3.6 - 3.13
# ⚠️ 3.13 下 download_sector_data() 有 bug
```

```python
# Python 3.13 兼容 workaround
import xtquant.xtdata as xd

# ❌ Python 3.13 下会卡住
# xd.download_sector_data()

# ✅ 使用旧 API
from xtquant.xtdata import client
client.down_all_sector_data()
```

### pywencai 问财数据自动化

```python
import pywencai

# 筛选条件（自然语言）
result = pywencai.get(
    '连续3天涨停，流通市值小于50亿，非ST',
    query_type='stock'
)
# 返回 DataFrame，包含股票代码、名称、各项指标
```

### Tick 数据下载限制

- **时间段限制**: 部分券商仅允许 9:00-16:00 下载 tick 数据
- **数据服务商差异**: 不同券商 tick 数据提供商不同
- **建议**: 盘后统一下载 + 本地缓存

---

## 实践启发

### Skill 更新建议

1. **xtquant 兼容性矩阵**: 补充 Python 3.13 bug 和 workaround 到 ths-auto-trader Skill
2. **pywencai 新增**: 作为免费数据源加入方案矩阵（替代 iFinD）
3. **QMT vs PTrade 选型指南**: 可独立为决策树 Skill
4. **问财简易量化**: pywencai + apscheduler + 钉钉，最小可用系统

### 对现有架构的影响

- **xtdata bug** 影响自动数据下载流程，需加入 fallback 逻辑
- **pywencai** 可替代部分 iFinD 功能，降低成本
- **MiniQMT MAC 绑定**限制远程部署方案，需确认具体券商策略

---

## 知识缺口

1. **xtquant Python 3.13 bug 修复时间线** — 是否有 PR 或 issue 跟踪
2. **pywencai 稳定性** — 问财接口反爬策略变化频率
3. **MiniQMT 各券商支持度对比表** — 哪些券商完整支持、哪些有限制
4. **PTrade Python API 深度** — 是否支持自定义策略开发
5. **QMT 算法交易 API** — TWAP/VWAP 实现方式
6. **银证转账 API 实战** — 250516 版新增，需 Windows 环境验证

---

*生成时间: 2026-05-19 | Phase: proactive-learn | 字数: ~2500*

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
- [ths-jqktrader-ecosystem-update-20260518](ths-jqktrader-ecosystem-update-20260518.md)
- [stock-analysis-system](../stock-analysis-system.md)
- [tdx-quant-trader](../tdx-quant-trader.md)
