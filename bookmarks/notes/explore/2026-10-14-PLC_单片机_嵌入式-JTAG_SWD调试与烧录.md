# JTAG/SWD 调试与烧录 — 从协议底层到救砖实战

> 探索日期 2026-10-14 | 兴趣等级 L2（PLC/单片机/嵌入式）| 来源 8+ 篇（Arshon 实战指南 / cnsee DAP 深解 / EET-China 协议帧 / pyOCD 官档 / STM32 RDP 安全研究）| 前序：嵌入式应用层笔记 60+ 篇，调试接口层首篇

## 摘要

JTAG 与 SWD 是嵌入式调试与烧录的两条主干道。JTAG（IEEE 1149.1）是通用边界扫描标准，4+1 线、可链式挂多器件；SWD 是 ARM CoreSight 专有双线替代，引脚省一半、速度更高，是 Cortex-M 事实标准。烧录的本质 = 调试器通过 DAP（Debug Access Port）的 MEM-AP 把 flash 映射为内存写入，再跑厂商 flash 算法。救砖三板斧 = connect under reset + 降速 + mass-erase；安全面 = STM32 RDP 三级读保护（L2 永久锁死不可逆，慎用）。

## 关键发现

**1. JTAG vs SWD 的本质分工**

- JTAG：TAP 状态机（TCK/TMS/TDI/TDO/±TRST），同一链可挂 MCU+FPGA+PMIC，需配置各器件 IR 长度；边界扫描能力是制造测试刚需（BSDL 文件驱动，不 boot 固件即可测开短路）
- SWD：SWDIO（双向，ARM 建议 100KΩ 上拉）+ SWCLK 两线，访问 DAP→MEM-AP→任意内存映射地址；SWO 单线输出 ITM/printf 跟踪
- 引脚复用：TMS=SWDIO、TCK=SWCLK，两协议共享焊盘，多数芯片上电默认 JTAG、靠魔数序列切换

**2. JTAG→SWD 切换魔数（协议层最硬核细节）**

调试器要在 TMS/TCK 上输出：>50 位 1 → 16 位 `0111100111100111`(MSB) → >50 位 1。此序列禁用 JTAG-DP 激活 SW-DP——意味着只用 SWD 两线也能完成切换，无需额外引脚。

**3. SWD 事务三段式（8+3+33 位）**

```
Host: [请求包 8bit] Start|APnDP|RnW|A[2:3]|Parity|Stop|Park
      ↓ (Trn 转换周期 — 双方都不驱动, SWDIO 换向)
Target: [ACK 3bit] 100=OK / 010=WAIT / 001=FAULT
      ↓ (Trn)
Data: [33bit] 32位数据 + 奇偶校验
```

- SWDIO 每次换向插入 1 bit 转换时间（turn-round），双方悬空靠上拉
- ACK=WAIT 时读数据要走 DP 的 RDBUFF 寄存器取回
- DP 寄存器组：IDCODE（M3/M4 读 0x2BA01477，M0+ 读 0x0BC11477——连上先读这个验链路）/ CTRL-STAT（上电请求 CDBGPWRUPREQ+CSYSPWRUPREQ）/ SELECT（APSEL[31:24]+APBANKSEL[7:4]）/ ABORT（清 STICKYERR 等）

**4. 烧录的真相：没有"烧录协议"，只有内存写**

probe（pyOCD/OpenOCD + CMSIS-DAP）通过 MEM-AP 的 CSW/TAR/DRW 三寄存器组合访问系统总线：TAR 设地址→DRW 读写数据→CSW 控制自增与位宽。Flash 烧录 = 调试器先把厂商 flash loader 算法塞进 RAM 执行，把 flash 编程包装成内存写。这也是"上帝视角"的基础——cnsee 实测直接改 SP/PC/LR 寄存器让芯片执行任意地址函数（`exec 栈基址 SP PC LR 参数`）。

**5. 调试器生态三档 + 救砖三板斧**

- J-Link：贵、快、全（ETM 高端跟踪），克隆版有被 SEGGER 固件反制风险
- ST-Link：STM32 生态零成本（Nucleo 板载即可当编程器），V2J21.S4 以下固件有坑
- CMSIS-DAP/DAPLink：开源标准，pyOCD+OpenOCD 双原生支持，¥10-20 即入
- 救砖三板斧：① connect under reset（nRESET 拉低时 attach——固件早期把 SWD 引脚重映射成 GPIO 时的唯一解）② 降速到 100-400kHz ③ mass-erase 清 option bytes 锁
- 新板 bring-up 铁律：首速 100-400kHz → 稳了再升 MHz；烧录中断电 = 砖，供电要有保持电容

## STM32 RDP 读保护三级（烧录/安全交叉点）

