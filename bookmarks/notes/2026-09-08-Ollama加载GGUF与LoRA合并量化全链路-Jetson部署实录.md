# Ollama 加载 GGUF 与 LoRA 合并量化全链路解析（Jetson 部署实录）

> **来源**：通义千问分享对话「助理千问自我介绍及服务场景」（qianwen.my.cn 分享链，实际内容为 GGUF/LoRA 技术问答）
> **原文链接**：https://qianwen.my.cn/share/chat/b81a8d9b2732491e91a14ecaeee97873
> **本地对照源**：AirCraft 项目 merge.py 实况、Jetson Orin 实测内存
> **记录日期**：2026-09-08
> **⚠️ 标注约定**：〔千问原文〕= 分享对话内容；〔本地对照〕= 本机实测/AirCraft 项目实况；〔增量分析〕= 本笔记补充

**标签**：#GGUF #Ollama #LoRA合并 #量化 #llama-cpp #Jetson部署 #AutoDL #边缘推理

---

## 一、内容整理

### 1.1 对话场景与结论〔千问原文〕

对话起于一个 Jetson 部署容量评估：**可行但紧张**——Q4_K_M 约 1.5GB + KV cache ~0.3GB ≈ 1.8GB，挤在 2.2GB 可用内存内。用 ollama 加载后关闭即可。

操作链路：启动 AutoDL → merge LoRA + 量化 GGUF（~1.5GB Q4_K_M）→ 下载 GGUF 到 Jetson → 启动 ollama → 加载模型。

随后展开两个核心问题的详细解析：①Ollama 为什么只认 GGUF；②merge LoRA + 量化 GGUF 是什么过程。

### 1.2 为什么 Ollama 加载量化模型必须是 GGUF〔千问原文〕

**核心比喻**：Ollama 本质是一个"播放器"，GGUF 是它唯一能读懂的"磁带"格式。

1. **底层架构决定**：Ollama 底层推理引擎基于 llama.cpp 构建；llama.cpp 定义了 GGUF（GPT-Generated Unified Format）标准，任何模型转成 GGUF 就能被识别运行。
2. **专为本地推理设计**：与 HF 训练用的 PyTorch 格式（.safetensors）不同，GGUF 是为 CPU/边缘设备本地推理设计的二进制格式——把权重、架构配置（层数/注意力头数）、分词器（Tokenizer）打包进单一文件。
3. **极致的加载与运行效率**：支持 mmap 内存映射——操作系统按需把文件内容分页映射进内存，而非一次性全量加载。大幅提升加载速度、降低内存开销。
4. **灵活的量化支持**：原生支持多种量化方案（Q4_K_M/Q8_0 等），7B 模型可从 14GB 压到约 3.5GB，适配显存受限设备。

### 1.3 Merge LoRA 的数学原理与过程〔千问原文〕

- LoRA 训练时不修改原始大模型参数，只训练低秩适配器（Adapter）。
- 推理时输出 = 原始权重 W₀ + LoRA 路径（缩放后的 BA）。
- **Merge 操作**：计算权重更新量 ΔW = (α/r)·BA，直接加到原始权重矩阵上：
  **W_merged = W₀ + ΔW**
- **目的**：合并后适配器不再单独加载，模型成为包含新知识的独立完整模型——简化部署、提高推理速度、兼容不支持动态加载适配器的系统。

### 1.4 量化 GGUF 的转换与压缩〔千问原文〕

- 合并后模型通常是 FP16/BF16，体积庞大，无法直接在边缘设备运行。
- 用 llama.cpp 脚本或 Unsloth 框架将合并模型序列化导出 GGUF：16 位（2 字节）浮点参数压缩为 4 位整数（Q4_K_M）。
- 以极小精度损失换巨大体积缩减和推理加速。

**一句话总结**（原文）：merge LoRA + 量化 GGUF = 把"微调知识"永久注入底座，并打包压缩成 Ollama 能在 Jetson 上高效运行的"磁带"。

### 1.5 AutoDL 完整命令流程（LLaMA-Factory 版）〔千问原文〕

