---
title: ASC26 UnifoLM-WMA 世界模型推理复现完整实战（含 5 问题排查与 PSNR 归因疑点）
date: 2026-08-31
source: /home/jc/uclaw/project/process_record.md + /home/jc/uclaw/project/姓名_学号_ASC_WMA课后作业报告.docx
author: jc（ASC 课后作业实操）
tags: [UnifoLM-WMA, 世界模型, AutoDL, RTX 4090, 推理优化, PSNR, ASC26, 扩散模型, 具身智能]
---

# ASC26 UnifoLM-WMA 世界模型推理复现完整实战

> **素材**：实操日志 `process_record.md`（174 行）+ 作业报告 `姓名_学号_ASC_WMA课后作业报告.docx`（254 行）
> **术语校正**：本流程为 **Baseline 推理评测**（inference），非训练（training）——全程无梯度更新、无损失函数。"训练流程"实为"复现流程"，下文统一用准确表述。

## 导读：一页看懂

| 维度 | 数据 |
|------|------|
| 任务 | ASC26 具身世界模型优化课后作业：跑通 UnifoLM-WMA baseline 推理并计算 PSNR |
| 场景 | `unitree_g1_pack_camera` case1（5 场景之一：G1 机器人打包相机） |
| 平台 | AutoDL 容器，RTX 4090 24GB，torch 2.3.1+cu121，Python 3.10.18，conda env `unifolm` |
| 结果 | 推理成功完成，输出 22s 视频（8.3MB），**PSNR 9.11 dB（目标 ≥25 dB，未达标）** |
| 性能基线 | 53.03 s/it × 11 轮 = 11m4.8s；显存 19205/24564 MiB（78%）；GPU 利用率 94%；70°C |
| 踩坑数 | **5 个**（CSV 路径 / CLIP 下载 / ckpt 目录 / dataset 配置 / stats.safetensors 缺失） |

**关键结论预览**：① 流程已完全跑通，性能基线可信；② PSNR 9.11 dB 的官方归因（自回归幻觉）之外，**存在两个更硬的可疑点**——手写 CSV 示例数据 + stats.safetensors 零张量占位，可能导致动作轨迹整体偏离 GT（见 §9 疑点分析）。

---

## 1. 任务背景与系统架构

### 1.1 什么是 UnifoLM-WMA

UnifoLM-WMA（unitreerobotics/UnifoLM-WMA-0-Dual）是宇树开源的**具身世界模型**：给定历史帧 + 动作序列，自回归地预测未来视频帧。推理管线两级结构：

```
GT首帧 + 动作序列(CSV prompt)
   │
   ▼
World Model 前向 ──预测下一帧隐状态──► Diffusion Model 去噪(50步DDIM)
   ▲                                      │
   └──────── 生成的帧回灌作为下一步条件 ◄──┘   （自回归 × 11 轮迭代）
   │
   ▼
拼接输出 0_full_fs6.mp4 ←─与 GT 视频逐帧算 PSNR─► psnr_result.json
```

### 1.2 ASC26 作业设定

- 仓库：`github.com/ASC-Competition/ASC26-Embodied-World-Model-Optimization`（248 objects，64.09 MiB）
- 5 个评测场景（各含 case 目录 + GT 视频 + prompt CSV）：`unitree_g1_pack_camera`、`unitree_z1_stackbox`、`unitree_z1_dual_arm_stackbox`、`unitree_z1_dual_arm_stackbox_v2`、`unitree_z1_dual_arm_cleanup_pencils`
- 达标线：**PSNR ≥ 25 dB**；提交物：`output.log` + 推理视频 + psnr_result.json
- 本次选择：`unitree_g1_pack_camera` case1，`--frame_stride 6`、`--n_iter 11`（从官方总脚本 `run_world_model_interaction.sh` 的场景数组中提取）

## 2. 环境配置（日志 §1 + 报告 §3 合并）

