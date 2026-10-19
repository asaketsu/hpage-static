# Unsloth与LLaMA-Factory双框架实战 — 消费级显卡微调的两条路线：快省流vs全方法流

#Unsloth #LLaMA-Factory #微调 #LoRA #QLoRA #GRPO #DPO #PPO #消费级显卡 #显存优化 #TritonKernel #trl #PEFT #SFTTrainer #llamafactory-cli #WebUI #模型合并 #GGUF #vLLM #新手友好 #进阶

> **出处**：两个工具的官方仓库/Notebook 实抓（2026-08-19）：unslothai/unsloth README + Llama3.1(8B)-Alpaca 官方 notebook（31 cells）+ hiyouga/LLaMA-Factory README + examples/train_lora 全目录
> **定位**：使用方法与流程的**实操级对照笔记**——每条命令/代码都来自官方一手来源，不是转述
> 用户给的画像：Unsloth=消费级显卡优化+一键量化+界面友好适合新手，核心"快+省"（快2倍/省70%显存）；LLaMA-Factory=功能全面（LoRA/QLoRA/PPO/DPO等），适合进阶

## 一、内容整理

### 1. 全景对照表（先给结论）

| 维度 | Unsloth | LLaMA-Factory |
|---|---|---|
| 定位 | 微调加速库（drop-in 替换 HF 训练） | 全流程微调框架（训练→评估→部署） |
| 形态 | **三种**：Unsloth Desktop（桌面App）/ Unsloth Studio（Web UI，`unsloth studio -p 8888`）/ Unsloth Core（代码） | **两种**：llamafactory-cli（YAML 驱动）/ LLaMA Board WebUI（`llamafactory-cli webui`，Gradio） |
| 核心卖点 | 快+省：官方数据 2x faster / 70% less VRAM（gpt-oss 20B、Llama3.1 8B 等多数模型；MoE 12x faster / 35% less；新 packing 3x faster / 30% less） | 方法全：**预训练/SFT/多模态SFT/Reward Modeling/PPO/DPO/KTO/ORPO/SimPO** 九种训练 stage 全支持，模型 100+（Day-0/Day-1 支持新模型：Qwen3/Gemma 3/GLM-4.1V/Llama 4…） |
| 使用入口 | Python API（`FastLanguageModel`） | YAML 配置 + CLI 三连（train/chat/export） |
| 数据格式 | HF datasets + prompt 模板函数（alpaca 格式） | alpaca/sharegpt 等格式 + `dataset_info.json` 注册 |
| 产出 | LoRA adapters / merged_16bit / merged_4bit / **GGUF（q8_0/f16/q4_k_m 一行）** | LoRA 合并导出 / **GPTQ/AWQ 量化导出 / Ollama modelfile** / vLLM OpenAI API 部署 |
| 分布式 | 弱项（单卡/少量卡优化为主） | 强项：多机多卡（torchrun/NNODES/Ray）+ DeepSpeed ZeRO-3 + 弹性容错（MAX_RESTARTS）+ NPU 后端 |
| 量化方案 | bnb-4bit 预量化模型（下载快4倍+防OOM） | 4/8bit bnb/HQQ/EETQ + GPTQ + AWQ + **2bit AQLM** |
| RL 训练 | GRPO/GSPO（含 Vision RL、FP8、7x长上下文RL、500K context） | PPO/DPO/KTO/ORPO/SimPO + GRPO（姊妹项目 EasyR1 专做 GRPO） |
| 适合谁 | 新手/单卡用户/要 GGUF 落地 llama.cpp-Ollama 的人 | 进阶用户/要偏好对齐全流程/多卡集群/企业部署的人 |

### 2. Unsloth 使用流程（官方 notebook 实录）

**形态三选**：
```
Unsloth Desktop → 下载桌面App（图形界面）
Unsloth Studio  → unsloth studio -p 8888（Web UI，localhost 绑定；--secure 走 Cloudflare HTTPS 隧道，fail-closed）
Unsloth Core    → 代码方式（下述）
```

**安装（Core，uv 推荐）**：
```bash
uv venv unsloth_env --python 3.13
uv pip install unsloth --torch-backend=auto
# RTX 50x/B200/Blackwell 同上；Windows 需先装 PyTorch
```

