# 嵌入式 Rust 实战：no_std 开发、RTIC 框架、ESP32 固件深度研究

> 📅 2026-05-19 | 🏷️ 嵌入式/Rust/no_std/RTIC/ESP32/Embassy/esp-hal
> 📎 来源: EDN/eettaiwan/FOSDEM 2026/rtic.rs/GitHub esp-rs/Reddit/rust-lang 论坛
> 📎 Topic: 嵌入式 | 兴趣队列探索

---

## 一、核心发现

### 发现1：esp-hal 1.0.0 Beta — ESP32 生态的 Rust 里程碑

2025 年 2 月，esp-rs 项目发布了 **esp-hal 1.0.0-beta**，这是 ESP32 裸机 Rust 开发的重大里程碑：

**支持的芯片系列（全覆盖）**：
| 芯片 | 架构 | 特点 | Rust 支持 |
|------|------|------|-----------|
| ESP32 | Xtensa LX6 | 经典款，双核 240MHz | ✅ 完整 |
| ESP32-S2 | Xtensa LX7 | USB OTG，安全启动 | ✅ 完整 |
| ESP32-S3 | Xtensa LX7 | AI 加速，摄像头，BLE 5 | ✅ 完整 |
| ESP32-C3 | RISC-V RV32IMC | 低功耗，高性价比 | ✅ 完整（原生 LLVM） |
| ESP32-C6 | RISC-V RV32IMAC | WiFi 6, Thread/Matter | ✅ 完整 |
| ESP32-C5 | RISC-V | WiFi 6 增强版 | ✅ 完整 |
| ESP32-H2 | RISC-V | 纯 Thread/Zigbee | ✅ 完整 |
| ESP32-C61 | RISC-V | 新一代入门 | ✅ 完整 |

**关键突破**：
- **no_std WiFi/BLE/ESP-NOW** 已可用（通过 esp-wifi/esp-radio crate，需 `unstable` feature）
- 实现 `embedded-hal 1.0` traits（统一的硬件抽象接口）
- 阻塞 + async 双模式 API（通过 `into_async()` 转换）
- 多核支持（ESP32/S3 双核可独立使用不同 driver）
- Espressif 官方支持（不是社区维护，是厂商级投入）

**意义**：以前 Rust on ESP32 只能做 blink，现在可以写完整的 WiFi + BLE 产品固件。

### 发现2：RTIC v2 — 硬件加速的实时并发框架

**RTIC（Real-Time Interrupt-driven Concurrency）** 是嵌入式 Rust 的两大并发框架之一，核心设计基于 **Stack Resource Policy (SRP)**：

**架构特性**：
- **非传统 RTOS**：没有软件内核，直接利用硬件中断控制器（NVIC/PLIC/CLINT）
- **静态优先级调度**：编译期计算资源天花板（ceiling），零运行时开销
- **编译期并发安全**：利用 Rust 所有权模型，编译器保证无死锁、无数据竞争
- **任务模型**：
  - **Hardware tasks**：绑定中断向量，由硬件触发
  - **Software tasks**：由代码 spawn，支持优先级
  - **Message passing**：任务间通过 `spawn` 传递数据

**支持架构**：
| 架构 | 后端 | 状态 |
|------|------|------|
| Cortex-M (ARM) | NVIC | ✅ 完全支持 |
| RISC-V PLIC+CLINT | 中断控制器 | ✅ 支持（ESP32-C3/C6） |
| RISC-V CLIC | 增强中断 | ⚠️ 实验性 |

**RTIC v2 的重大变化**：
- v2 本质上是 async executor：
  - 优先级 0 的 software task ≈ Embassy 的 Executor
  - 高优先级 software task ≈ Embassy 的 InterruptExecutor
- SRP lock 不可跨 `.await`（编译期强制）
- 支持 RISC-V 目标（ESP32-C3/C6 可直接用 RTIC）

### 发现3：Embassy — 异步嵌入式的新范式

**Embassy** 是 RTIC 的主要竞争者，采用纯 async/await 模型：

**核心差异对比**：
| 维度 | RTIC v2 | Embassy |
|------|---------|---------|
| **并发模型** | 中断优先级 + SRP | async/await executor |
| **学习曲线** | 陡（需理解 SRP） | 平缓（async/await 熟悉） |
| **调度保证** | 硬实时（硬件中断） | 软实时（协作调度） |
| **ESP32 支持** | ✅ RISC-V 变种 | ✅ 原生（esp-rtos 集成） |
| **网络协议栈** | 需自建 | 内置（embassy-net） |
| **USB 支持** | 需自建 | 内置（embassy-usb） |
| **BLE 支持** | 需自建 | 内置（trouble crate） |
| **代码量** | 少（宏驱动） | 中等 |
| **适合场景** | 硬实时控制、电机驱动 | IoT 设备、传感器网络 |

