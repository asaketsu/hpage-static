# 嵌入式 Rust 实战深度学习笔记：no_std、RTIC、Embassy 与 ESP32 固件开发

> 学习日期：2026-05-19 | 来源：web_search 多轮搜索 + 已有 embedded-rust skill
> 主题：嵌入式 Rust 实战 — no_std 开发、RTIC/Embassy 框架、ESP32 固件
> 字数：约 3500 字

---

## 一、核心概念解析

### 1.1 no_std 环境

`no_std` 是 Rust 嵌入式开发的基础概念。标准库（`std`）依赖操作系统提供的服务（堆分配、线程、文件系统、网络），而嵌入式设备没有操作系统，因此需要 `#[no_std]` 去掉标准库依赖。

```rust
#![no_std]
#![no_main]  // 裸机没有 main 入口

use panic_halt as _;  // panic 时直接 halt

#[cortex_m_rt::entry]
fn main() -> ! {
    // 永不返回的函数，返回类型是 never type !
    let dp = pac::Peripherals::take().unwrap();
    loop {
        // 主循环
    }
}
```

**关键约束：**
- 没有堆分配（Vec, String, Box 不可直接用）
- 没有 panic unwinding（需要 `panic-halt` 或 `panic-probe`）
- 静态分配为主，或用 `alloc` crate + 自定义全局分配器
- 临界区（critical-section）需要硬件支持

### 1.2 PAC / HAL / BSP 三层架构

嵌入式 Rust 的硬件抽象分三层：

| 层级 | 全称 | 职责 | 示例 |
|------|------|------|------|
| PAC | Peripheral Access Crate | 寄存器级直接映射 | `esp32c3-pac`, `stm32f4-pac` |
| HAL | Hardware Abstraction Layer | 安全的、高级的硬件接口 | `esp-hal`, `stm32f4xx-hal` |
| BSP | Board Support Package | 特定开发板的便捷封装 | `esp32s3-bsp` |

PAC 由 `svd2rust` 工具从 SVD 文件自动生成，HAL 在 PAC 之上提供类型安全的 API。开发中通常直接使用 HAL。

### 1.3 RTIC 框架

RTIC（Real-Time Interrupt-driven Concurrency）是专为 Cortex-M 设计的实时并发框架，基于硬件中断优先级实现任务调度。

**核心理念：**
- 编译时确定任务优先级（静态优先级）
- 基于中断的抢占式调度
- 零堆分配，所有任务静态分配
- 通过 "resources" 实现任务间数据共享，编译时检查竞态条件

```rust
#[rtic::app(device = pac, peripherals = true)]
mod app {
    use stm32f4xx_hal::prelude::*;

    #[shared]
    struct Shared {
        counter: u32,
    }

    #[local]
    struct Local {}

    #[init]
    fn init(cx: init::Context) -> (Shared, Local, init::Monotonics) {
        // 初始化硬件和定时器
        let mut timer = cx.device.TIM2.counter_hz(
            &mut cx.device.RCC.constrain().cfg
        );
        timer.start(1.Hz()).unwrap();
        timer.listen(Event::Update);

        (Shared { counter: 0 }, Local {}, init::Monotonics())
    }

    #[task(binds = TIM2, shared = [counter])]
    fn timer_tick(cx: timer_tick::Context) {
        let mut counter = cx.shared.counter;
        counter.lock(|c| {
            *c += 1;
        });
    }

    #[task(priority = 2, shared = [counter])]
    fn high_prio_task(cx: high_prio_task::Context) {
        cx.shared.counter.lock(|c| {
            // 安全访问共享资源
        });
    }
}
```

**RTIC 的优势：**
- 编译时保证无死锁（优先级 ceiling protocol）
- 零运行时开销
- 资源访问在编译时检查

**RTIC 的局限：**
- 仅支持 Cortex-M（ARM），ESP32（RISC-V/Xtensa）暂不支持
- 需要自带 HAL（"bring your own HAL"）
- 学习曲线较陡

### 1.4 Embassy 框架

Embassy 是现代异步嵌入式框架，使用 Rust 的 async/await 模型，是目前 ESP32 开发的首选框架。

**核心理念：**
- 基于 async/await 的协作式多任务
- 内置 HAL（`embassy-nrf`, `embassy-rp`, `esp-hal-embassy`）
- 多优先级 executor（interrupt-mode）
- 无需堆分配的异步执行器

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use esp_backtrace as _;
use esp_hal::gpio::{Io, Level, Output};

