# QuadRF — 开源 4×4 MIMO 相控阵 SDR 开发套件

> 来源：https://github.com/open-space-sdr/main (467★, C 主导)
> 组织：Scale RF (open-space-sdr)
> Crowd Supply 即将上线：https://www.crowdsupply.com/scale-rf/quadrf
> 日期：2026-08-14

---

## 一、项目定位

**QuadRF 是一个模块化 4×4 MIMO 软件定义无线电（SDR）瓦片**，集成树莓派 5 + Lattice ECP5 FPGA，开箱即用做实时 RF 相机——将 SDR 探索从传统时域/频域扩展到**空间域**。

核心理念：**让相控阵技术民主化**，从航空航天级设备变成黑客友好的桌面开发平台。

- 单块 QuadRF = 完整的 4 通道相控阵开发平台
- 多块拼接 = 平方米级相控阵（如 MoonRF 240 天线设计）
- 波束成形计算分布在每块瓦片的 FPGA 上，可级联扩展

---

## 二、硬件规格

### RF 性能

| 参数 | 规格 |
|------|------|
| 通道数 | 4 RX / 4 TX 全双工相干通道 |
| 频率范围 | 4.9 ~ 6.0 GHz（C 波段） |
| 带宽 | 每天线 40 MHz |
| 发射功率 | 每天线 1W（4 × SiGe 功率放大器） |
| 天线 | 4 个可更换圆极化贴片天线模块 |
| 极化 | 接收 RHCP/LHCP 可切换，发射 RHCP |

### 计算与处理

| 组件 | 型号/说明 |
|------|----------|
| 主控 | **树莓派 5**（板载 Linux 计算与控制） |
| FPGA | **Lattice ECP5** (LFE5U-45F-7BG256I) — 分布式 DSP + 波束成形 |
| 上变频 | Analog Devices MAX2850（4 通道上变频混频器） |
| 下变频 | Analog Devices MAX2851（4 通道下变频混频器） |
| 数据通路 | RF FPGA ↔ Pi 5 之间高吞吐 MIPI 接口 |

### 物理参数

| 项目 | 参数 |
|------|------|
| 尺寸 | 15 × 11 × 4 cm (5.9 × 4.3 × 1.6 in) |
| 重量（瓦片+天线） | 35 g |
| 重量（全套含三脚架） | 670 g |
| 外壳 | 3D 打印磁吸外壳 |
| 三脚架 | 可变形为移动手柄 + 智能手机 AR 支架 |

### 连接与供电

- USB 3.0 / 千兆以太网 / Wi-Fi / HDMI
- 可选 Mobile Pack：21700 锂电池组，Rx 5~6 小时 / 全 Tx 3~4 小时

---

## 三、软件架构

### 开源分层模型

| 层 | 开源状态 | 许可证 |
|----|---------|--------|
| **软件/驱动/应用** | ✅ 100% 开源 | GPLv2/GPLv3 |
| **天线/机械设计** | ✅ 开源 | CC BY-SA 4.0 |
| **FPGA** | ✅ 用户可编程 | OpenOCD / JTAG |
| **RF 核心** | ❌ 专有 | 源码可查看（调试/研究），不可复制制造 |

### 目录结构

