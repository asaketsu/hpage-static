# 问财选股工具使用笔记

> 基于 pywencai（同花顺问财 Python SDK），安装于 2026-04-06
> 数据来源：同花顺官方，免费，无需 cookie

## 安装

```bash
pip install pywencai --break-system-packages
```

## 快速使用

```python
import pywencai

# A股选股（自然语言）
df = pywencai.get(query='ROE大于15%且市盈率低于20的股票')

# 指定类型
df = pywencai.get(query='涨幅前10', query_type='stock')      # A股
df = pywencai.get(query='涨幅前10', query_type='fund')       # 基金
df = pywencai.get(query='涨幅前10', query_type='hkstock')    # 港股
df = pywencai.get(query='涨幅前10', query_type='usstock')    # 美股
df = pywencai.get(query='溢价率小于10%', query_type='conbond') # 可转债
df = pywencai.get(query='主力合约', query_type='futures')    # 期货
```

## 支持的查询类型（query_type）

| 类型 | 参数 | 说明 |
|------|------|------|
| A股 | stock（默认） | 5000+股票全市场筛选 |
| 指数 | zhishu | 大盘/行业/概念指数 |
| 基金 | fund | 公募基金（股票型/债券型/混合型） |
| 港股 | hkstock | 港股通标的 |
| 美股 | usstock | 纳斯达克/纽交所 |
| 可转债 | conbond | 含溢价率、正股、评级 |
| 期货 | futures | 主力合约/品种 |
| 保险 | insurance | 保险产品 |
| 新三板 | threeboard | 新三板企业 |
| 理财 | lccp | 银行理财产品 |

## 常用查询示例

### 选股
- "ROE大于15%且市盈率低于20的非ST股票"
- "连续3日涨停，非一字板"
- "北向资金连续5日净流入，市值大于100亿"
- "换手率大于10%且涨幅大于5%"
- "主力净流入排名前20"

### 行业/板块
- "今日概念板块涨跌幅排名前20"
- "人工智能板块成分股"
- "申万一级行业涨跌幅排名"

### 财务指标
- "营收增速超30%且净利润增速超20%"
- "资产负债率低于30%且ROIC大于10%"

### 事件驱动
- "今日涨停原因及封单额"
- "近一周解禁市值排名"
- "业绩预告超预期的股票"

### 其他
- "可转债溢价率小于10%且剩余期限大于2年"
- "今日IPO新股" / "待申购新股"

## 注意事项

1. **数据延迟**：非Level-2行情，约15分钟延迟，不适合高频交易
2. **非交易时间**：周末/节假日数据为最近交易日收盘数据
3. **返回格式**：DataFrame，列名带中括号日期（如"成交量[20260403]"）
4. **Cookie**：部分高级查询可能需要cookie（登录 iwencai.com → F12 → Network → 复制Cookie）
5. **pywencai依赖**：PyExecJS（已安装，无AVX问题）

## 相关笔记
- [OpenClaw-4-things-persistent-tasks](2026-04-10-OpenClaw-4-things-persistent-tasks.md)
- [stock-trading-discipline-washout](2026-04-11-stock-trading-discipline-washout.md)
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
- [tdx-quant-trader](tdx-quant-trader.md)
