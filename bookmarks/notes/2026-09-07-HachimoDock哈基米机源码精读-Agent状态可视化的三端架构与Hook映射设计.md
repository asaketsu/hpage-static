# HachimoDock 哈基米机源码精读 — Agent 状态可视化的三端架构与 Hook 映射设计

#HachimoDock #哈基米机 #ESP32P4 #Agent状态可视化 #ClaudeCodeHook #桌面宠物 #Tauri #PetUI #USB协议 #开源硬件 #Agent外设

## 出处

- 原文：微信公众号文章《哈基米机 HachimoDock：开源、乐鑫 ESP32 主控、任务跟踪、萌宠表情》（约 2.6K 字产品介绍）
- 源码：github.com/YizhengWw/HachimoDock（已 clone 至 `~/uclaw/project/hachimodock/`，29MB）
- 精读范围：README/protocol.md + 桌面端 Rust/Node bridge（hooks+agents 双机制）+ 固件 20 个核心 C 模块（共 ~178K 行 C + ~60K 行 PC 端）
- 笔记日期：2026-09-07 | 指令语义：**分析形成单独项目和笔记保存**

## 一、内容详细整理

### 1.1 产品定位：解决"状态看不见、提醒易遗漏、交互太单调"

HachimoDock（哈基米机）= **桌面端管理器 + ESP32-P4 小屏固件 + 开源硬件** 三件套：

- **下行链路**：PC 上 Codex/Claude Code/OpenClaw/WorkBuddy 等 Agent 的思考/执行/完成/报错状态 → 实时同步到桌面小屏 → 变成宠物表情、动作、颜色、短标签、气泡
- **上行链路**：3 个实体按键 + 四向摇杆（12 种可配置手势）+ 麦克风（长按语音→ASR→注入当前 Agent Session）

**状态语义设计**（16 组状态动画，内置西高地小狗形象）：
- 思考/执行工具/等待确认/完成/报错 → 各有专属表情+动作+颜色
- Agent 空闲 → 待机小动作（"抬头就知道 Agent 是否还在工作、是否在等你决策"）
- 完成/报错气泡保留 60 秒再消失——**不打扰但可追溯**

### 1.2 三端架构总览（README mermaid 图 + 源码验证）

```text
Agent (Codex/Claude/OpenClaw/Copilot/Gemini/Cursor/CodeBuddy/MimoCode...)
   │  hook 注入 / 日志监控 / 进程树识别
   ▼
桌面端 Pet Manager (Tauri + React 前端 / Rust 37.5K 行 / Node bridge sidecar)
   │  USB-UART JSONL（烧录救援） / 原生 USB HS bulk（运行时）
   ▼
ESP32-P4 固件 (~178K 行 C: renderer/input/PetUI/OTA)
   │  MIPI-DSI
   ▼
2.8" 480×640 竖屏（宠物动画 + Session 气泡 + PetUI 组件）
```

**硬件规格**：ESP32-P4（RISC-V 双核 HP@400MHz + LP@40MHz，768KB L2 SRAM）+ 32MB QSPI Flash + 32MB 封装内 PSRAM + ESP32-C6（WiFi6）+ 2.8 英寸 MIPI-DSI 触摸屏。

### 1.3 Agent 状态检测双机制（本项目技术含金量最高的部分）

**机制一：Hook 注入**（`pc/src-tauri/bridge/hooks/`，11 种 Agent 适配器）

以 Claude Code 的 clawd-hook.js 为例——**事件→宠物状态映射表**（源码照录）：

| Claude Code Hook 事件 | 宠物状态 |
|---------------------|---------|
| SessionStart | idle |
| SessionEnd | sleeping |
| UserPromptSubmit | working |
| AssistantMessage / AssistantOutput | speaking |
| PreToolUse / PostToolUse | working |
| PostToolUseFailure | error |
| Stop | attention |
| StopFailure | error |
| SubagentStart | **juggling**（杂耍——多任务视觉隐喻） |
| SubagentStop | working |
| PreCompact | **sweeping**（打扫——上下文压缩的视觉隐喻） |
| PostCompact | attention |
| Notification / Elicitation | notification |
| WorktreeCreate | **carrying**（搬运——git worktree 的视觉隐喻） |

**工程细节**：零依赖 Node 脚本（快冷启动）/ 1s 超时 / 读 hook JSON 转发 session+status+display 元数据到本地 server / PermissionRequest 走 HTTP 阻塞 hook 而非命令 hook（**区分阻塞型与通知型事件**）。