```
open-space-sdr/main/
├── Applications/           # 应用示例
│   ├── NTSC_Decode/        # NTSC 视频解码
│   ├── NearField/          # 近场扫描
│   └── SpatialRF/          # 空间域 RF 可视化（核心应用）
├── CLI/                    # 命令行工具
│   └── jtag/               # FPGA JTAG 编程
├── Drivers/                # Linux 内核驱动
│   ├── csi/                # MIPI CSI 接收驱动
│   └── dsi/                # MIPI DSI 发送驱动
├── Firmware/               # 固件
│   ├── arm_QEC/            # ARM QEC（数字预失真/校准）
│   └── teensy/             # Teensy 控制器固件
├── GUI/                    # Web RF 可视化界面
│   ├── app.py              # Flask/Web 后端
│   ├── static/             # 前端资源
│   └── templates/          # HTML 模板
├── Hardware/               # 硬件设计文件
│   ├── OpenEMS/            # OpenEMS 电磁仿真
│   ├── Patch/              # 贴片天线设计
│   └── QuadRF_Antenna/     # QuadRF 天线 PCB
├── Services/               # systemd 服务
│   ├── install.sh          # 一键安装
│   ├── quadrf-gui.service  # Web GUI
│   ├── soapysdr-server.service  # SoapySDR 远程
│   └── load-quadrf.service # 驱动加载
├── SoapySDR/               # SoapySDR 驱动（C++）
│   ├── MipiDevice.cpp/hpp  # MIPI 设备接口
│   ├── NEON.cpp            # ARM NEON SIMD 加速
│   ├── Farrow.hpp          # Farrow 结构分数延迟滤波器
│   └── Registration.cpp    # SoapySDR 注册
└── OpenOCD/                # FPGA 编程配置
    ├── board/
    └── interface/
```

### 语言分布

| 语言 | 代码量 | 占比 | 用途 |
|------|--------|------|------|
| C | 6.85 MB | 93.5% | FPGA 比特流/RF 核心 DSP |
| C++ | 196 KB | 2.7% | SoapySDR 驱动 |
| Makefile | 136 KB | 1.8% | 构建系统 |
| HTML | 76 KB | 1.0% | Web GUI |
| MATLAB | 22 KB | 0.3% | 电磁仿真 |
| Python | 11 KB | 0.2% | Web 后端/脚本 |

---

## 四、核心应用场景

### 4.1 RF 增强"视觉"（RF Camera）

30 fps 实时可视化 RF 环境：
- 定位房间内 WiFi 设备的物理位置
- 追踪天空中的无人机信号
- 可视化其他无线发射源

> 机器人可以像用 LiDAR 一样用 QuadRF 获取周围无线信标和接入点的实时空间感知。

### 4.2 波束成形 MIMO

- 4 个相干收发器实现真 4×4 MIMO
- 自动波束成形最大化 SNR
- 从移动无人机/气球流式传输 HD 视频
- 点对点链路、点对多点架构、空间 mesh 网络原型

### 4.3 RF 诊断工具

- 可视化设备辐射方向
- 测试外壳对信号的影响
- 发射探测信号测量空间响应（全双工）
- 表征阴影、吸收、反射、材料效应

### 4.4 可扩展阵列（MoonRF）

单块 QuadRF 是 4×4 阵列，但设计为**可级联的构建块**：

| 配置 | 天线数 | 应用 |
|------|--------|------|
| 1 块 QuadRF | 4×4=16 | 桌面开发/教学 |
| 多块拼接 | 可变 | 中型阵列 |
| MoonRF 设计 | 240 天线 | 平方米级相控阵研究 |

### 4.5 移动 AR 可视化

三脚架变形为移动手柄，集成智能手机支架：
- 手机摄像头与阵列对齐
- 实时 AR 叠加 RF 信号到现实场景
- 户外移动扫描

---

## 五、技术深度解析

### 5.1 为什么选 C 波段 (4.9~6.0 GHz)

| 原因 | 说明 |
|------|------|
| WiFi 6E 邻近 | 5.8 GHz WiFi 频段覆盖 |
| 无人机图传 | 大量消费级无人机用 5.8 GHz |
| 小型天线 | 频率越高天线越小（λ/2 ≈ 2.6cm） |
| 圆极化贴片 | C 波段圆极化贴片天线成熟 |

### 5.2 波束成形的分布式计算

传统相控阵需要中心计算单元做波束成形——天线越多，计算越集中。

QuadRF 的创新：**每块瓦片的 ECP5 FPGA 独立做本块 4 通道的波束成形**，然后只传递波束成形后的数据给 Pi 5。级联多块时，计算自然分布，无需中心瓶颈。

