# DimOS双神经系统架构 — Agent离散思考与物理连续世界的共存设计

#DimOS #具身智能 #Agent架构 #Stream-RPC #机器人运行时 #MCP #Blueprint #时空记忆

> **出处**：微信公众号「具身Agent」，2026-08-17 16:00 发布
> 原文链接：https://mp.weixin.qq.com/s/rfk9NLM61uiIFLxWWI-Q-w
> 抓取方式：移动 UA 直接 curl（3.1MB 全文）
> 主题：DimOS（github.com/dimensionalOS/dimos，0.0.14b1，Apache-2.0）把机器人拆成"两套神经系统"——Stream 持续流平面 + RPC 调用平面，核心命题：LLM 离散低频智能如何进入连续异步的物理世界

## 一、内容整理

### 0. 核心命题

> "具身智能真正难处理的，不只是「脑」和「身体」如何连接，而是**两个完全不同的时间世界如何共存：物理世界连续发生，Agent 的思考离散发生**"

"去厨房看杯子"不是一次 forward pass：理解厨房在哪→查地图→定位→规划→避障→移动→判断到达→取画面→识别→记录→回答。频率差鸿沟：**LLM 几秒想一次｜相机每秒几十帧｜定位持续更新｜底层控制 50-500Hz**。

DimOS 的答案：不用无所不能的"大 Agent"填缝，而是**把机器人拆成一群长期运行的模块，让数据自己流动，把适合决策的部分封装成技能**。

### 1. 八大机制拆解

#### ① Module：机器人是一群长期活着的模块
- 相机/雷达/SLAM/规划器/连接器/Agent 本身都是 Module，核心目录围绕 Module、Stream、Transport、Blueprint、Worker、Coordinator 组织
- 最小模块：`class Detector(Module): image: In[Image]; detections: Out[Detection3DArray]`——吃进 Image 吐出 Detection3DArray，图像谁给的、结果给谁它自己不知道
- 真实机器人像"开机到关机持续运转的生物体"：相机一直在看、定位一直在估、规划一直在算，只有 Agent 偶尔做高层决策——**生命周期完全不同却必须同时存在**
- Coordinator 把模块部署到 Worker 进程按负载分配，计算重的独占 Worker

**背压设计（很"机器人味"）**：异步消息来得比处理快时，不无限排队旧帧，**保留最新未处理值**——视觉/状态估计更需要"现在是什么"，不是补做几十帧前的功课。说明按实时物理系统设计，不是 Web Agent 消息队列生搬硬套。

#### ② Stream 与 RPC：两套神经系统
| 平面 | 承载 | 形态 |
|---|---|---|
| **Stream 持续流** | Image/PointCloud/Pose/JointState/cmd_vel | In[T]/Out[T]/IO[T] 类型化端口（IO 双向为新新增） |
| **RPC 调用** | get_state()/save_map()/plan()/start() | Spec 类型化依赖注入，明确一次请求 |
| Transport 底层 | LCM/共享内存/DDS/ROS2/Zenoh | 7-29 Zenoh RPC 从 Pub/Sub 模拟重写为原生 Query/Queryable |

- TF 坐标变换从特殊 Service **收回成普通数据流**——坐标变换是机器人世界的"基础事实"，不该是架构特例
- Blueprint 构建时找满足 Spec 的模块注入引用，**没有满足者构建阶段直接失败**，不是跑到半路才发现接口不存在
- 一句话：**Stream 描述持续发生持续变化的信号；RPC 做一次明确的请求**——运行时同时需要两种语言

#### ③ Blueprint：装配图而非胶水代码
- `autoconnect()` 按属性名+数据类型自动接线：camera.image 是 Out[Image]、detector.image 是 In[Image]，天然咬合；名字冲突 remap，换通信方式 override Transport
- Blueprint 是**冻结的数据结构**，可组合出更大 Blueprint
- 对 Coding Agent 的意义：结构化、声明式、类型明确的装配图 ≫ 散落目录的启动脚本。未来：人说"加巡检能力"→ Coding Agent 加模块、接流、生成新 Blueprint、仿真验证——**改的是系统拓扑结构而不是控制代码行**

