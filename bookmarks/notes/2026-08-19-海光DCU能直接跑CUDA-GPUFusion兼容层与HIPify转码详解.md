# 海光 DCU 能直接跑 CUDA？底层技术大放送！（GPUFusion 兼容层 + HIPify 转码）

> **来源**：微信公众号「海光信息」（推测）
> **原文链接**：https://mp.weixin.qq.com/s/qrAwkqJ4TUX5AWTOm3SksA
> **作者**：海光 DCU 团队
> **记录日期**：2026-08-19

**标签**：#海光DCU #CUDA兼容 #GPUFusion #HIPify #DTK #国产GPU #GPGPU #PTX翻译 #HSACO

---

## 一、内容整理

> **核心结论**：海光深算系列 DCU（Deep Computing Unit）采用 **GPGPU 架构，与 NVIDIA 隶属同一架构**，实现 CUDA 代码平滑迁移——「无需修改代码即可运行」。

### 1.1 作者动机

> 「在讨论海光 DCU 如何实现平滑迁移原先基于 CUDA 编程框架开发的应用程序时，缺少一些系统性的材料，直观展示实现的技术路径、底层原理以及相关细节。」

作者明确说：目的是帮 ISV/整机伙伴/客户/行业专家理解 DCU 的技术路径，从而「树立对海光 DCU 加速芯片的信心」。

### 1.2 两条兼容路径总览

```
              ┌─ 路径A：GPUFusion 兼容层（Runtime 运行时翻译）
              │    API 拦截 cuda_* → hip_*
              │    PTX → HSACO 指令翻译
              │    Kernel Fusion 抵消翻译损耗
              │
CUDA 应用 ───┤
              │
              │    源码转换 CUDA → HIP
              └─ 路径B：HIPify 转码工具（静态编译期翻译）
                    hipify-perl / hipify-clang
                    批量替换 API/类型/宏/内核语法
```

### 1.3 路径A：GPUFusion 兼容层（Runtime 透明兼容）

> **关键定位**：「源码基本不用修改」「整个过程对上层应用程序完全透明」

DTK 26.04 的 GPUFusion 兼容层**对标 CUDA 12.6**，兼容 **CUDA/ROCm 双生态**。底层三层实现：

| 层级 | 做的事 | 输入 → 输出 |
|------|--------|------------|
| API 层 | 拦截 cuda_\* 调用 | cudaMalloc → hipMalloc |
| 指令层 | PTX 翻译 | PTX 虚拟指令集 → HSACO 异构系统架构目标代码 |
| 性能层 | Kernel Fusion | 合并 kernel 抵消翻译损耗 |

编译器链路对比：

- **NVIDIA**：`nvcc` → PTX → Device Binary
- **海光**：`hipcc` / `hip-clang` → LLVM IR → HSACO

工作流程：`cuda_runtime.h` → 拦截 → `hip_runtime.h`；`cudaLaunchKernel` → 拦截 → `hipLaunchKernel`；PTX → LLVM IR → HSACO。

> **原文金句**：「在应用程序运行的过程中通过"拦截 CUDA API 调用 → 翻译为 hip 对应调用 → 返回应用程序"，整个过程对上层应用程序完全透明。」

### 1.4 路径B：HIPify 转码工具（静态主动迁移）

> **核心思想**：「主动迁移」——在运行之前完成「CUDA 代码 → HIP 代码」的转换。

内置工具：**hipify-perl** 和 **hipify-clang**，自动扫描全部 CUDA 源码文件（.cu/.h/.cpp），批量替换。

**五类替换维度**（原文完整对照）：

**1）设备指针类型**

```
cudaDeviceProp → hipDeviceProp
```

**2）函数返回值枚举**

```
cudaError_t → hipError_t
```

**3）内存拷贝方向枚举**

```
cudaMemcpyHostToDevice → hipMemcpyHostToDevice
cudaMemcpyDeviceToHost → hipMemcpyDeviceToHost
cudaMemcpyDeviceToDevice → hipMemcpyDeviceToDevice
```

**4）流/事件句柄**

```
cudaStream_t → hipStream_t
cudaEvent_t  → hipEvent_t
```

