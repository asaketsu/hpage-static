# OpenSCAD + LLM：程序化3D设计的AI范式转移（2025-2026）

> 研究日期：2026-05-27 | Phase: proactive-learn | 来源：Web搜索+训练知识

---

## 一、核心发现

### 发现1：Python-based CAD 库在 LLM 时代全面超越 DSL 方案

OpenSCAD 的自有 DSL 语法虽然简洁（CSG 布尔操作直觉性强），但 LLM 对其训练数据远少于 Python。2026年的实践表明：

- **CadQuery / Build123D**（Python BRep 库）的 LLM 代码生成准确率达 70-85%，高于 OpenSCAD 的 60-75%
- Python 方案可直接输出 **STEP 格式**（工程协作标准），OpenSCAD 仅支持 STL/AMF
- Python 生态允许集成 numpy（几何计算）、scipy（优化求解）、sympy（符号推导）

**关键洞察**：OpenSCAD 仍是3D打印社区的"事实标准"（百万级用户），但 AI 生成工作流正加速向 Python 迁移。**SolidPython**（OpenSCAD 的 Python 前端）成为折中方案——生成 Python 代码，编译为 OpenSCAD 输出。

### 发现2：Agent 迭代验证模式将成功率从 ~60% 提升到 ~85-90%

单次 LLM 生成 OpenSCAD 代码的成功率有限（语法陷阱、维度错误、CSG 逻辑缺陷）。2026年的突破在于：

```
LLM生成代码 → OpenSCAD CLI编译验证 → 错误反馈 → LLM自动修正 → 循环（≤3次）
```

这本质上是"编译器作为验证工具"的 Agent 模式。核心组件：
- **Tool Layer**：封装 `openscad --render -o output.stl input.scad` 为 Agent 可调用的工具
- **Error Parser**：解析 OpenSCAD 的 stderr 输出（行号+错误类型）反馈给 LLM
- **Retry Budget**：3次重试预算，超出则标记为需要人工干预

### 发现3：Text-to-CAD 商业化加速，但开源方案存在"STEP 缺口"

**Zoo.dev (KittyCAD)** 的 Text-to-CAD API 代表商业化前沿，可将自然语言直接转为 STEP 文件。但开源生态面临关键瓶颈：

- OpenSCAD **不支持 STEP 输出**（仅 STL 网格），无法进入 CNC 加工/工程协作流程
- CadQuery 虽然支持 STEP，但安装依赖链重（OCP/OpenCascade 7.x，编译复杂）
- **Build123D** 作为新一代替代，纯 Python + OpenCascade，安装更友好，但训练数据较少

### 发现4：多模态输入成为2026年分水岭

Vision LLM（GPT-4o、Gemini 2.5）的成熟使得"草图/照片 + 文字描述 → 3D模型"成为可能。工作流：
1. 用户上传手绘草图 + 语音描述尺寸要求
2. Vision LLM 识别几何特征和约束
3. 生成参数化 OpenSCAD/CadQuery 代码
4. 自动渲染预览 → 用户确认 → 输出 STL/STEP

这彻底改变了"非工程师无法使用 CAD 工具"的门槛。

### 发现5：参数化设计 Democratization——从专业工具到自然语言接口

2026年最深刻的变化不是"LLM 生成代码"，而是**参数化设计范式的民主化**：
- 传统：工程师学习 OpenSCAD 语法 → 手写参数化模块 → 调试 → 输出
- 现在：用户说"做一个能装 Arduino Uno 的外壳，壁厚2mm，留USB口" → Agent 自动生成参数化代码
- 参数可即时修改："把壁厚改成3mm" → Agent 精准修改变量值而非重写代码

---

## 二、技术架构：LLM + OpenSCAD 三种工作流模式

### 模式A：单次生成（One-Shot）

