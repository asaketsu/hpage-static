# Needle 2 工程集成：API 契约、离线部署与 LoRA 微调实战

> **来源**：[cactus-compute/needle](https://github.com/cactus-compute/needle) GitHub 仓库（README + doc/apis.md + doc/finetuning.md）
> **项目**：`~/uclaw/project/needle2-tool-calling/`
> **论文**：arXiv:2607.18363
> **记录日期**：2026-08-21
> **仓库数据**：⭐ 8.2k / Fork 526 / 276 commits

**标签**：#Needle2 #工具调用 #端侧AI #结构化抽取 #离线部署 #LoRA微调

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 6 个标签覆盖 API/部署/微调 |
| 出处 | 头部出处行 | GitHub README + API docs + finetuning docs |
| 内容整理 | 第一~三章 | 产品规格/API 契约/微调工作流 |
| 查询拓展 | 第四章 | 关键机制深潜 + 对比竞品 |
| 归纳总结 | 第五章 | API 设计哲学 + 决策树 |
| 趋势判断 | 第六章 | 4 条预测 |
| 关联分析 | 第七章 | 与 8 篇已有笔记交叉映射 |
| 拓展应用推荐 | 第八章 | 落地清单 + 微调用例 + 学习方向 |
| 指南分析 | 第九章 | 工程优缺点评估 + Hermes 集成建议 |

---

## 一、内容详细整理

### 1.1 产品规格速查

> **Needle 2 = 45M 参数 / 14MB 单二进制 / 28MB 运行时内存 / 256 token 滑动窗口**

| 指标 | 规格 | 备注 |
|------|------|------|
| 参数量 | 45M | 比 FunctionGemma 270M 小 6× |
| 模型体积 | 14MB（.cact 单文件） | 权重烘焙进引擎，无需独立模型文件 |
| 运行时内存 | ~28MB（峰值） | 不随对话长度增长，工具作为 KV sink 固定占用 |
| 量化精度 | CQ2-bit（Cactus Quants） | 2-bit 自适应，比 FP16 省 8× |
| 上下文窗口 | 256 tokens（滑动窗口） | 仅处理指令 + 工具返回，不需要长上下文 |
| 推理速度 | Prefill ~4300 t/s / Decode ~850 t/s | 桌面级基准；端侧可跑 30-50 t/s 实时 |
| 架构 | Simple Attention Network | Hadamard MLP + GQA + Engram KV + 多路超连接 |
| License | Apache 2.0 | 商用友好 |

### 1.2 API 契约：一句话——"所有问题都是函数调用"

> **Needle 的设计哲学**：不做自由文本生成，一切输出都是函数调用。不支持的操作返回空调用 `[]`，不是生成一段道歉文本。

**三种调用方式**：

| 方式 | 方法 | 适用场景 |
|------|------|----------|
| **全自动** | `agent.run(query)` | 模型选工具 → 执行 Python 函数 → 喂结果回来 → 最终响应 |
| **单步控制** | `agent.complete(text)` | 每步手动执行，适合需要审核的场景 |
| **结构化抽取** | `needle.extract(text, Pydantic)` | 一次性抽取，返回类型化对象 |

**核心 API 签名**：

```python
# 创建 Agent（绑定工具集）
agent = needle.Needle(
    tools=[get_weather, set_lights],  # 装饰函数 / Pydantic / JSON schema
    system="date: 2026-08-21; device: phone; battery: 62%",  # 环境事实
    weights="my_tuned.cact",           # 加载微调权重（可选）
    tool_index_path="index.bin",       # 大工具集的持久化嵌入索引
    buffer_size=65536
)

# 全自动运行
response = agent.run("what's it like in Lagos right now?")
# response["results"] → [{"city": "Lagos", "temp_c": 27, "sky": "clear"}]

# 单步控制
response = agent.complete("dim the living room to 30")
# response["type"] == "call" → 执行函数，再 complete(json.dumps(result))

# 结构化抽取
class Invoice(BaseModel):
    vendor: str
    total: float
    due_date: str
invoice = needle.extract("Invoice from Acme Corp, $1,200, due 2026-09-01", Invoice)
```

### 1.3 工具声明方式

**三种声明方式**（由浅入深）：

```python
# 方式 1：装饰器（最简）
@needle.tool
def get_weather(city: str):
    """Get the current weather for a city."""
    return {"city": city, "temp_c": 27}

# 方式 2：带参数约束
from typing import Annotated, Literal
@needle.tool
def send_money(
    amount: Annotated[float, needle.Field(gt=0, le=10000)],
    to: Annotated[str, needle.Field(pattern=r"^@[a-z0-9_]+$")],
    mode: Literal["heat", "cool", "auto"] = "auto"
):
    return {"sent": amount, "to": to}

# 方式 3：原生 JSON schema（最大灵活性）
tools = [{
    "name": "set_lights",
    "description": "Turn a room's lights on or off",
    "parameters": {
        "type": "object",
        "properties": {
            "room": {"type": "string", "description": "which room"},
            "on": {"type": "boolean"},
            "brightness": {"type": "integer", "minimum": 0, "maximum": 100}
        },
        "required": ["room", "on"]
    }
}]
```

**Field 支持完整约束**：`description` / `enum` / `const` / `ge`/`le`/`gt`/`lt` / `multiple_of` / `min_length`/`max_length` / `pattern` / `format` / `min_items`/`max_items` / `unique_items`

> **关键机制**：所有约束在解码时编译成字节级语法（byte-level grammar），模型只能生成满足约束的值。不是"请求模型遵守"，是"语法上不可能违规"。

### 1.4 响应契约

每次返回一个 JSON 对象：

```json
{
    "type": "call",
    "success": true,
    "error": null,
    "function_calls": [
        {"name": "set_lights", "arguments": {"room": "living room", "brightness": 30}}
    ],
    "reasoning": "'living room' -> room; 'dim' -> brightness 30",
    "confidence": 0.94,
    "prefill_tps": 4300.0,
    "decode_tps": 850.0,
    "peak_ram_mb": 28.5
}
```

- `type: "call"` — 有工具调用
- `type: "respond"` — 循环结束（最终响应 = 工具结果本身，无自由文本）
- `function_calls: []` — 主题外请求，返回空调用而非生成文本
- `reasoning` — 每个参数从源 span 推导的短解释（不受语法约束，保持可读）

### 1.5 置信度门控（Confidence Gating）

> **核心设计**：每个响应携带校准后的置信度分数，来自两个信号的最小值。

| 信号 | 来源 |
|------|------|
| **事后评分头** | 校准后评估完整 prompt + 模型刚生成的调用 |
| **解码概率** | 调用 token 的原始解码概率 |

**设计原则**：两个信号必须同时同意才接受，失败模式是**升级（escalation）而非错误执行**。

```
置信度 ≥ 阈值 → 自动执行
置信度 < 阈值 → 重新询问 / 路由到更大模型
主题外请求 → 返回空调用 []
```

> ⚠️ **微调限制**：微调不更新置信度头，调优后的模型返回 `confidence: None`。非英语场景置信度也可能不准（西班牙语正确调用曾测得 confidence 0.0）。

### 1.6 工具检索（Tool Retrieval）

> **机制**：5 个以内工具直接渲染；超过 5 个时，内置对比头嵌入查询，只取 top-5 工具进入上下文，语法约束到该子集。

- 每次初始化时每个工具 schema 嵌入一次
- `tool_index_path` 持久化嵌入到磁盘，按 schema 指纹索引
- schema 变化时只重新嵌入变化部分
- **未选中的工具是不可达的（unreachable），不是"概率低"（unlikely）**

### 1.7 离线部署（Air Gapped）

> 推理引擎在首次使用时从 Hugging Face 下载并缓存，之后完全不碰网络。

```bash
# 方式 1：下载引擎到缓存
needle fetch --out /path/to/libneedle.so
needle fetch --platform-tag manylinux2014_aarch64  # 交叉下载

# 方式 2：拷贝引擎文件到同一缓存路径，或放到安装的 needle/ 包目录
# 方式 3：设置 NEEDLE_LIB_PATH=/path/to/libneedle.so 直接指定

# 完全离线安装包
pip download cactus-needle
pip install --no-index --find-links <dir> cactus-needle
export HF_HUB_OFFLINE=1  # 防止缺失时尝试联网
```

**平台 tag**：`macosx_11_0_arm64` / `manylinux2014_x86_64` / `musllinux_1_2_aarch64` / `win_amd64` / `win_arm64`

### 1.8 LoRA 微调工作流

**三步流程**：合成数据（可选）→ LoRA 微调 → 导出 .cact

**数据格式**（JSONL，每行一个样例）：

```json
{
  "query": "dim the kitchen to 10",
  "tools": [{"name": "set_lights", "parameters": {...}}],
  "answers": [{"name": "set_lights", "arguments": {"room": "kitchen", "brightness": 10}}],
  "reasoning": "'kitchen' -> room; 'dim to 10' -> brightness 10"
}
```

**关键规则**：
1. 参数值只能来自 query 中实际出现的文本，无证据的可选字段省略而非填空
2. 包含约 1/8 的"主题外"样例（`"answers": []`），否则模型对什么都调用
3. 相似工具集包含歧义查询解析到正确工具的样例
4. 每行必须 ≤ `--max-len` tokens（默认 1024），超长静默截断

**命令**：

```bash
# 1. 合成数据（可选，需 OPENROUTER_API_KEY）
needle generate-data --tools my_tools.json --num-samples 500 --output data.jsonl
needle generate-data --augment data.jsonl --num-samples 500

# 2. LoRA 微调
needle finetune data.jsonl --epochs 10
needle finetune data.jsonl --epochs 10 --generate 300 --lora-rank 16 --lora-alpha 32

# 3. 导出
needle build checkpoints/needle2.pkl --lora checkpoints/needle_lora.pkl --out my_needle.cact
# 可选 --bits 2 进一步压缩

# 4. 运行
needle playground --weights my_needle.cact  # 浏览器 UI 测试
```

**训练参数速查**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--epochs` | 3 | 小数据集建议 10-30 |
| `--lora-rank` | 16 | 论证密集型任务升到 32 |
| `--lora-alpha` | 32 | rank 的两倍 |
| `--lr` | 1e-4 | warmup + cosine decay |
| `--batch-size` | 16 | 小数据集保持默认 |
| `--max-len` | 1024 | 短数据集建议降到 256（6× 提速） |
| `--val-split` | 0.1 | 验证集比例 |

**加速器支持**：

| 后端 | 安装方式 | 备注 |
|------|----------|------|
| CPU | `pip install cactus-needle` | 默认 |
| NVIDIA GPU | `pip install "cactus-needle[gpu]"` | CUDA |
| Apple Silicon GPU | `pip install "cactus-needle[metal]"` | M5 Max 比 CPU 快 ~4× |

### 1.9 损失曲线解读

> **关键**：损失覆盖的是推理行 + JSON 调用目标。大量 JSON 是模型已会预测的样板文本（工具名、花括号、字段名），所以损失从 ~1.0 开始而非随机。

**判断标准**：看趋势而非绝对值。

| 现象 | 含义 | 对策 |
|------|------|------|
| 损失卡在起始值 | 欠训练 | 先加 epochs，再调学习率 |
| 训练损失降 / 验证损失升 | 过拟合 | 停止或加数据 |
| 工具选对了但参数值错 | 数据太小或太单一 | 加数据，考虑 --lora-rank 32 |
| 所有请求都返回 "Sorry" | 旧版引擎置信度门控 bug | 升级到 engine 2.0.1+ |

**数据规模建议**：

```
200 样例 × batch 16 = 13 steps/epoch × 3 epochs = 39 steps → 几乎不动
→ 几百样例跑 10-30 epochs 才有清晰下降趋势
→ 几百样例即可提升工具选择
→ 几千样例才能改善参数论证
```

---

## 二、查询拓展

### 2.1 Byte-Level Grammar 编译

Needle 的核心安全机制不是"告诉模型遵守约束"，而是**在解码层面让违规输出语法上不可能存在**。

实现链路：JSON schema → `Field` 约束 → 字节级 grammar 编译 → 解码时强制约束。这意味着：
- 枚举值只能选声明的选项
- 数值范围不能越界
- 正则模式必须匹配
- 字符串长度不能超过上限

这个机制与 vLLM 的 grammar-constrained decoding、OpenAI Chat Completions API 的 `response_format` 语法类似，但 Needle 是**内置编译到引擎中**，不需要外部库。

### 2.2 System Facts 的设计哲学

> System turn 传递环境状态作为**事实**（facts），不是**指令**（instructions）。

```
system="date: 2026-08-21; locale: en-US; device: phone; battery: 62%"
```

- 识别的 key：`date` / `locale` / `device` / `battery` / `network` / `location` / `user` / `assistant`
- 相对语言解析：`"tomorrow at 7"` 只在有 `date:` fact 时才解析为绝对时间
- **在 system 中放指令不会 steering 模型**（训练时就明确不响应指令）

### 2.3 Tool Retrieval 的指纹机制

`tool_index_path` 持久化嵌入索引，按 schema 的**指纹**（fingerprint）做键。指纹匹配时即时加载；schema 变化时只重新嵌入变化部分。这意味着：
- 大型工具集（几百个工具）的初始化成本是 O(1)（已有指纹）而非 O(n)
- 添加/删除单个工具不影响其他工具的嵌入

---

## 三、归纳总结

### 3.1 Needle 2 API 设计哲学

```
┌─ 输入层 ─────────────────────────────┐
│  装饰函数 / Pydantic / JSON schema     │
│  System facts（环境状态，非指令）       │
├─ 推理层 ─────────────────────────────┤
│  Byte-level grammar（语法层面约束）      │
│  Tool retrieval（>5 工具时自动检索）    │
│  Confidence gating（双信号校准）         │
├─ 输出层 ─────────────────────────────┤
│  function_calls（结构化调用）           │
│  reasoning（参数推导过程）              │
│  confidence（0-1 校准分数）             │
├─ 循环控制 ──────────────────────────┐
│  run() 全自动 / complete() 手动单步     │
│  空调用 [] = 主题外（非自由文本道歉）   │
│  256 token 滑动窗口（工具作为 KV sink） │
└───────────────────────────────────────┘
```

### 3.2 决策树：何时用 Needle

```
任务 = 工具调用 / 结构化抽取 / 设备控制？
  ├─ 是
  │   ├─ 需要多模态（图片/视频）？ → 否（Needle 仅文本）
  │   ├─ 需要长上下文（>256 token）？ → 否
  │   ├─ 需要 >50 个工具？ → 考虑两次调用（检索+调用分离）
  │   ├─ 需要离线/资源受限部署？ → Needle 2 是最强选择
  │   └─ 需要自定义工具集？ → LoRA 微调（几十分钟出效果）
  └─ 否（需要通用文本生成） → 不选 Needle
```

### 3.3 与竞品的尺寸-性能前沿

> Needle 2 以 14MB/45M 参数在 FunctionGemma 270M、LFM2.5 230M、Apple FM 的对标基准中"trades wins"（有来有回），体积只有它们的 5×-70×。

关键差异不是精度而是**工程范式**：
- FunctionGemma / LFM：需要单独的模型文件 + 推理框架
- Apple FM：需要 Apple 生态绑定
- **Needle**：单二进制 + 内置引擎 + 内置 grammar 编译 + 离线可用

---

## 四、趋势判断

### 趋势 1：端侧工具调用将催生专用小模型类别

> 依据：Needle 2 证明了 14MB/28MB 内存可以在端侧完成完整的工具调用闭环（选工具→填参数→语法约束→置信度门控）。这比"小语言模型"定位更窄但更精确。

未来会出现一批**专用工具调用模型**（而非通用小模型），类比浏览器/数据库引擎——不需要多强，只需要在特定任务上做到极致。

### 趋势 2：Grammar-Constrained Decoding 将从边缘走向主流

> 依据：Needle 将 grammar 编译到引擎层，OpenAI `response_format` 提供了外部接口，vLLM 也支持 grammar decoding。

三年后，**"语法约束"将成为 API 设计的默认选项**——不是可选的优化，而是正确性的保障。尤其在金融、医疗、法律等对输出格式有严格要求的场景。

### 趋势 3：置信度门控将成为 Agent 可靠性的核心组件

> 依据：Needle 设计了双信号校准 + 升级而非错误执行的失败模式。这是 Agent 从"能工作"到"能信任"的关键一步。

未来 Agent 框架需要把置信度从"可选字段"变成"必选组件"，配合 fallback 机制（低置信度 → 人工审核 / 路由到更大模型）。

### 趋势 4：离线 AI 部署将成为硬件设计的默认选项

> 依据：Needle 的离线部署方案（single binary + air gap + `HF_HUB_OFFLINE=1`）覆盖了从开发机到嵌入式设备的全链路。

随着 IoT 设备、汽车、医疗等场景对数据主权的要求提高，**离线 AI 将成为硬件平台的标配而非加分项**。

---

## 五、关联分析

### 5.1 与 [2026-08-14-Needle2-极简端侧AIoT模型架构.md](2026-08-14-Needle2-极简端侧AIoT模型架构.md) 的关联

那篇笔记侧重**架构层**（SAF 创新、Hadamard MLP、Engram KV、CQ2 量化、28MB 内存分析），本篇侧重**工程层**（API 契约、工具声明方式、置信度门控、离线部署、微调参数）。

**互补关系**：架构决定"为什么能做到"，API/工程决定"怎么用起来"。两篇合起来构成 Needle 2 的完整理解图谱。

### 5.2 与 [2026-08-07-MoE与MMoE模型全解-从1991到2026两条技术路线.md](2026-08-07-MoE与MMoE模型全解-从1991到2026两条技术路线.md) 的关联

MoE 路线是"参数大但激活少"（DeepSeek V3 671B/37B 激活），Needle 路线是"参数极少但架构创新"（45M 全激活 + SAF）。

**对比意义**：AI 模型的"更小更强"有两条路——MoE 靠路由，Needle 靠架构简化 + 量化。端侧场景 Needle 路线更优（单卡/单设备可跑），数据中心场景 MoE 路线更优。

### 5.3 与 [2026-08-12-LLM推理时扩展七大方法分类与工业实践.md](2026-08-12-LLM推理时扩展七大方法分类与工业实践.md) 的关联

那篇讲推理时扩展的七大方法（CoT → Self-Consistency → Best-of-N → Rejection → Self-Refinement → MCTS → 组合）。Needle 的 `reasoning` 字段本质上是**内置的极简 CoT**——每个参数从源 span 的推导过程。

**差异**：Needle 的 reasoning 是**语法约束下的结构化推导**（`'kitchen' -> room; 'dim to 10' -> brightness 10`），而非自由文本推理。这是对 CoT 的端侧精简版。

### 5.4 与 [2026-08-18-主流LLM微调方法全景-全参-LoRA-QLoRA-DoRA-SFT-DPO-GRPO.md](2026-08-18-主流LLM微调方法全景-全参-LoRA-QLoRA-DoRA-SFT-DPO-GRPO.md) 的关联

那篇覆盖通用 LLM 微调方法全景，Needle 的微调是**专用微调**——只微调五个 attention 投影的 LoRA rank 16，合并后导出单文件 .cact。

**关键差异**：
- 通用 LoRA：改 Q/K/V/O/输出投影，需要 vLLM/TensorRT 加载
- Needle LoRA：改 SAF 五投影，合并回 base + 量化 + 导出单二进制

### 5.5 与 [2026-08-20-LLM后训练RL效率与可靠性-RLVR调度Debate抗Hack与ES换道.md](2026-08-20-LLM后训练RL效率与可靠性-RLVR调度Debate抗Hack与ES换道.md) 的关联

后训练的可靠性问题（reward hacking / mode collapse）在 Needle 的**置信度门控**中有对应工程解——双信号校准 + 升级而非错误执行。这是后训练可靠性在**部署层**的工程落地。

### 5.6 与 Hermes Agent 的关联

Hermes 的 Skill 系统本质上是 Needle 的"工具声明"的宏观版：
- Hermes Skill = 一个带文档 + 前置知识 + 工具调用的封装
- Needle tool = 一个带 schema + grammar 约束的函数

**差异**：Hermes Skill 面向人类 Agent 的阅读 + 执行，Needle tool 面向模型推理的语法约束。两者在"结构化能力封装"这一设计哲学上一致，但目标运行时不同。

---

## 六、拓展应用推荐

### 6.1 立即可做的 Needle 集成实验

- **飞书消息路由**：把 WorkBuddy 风格的"只读问答/计划/执行"三模式用 Needle 实现——声明三个工具（ask/plan/execute），用 confidence 阈值决定是否自动执行
- **HomeAssistant 自动化**：Needle 的离线部署 + 工具调用完美适配智能家居场景——声明灯光/空调/窗帘工具，Grammar 约束范围，confidence gating 做安全门控
- **发票/收据抽取**：用 `needle.extract()` + Pydantic 做离线票据 OCR 后处理，无需联网
- **Hermes 本地 STT 辅助**：将 Needle 部署到 Jetson 上作为 STT 结果的结构化后处理器

### 6.2 微调用例清单

| 场景 | 数据规模 | LoRA 配置 | 预期效果 |
|------|----------|-----------|----------|
| 智能家居控制（5-10 工具） | 200 样例 | rank 16, 10 epochs | 工具选择准确率显著提升 |
| 发票抽取 | 500 样例 | rank 16, 15 epochs | 字段抽取准确率提升 |
| 多语言工具调用 | 2000+ 样例 | rank 32, 30 epochs | 参数论证质量改善 |
| 专业领域（医疗/法律） | 1000+ 样例 | rank 32, 20 epochs | 领域术语理解 + 工具选择 |

### 6.3 适合跟进的学习方向

- **arXiv:2607.18363 论文精读** — SAF 架构的完整数学推导 + ablation 实验
- **Cactus Quants 量化算法** — 2-bit 自适应量化的具体实现
- **Tool Retrieval 的对比头设计** — 如何在 45M 模型内置嵌入 + 检索
- **Grammar-Constrained Decoding 实现** — 从 JSON schema 到字节级 grammar 的编译过程

---

## 七、指南分析

### 7.1 Needle 2 的工程优势

- **单二进制部署**：14MB `.cact` 文件直接塞进固件，无需模型文件管理、无需推理框架安装
- **语法级安全**：不是"请求模型遵守约束"而是"语法上不可能违规"
- **置信度门控**：校准后的置信度 + 升级而非错误执行的失败模式
- **离线能力**：一次下载后完全不碰网络，覆盖 air gap 设备
- **微调门槛低**：JAX 原生，CPU 可调，几十分钟出 .cact

### 7.2 局限性与适用边界

| 限制 | 影响 | 适用性判断 |
|------|------|------------|
| 256 token 窗口 | 无法处理长文档/长对话 | ❌ 长上下文 RAG、多轮对话、长推理 trace |
| 仅文本 | 不支持图片/视频输入 | ❌ 视觉理解、图片标注、视频摘要 |
| 单一模型 | 无模型路由/多模型组合 | ❌ 需要多模型协作的复杂 Agent |
| 工具选择上限 | >50 工具需两次调用 | ⚠️ 超大规模工具集需架构设计 |
| 非英语 token 膨胀 | 非英语 ~1.7× token 数 | ⚠️ 中文/日文/韩文场景窗口压缩 |

### 7.3 与 Hermes 集成的建议

- **短期**：在 Hermes 的工具调用层集成 Needle 作为**置信度门控的参考实现**——借鉴其双信号校准 + 升级而非错误执行的失败模式
- **中期**：将 Needle 部署到 Jetson 上作为**本地结构化抽取引擎**——离线发票/票据/文档字段提取
- **长期**：观察 Needle 后续版本（3.0+）是否扩展到多模态/长上下文，评估是否纳入 Hermes 的端侧 Agent 能力栈

---

## 八、金句摘录

> "Needle solves every problem as a function call. The context declares what may be called; the model answers with calls."

> "Arguments contain only values evidenced by the input. An optional field with no evidence is omitted, not guessed."

> "A call is accepted only when both [confidence signals] agree, so the failure mode is escalation, not wrong execution."

> "Describe each argument and offer choices. Needle reads your tool descriptions to decide what to call and how to fill arguments, so describing them well is the whole game."

> "Training starts near 1.0 rather than near random. Judge a run by its trend, not its level."

---

## 九、行动启示

- **下载 Needle 并跑通 Quickstart**：`pip install cactus-needle` → 声明一个工具 → `agent.run()` → 观察 confidence 和 reasoning
- **在 Hermes 工具调用层借鉴 confidence gating 模式**：每次工具调用附带校准置信度，低于阈值走升级路径
- **评估 Needle 在 Jetson 上的部署可行性**：作为本地结构化抽取引擎，离线票据/文档处理
- **关注 arXiv:2607.18363 论文**：SAF 架构的设计原理可能影响 Hermes 自身的 Agent 架构设计
- **记录在 error-case-library**：如果尝试集成遇到"非英语 token 膨胀"或"置信度不准"，沉淀为已知坑

---

> **延伸阅读**：
> - [Needle 2 架构笔记](2026-08-14-Needle2-极简端侧AIoT模型架构.md) — SAF/CQ2/Engram KV 架构层
> - [LLM 推理时扩展七大方法](2026-08-12-LLM推理时扩展七大方法分类与工业实践.md) — reasoning 与 CoT 的关联
> - 论文：[arXiv:2607.18363](https://arxiv.org/abs/2607.18363) — Simple Attention Network
> - API 文档：[doc/apis.md](https://github.com/cactus-compute/needle/blob/main/doc/apis.md)
> - 微调文档：[doc/finetuning.md](https://github.com/cactus-compute/needle/blob/main/doc/finetuning.md)


## 相关笔记

- [Kimi K3 + Blender MCP](2026-08-21-KimiK3-BlenderMCP-能看能改的3D场景Agent工作流.md) — 另一 Agent 工具生态案例
- [Qwen3.8-27B FP8 推理指南](2026-08-21-Qwen3.8-27B-FP8使用指南-三条推理路线完整代码.md) — 推理部署与 LoRA 微调关联
- [DeepSeek Harness 四种 Agent 预设](2026-08-20-DeepSeekHarness四种Agent预设与性能实测.md) — Agent 框架对比