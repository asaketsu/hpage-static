# 机器学习因子选股：XGBoost / LightGBM 实战指南

## 核心概念

### 什么是因子选股
因子选股（Factor-based Stock Selection）是量化投资的核心方法。通过提取股票的多维度特征（因子），利用统计或机器学习模型预测未来收益，构建投资组合。

### 传统 vs ML 方法对比

| 维度 | 传统多因子 | ML因子 |
|------|-----------|--------|
| 因子合成 | 线性加权 (IC加权/等权) | 非线性组合 |
| 因子挖掘 | 人工设计 | 自动发现交互效应 |
| 过拟合风险 | 低 | 高（需要严格验证） |
| 表达能力 | 线性关系 | 非线性 + 交互 |
| 可解释性 | 高 | 中等（SHAP可补救） |

### A股常用因子分类
- **价值因子**: PE、PB、PS、EV/EBITDA
- **成长因子**: ROE同比、营收增速、净利润增速
- **技术因子**: 动量、反转、波动率、换手率
- **质量因子**: 资产负债率、现金流/净利润、应收账款周转
- **情绪因子**: 北向资金、融资融券余额、分析师评级调整
- **另类因子**: 龙虎榜、大宗交易、限售解禁

## XGBoost 因子选股实战

### 数据准备流水线
```
原始行情 → 因子计算 → 标准化 → 去极值 → 缺失值处理 → 标签生成
```

### 关键步骤

#### 1. 标签构造（最关键）
```python
# 方式一：收益率分类
labels = (future_return > median_return).astype(int)  # 二分类
labels = pd.qcut(future_return, 5, labels=False)      # 5分类

# 方式二：超额收益
excess_return = stock_return - benchmark_return
labels = (excess_return > 0).astype(int)
```

#### 2. 特征工程
```python
import pandas as pd
import numpy as np

def compute_factors(df):
    """计算常用因子"""
    factors = pd.DataFrame()
    
    # 价值因子
    factors['pe_ttm'] = df['market_cap'] / df['net_profit_ttm']
    factors['pb'] = df['market_cap'] / df['net_asset']
    
    # 动量因子（过去N日收益率）
    for period in [5, 10, 20, 60]:
        factors[f'mom_{period}'] = df['close'].pct_change(period)
    
    # 波动率因子
    factors['vol_20'] = df['close'].pct_change().rolling(20).std()
    factors['vol_60'] = df['close'].pct_change().rolling(60).std()
    
    # 换手率因子
    factors['turnover_20'] = df['turnover'].rolling(20).mean()
    factors['turnover_ratio'] = df['turnover'] / df['turnover'].rolling(20).mean()
    
    # 量价背离
    factors['price_vol_corr'] = df['close'].rolling(20).corr(df['volume'])
    
    return factors
```

#### 3. XGBoost 模型训练
```python
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

# 时间序列交叉验证（不能用普通CV！）
tscv = TimeSeriesSplit(n_splits=5)

params = {
    'objective': 'binary:logistic',  # 或 'multi:softprob'
    'max_depth': 6,                   # 控制过拟合
    'learning_rate': 0.05,
    'n_estimators': 500,
    'subsample': 0.8,                 # 行采样
    'colsample_bytree': 0.8,          # 列采样
    'reg_alpha': 0.1,                 # L1正则
    'reg_lambda': 1.0,                # L2正则
    'min_child_weight': 50,           # 防止过拟合关键参数
    'early_stopping_rounds': 50,
}

model = xgb.XGBClassifier(**params)
model.fit(X_train, y_train, 
          eval_set=[(X_val, y_val)],
          verbose=False)
```

#### 4. LightGBM 优势
```python
import lightgbm as lgb

params = {
    'objective': 'binary',
    'metric': 'auc',
    'max_depth': 6,
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_data_in_leaf': 50,
    'lambda_l1': 0.1,
    'lambda_l2': 1.0,
}

# LightGBM 优势：
# 1. 训练速度快 3-5x（直方图加速）
# 2. 内存占用少
# 3. 类别特征原生支持（行业、板块）
# 4. 更好的并行效率
```

### 模型评估指标
```python
# IC (Information Coefficient) — 因子预测力核心指标
def calc_ic(predictions, actual_returns):
    """计算Rank IC（Spearman相关系数）"""
    from scipy.stats import spearmanr
    ic, pvalue = spearmanr(predictions, actual_returns)
    return ic

# ICIR = IC均值 / IC标准差（越大越好，>0.5 为优秀）
# 分层回测：将股票按预测分5组，看多空收益差
```

## ⚠️ 实战避坑指南

### 常见过拟合陷阱
1. **未来数据泄漏**: 因子计算时用了未来数据（最致命）
2. **标签与特征重叠**: 动量因子和标签使用了重叠时间窗口
3. **幸存者偏差**: 只用了当前存续的股票，忽略已退市
4. **时序交叉验证错误**: 用了随机打乱的 CV（必须用 TimeSeriesSplit）
5. **特征数量过多**: >100个特征几乎必过拟合

### 防过拟合 Checklist
- [ ] 所有因子计算只用历史数据
- [ ] 严格时间序列切分（train/val/test）
- [ ] 测试集完全不可见，只最后评估一次
- [ ] IC 月度序列稳定性检查（不能忽高忽低）
- [ ] 分层回测每组单调递增/递减
- [ ] 换仓成本模拟（A股双边千三+冲击成本）
- [ ] 样本外走查至少 1 年

### 与 ths-auto-trader 集成思路
1. **因子计算层**: 独立模块，从同花顺获取行情数据计算因子
2. **模型预测层**: 每日收盘后批量预测，输出 Top-N 股票池
3. **信号输出层**: 将预测结果转为买入/卖出信号
4. **风控层**: 仓位控制、止损、最大回撤限制
5. **执行层**: 通过 xdotool 自动下单

## 技术栈推荐
```
数据源: 同花顺 iFinD / Tushare / AKShare
因子计算: Alphalens / 自研
模型: LightGBM（首选）/ XGBoost
回测: backtrader / 自研轻量框架
部署: ths-auto-trader 内嵌
```

## 参考
- 《主动投资组合管理》— Grinold & Kahn
- 《量化投资：策略与技术》— 丁鹏
- WorldQuant Alpha 101 因子库
- OpenAlpha: 开源 A 股因子挖掘框架

## 相关笔记
- [[2026-04-02-股票投资GitHub投研工作流]]
- [[2026-03-31-张雪峰推荐的6个计算机专业]]
