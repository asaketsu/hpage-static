# ROSClaw Physical AI Harness：MuJoCo 从仿真器到物理实验室

> 原文：微信公众号（具身Agent｜深度解构 Physical AI 的前沿与边界）
> URL: https://mp.weixin.qq.com/s/gjnik87PV7_j2EaRexHeLA
> 阅读日期：2026-09-21 | 评分：★★★★★（5/5，与 DUCK 训练管线和 Harness 方法论双重强相关）
> tag: #MuJoCo #ROSClaw #PhysicalAI #Harness #具身智能 #Agent架构 #仿真验证

## 一、核心命题

**MuJoCo 负责算物理，ROSClaw 补的是 Agent 做实验、留证据、能重放的那一层。** 把 MuJoCo 从"Agent 可以调用的 simulator"升级为 Agent 原生的 Physical AI Harness——不是让 Agent 更方便地调 MuJoCo，而是给具身 Agent 搭一座可以工作的物理实验室。

核心类比：Codex/Claude Code 能持续修改大型软件，靠的不只是模型，还有 repository/filesystem/diff/test/CI/版本控制/权限边界这层 Coding Harness。物理世界需要同构的东西——Repository→Model、Branch→State Branch、Test→Physics Experiment、CI→Strict Replay。

## 二、四条不可妥协的设计纪律

1. **Agent 不直连 MuJoCo**：一切通过结构化工具（Tool Gateway + SimulationRuntime）
2. **Model/State/Trace 一旦成为证据就不可原地修改**（immutable ref）
3. **任务终态由 Verifier 定义**，不是 Agent 的自由文本
4. **SIMULATED EVIDENCE 永远不能自动兑换成 REAL PERMIT**——仿真一万次成功也不能自动获得真机执行权

## 三、工具原语：理解—构造—实验—验证四组工作流

| 组 | 原语 | 说明 |
|----|------|------|
| Understand | capabilities / load / inspect / observe | 结构化字段优先："自然语言负责理解，结构化数据负责证明" |
| Build | patch / snapshot / compile_world | 修改不落原文件，形成新 Model Reference |
| Experiment | rollout / branch_experiment / compare / render | 分叉实验+受控比较 |
| Verify & Interact | audit / interact | 交互走 validate→precondition→execute→observe→postcondition→receipt |

跨身体通用：UR5e/Unitree Go2/Shadow Hand 共享同一套 Body/State/Action/Evidence 语言。

## 四、复现性三契约（本文技术含量最高部分）

1. **模型不可变**：改 damping = 新 Model Reference（母模型+修改内容+新 digest，类似 Git commit）；digest 覆盖 mesh/texture——两份相同 XML 配不同 mesh ≠ 同一物理世界；可导出自包含 .mjz 工件
2. **状态完整**：只存 time/qpos/qvel/ctrl 不够——延迟传感器的 history buffer、Equality Constraint 激活态、plugin state、userdata、warmstart 都影响未来演化。**姿态相同 ≠ 物理状态相同**。State Semantics v2 以 mjSTATE_INTEGRATION 为权威语义，证据分 fidelity 等级：LEGACY_PARTIAL 最高只能 semantic replay，永远不能升级成 RAW_EXACT——"证据强度不能比原始数据本身更强"
3. **控制通道显式**：MuJoCo PID actuator 引入后一个执行器可对应多个 control 输入，Control Schema 显式描述每个通道

**给我们的直接映射**：DUCK 项目踩过的坑全部被这套契约覆盖——G8 域不匹配（训练域≠部署域）、warm start 状态不完整、执行器参数被框架替换而不自知（kp_fw 被 BAM actuator 覆盖）。这就是"把隐性物理知识变成 Agent 不能绕过的机器契约"。

## 五、Branch Experiment：Agent 像科学家一样做实验

案例：UR5e 关节 damping 调多少既稳又不过慢？
- 所有候选从同一 Snapshot 出发，仅改变实验变量
- 不是 LLM 猜参数，而是 rollout→Audit→Metrics→Strict Replay，由 sim_compare 计算指标表、best candidate 和 **Pareto 非支配集合**
- 并行批实验：CPU 多线程 batch，joint/actuator 结构签名必须一致才放行；batch 与串行 qpos 差异对齐到 **1e-9**
- 范式分工：**GPU 找候选，CPU MuJoCo 判结果**（未来接 MJX/MJWarp 大规模搜索，权威验证面仍是 CPU strict replay）

范式转变：程序员思维（写代码→跑程序→看画面）→ 实验科学思维（观察→假设→控制变量→分叉实验→测量→否证→比较→重放→留证据）。

