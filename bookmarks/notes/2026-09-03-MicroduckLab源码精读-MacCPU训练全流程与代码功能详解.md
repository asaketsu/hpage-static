# MicroduckLab源码精读 — Mac CPU训练全流程与代码功能详解

#MicroduckLab #强化学习 #PPO #Sim2Real #DUCK相关 #奖励设计 #课程学习 #CPU训练

## 出处

- 原项目：https://github.com/jonathanhawkins/microduck-lab（jonathanhawkins，53 stars，**2026-09-01 创建**，社区项目非 Pollen 官方）
- 定位：**在普通 Mac（无 CUDA GPU）上为 Microduck 训练 RL 策略，浏览器实时观看学习过程**
- 分析日期：2026-09-03 | 深度模式：clone + 全源码精读（114 文件，microduck_local 9227 行 Python + duck-viewer Next.js）
- 与我们的关系：**DUCK-Pi_5 的直接同源项目**——同样基于官方 microduck_rl 的 61-obs/14-action 契约、同 MJCF、同 50Hz；本仓库 = 官方 GPU 栈的"CPU 原型环"

## 一、内容详细整理（详细训练过程）

### 1.1 总体架构：四仓并排工作区

| 仓库 | 角色 | 技术栈 |
|------|------|--------|
| `microduck_local/`（本仓） | **CPU-MuJoCo + SB3 PPO 原型训练harness** + duck-lab 流式后端 + 🎓教学环 | Python 3.12/uv |
| `duck-viewer/`（本仓） | Next.js + react-three-fiber 浏览器查看器：多策略并排走、WS 25Hz 实时 | Next.js/TS |
| `microduck/`（上游 clone） | 机器人本体软件、官方 ONNX 策略、文档 | Rust |
| `microduck_rl/`（上游 clone） | 官方 GPU 训练栈（MuJoCo Warp + mjlab + PPO）、BAM sim2real 配方 | Python/uv |

**定位哲学**（README 原文）：官方栈需要 CUDA GPU，本项目跑在你已有的笔记本上——它是"奖励设计、课程、新技巧的原型环"，行为在这里发明后**直接移植到官方栈做最终 sim2real**，导出的 ONNX 与官方工具链 drop-in 兼容。

### 1.2 完整训练工作流（README quick start 还原）

```bash
# 0. 环境准备（Apple Silicon Mac 或 Linux，uv + Node 20+，~3GB 磁盘）
git clone microduck-lab && cd microduck-lab
git clone pollen-robotics/microduck      # 官方策略/文档
git clone pollen-robotics/microduck_rl   # MJCF 模型/官方栈
cd microduck_local && uv sync

# 1. 契约测试（训练前必跑——obs 布局/DR 恢复/惩罚符号/官方 alpha_walking 存活回归）
uv run --with pytest pytest tests/       # 应全绿

# 2. 训练第一个步态策略（M 系列 Mac 几分钟）
uv run train-walk --envs 32 --steps 3_000_000 --run-name first-gait

# 3. 导出 ONNX（obs 归一化器烘焙进去）
uv run export-walk runs/first-gait

# 4. 无头评估（摔倒/指令跟踪电池）
uv run eval-walk runs/first-gait/policy.onnx

# 5. 渲染查看（mp4 给人 + 带字幕帧接触表给 AI 读）
uv run render-rollout --policy runs/my-run/policy.onnx --behavior stand --out /tmp/rr

# 6. 启动实验室 + 查看器
uv run duck-lab runs/first-gait ../microduck/policies/alpha_walking.onnx
cd ../duck-viewer && npm install && npm run dev  # 浏览器打开
```

### 1.3 训练环境核心（walk_env.py，792 行）

**MicroduckWalkEnv(gym.Env)** 的关键设计：

- **双执行器模型**：`actuator="xml"`（快速线性化 XML 舵机，日常步态）或 `"bam"`（**诚实 BAM XL330 电压模型**，numba 融合，用于会打满舵机的机动动作）——与 DUCK-Pi_5 已知的 BAM 电压模型同源
- **域随机化**（`_apply_domain_rand`）：**先恢复编译时默认再施加**——绝不允许跨 reset 累积（契约测试锁定）
- **观测 61 维**（顺序即热交换契约，永不重排）：
  `[base_ang_vel(3), projected_gravity(3), joint_pos_rel(14), joint_vel(14), last_action(14), twist_cmd(3), head_pose_cmd(4), body_pose_cmd(6)]`
