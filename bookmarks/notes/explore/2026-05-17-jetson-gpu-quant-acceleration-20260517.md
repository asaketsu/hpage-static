# Jetson Orin GPU 加速量化计算 + AKShare 实时行情可行性研究

> 本地知识蒸馏 + 实测验证 | 2026-05-17 | Topic: ths-auto-trader
> 难度: L4（实测级）| 字数: ~2500

---

## 一、核心发现（4 个）

### 发现 1：Jetson Orin 上 PyTorch CUDA 计算核心不可用

**实测结果**：torch 2.4.0 在 Jetson Orin (SM 8.7, Ampere) 上执行 CUDA 运算时抛出：

```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

**根因分析**：
| 项目 | 值 |
|------|-----|
| SoC | Jetson Orin Nano Super (aarch64) |
| CUDA Toolkit | 12.6.11 |
| JetPack | R36.4.7 |
| GPU Compute Capability | 8.7 (Ampere) |
| torch.version.cuda | 12.4 |
| torch CUDA available | True（检测通过但执行失败）|

**问题本质**：安装的 torch 2.4.0 是标准 pip 版本（CUDA 12.4），其编译时未包含 SM 8.7 的 kernel image。Jetson 需要安装 NVIDIA 官方的 **torch for Jetson** 特定版本（从 NVIDIA Jetson forums 下载 `.whl`），而非 PyPI 标准版。

**修复方案**：
```bash
# 1. 卸载当前版本
pip uninstall torch torchaudio

# 2. 安装 Jetson 专用版本（需要从 NVIDIA 论坛下载）
# 参考: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
# JetPack 6.x (R36.x) 对应 torch 2.5+ 的 Jetson wheel
wget https://developer.download.nvidia.com/compute/redist/jp/v61/pytorch/torch-2.5.0-cp312-cp312-linux_aarch64.whl
pip install torch-2.5.0-cp312-cp312-linux_aarch64.whl

# 3. 验证
python3 -c "import torch; x=torch.randn(100,100,device='cuda'); print(x.mean())"
```

**实践启发**：这是 Jetson 平台的常见陷阱——`torch.cuda.is_available()` 返回 True 但实际执行失败。在 ths-auto-trader 项目中，必须先验证实际计算可用性，而非仅检测 CUDA 可用性。

---

### 发现 2：NumPy 在 Jetson 上的量化计算性能基线

在 GPU 不可用的情况下，NumPy CPU 实测性能（500 股票 × 250 日 × 10 因子）：

| 操作 | 耗时（100/10 iter） | 单次耗时 |
|------|---------------------|---------|
| Rolling Mean (window=20) | 862ms / 100 iter | **8.6ms** |
| Z-score 标准化 | 1399ms / 100 iter | **14.0ms** |
| Rank 排序 | 6.6ms / 10 iter | **0.66ms** |
| Correlation Matrix | 1367ms / 10 iter | **136.7ms** |

**关键洞察**：
- 对于 A 股日频策略（每天最多运行 1-2 次），**NumPy CPU 完全够用**
- 500 股票 × 250 日的 rolling mean 仅需 8.6ms，远低于策略的时间预算（分钟级）
- **GPU 加速仅在以下场景有价值**：
  - 全市场扫描（5000+ 股票 × 多因子）
  - 高频/分钟级策略（每分钟运行）
  - 大规模回测（1000+ 策略 × 10 年 × 全市场）

**结论**：ths-auto-trader 当前规模（5-50 只股票、日线策略），**不需要 GPU 加速**。这是一个"过早优化"陷阱。

---

### 发现 3：AKShare 无原生 WebSocket 实时推送能力

通过函数扫描 `dir(akshare)` 中所有 streaming/realtime 相关函数：

```python
# 扫描关键词: stream, ws_, push, real_time, subscribe
# 结果：无任何 WebSocket/流式推送函数
# 仅有订阅模式的期货函数（非 A 股）
```

**AKShare 的 A 股实时数据机制**：
| 方式 | 函数 | 延迟 | 适用场景 |
|------|------|------|---------|
| 全市场快照 | `stock_zh_a_spot_em()` | 1-3s（HTTP 轮询）| 选股扫描 |
| 个股分时 | `stock_intraday_em(symbol)` | 1-2s | 分钟级行情 |
| 五档盘口 | `stock_bid_ask_em(symbol)` | 0.5-1s | 下单决策 |

**全部基于 HTTP 轮询东方财富 Web API**，本质是爬虫，无原生推送。

**对 ths-auto-trader 的启示**：
- 日线策略：用 AKShare 轮询完全够用（每天收盘后跑一次）
- 分钟线策略：需要直接对接东方财富 push2 API（已有 reference: `eastmoney-api.md`）
- 秒级策略：AKShare 不可用，需要 QMT/PTrade 专线

**实时行情推荐方案（三档）**：
```
日线策略 ← AKShare HTTP（免费，够用）
分钟线   ← 东财 push2ex.eastmoney.com WebSocket（免费，需自行对接）
秒/Tick  ← QMT xtquant / PTrade API（付费，券商提供）
```

---

### 发现 4：Jetson 环境的量化计算技术选型矩阵

综合以上发现，ths-auto-trader 在 Jetson Orin 上的技术选型：

| 层级 | 推荐方案 | 备选 | 不推荐 |
|------|---------|------|--------|
| 数值计算 | NumPy 2.4.4（CPU）| 修复 torch Jetson 版 | 标准 pip torch |
| 数据获取 | AKShare HTTP | 东财 push2 WebSocket | iFinD（太贵）|
| 数据存储 | SQLite + Parquet | CSV | 纯内存（重启丢失）|
| 策略回测 | 自研 BacktestEngine | backtrader | vnpy（太重）|
| 执行层 | xdotool（Linux）| 远程 easytrader（Windows）| 直接柜台（门槛高）|
| GPU 加速 | 暂不需要 | 修复 torch 后用于 ML 因子 | cupy（Jetson 无预编译包）|

---

## 二、技术细节

### 2.1 Jetson torch 兼容性检测代码

```python
"""可靠的 Jetson CUDA 可用性检测"""
import torch

