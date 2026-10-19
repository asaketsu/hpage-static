# A100 局域网部署 DeepSeek-V4-Flash：框架选型与 8 卡微调指南

> **出处**：飞书知识库《在A100的gpu配置下在局域网中部署deepseek-v4-flash》（wiki S6YMw41Qoi2vtWksLRocG0FknLh）——AI 生成文档（含引用标注 [1]-[9]），经交叉核对后收录
> **记录日期**：2026-08-16

**标签**：#A100 #DeepSeek #vLLM #SGLang #Ollama #DeepSpeed #局域网部署 #推理服务

---

## 一、核心内容（原文完整还原）

文档分三大块：**推理框架对比选型 → 8 卡微调指南 → SGLang 进阶部署**。

### 1.1 推理框架三选一（原文决策规则）

| 场景 | 选型 | 理由 |
|------|------|------|
| 协同 >10 人 / 高并发 API | **vLLM** | PagedAttention 吃满 A100 2TB/s 带宽 |
| 个人开发 / 小团队偶尔调用 | **Ollama** | 快速搭 UI（+Open WebUI） |
| DeepSeek MLA/MoE 架构极致优化 | **SGLang** | RadixAttention + DPA+EP 混合并行 |

### 1.2 vLLM 生产级部署（原文命令）

**单卡启动**：
```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-V4-Flash \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 4096 --gpu-memory-utilization 0.90
```

**多卡并行**（关键：`--tensor-parallel-size` = 实际卡数）：
```bash
export CUDA_VISIBLE_DEVICES=0,1
python3 -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-V4-Flash \
    --host 0.0.0.0 --port 8000 \
    --tensor-parallel-size 2 --trust-remote-code
```

**局域网验证**（任意内网机器 OpenAI 协议 curl）：
```bash
curl http://192.168.1.100:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-ai/DeepSeek-V4-Flash",
       "messages": [{"role": "user", "content": "你好，请确认你的模型名称。"}]}'
```

### 1.3 Ollama 轻量部署（原文要点）

Ollama 默认只听 127.0.0.1，**必须改 systemd 配置**开局域网：
```ini
# sudo systemctl edit ollama.service
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```
```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
ollama run deepseek-v4-flash
```

### 1.4 8 卡微调：Accelerate + DeepSpeed ZeRO-3（原文流程）

**架构理由**：ZeRO-3 把参数/梯度/优化器状态切分 8 卡（单机可微调千亿级）；NVLink 带宽吃满；MASTER_ADDR 配局域网 IP 后任意客户端 SSH 提交。

**环境验证**（第一步）：
```bash
nvidia-smi topo -m   # 卡间显示 NV8/NVLink = 全互联正常，8 卡微调前提
```

**accelerate 交互配置**（8 卡 bf16 DeepSpeed ZeRO-3）：This machine → multi-GPU → 1 机 → 8 GPU → bf16 → DeepSpeed → ZeRO Stage 3。

**ds_config.json 关键段**：
```json
{
  "bf16": { "enabled": true },
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": { "device": "cpu", "pin_memory": true },
    "offload_param": { "device": "none" },
    "overlap_comm": true,
    "reduce_bucket_size": "auto",
    "stage3_prefetch_bucket_size": "auto"
  },
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto"
}
```

**局域网远程提交**（客户端无需 CUDA）：
```bash
ssh user@192.168.1.100 "cd /path/to/project && conda activate deepseek && nohup accelerate launch train.py > train.log 2>&1 &"
```

**监控**：`tensorboard --host=0.0.0.0 --port=6006` → 内网浏览器 http://192.168.1.100:6006

**多人分卡**（轻量团队替代 Slurm）：`CUDA_VISIBLE_DEVICES=0,1,2,3` 给工程师 A / `4,5,6,7` 给工程师 B。

### 1.5 SGLang 进阶（原文宣称的优势）

- **RadixAttention**：共享 System Prompt 前缀"零开销"复用，TTFT 降低 70%+
- **DPA+EP 混合并行**：MoE 专家用 FlashInfer+DeepEP 算子，吞吐比纯 TP 高 3-5×
- **FP8/FP4 混合量化内核**：省显存换更大 KV Cache 批并发
- **部署**：官方建议 Docker（`lmsysorg/sglang:latest`），8 卡 `--tensor-parallel-size 8`；高并发改 `--tp 4 --dp 2`；配 `--moe-runner-backend flashinfer_mxfp4` 与 `--reasoning-parser deepseek-v4`

---

## 二、五要素展开

### 2.1 功能清单

