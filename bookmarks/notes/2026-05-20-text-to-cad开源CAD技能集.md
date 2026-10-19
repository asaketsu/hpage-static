# Text-to-CAD：AI 驱动的 3D 零件生成开源 CAD 技能集

> 来源：AI开源提效指南 ｜ 2026-05-20 ｜ [原文链接](https://mp.weixin.qq.com/s/9nuVL89pix2QzxTtURMs8g)

---

## 核心定位

Text-to-CAD 是一个开源的 AI Agent 驱动 CAD 建模技能集，用自然语言生成 3D 零件，专为 CAD 建模、机器人和硬件设计而生。GitHub 3K+ Stars。

**核心理念**：用自然语言描述零件或机构，让 AI 编程代理（Codex、Claude Code）自动生成参数化 CAD 模型。

**底层技术栈**：
- **build123d**：Python 参数化 CAD 库
- **OpenCascade**：开源 CAD 内核
- **WASM**：WebAssembly 支持浏览器端渲染
- **Agent Skills 标准**：遵循开放标准

---

## 七大技能

| # | 技能 | 功能 | 输出格式 |
|---|------|------|----------|
| 1 | **CAD Skill**（核心） | 生成参数化 CAD 模型、`@cad[...]` 几何引用 | STEP、STL、3MF、DXF、GLB |
| 2 | **step.parts Skill** | 从标准件库查找下载螺丝/轴承/电机等 | 标准件 3D 模型 |
| 3 | **CAD Explorer Skill** | 浏览器 WebGL 渲染预览 | 可视化链接 |
| 4 | **URDF Skill** | 生成机器人描述 XML | URDF |
| 5 | **SDF Skill** | 生成仿真描述 XML | SDF |
| 6 | **SRDF Skill** | MoveIt2 语义定义 | SRDF |
| 7 | **SendCutSend Skill** | 激光切割预处理报告 | DXF、STEP |

---

## 支持格式

| 类别 | 格式 |
|------|------|
| CAD | STEP、STL、3MF、DXF、GLB |
| 机器人 | URDF（ROS）、SDF（Gazebo/Isaac）、SRDF（MoveIt2） |

---

## 快速上手

```bash
# 克隆
git clone https://github.com/earthtojake/text-to-cad.git
cd text-to-cad

# 各 Agent 安装
./scripts/codex-install.sh        # Codex
./scripts/claude-install.sh       # Claude Code
./scripts/gemini-install.sh       # Gemini CLI
./scripts/openclaw-install.sh     # OpenClaw

# 通用安装（推荐）
npx agent-skills-cli add earthtojake/text-to-cad
```

### 工作流

1. **描述** — 告诉 Agent 你想要的零件/组件/夹具/机器人
2. **编辑** — 让 Agent 更新 CAD 源文件
3. **生成** — 创建 STEP/STL/3MF/DXF/GLB/URDF/SDF/SRDF 输出
4. **检查** — 打开 CAD Explorer 审查模型
5. **引用** — 复制 `@cad[...]` 句柄进行几何感知的精确编辑
6. **提交** — 保存源文件和生成的产物

---

## 10 个基准测试案例

| # | 名称 | 描述 |
|---|------|------|
| 1 | 矩形校准块 | 四孔校准块 |
| 2 | 圆形法兰 | 螺栓孔阵列 |
| 3 | L 型支架 | 加强筋、双向孔 |
| 4 | 阶梯轴 | 键槽 |
| 5 | 开放式电子外壳 | 带安装柱 |
| 6 | 航空级叉形支架 | 减重切口 |
| 7 | 径向发动机 | 气缸散热片 |
| 8 | 离心叶轮 | 后弯叶片 |
| 9 | 螺旋楼梯 | 螺旋扶手 |
| 10 | 行星齿轮组 | 多齿轮配合 |

---

## 项目亮点

- **完整的 Text-to-CAD 实现**：从简单校准块到复杂行星齿轮组
- **多 Agent 支持**：Codex、Claude Code、Gemini CLI、OpenClaw
- **CAD Explorer 可视化**：基于 WebGL 浏览器预览，无需桌面 CAD
- **机器人描述全链路**：URDF + SDF + SRDF 一键生成
- **标准件库集成**：step.parts 在线标准件查找

---

## 关键链接

| 资源 | 链接 |
|------|------|
| 官方文档 | https://www.cadskills.xyz |
| 在线演示 | https://demo.cadskills.xyz |
| GitHub | https://github.com/earthtojake/text-to-cad |

---

## 与 Hermes 集成潜力

- 可通过 `npx agent-skills-cli add` 安装为 Hermes Skill
- 适用于 AERIS-10 项目中机械零件的快速建模
- URDF/SDF 输出可直接用于机器人仿真

---

*笔记时间：2026-06-05*

## 相关笔记
- [开源3D_设计AI:-text-to-3](explore/2026-06-01-开源3D_设计AI:-text-to-3.md)