```bash
# AutoDL 开机（下载阶段用无 GPU 模式省钱，推理前重启切 GPU 模式——日志原文：'重启打开gpu'）
conda activate unifolm

# unifolm-world-model-action 仓库无 requirements.txt，走 pyproject.toml
git clone https://github.com/unitreerobotics/unifolm-world-model-action
cd unifolm-world-model-action
pip install .
```

环境自检（日志原样照录）：

```
(unifolm) root@autodl-container-cy4y65yjz3-56645edd:~/autodl-tmp# which python
/root/miniconda3/envs/unifolm/bin/python
(unifolm) ...# python --version
Python 3.10.18
(unifolm) ...# python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda)"
2.3.1+cu121
True
12.1
(unifolm) ...# python -c "import torch; print(torch.cuda.get_device_name(0))"
NVIDIA GeForce RTX 4090
```

配置备份习惯（好实践，照录）：

```bash
cp world_model_interaction.yaml world_model_interaction.yaml.bak
```

## 3. 数据集与权重下载

### 3.1 作业数据集（走 AutoDL 学术加速）

```bash
source /etc/network_turbo   # AutoDL 学术加速：仅 github/HF，其他源反而变慢
git clone https://github.com/ASC-Competition/ASC26-Embodied-World-Model-Optimization.git
# 248 objects, 64.09 MiB @ 10.67 MiB/s
```

### 3.2 模型权重（HF 中断 → 魔搭镜像）

```bash
pip install modelscope
modelscope download --model unitreerobotics/UnifoLM-WMA-0-Dual \
  --local_dir /root/autodl-tmp/UnifoLM-WMA-0-Dual
# Downloading 10 files ... 29:02 完成，含核心权重 unifolm_wma_dual.ckpt
```

### 3.3 隐性依赖：CLIP-ViT-H-14

文本/视觉特征提取依赖 `CLIP-ViT-H-14 (laion2b_s32b_b79k)`，**首次推理时自动下载**（日志现象：卡在 `Loading pretrained ViT-H-14 weights`）。国内环境需先设镜像（见 §6 问题 2）。

## 4. 配置文件修改

`configs/inference/world_model_interaction.yaml` 两处：

| 配置项 | 修改前 | 修改后 |
|--------|--------|--------|
| `data_dir` | `/path/to/unifolm-world-model-action/examples/world_model_interaction_prompts` | `/root/autodl-tmp/asc_homework_data/ASC26-Embodied-World-Model-Optimization` |
| `dataset_and_weights` | 5 场景各 0.2（遍历所有场景） | 只保留/指向目标场景（否则报找 `unitree_z1_stackbox.csv`，见问题 4） |

`dataset_and_weights` 原始内容（日志照录）：

```yaml
dataset_and_weights:
  unitree_z1_stackbox: 0.2
  unitree_z1_dual_arm_stackbox: 0.2
  unitree_z1_dual_arm_stackbox_v2: 0.2
  unitree_z1_dual_arm_cleanup_pencils: 0.2
  unitree_g1_pack_camera: 0.2
```

## 5. 推理命令与参数全解

最终可用命令（日志终版，直接可复用）：

```bash
{ time CUDA_VISIBLE_DEVICES=0 python3 scripts/evaluation/world_model_interaction.py \
    --seed 123 \
    --ckpt_path /root/autodl-tmp/UnifoLM-WMA-0-Dual/unifolm_wma_dual.ckpt \
    --config configs/inference/world_model_interaction.yaml \
    --savedir /root/autodl-tmp/unifolm-world-model-action/output/testing/unitree_g1_pack_camera \
    --bs 1 --height 320 --width 512 \
    --unconditional_guidance_scale 1.0 \
    --ddim_steps 50 \
    --ddim_eta 1.0 \
    --prompt_dir /root/autodl-tmp/asc_homework_data/ASC26-Embodied-World-Model-Optimization/unitree_g1_pack_camera/case1/world_model_interaction_prompts \
    --dataset unitree_g1_pack_camera \
    --video_length 16 \
    --frame_stride 6 \
    --n_action_steps 16 \
    --exe_steps 16 \
    --n_iter 11 \
    --timestep_spacing 'uniform_trailing' \
    --guidance_rescale 0.7 \
    --perframe_ae; } 2>&1 | tee output.log
```

