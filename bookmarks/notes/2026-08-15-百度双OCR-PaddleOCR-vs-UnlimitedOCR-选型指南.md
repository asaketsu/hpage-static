# 百度双 OCR：PaddleOCR vs Unlimited-OCR 选型与使用指南

> **来源**：掘金·知澈Datalab 对比评测 + GitHub 官方仓库（baidu/Unlimited-OCR、PaddlePaddle/PaddleOCR）+ 量子位/科技日报报道
> **原文链接**：https://juejin.cn/post/7659556749486227508 ｜ https://github.com/baidu/Unlimited-OCR
> **记录日期**：2026-08-15

**标签**：#OCR #PaddleOCR #UnlimitedOCR #文档解析 #RAG #部署

---

## 一、内容整理

### 1.1 一句话定位

- **PaddleOCR**：产业级 OCR **工具箱**（2020 年诞生，打磨 6 年，GitHub 73.3k★ 超 Tesseract 登顶全球第一）——检测、识别、版面分析、表格识别、公式识别全套流水线
- **Unlimited-OCR**：端到端长文档 **专用模型**（2026-06-22 发布，5 天破万★，现 23.8k★，GitHub+HuggingFace 四榜第一）——图像进、Markdown 出，一次前向转录 40+ 页

**关系：不是竞争，是百度 OCR 的两条腿——一条负责"广"，一条负责"深"。两个都装不冲突。**

### 1.2 核心对比表

| 维度 | PaddleOCR | Unlimited-OCR |
|------|-----------|---------------|
| 技术路线 | 两阶段流水线（检测→识别） | 端到端（图像→文本一步到位） |
| 模型规模 | 轻量级 1.5MB 起 | 3B 总参数，推理激活 570M |
| 核心创新 | 模块化设计、PP-OCRv6 系列 | **R-SWA 注意力**（恒定 KV Cache） |
| 长文档 | 逐页拼接，KV Cache 膨胀 | **单次解析 40+ 页**，KV Cache 恒定 |
| 语言 | 100+ 种 | 中文及主流语言 |
| OmniDocBench | **96.3%**（VL-1.6） | 93.92%（v1.6） |
| 部署 | 本地/云端/边缘/浏览器/国产硬件 | 本地/云端 |
| 生态 | Dify、RAGFlow、Cherry Studio、HF、Milvus（OCEAN 联盟） | 建设中（vLLM/SGLang/ms-swift/百度云已支持） |
| License | Apache 2.0 | **MIT** |

### 1.3 PaddleOCR 技术要点

- 双引擎：**PP-OCRv6**（轻量流水线，v6 比 v5 检测 +4.6%、识别 +5.1%，CPU 端到端提速 5.2×）+ **PaddleOCR-VL**（0.9B 视觉语言模型，"由粗到细"架构：VRFM 模块先定位有效区域，视觉 Token 只有竞品 1/3~1/2，OmniDocBench V1.5 92.62 分全球 SOTA，VL-1.6 已到 96.3%）
- **PP-StructureV3**：PDF/图 → Markdown/JSON，带细粒度坐标（表格单元格坐标、文本坐标）
- 数据工程洞察（量子位报道）：训练存在"难度甜点区"，中等难度数据效率最高；小模型对标签噪声天然鲁棒——**小模型靠精细化数据工程可媲美大模型**
- 服务化：官网免费每日 2 万页解析；OCEAN 生态联盟首批成员含 HuggingFace/Dify/RAGFlow/Milvus

### 1.4 Unlimited-OCR 技术要点（R-SWA 机制）

- 痛点：传统端到端 OCR 每生成 1 个 token，KV Cache 膨胀——越生成越慢、显存越占越多
- R-SWA（Reference Sliding Window Attention）：灵感来自人类抄长文——**始终关注原文，只保留最近生成的"工作记忆"**，不无限累积历史
- 效果：KV Cache 从线性增长→**常数**；32K 最大长度下单次前向传播转录数十页文档
- 出身：明确致谢站在 DeepSeek-OCR/DeepSeek-OCR-2 肩膀上（"push DeepSeek-OCR one step further"）；对比 DeepSeek-OCR 2 在 9 个类目中 7 个（文本和阅读顺序指标）领先
- 训练支持：ms-swift（2026-07-21 起）

## 二、查询拓展