**五步流程（Llama3.1-8B-Alpaca 官方 notebook，逐 cell 提取）**：

```python
# ① 载入4bit量化模型（核心：用官方预量化模型，下载快4倍+防OOM）
from unsloth import FastLanguageModel
import torch
max_seq_length = 2048      # 内部自动 RoPE Scaling
dtype = None               # None=自动检测（T4/V100→fp16, Ampere+→bf16）
load_in_4bit = True

fourbit_models = [
    "unsloth/Llama-3.1-8B-bnb-4bit",
    "unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    "unsloth/Mistral-Nemo-Instruct-2407-bnb-4bit",  # 12B
    "unsloth/gemma-2-9b-bnb-4bit", ...
]
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# ② 挂 LoRA（关键参数：use_gradient_checkpointing="unsloth" 再省30%显存、batch翻倍）
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,                    # 建议 8/16/32/64/128
    target_modules = ["q_proj","k_proj","v_proj","o_proj",
                      "gate_proj","up_proj","down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,          # 0 是优化值（支持任意）
    bias = "none",             # "none" 是优化值
    use_gradient_checkpointing = "unsloth",  # [NEW] 30% less VRAM
    random_state = 3407,
    use_rslora = False,        # 支持 rank stabilized LoRA
    loftq_config = None,
)

# ③ 数据：alpaca 模板 + EOS_TOKEN（不加会无限生成！）
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""
EOS_TOKEN = tokenizer.eos_token
def formatting_prompts_func(examples):
    texts = [alpaca_prompt.format(i, inp, out) + EOS_TOKEN
             for i, inp, out in zip(examples["instruction"], examples["input"], examples["output"])]
    return {"text": texts}
from datasets import load_dataset
dataset = load_dataset("unsloth/alpaca-cleaned", split="train")
dataset = dataset.map(formatting_prompts_func, batched=True)

# ④ 训练：trl 的 SFTTrainer（unsloth 加速在底层生效）
from trl import SFTConfig, SFTTrainer
trainer = SFTTrainer(
    model = model, tokenizer = tokenizer, train_dataset = dataset,
    dataset_text_field = "text", max_seq_length = max_seq_length,
    packing = False,          # 短序列 packing 可再快5倍
    args = SFTConfig(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5, max_steps = 60,
        learning_rate = 2e-4,
        optim = "adamw_8bit",  # 8bit 优化器省显存
        weight_decay = 0.001, lr_scheduler_type = "linear",
        seed = 3407, output_dir = "outputs", report_to = "none",
    ),
)
trainer.train()

# ⑤ 推理验证 + 导出（四选一）
FastLanguageModel.for_inference(model)   # 原生2x推理加速
inputs = tokenizer([alpaca_prompt.format("Continue the fibonacci sequence.", "1, 1, 2, 3, 5, 8", "")],
                   return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=64, use_cache=True)

# 导出（官方全清单）：
model.save_pretrained("llama_lora")                                   # 仅LoRA适配器
model.save_pretrained_merged("out_16bit", tokenizer, save_method="merged_16bit")  # 合并16bit
model.save_pretrained_merged("out_4bit", tokenizer, save_method="merged_4bit")
model.save_pretrained_gguf("out", tokenizer)                          # GGUF Q8_0
model.save_pretrained_gguf("out", tokenizer, quantization_method="q4_k_m")  # GGUF q4_k_m
model.push_to_hub_gguf(...)  # 推 HF（还有 push_to_hub_merged / push_to_hub）
```

**Unsloth 独有能力（2026 时点）**：embedding 微调 1.8-3.3x / GRPO 长上下文 7x（新 batching 算法）/ RoPE+MLP Triton Kernels + Padding-Free Packing 3x / 20B 模型 500K 上下文（80GB 单卡）/ FP8 + Vision RL 上消费卡 / MoE 12x / `unsloth start claude-code|codex|opencode` 一键把本地模型接给 Agent 工具。

### 3. LLaMA-Factory 使用流程（官方 README+examples 实录）

