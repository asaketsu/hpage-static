# MCU 低功耗设计 — Stop/Standby 模式与唤醒源

> 探索日期 2026-10-17 | 兴趣等级 L2（PLC/单片机/嵌入式）| 来源 8 篇（EET-China 模式对比 / 腾讯云实测心得 / 乐鑫官方 ESP-IoT-Solution / 野火 F103 实战指南 / ST 社区 L0 详解 / CSDN 引脚漏电流实战）| 前序：JTAG-SWD 调试(10-14)、RISC-V MCU(10-14)

## 摘要

MCU 低功耗设计 = 模式选型（功耗/唤醒源/状态保持三角权衡）+ 唤醒源配置 + 漏电流治理三件事。STM32 走"运行→睡眠→停止→待机"四级阶梯：Stop 保留 SRAM/寄存器、任意 EXTI 唤醒、唤醒后可"秒回现场"；Standby 电流最低但 1.2V 域断电，唤醒=复位重跑。ESP32 走 deep sleep + ULP 协处理器路线，官方实测 timer/EXT 唤醒低至 ~6µA。最大的实战教训：**决定最终功耗的往往不是模式本身，而是引脚/外设漏电流治理**——同一块板，GPIO 配置与调试器处理不当可以从 0.75µA 劣化到 mA 级（千倍差距）。

## 关键发现

**1. STM32 四级模式阶梯与三维权衡**

- 睡眠（Sleep）：仅关内核时钟，片上外设照常跑。任一中断可唤醒，唤醒零延迟（L0 实测 0.36µs）。是"最耗电的低功耗模式"——适合外设干活 CPU 等中断的场景
- 停止（Stop）：所有时钟停止，但 1.2V 域部分电源保持 → 内核寄存器+SRAM 内容保留，唤醒后从 WFI/WFE 之后继续执行。唤醒源=任一外部中断（EXTI，注意不是任一中断）。唤醒后系统时钟自动切回 HSI（F1=8M/F4=16M），必须软件重配回 HSE+PLL
- 待机（Standby）：1.2V 域完全断电，SRAM 内容丢失，所有 IO 进高阻。唤醒源仅 WKUP 引脚（PA0）上升沿 / NRST 复位 / 重新上电 / RTC / IWDG。唤醒后等同复位，从 boot 重跑——靠读 PWR_FLAG_WU 区分唤醒来源
- 实测功耗（正点原子教程口径）：F1 Stop ~20+µA / Standby ~5µA；F4 Stop ~350µA / Standby ~2.2µA。L 系做得好可到 0.75µA（见发现 3）

**2. 唤醒源架构：STM32 与 ESP32 的两条路线**

- STM32 分层收窄：Sleep=任一中断 → Stop=任一 EXTI → Standby=仅 WKUP/复位/RTC，层级越深唤醒源越少
- ESP32 deep sleep 唤醒源：定时器 / ext0（单个 RTC IO 达到指定电平）/ ext1（多个 RTC IO 组合电平）/ touchpad / ULP 协处理器。唤醒后同样走复位 boot，但先执行 RTC fast memory 里的 wake stub（esp_wake_deep_sleep）再进 bootloader——相当于给了"复位前钩子"
- ESP32 官方实测：Station 正常工作 ~115mA；deep sleep + timer/EXT 唤醒 ~6µA；touchpad 唤醒 ~36µA（文档正文另载 ~50µA 量级）；ULP 周期采集（10Hz）呈周期尖峰
- 无线保活档位（ESP32 独有）：modem-sleep（DTIM 听信标）1~15mA；light-sleep（CPU/外设暂停、WiFi/BLE 可唤醒）0.8~2mA；deep sleep ~5µA

**3. 漏电流治理清单——实测数字说话（腾讯云博主 STM32L 实测）**

- 未用 GPIO 全部设为模拟输入：最小系统 3.3V 下 Stop 电流 0.75µA；不配置（默认浮空输入）则电流大幅劣化
- 三个易漏引脚：除 PA/PB/PC 各 16 个外，还有 **PD2、PH0、PH1**——漏配任何一个功耗都下不来
- 预留 9 个 EXTI 唤醒口后实测 3.5µA——唤醒源数量与功耗直接交换
- 悬空的中断引脚必须配内部上拉/下拉；已接外设的引脚配浮空即可
- 调试器未关：PH0 案例中 Stop 电流 800µA，根因是 `HAL_DBGMCU_DisableDBGSleepMode()` 没调用——**测功耗前必关 DBGMCU**
- ADC 残留：采样过一次后再休眠，电流 1.8mA vs 不采 38µA（差 47 倍）→ `HAL_ADC_Stop_IT(&hadc)` + `__HAL_RCC_ADC1_CLK_DISABLE()`
- 通讯外设用 `HAL_UART_MspDeInit()` 一类 MspDeInit 关闭（关中断+清寄存器+引脚转 GPIO 模式）
- Standby 反噬陷阱：IO 全高阻后，外接器件引脚可能倒灌大电流，外设多的板子 Standby 反而比 Stop 更耗电