### 2.1 OmniDocBench
文档解析权威评测基准（文本/表格/公式/阅读顺序/版面多维），V1.5/V1.6 版本 leaderboard 是当前 OCR 模型排位主战场。PaddleOCR-VL 系列、MinerU、DeepSeek-OCR、dots.ocr 等均在榜。

### 2.2 KV Cache 与长文本生成
Transformer 自回归生成的固有瓶颈：注意力需缓存全部历史 key/value，长输出显存线性涨。业内解法谱系：MQA/GQA（压缩头数）→ Sliding Window Attention（Mistral）→ YaRN/NSP（位置外推）→ 本文 R-SWA（抄写场景特化：原文常驻+滑动窗口工作记忆）。

### 2.3 端到端 OCR 谱系（2025-2026 新浪潮）
2025-10 起集中爆发：百度 PaddleOCR-VL、DeepSeek-OCR、olmOCR-2（Allen AI）、Nanonets-OCR2-3B、dots.ocr.base 几乎同期发布。共同思路：VLM 架构直接"看图写文"，跳过检测-识别两阶段，天然保留阅读顺序和结构（输出 Markdown）。代价是算力远超流水线小模型——PaddleOCR-VL 用 VRFM 粗到细缓解，Unlimited-OCR 用 R-SWA 解决长输出。

### 2.4 与 Tesseract 的代际差
Tesseract（1985 惠普→2005 Google，73.2k★）是传统视觉特征路线的最后堡垒；PaddleOCR 登顶标志着深度学习+大模型路线完成代际替换（2026-03-31，中国开源首次在 OCR 领域超越谷歌标杆）。

## 三、归纳总结

### 3.1 选型决策树

```
拿到一个 OCR 需求
│
├─ 文档类型？
│   ├─ 卡片/票据/路牌/自然场景/多语言 → PaddleOCR（PP-OCRv6）
│   ├─ 单页复杂文档（表格/公式/图表混排）→ PaddleOCR（PP-StructureV3 或 VL）
│   └─ 超长文档（财报/合同/论文/书籍 ≥40页）
│       └─ 要上下文连贯、一次成型 → Unlimited-OCR
│       └─ 要坐标/JSON 结构化 → PaddleOCR 逐页 + 拼接
│
├─ 部署约束？
│   ├─ 无 GPU / 边缘 / 浏览器 / 手机 → PaddleOCR（1.5MB 起）
│   ├─ 单卡服务器 → 两者皆可
│   └─ 高并发生产 → PaddleOCR（生态成熟）或 Unlimited-OCR vLLM/SGLang
│
└─ 集成需求？
    ├─ RAG/Agent 管线（Dify/RAGFlow/Milvus）→ PaddleOCR（现成插件）
    └─ 长文档一次性转 Markdown → Unlimited-OCR
```

### 3.2 五要素实操区

#### ✅ 功能清单

- [ ] PaddleOCR：通用文本检测+识别（PP-OCRv6，100+ 语言）
- [ ] PaddleOCR：版面分析+表格识别+公式识别（PP-StructureV3）
- [ ] PaddleOCR：PDF→Markdown/JSON（带单元格级坐标）
- [ ] PaddleOCR：VLM 级文档理解（PaddleOCR-VL 0.9B，SOTA 96.3%）
- [ ] PaddleOCR：训练-微调-量化-部署全工具链（边缘/浏览器/国产硬件）
- [ ] Unlimited-OCR：单图端到端解析（gundam/base 两种配置）
- [ ] Unlimited-OCR：多页/PDF 一次性解析（40+ 页，R-SWA 恒定显存）
- [ ] Unlimited-OCR：vLLM/SGLang 高性能推理 + ms-swift 训练

#### 🎯 使用性评估

- **PaddleOCR**：上手最快（`pip install paddleocr` 三行代码出结果）；CPU 可跑；文档中文完善；缺点是 PaddlePaddle 框架依赖较重、GPU 版安装偶有 CUDA 版本匹配坑
- **Unlimited-OCR**：需 GPU（3B 模型 bfloat16 推理，建议 ≥16GB 显存；Jetson 8GB 统一内存理论上可跑但速度受限）；依赖新（torch 2.10 + transformers 4.57 + python 3.12）；胜在输出即 Markdown、长文档零拼接
- **精度**：单页综合 PaddleOCR-VL 更高（96.3 vs 93.9）；长文档连贯性 Unlimited-OCR 独有优势
- **License**：Unlimited-OCR MIT 比 PaddleOCR Apache 2.0 更宽松，商用闭源友好