**5）内核启动语法**（语法不变，仅头文件/底层 API 变更）

```cpp
// 原始 CUDA
vectorAdd<<<gridDim, blockDim>>>(d_A, d_B, d_C, N);

// HIPify 后（语法不变）
vectorAdd<<<gridDim, blockDim>>>(d_A, d_B, d_C, N);
// 头文件自动替换：
#include <cuda_runtime.h> → #include <hip/hip_runtime.h>
```

### 1.5 完整代码迁移示例（原文）

**原始 CUDA 代码**：

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

int main() {
    float* dev_ptr;
    cudaError_t ret = cudaMalloc(&dev_ptr, 1024 * sizeof(float));
    if(ret != cudaSuccess) {
        printf("显存分配失败\n");
        return -1;
    }
    float host_buf[1024] = {0.5f};
    cudaMemcpy(dev_ptr, host_buf, 1024*sizeof(float), cudaMemcpyHostToDevice);
    cudaDeviceSynchronize();
    cudaFree(dev_ptr);
    return 0;
}
```

**HIPify 转换后**：

```cpp
int main() {
    float* dev_ptr;
    hipError_t ret = hipMalloc(&dev_ptr, 1024 * sizeof(float));
    if(ret != hipSuccess) {
        printf("显存分配失败\n");
        return -1;
    }
    float host_buf[1024] = {0.5f};
    hipMemcpy(dev_ptr, host_buf, 1024*sizeof(float), hipMemcpyHostToDevice);
    hipDeviceSynchronize();
    hipFree(dev_ptr);
    return 0;
}
```

### 1.6 作者原话总结

> 「无论是通过海光 DTK 软件栈提供的 HIPify 转码工具还是通过 GPUFusion 兼容层，都可以实现在海光 DCU 加速器运行 CUDA 应用程序。」

> 「HIPify 转码工具属于**静态编译**，即在程序运行之前完成编码；而 GPUFusion 兼容层属于**运行时编译**，整个过程对上层应用程序完全透明。」

> 「……是**过渡阶段的手段**，目的是减少不必要的重复开发、降低应用迁移难度，使用户的 AI 应用能够快速在海光国产 DCU 跑起来。」

> 最终呼吁：「以 DTK 编程框架为基础开展 **DCU 原生应用开发**，摆脱 CUDA 程序迁移适配带来的繁琐改造与性能损耗。」

## 二、查询拓展

### 2.1 HSACO 与 PTX 的关系

**PTX**（Parallel Thread Execution）是 NVIDIA 的中间虚拟指令集——类似 Java 的 bytecode，`nvcc` 编译到 PTX 后由设备端的 JIT（just-in-time）编译器译成具体 GPU 架构的 SASS 指令。

**HSACO**（Heterogeneous System Architecture Object Code）是 AMD GCN/CDNA 架构的 object code 格式，由 AMD 的 ROCm 编译器链（`hipcc` → LLVM）生成。海光 DCU 因架构源自 AMD GCN，沿用 HSACO 格式。

**翻译路径**：GPUFusion 拦截到 PTX 后，通过 LLVM 后端将其翻译为 HSACO——本质上是「NVIDIA PTX 虚拟 ISA → LLVM IR → AMD GCN/CDNA 后端」的一段编译链路。

### 2.2 ROCm 与 HIP 生态

HIP（Heterogeneous-Compute Interface for Portability）是 AMD 主导的 CUDA 兼容 API 抽象层。DTK 的 GPUFusion 兼容层对标 **CUDA 12.6**，本质上是「CUDA API ↔ HIP API」的运行时桥接，再走 ROCm 编译器链落到 HSACO。

这条路径与 NVIDIA 自家的 CUDA、AMD 的 ROCm/HIP 形成三方对照：

- NVIDIA：CUDA API + nvcc + PTX + SASS
- AMD：HIP API + hipcc + LLVM IR + HSACO
- **海光**：CUDA API（拦截）→ HIP API → hipcc → LLVM IR → HSACO

### 2.3 海光 DCU 架构谱系

海光 DCU 源自 AMD GCN 架构授权（海光信息曾通过合资方式获得 AMD 技术授权），属于 GPGPU 大类。产品线包括：

- **深算一号（DCU-9000 系列）**：对标 NVIDIA V100
- **深算二号（DCU-9200 系列）**：对标 NVIDIA A100
- **DTK 26.04**（2026 年 4 月发布）：兼容层对标 CUDA 12.6

### 2.4 国产化 GPU 兼容 CUDA 的三种技术路线对照

- **海光 DCU**：API 拦截 + PTX→HSACO 翻译 + Kernel Fusion（本文路径A）
- **华为昇腾**：Ascend C / CANN，提供 `cuda2ascend` 迁移工具，但架构不同（达芬奇 NPU），翻译难度更高
- **壁仞/摩尔线程**：自建编译器链 + CUDA API 兼容层，壁仞通过 BR-SIMD CUDA 兼容层实现

## 三、归纳总结

### 3.1 两条路径的选择决策树

```
你的 CUDA 程序能不能改源码？
├─ 不能改 / 不想改 / 时间紧
│    └─ 路径A：GPUFusion 兼容层
│         • 透明、零源码修改
│         • 但有翻译损耗 → 靠 Kernel Fusion 抵消
│         • 性能略低于 HIPify（翻译层开销）
│
└─ 能改 / 追求极限性能
     └─ 路径B：HIPify 转码
          • 一次性成本：跑 hipify-perl/clang
          • 产出 HIP 原生代码，后续可直接优化
          • 最终走 DCU 原生编译链路 → 最佳性能