**第一步：Merge LoRA**
```yaml
# merge_lora.yaml
model_name_or_path: /路径/Qwen1.5-1.8B-Chat     # 必须是未量化的完整基座
adapter_name_or_path: /路径/lora/train_2024-xx-xx
template: qwen                                    # 必须与训练时一致
finetuning_type: lora
export_dir: /路径/Qwen1.5-1.8B-Chat-merged
export_size: 4
export_device: cuda
export_legacy_format: false
```
```bash
llamafactory-cli export merge_lora.yaml
```

**第二步：准备工具**
```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
python -m venv llama-venv && source llama-venv/bin/activate
pip install -r requirements/requirements-convert_hf_to_gguf.txt
```

**第三步：转换 + 量化**
```bash
python convert_hf_to_gguf.py /路径/Qwen1.5-1.8B-Chat-merged \
  --outfile Qwen1.5-1.8B-Chat-F16.gguf
./llama-quantize Qwen1.5-1.8B-Chat-F16.gguf Qwen1.5-1.8B-Chat-Q4_K_M.gguf Q4_K_M
```

**第四步：Jetson 部署**
```dockerfile
# Modelfile（TEMPLATE 必须与训练 chat_template 一致，否则输出乱码）
FROM ./Qwen1.5-1.8B-Chat-Q4_K_M.gguf
TEMPLATE """{{ if .System }}system
{{ .System }}
{{ end }}{{ if .Prompt }}user
{{ .Prompt }}
{{ end }}assistant
{{ .Response }}"""
PARAMETER temperature 0.7
```
```bash
ollama create my-fine-tuned-model -f Modelfile
ollama run my-fine-tuned-model
```

---

## 二、查询拓展

### 2.1 Q4_K_M 的 "K_M" 到底是什么

Q4_K_M = 4-bit Quantization + K-quant + Medium mix。llama.cpp 的 K-quant 系列不是简单均匀量化：把权重张量按重要性分层——关键层（如 attention 的 wq/wk）保留更高精度（Q6_K），次要层（部分 FFN）用 Q4_K，混合成 Medium 档。相比老的 Q4_0 均匀量化，Q4_K_M 在同体积下困惑度（ppl）显著更低，是社区公认的"质量-体积甜点"（默认推荐档）。档位谱系：Q2_K（极限压缩）→ Q3_K_M → **Q4_K_M（甜点）** → Q5_K_M → Q6_K → Q8_0（近乎无损）→ F16（不量化）。

### 2.2 mmap 内存映射为什么是 GGUF 的杀手锏

传统加载：整个模型文件读入内存 → 2GB 模型就要占 2GB RSS。mmap：文件被映射到虚拟地址空间，**操作系统按需分页加载**（_page fault 时才真正读磁盘）——好处有三：①冷启动快（不用等全量读盘）；②多进程共享同一映射（Ollama 并发请求共享权重页）；③未被访问的权重页可被内核回收再分配。这正是千问原文说"大幅提升加载速度并降低内存开销"的机制本质。对 Jetson 这种内存紧张设备（可用 2.2GB），mmap 是"挤得进"的关键技术。

### 2.3 LoRA 合并的精度陷阱：为什么必须在完整精度基座上 merge

千问原文化调"合并必须在完整的、未量化的基础模型上进行"，原因：ΔW = (α/r)·BA 的计算和加法在 FP16/FP32 下进行，若基座已量化（如 Q4），W₀ + ΔW 的加法对象是反量化后的有损值，合并结果会叠加量化误差，且无法再干净地重新量化。**正确顺序铁律：FP 基座 → merge → 再量化**。顺序错了只能从基座重来。AirCraft 项目的 merge.py 正是这么做的（float32 加载 + merge_and_unload + 健康检查 NaN/Inf/max_abs）。

### 2.4 Ollama 的 Modelfile 三要素