#### ④ Skill 与 MCP：LLM 看到的是能力不是电机
- `@skill` 标注的函数生成 Agent 可理解的 Tool Schema；实现严格：docstring 必须有、参数完整标类型——函数名/参数/说明直接进模型工具描述
- **API 范式迁移：从「机器可执行」到「Agent 可理解」**——过去的 move_base() 写给程序员，未来的 API 还要写清这个能力意味着什么、何时调用、参数物理含义、失败为什么失败
- McpServer 把运行中 Skill 暴露出去，McpClient 动态读取——DimOS 内部 Agent、Claude Code、OpenClaw 面对同一套运行中的机器人能力
- `dimos shell` 直连运行中模块 RPC 不经 MCP——**同时服务三种操作者：人类工程师/Coding Agent/运行时 LLM Agent，同一具身体，不同权限与抽象**
- ⚠️ 边界：Tool 能被调用 ≠ 安全。MCP 解决"怎么找到和调用能力"，不解决"当前物理状态下能不能执行"（第三篇话题）

#### ⑤ memory2：记忆的单位是经验不是句子
- 聊天记录扔向量数据库没用——机器人要存：**什么时候、在哪里、什么位姿、哪个传感器、看到了什么**
- Observation Stream：每条 Observation 绑定时间戳/位姿/标签/原始数据；语义检索时经 Transformer（CLIP 类）生成 Embedding 做相似搜索
- 时空查询 API：`logs.after(t1).before(t2)` / `logs.near(pose, radius=2.0)` / `logs.tags(level="error")` / `logs.search(embedding, k=5)`——Lazy 管线构造，消费时执行
- `live()` 最妙：历史查询+实时订阅同一种 Stream 思维——"这个位置过去的异常给我，从现在起再出异常继续推"
- **设计精髓：Embedding 不是记忆本体，只是记忆的一种索引**——memory2 与普通 Agent RAG 的分野：语言 Agent 记"我以前知道什么"，机器人还要答"我在哪里、什么身体状态、看见过什么"
- 8-13 新增 Agent Eval Framework：历史记录变成评测集，同一框架跑录制数据/仿真/真机（Passive/Interactive）；**Eval 本身暴露成 Skill——Agent 可跑评测、读结果、改代码/Prompt、再跑**。记忆从"档案"变成"经验与评测底座"

#### ⑥ 全链路重演：「去厨房看红杯子」
| 层 | 时间尺度 | 职责 |
|---|---|---|
| LLM/Agent | 秒级·事件触发 | 只在任务节点做决定 |
| 地图/规划 | 按状态与事件更新 | 不一定连续高频 |
| 感知/定位 | 持续采样 10-30Hz | 持续更新位姿 |
| 控制器 | 高频闭环 50-500Hz | 持续输出 cmd_vel |

Agent 理解复合任务→调导航 Skill（LLM 工作结束）→Runtime 世界接管→到达后导航 Skill 返回→Agent 调观察能力→VLM 判断→结果沉淀 memory2→Agent 回答。**金句：Agent 管任务的离散切换，Runtime 管物理世界的连续发生。**

#### ⑦ 三个方向性变化（0.0.14b1）
1. **多本体**：Boston Dynamics Spot 进入（CmdVel 速度驱动+传感器流+Recorder）
2. **拓扑寻址**：Control Coordinator 改 per-instance addressing——"addressing is topology"，消息发给谁由端口拓扑决定不是消息里的地址（双臂/多任务复杂身体关键）
3. **闭环评测**：memory2 之上 Agent Evals（录制/仿真/真机）

#### ⑧ 现状与边界
- 仍在高速重构：接口今天 Service 明天 Topic，RPC 后端会变，不少机器人支持是 Beta
- 适合研究/原型/快速迭代，**离稳定平台有距离**——但正因没定型才看得清 Agent-native 运行时长什么样