```

### 3.2 五维对比表

```
              GPUFusion 兼容层          HIPify 转码工具
──────────────────────────────────────────────────────
翻译时机      运行时（Runtime）          编译期（静态）
源码修改      零                         自动批量替换
API 透明性    完全透明                   头文件/API 名可见变更
性能损耗      有（Kernel Fusion 抵消）   低（HIP 原生）
适用场景      快速验证/ISV 迁移          正式产品/追求性能
对标 CUDA     12.6                       由 hipify 版本决定
工具          自动                        hipify-perl / hipify-clang
```

### 3.3 作者的战略意图

作者反复强调「过渡阶段的手段」「原生应用开发」——**兼容 CUDA 是吸引生态的入场券，不是终点**。真正的目标：开发者先跑起来 → 用 DTK 原生框架重写 → 摆脱迁移损耗。

## 四、趋势判断

### 趋势1：GPUFusion 兼容层的 CUDA 版本对齐将持续推进

DTK 26.04 对标 CUDA 12.6。随着 NVIDIA 发布 CUDA 13/14，海光必然继续追赶。但每追一个版本都意味着新 API/新指令（如 cooperative groups、async copy）需要新翻译规则——**兼容性是有技术债的**。

### 趋势2：Kernel Fusion 优化是性能竞争的核心战场

PTX→HSACO 翻译天然有性能损耗（调度粒度和寄存器分配策略差异）。海光能否在「翻译损耗 ≤ 5%」的目标下稳定交付，取决于 Kernel Fusion 的覆盖率和优化深度。这是 ISV 选型时最关注的数据。

### 趋势3：DCU 原生生态建设是长期胜负手

作者自己说了「过渡阶段」——真正有竞争力的 DCU 应用必然是 DTK 原生编写，绕开兼容层。但开发者迁移到原生的动力取决于 DTK 工具链的成熟度（profiler、debugger、math lib 精度），而不是兼容层本身的承诺。

## 五、关联分析

### 5.1 与「嵌入式 AI-TinyML 现状」(2026-07-19) 的架构层对照

- 那篇聚焦 MCU 端侧推理（TinyML）；本篇聚焦数据中心 GPU（DCU）
- 两者形成「嵌入式端 + 数据中心端」的国产算力完整画像
- TinyML 走的是 TFLM/CMSIS-NN 路线；DCU 走的是 GPGPU/DTK 路线——两条完全不同的算力生态

### 5.2 与「TinyML 模型部署 STM32 精度排查」(2026-06-04) 的调试方法论共通

- 那篇讲的是「PC/MCU 双端推理结果不一致时怎么查」
- 本篇的 GPUFusion 路径本质上是「NVIDIA PTX → HSACO」的双端翻译——**量化误差/精度偏差的调试方法论高度相通**
- 那篇的「黄金输入分层比较」思路可以直接迁移到 DCU 兼容层性能验证

### 5.3 与「MCU 跑神经网络与普通 C 算法差异」(2026-08-19) 同日笔记的互补

- 同日另一篇讲 TinyML 底层原理（NN vs C 算法差异）
- 本篇讲 GPGPU 迁移兼容性——**两者合起来构成「端侧推理 + 数据侧加速」的完整国产 AI 硬件视野**

## 六、金句摘录

> 「海光深算系列人工智能芯片 —— DCU（Deep Computing Unit）采用 GPGPU 架构，与 NVIDIA 隶属同一架构，能够实现 CUDA 代码平滑迁移，无需修改代码即可运行。」

> 「GPUFusion 兼容层属于运行时编译，在应用程序运行的过程中通过'拦截 CUDA API 调用 → 翻译为 hip 对应调用 → 返回应用程序'，整个过程对上层应用程序完全透明。」

> 「HIPify 转码工具属于静态编译，即在程序运行之前完成编码。」

> 「……是过渡阶段的手段，目的是减少不必要的重复开发、降低应用迁移难度，使用户的 AI 应用能够快速在海光国产 DCU 跑起来。」

> 「以 DTK 编程框架为基础开展 DCU 原生应用开发，摆脱 CUDA 程序迁移适配带来的繁琐改造与性能损耗。」

## 七、拓展应用推荐

### 7.1 对 Hermes/Jetson 工作站的借鉴

> **不直接迁移 CUDA 代码，但可借鉴架构思想**：

- Hermes 当前运行在 Jetson Orin（NVIDIA 架构），本篇的「API 拦截 + 编译期翻译」思想可类比用于「Jetson CUDA → 未来国产卡」的迁移预案
- 若项目涉及 DCU 采购评估：直接跑 GPUFusion 兼容层做快速 POC，再评估 HIPify 做正式迁移

### 7.2 对量化交易 GPU 加速的延伸

- 用户在做的量化交易（iron-rules/连板策略）若需 GPU 加速（如 GPU 并行回测），可评估 DTK 兼容层能否直接跑现有 cuDF/CuPy 代码
- 路径A（GPUFusion）适合快速验证；路径B（HIPify）适合追求极致回测速度的生产部署

## 八、指南分析

### 给不同角色的行动建议

- **ISV/应用开发者**：先用 GPUFusion 兼容层做「零修改迁移」验证——能跑起来再决定要不要 HIPify
- **架构师**：GPUFusion 兼容层有翻译损耗，生产环境长期跑需要量化「Kernel Fusion 抵消后的净性能」数据
- **采购/选型人员**：DTK 版本 → CUDA 对标版本（当前 12.6）是核心指标，直接问海光销售要「DTK vs CUDA 性能对比白皮书」
- **量化交易者**：cuDF/CuPy 代码若要通过兼容层跑 DCU，先跑一个最小 benchmark（向量加法 + GEMM）测损耗

## 出处

- 原文公众号推文：https://mp.weixin.qq.com/s/qrAwkqJ4TUX5AWTOm3SksA
- 海光信息官网：https://www.hygon.co/
- DTK（DCU Toolkit）文档：https://dtk-docs.hygon.cn/
- 关联笔记：
  - [MCU 跑神经网络与普通 C 算法差异-TinyML 深入浅出第 02 篇](./2026-08-19-MCU跑神经网络与普通C算法差异-TinyML深入浅出第02篇.md)
  - [TinyML 模型部署 STM32 精度排查](./2026-06-04-TinyML模型部署STM32精度排查.md)
  - [嵌入式 AI-TinyML 现状](./2026-07-19-嵌入式AI-TinyML现状-从MCU感知到端侧小语言模型.md)

## 相关笔记
- [DCU算子开发全流程指南-海光DCU从环境验收到性能优化](2026-08-17-DCU算子开发全流程指南-海光DCU从环境验收到性能优化.md)
