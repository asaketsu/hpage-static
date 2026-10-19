# 结构工程师从零入门 Codex（四）—— 让 Codex 接上 AutoCAD

## Tag
#Codex #AutoCAD #MCP #ModelContextProtocol #结构工程 #AI辅助设计 #COM #AutoLISP #DXF #ezdxf #Autodesk #自动化绘图 #AI工具链

## 出处
- **来源**：微信公众号（结构工程师从零入门 Codex 系列）
- **标题**：结构工程师从零入门 Codex（四）—— 让 Codex 接上 AutoCAD
- **链接**：https://mp.weixin.qq.com/s/w8Lx2K4h9S0PnAtj1y9AyQ
- **日期**：2026年6月

## 内容详细整理

### 核心结论

> Autodesk 官方的 Product Help MCP 主要是查资料，不是画图。想让 Codex 真正操作 AutoCAD，得靠社区方案或自己包装 COM/AutoLISP/DXF 生成能力。

### MCP（Model Context Protocol）是什么

MCP 是一套「AI 接外部工具的协议」。以前 Codex 回答问题靠两类东西：
1. 训练数据里的知识
2. 本地文件系统 + 终端

但 AutoCAD、Revit、企业资料库等不会自动出现在 Codex 面前，中间需要一个「接头」——**MCP Server**。

一个 MCP Server 可以暴露三类东西：
- **Resources**（只读资源：文件、文档、数据）
- **Tools**（可执行工具：脚本、API 调用）
- **Prompts**（预设提示模板）

### 两个层次的清晰拆解

| 层次 | 问题 | 技术方案 |
|------|------|---------|
| **第一层：CAD 能力从哪来** | 底层绘图自动化 | COM/ActiveX、AutoLISP、.NET API、ezdxf(DXF) |
| **第二层：怎么交给 AI 用** | 接口标准化 | MCP Server（把底层能力包装成标准工具） |

> MCP 不是 CAD 能力本身，它更像外面套的一层工具接口。

### Autodesk 官方的两条 MCP 路线

| 路线 | 位置 | 能力 | 定位 |
|------|------|------|------|
| **Autodesk Assistant**（内置） | AutoCAD 2027 内部 | 能理解绘图上下文、CAD 标准检查 | AI 引导式帮助与支持入口 |
| **Product Help MCP**（外部） | HTTP endpoint | 查资料，110+ 产品文档 | read-only 文档查询 |

**Product Help MCP 地址**：`https://developer.api.autodesk.com/knowledge/public/v1/mcp`

**Product Help MCP 能做**：
- 查命令用法（如 LAYISO 怎么用）
- 查产品文档
- 查操作流程

**Product Help MCP 不能做**：
- 不能打开本机 AutoCAD
- 不能画线、建图层、保存 DWG

### 社区方案：autocad-mcp

| 项目 | 地址 | 说明 |
|------|------|------|
| puran-water/autocad-mcp | GitHub | 社区项目，非官方 |

**两个后端**：
- **File IPC**：控制 Windows 上运行中的 AutoCAD LT
- **ezdxf**：无 AutoCAD 环境时生成 DXF 文件

**配置步骤**：

```
1. 克隆项目到 D:\tools\autocad-mcp
   git clone https://github.com/puran-water/autocad-mcp.git
   uv sync

2. 在 AutoCAD 中加载 LISP dispatcher
   APPLOAD → mcp_dispatch.lsp

3. 在 Codex 配置 ~/.codex/config.toml
   [mcp_servers."autocad-mcp"]
   command = 'D:\tools\autocad-mcp\.venv\Scripts\python.exe'
   args = ["-m", "autocad_mcp"]
```

**连接验证**：调用 `system(operation="status")` 检查 backend 类型
- `file_ipc` = 连上了本机 AutoCAD
- `ezdxf` = 离线 DXF 后端

### 实际效果

作者用详细 prompt 让 Codex 绘制标准结构轴网（18×K 轴网，8400×7200 间距），Codex 耗时 11 分钟，生成的轴网**完全可用，不需修改**。

关键洞察：**不同的提示词得到的结果完全不同**。AI 时代，学会和 AI 对话本身就是一项重要能力。

## 查询拓展

### 相关技术

1. **COM / ActiveX**：Windows 平台上 AutoCAD 自动化的传统方式，Python 通过 `pywin32` 连接运行中的 AutoCAD 实例。

2. **AutoLISP**：AutoCAD 内置的脚本语言，可以通过 `APPLOAD` 加载 `.lsp` 文件执行。

3. **ezdxf**：Python 库，无需安装 AutoCAD 即可创建/修改 DXF 文件。跨平台，适合服务器端批量生成图纸。

4. **.NET API for AutoCAD**：AutoCAD 官方提供的 .NET 编程接口，比 COM 功能更全。

5. **Codex**：OpenAI 的 AI 编码助手（类似 Claude Code），支持通过 MCP 连接外部工具。

6. **uv**：Astral 开发的 Python 包管理器（Rust 实现），替代 pip + venv。