### 2. 一句话总结（作者判断）

> **不是把 Agent 接到机器人上，而是把机器人软件本身，变成 Agent 可以理解和操作的运行环境。** LLM 进物理世界的答案不是"更聪明的大模型"，而是"重新设计身体"

## 二、查询拓展

1. **Agent/控制分界线**：Skill 粒度多细合适？navigate() 与 pick() 之间是否需要 walk_through_door() 级中间技能——分界线的工程判据
2. **与 ROS2 生态的生死关系**：DimOS 能绕开 ROS 成为"机器人 Android"吗？DDS/Zenoh/共享内存多 Transport 的性能实测对比
3. **安全边界谁守护**：MCP 暴露 Skill 后，实时控制/权限/物理边界的 enforcement 层在哪（第三篇预告的核心）
4. **memory2 的数据膨胀**：原始数据全存 vs 抽帧存储 vs 事件触发存储的成本-召回权衡
5. **Eval-as-Skill 的自进化闭环**：Agent 跑评测→改代码→再跑，与 SWE-bench 类静态评测的差异——真机上的安全约束

## 三、归纳总结

| 维度 | 要点 |
|---|---|
| 一句话 | DimOS 用 Stream（持续流）+RPC（一次调用）两套神经系统，让离散秒级的 Agent 思考与连续 500Hz 的物理世界共存 |
| 核心抽象 | Module（长期活着）→ Stream/RPC（两种信息）→ Blueprint（声明式装配）→ Skill/MCP（Agent 可理解的能力）→ memory2（时空经验）→ Evals（经验变评测） |
| 最妙设计 | ①背压保留最新值（实时系统思维）②TF 收回普通数据流（去特例化）③Embedding 只是索引不是记忆本体（与 RAG 分野）④Eval 暴露成 Skill（自进化闭环） |
| 时间分层 | Agent 秒级 / 规划事件级 / 感知 10-30Hz / 控制 50-500Hz——LLM 不参与每个控制周期 |
| 定位 | 从"执行 Runtime"长成"执行+记录+评测"闭环基础设施；0.0.14b1 高速重构期 |
| 开放问题 | 谁告诉 Agent 身体的能力边界？安全/实时/权限的 enforcement？能否绕开 ROS？ |

## 四、趋势判断

1. **"Agent-native 运行时"成为具身智能新赛道**：DimOS 证明核心不是更聪明的大模型而是"重新设计身体"——2026 会涌现更多 Agent-first 机器人中间件，与 ROS2 生态形成两代范式竞争
2. **机器人 API 从"机器可执行"走向"Agent 可理解"是全行业迁移**：docstring/类型/物理含义成为 API 一等公民——所有硬件 SDK 都将重写文档层（工具文档 = 新的接口规格书）
3. **memory2 的"经验+评测底座"模式将成标配**：聊天记录 RAG 不适用于机器人，时空绑定的 Observation Stream + Eval-as-Skill 自进化闭环是真身记忆的形态——与 AI4AI harness 论文（脚手架=可复用任务结构）互相印证
4. **Blueprint 是给 Coding Agent 的机器人拓扑接口**：声明式装配图让 Agent 改系统拓扑而非代码行——机器人工程的"自然语言编程"入口，比端到端 VLA（OpenVLA 路线）更工程可控，两条路线将分层共存：VLA 管低层技能，Blueprint+Skill 管系统编排
5. **背压与拓扑寻址反映"物理实时性"回归**：Web 架构模式（无限队列/内容寻址）在机器人场景被逐个修正——实时物理系统的约束正在重塑 Agent 基础设施设计

## 五、关联分析

### 与已有笔记/体系的关联