**Embassy 独有能力**：
- `embassy-boot`：轻量 bootloader + DFU（固件升级、掉电安全、试启动+回滚）
- `embassy-net`：async TCP/IP 协议栈（smoltcp 后端）
- `embassy-usb`：async USB 设备栈
- `trouble`：BLE 4.x/5.x Host 协议栈（支持 nRF52/ESP32/RP2040）
- `lora-rs`：async LoRa/LoRaWAN 协议栈

### 发现4：从 C 到 Rust 的固件迁移实战（FOSDEM 2026）

FOSDEM 2026 有一场专题演讲 **"From C to Rust on the ESP32: A Developer's Journey into no_std"**，分享真实迁移经验：

**迁移策略**：
1. **渐进式**：不是一次性重写，而是从外围驱动开始逐模块替换
2. **FFI 桥接**：C 和 Rust 代码通过 `extern "C"` 互操作，逐步替换
3. **工具链并行**：ESP-IDF (C) 和 esp-rs (Rust) 构建系统共存
4. **测试驱动**：每个替换的模块都有主机端单元测试（Rust 的 `#[test]` 在 host 上跑）

**关键教训**：
- `unsafe` 块应该小且集中（嵌入式 Rust 中不可避免，但要限制范围）
- Xtensa 目标需要 `espup` 安装自定义工具链（RISC-V 如 C3/C6 可直接用标准 Rust）
- WiFi/BLE 驱动尚不稳定，生产环境建议保守
- 社区生态在快速成长但尚未达到 C/ESP-IDF 的成熟度

---

## 二、技术细节

### 2.1 no_std 项目结构

一个完整的 ESP32 no_std Rust 项目结构：

```
my-esp32-firmware/
├── .cargo/
│   └── config.toml          # 目标三元组 + linker 配置
├── Cargo.toml
├── build.rs                 # 编译时生成链接脚本
├── memory.x                 # 内存布局定义
└── src/
    └── main.rs              # #![no_std] + #![no_main] 入口
```

**Cargo.toml 关键配置**：
```toml
[package]
name = "my-esp32-firmware"
version = "0.1.0"
edition = "2021"

[dependencies]
esp-hal = { version = "1.0.0-beta", features = ["esp32s3"] }
esp-backtrace = { version = "0.14", features = ["esp32s3", "panic-handler", "exception-handler"] }
esp-println = { version = "0.12", features = ["esp32s3"] }
critical-section = "1.2"

# 可选：Embassy async
embassy-executor = { version = "0.7", features = ["nightly"] }
embassy-time = "0.4"

[profile.dev]
opt-level = "s"    # 必须！无优化代码太大塞不进 Flash

[profile.release]
opt-level = "s"
lto = true         # 链接时优化，减小体积
```

**main.rs 骨架**：
```rust
#![no_std]
#![no_main]

use esp_backtrace as _;  // panic handler + exception handler
use esp_hal::{clock::ClockControl, peripherals::Peripherals, prelude::*};
use esp_println::println;

#[entry]
fn main() -> ! {
    let peripherals = Peripherals::take();
    let system = peripherals.SYSTEM.split();
    let clocks = ClockControl::boot_defaults(system.clock_control).freeze();

    // 配置 GPIO
    let io = Io::new(peripherals.GPIO, peripherals.IO_MUX);
    let mut led = io.pins.gpio2.into_push_pull_output();

    loop {
        led.toggle().unwrap();
        delay(500_000);  // 简单延时
    }
}
```

### 2.2 RTIC 任务框架示例

