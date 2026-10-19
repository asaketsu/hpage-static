# safetensors 与 ONNX 选型：权重仓库与冻结计算图的本质区别

> 来源: 微信公众号 · [原文](https://mp.weixin.qq.com/s/aTFJ2QqNhReMSu9WltE5-A)
> 场景: ComfyUI 的 10GB safetensors vs 云服务器 91MB ONNX——"这俩谁更好"是个坏问题

`#模型部署` `#ONNX` `#safetensors` `#推理优化` `#格式选型`

## 归纳总结

safetensors 是**权重仓库**（装"数"：JSON头记录 tensor 名/dtype/shape/偏移 + 裸数据，无算子无结构），ONNX 是**冻结计算图**（装"算式"：算子连接+shape 流转+权重固化为常量）。拿仓库跟算式比速度=问"冰箱和菜谱谁做饭快"。选型铁律：训练微调用 safetensors，无卡部署用 ONNX，本地大模型用 GGUF，Intel 用 OpenVINO，苹果用 CoreML，N 卡用 TensorRT，零运维调 API。性能收益排序（换引擎 2-3x < 量化 2x < 换小模型 5-10x）常被做反——花两周折腾格式转换不如换小一号模型。

## 内容整理：核心对比

| 维度 | safetensors | ONNX |
|---|---|---|
| 本质 | 权重存档（数据容器） | 计算图（结构+常量权重） |
| 结构信息 | 无——网络定义在 Python 代码里 | 有——算子/连接/shape 全在图里 |
| 执行依赖 | 需自己搭网络（load_state_dict） | ORT C++ 引擎直接跑 |
| 安全 | 纯数据可审计（堵死 pickle 任意代码执行） | 图可检查但生态复杂 |
| 生态锁定 | ComfyUI 全链（LoRA/ControlNet/kohya/采样器） | 部署域（CPU/跨平台/边缘） |
| 加载 | mmap 零拷贝 | 图解析+常量加载 |

## 为什么 ComfyUI 不能换 ONNX

不是快慢问题，是**生态重力**：LoRA 合并、ControlNet、kohya 微调脚本、采样器调度全部长在 PyTorch Module 结构上。换 ONNX = 扔掉微调+插件+社区节点。"变慢是自找的"。

## ONNX 快在哪（以及不快在哪）

- **快**：图优化——Conv+BatchNorm+ReLU 融合单算子、常量折叠、内存复用；核心是**少走 Python 调度层**而非算得快。纯 CPU 场景 1.5-3 倍常见
- **不快**：N 卡上拿 ORT CUDA EP 打 PyTorch cuDNN 本来就打不过——ORT 主场在 CPU 和无卡环境
- **弱项**：动态 shape/控制流（while 循环）/自定义算子一直是坑

## 部署账（ExoMind 实测）

2C2G 阿里云 ECS 跑 embedding 服务：torch 栈常驻内存 450MB → ONNX 91MB；torch wheel 800MB+ vs ORT CPU 包 <20MB；冷启动提速 52 倍；同权重同输入余弦相似度 1.000000。

## 收益排序铁律（踩坑才服）

1. **换模型（大换小/蒸馏）：5-10 倍**
2. **换推理引擎（torch→ORT）：2-3 倍**
3. **量化（fp32→int8/4bit）：约 2 倍**

多数人把顺序做反：花两周折腾格式转换，收益不如把模型换小一号。

## 七条路线表

| 路线 | 组合 | 适合谁 |
|---|---|---|
| 训练/微调 | safetensors + PyTorch | 要改结构、合 LoRA |
| 无卡部署 | ONNX + ORT | CPU 服务器、跨平台 |
| 本地大模型 | GGUF + llama.cpp | Ollama 底层，内存优先 |
| Intel 极致 | OpenVINO | Intel CPU/核显/NPU |
| 苹果 | CoreML | 唯一真吃 ANE 的路径 |
| N 卡 | TensorRT | 生产级 GPU 推理 |
| 零运维 | 直接调 API | 数据不出境就别想 |

## 💡 对我们的价值分析

### ✅ 已在做的（文章验证了我们路线正确）
- **DUCK 部署链正是此范式**：microduck 训练（pt/safetensors 域）→ ONNX 导出（opset13, IR≤9, 动态batch）→ pi5 真机推理——训练用仓库、部署用图
- **动态 batch 坑我们踩过并固化**：e23b_m12500.onnx 动态 batch(1,61) 导出验证 3 行——文章的 dynamic_axes 坑正是我们 E23b 导出时显式处理的
- **外部数据铁律同构**：ONNX 部署三件套坑（.onnx/.onnx.data 伴生文件+norm 常量）是文章没覆盖的实战补充

### 🔥 重点行动
1. **Jetson 路线对照**：我们在 Orin 上有 TensorRT 路线（jetson-tensorrt-deploy skill），文章七条路里"N 卡=TensorRT"印证——下一步 DUCK 若上 Jetson 推理，ONNX→TRT 引擎转换是正路
2. **收益排序应用到 DUCK**：当前训练线在"换引擎/量化"层打转（int8 量化探索），铁律提示**换小模型（蒸馏/架构缩小）才是 5-10x 空间**——与 rl-policy-architecture-selection skill 的结论互证
3. **冷启动 52 倍**对 pi5 上电到策略接管链路有直接参考价值（我们每次上电要加载 onnx+norm）

### ⚠️ 保持怀疑的
- 91MB vs 450MB 的对比含 torch 运行时本身——纯推理场景 torch 也可用 torch.compile/静态图缩小差距
- "余弦相似度 1.000000" 是 embedding 模型的宽容指标，控制类网络（RL 策略）对数值误差更敏感，转换后必须逐层对拍（我们的 md5+对拍 diff<1e-06 流程是必要的）

## 关联分析

本文格式选型框架与我们四条既有线交叉验证：①DUCK 训练-部署链（microduck pt→ONNX opset13→pi5）正是"训练仓库/部署计算图"双轨制的实践，且我们的动态 batch 导出+外部数据三件套坑是文章未覆盖的实战补充；②rl-policy-architecture-selection skill 结论（架构缩小优于调参）与文章收益排序铁律（换模型 5-10x > 引擎 2-3x > 量化 2x）完全同向——两条独立推理路径得出同一结论，可信度互证；③edge-llm-quantization 的 GGUF 路线对应文章"本地大模型"行；④jetson-tensorrt-deploy 对应"N 卡=TensorRT"行。关联笔记：手写GPU推理内核（底层视角）+ 走路用RL干活用Transformer（模型缩小=知识迁移）。

## 📊 趋势判断

格式战争正在收敛为"训练域格式 + 部署域格式"双轨制：HuggingFace 生态用 safetensors 统一训练侧，部署侧则按硬件碎片化（ONNX/COREML/OpenVINO/TRT/GGUF 各占一方）。真正的杠杆不在格式转换而在模型缩小——这条铁律与 2026 年端侧模型蒸馏潮（知识缺口决定论笔记的 VLA 统一架构）同向。.gguf 在本地 LLM 的胜利说明"内存优先"约束下连执行图都可以让步。

## 🔍 查询拓展

- ONNX opset 版本兼容矩阵与算子覆盖缺口（控制流 while 的替代方案）
- safetensors 的 mmap 零拷贝在大模型（>10GB）加载的实测增益
- torch.compile 与 ORT 图融合的本质差异（编译时机 vs 执行引擎）
- TRT 的 INT8 校准与 ORT 量化接口的精度对比
- GGUF 为什么能省内存：量化粒度与 attention 结构的适配

## 🛠️ 指南分析

- 转换最小路径：torch.onnx.export(opset 17+dynamic_axes) → onnxruntime CPU EP → 数值对拍
- 排障顺序：opset 版本 → dynamic_axes → 算子覆盖 → provider 配置
- 部署预算思维：先算内存/冷启动预算再选格式，不是先转格式再测

## 🔗 拓展应用推荐

- DUCK pi5 部署链加冷启动计时指标（对齐文章 52 倍参考基准）
- edge-llm-quantization skill 补充本文的收益排序铁律作选型前置判断
- 微调与部署的分界点写入 robotics 项目 README（什么时候必须回到 pt 域）

## 相关笔记

→ 相关：2026-10-13-手写GPU推理内核-从TiledGEMM到PagedKVCache白盒实录.md（TRT/cuBLAS 域的底层视角，本文是格式层视角）
→ 相关：2026-10-13-走路用RL干活用Transformer-机器人算法的知识缺口决定论.md（模型缩小=知识迁移，蒸馏是 5-10x 的正路）