| 关联对象 | 关系 | 说明 |
|---|---|---|
| 笔记《2026-08-18-OpenVLA架构解剖》 | 对照路线 | OpenVLA 是端到端 VLA（模型即策略，7 token 出动作）；DimOS 是分层运行时（Agent 管决策，Runtime 管连续控制）——两条路线在同一具身体上将分层共存 |
| 笔记《2026-08-18-AI4AI测试时能力迁移》 | 理论互证 | AI4AI 证明"脚手架=外化的可复用任务结构"；DimOS 的 Skill/Blueprint 就是物理世界的脚手架——harness 思想在机器人领域的落地 |
| skill `embodied-ai-control`（ROS2+Gazebo+VLM） | 直接技术栈 | DimOS 支持 ROS2 Transport，其 Module/Stream 抽象可与我们的 ROS2 实践对照；"大脑-小脑分离"设计即本文 Agent/Runtime 分层 |
| skill `dual-mcu-robot-architecture` | 同构验证 | ESP32(执行)+STM32(决策) 分层 = DimOS Agent/Runtime 分层的嵌入式版本；"安全约束在底层"与 dimos shell 权限分层同理 |
| Hermes 自身架构 | 镜像映射 | Hermes 的 Skill=DimOS 的 @skill（Tool Schema 化）；cron/watchdog=长期运行模块；session/memory=memory2（时间戳+上下文绑定）——**MeowBot 本身就是一个 Agent-native 运行时的软件版** |
| skill `mcp-integration` / `native-mcp` | 协议层直接关联 | DimOS 的 McpServer 把 Skill 暴露给 Claude Code/OpenClaw——与 Hermes 的 MCP 客户端生态直接互通的理论基础 |

### 对我们的直接价值（吸收+优化自我）

1. **两套神经系统自查**：Hermes 体系里 Stream（持续流）对应 cron 周期任务/事件推送，RPC 对应对话触发——检查是否有"该做 Stream 的做成了 RPC"（如盯盘应是 Stream 推送不是等用户问）
2. **"Embedding 只是索引不是记忆本体"的警示**：我们的记忆体系（MEMORY.md/skills）价值在时空绑定的上下文（什么场景发现的经验），不只是语义检索——error-case-library 的结构（症状+根因+场景）正是防"档案化"
3. **Eval-as-Skill 自进化**：DimOS 让 Agent 跑评测→改→再跑——skill-stress-test 的自动化方向：评测本身封装成 skill 供 cron 定期自检
4. **背压"保留最新值"策略可平移**：cron 任务积压时（如盯盘推送），应丢弃过期行情快照只处理最新——修改 watchdog 的队列策略
5. **Blueprint 装配思维用于系统编排**：声明式描述模块连接（scan_data→md2html→sync→验证）已隐性存在，可显性化为可组合的 Blueprint 结构，让 Coding Agent 更好理解 homepage 管线

→ 相关：2026-08-18-OpenVLA架构解剖-7B-VLA透明样本的完整链路与OFT手术.md
→ 相关：2026-08-18-AI4AI测试时能力迁移-强模型为弱模型搭推理脚手架.md
→ 相关：2026-05-11-具身智能2026-世界模型VLA车企入局.md

## 相关笔记
- [LLM-Agent多智能体信用归因与自进化](2026-05-31-LLM-Agent多智能体信用归因与自进化.md)
- [自进化Agent三框架与2026记忆基准](2026-08-16-自进化Agent三框架与2026记忆基准.md)
- [Agent记忆系统2026综述-write-manage-read闭环与记忆即RL策略转向](2026-08-18-Agent记忆系统2026综述-write-manage-read闭环与记忆即RL策略转向.md)
- [HarnessVLA无需训练-冻结VLA封装成可调用原语与记忆引导Agent](2026-08-18-HarnessVLA无需训练-冻结VLA封装成可调用原语与记忆引导Agent.md)
- [SinkFlex-RL长视野Agent高效RL训练](explore/2026-08-14-SinkFlex-RL长视野Agent高效RL训练.md)
- [AI-Agent-IDE-Cursor竞品全景](explore/2026-08-16-AI-Agent-IDE-Cursor竞品全景.md)
- [Agent-Optimization替代SEO-GEO商业模式](explore/2026-08-16-Agent-Optimization替代SEO-GEO商业模式.md)