#### 💡 指导性意见

1. **默认装 PaddleOCR**——90% 场景的答案：票据、截图、扫描件、RAG 入库
2. **长文档才上 Unlimited-OCR**——"逐页识别+人工拼接"痛到一定程度才值得装 3B 模型
3. **两个都装不冲突**——日常 PaddleOCR，超长文档 Unlimited-OCR，互补
4. **本机（Jetson Orin 8GB）落地建议**：PaddleOCR 用 PP-OCRv6 轻量版（CPU 即可）；Unlimited-OCR 需评估统一内存预算（LuxTTS+F5-TTS 已占 ~2.1GB GPU），或走百度云 API 免部署
5. **别忽略官网 API**：PaddleOCR 官网免费每日 2 万页——个人用量直接白嫖 API 比本地部署省心

#### 📌 案例

1. **掘金评测结论**（同场景实测）：日常 OCR + RAG 集成选 PaddleOCR；几十页财报/上百页合同选 Unlimited-OCR
2. **PaddleOCR-VL 论文案例**：OmniDocBench V1.5 以 92.62 登顶，视觉 Token 仅竞品 1/3~1/2——高分辨率文档不再算力爆炸
3. **Unlimited-OCR 官方 demo**：HuggingFace Spaces（baidu/Unlimited-OCR）在线试用，无需本地部署先验证效果

#### 🔧 使用方法借鉴（可直接抄）

**PaddleOCR 快速上手（本机 CPU 可跑）**：
```bash
pip install paddlepaddle paddleocr  # CPU 版；GPU 版装 paddlepaddle-gpu
```
```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_textline_orientation=True, lang="ch")
result = ocr.predict("your_image.jpg")  # 检测+识别一步
for res in result:
    res.print()          # 文本
    res.save_to_img()    # 可视化
    res.save_to_json()   # 结构化
```

**Unlimited-OCR 单图/多页/PDF（GPU）**：
```python
import torch
from transformers import AutoModel, AutoTokenizer

model_name = 'baidu/Unlimited-OCR'
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True,
           use_safetensors=True, torch_dtype=torch.bfloat16).eval().cuda()

# 单图（gundam 模式：裁剪增强）
model.infer(tokenizer, prompt='document parsing.', image_file='your_image.jpg',
    output_path='out/', base_size=1024, image_size=640, crop_mode=True,
    max_length=32768, no_repeat_ngram_size=35, ngram_window=128)

# 多页 PDF（base 模式，PyMuPDF 转 300dpi 图）
import fitz, tempfile, os
def pdf_to_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(dpi/72, dpi/72)
    paths = []
    for i, page in enumerate(doc):
        p = os.path.join(tempfile.mkdtemp(prefix='pdf_ocr_'), f'page_{i+1:04d}.png')
        page.get_pixmap(matrix=mat).save(p)
        paths.append(p)
    return paths

model.infer_multi(tokenizer, prompt='Multi page parsing.',
    image_files=pdf_to_images('your_doc.pdf', dpi=300),
    output_path='out/', image_size=1024, max_length=32768,
    no_repeat_ngram_size=35, ngram_window=1024)
```

**Unlimited-OCR 生产部署（vLLM 一条命令）**：
```bash
docker pull vllm/vllm-openai:unlimited-ocr          # CUDA 13.0
docker pull vllm/vllm-openai:unlimited-ocr-cu129    # Hopper
# OpenAI 兼容 API，配方：https://recipes.vllm.ai/baidu/Unlimited-OCR
```

**关键参数备忘**：`no_repeat_ngram_size=35` + `ngram_window`（单图 128/多页 1024）是防重复生成的核心——借鉴自 DeepSeek-OCR 的 no-repeat ngram 技巧，别乱调。

## 四、趋势判断

### 趋势1：OCR 正从"工具"变成"大模型的信息入口"
依据：吴恩达 2026 年新课程聚焦 Agent Doc Extraction；量子位判断"谁拥有更强 OCR，谁掌握现实世界信息入口"；PaddleOCR OCEAN 联盟拉上 HF/Dify/RAGFlow/Milvus。
判断：OCR 与 RAG/Agent 的集成深度将成为选型第一权重，纯 standalone OCR 工具价值萎缩。