参数逐项（报告 §3.3 + 补全）：

| 参数 | 值 | 含义与出处 |
|------|-----|-----------|
| `--ckpt_path` | .../unifolm_wma_dual.ckpt | 模型权重**文件**（初版指向目录报 IsADirectoryError，见问题 3） |
| `--prompt_dir` | .../case1/world_model_interaction_prompts | prompt 目录要**指到 case1 子目录**（初版指向仓库根报 CSV 找不到，见问题 1） |
| `--dataset` | unitree_g1_pack_camera | 只跑这一个场景 |
| `--bs` | 1 | batch size（显存余量 5GB，可试加大） |
| `--height/--width` | 320/512 | 生成分辨率 |
| `--video_length` | 16 | 每次生成 16 帧 |
| `--frame_stride` | 6 | 帧间隔 6（官方脚本场景数组提取） |
| `--n_action_steps / --exe_steps` | 16/16 | 动作步数/执行步数 |
| `--n_iter` | 11 | 自回归迭代 11 轮（16帧×11轮 ≈ 176 帧 ≈ 22s 视频） |
| `--ddim_steps` | 50 | 扩散去噪 50 步（**耗时主体**，报告 §7.3 证实） |
| `--ddim_eta` | 1.0 | DDIM 随机性 |
| `--unconditional_guidance_scale` | 1.0 | CFG 无条件引导强度 |
| `--guidance_rescale` | 0.7 | CFG 重标定（CFG-rescale 技巧，防过饱和） |
| `--timestep_spacing` | uniform_trailing | 时间步采样策略 |
| `--perframe_ae` | 开 | 逐帧自编码器（视频 VAE 按帧处理） |
| `tee output.log` | — | 作业要求提交的日志文件 |

## 6. 五个问题排查实录（日志独有细节，报告未全收录）

| # | 现象（报错原文） | 根因 | 修复 |
|---|----------------|------|------|
| 1 | `FileNotFoundError: .../unitree_g1_pack_camera.csv` | `--prompt_dir` 指向仓库根，CSV 实际在 case 子目录深层 | 改为 `.../unitree_g1_pack_camera/case1/world_model_interaction_prompts`（真实路径 `find` 确认） |
| 2 | 卡在下载 CLIP-ViT-H-14 | 容器连不上 huggingface.co | `export HF_ENDPOINT=https://hf-mirror.com` 切国内镜像 |
| 3 | `IsADirectoryError: [Errno 21] Is a directory: '/root/autodl-tmp/UnifoLM-WMA-0-Dual'` | ckpt_path 指向了目录而非权重文件 | `find ... -name "*.ckpt" -o -name "*.pth"` 定位 → 改指 `unifolm_wma_dual.ckpt` |
| 4 | `FileNotFoundError: .../unitree_z1_stackbox.csv`（明明指定的是 g1_pack_camera） | yaml 的 `dataset_and_weights` 含全部 5 场景，按权重轮询到别的场景 | 改配置只留目标场景 + **手写 CSV 表头和一行示例数据** ⚠️（埋雷，见 §9） |
| 5 | 缺 `stats.safetensors` | 作业数据仓不含 transitions 元数据 | 创建目录 + 写入**零张量占位字典** ⚠️（埋雷，见 §9） |

问题 5 的占位文件构造（日志照录）：

```bash
mkdir -p /root/autodl-tmp/asc_homework_data/ASC26-Embodied-World-Model-Optimization/transitions/unitree_g1_pack_camera/meta_data

python3 -c "
from safetensors.torch import save_file
import torch
# 创建一个包含 'action' 键的字典，值为一个形状为 (1,) 的张量
# 这足以让程序通过 self.stats['action']['max'].shape[-1] 的检查
stats = {
    'action_max': torch.zeros(1),
    'action_min': torch.zeros(1),
}
save_file(stats, '/root/autodl-tmp/asc_homework_data/ASC26-Embodied-World-Model-Optimization/transitions/unitree_g1_pack_camera/meta_data/stats.safetensors')"
```