- **动作 14 维**：`target = DEFAULT_POSE + action`（scale 1.0，弧度）
- **joint_vel 滞后一个控制步**（Dynamixel 移动平均），匹配训练与硬件——**"别修它"**（不变量）
- 未用指令槽**零填充且保留微小采样范围**——保持 normalizer 活着，永不移除

### 1.4 PPO 超参与网络（train.py + ppo_hparams.py）

| 参数 | 值 | 来源与理由（注释原文还原） |
|------|-----|---------------------------|
| 网络结构 | pi/vf 各 [512,256,128] MLP | "rsl_rl 风味：偏大的 MLP" |
| 激活函数 | **ELU** | 对齐官方 rsl_rl cfg |
| n_steps | 256 | 共享常量 |
| batch 策略 | 目标 1024×4 minibatch | 复杂两段规则（见下） |
| n_epochs | 5 | — |
| learning_rate | **1e-3** | 对齐官方栈；"一半熵+三分之一学习率在更少样本上会坍缩到最安全的策略——站着不动（first-gait 学到的）" |
| gamma / gae_lambda | 0.99 / 0.95 | — |
| ent_coef | 0.01 | 对齐官方 |
| vf_coef | **1.0** | rsl_rl 的 value_loss_coef（SB3 默认 0.5 会让 critic 只有 GPU 栈一半响度） |
| log_std_init | 0.0 | — |
| 对称损失系数 | 0.5 | 上游 SYMMETRY_CFG 的 mirror_loss_coeff |

**batch_size 两段规则**（ppo_hparams.py 精读）：
- buffer < 1024×4：取 ≤1024 的最大约数（16 envs → 4×1024，与上游一致）
- buffer ≥ 1024×4：固定 4 个 minibatch（24 envs → 4×1536 而非 6×1024；28 → 4×1792 而非 7×1024）——**加 helper duck 买的是 rollout 不是更长 update**（28 envs 曾让串行 update 增长 75% 换 ~8% 更多 rollout，核全闲着）

**TORCH_INTRA_THREADS=8 的测量依据**：1024×512 Linear 在 8 线程峰值 0.38ms，PyTorch 默认 6 P-core 0.42ms，18 线程 0.42ms（E-core 帮倒忙）。**ppo_hparams 刻意不 import torch**——train.py fork SubprocVecEnv worker 之前不能拉起 OpenMP 线程池，否则 macOS fork 死锁。

### 1.5 双侧对称镜像增强（symmetry.py，883 行——本项目最有价值的算法组件）

**原理**：步态是左右对称技能，每个转移 `(o,a)` 有物理合法的孪生 `(M·o, M·a)`。**预先告诉策略这个结构，而不是让它从样本中重新发现**——这是相对官方栈的唯一差距补齐，**买的是样本效率而非更多样本**，是 CPU 训练器唯一的货币。

**镜像算子 M**（带符号置换，M∘M=I 对合）：
- **关节块（14）**：左腿(0-4)↔右腿(9-13) 交换后**全部取负**（MJCF 左右 home 坐标系相反）；中线 neck/head(5-8) 不动
- **head_yaw/head_roll 取负**（左右反射下 yaw/roll 轴反转）；neck_pitch/head_pitch 是矢状面关节**不取负**
- **base_ang_vel（陀螺仪）是伪向量**：取负 roll(x) 和 yaw(z)，保留 pitch(y)。形式化：S=diag(1,-1,1)，镜像体旋转 R'=SRS，ω'_body=-S·ω_body
- **projected_gravity 是真向量**：g'_body=S·g_body（仅 gy 取负）
- **twist 指令**：lin_vel_y 和 ang_vel_z 取负，lin_vel_x 不变
- 验证方式：test_symmetry.py 把一个 pose 镜像后检查 MuJoCo 正运动学把每个 body 放到伙伴的反射帧

**FastActorCriticPolicy**（symmetry.py 内）：手写 diag-Gaussian rollout 前向，batch 32 时 234→215μs，log-prob 与 evaluate_actions 浮点容差一致（test_fast_policy.py 锁定）。

### 1.6 九个可教技巧（behaviors/）