Modelfile 是 Ollama 的模型描述文件（类比 Dockerfile）：FROM（GGUF 路径/仓库模型）、TEMPLATE（chat 模板——必须与训练模板一致）、PARAMETER（推理参数）。**TEMPLATE 不一致的后果是输出乱码/复读**——因为模型的 chat 标记（如 `<|im_start|>`）是训练时固化在 tokenizer 行为里的，推理时换模板等于让模型读一门没学过的语言。这就是千问原文反复强调"必须与训练时的 chat_template 一致"的原因。

### 2.5 本地部署现状对照〔本地对照〕

Jetson Orin 实测（2026-09-08）：

```
内存:  total 7.4Gi | used 4.9Gi | available 2.2Gi | swap 11Gi(用3.3Gi)
ollama: ✅ 已安装(/usr/local/bin/ollama)
llama.cpp 工具链: 未装(llama-cli/llama-quantize 不在 PATH)
```

千问对话中"2.2GB 可用"与本次实测**完全一致**（available 2.2Gi）——该对话就是针对本机做的容量评估。Q4_K_M 1.5GB + KV cache 0.3GB ≈ 1.8GB 的方案在当前内存占用下成立，但余量仅 ~0.4GB，若同时跑 LuxTTS/RL 推理会挤爆——需要 swap 兜底或错峰使用。

---

## 三、归纳总结

### 3.1 全链路一张图：从 LoRA 适配器到 Jetson 运行

```
[训练侧 - AutoDL/GPU机]
LoRA adapter (4.6MB, r=16)
   +
FP基座 (103MB FP32 / 3.7GB FP16)
   │ ① merge: W_merged = W₀ + (α/r)·BA    ← 必须FP精度,顺序铁律
   ▼
完整模型 (HF格式, 含微调知识)
   │ ② convert_hf_to_gguf.py → F16.gguf   ← 序列化+打包权重/config/tokenizer
   ▼
F16 GGUF (单文件)
   │ ③ llama-quantize → Q4_K_M.gguf       ← 16bit→4bit, 体积÷4
   ▼
Q4_K_M GGUF (~1.5GB for 2B模型)
   │ ④ scp → Jetson
   ▼
[部署侧 - Jetson]
Modelfile (FROM + TEMPLATE + PARAMETER)
   │ ⑤ ollama create / run
   ▼
mmap 加载 → 内存占用 ≈ 模型体积 + KV cache
```

### 3.2 两种 merge 路线对照〔增量分析〕

```
路线                工具                     适用
────────────────────────────────────────────────────────────
PEFT 原生路线       merge_and_unload()       AirCraft 在用: 26M小模型,
                    (AirCraft merge.py)      3行核心代码,自带权重健康检查
LLaMA-Factory路线   llamafactory-cli export  千问推荐: 生产级,YAML配置,
                                             支持export_size分卷/export_device加速
```

AirCraft 的 PEFT 路线已含千问流程的全部要素（FP 加载→merge→健康检查→保存），对 26M 模型足够；若未来升级到 Qwen 级 2B 模型，LLaMA-Factory 的 YAML 化管理更省心。

### 3.3 方法论提炼

- **格式即生态**：GGUF 之于 llama.cpp = SafeTensors 之于 HF——容器格式决定分发路径，分发路径决定部署生态。
- **顺序不可逆**：merge 必须在量化前（FP 精度加法），量化后无法干净 merge。
- **模板即语言**：推理 TEMPLATE 与训练 chat_template 不一致 = 让模型读外语，输出必然乱码。
- **内存账要算三层**：模型体积 + KV cache（随上下文长度增长）+ 运行时开销——千问对话的 1.5+0.3≈1.8GB 算法是正确范式。

---

## 四、趋势判断

### 趋势1：LoRA→GGUF 部署链正在工具化收敛，个人微调模型端侧部署成为标准动作

依据：LLaMA-Factory 一条 YAML + llama.cpp 两条命令 + Ollama 一个 Modelfile，全链路已无任何需要手写的胶水代码。Unsloth 进一步把 merge+量化+导出合并成单 API。门槛已从"懂原理的工程师"降到"会跑命令的爱好者"。

### 趋势2：边缘设备内存评估成为端侧部署的第一道关卡

