　　
# tdx-quant-trader

## 项目信息
构型类型：Python
功能标签：量化、Python

## 项目简介
　　# 通达信量化模拟交易系统 (tdx-quant-trader) 基于通达信 tdxquant (tqcenter.py) 封装的 Python 量化交易框架，支持模拟交易完整流程。 ## 功能特性 🔌 **连接管理**: 自动初始化/关闭，支持 with 语句 📊 **查询**: 资产/持仓/委托/实时行情 💰 **交易**: 买入/卖出/市价单/撤单 📈 **策略引擎**: 评分信号/网格/均值回归/动量突破 🛡️ **风控**: 单笔限额/日交易上限/止损止盈/持仓集中度 🔄 **代码格式兼容**: 自动转换 `sz000823` ↔ `000823.SZ` ## 项目结构 ``` tdx-quant-trader/ ├── README.md ├── requirements.txt ├── run.py                    ← 一键运行入口 ├── src/ │   ├── tdx_trader.py         ← 核心交易封装 (TdxTrader 类) │   └── strategies.py         ←


## 相关笔记
- [通达信tdxquant量化模拟交易封装](2026-04-24-通达信tdxquant量化模拟交易封装.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [stoc蒸馏-AI-Agent自学习量化交易系统](2026-04-30-stoc蒸馏-AI-Agent自学习量化交易系统.md)
- [MACD-KDJ共振策略](2026-05-08-MACD-KDJ共振策略.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [RSI布林带组合策略](2026-05-11-RSI布林带组合策略.md)
- [板块轮动资金流向分析](2026-05-11-板块轮动资金流向分析.md)
- [技术指标组合策略-multi-indicator](2026-05-12-技术指标组合策略-multi-indicator.md)
- [板块轮动-北向资金](2026-05-14-板块轮动-北向资金.md)
- [RSI布林带组合交易策略](2026-05-15-RSI布林带组合交易策略.md)
- [rsi-bollinger-strategy](explore/2026-05-06-rsi-bollinger-strategy.md)
- [技术指标组合策略-多指标确认](explore/2026-05-06-技术指标组合策略-多指标确认.md)
- [板块轮动与北向资金流向](explore/2026-05-06-板块轮动与北向资金流向.md)
- [MACD-KDJ共振策略-实战指南](explore/2026-05-09-MACD-KDJ共振策略-实战指南.md)
- [技术指标组合策略-多指标确认](explore/2026-05-09-技术指标组合策略-多指标确认.md)
- [MACD-KDJ共振策略](explore/2026-05-14-MACD-KDJ共振策略.md)
- [技术指标组合策略-多指标确认](explore/2026-05-14-技术指标组合策略-多指标确认.md)
- [板块轮动-北向资金](explore/2026-05-14-板块轮动-北向资金.md)
- [ths-auto-trader-xdotool-stability](explore/2026-05-16-ths-auto-trader-xdotool-stability.md)
- [动态止损策略对比](explore/2026-05-17-动态止损策略对比.md)
- [北向资金主力资金流向指标有效性验证](explore/2026-05-17-北向资金主力资金流向指标有效性验证.md)
- [实盘模拟vs真实交易技术差异](explore/2026-05-17-实盘模拟vs真实交易技术差异.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [MACD-KDJ共振](orphan/2026-05-15-MACD-KDJ共振.md)
- [stock-analysis-system](stock-analysis-system.md)