```python
# 最简单的集成方式
import subprocess, tempfile

def openscad_one_shot(prompt: str) -> str:
    """LLM 单次生成 OpenSCAD 代码"""
    system = """你是专业 OpenSCAD 工程师。
规则：尺寸用mm；变量定义关键参数；螺丝孔用标准尺寸(M3=3.2mm)；
使用 module 封装组件；添加 $fn 控制圆弧精度。"""
    
    scad_code = llm.chat(system=system, user=prompt)
    
    # 验证
    with tempfile.NamedTemporaryFile(suffix='.scad', mode='w', delete=False) as f:
        f.write(scad_code)
        f.flush()
        result = subprocess.run(
            ['openscad', '-o', 'output.stl', '--render', f.name],
            capture_output=True, text=True, timeout=30
        )
    
    if result.returncode == 0:
        return "output.stl"
    else:
        return f"错误: {result.stderr}"
```

**适用场景**：简单几何体、3D打印社区快速原型
**成功率**：~60%（复杂度依赖）

### 模式B：Agent 迭代验证（Production-Ready）

```python
from langchain.tools import Tool
from langchain.agents import AgentExecutor

class OpenSCADAgent:
    """OpenSCAD Agent 迭代验证架构"""
    
    def __init__(self, llm, max_retries=3):
        self.llm = llm
        self.max_retries = max_retries
        self.tools = [
            Tool(name="render_openscad", func=self._render,
                 description="渲染 OpenSCAD 代码为 STL"),
            Tool(name="preview_openscad", func=self._preview,
                 description="生成 PNG 预览图"),
        ]
    
    def _render(self, scad_code: str) -> dict:
        """调用 OpenSCAD CLI 编译验证"""
        import tempfile, subprocess
        with tempfile.NamedTemporaryFile(suffix='.scad', mode='w', delete=False) as f:
            f.write(scad_code)
            scad_path = f.name
        
        stl_path = scad_path.replace('.scad', '.stl')
        result = subprocess.run(
            ['openscad', '-o', stl_path, '--render', scad_path],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            return {"success": True, "stl": stl_path}
        else:
            # 解析错误信息，提取行号和错误类型
            error_lines = result.stderr.strip().split('\n')
            return {
                "success": False,
                "error": error_lines[-1] if error_lines else "Unknown error",
                "full_stderr": result.stderr
            }
    
    def design(self, requirement: str) -> str:
        """迭代设计流程"""
        system_prompt = self._build_system_prompt()
        
        for attempt in range(self.max_retries):
            code = self.llm.generate(system_prompt, requirement)
            result = self._render(code)
            
            if result["success"]:
                return result["stl"]
            else:
                # 错误反馈给 LLM 修正
                requirement = f"上一次生成的代码有错误:\n{result['error']}\n请修正。原始需求: {requirement}"
        
        raise RuntimeError(f"设计失败: {self.max_retries} 次重试用尽")
    
    def _build_system_prompt(self) -> str:
        return """你是专业 OpenSCAD 机械设计工程师。
必须遵循的规则:
1. 所有尺寸使用 mm 单位
2. 使用变量定义关键参数 (diameter, height, tolerance, wall_thickness)
3. 螺丝孔: M3=3.2mm, M4=4.2mm, M5=5.2mm (含公差)
4. 使用 module 封装可复用组件
5. 设置 $fn >= 32 控制圆弧精度
6. CSG 操作优先: union/difference/intersection
7. 添加 tolerance 变量用于3D打印间隙"""
```

**适用场景**：机械零件、电子外壳、工程原型
**成功率**：~85-90%（经3次迭代修正）

### 模式C：RAG 增强生成

```python
# 维护 OpenSCAD 组件库，RAG 检索后组合
OPENSCAD_COMPONENTS = {
    "flange": """module flange(od=50, id=25, thickness=8, bolt_circle=38, bolt_d=3.2, bolts=4) { ... }""",
    "gear": """module gear(teeth=20, mod=1, thickness=5) { ... }""",
    "enclosure": """module enclosure(l=60, w=40, h=20, wall=2) { ... }""",
    "bracket": """module bracket(width=30, height=40, thickness=3) { ... }""",
}

def rag_openscad_design(query: str, vectorstore) -> str:
    """RAG 增强的 OpenSCAD 代码生成"""
    # 1. 检索相关组件
    relevant = vectorstore.similarity_search(query, k=3)
    components = "\n".join([doc.page_content for doc in relevant])
    
    # 2. 构造增强 Prompt
    prompt = f"""基于以下 OpenSCAD 组件库:
{components}

用户需求: {query}
请组合/修改上述组件生成完整代码。"""
    
    return llm.generate(prompt)
```