依据：千问对话的完整起点就是一个内存容量算术（1.5+0.3 vs 2.2GB）。Jetson/树莓派级设备的 LLM 部署决策 = 量化档位选择（Q2~Q8）× 上下文长度（KV cache）× 并发数的三角权衡。mmap 让"挤得进"成为可能，但推理速度仍受内存带宽硬约束。

### 趋势3：量化档位将出现"自动选择器"

依据：目前 Q4_K_M 是社区默认甜点，但最优档位实际取决于模型规模/任务容差/设备带宽。llama.cpp 的 ppl 回归测试工具已能评估各档位质量损失——"给设备画像→自动推荐档位"的工具化是显然的下一步（类似 NNCF/AutoQ 的普及路径）。

---

## 五、关联分析

### 5.1 与「推理生态架构差异」笔记的直接续篇关系

上一篇（Transformers vs llama.cpp）讲两生态**为什么分野**；本篇讲分野之后**如何跨越**——merge+量化+GGUF 就是从 HF 生态进入 llama.cpp 生态的"移民通道"。两篇构成"理论→实操"上下集。

### 5.2 与 AirCraft 项目的逐条对照〔本地对照〕

| 千问流程步骤 | AirCraft 现状 | 差距 |
|---|---|---|
| ① merge（FP 基座） | ✅ merge.py 已做（float32 + merge_and_unload + 健康检查） | 无 |
| ② convert GGUF | ❌ 未做 | minimind 需走 llama.cpp 的 convert_hf_to_gguf.py |
| ③ 量化 Q4_K_M | ❌ 未做 | 26M 模型量化收益小，可先 F16/Q8 |
| ④ Modelfile + ollama | ❌ 未做 | 本机已装 ollama，只差 Modelfile |
| 内存评估 | ✅ 2.2GB available 实测一致 | 26M 模型毫无压力 |

**结论**：AirCraft 距离"ollama 跑通"只差 ②③④ 三步命令，且因模型只有 26M，量化步骤甚至可跳过（F16 GGUF 仅 ~100MB）。这正是 MiniMind 笔记"路线 A"的最后一段。

### 5.3 与 MiniMind 全管线笔记的衔接

MiniMind 笔记案例 07 的六条导出路径中，GGUF 路径的操作细节当时只有一行命令；本篇补全了完整四步流程（merge→convert→quantize→Modelfile），两篇合起来 = 领域微调模型端侧部署的完整手册。

### 5.4 与 sensenova-pool / DUCK-Pi_5 的资源管理同构

千问对话开头的"可行但紧张"内存评估，与 DUCK-Pi_5 训练前的 GPU 显存评估、sensenova-pool 的 key 池容量管理是同一思维：**部署前先算资源账，算完账再动工**。三层账本：模型账（体积/精度）× 上下文账（KV cache）× 并发账（吞吐）。

---

## 六、金句摘录

> 「Ollama 本质上是一个'播放器'，而 GGUF 就是它唯一能读懂的'磁带'格式。」〔千问原文〕— 最易懂的 Ollama×GGUF 绑定关系比喻。

> 「merge LoRA + 量化 GGUF，实际上就是把'微调知识'永久注入底座，并打包压缩成 Ollama 能够直接在 Jetson 上高效运行的'磁带'。」〔千问原文〕— 全流程的一句话压缩。

> 「TEMPLATE 必须与训练时的 chat_template 一致，否则输出会乱码。」〔千问原文〕— 最容易被忽视的部署坑，模板即语言。

> 「合并操作必须在完整的、未量化的基础模型上进行。」〔千问原文〕— merge 顺序铁律，反了就只能从基座重来。

---

## 七、行动启示

```
启示                              行动
────────────────────────────────────────────────────────────────
AirCraft 距 ollama 只差三步       ①convert_hf_to_gguf.py 转 minimind
(且26M模型可跳过量化)             -am-merged → F16.gguf (~100MB)
                                  ②写 Modelfile(TEMPLATE 用
                                  MiniMind的### Instruction格式)
                                  ③ollama create + run 验证
内存账算法要沉淀                  Q4_K_M体积+KV cache(0.3GB量级)
                                  +运行时开销 = 三层账本,
                                  部署任何模型前先算
merge 顺序铁律进 error-case       已入 AirCraft README;若未来
                                  在已量化基座上merge翻车,
                                  记得这条铁律
TEMPLATE 一致性校验               ollama 部署前 diff 训练模板
                                  与 Modelfile TEMPLATE
```