另有两个报告补充的小问题：`psnr_score_for_challenge.py` 需绝对路径调用（在数据集目录而非代码仓）；脚本必须在项目根目录执行。

## 7. 运行结果与性能基线

| 指标 | 数值 | 解读 |
|------|------|------|
| 单步耗时 | 53.03 s/it | 每轮 = WM 前向 + 50 步 DDIM 去噪 |
| 总耗时 | 11m4.845s | 11 轮自回归 |
| 显存峰值 | 19205 / 24564 MiB（78%） | 余 ~5GB → batching/缓存有空间 |
| GPU 利用率 | 94% | 计算密集，无 I/O 等待瓶颈 |
| GPU 温度 | 70°C | 健康，可上强度 |
| 输出 | `0_full_fs6.mp4`，8.3MB，约 22s | 初始帧"绘画感"模糊，后续帧收敛，机械臂打包动作可辨 |
| 中间产物 | `sample_0/dm/6/itr-0..10.mp4`、`sample_0/wm/6/itr-0..10.mp4`、tensorboard/ | dm=扩散模型中间帧，wm=世界模型中间帧 |

报告 §7.8 的方法论点（有价值，照录结论）：**GPU 利用率高 ≠ 高效**——94% 只说明计算单元忙，瓶颈可能在 kernel 本身太重（50 步去噪）、显存带宽、或 O(n) 自回归复杂度，不能靠"利用率满"排除优化空间。

## 8. PSNR 评测

```bash
# 1. 定位 GT 视频
find /root/autodl-tmp -name "*.mp4" | grep "unitree_g1_pack_camera"
# → .../unitree_g1_pack_camera/case1/unitree_g1_pack_camera_case1.mp4

# 2. 计算分数
python3 /root/autodl-tmp/asc_homework_data/ASC26-Embodied-World-Model-Optimization/psnr_score_for_challenge.py \
  --gt_video  .../unitree_g1_pack_camera/case1/unitree_g1_pack_camera_case1.mp4 \
  --pred_video .../output/testing/unitree_g1_pack_camera/inference/0_full_fs6.mp4 \
  --output_file .../output/testing/unitree_g1_pack_camera/psnr_result.json
```

`psnr_result.json` 原文：

```json
{
  "gt_video": ".../unitree_g1_pack_camera/case1/unitree_g1_pack_camera_case1.mp4",
  "pred_video": ".../output/testing/unitree_g1_pack_camera/inference/0_full_fs6.mp4",
  "psnr": 9.11
}
```

**9.11 dB vs 目标 25 dB：未达标**。量级感校准（补充）：对齐良好的重建视频 PSNR 通常 25-35 dB；内容相同但轻微错位的视频 ~15-20 dB；**内容完全不同的两段视频 ≈ 7-10 dB**。9.11 dB 已接近"内容不同"档——这是 §9 疑点分析的出发点。

## 9. 归因分析：报告的四点 + 两个被忽略的硬可疑点

### 9.1 报告原文归因（照录）

1. **扩散模型自回归累积误差（核心）**：初始帧"抽象/模糊"幻觉，MSE 逐像素指标被前几帧严重拉低；每步误差累积放大
2. **世界模型预测特性**：WMA 任务是物理规律预测而非像素级重建，长程推演中动作偏差被放大
3. **硬件与精度限制**：消费级 4090，FP16 与专业卡 BF16 有差异，"可能导致 PSNR 偏差 1-2 dB"
4. **帧数与时序对齐**：生成帧率（frame_stride=6）与 GT 时序微小错位，像素级错位急剧拉低 PSNR

### 9.2 ⚠️ 疑点一：手写 CSV prompt（问题 4 的修复方式）