**安装**：
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
# 可选：pip install -r requirements/metrics.txt（评估）/ requirements/deepspeed.txt
# QLoRA 需：pip install bitsandbytes
```

**数据准备**：数据集格式见 `data/README.md`（alpaca / sharegpt 等格式，HF/ModelScope/本地/S3 皆可）；**自定义数据集必须注册进 `data/dataset_info.json`**；配套合成数据工具 Easy Dataset / DataFlow / GraphGen。

**三条命令跑通全流程（Qwen3-4B LoRA SFT 官方 Quickstart）**：
```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml   # 训练
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml     # 聊天验证
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml  # 合并导出
```

**训练 YAML 解剖（qwen3_lora_sft.yaml 官方全文逐段）**：
```yaml
### model
model_name_or_path: Qwen/Qwen3-4B-Instruct-2507
trust_remote_code: true
### method
stage: sft                 # 训练阶段：sft/pretrain/reward/ppo/dpo/kto/orpo/simpo
do_train: true
finetuning_type: lora      # lora / full
lora_rank: 8
lora_target: all           # 所有线性层
### dataset
dataset: identity,alpaca_en_demo
template: qwen3_nothink    # 对话模板必须匹配模型
cutoff_len: 2048
max_samples: 1000
preprocessing_num_workers: 16
dataloader_num_workers: 4
### output
output_dir: saves/qwen3-4b/lora/sft
logging_steps: 10
save_steps: 500
plot_loss: true            # 自动画 loss 曲线
report_to: none            # wandb/tensorboard/swanlab/mlflow
### train
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 1.0e-4
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
### eval（注释打开即用）
# eval_dataset: alpaca_en_demo
# val_size: 0.1
# eval_strategy: steps
# eval_steps: 500
```

**方法全覆盖命令（examples 实录）**：
```bash
# LoRA 家族
llamafactory-cli train examples/train_lora/qwen3_lora_pretrain.yaml   # 继续预训练
llamafactory-cli train examples/train_lora/qwen3vl_lora_sft.yaml      # 多模态SFT
llamafactory-cli train examples/train_lora/qwen3_lora_dpo.yaml        # DPO/ORPO/SimPO
llamafactory-cli train examples/train_lora/qwen3_lora_reward.yaml     # 奖励建模
llamafactory-cli train examples/train_lora/qwen3_lora_kto.yaml        # KTO
# QLoRA（4/8bit bnb/HQQ/EETQ）
llamafactory-cli train examples/train_qlora/qwen3_lora_sft_otfq.yaml  # 官方推荐
llamafactory-cli train examples/train_qlora/llama3_lora_sft_gptq.yaml # GPTQ底座
llamafactory-cli train examples/train_qlora/llama3_lora_sft_awq.yaml  # AWQ底座
llamafactory-cli train examples/train_qlora/llama3_lora_sft_aqlm.yaml # 2bit AQLM
# 全参微调
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_full/qwen3_full_sft.yaml
# 多机多卡
FORCE_TORCHRUN=1 NNODES=2 NODE_RANK=0 MASTER_ADDR=192.168.0.1 MASTER_PORT=29500 \
    llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
# 弹性容错（节点故障自动重启）
FORCE_TORCHRUN=1 MIN_NNODES=1 MAX_NNODES=3 MAX_RESTARTS=3 RDZV_ID=llamafactory \
    MASTER_ADDR=192.168.0.1 MASTER_PORT=29500 llamafactory-cli train examples/train_full/qwen3_full_sft.yaml
# DeepSpeed ZeRO-3 权重分片 / Ray 4卡
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_lora/qwen3_lora_sft_ds3.yaml
USE_RAY=1 llamafactory-cli train examples/train_lora/qwen3_lora_sft_ray.yaml
```

**导出与部署**：
```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml   # LoRA合并（禁用量化底座）
llamafactory-cli export examples/merge_lora/qwen3_gptq.yaml       # AutoGPTQ 量化导出
llamafactory-cli export examples/merge_lora/qwen3_full_sft.yaml   # Ollama modelfile
# OpenAI 风格 API（vLLM 后端）
API_PORT=8000 llamafactory-cli api examples/inference/qwen3.yaml infer_backend=vllm vllm_enforce_eager=true
# 评估：vLLM 多卡推理 + BLEU/ROUGE
python scripts/vllm_infer.py --model_name_or_path Qwen/Qwen3-4B-Instruct-2507 \
    --template qwen3_nothink --dataset alpaca_en_demo