```rust
#![no_std]
#![no_main]

use rtic::app;
use panic_halt as _;

#[app(device = esp32s3, peripherals = true)]
mod app {
    use esp_hal::gpio::{Gpio2, Output, PushPull};
    use esp_hal::timer::Timer;

    // 共享资源（编译期保证无数据竞争）
    #[shared]
    struct Shared {
        counter: u32,
    }

    // 本地资源（任务独占）
    #[local]
    struct Local {
        led: Gpio2<Output<PushPull>>,
        timer: Timer,
    }

    #[init]
    fn init(cx: init::Context) -> (Shared, Local, init::Monotonics) {
        let peripherals = cx.device;
        // 初始化硬件...

        (
            Shared { counter: 0 },
            Local { led, timer },
            init::Monotonics(),
        )
    }

    // 硬件任务：绑定到定时器中断
    #[task(binds = TIMER0, priority = 2, local = [led], shared = [counter])]
    fn timer_tick(cx: timer_tick::Context) {
        let led = cx.local.led;
        led.toggle().unwrap();

        cx.shared.counter.lock(|c| {
            *c += 1;
        });
    }

    // 软件任务：可被 spawn
    #[task(priority = 1, shared = [counter])]
    fn process_data(cx: process_data::Context) {
        let count = cx.shared.counter.lock(|c| *c);
        // 处理数据...
    }
}
```

**RTIC 关键概念**：
- `#[shared]`：多任务共享资源，编译期自动插入临界区
- `lock()`：SRP 锁，天花板优先级协议，保证无死锁
- `priority`：静态优先级，编译期确定调度顺序
- `spawn`：任务间消息传递，非阻塞

### 2.3 Embassy async 模式示例

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use esp_backtrace as _;
use esp_hal::gpio::{Gpio2, Output, PushPull};

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let peripherals = esp_hal::init(esp_hal::Config::default());
    let io = esp_hal::gpio::Io::new(peripherals.GPIO, peripherals.IO_MUX);

    let led = io.pins.gpio2.into_push_pull_output();

    // Blink task
    loop {
        led.set_high().await;
        Timer::after(Duration::from_millis(500)).await;
        led.set_low().await;
        Timer::after(Duration::from_millis(500)).await;
    }
}
```

**Embassy 多任务示例**：
```rust
#[embassy_executor::task]
async fn sensor_reader(mut sensor: I2c<'static>) {
    loop {
        let data = sensor.read(0x68, 6).await;
        // 处理传感器数据
        Timer::after(Duration::from_millis(100)).await;
    }
}

#[embassy_executor::task]
async fn wifi_manager(stack: WifiStack) {
    // WiFi 连接管理...
    stack.connect().await;
}

#[embassy_executor::main]
async fn main(spawner: Spawner) {
    // 初始化硬件...
    spawner.spawn(sensor_reader(sensor)).ok();
    spawner.spawn(wifi_manager(stack)).ok();
}
```

### 2.4 Xtensa vs RISC-V 工具链差异

| 维度 | Xtensa (ESP32/S2/S3) | RISC-V (C3/C6/H2) |
|------|----------------------|-------------------|
| 工具链安装 | `espup` (自定义 LLVM) | 标准 `rustup target add` |
| Rust 版本 | 需要 esp-rs fork | 标准 stable Rust |
| 编译速度 | 较慢（fork 工具链） | 快（原生 LLVM 后端） |
| 调试 | probe-rs / JTAG | probe-rs / JTAG |
| 生态成熟度 | 稍早（历史更长） | 快速追赶中 |

**推荐入门芯片**：**ESP32-C3**（RISC-V，可用标准 Rust 工具链，学习阻力最小）

### 2.5 embedded-hal 1.0 — 统一硬件抽象

`embedded-hal` 是嵌入式 Rust 的核心抽象层，2024 年底正式发布 1.0：

```rust
use embedded_hal::digital::OutputPin;
use embedded_hal::delay::DelayNs;

// 泛型驱动 — 不依赖任何具体 MCU
fn blink<P, D>(pin: &mut P, delay: &mut D) -> !
where
    P: OutputPin,
    D: DelayNs,
{
    loop {
        pin.set_high().ok();
        delay.delay_ms(500);
        pin.set_low().ok();
        delay.delay_ms(500);
    }
}

// 同一份代码可用于 ESP32 / STM32 / RP2040 / nRF52
```

**关键 traits**：
- `embedded_hal::digital::{InputPin, OutputPin}` — GPIO
- `embedded_hal::spi::SpiBus` — SPI 总线
- `embedded_hal::i2c::I2c` — I²C 总线
- `embedded_hal::uart::Uart` — 串口
- `embedded_hal::pwm::SetDutyCycle` — PWM
- `embedded_hal::adc::Adc` — ADC
- `embedded_hal_async::*` — 异步版本（用于 Embassy）

---

## 三、实践启发

### 3.1 选择框架的决策树

```
是否需要硬实时保证（电机控制/飞控）？
├─ 是 → RTIC（SRP 调度保证确定性）
└─ 否
    ├─ 需要 WiFi/BLE/USB？ → Embassy（内置协议栈）
    └─ 简单传感器读取？ → 裸 loop + esp-hal（最简单）