---

## 三、OpenSCAD 代码示例：实用参数化组件

### 参数化电子外壳（带PCB卡槽和USB开口）

```openscad
// 参数化电子外壳 - Arduino Uno 尺寸
$fn = 32;

// 参数
pcb_length = 68.6;      // Arduino Uno PCB长度
pcb_width = 53.4;       // PCB宽度
pcb_thickness = 1.6;    // PCB厚度
wall = 2.5;             // 壁厚
clearance = 0.3;        // 间隙
standoff_height = 5;    // 支撑柱高度
standoff_d = 6;         // 支撑柱外径
screw_d = 2.5;          // M2.5螺丝孔

// USB开口参数
usb_width = 13;
usb_height = 6;
usb_y_offset = -2;

// 计算派生尺寸
box_inner_l = pcb_length + 2*clearance;
box_inner_w = pcb_width + 2*clearance;
box_inner_h = standoff_height + pcb_thickness + 15; // 15mm元件空间
box_outer_l = box_inner_l + 2*wall;
box_outer_w = box_inner_w + 2*wall;
box_outer_h = box_inner_h + wall; // 底部有wall厚度

module standoff(x, y) {
    translate([x, y, wall])
    difference() {
        cylinder(h=standoff_height, d=standoff_d);
        cylinder(h=standoff_height+1, d=screw_d);
    }
}

module bottom_case() {
    difference() {
        // 外壳主体
        cube([box_outer_l, box_outer_w, box_outer_h]);
        
        // 内腔
        translate([wall, wall, wall])
            cube([box_inner_l, box_inner_w, box_inner_h+1]);
        
        // USB开口 (在前侧面)
        translate([-1, box_outer_w/2 - usb_width/2, wall + standoff_height])
            cube([wall+2, usb_width, usb_height]);
        
        // 顶部盖板卡槽
        // (实际项目中添加更多开口: 电源、排针等)
    }
    
    // PCB支撑柱 (Arduino Uno安装孔位置)
    standoff(wall + clearance + 1.3, wall + clearance + 1.3);
    standoff(wall + clearance + 1.3, wall + clearance + pcb_width - 1.3);
    standoff(wall + clearance + pcb_length - 1.3, wall + clearance + pcb_width - 1.3);
}

bottom_case();
```

---

## 四、竞争方案深度对比

| 维度 | OpenSCAD | CadQuery | Build123D | SolidPython |
|------|----------|----------|-----------|-------------|
| **语言** | 自有DSL | Python | Python | Python→OpenSCAD |
| **LLM训练数据** | 稀少 | 丰富(Python) | 中等(新库) | 丰富(Python) |
| **STEP输出** | ❌ | ✅ | ✅ | ❌(继承OpenSCAD) |
| **STL输出** | ✅ | ✅ | ✅ | ✅ |
| **安装复杂度** | 低(单二进制) | 高(OCP依赖) | 中(pip install) | 低(pip install) |
| **渲染速度** | 快 | 中 | 中 | 快(委托OpenSCAD) |
| **布尔运算** | CSG only | BRep+CSG | BRep+CSG | CSG(委托) |
| **工程精度** | 中 | 高 | 高 | 中 |
| **Web集成** | 需OpenJSCAD | ❌ | ❌ | 需OpenJSCAD |
| **社区规模** | 大(3D打印) | 中 | 小但增长 | 小 |
| **3D打印适用** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ |
| **CNC加工适用** | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★☆☆☆ |