python scripts/eval_bleu_rouge.py generated_predictions.jsonl
```

**WebUI 路线（零代码）**：`llamafactory-cli webui` → LLaMA Board（Gradio）：选模型/方法/数据集/超参全点选，导出 YAML 可复现。WebUI 聊天：`llamafactory-cli webchat <yaml>`。

**环境变量速查**：`CUDA_VISIBLE_DEVICES`（选卡，默认全用）/ `ASCEND_RT_VISIBLE_DEVICES`（NPU）/ `FORCE_TORCHRUN=1`（强制多卡启动）/ `USE_RAY=1` / 命令行参数可覆盖 YAML（`llamafactory-cli train x.yaml learning_rate=1e-5`）。

### 4. 选型决策树

```
你的卡？
├─ 单卡消费级（≤24GB）且目标是"跑起来+导出GGUF给Ollama用"
│    → Unsloth（bnb-4bit预量化+GGUF一键导出是杀手锏）
├─ 要做偏好对齐全流程（RM→PPO 或 DPO/KTO/ORPO/SimPO 混合）
│    → LLaMA-Factory（九种stage全；Unsloth 侧重 GRPO）
├─ 多卡/多机/集群
│    → LLaMA-Factory（DeepSpeed ZeRO-3/Ray/弹性容错/NPU）
├─ 完全不想写代码
│    → Unsloth Studio（WebUI）或 LLaMA Board（llamafactory-cli webui）
└─ GRPO/RL 推理训练
     → Unsloth（长上下文7x/FP8/Vision RL）或 EasyR1（LLaMA-Factory 姊妹项目）