## 六、Physical Honesty：抓取的四条铁律 + 证据拆分

最容易暴露"假成功"的是抓取：
1. contact 必须真实出现，没接触直接失败
2. 不能 teleport qpos，不能运行时偷偷创建 hidden weld（"焊"在手上的假抓取）
3. constraint-assisted grasp 必须在 receipt 中标注，不许冒充纯接触抓取
4. task_success 由 Verifier 判定，不由 Agent 宣布

**证据拆分**：simulation_valid ≠ physical_audit_pass ≠ task_success ≠ verification_status——仿真没崩不等于任务成功，视频看起来正确同样不等于。Verifier 谓词（inside/near/contact/upright）返回测量值+阈值+为什么满足/不满足；"looks placed correctly"永远不能成为 Verifier Truth。

Audit 23 项检查六大类：几何完整性（collision coverage/penetration/self-overlap）、动力学稳定性（servo hold/divergence/energy）、执行器安全（saturation/force/velocity）、传感器可信度（finite/delay buffer）、确定性（reset/replay/state-model consistency）、数值坐标一致性（solver/timestep sensitivity/frame convention）。

**诚实原则**：机器人没声明最大速度就返回 NOT_EVALUATED，不凭空编造"2 rad/s 安全"——诚实的"不知道"很重要。

## 七、视觉证据链 + 跨后端演进

- 视觉观测（camera_rgb/depth/segmentation）返回 Artifact Reference 而非裸数组，附内外参+simulation time，图像 provenance 全可查
- 工程旁注（**Jetson 实战经验**）：部分 Jetson 环境 GL Context 初始化触发 native abort → rendering 隔离在子进程，失败显式返回 SIM_RENDER_UNAVAILABLE，不允许静默掩盖
- Receipt 永远标记 trust_level=SIMULATED、usable_for_real_execution=false
- Replay 区分四种不一致：ENV mismatch / MODEL mismatch / STATE mismatch / PHYSICS divergence
- 下一站 System Identification：真机数据反向校准仿真参数（mass/friction/damping/sensor delay 搜索空间→分叉实验→training 拟合→holdout 验证）
- 远期：Isaac Sim/Gazebo/真机影子执行遵循同一套 Body/State/Action/Experiment/Evidence/Verifier/Receipt 抽象

## 八、Practice 概念：从 Action 到 Experiment 到 Practice

**Physical AI 的基本单位不是一次 Action，而是一次被验证、被记录、能进入 Memory 的 Practice。** SimulationReceipt 继续进入 Practice/Memory/Darwin：
- 一次失败 → Failure Pattern
- 一组实验 → Parameter Recipe
- 反复验证的方案 → Candidate Skill，交 Darwin 多 seed/多扰动验证

轨迹记录"机器人做了什么"，Practice 记录"为什么这么做、哪里失败、怎样改对、能否复用"。

## 九、💡 对我们的价值分析

### ✅ 已在做的（印证方向）
- **DUCK 训练门禁体系**：开训三层门禁（注册表比对/env.yaml 复核/每小时指纹）= ROSClaw "Agent 不能绕过的机器契约"的雏形；位移验收禁代理指标 = "task_success 由 Verifier 判定不由 Agent 宣布"
- **error-case-library + experience-bank**：Failure Pattern→Skill 沉淀路径与 Practice/Memory/Darwin 同构
- **harness 架构 skill 族**（六层 Harness/harness-engineering-principles）：Coding Harness→Physical Harness 的迁移判断已被本文独立验证

### ⚠️ 可改进的（差距）
- **无 digest 化 Model Reference**：DUCK 变体管理靠目录隔离+md5 双验，缺"母模型+修改+新 digest"的 Git 式链——G8-G11 变体森林溯源困难（曾靠"lineage archaeology"考古）
- **状态保存不完整**：asa 播放器存 qpos 恢复 ≠ 物理等价，warmstart/sensor history 丢失——正是 State Semantics v2 指出的坑
- **仿真→真机无显式 Permit 边界**：asa 部署链没有 trust_level 标记，仿真通过后直接上真机的流程缺一道"REAL permit 人工授予"闸
- **System Identification 是 DUCK 下一步刚需**：3025 执行器域力限差 83% 的教训 = 仿真参数没被真机数据校准过