```

### 3.2 Jetson Orin + ESP32 的混合架构

结合猫仔运行环境（Jetson Orin Nano），实用方案：
- **Jetson 端**：Python 策略引擎 + 数据分析（AKShare/Tushare）
- **ESP32 端**：Rust 固件做实时信号采集 + 执行
- **通信**：UART/MQTT over WiFi，Jetson 下发指令，ESP32 上报数据
- **固件开发**：用 `cross` 或 Jetson 上的 Rust 工具链交叉编译

### 3.3 AI 时代嵌入式开发的变革

Embedded Computing Design 的社区圆桌观点：
- **AI 将写大部分嵌入式代码**（但需要类型安全语言生成，Rust 更适合）
- **Rust 的编译器即测试**理念与 AI 代码生成天然互补
- **内存安全在 AI 生成代码中更为关键**（AI 不理解裸机指针陷阱）
- Linux 内核已接受 Rust 模块，NASA 评估 Rust 用于航天系统

### 3.4 性能对比（Rust vs C）

根据学术研究（ResearchGate 论文 + Instagram 团队分享）：
- **Flash 占用**：Rust 略大于 C（约 5-15%），但 LTO 可缩小差距
- **RAM 使用**：Rust 更优（无动态分配，编译期确定性内存）
- **运行性能**：零成本抽象 ≈ 手写 C（benchmark 差异 <3%）
- **开发效率**：Rust 前期慢（学习曲线），后期快（编译器捕获 bug）

---

## 四、知识缺口

- [ ] esp-radio（原 esp-wifi）的稳定时间线（当前需 `unstable` feature）
- [ ] ESP32-S3 + ESP-IDF + Rust std 模式 vs no_std 模式的功能对比
- [ ] Embassy 的 `embassy-boot` DFU 在 ESP32 上的实际使用案例
- [ ] RTIC 在 RISC-V ESP32-C6 上的中断延迟实测数据
- [ ] probe-rs + VSCode 调试 ESP32 Rust 固件的完整工作流
- [ ] Rust async 在 ESP32 上的栈使用分析（每个 task 的栈开销）

---

## 五、与现有生态的关系

| 发现 | 可采纳度 | 行动 |
|------|----------|------|
| esp-hal 1.0 beta 全系列支持 | ⭐⭐⭐ | 记录到 memory，嵌入式 skill 需更新 |
| RTIC v2 RISC-V 支持 | ⭐⭐ | 笔记存档，待实际项目时参考 |
| Embassy esp-rtos 集成 | ⭐⭐⭐ | 推荐 ESP32 IoT 项目首选 Embassy |
| embedded-hal 1.0 统一抽象 | ⭐⭐⭐ | 写入 memory，泛型驱动设计模板 |
| Bevy ECS on ESP32 (no_std) | ⭐ | 纯新奇，暂无实际应用场景 |

---

## 六、参考资源

1. [esp-hal 1.0.0-beta 公告](https://developer.espressif.com/blog/2025/02/rust-esp-hal-beta/) — Espressif 官方
2. [RTIC Book](https://rtic.rs/) — 官方文档
3. [Embassy GitHub](https://github.com/embassy-rs/embassy) — 14,897 commits，活跃开发
4. [FOSDEM 2026: From C to Rust on ESP32](https://fosdem.org/2026/schedule/event/GNNQFP-converting-c-firmware-to-rust/)
5. [EDN: Rust 嵌入式内存安全](https://www.ednchina.com/news/a14639.html) — 2025-12
6. [Embedded Rust ESP 开发生态](https://blog.theembeddedrustacean.com/the-embedded-rust-esp-development-ecosystem)
7. [RTIC vs Embassy 对比](https://www.willhart.io/post/embedded-rust-options/) — 实战对比
8. [Rust on ESP Book](https://docs.espressif.com/projects/rust/book/) — Espressif 官方 Rust 教程

## 相关笔记
- [esp32-projects](esp32-projects.md)
- [esp32-lcd-display](esp32-lcd-display.md)
- [esp32-edge-impulse-pipeline](explore/2026-05-18-esp32-edge-impulse-pipeline.md)
- [embedded-rust-deep-learn](explore/embedded-rust-deep-learn.md)
- [esp32-s3-voice-gesture-lamp-analysis](esp32-s3-voice-gesture-lamp-analysis.md)