| 功能 | 命令/配置 | 来源 |
|------|-----------|------|
| vLLM 单卡/多卡推理服务 | api_server + TP 参数 | 原文 §二 |
| Ollama 局域网化 | systemd OLLAMA_HOST | 原文 §三 |
| OpenAI 协议验证 | curl /v1/chat/completions | 原文 §四 |
| 8 卡 ZeRO-3 微调 | accelerate + ds_config | 原文 §四(微调) |
| SSH 远程提交 + nohup | 断线训练不断 | 原文 §四 |
| TensorBoard 局域网监控 | --host 0.0.0.0:6006 | 原文 §四 |
| 多人分卡 | CUDA_VISIBLE_DEVICES | 原文 §五 |
| SGLang Docker 部署 | lmsysorg/sglang | 原文 SGLang 节 |

### 2.2 使用性评估（含可信度核对）

**可直接照抄的部分**：vLLM/Ollama 启动命令、systemd 局域网配置、accelerate 交互流程、ds_config.json、SSH+nohup 提交、TensorBoard 监控、CUDA_VISIBLE_DEVICES 分卡——与官方文档惯例完全一致，**低风险**。

**需要存疑的部分（AI 文档幻觉风险点）**：
- `deepseek-ai/DeepSeek-V4-Flash` 的模型 ID 是否在 HF 真实存在需核验（AI 生成文档常见"拼装型号名"）
- SGLang "TTFT 降 70%/吞吐 3-5×" 是无出处的数字，方向正确（RadixAttention/DP-EP 均为真机制）但幅度未经独立基准验证
- `--moe-runner-backend flashinfer_mxfp4`、`--reasoning-parser deepseek-v4` 参数名需对 SGLang 当前版本文档核验
- A100（SM80）**不支持 FP8 硬件加速**（Hopper 起）；SGLang 的 FP8 优势在 A100 上大打折扣——原文未提示此硬件限制

### 2.3 指导性意见

- **决策顺序**：先用 vLLM 起服务（生态最稳）→ 并发痛了再迁 SGLang（DeepSeek MLA 专属优化）→ 个人玩用 Ollama
- **A100 上别指望 FP8**：量化优势场景在 H100/H200；A100 的甜点是 bf16 + PagedAttention/RadixAttention 这类显存管理优化
- **微调选型对齐既有手册**：全量微调用本文 ZeRO-3 流程；LoRA/QLoRA 调行为直接套 `a100-training-playbook` 三档模板（更省显存）
- **多人共用先分卡后上 Slurm**：<5 人 CUDA_VISIBLE_DEVICES 够用；任务排队/优先级需求出现再上 Slurm/K8s+Volcano
- **局域网安全**：0.0.0.0 监听 = 局域网裸奔，内网可信环境可接受，跨网段务必加反向代理+鉴权

### 2.4 案例可寻

- 原文自带完整命令链（环境→启动→验证→监控→远程提交）可直接作为最小落地案例
- 体系内姊妹实例：`lan-llm-farm`（Jetson 网关已建）承接本文的"局域网调用层"；`a100-training-playbook`（7 脚本实测）承接"训练工程层"——本文补齐"推理服务层"最后一块

### 2.5 使用方法借鉴（最小落地路径）

```bash
# ① 环境（A100 服务器）
conda create -n deepseek python=3.10 -y && conda activate deepseek
pip install vllm
# ② 起服务（8 卡全量）
python3 -m vllm.entrypoints.openai.api_server \
    --model <核验后的真实模型ID> --host 0.0.0.0 --port 8000 \
    --tensor-parallel-size 8 --gpu-memory-utilization 0.90
# ③ 局域网任意机器验证
curl http://<服务器IP>:8000/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"model":"...","messages":[{"role":"user","content":"ping"}]}'
```

---

## 三、查询拓展

1. **模型 ID 核验优先**：AI 生成文档的型号名（V4-Flash）先在 HF/官方渠道确认存在与确切 repo 路径，再抄命令——模型名错则全链路白搭
2. **vLLM vs SGLang 的真实分界**：vLLM 通用生态强（/v1 兼容、工具链全），SGLang 在 DeepSeek MLA/MoE + 高并发多轮对话场景有结构优势（前缀缓存/专家并行）——先跑 vLLM 基准再决定迁移
3. **RadixAttention 原理**：基数树组织的 KV 前缀缓存，多用户共享 system prompt 时命中即免重算——与 vLLM 的 automatic prefix caching 同思想不同实现
4. **ZeRO-3 offload 取舍**：显存够（A100 80G×8）就 `offload_param: none` 保速度；40G 卡微调大模型才开 CPU offload（速度降但能装下）
5. **Slurm 最小化引入**：团队规模到排队冲突时，先试 `submitit`/`torchrun --rdzv` 这类轻量方案，Slurm 是终极形态不是第一步

---

## 四、内容整理