```

两框架**不互斥**：常见组合是 Unsloth 快速迭代 LoRA → 满意后用 LLaMA-Factory 做正式训练（多卡+评估+部署）。

### 5. 关键坑位提示（官方文档+实践综合）

| 坑 | 说明 |
|---|---|
| EOS_TOKEN 缺失 | Unsloth 数据格式化不加 EOS → 生成无限 continuation（官方加粗警告） |
| template 不匹配 | LLaMA-Factory 的 `template` 必须与模型聊天模板一致（qwen3_nothink vs qwen3） |
| LoRA 合并遇量化底座 | LLaMA-Factory 明确：合并适配器**禁用**量化模型/quantization_bit |
| Windows 安装 | Unsloth Windows 需先装 PyTorch；bitsandbytes 有专用 wheel |
| lr 量级 | LoRA 常用 1e-4~2e-4（两框架示例一致）；全参微调低 1-2 个量级 |
| packing 权衡 | Unsloth：短序列 packing=True 快 5 倍；但长文本任务关掉 |
| dataset_info.json | LLaMA-Factory 自定义数据不注册 = 加载报错（最常见新手问题） |

## 二、查询拓展

1. Unsloth Triton Kernel 手写逆向注意（license 与下游商用边界）——选型前的合规检查
2. LLaMA-Factory GRPO 配置细节（examples 里 qwen3 GSPO/GRPO 与 EasyR1 的分工）
3. 4bit QLoRA 训练后合并的精度损失量化（merged_4bit vs 先合并再量化）
4. Unsloth Studio 的 API key/LAN 访问安全模型（--secure fail-closed 机制细节）
5. 两框架在 Qwen3.5/GLM-4.x 最新模型上的 Day-N 支持时差
6. llamafactory-cli 的 `stage: rm+ppo` 完整链路 YAML（RM 训练→PPO 引用 RM 的参数衔接）
7. GGUF q4_k_m 与 AWQ/GPTQ 在 vLLM 与 llama.cpp 两条部署线的吞吐对比

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | Unsloth=**加速器**（把 HF/trl 训练透明提速2倍省70%显存，单卡+GGUF 落地最顺）；LLaMA-Factory=**全流程线**（九种训练方法+多卡分布式+评估+API部署） |
| 使用范式差异 | Unsloth：Python notebook 五步（载模型→挂LoRA→格式化数据→SFTTrainer→导出）；LLaMA-Factory：YAML+CLI 三连（train→chat→export） |
| 共同底座 | 都吃 HF 生态（transformers/trl/peft/datasets）；LoRA 超参共识：r=8-16、target=all、lr=1e-4~2e-4、bf16、8bit优化器 |
| 快省的来源 | Unsloth：手写 Triton Kernel（RoPE/MLP/交叉熵）+ 4bit预量化+ unsloth 梯度检查点+packing；不是魔法，是 kernel 级工程 |
| 新手路线 | Unsloth Colab 免费笔记本起步（选模型表格一键开跑）→ Studio WebUI → Core 代码 |
| 进阶路线 | LLaMA-Factory YAML 复现 → 改 stage 做 DPO → 多机 ZeRO-3 → vLLM API 上线 |
| 不互斥 | 快迭代用 Unsloth，正式训练部署用 LLaMA-Factory——两框架共享 HF 模型/数据格式 |

## 四、趋势判断

1. **微调工具的"双轨固化"**：加速层（Unsloth 类 kernel 工程）与流程层（LLaMA-Factory 类编排工程）会长期并存——像 CUDA 与 PyTorch 的分层，最终可能融合（LLaMA-Factory 已可选接入加速后端）
2. **消费级显卡微调成为默认入口**：4bit 预量化模型+8bit 优化器+梯度检查点三件套让 8B-14B 在 16-24GB 卡上可训——个人/小团队的定制模型门槛已降至"一台游戏本"
3. **GGUF/Ollama 是消费级落地的终局格式**：Unsloth 一键 GGUF 导出直连 llama.cpp 生态；LLaMA-Factory 跟进 Ollama modelfile 导出——"训练完跑在本地 Ollama"成为个人模型闭环标配
4. **偏好对齐方法在收敛**：DPO 系（DPO/KTO/ORPO/SimPO 无需 RM 的直接偏好优化）已成主流路径，PPO 只在特定场景保留——LLaMA-Factory 九种 stage 的重心正在向 DPO 系+GRPO 倾斜
5. **RL（GRPO）是新战场**：Unsloth 重注 GRPO（长上下文 7x/FP8/Vision RL/500K context），LLaMA-Factory 拆出 EasyR1 专门做——推理能力训练的工具竞争刚开始
6. **Agent 集成是新入口**：Unsloth `unsloth start claude-code/codex` 把本地微调模型直接接到编码 Agent——微调的动机从"做个聊天机器人"转向"定制我的 Agent 大脑"

## 五、关联分析

| 关联对象 | 关系 |
|---|---|
| **本仓 skill `unsloth`**（mlops/training/unsloth） | 本篇实操流程可直接回填该 skill 的 Quick Reference（references/ 已有 llms.txt 全文档，Quick Reference 空缺） |
| **本仓 skill `peft-fine-tuning` / `fine-tuning-with-trl` / `axolotl`** | 同族工具对照：axolotl 也是 YAML 驱动全流程（与 LLaMA-Factory 同类竞品）；trl 是 Unsloth 底层 SFTTrainer 来源；peft 是 LoRA 理论层——四者构成"理论→库→框架→加速"栈 |
| **本仓 skill `gguf-quantization`** | Unsloth 的 GGUF 导出（q8_0/f16/q4_k_m）与 llama.cpp 量化体系正是该 skill 的实操入口 |
| **笔记《2026-08-18-LittleLearner》** | 微调的边界证据：LoRA/SFT 干预不改基座知识边界——"微调快 2 倍"解决的是效率不是能力；小模型微调适合"格式/风格/领域术语"定制而非知识注入 |
| **笔记《2026-08-19-企业Agent技术选型》** | 选型同构：Unsloth vs LLaMA-Factory = "单一工具做深" vs "全流程平台"；企业侧通常两者都要（快迭代+正式产线） |
| **笔记《2026-08-19-物理AI的裁判层提案》** | GRPO/RLVR 联动：Unsloth 重注的 GRPO 训练正是物理提案"验证器进 RL 回路"的技术载体——可验证奖励+GRPO=领域模型强化的标准配方 |
| Jetson 边缘部署线（edge-llm-quantization / jetson-tensorrt-deploy） | GGUF→llama.cpp 是 Jetson 本地推理主路线之一：Unsloth 训练→GGUF 导出→Jetson Ollama 部署闭环可行 |
| 本仓铁律"不在 Jetson 跑重型训练" | 两框架在本仓定位=代码管线就绪即可，实际训练留给有 GPU 的机器——与"研究项目产出文档+单测不部署"一致 |

→ 官方仓库：https://github.com/unslothai/unsloth · https://github.com/hiyouga/LLaMA-Factory
→ 官方文档：https://unsloth.ai/docs · https://llamafactory.readthedocs.io
→ Colab 起点：Unsloth 官方 notebook 表格 / LLaMA-Factory Colab（免费）

## 六、拓展应用推荐

**① 立即可用的三件事**
- **30 分钟体验**：Unsloth Colab（Llama3.2-1B/3B Conversational 免费卡）跑通五步流程——第一次微调的最佳起点
- **本地 Ollama 闭环**：任何 bnb-4bit 模型 + 自有数据 → `save_pretrained_gguf(q4_k_m)` → `ollama create` 导入——个人定制模型一条龙
- **YAML 复现实验**：LLaMA-Factory 三连命令 + `plot_loss: true`——每个 YAML 都是可 diff 的实验记录

**② 进阶组合玩法**
- **DPO 品味定制**：用自建偏好对（好答案/差答案）+ LLaMA-Factory `stage: dpo`——比 SFT 更适合"输出风格/拒答边界"调优
- **GRPO 推理强化**：Unsloth GRPO notebook（Qwen3 Advanced GRPO）+ 可验证任务（数学/代码）——领域推理能力强化
- **多卡正式产线**：单卡 Unsloth 调参满意 → LLaMA-Factory ZeRO-3 多卡放大 → vLLM API 部署

**③ 数据工程提示**（两框架共同前置）
- alpaca 格式（instruction/input/output）最通用；sharegpa 适合多轮对话；LLaMA-Factory 记得注册 dataset_info.json
- 合成数据工具链：Easy Dataset / DataFlow / GraphGen（LLaMA-Factory 官方推荐三件）
- **EOS_TOKEN 陷阱**：所有自定义数据格式化必须显式拼 EOS——无限生成的头号原因

## 七、指南分析

**速查卡：两框架核心命令**

```
Unsloth 五步：
  FastLanguageModel.from_pretrained(bnb-4bit模型)   ← ①
  FastLanguageModel.get_peft_model(r=16, checkpoint="unsloth") ← ②
  dataset.map(格式化+EOS)                           ← ③
  SFTTrainer(SFTConfig(lr=2e-4, optim="adamw_8bit")) ← ④
  save_pretrained_gguf(q4_k_m)                      ← ⑤