**4. Stop 唤醒后时钟恢复（必做动作，漏了=主频悄悄掉到 HSI）**

```c
// 野火 SYSCLKConfig_STOP：唤醒后时钟三步恢复
RCC_HSEConfig(RCC_HSE_ON);
while (RCC_GetFlagStatus(RCC_FLAG_HSERDY) == RESET);   // 等 HSE 就绪
RCC_PLLCmd(ENABLE);
while (RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET);   // 等 PLL 就绪
RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK);              // 切回 PLL
```

- 通讯外设同理：MspDeInit 过的 UART 唤醒后仅 Init 不够，必须重开 `HAL_NVIC_EnableIRQ(USARTx_IRQn)`，否则收发静默失灵
- Standby 判源：`PWR_GetFlagStatus(PWR_FLAG_WU)` 区分待机唤醒复位 vs 上电/引脚复位

**5. 模式选型决策树（工程案例驱动）**

- 要"唤醒秒回现场、状态不丢" → Stop（RAM/寄存器保留，EXTI 唤醒）
- 要"极致省电 + 单按键开关机" → Standby（手机电源键模型：持续供电只为监视 PA0 上升沿）
- 关机充电显示案例：Standby+PA0 复用（充电口 RC 脉冲也走 PA0）需长短按判别、软件难分；**正解=Stop + 双 EXTI**（按键一脚、充电检测一脚），电平天然可分
- 无线连接不能断 → modem/light sleep；睡眠中还要采集 → ULP
- 电池寿命估算：寿命 = 电池容量 / 平均电流；平均电流 = Σ(各状态电流×时间占比)

**6. ESP32 ULP 协处理器——"睡眠中干活"的独门武器**

- Deep sleep 期间 ULP（超低功耗协处理器）可运行汇编程序：采集 ADC/片上温度存 RTC slow memory，满足条件才唤醒主核——数据放 RTC 慢存，主核醒来直接读走
- 官方 ulp_monitor 模块做了 C 封装：`ulp_add_adc_monitor` / `ulp_add_temperature_monitor` 设阈值，`ulp_monitor_start` 设频率
- 三场景映射：定时上报（timer 唤醒）/ 传感器自带 GPIO 触发（ext0/ext1）/ 传感器无触发但需轮询（ULP）——第三类对传感器要求最低
- 应用参考：语音助手用 ULP 做唤醒词预检，仅增 ~10µA 量级，避免频繁唤醒主 CPU

## 与现有工作的关联（对工作的价值）

- **ASC 云台项目（ESP32-CAM）**：1012 供电塌陷复位循环案例的反面印证——低功耗治理本质是电源树治理；未来电池供电版本可直接套 ESP32 三档（modem/light/deep）选型树，串口烧录断连场景在 deep sleep 下同样存在（需 wake stub 或外部复位进入下载模式）
- **机器人传感器节点**：DUCK 遥测/姿态记录节点若做成电池版，"定时采集+异常 GPIO 触发"双唤醒源架构（Stop+RTC+EXTI）是现成答案；CTRL 板电池监测用 ADC 唤醒后必须 Stop_IT+关时钟，否则休眠电流 1.8mA 级直接吃掉电池
- **前序笔记衔接**：JTAG/SWD(10-14) 提到 DAP 在 Standby 下无法烧录——本文闭环了原因（1.2V 域断电，调试域不供电）；RISC-V MCU(GD32) 的 PMU 模式命名与 STM32 大同小异，可平移本框架
- **嵌入式 AI 笔记系（TinyML 两篇）**：TinyML 端侧推理的"占空比工作"模型（采集→推理→上报→睡）正是本篇 Stop/deep-sleep 循环的载体——平均电流公式决定纽扣电池能否撑过一年

## Actionable Insights（行动建议）