| 文件 | Behavior | 要点 |
|------|----------|------|
| locomotion.py | 行走族 | 速度指令跟踪 |
| poses.py | 4 个姿态 trick | 站立类 |
| headstand.py | 倒立 | **servo-ladder 模式的诞生地**（见 1.8） |
| backflip.py | 后空翻 | **5 阶段链式课程**：reverse curriculum（spawn 族环境旋钮）+ 分阶段 `--init-from` 链 |
| airflip.py | 空翻 | — |
| imitate.py | 模仿 | Animate 面板关键帧→RL 学着物理执行 |

**Behavior 数据类**（core.py）：奖励项（signed per 规则）+ 友好字符串 + 聊天关键词 + 可选 CurriculumStage。**奖励项目录**（head_up/flat_feet/calm_body/smooth_torque 等）让查看器教学面板能以滑块提供——"看起来不对的 trick 通常需要目录项，不是新的定制项"。

**教学面板反幻觉设计**：只提供 behaviors/ 里存在的 trick——**未识别的请求返回目录而非即兴编配方**（与我们的 LLM 反幻觉纪律同构）。

### 1.7 性能工程（2026-08-31 speed pass 全记录）

**实测数字**（M 系列）：~16.5k env-steps/s（32-env 出厂配方，1M 步约 1 分钟）；峰值 ~27k。

| 优化 | 手段 | 效果 | 采纳状态 |
|------|------|------|----------|
| 共享模型 fork | 编译一次 mjModel（~470MB）+ fork worker 写时复制 | 64 envs 内存 **41GB→1.5GB**；vec env 启动 7.8s→0.2s | ✅ 默认（吞吐中性 +3.9~8.3% 但一段 -4.5%，"不更慢"） |
| Semaphore IPC | 共享内存+信号量替代每步管道+pickle | 32 envs 无策略地板 1.61→1.08ms | ✅ 精确语义+奇偶测试 |
| numba 融合 BAM | ~48 次 numpy dispatch/substep → 3 个编译核 | **BITWISE 移植**（exp/power 留 numpy——SIMD 不可复现），float64 黄金 rollout 锁定 | ✅ numba 可选，无则回退 numpy |
| Overlapped update | rollout k+1 用冻结快照采集时后台 update k | +25% steps/s，**但 seed 匹配 A/B：reward/step 掉一半**（seed4@1.45M：ep_rew 530 vs 270） | ❌ opt-in 旗标（lr=1e-3 下每 update KL 太大，陈旧数据落在 clip 窗外被代理丢弃） |
| 大 batch | 64-env batch-4096 | +40% steps/s，**~2x 更少学习/步** | ❌ opt-in（加倍 lr 大部分但不完全恢复） |
| MPS 更新 | minibatch 环上 GPU | batch 1024 是 LOSS（13.5k vs 14.8k），4096 大赢（18k vs 12.5k） | ✅ auto 仅 batch≥2048 启用 |

**最重要的结论**：**reward-per-wall-second 才是真正的指标**，两个吞吐"胜利"都牺牲了每步学习——**质量安全的甜点是 32 envs（~14.8k steps/s，工作区起点的 2.2 倍）**。

### 1.8 奖励设计规则（AGENTS.md 精读——DUCK 重训最该抄的部分）

1. **永不奖励策略无法观测的东西**：obs 契约没有 yaw 和世界位置——航向/世界锚定的奖励项是不可学习的噪声（**一个这样的项产生了 30M 步的绕圈**，看着像优化器问题）。直线度/航向属于速度指令器，不属于奖励。**加项前，指出让策略看到你打分的 obs 索引**
2. **小心 MuJoCo 速度坐标系**：`mj_objectVelocity(..., flg_local=0)` 是世界系；naive 索引曾把侧向拖步奖成"前进"。写读速度的项前，先在一个你能推理的 pose 里打印它
3. **没有头奖**：稠密有界塑形胜过稀疏横财——**策略能爆一次并刷分的项一定会被刷**
4. **奖励设计无法修复探索缺口**：如果 rollout 从不包含目标技能（连瞬态/随机都没有），任何项/权重/门/ramp 都教不会——**从未采样的状态的价值永远不会被学习**。headstand 付出了整晚代价：5 个配方变体（扩展 pay ramp/坚持奖励/3× 梯度/惩罚移除/静止 spawn）全部收敛到同一个简单局部 pose，因为在诚实 BAM 舵机下**从随机行为中采不出"持续伸展的倒立"**。**修复从来不在奖励里：给物理搭梯子**——强舵机(xml)钻台阶段 + ~80% 放入式 spawn，几分钟内技能就出现在 rollout 里，然后舵机降回诚实 BAM。**动项之前先问一句："有没有 ANY rollout 做过这个事？"没有就改世界，不是改工资**
5. **课程阶段只能梯子化物理、spawn、严格度——永不奖励**：第一代分阶段失败因为每级带自己的项编辑，每级长出自己的作弊窝。headstand 梯子**每阶段保持同一密封项集**（测试强制 stage-env 旋钮白名单）——阶段可以让世界更容易或评判更严格，但**永不改变付什么钱**。查看器的 stageWeights 滑块是刻意例外（人看的实时重定价是实验不是配方；CurriculumStage 没有 weights 字段，阶段调优必须挣回来变成 term 或物理旋钮才能出厂）