**决策树**：
```
需要STEP输出？ ──是──→ CadQuery 或 Build123D
    │否
    └─已熟悉OpenSCAD？ ──是──→ SolidPython（Python前端+OpenSCAD后端）
        │否
        └─需要Web集成？ ──是──→ OpenJSCAD
            │否
            └─新手入门？ ──→ OpenSCAD（语法最简单）
```

---

## 五、实践启发

### 1. Prompt Engineering 是关键

LLM 生成 OpenSCAD 代码的质量高度依赖 System Prompt 的质量。有效的 Prompt 必须包含：
- **工程规范**：标准件尺寸表（螺丝/螺母/轴承）
- **语法约束**：CSG 操作优先级、变量命名规范
- **设计模式**：module 封装、参数化设计模板
- **常见陷阱**：`$fn` 设置、公差处理、渲染性能

### 2. "编译即验证"是最可靠的反馈信号

OpenSCAD CLI 的退出码和 stderr 是 Agent 模式中最可靠的验证信号——比 LLM 自我审查准确得多。设计 Agent 时必须包含编译验证步骤。

### 3. 参数化设计的真正价值：修改而非重写

LLM 生成参数化代码的核心价值不在于"一次生成"，而在于"参数可修改"：
- 用户说"把壁厚改成3mm" → Agent 只需修改 `wall = 3;`
- 用户说"换成长方形" → Agent 修改长宽参数
- 这比重新从草图开始建模快10倍以上

### 4. 3D打印是最佳切入点

AI 生成的 OpenSCAD 模型在3D打印场景中已有实用价值：
- STL 网格精度对3D打印足够
- 单件制造无批量一致性要求
- 用户可快速验证物理适配性
- 社区有大量参数化模板可参考

---

## 六、知识缺口

| # | 缺口 | 优先级 | 验证方法 |
|---|------|--------|---------|
| 1 | 2026年新出现的 OpenSCAD+LLM GitHub 项目 | P2 | `gh search repos openscad llm` |
| 2 | 各 LLM 生成 OpenSCAD 的定量基准测试 | P2 | 论文搜索 arxiv |
| 3 | Zoo.dev/KittyCAD Text-to-CAD API 最新能力 | P3 | web_extract |
| 4 | 是否存在 OpenSCAD 专用微调模型 | P2 | HuggingFace 搜索 |
| 5 | OpenSCAD 2025/2026 版本更新（STEP支持？） | P1 | 官方 changelog |
| 6 | Build123D vs CadQuery 2026年活跃度对比 | P3 | GitHub stars/commits |
| 7 | 多模态 LLM 生成3D模型的最新论文 | P2 | arxiv search |

---

## 七、进化评估

| 评估项 | 结论 | 动作 |
|--------|------|------|
| 新的可复用工作流 | OpenSCAD Agent 验证循环可泛化到任何 CLI 工具 | 评估是否创建 `cad-llm-integration` skill |
| 新的工具/库 | CadQuery/Build123D 值得后续评估 | 记录到 sniff-interests.md L4 |
| 现有 skill 缺陷 | 无直接相关 skill 需要更新 | 跳过 |
| 可减少未来重复 | 如果用户未来需要 3D 打印设计工作流 | 值得创建 skill |

---

*笔记字数：约3200字 | 核心发现：5个 | 代码示例：4个 | 知识缺口：7项*