日志明确记录："**向 CSV 文件中写入一行表头和一行示例数据**"。这意味着推理吃的动作序列是**手工编造的示例行，不是官方 GT 动作序列**。世界模型是开环 rollout：动作不同 → 轨迹不同 → 生成视频与 GT 从动作执行的第一步起就分叉。这足以单独把 PSNR 打到 7-10 dB 档（与实测 9.11 吻合）。**在换回官方 CSV 之前，任何"自回归幻觉"归因都无法证实。**

### 9.3 ⚠️ 疑点二：stats.safetensors 零张量占位（问题 5 的修复方式）

占位注释写明目的是"通过 `self.stats['action']['max'].shape[-1]` 的检查"。但代码既然后续会读 `action_max/action_min`，**若用于动作反归一化（denormalize），全零 stats 会让动作解码整体失真**（min=max=0 时归一化区间宽度为 0，除零或动作全坍缩）。需要读源码确认 stats 是否只做 shape 校验——若是则无害，若参与反归一化则是第二个雷。

### 9.4 对报告归因的两处技术商榷（证据式反驳）

| 报告论点 | 商榷 | 依据 |
|---------|------|------|
| "受限于显存，未能开启 BF16" | **不成立**：BF16 比 FP32 更省显存，开启它不需要额外显存；且 RTX 4090（Ada Lovelace）**完整支持 BF16 Tensor Core**，不存在"消费级卡做不了 BF16" | 显存实测余量 5GB；Ada 架构规格 |
| "消费卡 FP16 与专业卡 BF16 差异导致 1-2 dB 偏差" | **无依据**：数值精度差异影响的是数值稳定性，同 seed 下 FP32 vs BF16 的 PSNR 波动通常 <0.5 dB，量级估计过大 | 混合精度推理常规结论 |

真实原因排序（我的判断）：**CSV 动作序列非官方（疑点一）≫ stats 占位（疑点二）> 自回归累积误差 > 时序对齐**。验证顺序也应如此：先换官方 CSV 重跑一次（成本 11 分钟），PSNR 若跳回 20+ dB 则疑点坐实。

## 10. 优化路线图（报告 §7.9/§8 + 技术依据补全）