### 1.9 验证纪律（六条防自欺规则）

1. **训练图度量的是噪声拐杖的随机策略**——对 run 的断言用确定性导出 ONNX，从不用 ep_rew 曲线。导出→评估→看
2. **下结论前先看**：render-rollout 写 mp4（人）+ 带字幕帧接触表（agent 读，含每帧高度/角度/接触）。**奖励电池在这里曾把脸朝下的蹲姿评为"站立"**
3. **渲染空对照**（`--policy limp`/`zero`）再归功于策略——spawn pose 或重力能做的事不算数
4. **吞吐不是学习速度**：任何让训练更快的改动在成为默认前，做 seed 匹配 A/B（匹配步数）
5. **诡异的优化器指标通常是坏奖励**：一次 KL 爆炸被当 PPO 调参问题追了一天，原因是不可学习的奖励项。**重新调"问多用力"之前先查"在要什么"**
6. **Warm-start 链会把 action std 悄悄棘轮成 bang-bang**：每次 `--init-from` 重载前 run 的 log_std，熵奖励每代推高；一条长链在 ±4 动作空间达到 std 21-26——**裁剪噪声分布在承载行为**（随机 episode 活 6.9s）而导出的确定性均值是饱和垃圾（0.5s 摔倒），遥测分不出来。LOG_STD_MAX 在加载和每次 rollout 时封顶；均值中毒的谱系无法巩固，必须从头重启。**每个 checkpoint 确定性探测 live.onnx——那才是出厂的策略**

### 1.10 duck-viewer 与 duck-lab（浏览器实时观看）

- 架构：duck-lab（Python，每个策略一个 CPU-MuJoCo env 实时 50Hz）→ GET /scene 一次性给 mesh+颜色（从编译 MuJoCo 模型直提几何，无资产管线）→ WS ~25Hz 推 body poses+stats ← 查看器发 `{"cmd":[vx,vy,wz]}`/`{"reset"}`
- **多鸭并排**：每个参数一只鸭；**训练 checkpoint 串**（--checkpoints）一只鸭一个快照——看策略在 500k 步快照间学会
- **策略芯片热交换**：拖芯片到鸭身上，**步态中途换脑**
- 🎓 教学面板：关键字匹配（无 LLM 环路）；每 ~15s 热载 live 快照看学员进步；拖奖励滑块实时微调——**无 Python 环路的奖励塑形**
- 🎬 Animate 面板：关键帧 pose 编辑器+游戏风格控制 rig；浏览器里编动作片段，"train this"让 RL 学着物理执行
- 🎥 Capture 面板：📷 全分辨率 PNG；🎥 摄像机框住一只鸭拍成 mp4+GIF（可直接贴 PR）

### 1.11 sim2real 诚实条款

本 harness 是**分钟级反馈环的原型**。即使在 `actuator="bam"` 下它也只是官方域随机化栈的子集。行为在这里跑通后，**把 env 设计移植到上游 microduck_rl 的 mjlab cfg 并在 GPU 上重训**——那才是能在真实硬件上活下来的策略配方。导出的 ONNX 虽 drop-in 兼容，但**上硬件的策略要官方栈重训**。

## 二、代码功能地图（模块级）