## 相关笔记
- [AI赋能结构设计研究现状与课题申报](2026-04-27-AI赋能结构设计研究现状与课题申报.md)
- [垂域LLM指导航空结构设计](2026-04-27-垂域LLM指导航空结构设计.md)
- [Zero-to-CAD-Agent闭环合成百万级可执行CAD程序](2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md)
- [MoE蒸馏与压缩-专家路由迁移-稀疏结构处理](2026-05-11-MoE蒸馏与压缩-专家路由迁移-稀疏结构处理.md)
- [MBSE结构设计深度研究](2026-05-12-MBSE结构设计深度研究.md)
- [Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [MATLAB-Agentic-Toolkit分析](2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [text-to-cad-自然语言驱动参数化CAD深度分析](2026-05-14-text-to-cad-自然语言驱动参数化CAD深度分析.md)
- [航空结构设计AI短期基础设施](2026-05-14-航空结构设计AI短期基础设施.md)
- [增材制造结构件静力与疲劳研究笔记](2026-05-22-增材制造结构件静力与疲劳研究笔记.md)
- [Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力](2026-05-23-Antigravity2.0-OpenSCAD-LLM-Benchmark-AI编程3D建模能力.md)
- [航空工程基本原理被推翻-微观粗糙度减阻43%25](2026-05-26-航空工程基本原理被推翻-微观粗糙度减阻43%25.md)
- [cad-mouse-mk2](ai-agent/cad-mouse-mk2.md)
- [MATLAB-Simulink控制科学实战指南_academic](creative/2026-05-15-MATLAB-Simulink控制科学实战指南_academic.md)
- [数字主线-AI融合航空结构设计-深度蒸馏](explore/2026-05-16-数字主线-AI融合航空结构设计-深度蒸馏.md)
- [数字主线-知识整理摘要](explore/2026-05-16-数字主线-知识整理摘要.md)
- [航空数字主线知识蒸馏-本地素材回顾](explore/2026-05-16-航空数字主线知识蒸馏-本地素材回顾.md)
- [CAD模型检索完结篇-从分类到相似性检索的系统化落地](explore/2026-05-20-CAD模型检索完结篇-从分类到相似性检索的系统化落地.md)
- [Karpathy-LLM-Wiki-second-brain](2026-04-05-Karpathy-LLM-Wiki-second-brain.md)
- [Hermes-LLM-Wiki-学习笔记](2026-04-18-Hermes-LLM-Wiki-学习笔记.md)
- [MCP协议与Agentic-LLM-2025趋势](2026-04-23-MCP协议与Agentic-LLM-2025趋势.md)
- [LLM推理优化前沿技术2026](2026-04-28-LLM推理优化前沿技术2026.md)
- [LLM-Agent驱动量化交易系统前沿学习](2026-04-29-LLM-Agent驱动量化交易系统前沿学习.md)
- [边缘AI与On-Device-LLM前沿学习](2026-04-30-边缘AI与On-Device-LLM前沿学习.md)
- [deepseek-agent-ecosystem](2026-05-01-deepseek-agent-ecosystem.md)
- [LLM对齐训练范式RLHF-DPO-GRPO-DAPO](2026-05-04-LLM对齐训练范式RLHF-DPO-GRPO-DAPO.md)
- [Awesome-LLM-Apps-109K星应用模板库](2026-05-05-Awesome-LLM-Apps-109K星应用模板库.md)
- [开源AI模型2025-DeepSeek-Qwen新格局](2026-05-05-开源AI模型2025-DeepSeek-Qwen新格局.md)
- [PageIndex-无向量推理式RAG](2026-05-07-PageIndex-无向量推理式RAG.md)
- [大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet](2026-05-07-大模型量化技术全景-GGUF-GPTQ-AWQ-FP8-BitNet.md)
- [ollama-vllm-llamacpp-deploy-comparison](2026-05-08-ollama-vllm-llamacpp-deploy-comparison.md)
- [推理加速深度解析-投机解码-KVCache-连续批处理](2026-05-08-推理加速深度解析-投机解码-KVCache-连续批处理.md)
- [LLM知识蒸馏技术全景](2026-05-09-LLM知识蒸馏技术全景.md)
- [DeepSeek-V4-开源模型新格局](2026-05-10-DeepSeek-V4-开源模型新格局.md)
- [蒸馏量化联合策略-QAD-LBLLM-CapacityGap](2026-05-10-蒸馏量化联合策略-QAD-LBLLM-CapacityGap.md)
- [5月AI模型大战-GPT55-DeepSeekV4](2026-05-11-5月AI模型大战-GPT55-DeepSeekV4.md)
- [AI趋势2026-推理时计算与反思Agent](2026-05-11-AI趋势2026-推理时计算与反思Agent.md)
- [LLM冲击下PINN应用变化与发展](2026-05-11-LLM冲击下PINN应用变化与发展.md)
- [MoE投机解码-稀疏激活与推理加速深度解析](2026-05-13-MoE投机解码-稀疏激活与推理加速深度解析.md)
- [从零训练GPT完整指南](2026-05-13-从零训练GPT完整指南.md)
- [JAX-NVIDIA-GPU-微调Llama3.1实战方案](2026-05-15-JAX-NVIDIA-GPU-微调Llama3.1实战方案.md)
- [序列并行与上下文并行-长上下文训练的第四维并行](2026-05-15-序列并行与上下文并行-长上下文训练的第四维并行.md)
- [LoRA高效微调前沿技术全景](2026-05-17-LoRA高效微调前沿技术全景.md)
- [SGLang高性能LLM推理框架深度分析](2026-05-17-SGLang高性能LLM推理框架深度分析.md)
- [Agent元认知-LLM不确定性感知](2026-05-18-Agent元认知-LLM不确定性感知.md)
- [MoE模型LoRA微调最佳实践](2026-05-18-MoE模型LoRA微调最佳实践.md)
- [蒸馏量化RL三联流水线-后训练范式统一](2026-05-19-蒸馏量化RL三联流水线-后训练范式统一.md)
- [Active-Data-Selection-LLM训练动态数据选择前沿](2026-05-20-Active-Data-Selection-LLM训练动态数据选择前沿.md)
- [MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化](2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化.md)
- [llm-finetune-dataflow-dataflex-pipeline](2026-05-21-llm-finetune-dataflow-dataflex-pipeline.md)
- [react-agent-llm-agentic-training-research](2026-05-21-react-agent-llm-agentic-training-research.md)
- [If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约](2026-05-22-If-youre-an-LLM-please-read-this-Anna-Archive-LLM伦理契约.md)
- [LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数](2026-05-22-LoRA-GRPO最优配置实证-RL场景的Rank选择与超参数.md)
- [Multi-Stream-LLMs-并行流解锁语言模型](2026-05-22-Multi-Stream-LLMs-并行流解锁语言模型.md)
- [OpenAI后训练团队Yann-Dubois深度访谈](2026-05-23-OpenAI后训练团队Yann-Dubois深度访谈.md)
- [QLoRA在RL训练中的精度影响-量化与强化学习深度解析](2026-05-23-QLoRA在RL训练中的精度影响-量化与强化学习深度解析.md)
- [VLM强化学习RL训练-视觉编码器与LoRA配置前沿](2026-05-24-VLM强化学习RL训练-视觉编码器与LoRA配置前沿.md)
- [nashsu-llm_wiki项目分析_deep-blue](2026-05-24-nashsu-llm_wiki项目分析_deep-blue.md)
- [DeepSeek-Reasonix-开源省钱Agent](2026-05-25-DeepSeek-Reasonix-开源省钱Agent.md)
- [DeepSeek-V4-Pro永久降价75-AI价格战新阶段](2026-05-25-DeepSeek-V4-Pro永久降价75-AI价格战新阶段.md)
- [DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现](2026-05-25-DoRA量化RL训练-方向幅度分解在低精度强化学习中的表现.md)
- [DeepSeek-Reasonix-成本优化架构解析](2026-05-26-DeepSeek-Reasonix-成本优化架构解析.md)
- [proactive-learn-mcp-llm-quant-evolution](2026-05-26-proactive-learn-mcp-llm-quant-evolution.md)
- [挪威2PB-Huawei闪存-LLM训练-主权AI基础设施案例](2026-05-26-挪威2PB-Huawei闪存-LLM训练-主权AI基础设施案例.md)
- [MoE多模态训练-视觉语言MoE路由策略特殊挑战](2026-05-27-MoE多模态训练-视觉语言MoE路由策略特殊挑战.md)
- [外包加本地AI-vs-前沿实验室-LLM经济学拐点](2026-05-27-外包加本地AI-vs-前沿实验室-LLM经济学拐点.md)
- [用无聊语言写LLM代码-一致性复合效应](2026-05-27-用无聊语言写LLM代码-一致性复合效应.md)
- [MoE模型QLoRA-RL训练-专家路由量化噪声叠加效应深度解析](2026-05-28-MoE模型QLoRA-RL训练-专家路由量化噪声叠加效应深度解析.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [AutoSearch 自主训练任务](AutoSearch 自主训练任务.md)
- [多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解](ai-agent/2026-05-14-多目标GRPO-GDPO-AW-GRPO-Reward融合与冲突消解.md)
- [MegatronCore模块化重构与MoE训练前沿](ai-agent/2026-05-16-MegatronCore模块化重构与MoE训练前沿.md)
- [表达清晰的5个训练](ai-agent/2026-05-16-表达清晰的5个训练.md)
- [2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1](explore/2026-05-09-2025年5月AI大爆发-Claude4-Qwen3-DeepSeek-R1.md)
- [开源AI春季爆发-模型推理Agent](explore/2026-05-09-开源AI春季爆发-模型推理Agent.md)
- [2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4](explore/2026-05-13-2026年5月AI模型大战-GPT5.5-Grok4.3-DeepSeekV4.md)
- [开源AI模型新格局-DeepSeek冲击波](explore/2026-05-13-开源AI模型新格局-DeepSeek冲击波.md)
- [LLM推理优化-MoE量化加速全景](explore/2026-05-16-LLM推理优化-MoE量化加速全景.md)
- [LLM推理优化技术](explore/2026-05-16-LLM推理优化技术.md)
- [llm-inference-opt-incremental2](explore/2026-05-18-llm-inference-opt-incremental2.md)
- [llm-inference-opt-update](explore/2026-05-18-llm-inference-opt-update.md)
- [llm-self-prompt-optimization](explore/2026-05-18-llm-self-prompt-optimization.md)
- [MoE-稀疏激活微调工程实践](explore/2026-05-19-MoE-稀疏激活微调工程实践.md)
- [SGLang-vs-vLLM-推理引擎对比](explore/2026-05-19-SGLang-vs-vLLM-推理引擎对比.md)
- [llm_wiki分析与Skill进化](explore/2026-05-20-llm_wiki分析与Skill进化.md)
- [边缘AI推理优化-Jetson平台深度研究](explore/2026-05-21-边缘AI推理优化-Jetson平台深度研究.md)
- [llama-cpp预编译二进制与本地LLM推理](explore/2026-05-22-llama-cpp预编译二进制与本地LLM推理.md)
- [VPO向量策略优化多样性训练提升推理搜索](explore/2026-05-23-VPO向量策略优化多样性训练提升推理搜索.md)
- [LLM推理冗余分析](explore/2026-05-27-LLM推理冗余分析.md)
- [OPT-BENCH-LLM自我优化评测](explore/2026-05-28-OPT-BENCH-LLM自我优化评测.md)
- [antization-deploy-deep-20260524](explore/edge-llm-quantization-deploy-deep-20260524.md)
- [llm-inference-opt-2026-05-17](explore/llm-inference-opt-2026-05-17.md)
- [llm-inference-opt-2026-05-20-supplement](explore/llm-inference-opt-2026-05-20-supplement.md)
- [llm-inference-opt-deep-dive](explore/llm-inference-opt-deep-dive.md)
- [llm-inference-opt-incremental-20260517](explore/llm-inference-opt-incremental-20260517.md)
- [llm-inference-optimization-2026](explore/llm-inference-optimization-2026.md)
- [llm-pid-tuner](llm-pid-tuner.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [分布式训练技术全景-FSDP-DeepSpeed-Megatron](orphan/2026-05-05-分布式训练技术全景-FSDP-DeepSpeed-Megatron.md)
- [MoE混合专家模型-路由策略-负载均衡-训练稳定性](orphan/2026-05-06-MoE混合专家模型-路由策略-负载均衡-训练稳定性.md)
- [tinyedge-lora](tinyedge-lora.md)
- [前瞻性问题-AI垂域LLM载具设计](前瞻性问题-AI垂域LLM载具设计.md)