---

## 八、拓展应用推荐

- **立即可做（AirCraft 路线 A 收尾）**：`git clone llama.cpp` → `pip install -r requirements-convert_hf_to_gguf.txt` → `convert_hf_to_gguf.py ~/uclaw/project/AirCraft/AM_LoRA_offline/minimind-am-merged --outfile minimind-am-F16.gguf` → 写 Modelfile → `ollama create aircraft-am -f Modelfile`。全程本机可跑，无需 AutoDL（26M 模型 merge 早已完成）。
- **量化档位实验**：26M 模型可做 Q8_0 vs F16 vs Q4_K_M 三档 ppl 对比（llama-perplexity 工具），观察超小模型对量化的敏感度——大模型 Q4 几乎无损，26M 可能 Q4 就明显掉点，这个实验本身有价值。
- **LLaMA-Factory**：若 AirCraft 升级路线 B（minimind-3 64M）或路线 C（Qwen 级），直接用 LLaMA-Factory 的 merge_lora.yaml 流程，比手写 PEFT 脚本省心。
- **延伸阅读**：llama.cpp 量化文档（K-quant 各档位 ppl 对照表）；PEFT merge_and_unload 源码（理解 ΔW 加法细节）；Ollama Modelfile 官方文档（TEMPLATE/PARAMETER 全参数）。

---

## 九、指南分析

**阅读与使用指南：**

1. **文体定性**：千问 AI 对话实录，标题（"助理千问自我介绍"）与内容（GGUF/LoRA 技术问答）不符——分享页标题取自对话开场白而非主体内容，检索时注意。技术内容本身质量高：数学公式（ΔW=(α/r)BA）正确、流程命令可执行、"播放器/磁带"比喻精准。
2. **可信度判读**：四个技术要点（GGUF 绑定原因/mmap 机制/merge 数学/量化流程）全部经得起推敲，与本机实况（ollama 已装、2.2GB available、AirCraft merge.py 已做）交叉一致。LLaMA-Factory YAML 和 llama.cpp 命令与两方官方文档一致。
3. **本笔记增量**：①用 AirCraft merge.py 逐条对照千问流程，量化了"距离 ollama 只差三步"的现状；②补 K-quant 档位谱系（Q4_K_M 的 K/M 含义）、mmap 三好处、merge 精度陷阱的机理；③本机内存实测与对话说法互相印证（2.2GB 完全一致）；④给出 26M 模型可跳过量化的判断（F16 GGUF 仅 100MB）。
4. **风险提示**：千问对话中的模型是 Qwen1.5-1.8B（示例），AirCraft 是 MiniMind 26M——流程同构但参数要换；MiniMind 的 TEMPLATE 是 `### Instruction/### Response` 格式而非 Qwen 的 im_start 格式，Modelfile 必须相应改写，直接抄千问的 TEMPLATE 会乱码。
5. **最佳使用方式**：把本笔记当作 AirCraft 路线 A 的施工图——第五节对照表就是差距清单，第八节第一条就是可直接复制的命令序列。

## 相关笔记

- [2026-09-08-大模型推理生态架构差异-Transformers与llamacpp](./2026-09-08-大模型推理生态架构差异-Transformers与llamacpp.md) — GGUF 部署链的架构哲学层（通用解释 vs 专用编译）
- [2026-09-08-Qwen3.8本地运行全指南-Unsloth量化版实测手册](./2026-09-08-Qwen3.8本地运行全指南-Unsloth量化版实测手册.md) — 量化档位选型参照
- [2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例](./2026-09-08-MiniMind从零训练极小语言模型-全管线与7阶段案例.md) — LoRA 训练上游，本笔记部署下游