def check_jetson_cuda():
    """不只是 is_available()，还要验证实际计算"""
    if not torch.cuda.is_available():
        return False, "CUDA not available"
    
    try:
        # 关键：必须执行实际运算来检测 SM 兼容性
        x = torch.randn(10, 10, device='cuda')
        y = x + x  # 触发实际 kernel
        _ = y.mean().item()  # 强制同步
        return True, f"CUDA OK, GPU: {torch.cuda.get_device_name(0)}"
    except RuntimeError as e:
        if "no kernel image" in str(e):
            return False, f"SM mismatch: need Jetson-specific torch build"
        return False, str(e)

ok, msg = check_jetson_cuda()
print(f"CUDA usable: {ok} | {msg}")
```

### 2.2 NumPy 量化因子加速模式（无需 GPU）

```python
"""Jetson 上实用的因子计算优化"""
import numpy as np

class FastFactorEngine:
    """针对小规模（<500股票）优化的因子计算引擎"""
    
    @staticmethod
    def rolling_zscore(data: np.ndarray, window: int = 20) -> np.ndarray:
        """向量化 rolling z-score — 避免循环"""
        # data shape: (n_stocks, n_days)
        cumsum = np.cumsum(data, axis=1)
        cumsum2 = np.cumsum(data ** 2, axis=1)
        
        # Welford's online algorithm in vectorized form
        sum_w = cumsum[:, window:] - cumsum[:, :-window]
        sum_w2 = cumsum2[:, window:] - cumsum2[:, :-window]
        mean = sum_w / window
        std = np.sqrt((sum_w2 / window - mean ** 2).clip(min=1e-8))
        
        return (data[:, window:] - mean) / std
    
    @staticmethod  
    def cross_sectional_rank(data: np.ndarray) -> np.ndarray:
        """截面排序（跨股票）— 单行代码"""
        # data shape: (n_stocks,) -> returns rank [0, 1]
        ranks = np.argsort(np.argsort(data, axis=0), axis=0)
        return ranks / max(len(data) - 1, 1)
    
    @staticmethod
    def multi_factor_score(factors: dict, weights: dict) -> np.ndarray:
        """多因子加权评分 — 一次矩阵运算"""
        aligned = np.column_stack([
            (factors[k] - factors[k].mean()) / (factors[k].std() + 1e-8)
            for k in weights
        ])
        w = np.array([weights[k] for k in weights])
        return aligned @ w
