# text-to-cad：自然语言驱动的参数化 CAD — 深度分析笔记

> **来源**: 微信公众号（mp.weixin.qq.com/s/l-1HZnn_HPUvB4EtZBe5Bg）
> **笔记日期**: 2026-05-14
> **标签**: #CAD #AI设计 #build123d #OpenCASCADE #agent #text-to-cad
> **关联项目**: [[text-to-cad-agent]] [[struct-gen]] [[Claude 3D CAD 连接器分析]]
> **格式**: 双格式(MD + HTML) · 含借鉴进化点

## 摘要

text-to-cad（earthtojake）利用 build123d Python 库 + OpenCASCADE 几何内核，让 AI 通过**生成 Python 代码**而非渲染图片来创建 CAD 模型。核心创新是 @cad[] 引用机制 — 给每个几何特征分配句柄，支持精准局部编辑。已支持 STEP/STL/URDF/SDF 导出，并内置 SendCutSend 制造预检。GitHub 一天涨 2500 星。

## 核心技术点

### 1. 代码即几何（Code-as-Geometry）
- 不是 Midjourney 式"生成图片"，而是 AI 写 build123d Python 代码
- 代码可执行、可调试、可局部修改、可复用
- 设计意图被翻译成结构化程序，而非不可回溯的操作历史

### 2. @cad[] 引用机制
- 每个零件/特征/组件分配句柄（如 @cad[flange]）
- 解决"左边那个孔"等自然语言歧义问题
- 本质是自然语言↔三维几何的双向桥
- 支持团队协作：设计变更变成可追溯的对话记录

### 3. 多格式导出
- STEP/STP → 传统 CAD
- STL/3MF → 3D 打印
- DXF → 激光切割
- URDF/SDF/SRDF → 机器人仿真（Gazebo/MuJoCo）

### 4. 制造预检
- SendCutSend 集成：材料厚度、最小特征尺寸、倒角半径
- 设计完 → AI 预检 → 提交生产，全链路打通

### 5. 安装方式
```bash
npx agent-skills-cli add earthtojake/text-to-cad
```
兼容 Codex、Claude Code、Gemini CLI、OpenClaw、Hermes

## Benchmark 样例
- 矩形校准块（100×60×20mm，四角打孔，顶部倒角）
- 行星齿轮组
- 螺旋楼梯
- 离心叶轮
- 共 10 个，每个附带完整 AI 生成代码

## 与现有生态的对比

| 维度 | text-to-cad | Claude MCP 连接器（Blender/Fusion） | 传统 CAD |
|------|------------|-----------------------------------|---------|
| AI 角色 | 生成几何代码 | 操作现有工具 API | 人工操作 |
| 输出 | 可编辑 Python | 可编辑工程对象 | 二进制文件 |
| 精度 | 参数级 | 参数级 | 参数级 |
| 协作 | @cad[] 句柄引用 | 对话式 | 文件版本管理 |
| 入门门槛 | 极低（一条命令） | 需要专业工具 | 高（学习曲线长） |
| 成熟度 | 早期（Star暴涨中） | 早期（4月发布） | 成熟 |

## 借鉴进化点（对我方系统的启发）

### B1: 代码即模型 — struct-gen 已部分实现
- struct-gen 的 NLU Parser 已有自然语言→参数的能力
- 但目前生成的是结构化参数（非几何代码）
- **进化方向**: 引入 build123d 作为几何代码生成层

### B2: 引用机制 — struct-gen 缺失
- struct-gen 没有句柄引用概念
- 修改参数需要重跑整个流程
- **进化方向**: 为截面、构件、连接添加 @struct[] 引用

### B3: 制造预检 — struct-gen 无
- struct-gen 只做规范验算（强度），不做可制造性检查
- **进化方向**: 添加 DFM 检查模块

### B4: 机器人导出 — struct-gen 无
- AERIS-10 项目的结构件如果能直接导出 URDF 将非常有价值
- **进化方向**: 添加 URDF/SDF 导出器

### B5: Agent 化集成 — 核心机会
- text-to-cad 支持多 AI Agent（Codex/Claude Code/Hermes）
- 与 Hermes 生态天然契合
- **进化方向**: 建为 Hermes Skill，自然语言全流程驱动

## 能力边界 & 局限
- 复杂曲面设计（如汽车外观）尚不可用
- 大型装配体管理未涉及
- 公差/配合/表面处理等制造细节未覆盖
- 无结构强度验算（与 struct-gen 互补）

## 关联笔记
- [[2026-05-13-Claude-3D-CAD-创意连接器深度分析]] — MCP 路线对比
- [[2026-05-12-MBSE结构设计深度研究]] — MBSE + CAD 融合
- [[2026-05-12-nTop-Automate-CLI-完整测试文档]] — 参数化设计 CLI 参考
- [[2026-05-11-LLM冲击下PINN应用变化与发展]] — 数字孪生 + 仿真

## 相关笔记
- [Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [航空结构设计AI短期基础设施](2026-05-14-航空结构设计AI短期基础设施.md)


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)

### CAD/航空系列
- [2026-05-14-航空结构设计AI短期基础设施](2026-05-14-航空结构设计AI短期基础设施.md)
- [2026-05-13-Claude-3D-CAD-创意连接器深度分析](2026-05-13-Claude-3D-CAD-创意连接器深度分析.md)
- [explore/2026-05-16-航空数字主线知识蒸馏-本地素材回顾](explore/2026-05-16-航空数字主线知识蒸馏-本地素材回顾.md)