### 趋势2：端到端与流水线将长期共存分层
依据：PaddleOCR 自己双线并行（PP-OCRv6 流水线 + VL 端到端）；Unlimited-OCR 致谢 DeepSeek-OCR——端到端路线迭代速度极快但单页精度仍落后流水线 2.4 个点。
判断：未来 2 年"流水线保精度下限、端到端攻长文档上限"的混合架构是主流，PaddleOCR 工具箱定位正好卡住这个生态位。

### 趋势3：注意力机制创新是长序列生成的下一个爆发点
依据：R-SWA 用"人类抄写"隐喻解决 KV Cache 膨胀，与 Mistral SWA、MInference 等同谱系；OCR 是长输出生成的完美试验场（输出长度可预测、原文常驻）。
判断：R-SWA 式"场景特化注意力"会外溢到代码生成、会议转录等其他长输出任务。

## 五、关联分析

### 5.1 与本机 OCR 工具链的关联
现有 `ocr-and-documents` skill（pymupdf/marker-pdf 路线）处理文本层 PDF 已够用；图片型 PDF 和扫描件是缺口——PaddleOCR PP-OCRv6（CPU 可跑）正好补位，`read_file` 的 PDF 转换覆盖率可借此提升。`vision-image-recognition` skill 的降级链也可加 PaddleOCR 一层（本地 OCR 优先于 API）。

### 5.2 与 RAG/知识库体系的关联
`rag-index-rebuild`、`enterprise-rag-knowledge-engine` 的入库前端一直缺高精度文档解析器：PaddleOCR PP-StructureV3（坐标级 JSON）适合需要引用定位的知识库；Unlimited-OCR（整本 Markdown）适合全文人库。两者结合 = "精读用 Paddle、通读用 Unlimited"。

### 5.3 与 PhysicsForAI 笔记的呼应
PaddleOCR 的"数据工程"发现（难度甜点区、小模型媲美大模型）与 PhysicsForAI 判据一"分析中不涉及数据分布的地方物理帮得上"异曲同工——**数据策略的上限尚未挖尽**是两个领域共同的开放方向。

### 5.4 与 PTX/GEMM 笔记的硬件呼应
Unlimited-OCR 3B 模型 bfloat16 在 Jetson 8GB 统一内存的部署评估，直接复用 PTX 笔记的结论：带宽紧的卡上，模型选择的首要考量是工作集大小而非峰值算力——R-SWA 恒定 KV Cache 恰好是最友好的特性。

## 六、金句摘录

> "PaddleOCR 是'产业级工具箱'，Unlimited-OCR 是'长文档专用利器'——它们不是竞争关系，而是百度在 OCR 领域的两条腿，一条负责'广'，一条负责'深'。"

> "谁拥有更强的 OCR 能力，谁就掌握了现实世界的信息入口。"（量子位）

> "数据本身，可能会慢慢变成一条更独立、也更重要的能力曲线。"（PaddleOCR 团队）

## 七、行动启示

| 启示 | 行动 |
|------|------|
| 本机缺图片型 PDF 解析能力 | 在独立 venv 装 PaddleOCR CPU 版（`pip install paddlepaddle paddleocr`），补进 ocr-and-documents skill 降级链 |
| 长文档解析可白嫖 | PaddleOCR 官网 API 每日免费 2 万页，注册 key 备用；Unlimited-OCR 先用 HF Spaces 在线验证效果再决定是否本地部署 |
| Jetson 部署评估 | Unlimited-OCR 本地部署前排 GPU 内存预算（现有 2.1GB 被 TTS 占用），或走 vLLM 云端配方 |
| 笔记复用 | 选型决策树（§3.1）+ 代码模板（§3.2）可直接抄给任何 OCR 需求 |

## 相关笔记
- [局域网A100算力池×双OCR-批量文档与微调业务流程](2026-08-15-局域网A100算力池×双OCR-批量文档与微调业务流程.md)
- [HuggingFace-Trending全景-2026年7月AI模型生态](2026-07-24-HuggingFace-Trending全景-2026年7月AI模型生态.md)
- [liteparse](2026-05-29-liteparse.md)