| 方向 | 报告预期 | 技术依据与补全 | 优先级 |
|------|---------|---------------|--------|
| 修复数据依赖（本笔记新增） | 未列 | 换官方 prompt CSV + 真实 stats.safetensors，先验证正确性再谈优化 | **P0——正确性优先于速度** |
| BF16/FP16 混合精度 | 速度 1.5-2× | 4090 Tensor Core 原生支持；同时降显存（腾出 batching 空间） | P1 |
| KV-Cache（WM attention） | 每步 -20-30% | 适用于 World Model 若为 Transformer 结构的自回归 attention（原理见姊妹篇 [KV Cache 笔记](https://hpage.top/bookmarks/notes/2026-08-30-%E4%B8%BA%E4%BB%80%E4%B9%88KVCache%E5%8F%AA%E5%AD%98K%E5%92%8CV%E4%BB%8E%E4%B8%8D%E5%AD%98Q.html)：K/V 是 append-only 累积量，历史帧的 K/V 每步复用，缓存必有收益）。注意：**扩散 U-Net 部分不适用 LLM 式 KV-Cache**，报告未区分这一点 | P1 |
| TensorRT 编译 | 纯计算 2-3× | DDIM 50 步是耗时主体，算子融合收益最大；可与 BF16 叠加。Jetson 侧经验：TRT 对扩散模型 FP16 加速约 2-2.5×（见 [DUCK-Pi_5 笔记](https://hpage.top/bookmarks/notes/2026-08-29-DUCK-Pi_5%E6%A0%91%E8%8E%84%E6%B4%BE%E4%B8%BB%E6%8E%A7%E7%A7%BB%E6%A4%8D%E5%AE%8C%E6%95%B4%E6%96%B9%E6%A1%88.html) TensorRT 部署章节） | P2 |
| 增大 Batch Size | 吞吐↑ | 5GB 余量下 bs=1→2 可行；注意 bs 对 PSNR 无收益，只对吞吐 | P2 |
| 关键帧重初始化 | 消自回归误差 | 周期性用 GT 帧重锚定（若规则允许——**比赛语境下需先确认是否违反开箱评测**） | P3 |

正确性保障（报告 §7.10 照录）：优化前后同脚本算 PSNR 对比（降幅 >2dB 需调参）、人工看视频、对比同 Step 中间帧、查 output.log 无异常。

## 11. 与既有 AutoDL 实战笔记的对照

| 维度 | 本篇（WMA 推理） | [AutoDL 4090 训练 16GB 数据集](https://hpage.top/bookmarks/notes/2026-08-29-AutoDL%E7%A7%9F%E7%94%A84090%E8%AE%AD%E7%BB%8316GB%E6%95%B0%E6%8D%AE%E9%9B%86%E5%AE%8C%E6%95%B4%E5%AE%9E%E6%88%98.html) |
|------|----------------|------------------|
| 任务类型 | 推理评测（无梯度） | 训练（有梯度） |
| 无 GPU 省钱模式 | 下载/配置阶段 | 数据准备阶段 |
| 国内镜像 | modelscope（权重）+ hf-mirror（CLIP） | HF 镜像 + pip 源 |
| 显存策略 | 78% 余 5GB | AMP 混合精度压显存 |
| 踩坑模式 | 路径/配置/缺失文件 5 连 | OOM/依赖/长时任务断点 |

两篇合并即为 AutoDL 4090 的"训练+推理"完整手册。

## 12. 复现清单（浓缩版，可直接照抄执行）

```bash
# 1. 环境
conda activate unifolm && pip install .            # pyproject.toml
# 2. 数据（学术加速）
source /etc/network_turbo && git clone https://github.com/ASC-Competition/ASC26-Embodied-World-Model-Optimization.git
# 3. 权重（魔搭）
modelscope download --model unitreerobotics/UnifoLM-WMA-0-Dual --local_dir /root/autodl-tmp/UnifoLM-WMA-0-Dual
# 4. 镜像 + 配置
export HF_ENDPOINT=https://hf-mirror.com           # CLIP 自动下载走镜像
vim configs/inference/world_model_interaction.yaml  # data_dir + dataset_and_weights
# 5. 推理（§5 完整命令，注意 ckpt 文件路径 + prompt_dir 到 case1）
# 6. 评测
python3 .../psnr_score_for_challenge.py --gt_video <GT> --pred_video <输出> --output_file psnr_result.json
```

## 出处

- 实操日志：`/home/jc/uclaw/project/process_record.md`（174 行，2026-08-30 16:13）
- 作业报告：`/home/jc/uclaw/project/姓名_学号_ASC_WMA课后作业报告.docx`（254 段，2026-08-30 16:33，docx XML 直接解包提取）
- §1/§9.4/§10 优先级与"疑点"两节为分析补充，其余为两份素材合并整理（日志细节 > 报告表格，冲突处以日志为准——报告未收录问题 2/3/5 的完整修复过程）
- 姊妹篇：[为什么KVCache只存K和V从不存Q](https://hpage.top/bookmarks/notes/2026-08-30-%E4%B8%BA%E4%BB%80%E4%B9%88KVCache%E5%8F%AA%E5%AD%98K%E5%92%8CV%E4%BB%8E%E4%B8%8D%E5%AD%98Q.html)、[AutoDL租用4090训练16GB数据集完整实战](https://hpage.top/bookmarks/notes/2026-08-29-AutoDL%E7%A7%9F%E7%94%A84090%E8%AE%AD%E7%BB%8316GB%E6%95%B0%E6%8D%AE%E9%9B%86%E5%AE%8C%E6%95%B4%E5%AE%9E%E6%88%98.html)、[DUCK-Pi_5树莓派主控移植完整方案](https://hpage.top/bookmarks/notes/2026-08-29-DUCK-Pi_5%E6%A0%91%E8%8E%84%E6%B4%BE%E4%B8%BB%E6%8E%A7%E7%A7%BB%E6%A4%8D%E5%AE%8C%E6%95%B4%E6%96%B9%E6%A1%88.html)（TensorRT 章节）