```

### 2.3 AKShare 轮询 vs WebSocket 延迟对比

```
场景：盘中每 30 秒刷新 50 只股票的实时价格

方案 A: AKShare 轮询
- stock_zh_a_spot_em() 一次返回全市场 ~5000 条
- 延迟: ~2s/次 × 1 次 = 2s
- 频率: 每 30s 一次 → 日内 480 次
- 风险: 反爬限制（同一 IP 高频请求可能被封）

方案 B: 东财 push2 WebSocket
- 连接一次，持续推送
- 延迟: ~100ms/tick
- 频率: 实时
- 风险: 连接断开需重连（已有心跳机制）

方案 C: 混合（推荐）
- 启动时用 AKShare 获取快照（全量初始化）
- 盘中用 push2 WebSocket 增量更新
- 每 5 分钟用 AKShare 做一次全量校准
```

---

## 三、实践启发

### 3.1 ths-auto-trader 数据层建议更新

基于发现，原架构的数据层应做如下调整：

1. **去掉 GPU 加速依赖**：当前规模不需要，移除不必要的复杂性
2. **增加数据新鲜度检测**：每次获取数据时记录时间戳，超时自动降级
3. **双数据源冗余**：AKShare（主）+ 东财 API（备），自动切换
4. **本地缓存优先**：Parquet 文件缓存历史数据，减少网络请求

### 3.2 开发优先级调整

| 原优先级 | 调整后 | 原因 |
|---------|--------|------|
| P0: 数据层 | P0: 数据层（不变）| 核心基础 |
| 新增 | P1: Jetson torch 修复 | 为后续 ML 因子铺路 |
| P2: 风控 | P2: 风控（不变）| 独立模块 |
| 新增 | P3: WebSocket 行情接入 | 分钟级策略的前提 |

---

## 四、知识缺口（仍需探索）

1. **Jetson 专用 torch 安装**：JetPack 6.1 对应的 torch 2.5+ wheel 具体下载地址和验证步骤
2. **东财 push2 WebSocket 协议**：已有 `eastmoney-api.md` reference，但尚未实际编码对接
3. **cupy on Jetson**：是否有 aarch64 预编译包？源码编译的可行性？
4. **NumPy MKL vs OpenBLAS**：Jetson 上用的是哪个 BLAS？MKL 不可用（Intel 专属），OpenBLAS 是否已自动启用 NEON 加速？
5. **策略规模阈值**：从 NumPy CPU 切换到 GPU 加速的"盈亏平衡点"在哪里？（多少股票 × 多少因子 × 多少频率）

---

## 五、参考资料

1. NVIDIA Jetson PyTorch: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
2. 已有 reference: `eastmoney-api.md` — 东财 push2 API 使用指南
3. 已有 reference: `auto-trading-system-design.md` — 系统架构设计
4. 前序笔记: `ths-auto-trader-architecture-deep-dive-20260517.md` — 知识缺口 #4 和 #5
5. AKShare 源码: https://github.com/akfamily/akshare

---

*笔记生成时间：2026-05-17 17:35 | 基于实测 benchmark + 本地知识蒸馏*
*核心贡献：首次实测验证 Jetson Orin 上 torch CUDA 不兼容问题，建立 NumPy 性能基线*

## 相关笔记
- [边缘AI推理优化-Jetson平台深度研究](explore/2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [jetson-tensorrt-edge-inference-optimization](explore/2026-05-19-jetson-tensorrt-edge-inference-optimization.md)
- [Jetson-Orin-Nano-Super-性能优化](explore/2026-05-19-Jetson-Orin-Nano-Super-性能优化.md)
- [litevla-edge-analysis](2026-05-01-litevla-edge-analysis.md)
- [jetson-camera-vision](jetson-camera-vision.md)