| 模块 | 行数 | 功能 |
|------|------|------|
| viz_server.py | 3582 | duck-lab 流式后端：多策略 env 管理/WS/teach API/capture |
| symmetry.py | 883 | 双侧镜像算子+FastActorCriticPolicy+SymmetryPPO |
| walk_env.py | 792 | 训练环境（双执行器/DR/obs/奖励计算） |
| bam_actuator.py | 728 | BAM XL330 电压模型（numba 融合核，BITWISE 对齐 numpy 参照） |
| render_rollout.py | 704 | mp4+帧接触表渲染（AI 可读字幕） |
| vec_env.py | 583 | ForkVecEnv（共享模型/信号量 IPC/四后端） |
| train_behavior.py | 532 | trick 训练器（LOG_STD_MAX/阶段链） |
| bench_envs.py | 453 | worker 数扫描推荐（真实 PPO 非裸步进） |
| motion.py | 218 | 关键帧动作片段 |
| distill.py | 177 | mjlab 蒸馏奖励 |
| train.py | 162 | 步态训练主入口 |
| contract.py | — | 61obs/14act 契约单一真相源（镜像自上游 infer_policy.py） |
| behaviors/ | — | 9 trick + 奖励项目录 + 课程阶段 |

**测试（19 个文件）**：契约锁（env_contract/behaviors 符号与关键词）、BAM 性能奇偶（float64 黄金 rollout）、对称（正运动学反射验证）、快速策略（log-prob 容差）、向量环境奇偶、导出、训练恢复、渲染 rollout、捕获、自适应 lr、惩罚尺度、bench、clips、lab、overlap、step 性能奇偶——**每个性能优化都带奇偶测试**。

## 三、查询拓展

- mjlab_distill（distill.py）如何从官方 GPU 栈蒸馏奖励到本地
- backflip 5 阶段的具体 spawn-family 旋钮与 stage detail 叙事
- `MICRODUCK_SPAWN_FAMILY_PROBS` 的族分布设计
- ForkVecEnv 的 semaphore 协议细节（信号量环）
- duck-viewer 的 GPU 陷阱（README 提到"已踩的坑"）
- Animate 面板关键帧→RL 的 imitate 数据流

## 四、归纳总结

1. **本仓库是"官方栈的原型环"这个定位本身就是最大工程智慧**：CPU 分钟级迭代（1M 步/分钟）做奖励/课程设计，收敛后移植 GPU 栈做 sim2real——**两层栈分工而非替代**，与 DUCK-Pi_5 的 AutoDL 重训计划完全同构。
2. **样本效率是 CPU 训练的唯一货币**：双侧对称镜像增强（买样本效率）、稠密有界奖励（防刷分）、课程只动物理不动奖励（防作弊窝）——三条规则全部围绕"从每一步榨出最多学习"。
3. **"改世界不改工资"是探索缺口的唯一解**：headstand 整晚失败→servo-ladder（强舵机+spawn 注入）几分钟解决的案例，是 RL 课程设计的教科书级叙事——**从未采样的状态价值永远不会被学习**。
4. **反自欺纪律密度全开源项目罕见**：确定性 ONNX 断言/render-rollout 帧表/null 对照/seed 匹配 A/B/LOG_STD_MAX 防棘轮——六条规则每条都来自真实翻车（奖励电池把脸朝下蹲姿评为站立）。
5. **性能工程的双账本**：吞吐优化全记录含被拒项（overlapped update +25% steps/s 但学习减半）——**reward-per-wall-second 才是真指标**，这个纪律值得所有训练项目抄。
6. **AI 协作设计贯穿产品**：render-rollout 的"给 AI 读的带字幕帧接触表"、behaviors 的"未识别返回目录"、AGENTS.md 的 agent playbook——这仓库把 LLM 当一等公民协作者设计。

## 五、趋势判断

1. **CPU 原型环会成为腿足 RL 的标准配置**：GPU 贵且慢启动，Mac CPU 分钟级迭代做设计、GPU 做最终训练的分层会普及（本项目 + 我们 DUCK 计划同构）。
2. **对称性先验/结构先验注入会从论文走向标配**：symmetry.py 式的"告诉策略物理结构而非让它发现"在样本受限场景是免费午餐。
3. **"AI 可读的策略检查产物"会成为训练工具标配**：帧接触表（每帧高度/角度/接触烧进图）让 LLM 能审策略——与我们的 render+看 流程同构，但更系统。
4. **奖励设计规则的形式化**（可观测性检查/无头奖/课程不改奖励）会被更多项目写成测试而非文档。