### SAP2000/PKPM/YJK 接入思路

文章提到结构分析软件接入思路相似，但每个软件接口差别很大：
- **SAP2000**：OAPI（Open API），COM 接口
- **PKPM**：有限的外部接口
- **YJK**：有自己的 API 体系

## 归纳总结

### MCP 的本质

| 问题 | 回答 |
|------|------|
| MCP 是 CAD 能力本身吗？ | ❌ 不是，MCP 是工具接口层 |
| MCP 解决什么问题？ | 「怎么把能力交给 AI 用」 |
| COM/AutoLISP 解决什么？ | 「CAD 能力从哪来」 |

### 四种 CAD 自动化方式对比

| 方式 | 需要 AutoCAD | 难度 | 能力范围 | 适合 MCP 包装 |
|------|-------------|------|---------|-------------|
| COM/ActiveX | ✅ 需要（Windows） | 中 | 最全（读写操作） | ✅ |
| AutoLISP | ✅ 需要（CAD 内） | 低-中 | 中（CAD 内操作） | ✅ |
| .NET API | ✅ 需要（Windows） | 高 | 最全 | ✅ |
| ezdxf (DXF) | ❌ 不需要 | 低 | 有限（文件生成） | ✅ |

### 当前状态总结

```
官方 Product Help MCP → 查资料（read-only）
官方 Autodesk Assistant → 引导式帮助（AutoCAD 2027 内置）
社区 autocad-mcp → 真正操作 CAD（COM + ezdxf）
```

## 趋势判断

### 短期（1-2年）
- 更多工程软件开放 MCP 接口（SAP2000、Revit、PKPM）
- Autodesk 官方可能推出真正能操作 CAD 的 MCP（目前只能查资料）
- 社区 MCP Server 生态爆发，覆盖各种工程软件

### 中期（3-5年）
- 结构工程全流程 AI 化：建模→分析→出图→校审
- MCP 标准化成熟，工程软件标配 MCP Server
- AI 理解工程规范，自动校验图纸合规性

### 长期（5-10年）
- 结构工程师角色转型：从画图到审图/决策
- AI 负责重复性绘图工作，工程师负责方案优化和判断
- 工程知识库 + MCP + AI = 全自动化设计流水线

### 技术挑战
1. **CAD 接口复杂度**：不同 CAD 软件接口差异大，统一封装难
2. **工程语义理解**：AI 不理解结构力学语义，容易生成不合理图纸
3. **Prompt 工程门槛**：详细 prompt 才能得到可用结果
4. **安全性**：AI 直接操作 CAD 有风险，需要权限控制和回滚机制

## 关联分析

### 与已有项目的交叉

| 已有项目 | 交叉点 |
|---------|--------|
| **struct-gen / struct-gen-agent** | 结构设计 AI Agent，可直接对接 autocad-mcp 做图纸输出 |
| **CATIA CAA** | 同属 CAD 自动化，CAA 是 CATIA 的 API，MCP 思路通用 |
| **舵机机械臂** | 机械臂路径规划类似 CAD 自动化的轨迹生成 |
| **ACR AI Advisor** | ICAO ACR 智能顾问，MCP 接入工程软件的通用模式 |

### 与已有笔记的关联

| 笔记 | 关联点 |
|------|--------|
| 机器狗MPC贝叶斯优化 | 都是 AI 接入工程系统：一个是控制参数优化，一个是设计自动化 |
| 语义SLAM行为地图 | 行为地图需要理解环境语义，MCP 让 AI 理解 CAD 语义，殊途同归 |

### 技术栈层次

```
┌─────────────────────────────────────────────┐
│              AI 客户端 (Codex/Claude)          │
│         自然语言 → 工具调用 → 结果返回          │
├─────────────────────────────────────────────┤
│              MCP 协议层                        │
│     Resources + Tools + Prompts 标准化接口      │
├─────────────────────────────────────────────┤
│              MCP Server 层                    │
│  autocad-mcp / SAP2000-mcp / Revit-mcp ...    │
├─────────────────────────────────────────────┤
│              CAD 能力层                        │
│   COM / AutoLISP / .NET API / ezdxf (DXF)    │
├─────────────────────────────────────────────┤
│              CAD 软件                         │
│        AutoCAD / Revit / SAP2000              │
└─────────────────────────────────────────────┘
```

---

**生成时间**：2026-06-26
**笔记路径**：`~/uclaw/bookmarks/notes/2026-06-26-结构工程师从零入门Codex接上AutoCAD.md`

## 相关笔记
- [AI+CAD 五大方向全景分析](2026-06-24-AI+CAD五大方向全景分析.md) (AI+CAD全景)
- [Codex 指令保姆级教程 — @dengdry (Oldeng) 深度拆解](ai-agent/2026-05-07-Codex指令保姆级教程.md) (Codex指令)
- [开源3D/设计AI: OpenSCAD + LLM](explore/2026-06-12-开源3D_设计AI-OpenSCAD+LLM.md) (OpenSCAD+LLM)