LLaMA-Factory 三连：
  llamafactory-cli train  <yaml>   # stage: sft/dpo/ppo/...
  llamafactory-cli chat   <yaml>   # 验证
  llamafactory-cli export <yaml>   # 合并/量化/Ollama
  # WebUI: llamafactory-cli webui
  # API:  llamafactory-cli api <yaml> infer_backend=vllm
```

**选型三问**
- 只有一张消费卡+要本地部署？→ Unsloth
- 要 PPO/DPO/多卡/正式评估？→ LLaMA-Factory
- 两样都要？→ 都装（共享 HF 生态不冲突），快迭代 U、正式产线 L

**避坑清单（背下来）**
- EOS 必拼（Unsloth 数据格式化）
- template 必匹配模型（LLaMA-Factory）
- LoRA 合并禁量化底座（两框架同）
- lr：LoRA 1e-4~2e-4 / 全参低两个量级
- 自定义数据集注册 dataset_info.json（LLaMA-Factory 新手第一坑）

**何时重读本篇**：拿到新卡装环境时（安装段）；选工具时（决策树）；导出部署时（GGUF/Ollama/vLLM 段）；数据翻车时（坑位表）。

## 相关笔记

- [2026本地大模型部署指南](./2026-08-10-2026本地大模型部署指南-从8GB到万亿参数.md) — 微调后部署衔接
- [MoE时代的Scaling意义](./2026-08-19-MoE时代的Scaling意义与发展-解耦参数与计算后规模定律的重新定义.md) — 基座选型经济学