- P0 · STM32 电池项目上电即查五件套：未用 GPIO 全模拟输入（含 PD2/PH0/PH1）｜悬空 EXTI 内部上下拉｜进 Stop 前 MspDeInit 通讯外设+关 ADC 时钟｜测功耗前 `HAL_DBGMCU_DisableDBGSleepMode()`｜唤醒后 SYSCLKConfig_STOP+重开 NVIC 中断
- P1 · 选型口诀：秒回现场用 Stop，极致省电按键唤醒用 Standby，无线保活用 modem/light，睡眠采集用 ULP——跨系不可直接套数字（F1/F4/L 系差异巨大，L4 Stop2 已到 1µA 级）
- P1 · Standby 项目状态迁移：依赖 RAM 的业务数据必须搬进 RTC 备份寄存器/RTC slow mem，唤醒后按 PWR_FLAG_WU 走恢复分支
- P2 · 功耗验收用数字门槛：万用表串测，deep sleep 档 <5~10µA、Stop 档（L 系）<5µA 为合格线；超标先查引脚配置与 DBGMCU，再查外设残留

## 关键风险与盲点

- 来源级别标注：0.75µA/3.5µA/800µA/1.8mA 系腾讯云博主 2020 单方实测（社区复现级，方向可信、数值仅供参考）；F1/F4 数字出自正点原子教程（厂商手册未详列，二手口径）；ESP32 6µA/36µA/115mA 出自乐鑫官方文档（高可信）
- 跨系列数字禁直接对标：本文 F1/F4/L0 口径不适用 L4/G0/U5（Stop1/Stop2 细分、PSM 特性差异大）——选型时必须查对应系列 datasheet 的功耗表
- Standby 的高阻 IO 对外部器件的影响因板而异，多外设板可能"更低功耗模式反而更耗电"，需整机实测
- 量产产线注意：Standby/Stop 下部分调试器行为异常（野火：DAP 待机态无法下载），产测工位需设计唤醒-烧录时序

## 一页速查

> - Stop：RAM 保留 / 任意 EXTI 唤醒 / 唤醒续跑 / 唤醒后必须重配时钟（HSI→HSE+PLL）
> - Standby：RAM 丢失 / 仅 WKUP(PA0)+RTC+复位 / 唤醒=复位 / IO 高阻防倒灌
> - 睡眠：外设全跑 / 任一中断 / 零延迟 / 最"耗电的低功耗"
> - ESP32 deep sleep ~6µA（timer/ext），touchpad ~36µA，light sleep 0.8-2mA，工作 115mA
> - 漏电流三巨头：浮空 GPIO（→模拟输入）、DBGMCU 未关（800µA）、ADC 残留（1.8mA）
> - 电池寿命 = 容量 / 平均电流；唤醒源数量与休眠电流直接交换（9 个 EXTI 口 = 0.75→3.5µA）

## 待深入

- STM32L4/U5 的 Stop2 与 PSM（可扩展状态保持）实测数字
- modem-sleep DTIM 周期与路由器 beacon 的匹配调优（1~15mA 区间怎么压）
- 专业功耗剖析工具（Nordic PPK2 / Joulescope）的 µs 级电流波形用法

## 来源列表

1. STM32几种低功耗模式的实现与差别 — 电子工程专辑 · https://www.eet-china.com/mp/a98380.html
2. STM32低功耗控制心得体会（实测 0.75µA/3.5µA/800µA/1.8mA）— 腾讯云开发者社区 · https://developer.cloud.tencent.com/article/1599572
3. ESP32 低功耗方案概述 — 乐鑫 ESP-IoT-Solution 官方文档 · https://espressif-docs.readthedocs-hosted.com/projects/espressif-esp-iot-solution/zh-cn/latest/low_power_solution/esp32_lowpower_solution.html
4. 电源管理—实现低功耗（SYSCLKConfig_STOP/待机例程）— 野火 STM32 库开发实战指南 · https://doc.embedfire.com/mcu/stm32/f103badao/std/zh/latest/book/Power.html
5. STM32L0系列控制器低功耗模式详解（五模式排名法）— ST 意法半导体中文社区 · https://shequ.stmicroelectronics.cn/thread-633290-1-1.html
6. STM32低功耗模式有哪些 — MCU加油站 EETrend · https://mcu.eetrend.com/content/2021/100114476.html
7. STM32 学习13 低功耗模式与唤醒 — 知乎 · https://zhuanlan.zhihu.com/p/694111094
8. 豆包语音助手低功耗设计：ESP32-S3 省电模式实践 — CSDN · https://blog.csdn.net/2501_93893659/article/details/153704354
