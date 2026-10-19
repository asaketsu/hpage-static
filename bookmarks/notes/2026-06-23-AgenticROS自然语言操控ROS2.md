# AgenticROS：用自然语言操控 ROS 2 机器人

> 来源：微信公众号文章  
> 日期：2026-06-23

## 核心价值
**AI Agent 无关的 ROS 2 通用接口层**，用自然语言操控 ROS 2 机器人，让机器人从"遥控工具"变为"协作队友"。

## 定位
AgenticROS 是一个开源的 ROS 2 插件和中间件层，由开发者 Chris Matthieu 创建。它是一个桥接层——把 AI 推理模型（Claude、Gemini、OpenAI Codex 等）与底层机器人硬件（摄像头、深度传感器、电机）连接起来。

**核心理念**：*"一个 ROS 2 工作区，一个配置，多个智能体"*

## 快速开始

```bash
# 一行命令完成全部设置
npx agenticros

# 交互式菜单选择 "First-time setup"
# 自动初始化工作区、插件和 API Key
```

## 常用 CLI 命令

| 命令 | 说明 |
|------|------|
| `agenticros up real` | 启动真机栈 |
| `agenticros up sim-amr` | 启动仿真 AMR（Gazebo + RViz） |
| `agenticros mode <real\|sim>` | 切换仿真/真机模式 |
| `agenticros robots` | 管理集群中的机器人 |
| `agenticros skills` | 管理技能 |
| `agenticros doctor` | 健康检查 |
| `agenticros down` | 停止所有服务 |

## 适用场景

| 场景 | 说明 |
|------|------|
| **自然语言控制机器人** | 通过 Claude Code/Desktop 发送自然语言指令，AgenticROS 翻译为 ROS 2 命令，机器人执行并反馈状态 |
| **多机器人任务路由** | 支持发现、列出和管理多个在线机器人，可根据能力筛选合适的机器人执行任务 |
| **仿真/真机无缝切换** | 通过配置文件快速切换 real/sim 模式，自动处理命名空间和话题路由。支持 TurtleBot3、6-DOF 机械臂等主流仿真环境 |

## 项目信息

| 属性 | 值 |
|------|-----|
| **许可证** | Apache-2.0（完全免费开源） |
| **推荐指数** | ⭐⭐⭐⭐☆（满分5星，项目较新、生态尚在建设中） |
| **适合人群** | 机器人开发者、ROS 2 用户、AI 教育/研究机构、企业机器人研发团队 |
| **官网** | AgenticROS 官网 |
| **GitHub** | agenticros/agenticros |

---

## 相关笔记

- [2026-06-23-CompanionBot双脑陪伴机器人](./2026-06-23-CompanionBot双脑陪伴机器人.md)
- [2026-06-23-AgenticROS自然语言操控ROS2](./2026-06-23-AgenticROS自然语言操控ROS2.md)
- [2026-06-23-ESP32-S3引脚配置](./2026-06-23-ESP32-S3引脚配置.md)