### 🔥 重点行动
1. **给 DUCK 变体加 Model digest 链**：XML+mesh+actuator 参数联合 digest，变体 fork 时记录母引用——治"lineage 考古"病，成本一天
2. **验收 receipt 化**：headless_eval 输出从"日志文本"升级为结构化 receipt（model digest+scene+指标+audit 结果），真机部署前检查 trust_level
3. **跟踪 ROSClaw 仓库**（github.com/ros-claw/rosclaw）：其 MuJoCo Menagerie 多身体 Harness 若开源成熟，DUCK 的 asa 播放/评测链可借其 branch_experiment 做参数扫描（替代手写循环脚本）

## 十、内容整理（归纳总结与关联分析）

**归纳总结**：一套位于 Agent 与物理引擎之间的证据基础设施——四纪律（不直连/不可变/Verifier 裁决/仿真≠真机权）+三契约（模型 digest/完整状态/显式控制通道）+四组原语（理解/构造/实验/验证）+23 项审计，把"跑完了"变成"有证据、可验证、能重放"。关键数字：23 项 audit 检查、batch-串行对齐 1e-9、6 类审计域、4 种 replay 不一致分类。

**关联分析**：与 [[2026-09-21-达索全线AI化-LEO与CATIA虚拟伙伴]] 同周阅读形成呼应——达索"拒绝幻觉创作、基于物理规律的工业世界模型"是产品叙事，ROSClaw 是这套叙事在 Agent 基础设施层的工程实现；两者的公约数都是"证据链+可验证性"。与 harness-engineering 的关系：本文是 Physical 域对"质量门禁机械化"原则的独立再发现，可作该 skill 的具身智能案例补丁。

## 十一、查询拓展

- ROSClaw 仓库：github.com/ros-claw/rosclaw（Alpha 阶段，看 audit 23 项清单与 State Semantics v2 实现细节）
- mjSTATE_INTEGRATION 权威语义：MuJoCo 文档 "State and Integration" 章节
- .mjz 自包含工件格式规范（对标 reproducible research 的容器化）
- 对比阅读：Genesis/Isaac Lab 的实验管理（是否有同级别 receipt 概念——大概率没有，这是 ROSClaw 差异点）

## 十二、趋势判断

1. **Harness 从 Coding 泛化到 Physical 是 2026 主线**：Coding Harness（repo/test/CI）→ Physical Harness（model/state/replay/audit）→ 未来所有"Agent 修改外部世界"的域都会长出自己的 Harness 层
2. **"证据等级"语言将成为具身智能标准词汇**：RAW_EXACT vs semantic replay、NOT_EVALUATED vs FAILED 的区分比"成功/失败"二值更符合工程现实，预计被主流框架（Isaac Lab/MuJoCo Playground）跟进
3. **Sim2Real 的闸门设计比成功率更重要**：usable_for_real_execution=false 的硬编码拒绝是安全架构不是功能缺失——真机执行权必须人来授予，这与航空"适航放行"逻辑完全同构
4. **Practice 作为数据单位**：从 trajectory/action token 上升到"完整实践"（含失败原因与修复路径），是 RL 数据工程从"状态-动作对"到"经验卡片"的范式升级，与我们的 experience-bank 设计互证

## 十三、指南分析（怎么用这篇文章）

- 设计评测/验收管线：直接抄第四/六节的契约清单当 checklist（模型 digest、完整状态字段、Verifier 谓词、证据四拆分）
- 讲 Agent 基础设施趋势：第一节的 Coding→Physical Harness 类比是最好开题（30 秒讲清赛道）
- 给 DUCK 项目做架构升级评审：第九节三条重点行动即提案正文，每条都有明确的坑案例（lineage 考古/warmstart 状态丢失/域不匹配）支撑

## 十四、拓展应用推荐

- 延伸阅读：[[2026-05-11-OpenClaw-ROS2机械夹爪自然语言控制]]（同项目族早期：RosClaw 作为低层夹爪插件；本文是同一生态向 Harness 层的跃迁）
- DUCK 项目落地：digest 链+receipt 化两条行动项建议进 docs/NN 变体管理章节
- harness-engineering-principles skill：本文可作 Physical 域案例引用

## 相关笔记

- [Microban与2026双足RL前沿](./2026-09-01-Microban与2026双足RL前沿-低成本平台同构与重训校准.md) — 低成本双足同构平台
- [MuJoCo仿真到Three.js可视化全链路](./2026-09-01-MuJoCo仿真到Three.js可视化全链路-千问工程还原.md) — MuJoCo 工具链近亲
- [达索全线AI化](./2026-09-21-达索全线AI化-LEO与CATIA虚拟伙伴.md) — 工业世界模型的 CAD 端叙事
