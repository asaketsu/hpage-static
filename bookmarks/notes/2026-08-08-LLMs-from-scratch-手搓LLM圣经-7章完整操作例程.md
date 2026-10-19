# Build a Large Language Model (From Scratch) — Sebastian Raschka 的 102K Stars 手搓 LLM 圣经（7 章 + 详细操作例程）

> **来源**：[github.com/rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)
> **Stars**：101,875 · **Forks**：15,616
> **作者**：Sebastian Raschka（前 Meta/Falcon LLM 研究科学家）
> **配套书籍**：[Build a Large Language Model (From Scratch)](https://amzn.to/4fqvn0D) · Manning · ISBN 9781633437166
> **视频课程**：17 小时 15 分钟逐章编码
> **续作**：[Build A Reasoning Model (From Scratch)](https://mng.bz/lZ5B)
> **标签**：LLM、PyTorch、GPT、从零实现、预训练、微调

---

## 一句话定义

> **101K Stars 的从零构建 LLM 教程**——从文本数据处理到 Attention 机制到 GPT 架构到预训练到分类微调到指令微调的完整 7 章。所有代码用纯 PyTorch 从零实现，不使用 HuggingFace Transformers 等外部库。**在普通笔记本上即可运行**，有 GPU 自动加速。

---

## 完整章节架构与操作例程

### 全书思维导图

```
Ch1: LLM 概念理解（无代码）
  │
  ├─ Ch2: 文本数据处理
  │    └─ 分词 → 滑动窗口 → Embedding → Dataset
  │
  ├─ Ch3: Attention 机制
  │    └─ 自注意力 → 多头注意力 → 因果掩码
  │
  ├─ Ch4: GPT 模型架构
  │    └─ Transformer Block → LayerNorm → GELU → 残差连接 → 完整 GPT
  │
  ├─ Ch5: 无标签数据预训练
  │    └─ 训练循环 → 损失计算 → 生成文本 → 加载预训练权重
  │
  ├─ Ch6: 文本分类微调
  │    └─ 分类头 → IMDb 情感分析 → LoRA 偏好微调
  │
  └─ Ch7: 指令遵循微调
       └─ 指令数据集 → SFT → 评估 → DPO 偏好优化
```

---

### Ch 2: Working with Text Data（文本数据处理）

**操作例程**：

```python
# 1. 读取文本
import re
with open("the-verdict.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 2. 分词（简单版 → BPE）
preprocessed = re.split(r'([,.?_!"()\']|--|\s)', raw_text)
tokens = [t for t in preprocessed if t.strip()]

# 3. 构建词表
all_tokens = sorted(set(tokens))
vocab = {token: i for i, token in enumerate(all_tokens)}

# 4. BPE Tokenizer（使用 tiktoken）
import tiktoken
tokenizer = tiktoken.get_encoding("gpt2")

# 5. 滑动窗口数据加载
from torch.utils.data import Dataset, DataLoader

class GPTDatasetV1(Dataset):
    def __init__(self, txt, tokenizer, max_length, stride):
        self.input_ids = []
        self.target_ids = []
        token_ids = tokenizer.encode(txt)
        for i in range(0, len(token_ids) - max_length, stride):
            self.input_ids.append(token_ids[i:i + max_length])
            self.target_ids.append(token_ids[i+1:i + max_length + 1])
    
    def __len__(self): return len(self.input_ids)
    def __getitem__(self, idx): return self.input_ids[idx], self.target_ids[idx]

# 6. Embedding
import torch
vocab_size = 50257
output_dim = 256
max_len = 4

# Token Embedding + Positional Embedding
token_embedding_layer = torch.nn.Embedding(vocab_size, output_dim)
pos_embedding_layer = torch.nn.Embedding(max_len, output_dim)
```

**核心概念**：
- BPE（Byte Pair Encoding）分词
- 滑动窗口生成训练样本（input → next-token target）
- Token Embedding + Positional Embedding 的区别

---

### Ch 3: Coding Attention Mechanisms（Attention 机制）

**操作例程**：

```python
import torch.nn as nn

# 1. 简化版自注意力
class SelfAttention_v1(nn.Module):
    def __init__(self, d_in, d_out):
        super().__init__()
        self.W_query = nn.Linear(d_in, d_out)
        self.W_key   = nn.Linear(d_in, d_out)
        self.W_value = nn.Linear(d_in, d_out)
    
    def forward(self, x):
        Q = self.W_query(x)  # (batch, seq, d_out)
        K = self.W_key(x)
        V = self.W_value(x)
        attn_scores = Q @ K.transpose(-2, -1)
        attn_weights = torch.softmax(attn_scores / K.shape[-1]**0.5, dim=-1)
        context_vec = attn_weights @ V
        return context_vec

# 2. 因果掩码（防止看到未来 token）
context_length = 4
mask = torch.triu(torch.ones(context_length, context_length), diagonal=1)
masked = attn_scores.masked_fill(mask.bool(), -torch.inf)

# 3. 多头注意力
class MultiHeadAttentionWrapper(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads):
        super().__init__()
        self.heads = nn.ModuleList([
            CausalAttention(d_in, d_out, context_length, dropout)
            for _ in range(num_heads)
        ])
    
    def forward(self, x):
        return torch.cat([head(x) for head in self.heads], dim=-1)

# 4. 高效多头注意力（batch 矩阵乘法，一次性计算所有头）
class MultiHeadAttention(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias=False):
        super().__init__()
        assert d_out % num_heads == 0
        self.d_out = d_out
        self.num_heads = num_heads
        self.head_dim = d_out // num_heads
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key   = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.out_proj = nn.Linear(d_out, d_out)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer(
            'mask', torch.triu(torch.ones(context_length, context_length), diagonal=1)
        )
    
    def forward(self, x):
        b, num_tokens, d_in = x.shape
        keys = self.W_key(x).view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
        queries = self.W_query(x).view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
        values = self.W_value(x).view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
        
        attn_scores = queries @ keys.transpose(2, 3)
        attn_scores.masked_fill_(self.mask.bool()[:num_tokens, :num_tokens], -torch.inf)
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        context_vec = (attn_weights @ values).transpose(1, 2)
        context_vec = context_vec.contiguous().view(b, num_tokens, self.d_out)
        return self.out_proj(context_vec)
```

**核心概念**：
- Q/K/V 三矩阵的物理含义
- 缩放点积注意力（÷√d_k）
- 因果掩码（上三角 -inf）
- 多头并行计算（batch matmul）

---

### Ch 4: Implementing a GPT Model from Scratch（GPT 架构）

**操作例程**：

```python
import torch.nn as nn

# 1. LayerNorm（与 BatchNorm 对比）
class LayerNorm(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.eps = 1e-5
        self.scale = nn.Parameter(torch.ones(dim))
        self.shift = nn.Parameter(torch.zeros(dim))
    
    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True)
        return self.scale * (x - mean) / torch.sqrt(var + self.eps) + self.shift

# 2. GELU 激活函数
class GELU(nn.Module):
    def forward(self, x):
        return 0.5 * x * (1 + torch.tanh(
            torch.sqrt(torch.tensor(2.0 / torch.pi)) *
            (x + 0.044715 * torch.pow(x, 3))
        ))

# 3. FeedForward 网络
class FeedForward(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(cfg["emb_dim"], 4 * cfg["emb_dim"]),
            GELU(),
            nn.Linear(4 * cfg["emb_dim"], cfg["emb_dim"]),
        )
    def forward(self, x): return self.layers(x)

# 4. Transformer Block
class TransformerBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.att = MultiHeadAttention(
            cfg["emb_dim"], cfg["emb_dim"], cfg["context_length"],
            cfg["drop_rate"], cfg["n_heads"], cfg["qkv_bias"]
        )
        self.ff = FeedForward(cfg)
        self.norm1 = LayerNorm(cfg["emb_dim"])
        self.norm2 = LayerNorm(cfg["emb_dim"])
        self.drop_shortcut = nn.Dropout(cfg["drop_rate"])
    
    def forward(self, x):
        # 残差连接 + LayerNorm
        x = x + self.drop_shortcut(self.att(self.norm1(x)))
        x = x + self.drop_shortcut(self.ff(self.norm2(x)))
        return x

# 5. 完整 GPT 模型
class GPTModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.tok_emb = nn.Embedding(cfg["vocab_size"], cfg["emb_dim"])
        self.pos_emb = nn.Embedding(cfg["context_length"], cfg["emb_dim"])
        self.drop_emb = nn.Dropout(cfg["drop_rate"])
        self.trf_blocks = nn.Sequential(
            *[TransformerBlock(cfg) for _ in range(cfg["n_layers"])]
        )
        self.final_norm = LayerNorm(cfg["emb_dim"])
        self.out_head = nn.Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)
    
    def forward(self, in_idx):
        batch_size, seq_len = in_idx.shape
        tok_embeds = self.tok_emb(in_idx)
        pos_embeds = self.pos_emb(torch.arange(seq_len, device=in_idx.device))
        x = tok_embeds + pos_embeds
        x = self.drop_emb(x)
        x = self.trf_blocks(x)
        x = self.final_norm(x)
        logits = self.out_head(x)
        return logits

# GPT 配置（124M 参数的 GPT-2 小型版）
GPT_CONFIG_124M = {
    "vocab_size": 50257,
    "context_length": 256,     # 书中缩短版（原版 1024）
    "emb_dim": 768,
    "n_heads": 12,
    "n_layers": 12,
    "drop_rate": 0.1,
    "qkv_bias": False,
}

# 6. 文本生成
def generate_text_simple(model, idx, max_new_tokens, context_size):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -context_size:]
        with torch.no_grad():
            logits = model(idx_cond)
        logits = logits[:, -1, :]  # 只取最后一个 token 的 logits
        probas = torch.softmax(logits, dim=-1)
        idx_next = torch.argmax(probas, dim=-1, keepdim=True)
        idx = torch.cat((idx, idx_next), dim=1)
    return idx

# 运行
import torch
model = GPTModel(GPT_CONFIG_124M)
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")  # 163M（含 positional embedding）
```

**核心概念**：
- Transformer Block = LayerNorm + Multi-Head Attention + 残差 + LayerNorm + FeedForward + 残差
- GPT-2 124M = 12 层 × 768 维 × 12 头
- 自回归生成（每次取最后 token 的 logits）

---

### Ch 5: Pretraining on Unlabeled Data（预训练）

**操作例程**：

```python
# 1. 计算 Loss（交叉熵）
def calc_loss_batch(input_batch, target_batch, model, device):
    input_batch, target_batch = input_batch.to(device), target_batch.to(device)
    logits = model(input_batch)
    loss = torch.nn.functional.cross_entropy(
        logits.flatten(0, 1), target_batch.flatten()
    )
    return loss

def calc_loss_loader(data_loader, model, device, num_batches=None):
    total_loss = 0.
    if num_batches is None:
        num_batches = len(data_loader)
    for i, (input_batch, target_batch) in enumerate(data_loader):
        if i < num_batches:
            loss = calc_loss_batch(input_batch, target_batch, model, device)
            total_loss += loss.item()
        else:
            break
    return total_loss / num_batches

# 2. 训练循环
def train_model_simple(model, train_loader, val_loader, optimizer, device,
                       num_epochs, eval_freq, eval_iter, start_context, tokenizer):
    train_losses, val_losses, track_tokens_seen = [], [], []
    tokens_seen = 0
    global_step = -1

    for epoch in range(num_epochs):
        model.train()
        for input_batch, target_batch in train_loader:
            optimizer.zero_grad()
            loss = calc_loss_batch(input_batch, target_batch, model, device)
            loss.backward()
            optimizer.step()
            tokens_seen += input_batch.numel()
            global_step += 1

            if global_step % eval_freq == 0:
                train_loss, val_loss = evaluate_model(
                    model, train_loader, val_loader, device, eval_iter)
                train_losses.append(train_loss)
                val_losses.append(val_loss)
                track_tokens_seen.append(tokens_seen)
                print(f"Ep {epoch+1} (Step {global_step:06d}): "
                      f"Train loss {train_loss:.3f}, Val loss {val_loss:.3f}")

        # 每个 epoch 后生成一段文本看效果
        generate_and_print_sample(model, tokenizer, device, start_context)

    return train_losses, val_losses, track_tokens_seen

# 3. 加载 OpenAI 预训练权重（GPT-2 124M/355M/774M/1558M）
from gpt_download import download_and_load_gpt2
settings, params = download_and_load_gpt2(
    model_size="124M", models_dir="gpt2"
)
# 将权重加载到我们的 GPTModel 中
model = GPTModel(GPT_CONFIG_124M)
load_weights_into_gpt(model, params)

# 4. 使用加载的模型生成文本
token_ids = generate_text_simple(
    model, idx=text_to_token_ids("Every effort moves you", tokenizer),
    max_new_tokens=15, context_size=GPT_CONFIG_124M["context_length"]
)
print(token_ids_to_text(token_ids, tokenizer))
```

**核心概念**：
- Next-token prediction loss（交叉熵）
- Train/Val loss 监控
- 从 OpenAI 加载 GPT-2 预训练权重
- 两种模式：从零训练 vs 加载预训练权重微调

---

### Ch 6: Finetuning for Text Classification（分类微调）

**操作例程**：

```python
# 1. 准备数据集（IMDb 50K 影评）
import pandas as pd
df = pd.read_csv("IMDB Dataset.csv")
# 分割 train/val/test

# 2. 替换输出头（768 → 2 分类）
class GPTClassifier(nn.Module):
    def __init__(self, base_config, num_classes=2):
        super().__init__()
        self.gpt = GPTModel(base_config)
        # 冻结基础模型参数（可选）
        for param in self.gpt.parameters():
            param.requires_grad = False
        # 只训练最后一个 token 的分类头
        self.class_head = nn.Linear(base_config["emb_dim"], num_classes)
    
    def forward(self, text):
        x = self.gpt(text)
        x = x[:, -1, :]  # 取最后一个 token
        return self.class_head(x)

# 3. 训练分类器
optimizer = torch.optim.AdamW(
    model.parameters(), lr=4e-4, weight_decay=0.1
)
# 标准训练循环...

# 4. LoRA 微调（Appendix E）
from peft import LoraConfig, get_peft_model
config = LoraConfig(
    r=8, lora_alpha=16,
    target_modules=["W_query", "W_key", "W_value"],
    lora_dropout=0.05, bias="none",
    task_type="FEATURE_EXTRACTION"
)
model = get_peft_model(model, config)
```

**核心概念**：
- 分类头替换（vocab_size → num_classes）
- 冻结基础模型参数（只训练分类头）
- 取最后一个 token 的表示做分类
- LoRA 高效微调

---

### Ch 7: Finetuning to Follow Instructions（指令微调）

**操作例程**：

```python
# 1. 准备指令数据集（Alpaca 风格）
# 格式: {"instruction": "...", "input": "...", "output": "..."}

# 2. 格式化为 prompt
def format_input(entry):
    instruction_text = (
        f"Below is an instruction that describes a task. "
        f"Write a response that appropriately completes the request."
        f"\n\n### Instruction:\n{entry['instruction']}"
    )
    input_text = f"\n\n### Input:\n{entry['input']}" if entry["input"] else ""
    return instruction_text + input_text

# 3. 构建训练数据（mask 掉 prompt 部分，只对 response 计 loss）
def custom_collate_fn(batch, pad_token_id, ignore_index=-100, device="cpu"):
    batch_max_length = max(len(item)+1 for seq in batch for item in seq["input_ids"])
    
    input_lst, target_lst = [], []
    for batch_entry in batch:
        # input = prompt + response
        input_ids = batch_entry["input_ids"]
        # target = [-100] * len(prompt) + response_ids  # -100 = ignore
        target_ids = batch_entry["labels"]
        # padding
        input_ids = input_ids + [pad_token_id] * (batch_max_length - len(input_ids))
        target_ids = target_ids + [ignore_index] * (batch_max_length - len(target_ids))
        input_lst.append(input_ids)
        target_lst.append(target_ids)
    
    return torch.tensor(input_lst), torch.tensor(target_lst)

# 4. SFT 训练
model = GPTModel(GPT_CONFIG_124M)
load_weights_into_gpt(model, params)  # 加载预训练
model.out_head = nn.Linear(...)  # 保持原样

optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.1)
# 标准 SFT 训练循环...

# 5. DPO 偏好优化（Bonus）
# 构建偏好数据: (prompt, chosen_response, rejected_response)
# DPO loss = -log(sigmoid(beta * (log_ratio_chosen - log_ratio_rejected)))

# 6. 评估（Ollama）
# 用 ollama_evaluate.py 评估指令遵循质量
```

**核心概念**：
- Prompt 格式化（instruction + input + response）
- Loss masking（只对 response 计算 loss）
- SFT → DPO 的完整对齐流程
- LLM-as-a-Judge 评估

---

## Bonus Material 重点（进阶内容）

| 模块 | 内容 |
|------|------|
| **Ch2 Bonus** | BPE Tokenizer 从零实现、Embedding vs Linear Layer 对比 |
| **Ch3 Bonus** | 高效多头注意力实现对比（Flash Attention 等） |
| **Ch4 Bonus** | FLOPs 分析、KV Cache、GQA、MLA、SWA、MoE |
| **Ch5 Bonus** | Llama 3.2/Qwen3/Gemma3/Olmo3/Qwen3.5/Gemma4 从零实现、超参调优 |
| **Ch6 Bonus** | 不同层微调对比实验、IMDb 50K 数据集 |
| **Ch7 Bonus** | DPO 从零实现、偏好数据生成、数据集质量改进 |

### 最有价值的 Bonus

| Bonus | 为什么重要 |
|-------|-----------|
| **Llama 3.2 从零实现** | 看到工业级 LLM 与 GPT-2 的架构差异 |
| **Qwen3 MoE 从零实现** | 理解稀疏 MoE 的工作机制 |
| **KV Cache** | 推理加速的核心技术 |
| **GQA (Grouped-Query Attention)** | Llama 2/3 用的注意力变体 |
| **MLA (Multi-Head Latent Attention)** | DeepSeek-V2/V3 的注意力变体 |
| **DPO 从零实现** | RLHF 的简化替代方案 |
| **Llama 3.1 70B 生成偏好数据** | 用大模型生成训练数据 |

---

## 硬件要求

| 模式 | 硬件 | 说明 |
|------|------|------|
| **主章节代码** | 普通笔记本（CPU 即可） | 设计为在笔记本上合理时间内跑完 |
| **GPU 加速** | 有 GPU 自动使用 | 代码自动检测 GPU |
| **预训练权重** | GPT-2 124M/355M/774M/1558M | 可加载不同大小的 OpenAI 权重 |
| **微调** | GPU 推荐 | IMDb 50K 分类和指令微调 |

---

## 环境搭建

```bash
# 克隆仓库
git clone --depth 1 https://github.com/rasbt/LLMs-from-scratch.git
cd LLMs-from-scratch

# 安装依赖
pip install -r setup/requirements.txt
# 或用 uv
uv pip install -r setup/requirements.txt

# 主要依赖
# - torch >= 2.0
# - tiktoken >= 0.5.1
# - matplotlib
# - pandas
# - tqdm
```

---

## 结合最新研究与技术变化

### 1. 与 Hands-On Modern RL 笔记的关联

LLMs-from-scratch 是 LLM 的"静态"实现（架构+预训练+微调），Hands-On Modern RL 是"动态"实现（RL 训练+推理扩展）。两者互补：先读 LLMs-from-scratch 理解 GPT 架构，再读 Modern RL 理解如何用 RL 提升推理能力。

续作 [Build A Reasoning Model (From Scratch)](https://github.com/rasbt/reasoning-from-scratch) 直接衔接——从预训练模型开始，实现 inference-time scaling、RL（GRPO）和蒸馏。

### 2. 与 LFM2.5-2.6B 端侧 Agent 模型笔记的关联

LFM2.5 的四阶段后训练管线（SFT → Teacher Specialization → MOPD → Agentic RL）中，前两个阶段（SFT + 蒸馏）正是 Ch 7 的内容。理解 Ch 7 的 SFT/DPO 是理解 LFM2.5 的前提。

### 3. 与 AI for Physics 五路线笔记的关联

LLMs-from-scratch 的 GPT 架构是 AI for Physics 中"路线 B（数值模拟）"的基础工具——机器学习势函数、神经算子、神经网络量子态都基于 Transformer 架构。

### 4. 与 LLM 推理优化 Skill 的关联

PagedAttention/量化/推测解码/连续批处理等推理优化技术的理论基础都在 Ch 4（GPT 架构）和 Ch 4 Bonus（KV Cache/GQA/MLA）中。

---

## 学习进化借鉴点

| 洞察 | 可借鉴到 Hermes | 优先级 |
|------|----------------|--------|
| **从零实现是最深理解** | 学习方法 | 高 |
| **在笔记本上可运行** | 降低门槛 | 高 |
| **加载预训练权重** | 从零训练 vs 加载权重的选择 | 高 |
| **Loss masking** | 只对 response 计算 loss | 高 |
| **Bonus 覆盖前沿架构** | GQA/MLA/MoE/KV Cache | 高 |
| **多模型从零实现** | Llama3/Qwen3/Gemma3/Olmo3 | 高 |
| **DPO 从零实现** | RLHF 的简化替代 | 中 |
| **17 小时视频课程** | 视觉化学习 | 中 |

---

## 趋势判断

1. **从零实现是最有效的学习路径**——102K Stars 证明了这个判断
2. **LLM 教育正在标准化**——Sebastian Raschka 的书 + 视频 + 代码三位一体
3. **Bonus 追踪前沿**——从 GPT-2 扩展到 Llama3/Qwen3/Gemma4/GQA/MLA/MoE
4. **续作 Reasoning Model**——从 LLM 到推理模型（inference scaling + RL + 蒸馏）的延伸
5. **"在笔记本上可运行"是设计原则**——不需要 H100 集群就能理解 LLM

---

## 关联分析

- **与 Hands-On Modern RL**：静态实现 + 动态训练 = 完整 LLM 知识体系
- **与 LFM2.5-2.6B**：Ch 7 SFT/DPO = LFM2.5 后训练的前两阶段
- **与 LLM 推理优化**：Ch 4 Bonus = KV Cache/GQA/MLA 理论基础
- **与 AI for Physics**：Transformer = 路线 B 数值模拟的基础
- **与 Awesome Journal Skills**：学术方法论 + 技术实现 = 论文写作全栈
- **与 CodexLoom Agent Team**：LLM 从零实现 = 理解 Agent 底层引擎

---

## 📎 关键资源

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [github.com/rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) |
| 书籍（Amazon） | [amzn.to/4fqvn0D](https://amzn.to/4fqvn0D) |
| 书籍（Manning） | [mng.bz/orYv](http://mng.bz/orYv) |
| 视频课程 17h | [manning.com/livevideo/...](https://www.manning.com/livevideo/master-and-build-large-language-models) |
| 续作 Reasoning | [github.com/rasbt/reasoning-from-scratch](https://github.com/rasbt/reasoning-from-scratch) |
| 作者博客 | [sebastianraschka.com](https://sebastianraschka.com) |
| 测试 PDF（170 页） | [Test Yourself PDF](https://www.manning.com/books/test-yourself-on-build-a-large-language-model-from-scratch) |

---

*笔记创建：2026-08-08 · 来源：Sebastian Raschka LLMs-from-scratch GitHub（101.8K Stars）*

---

## 相关笔记

- [[2026-08-07-Hands-On-Modern-RL-从经典控制到LLM对齐与Agentic系统]] — 静态实现（本书）+ 动态训练（RL）= 完整 LLM 知识体系
- [[2026-08-08-LFM2.5-2.6B端侧Agent模型-手机30tok-s-GRPO训练HermesAgent]] — Ch7 SFT/DPO 是 LFM2.5 后训练前两阶段的前提
- [[2026-08-07-AI-for-Physics全景图-五条路线与AI落点分析]] — Transformer 架构是路线 B 数值模拟的基础
- [[2026-08-07-LLM微调从能力增强到成本工程-2026决策指南]] — 微调决策框架，本书 Ch6/Ch7 是其基础实现