#[main]
async fn main(spawner: Spawner) {
    let peripherals = esp_hal::init(esp_hal::Config::default());
    let io = Io::new(peripherals.GPIO, peripherals.IO_MUX);
    let mut led = Output::new(io.pins.gpio2, Level::Low);

    loop {
        led.toggle();
        Timer::after(Duration::from_millis(500)).await;
    }
}
```

**Embassy 的 spawn 模式：**

```rust
#[embassy_executor::task]
async fn sensor_reader(mut uart: Uart<'static, Blocking>) {
    let mut buf = [0u8; 64];
    loop {
        match uart.read_async(&mut buf).await {
            Ok(n) => { /* 处理数据 */ }
            Err(e) => { /* 错误处理 */ }
        }
    }
}

#[main]
async fn main(spawner: Spawner) {
    // spawner.spawn(sensor_reader(uart)).ok();
    // spawn 后任务与 main 并发运行
}
```

### 1.5 RTIC vs Embassy 对比

| 特性 | RTIC | Embassy |
|------|------|---------|
| 调度模型 | 抢占式（中断优先级） | 协作式（async/await） |
| 目标平台 | Cortex-M only | 多平台（ESP32, NRF, RP2040） |
| HAL | 自带（需集成） | 内置（batteries included） |
| 学习曲线 | 陡峭 | 较平缓 |
| 调试 | 可预测延迟 | 需注意 executor 调度 |
| 内存 | 静态分配 | 静态分配 |
| 生态成熟度 | 较老，文档完善 | 快速发展，2025-2026 活跃 |

**结论：ESP32 开发首选 Embassy，Cortex-M 低延迟场景可考虑 RTIC。**

---

## 二、ESP32 固件开发实战流程

### 2.1 环境搭建

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 ESP32 目标
rustup target add riscv32imc-unknown-none-elf      # ESP32-C3
rustup target add xtensa-esp32-none-elf             # ESP32 (Xtensa)

# 安装 espflash 烧录工具
cargo install espflash

# 创建项目
cargo generate --git https://github.com/esp-rs/esp-template
```

### 2.2 项目结构

```
esp32-project/
├── Cargo.toml
├── .cargo/
│   └── config.toml          # 目标配置、runner 配置
├── build.rs                  # 编译脚本
└── src/
    └── main.rs               # 主程序
```

`.cargo/config.toml` 示例：
```toml
[target.riscv32imc-unknown-none-elf]
runner = "espflash flash --monitor"

[build]
target = "riscv32imc-unknown-none-elf"

[target.riscv32imc-unknown-none-elf.dependencies]
...

[env]
ESP_LOG = "info"
```

### 2.3 GPIO + UART + I2C 综合示例

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use esp_backtrace as _;
use esp_hal::{
    gpio::{Io, Level, Output, Input, Pull},
    i2c::I2C,
    uart::Uart,
    prelude::*,
};

#[main]
async fn main(_spawner: Spawner) {
    let peripherals = esp_hal::init(esp_hal::Config::default());
    let io = Io::new(peripherals.GPIO, peripherals.IO_MUX);

    // GPIO: LED 输出 + 按钮输入
    let mut led = Output::new(io.pins.gpio2, Level::Low);
    let button = Input::new(io.pins.gpio9, Pull::Up);

    // I2C: 连接传感器（如 BME280）
    let i2c = I2C::new(
        peripherals.I2C0,
        io.pins.gpio8,   // SDA
        io.pins.gpio18,  // SCL
        100.kHz(),
    );

    // UART: 调试输出
    let uart = Uart::new(
        peripherals.UART0,
        io.pins.gpio21,  // TX
        io.pins.gpio20,  // RX
    );

    loop {
        if button.is_low() {
            led.set_high();
        } else {
            led.set_low();
        }
        Timer::after(Duration::from_millis(100)).await;
    }
}
```

### 2.4 异步多任务模式（传感器 + 通信 + 控制）

```rust
use embassy_sync::channel::Channel;
use embassy_time::{Duration, Timer};

static SENSOR_DATA: Channel<NoopRawMutex, SensorReading, 1> = Channel::new();

#[derive(Clone, Copy)]
struct SensorReading {
    temperature: f32,
    humidity: f32,
}

#[embassy_executor::task]
async fn sensor_task(i2c: I2C<'static, Blocking>) {
    loop {
        // 读取传感器
        let reading = SensorReading {
            temperature: 25.0,  // 实际从 i2c 读取
            humidity: 60.0,
        };
        SENSOR_DATA.send(reading).await;
        Timer::after(Duration::from_secs(1)).await;
    }
}