**机制二：日志监控**（`bridge/agents/claude-code.js`）

```javascript
POLL_INTERVAL_MS: 1000,           // 项目目录轮询 1s
PROCESS_POLL_INTERVAL_MS: 30000,  // 进程名扫描 30s
HEARTBEAT_MS: 30000,
INITIAL_TAIL_BYTES: 1048576,      // 初始只 tail 1MB
NEW_FILE_MAX_AGE_MS: 120000,      // 只认 2 分钟内的新文件
MAX_SCAN_FILES: 200,              // 扫描文件上限
PROCESS_NAMES_WIN: ["claude.exe", "claude.cmd", "claude"],
```
**设计哲学**：全部有界（时间/字节/文件数三重上限）——监控本身不能成为系统负担；进程树识别（process-tree.js）把 hook 事件归属到正确的 Agent 实例。

**双机制互补**：hook 给精确事件（有 hook 能力的 Agent），日志监控兜底（无 hook 的场景），进程扫描提供存活心跳。

### 1.4 USB 双协议（firmware/protocol.md）

- **USB-UART JSONL**（`pet-usb-jsonl-v3`）：烧录/救援/早期日志——每行一个 JSON：`{"topic":"<topic>","payload":{}}`
- **原生 USB HS vendor bulk**（`pet-usb-native-v1`）：Type-C 跳线切到 ESP32-P4 native USB OTG 后的运行时数据高速通道
- **hello 握手**：板→PC 上报 boardDeviceId/runtime/fw/buildId/gitSha/protocolSchema/**hardware 全清单**（soc/hpCpu/lpCpu/onChipSram/psram/flash）+ capabilities——**能力协商式设计**，桌面端据 capabilities 决定可用功能（如 H.264 直通、组件版本）

### 1.5 固件架构（20 个 pet_p4_* 模块，头注释即文档）

每个 C 文件头部有结构化注释块（[Input]/[Output]/[Pos]/[Sync]）——**文件级架构文档纪律**。核心模块：

| 模块 | 职责 |
|------|------|
| pet_p4_main.c | 任务协调器：UART/USB 协议流量+显示输入状态+资产，序列化状态访问，OTA 后内置组件包同步 |
| pet_p4_renderer.c | RGB565 逻辑帧 + aspect-fit 资产缩放 + **H.264 直通面板路径**（全尺寸待机播放）+ 组件运行时隐藏双点指示器 |
| pet_p4_miniapp.c | **PetUI 声明式组件运行时**：v3/v4 JSON 小组件（有界：8 变量/6 状态/4 页/12 转移/8 tick/8 按钮）+ RGB565-alpha 精灵 + 事务性安装器（字节预算+设备能力校验后**原子发布**） |
| pet_p4_input.c / touch | 12 手势输入核心 |
| pet_p4_ota.c | OTA + 背光门控首帧（升级不闪屏） |
| pet_p4_behavior.c | 宠物行为状态机（16 组动画调度） |
| pet_p4_assets.c / raw_assets | 资源双槽（固定西高地槽+可替换槽），传输保持原始宽高比 |
| pet_p4_stats / diagnostics | 独立 render/RX 健康采样 |

**UART RX 缓冲 128KB**——为 USB 高速传输到 C 侧解码的背压留足余量。

### 1.6 PetUI Skill：Agent 生成组件的管线

用户在 Agent（Codex/Claude）中调用 `petuiSkill` → Agent 生成游戏或工具 JSON → **结构校验 + 字节预算 + 设件能力校验** → 原子发布到组件库 → 同步到设备。内置组件：贪吃蛇/俄罗斯方块/番茄钟/喝水提醒/Token 仪表盘/Flappy Bird/像素贪食蛇。

**这是"Agent 为设备写 App"的最小可信实现**——生成物被三重门禁约束在设备能力内。

### 1.7 桌面管理端功能全景

- **设备首页**：自动发现 ESP32-P4（不依赖固定 COM 口）/连接/固件/Flash/PSRAM/传输状态/重连/诊断/固件维护
- **Agent 跟随**：自动读取工作中的 Session，标题+摘要+working/done/error 同步为气泡
- **Session 切换**：摇杆左右切气泡 ↔ 桌面端把对应 Agent/Session 拉到前台——**双向联动**
- **形象管理**：AI 生成/Codex 社区导入/本地视频导入，传输前完成面向 P4 的**裁切+转码+资源校验**
- **API 设置**：ASR/形象生成凭据只存本机应用配置，**不写入固件和仓库**

### 1.8 开源与商业边界

- License：**non-commercial source available**（源码可得但禁商用）——学习/复刻自由，商用需授权
- 三端全开源：桌面端+固件+硬件（OSHWHub PCB/BOM/装配教程）
- 公开安装包不内置任何 API Key

## 二、查询拓展

- Tauri sidecar 架构（Rust 主进程 + Node bridge 子进程的 IPC 设计）
- Claude Code hooks 的完整事件清单与阻塞型/通知型分类
- ESP32-P4 的 H.264 硬解码能力边界（esp_h264_dec vs sw）
- OSHWHub 复刻链路（立创 EDA → PCB 打样 → BOM 采购）
- petuiSkill 的 Skill 定义文件（Agent 侧 prompt 结构）
- RGB565-alpha 精灵格式的生成管线（视频→帧→调色板量化）
- 60 秒气泡保留的交互依据（通知疲劳研究）

## 三、归纳总结

1. **产品本质是"Agent 状态的可视化外设"**：把不可见的 Agent 生命周期（思考/执行/等待/报错）翻译成宠物语言——**外设化的关注力管理**：不用切窗口就能感知 Agent 状态
2. **Hook 映射表是全项目最浓缩的设计资产**：15 个 Claude Code 事件 → 15 个宠物状态，其中 juggling（子代理）/sweeping（压缩）/carrying（worktree）三个映射展现了**技术事件到情感隐喻的翻译功力**
3. **双机制检测=精确+兜底+心跳三层**：hook 给事件粒度、日志监控给无 hook 兜底、进程扫描给存活信号——**三层互补而非冗余**
4. **有界资源设计贯穿监控端**：1s 轮询/1MB tail/200 文件/120s 窗口——监控器本身不能成为负担，这是所有常驻 Agent 工具的铁律
5. **USB 双协议按场景分通道**：烧录救援走 UART JSONL（简单可靠），运行时走原生 USB HS bulk（高吞吐）——**一条物理连接两种逻辑通道**
6. **能力协商握手**：hello 报文上报硬件全清单+capabilities——桌面端按能力降级，与 HyperWorks MCP 的 get_environment 同一设计模式
7. **PetUI 是"Agent 写 App"的最小可信实现**：声明式 JSON+三重门禁（结构/预算/能力）+原子发布——生成物永远被约束在设备能力内
8. **文件头注释纪律值得照抄**：[Input]/[Output]/[Pos]/[Sync] 四行结构化注释 × 178K 行 C 代码全员一致——大型 C 项目的可维护性范本
9. **资源双槽设计**：固定形象槽+可替换槽，下发保持宽高比——**系统资源与用户资源的隔离**
10. **License 清醒**：non-commercial source available——开源生态里"学习自由+商用受限"的中间态选择

## 四、趋势判断

1. **"Agent 外设"会成为 2026-2027 硬件创业小风口**：Agent 常驻化（后台跑任务）催生状态感知的物理需求——**屏幕宠物只是第一形态**，后续会有 Agent 状态灯/Agent 手表/Agent 桌面机器人
2. **Hook 协议会成为 Agent 外设的标准接口**：Claude Code hooks/Codex 事件流这类"Agent 生命周期事件"是外设的数据源——**谁定义标准事件集谁卡位**
3. **ESP32-P4 会成为 AI 外设默认主控**：400MHz 双核+32MB PSRAM+MIPI 屏+H.264 解码——外设级 AI 显示的甜点配置
4. **"Agent 生成组件"是 App Store 的种子形态**：petuiSkill 展示了 Agent→设备 App 的自动管线——当组件运行时标准化，**Agent 应用市场**自然出现
5. **非商用 License 会成为 AI 外设开源的主流选择**：硬件创业者需要社区共建（复刻/改进）又需保留商业护城河——source available 是平衡点
6. **通知疲劳推动"环境化计算"**：60 秒气泡保留/待机小动作/不打扰原则——Agent 状态从"通知推送"转向"环境感知"，与 calm technology 理念合流

## 五、关联分析

> 关联对象：自有 Hermes 体系（petdex/observability-dashboard）/ DUCK-Pi_5 / HyperWorks MCP / GrokBot 三层架构

| 对照项 | HachimoDock | 自有体系 | 判定 |
|--------|-------------|---------|------|
| **Agent 状态可视化** | 实体小屏宠物动画 | observability-dashboard（Web 面板）+ petdex（屏幕吉祥物） | ✅ 亲缘：同一需求的软件/硬件两条路——Hermes 可借鉴其**hook 事件→状态映射表**做 dashboard 的事件语义层 |
| **Hook 机制** | Claude Code 15 事件映射 | Hermes 无 hook 状态外发 | ✅ 可借鉴：Hermes gateway 可加 status hook（任务开始/工具调用/等待确认/完成/失败五态），为未来外设/面板提供标准事件流 |
| **DUCK-Pi_5 对照** | 外围智能（智能在 PC，设备显示输入） | 本体智能（策略在设备上跑） | ✅ 两种产品哲学对照：哈基机是"Agent 的脸"，小鸭是"Agent 的身体"——**显示外设 vs 本体智能** |
| **能力协商** | hello 报文硬件全清单 | HyperWorks MCP get_environment | ✅ 同一模式三次出现（HyperWorks/哈基机/自有 cluster-health-check）——**设备/服务自描述+按能力降级**是 Agent 工程通用范式 |
| **有界资源** | 监控三重上限 | Hermes watchdog 巡检 | ✅ 对齐：常驻工具的资源有界是共同铁律 |
| **GrokBot 审批边界** | PermissionRequest→HTTP 阻塞 hook→宠物 attention 态 | GrokBot 审批边界的实体化 | ✅ 有趣对照：**审批等待变成宠物"求关注"**——严肃的权限设计获得了情感化界面 |

**最大启示**：HachimoDock 证明了 **Agent 状态的物理化呈现不是玩具而是生产力**——"抬头就知道 Agent 是否在等你决策"解决了多 Agent 并行工作时的注意力调度问题。对自有体系：**Hermes 多 cron/多 subagent 并行时的状态感知**目前全靠主动查询，hook 事件流+环境化显示是值得纳入的演进方向（可先做软件版：飞书卡片状态灯）。

## 六、指南分析

| 场景 | 查哪节 |
|------|--------|
| 快速理解产品 | §1.1 + §1.2 架构图 |
| Agent 检测怎么实现 | §1.3 双机制+映射表 |
| USB 协议设计 | §1.4 双通道+能力协商 |
| 固件怎么组织 | §1.5 模块表+文件头注释纪律 |
| Agent 生成 App 怎么约束 | §1.6 PetUI 三重门禁 |
| 复刻路径 | §1.7 + §1.8（先看 License） |
| 给自有体系的借鉴 | §五 对照表 |

**核心口诀**：Agent 状态翻译成宠物语言 / hook 映射表是设计资产 / 双机制精确兜底心跳三层 / 监控本身要有界 / USB 按场景分通道 / hello 握手能力协商 / 声明式组件三重门禁 / 文件头四行注释纪律 / License 学习自由商用受限 / 外设化注意力管理。

## 七、拓展应用推荐

- **给 Hermes observability-dashboard**：借鉴 §1.3 事件映射表，为 Hermes 任务生命周期定义标准五态（working/waiting_approval/done/error/idle）事件流——dashboard/飞书推送统一消费
- **给 petdex 技能**：哈基机的 16 组状态动画语义可映射到 Hermes 桌面吉祥物的状态机（当前 petdex 只有动画无状态语义）
- **给 DUCK-Pi_5（远期）**：小鸭的"本体智能+哈基机的状态表达"可合并——小鸭脖子屏幕/LED 表情反馈训练状态（P2 旋钮化之后的下一代交互）
- **硬件复刻候选**：OSHWHub PCB 资料+ESP32-P4 甜点配置——若做 Hermes 实体外设（状态宠物）可直接起步；预估 BOM <300 元
- **延伸阅读**：YizhengWw/HachimoDock 仓库 / OSHWHub 硬件页 / Claude Code hooks 文档 / Tauri sidecar 文档 / ESP32-P4 技术手册 / calm technology（Mark Weiser）

---

→ 相关：[[2026-09-07-HyperWorks-MCP源码精读-FastMCP工具面安全门与Qt主线程活桥的CAE-Agent架构.md]]（能力协商+有界资源同一范式；内嵌 Extension vs 外设显示的接口哲学）
→ 相关：[[2026-09-06-GrokBot智能体操作系统三层控制架构-从Harness-Loop-Graph到审批边界的完整设计.md]]（PermissionRequest→attention 态：审批等待的情感化界面）
→ 相关：[[2026-09-07-GigaBrain行为世界模型精读-三头预测架构地形自标注与DUCKPi5借鉴判定.md]]（DUCK-Pi_5 本体智能 vs 哈基机外围智能的哲学对照）
→ 相关：项目 hachimodock（源码 29MB 已落地）/ DUCK-Pi_5 / 技能 petdex / observability-dashboard
