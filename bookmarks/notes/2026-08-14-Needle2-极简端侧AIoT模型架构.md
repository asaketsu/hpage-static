# Needle 2 — 极致端侧 AIoT & 嵌入式 AI 智能体引擎研究

> 来源：微信公众号文章《仅 14MB 大小，Needle2 蒸馏 Gemini 拥有4500万参数，可在树莓派、ESP32 运行的 AIoT 物联网端侧 AI 小模型》
> 技术归纳与深度拆解 (2026-08-14)
> GitHub 仓库：https://github.com/cactus-compute/needle

---

## 一、Needle 2 核心规格与定位

Needle 2 是由 Cactus Compute 团队研发的，蒸馏自 Google Gemini 模型的 **极小端侧工具调用 (Tool Calling) 专用模型**。

| 指标 | 规格细节 | 解释与影响 |
|------|---------|-----------|
| **参数量** | 4500万 (45M) | 相比主流端侧模型 (Gemma 2B/Llama 3 8B) 缩减了两个数量级 |
| **单二进制文件** | 14MB (`.cact` 格式) | 可直接静态编译进固件或 App 分布式，免除复杂环境构建 |
| **运行时内存 (RAM)** | **固定约 28MB** | **不可思议的低内存。** 能够在树莓派、高端 ESP32 等微型 SoC 上平稳运行 |
| **量化精度** | CQ2-bit (Cactus Quants) | 独创的 2-bit 自适应压缩，比常规 FP16 内存降低 8x |
| **上下文窗口** | 256 tokens (滑动窗口) | 设计目标决定其不需要超长窗口，仅处理指令与工具返回 |
| **前向/推理速度** | Prefill ~4300 t/s, Decode ~850 t/s | 典型桌面级基准测试。在端侧上解码可轻松实现实时的 30-50 t/s |

---

## 二、架构创新：什么是“简单注意力网络 (Simple Attention Network)”？

传统 Transformer 因注意力机制的平方复杂度 $O(N^2)$ 以及巨大的前馈网络 (FFN) 导致参数失控。Needle 2 放弃了经典解法，采用**四项根本创新**：

```
                        [ Input Tokens ]
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [ Hadamard MLP ]                 [ Grouped Query ]
    ( Walsh-Hadamard Transform )        [   Attention  ]
               │                               │
               │                        [ Engram KV Memory ]
               │                       (Hash n-gram Indexing)
               │                               │
               └───────────────┬───────────────┘
                               ▼
                    [ Multi-channel Links ]
                    ( Differentiable Gates )
                               │
                               ▼
                       [ Output Logits ]
```

### 1. Hadamard MLP (哈达玛前馈层)
* **设计**：使用固定的、正交的 **Walsh-Hadamard 变换矩阵** 替换传统的 FFN 线性投影矩阵。
* **增益**：**零参数乘法！** 该矩阵没有可学习权重，其转置和计算通过快速哈达玛变换 (FHT) 以 $O(N \log N)$ 复杂度完成。模型最重的一块参数被“结构性硬编码”了。
* **物理机制**：相当于通过高维空间的正交旋转代替复杂的特征非线性组合。

### 2. Engram 键值记忆 (记忆槽)
* **设计**：用类似布隆过滤器的“哈希 n-gram 查找表”聚合过去的 Key-Value 键值对，而非维护完整的 KV Cache 历史。
* **增益**：对工具调用的 schema 及常识性上下文做“KV Sink”，锁死在哈希表中。**无论对话多长，KV 内存永不增长，维持在极低水位。**

### 3. GQA 密集投影 (GQA Attention)
* 用于实现更低的运算负载，只在核心参数上保留小规模门控。

### 4. 多通道超连接 (Multi-channel Links)
* 设置并联的残差流动通道，允许信息绕过注意力机制在相邻层之间高速渗透，使这颗“45M小心脏”在极浅层仍能拥有极强的数据路由能力。

---

## 三、更好解释：边缘智能如何确保“0 幻觉”工具调用？

把 45M 模型放到燃起炉灶的智能家居或汽车物理按键中，**绝对不允许发生格式错乱导致的解析器崩溃（幻觉）**。为此，Needle 2 采用了三层刚性安全设计：