- L0（option byte=0xAA）：出厂态，SWD 全开放
- L1（0xBB）：flash 不可读但可调试 RAM/外设；回退 L0 会触发 flash 全擦（mass-erase）——这是"解锁"的代价
- L2：SWD/JTAG/边界扫描永久禁用，**不可逆**，工厂量产锁死用
- 安全研究（USENIX WOOT'17 + Anvil 电压毛刺注入）：RDP L1 存在初始化不全的读取侧信道，定制 SWD 调试器可偶发读出受保护数据；L2 也有电压故障注入绕过的公开案例——RDP 是防抄板门槛不是密码学边界

## 与现有工作的关联

- **ASC 自瞄 V3.2（ESP32-CAM）**：当前烧录走 USB 串口 bootloader，遇到 1012 那种"供电塌陷复位循环"时串口烧录会反复断连——ESP32 的救援通道是 JTAG（GPIO9-11 复用引脚或原生 USB-JTAG），配合 `esptool --before no_reset` + 外部稳压供电。⚠️ ESP32 是 Xtensa/RISC-V 内核，**SWD/DAP 不适用**，本文协议细节仅适用于 ARM Cortex-M 系（STM32/GD32/CH32/N32 等）
- **硬件选型工作流**：STM32 系（如未来 U585 控制板）调试器采购决策已可闭环——开发用 ST-Link（板载零成本），量产/CI 用 CMSIS-DAP + pyOCD 脚本化（JSON 配置+并行烧录+板号校准数据写入一条龙）
- **飞机设计企业背景**：JTAG 边界扫描（IEEE 1149.1）是工业 PCB ICT/FCT 制造测试的标准手段，BSDL 文件+链图属于制造工艺文件范畴

## Actionable Insights

1. 采购备件：CMSIS-DAP 调试器（¥10-20 DAPLink 版）入硬件备件盒，覆盖未来所有 Cortex-M 板（STM32/GD32）的调试与救砖
2. 固化救砖预案到 ASC 项目 docs：ESP32 供电复位循环场景 = 独立 5V 供电 + 串口重试 3 次 + 失败转 JTAG
3. pyOCD 量产脚本模式（flash+option bytes+板号写入+电流自检）可作为未来多板部署的标准产线脚本模板

## 关键风险与盲点

- SWD 仅限 ARM：ESP32（Xtensa/RISC-V）、RISC-V MCU（CH32V 系列）不走 DAP，各有自己的 debug module（RISC-V JTAG DTM）——标注来源：ARM 官方文档 vs 社区实测（cnsee/pyOCD 官档为官方验证级）
- J-Link 克隆版：SEGGER 固件更新会警告/拒绝克隆硬件，产线禁用克隆探针
- 调试器实时性代价：live watch 轮询过频会拖慢实时任务；halt 电机控制环可能瞬间打满执行器——安全相关固件必须带 halt handler 落安全态

## 一页速查

> **选型**：日常 STM32=ST-Link；通用+脚本化=CMSIS-DAP+pyOCD；高端跟踪=J-Link。**连线**：SWDIO/SWCLK/VTref/GND×2/nRESET 六线起步，VTref 必须接（probe 靠它定驱动电平）。**首连**：读 IDCODE 验链路 → 100-400kHz 起步 → connect under reset 防引脚重映射。**砖了**：拉 nRESET 上电 + 降速 + mass-erase（RDP L1 解锁代价=全擦）。**量产**：RDP L2 锁死前必须留签名解锁/安全 bootloader 通道，否则返修无门。

## 待深入

- RISC-V JTAG Debug Module（CH32V/GD32V 系的调试协议，与 ARM DAP 完全不同栈）
- SWO/ITM 实时跟踪实操（RTOS 任务级 printf 通道分配）
- OpenOCD 自定义 flash loader 编写（非标 flash 芯片场景）

## 来源列表

- Arshon Inc. — JTAG and SWD debugging techniques: a field guide（实战 bring-up/trace/产线，官方博客）
- cnsee.net/PicoXTools — 深入了解 ARM 调试访问端口 DAP（协议帧+DP/AP 寄存器+exec 实验，社区验证）
- EET-China — 一文搞懂 SWD 调试接口协议（帧结构速查，社区）
- pyOCD 官方文档 — Debug probes（探针兼容矩阵+ST-Link 固件版本坑，官方）
- OpenOCD 官方 User's Guide — Debug Adapter Configuration（官方）
- efton.sk STM32 Gotchas #54 — RDP 三级语义与 F1 系列写保护耦合（社区，深度实测）
- USENIX WOOT'17 — Shedding Too Much Light on MCU Firmware Protection（RDP L1 侧信道，学术）
- Anvil Secure — Voltage fault injection glitching STM32 RDP（红队实测）
- Stm32World Wiki — STM32 Readout Protection 实操截图（社区）