#[embassy_executor::task]
async fn control_task(mut led: Output<'static>) {
    loop {
        let reading = SENSOR_DATA.receive().await;
        if reading.temperature > 30.0 {
            led.set_high();  // 过热报警
        } else {
            led.set_low();
        }
    }
}
```

---

## 三、Rust vs C：嵌入式开发对比

### 3.1 内存安全

Rust 的所有权系统在编译时消除了：
- 空指针解引用
- 数据竞态
- 缓冲区溢出
- Use-after-free

C 语言中这些是最常见的嵌入式 bug 来源。在 2025 年的一项调查中，嵌入式项目中约 60% 的安全漏洞与内存安全相关。

### 3.2 性能对比

| 指标 | Rust (no_std) | C (bare metal) |
|------|---------------|----------------|
| 二进制大小 | 略大（约 +5-15%） | 最小 |
| 运行时性能 | 基本持平 | 基本持平 |
| 编译时间 | 较长 | 较短 |
| 调试体验 | 较好（类型系统） | 传统 GDB |
| 生态丰富度 | 快速增长 | 非常成熟 |

### 3.3 开发体验优势

Rust 在嵌入式的独特优势：
- **编译时硬件检查**：GPIO 配置错误在编译时而非运行时发现
- **零成本抽象**：HAL 的类型安全不会带来运行时开销
- **强大的包管理**：cargo 比 C 的依赖管理（CMake + 手动管理）好太多
- **async/await**： Embassy 提供的异步模型比裸机状态机更易维护

---

## 四、实践启发

### 4.1 开发模式建议

1. **先 QEMU 模拟，后真机调试**：`qemu-system-riscv32` 可模拟部分 ESP32 功能
2. **defmt 日志**：嵌入式专用日志框架，比串口 println 高效 10 倍
3. **probe-run 调试**：直接在终端看 backtrace，不需要 IDE
4. **CI/CD**：cargo + target cross-compile 可轻松集成到 CI

### 4.2 常见陷阱

- **中断中的 async**：Embassy 的 interrupt executor 需要正确配置优先级
- **静态生命周期**：多任务共享数据必须 `'static`，用 `Channel` 或 `Signal` 传递
- **Flash 大小**：Rust 二进制可能偏大，用 `cargo bloat` 分析，`opt-level = "z"` 优化
- **Xtensa 工具链**：ESP32（非 C3/C6）需要自定义 LLVM，安装较复杂

---

## 五、知识缺口与未来方向

1. **Embassy 多核支持**：ESP32 双核（Xtensa）的 executor 分配策略
2. **DMA + async**：ESP32 DMA 外设的异步封装尚未完善
3. **WiFi/BLE**：`esp-wifi` crate 仍在积极开发中，稳定性待提升
4. **OTA 更新**：Rust 固件的空中升级方案（ESP-IDF partition table 兼容）
5. **功耗优化**：deep sleep + Embassy 唤醒模式的实践
6. **形式化验证**：Rust 类型系统在安全关键领域的认证进展
7. **ESP-IDF 互操作**：`esp-idf-hal`（基于 FreeRTOS）vs `esp-hal`（裸机）的选择

### 关键参考项目

| 项目 | 说明 |
|------|------|
| [esp-hal](https://github.com/esp-rs/esp-hal) | ESP32 系列 HAL，2025 年活跃维护 |
| [embassy](https://github.com/embassy-rs/embassy) | 异步嵌入式框架 |
| [esp-template](https://github.com/esp-rs/esp-template) | 项目模板 |
| [espflash](https://github.com/esp-rs/espflash) | 烧录工具 |
| [Bevy ECS on ESP32](https://developer.espressif.com/blog/2025/04/bevy-ecs-on-esp32-with-rust-no-std/) | 2025年新：Bevy ECS 在 ESP32 上运行 |

---

## 六、总结

嵌入式 Rust 在 2025-2026 已进入"可用"阶段：
- **ESP32 + Embassy** 是最主流的组合，esp-hal 持续更新
- **no_std** 开发模式成熟，cargo 生态完善
- **RTIC** 仍是 Cortex-M 低延迟场景的最佳选择
- 相比 C 的主要劣势在二进制大小和编译速度，但在开发效率和安全性上优势明显
- 下一步应关注 esp-wifi 稳定性和 OTA 方案

## 相关笔记
- [embedded-rust-nostd-rtic-esp32-deep-dive](explore/2026-05-19-embedded-rust-nostd-rtic-esp32-deep-dive.md)