**原文信息架构**：推理三框架对比（决策规则清晰）→ vLLM 命令（单卡/多卡/验证）→ Ollama UI 路线 → 8 卡微调全流程（拓扑验证→accelerate→ds_config→SSH 提交→监控→分卡）→ SGLang 进阶（三优势+Docker）。

**本笔记动作**：全文收录命令层（可抄）+ 逐段可信度分层（AI 文档必须做幻觉排查）+ 与既有体系三件套对位（本文=推理服务层）。

**体系拼图完成度**：a100-training-playbook（训练层）+ lan-llm-farm（网关层）+ 本文（推理服务层）= 局域网 A100 全栈调用方案。

---

## 五、趋势判断

1. **SGLang 类专用框架会吃掉 DeepSeek 系部署份额**：MLA/MoE 专属优化+前缀缓存是通用框架难追的结构性优势，6-12 个月内成为 DeepSeek 部署默认选项
2. **FP8/FP4 是 Hopper+ 世代红利**：A100 集群部署文档里的量化收益宣传要打折——Ada/Hopper 才有硬件加速，A100 停留在 bf16/int8
3. **推理与训练一体化调度**：白天推理服务/夜间微调训练的时分复用（gpu-farm-engineering 模式）会成为小团队算力标配
4. **Docker 成为复杂算子栈唯一发行方式**：SGLang/DeepEP/FlashMLA 依赖链手装地狱，容器化是不可逆趋势
5. **局域网 LLM 服务标准化**：OpenAI 协议 + 0.0.0.0 监听 + curl 验证三件套已是行业惯例，差异只在并行策略与缓存机制

---

## 六、归纳总结

**一句话**：A100 局域网部署三档选型——vLLM（高并发生产）/Ollama（轻量 UI）/SGLang（DeepSeek 专属优化），8 卡微调走 accelerate+ZeRO-3+SSH 提交；本文是 AI 生成文档，命令层可信可直接抄，数字层（70%/3-5×）与参数名需上机核验，A100 无 FP8 硬件加速是原文未提示的最大盲区。

**结构记忆**：
- 三框架：vLLM 稳 / Ollama 轻 / SGLang 专（DeepSeek）
- 微调五步：topo 验证 → accelerate 配置 → ds_config ZeRO-3 → SSH nohup 提交 → TensorBoard 监控
- 三个核验点：模型 ID / 性能数字 / FP8 硬件限制
- 体系定位：本文=推理服务层，与 training-playbook/lan-llm-farm 组成全栈

---

## 七、关联分析

| 关联 | 关系 |
|------|------|
| a100-training-playbook | 训练工程层姊妹篇：本文微调流程的深度展开与模板化 |
| lan-llm-farm | 网关层：本文部署的服务可挂入其统一提交入口 |
| Qwen3.8-27B 部署研究 | 同类部署方法论（VRAM 核算→引擎选型→启动命令），可互为参照 |
| gpu-farm-engineering | 时分复用：白天推理（本文）/夜间训练（playbook） |
| 代理模型 vs 降阶模型笔记 | A100 负载画像的另一极：LLM 推理服务 vs 科学计算训练 |

---

## 八、行动清单

- [x] 飞书文档全文提取 + 可信度分层笔记
- [ ] 上机核验：模型 ID 真实 repo、SGLang 参数名、TTFT/吞吐数字
- [ ] A100 真机：vLLM 8 卡 TP 部署基准（TTFT/吞吐实测）
- [ ] SGLang vs vLLM 对比基准（共享前缀多轮场景）
- [ ] 与 lan-llm-farm 网关联调（OpenAI 协议统一入口）

---

## 九、一句话总结

> 局域网 A100 部署 DeepSeek 三档口诀——多人并发 vLLM、个人把玩 Ollama、DeepSeek 极致 SGLang；8 卡微调 ZeRO-3 + SSH 提交；命令可直接抄，数字须核验，A100 没有 FP8 红利。


## 相关笔记

- [8卡A100局域网训练微调全流程指导](./2026-08-16-8卡A100局域网训练微调全流程指导.md) — 姊妹篇：部署（本文）+ 训练微调
- [LLM推理引擎竞争-vLLM-vs-SGLang](./2026-08-14-LLM推理引擎竞争-vLLM-vs-SGLang.md) — 三档框架选型的引擎层对比
- [局域网A100算力池×双OCR-批量文档与微调业务流程](./2026-08-15-局域网A100算力池×双OCR-批量文档与微调业务流程.md) — 算力池业务化应用层
- [投机解码生产化指南-EAGLE-3到P-EAGLE的vLLM实践](./2026-08-17-投机解码生产化指南-EAGLE-3到P-EAGLE的vLLM实践.md) — 部署后叠加投机解码提速