## 六、关联分析（对 DUCK-Pi_5 的直接价值 + 如何实施）

1. **【最高优先】奖励规则五条直接进 DUCK 重训 checklist**：尤其"永不奖励不可观测项"（obs61 无 yaw/世界位置——航向项是 30M 步绕圈的坑）和"课程只梯子物理/spawn/严格度"。**实施**：docs/09 实战手册重训节补引这五条（引用本笔记）。
2. **servo-ladder 模式是 STS3215 出域问题的直接对策**：DUCK 换 STS3215 增重 69% 出域，重训时若遇到"技能采不出来"，先用 xml 强舵机+spawn 注入让技能出现在 rollout，再降回诚实 BAM——**这比调奖励高效一个数量级**。**实施**：重训 runbook 加"探索缺口诊断第一步：有没有 ANY rollout 做过这个事？"
3. **验证纪律六条抄进 W0 门禁**：确定性 ONNX 断言（不用 ep_rew 曲线）、null 对照、render 后亲眼看——与我们的"渲染后看"流程互补成完整纪律。LOG_STD_MAX 防棘轮对 --init-from 链式训练是刚需。
4. **symmetry.py 可直接移植**：883 行自包含（含对上游表的交叉校验），DUCK 重训若用 SB3 PPO 路线可整文件搬——**但我们的 microduck_rl 栈已含镜像增强**（上游 SYMMETRY_CFG mirror_loss_coeff 0.5），此件主要价值是**理解**而非搬运。
5. **fork 共享模型模式对 AutoDL 多 env 训练直接适用**：41GB→1.5GB 的内存优化在 GPU 服务器同样成立（CPU 内存侧），64 env 以上必抄。
6. **与既有笔记链的合流**：本篇补上了"DUCK 训练侧外部参考"的最后一块——docs/08 官方栈精读（GPU 侧）+ 本篇（CPU 原型侧）+ Microban（低成本平台同构）+ bipedal-rl-sim2real（规则层）四层参考体系齐了。

## 七、指南分析

**DUCK 重训时的对照使用表**：

| 场景 | 查本笔记哪节 |
|------|--------------|
| 超参配置 | §1.4（对齐官方 rsl_rl 的完整参数表+两段 batch 规则） |
| 奖励项设计 | §1.8 五条规则 |
| 技能学不会 | §1.8 规则 4（servo-ladder）+ §1.9 规则 5（先查奖励可学习性） |
| 判断策略好坏 | §1.9 六条（确定性 ONNX+render+null 对照） |
| 训练链 --init-from | §1.9 规则 6（LOG_STD_MAX） |
| 多 env 内存爆 | §1.7（fork 共享模型 41GB→1.5GB） |
| 需要新 trick | §1.6（Behavior 数据类+奖励项目录模式） |

**禁止项**（不变量）：改 obs 布局/移除零填充槽/"修"joint_vel 滞后/手递 raw checkpoint/在本地 harness 出硬件策略。

## 八、拓展应用推荐

- **给 DUCK-Pi_5 docs/09**：奖励五规则+验证六纪律引用补入重训节（关联分析 #1/#3）
- **给 bipedal-rl-sim2real skill**：servo-ladder 案例与"改世界不改工资"原则补入
- **给本机 render 流程**：帧接触表（AI 可读字幕）模式可借鉴到 DUCK 可视化（docs/12）
- **延伸阅读**：microduck_rl 官方 AGENTS.md（上游完整 sim2real playbook）、jenga-stacker web viewer（几何直提模式来源）

---

→ 相关：[[2026-08-31-microduck_rl分析学习-Sim2Real实战规则.md]]（官方 GPU 栈精读，本篇是其 CPU 原型侧）
→ 相关：[[2026-09-01-Microban与2026双足RL前沿-低成本平台同构与重训校准.md]]（低成本平台同构）
→ 相关：[[2026-09-01-MuJoCo仿真到Three.js可视化全链路-千问工程还原.md]]（duck-viewer 的同构实现）
→ 相关：[[2026-09-02-MiniMind从零训练LLM全链路-3块钱64M模型与AgenticRL.md]]（同周"消费级硬件训练"叙事）