### 5.3 MIPI 数据通路

Pi 5 与 RF FPGA 之间用 MIPI（原本为手机摄像头/显示屏设计的接口）做高吞吐数据传输：
- MIPI CSI（Camera Serial Interface）用于 RF 数据接收
- MIPI DSI（Display Serial Interface）用于控制信号发送
- 复用现有树莓派硬件接口，零额外芯片

### 5.4 Farrow 分数延迟滤波器

SoapySDR 驱动中的 `Farrow.hpp` 是波束成形的关键组件——通过分数延迟实现精确的相位对齐：

```
Farrow 结构 → 多项式插值 → 任意分数延迟 → 相干波束成形
```

### 5.5 ARM NEON 加速

`NEON.cpp` 利用树莓派 5 (Cortex-A76) 的 NEON SIMD 指令加速实时 DSP 运算。

---

## 六、开源策略分析

### 混合模型：保护核心 + 开放生态

| 层级 | 策略 | 原因 |
|------|------|------|
| 软件全开 | GPLv2/GPLv3 | 吸引开发者社区，生态锁定 |
| 天线/机械开 | CC BY-SA 4.0 + 专利契约 | 允许 DIY 复制天线，防御专利诉讼 |
| FPGA 可编程 | 完全解锁 | 让用户自定义 DSP |
| RF 核心闭源 | 专有（源码可查不可制） | 保护 4×4 MIMO SDR 低成本的核心 IP |

> Scale RF 提供了**防御性专利契约**（royalty-free defensive patent covenant），允许社区制作天线衍生品而不被起诉专利——这在硬件开源项目中很少见。

---

## 七、对你的技术借鉴价值

| 维度 | 借鉴点 |
|------|--------|
| **嵌入式 SoC 通信** | MIPI CSI/DSI 复用做 RF 数据通路——Pi 5 ↔ FPGA 高速通信范例 |
| **分布式 DSP** | 每块瓦片独立 FPGA 计算 → 级联扩展的架构思路 |
| **SDR 驱动开发** | SoapySDR C++ 驱动模板（Registration/MipiDevice/NEON） |
| **ARM NEON 加速** | 嵌入式实时 DSP 的 SIMD 优化参考 |
| **FPGA + SDR** | ECP5 + MAX2850/MAX2851 相干收发架构 |
| **波束成形算法** | Farrow 分数延迟滤波器的工程实现 |
| **Web 可视化** | Flask + 前端的实时 RF 可视化（SpatialRF） |
| **相控阵理论** | OpenEMS 仿真 + 贴片天线设计的完整参考 |

---

## 八、竞品对比

| 维度 | QuadRF | HackRF One | PlutoSDR | USRP B210 |
|------|--------|-----------|----------|-----------|
| 通道数 | **4×4 MIMO** | 1×1 | 1×1 (2×2 AD9361) | 2×2 |
| 相控阵 | ✅ 原生 | ❌ | ❌ | ❌ |
| 板载计算 | **Pi 5 + ECP5** | 无 | ARM A9 | 无 |
| 频率 | 4.9-6.0 GHz | 1-6000 MHz | 70-6000 MHz | 70-6000 MHz |
| 带宽 | 40 MHz | 20 MHz | 56 MHz | 56 MHz |
| Tx 功率 | **1W × 4** | 15 mW | 70 mW | 100 mW |
| 价格 | ~$300-500 (预估) | $300 | $200 | $1200 |
| 开源程度 | 混合（软件全开） | 全开 | 部分开 | 全开 |

## 相关笔记

- [Flix ESP32 四旋翼飞控项目](./2026-08-14-Flix-ESP32四旋翼飞控项目.md) — 嵌入式开源硬件姊妹项目
- [Orbien Rust 内网穿透工具](./2026-08-14-Orbien-Rust内网穿透工具.md) — Rust 网络工具对照