```
 ┌────────────────────────────────────────────────────────┐
 │                      User Request                      │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │              A-GRA / Built-in Retrievor                │── [过滤] ── 只留下 Top 5 工具
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │             Confidence Gate (置信度评估)               │
 └───────────────────────────┬────────────────────────────┘
                             ├──────────────────────────┐
                   (Confidence >= Threshold)   (Confidence < Threshold)
                             │                          │
                             ▼                          ▼
 ┌────────────────────────────────────────────────────────┐  ┌────────────────────────────┐
 │               Byte-level Syntax Constraint             │  │   Escalate (升级处理)      │
 │    (强制输出合法 JSON, 拒绝一切非 Schema 规则的 token)   │  │   - 云端大模型 / 人类审核   │
 └───────────────────────────┬────────────────────────────┘  └────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                Execute Physical Tool                   │
 └────────────────────────────────────────────────────────┘
```

### 1. 约束生成 (Constrained Generation)
* **本质**：将 Pydantic 或 JSON Schema 编译到状态机 (FSM) 或前缀分析器中。
* **结果**：限制模型推理时对词表 (Vocabulary) 的采样范围。模型只能从符合 JSON 排布的 token 中概率采样。生成无效 JSON 在算力层被物理屏蔽。

### 2. 置信度门控 (Confidence Gating)
* **本质**：在网络上加了一层微型预测头，用于对当前回答的安全边际打分。当判定低于设定阈值，立即挂起，抛回云端或指示灯闪烁。

---

## 四、对 Hermes Agent 的启发与学习

1. **“Mission Autonomy Sold Separately”**：
   * 对应 Needle 2 的设计，Agent 开发正走向类似 **LLM + 射频/硬件控制芯片** 的解耦。我们应加强 Hermes 工具调用的接口模式（A-GRA 化），将具体环境细节和推理逻辑通过严格数据协议切开。
2. **轻量本地辅助 Agent 可能性**：
   * 在 Jetson 设备或局域网树莓派上构建一個 `needle-2` 本地网关。
   * 协助处理简单的 TTS/ASR 唤醒监听、硬件轮询，只在必要时唤醒宿主大模型，从而大幅降低 token 费率与本地能耗。

---

## 五、Needle 2 开发示范

### 1. 基础依赖与声明 (使用 Pydantic 实现严格约束提取)

```python
import needle
from pydantic import BaseModel, Field

# 声明期望的严格结构
class IoTHumidityControl(BaseModel):
    target_humidity: int = Field(..., description="目标湿度百分比, 30-80")
    boost_mode: bool = Field(False, description="是否开启极速除湿")
    duration_mins: int = Field(60, description="运行时间/分钟")

# 一次性提取结构化数据
data_source = "把主卧的抽湿机开大点, 湿度控在 45%, 开半小时就行了"
extracted = needle.extract(data_source, IoTHumidityControl)

print(f"Target: {extracted.target_humidity}% | Boost: {extracted.boost_mode} | Duration: {extracted.duration_mins}m")
# Output: Target: 45% | Boost: True | Duration: 30m
```

### 2. 带离线自愈与降级机制的 Tool-Calling 架构

```python
import needle

@needle.tool
def local_relay_switch(pin_id: int, status: bool) -> dict:
    """
    控制 ESP32 继电器的物理引脚状态。
    pin_id: GPIO 引脚编号 (1-32)
    status: True 为闭合通电, False 为断开
    """
    # 模拟底层的 GPIO 指令写入
    # os.system(f"echo {status} > /sys/class/gpio/gpio{pin_id}/value")
    return {"status": "success", "pin": pin_id, "state": "HIGH" if status else "LOW"}

# 初始化并搭载本地硬件接口工具
relay_agent = needle.Needle(tools=[local_relay_switch], confidence_threshold=0.85)

try:
    # 物理按键事件触发离线轻量处理
    response = relay_agent.run("帮我把 12 号引脚的用电设备关掉")
    print("Action executed:", response["results"])
except needle.LowConfidenceException:
    # 低置信度自适应降级：交由大模型二次校验
    print("WARNING: Local model confidence too low. Escalating to Cloud API...")
    # fallback_to_cloud_agent("帮我把 12 号引脚的用电设备关掉")
```

## 相关笔记

- [Qwen3.5-0.8B 端侧零件工程使用指南](./2026-08-14-Qwen3.5-0.8B端侧零件工程使用指南.md) — 端侧小模型当零件的工程实践
- [Flix ESP32 四旋翼飞控项目](./2026-08-14-Flix-ESP32四旋翼飞控项目.md) — ESP32 端侧智能硬件搭档
