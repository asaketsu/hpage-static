# 同花顺金融数据服务 Financial-API — 官方 A股数据 + Agent Skill 全家桶

> **来源**：[HiThink-Tech/Financial-API](https://github.com/HiThink-Tech/Financial-API)（同花顺官方，MIT）
> **官网**：https://fuyao.aicubes.cn/ · [API 文档](https://fuyao.aicubes.cn/docs/)
> **记录日期**：2026-08-22
> **定位**：同花顺官方面向 AI Agent / 量化研究 / 应用开发的 A股金融数据服务

**标签**：#同花顺 #A股数据 #FinancialAPI #AgentSkill #MCP #量化数据源

---

### 7 模块索引（本报告内容映射）

| 模块 | 对应章节 | 说明 |
|------|---------|------|
| tag 标签 | 头部标签行 | 6 个标签 |
| 出处 | 头部出处行 | GitHub 官方仓库 + 官网 |
| 内容整理 | 第一~三章 | 六种接入方式/数据能力/最新变化 |
| 查询拓展 | 第四章 | 与本机现有数据源对照 |
| 归纳总结 | 第五章 | 数据能力矩阵 + 替换决策 |
| 趋势判断 | 第六章 | 2 条预测 |
| 关联分析 | 第七章 | 与 ths-auto-trader/铁律引擎/i问财交叉 |
| 拓展应用推荐 | 第八章 | 落地路线（分阶段） |
| 指南分析 | 第九章 | 项目质量 + 边界 |

---

## 一句话总纲

> **一个 API Key 六种接入（Skill/MCP/CLI/API/Python/marketdb），同花顺官方把 A股行情、财务、估值、涨停炸板、龙虎榜、公募基金全部开放给 AI Agent——最大的价值是把"爬虫+逆向"的灰色数据链路变成官方合规链路。**

---

## 一、内容详细整理

### 1.1 六种接入方式（按场景选）

| 你的需求 | 推荐方式 | 说明 |
|----------|----------|------|
| AI Agent 自动查数据 | **`hithink-finance` Skill** | Agent 自动在 API/MCP/CLI/Python 间选择 |
| Claude/Cursor 聊天工具接入 | **MCP** | 4 个托管端点，配 Key 即用 |
| Python/Notebook 研究 | **Python SDK** | 研究脚本/自定义取数 |
| 网站/App/公司系统 | **REST API** | 零依赖 HTTP，任意语言 |
| 终端批量查询导出 | **CLI**（Node.js） | 远端取数+本地库+JSON 输出 |
| 长期保存+SQL 研究历史 | **marketdb** | 本地 DuckDB 自动构建维护 |
| 全市场大批量数据 | **CLI / Market Dumps** | 大结果落盘，防上下文过载 |

**统一凭据**：所有方式共用一个 `HITHINK_FINANCE_API_KEY`（官网 fuyao.aicubes.cn 创建）。

### 1.2 数据能力概览（14 类）

| 数据 | 内容 | 推荐入口 |
|------|------|----------|
| **A股最新行情快照** | 单只/多只/全市场最新价格与交易数据 | CLI/API/MCP/Python |
| **历史 K 线** | 历史走势，支持研究/回测/趋势分析 | CLI/marketdb |
| **公司行动与复权** | 分红送转 + 前复权/后复权生成 | CLI/marketdb |
| **财务报表与指标** | 三大报表 + 五类财务指标 | CLI/API/MCP/Python |
| **估值快照** | PE TTM/MRQ、PB MRQ、PS TTM、PCF TTM 批量 | CLI/API/MCP/Python |
| **集合竞价** | 竞价实时/终态快照 + 短期强弱基准 | CLI/API/MCP/Python |
| **标的目录** | 名称/代码/关键词 → 唯一 thscode | CLI/API/MCP/Python |
| **交易日历** | 交易日判断/数据同步/回测安排 | CLI/API/MCP/Python |
| **指数与板块** | 目录/成分股/行情/历史 K 线 | CLI/API/MCP/Python |
| **同花顺特色数据** | **涨跌停池/炸板池/连板/异动/热榜/龙虎榜** | CLI/API/MCP/Python |
| **公募基金** | 资料/公司/经理/财务/持仓/业绩/净值/场内行情 | CLI/API/MCP/Python |
| **全市场数据导出** | 全量/增量日 K、公司行动标准文件 | CLI/Market Dumps |
| **本地 DuckDB** | 初始化/同步/校验/修复/SQL 查询/导出 | CLI/marketdb |

**⚠️ 能力边界（官方明示）**：分钟 K、tick、海外行情、宏观数据、新闻公告原文、研报**不在公开范围**。请求未支持数据时明确说明，不用模拟数据冒充。

### 1.3 Agent Skill 设计（对本机最有参考价值）

`skills/hithink-finance/` 是统一 Agent Skill 入口：

- **自动路由**：Agent 识别环境和任务，在 API/MCP/CLI/Python SDK 间自动选择
- **契约镜像**：`references/` 内置 API/MCP 契约快照，只在真实调用时才读 `tools/list`
- **凭据管理**：读用户级 `credentials.env`；Agent 不复述 Key、只写用户级凭据源、不进代码/日志/Git
- **安装**：`npx skills add` / Skill Hub（skillhub.cn）/ 手动复制（必须保留 references/）

### 1.4 MCP 四端点

| 服务名 | 覆盖 |
|--------|------|
| `hithink-finance-a-share` | A股行情/K线/财务/估值/竞价 |
| `hithink-finance-a-share-index` | 指数与板块 |
| `hithink-finance-meta` | 标的目录/交易日历 |
| `hithink-finance-fund` | 公募基金 |

### 1.5 最新变化（monorepo 五项）

1. 扩展集合竞价/特色数据（跌停池/炸板池）/公募基金 21 项能力
2. 公募基金全量支持（资料/持仓/净值/区间收益/持有人结构/ETF）
3. 新增 Node.js CLI（`hithink-finance`）
4. 四个旧 Skill 合并为统一 `hithink-finance` Skill
5. 仓库升级 monorepo（Python 迁入 `python/`）

### 1.6 项目结构

```
docs/                  公共文档中心（docs/api 是 REST 契约唯一来源）
skills/hithink-finance/  可独立安装的统一 Agent Skill（含契约镜像）
hithink-finance-cli/   Node.js CLI（不依赖 Python）
python/
├── marketdb/          本地 DuckDB CLI 与 Python SDK
├── toolkit/fuyao/     远端数据 client
├── examples/          可执行示例
└── tests/
examples/inspirations/ 看板灵感（Prompt+预览+静态 HTML）
```

---

## 二、查询拓展

### 2.1 与本机现有数据源对照

本机量化体系当前数据源：

| 数据 | 现有来源 | 同花顺 API 能否替换/增强 |
|------|----------|--------------------------|
| 实时行情 | 腾讯 QT `qt.gtimg.cn`（免费） | ✅ 可替换（官方合规），但有调用频率限制待确认 |
| 日 K 线 | 腾讯 `web.ifzq.gtimg.cn` qfq | ✅ 官方复权数据（公司行动+复权生成） |
| 分时（VWAP） | 腾讯 minute 接口 | ❌ 分钟级不在公开范围——**腾讯源必须保留** |
| 换手率 | 需流通股本计算 | ✅ 行情快照直接提供 |
| 涨跌停池/炸板池 | 无稳定来源 | ✅ **净新增能力**（连板策略核心数据） |
| 龙虎榜 | 无 | ✅ **净新增** |
| 集合竞价 | 无 | ✅ **净新增**（弱转强九要件的 9:25-9:35 窗口数据！） |
| 财务报表/估值 | 无 | ✅ 净新增（基本面过滤） |
| 交易日历 | 手动维护 JSON | ✅ 可替换（每年手动更新的痛点消除） |
| 板块成分/热榜 | i问财（自然语言，不稳定） | ✅ 结构化替代 |

### 2.2 "数据源升级"的战略意义

本机数据链路的现状是**腾讯免费接口 + 手动日历 + i问财自然语言**组合——灰色程度高、稳定性靠运气。官方 API 的价值：

1. **合规性**：从"逆向接口"变成"授权调用"
2. **数据广度**：涨停池/炸板池/龙虎榜/竞价是连板策略的关键缺失数据
3. **维护成本**：交易日历/复权处理交给官方
4. **Agent 原生**：Skill/MCP 设计就是给 Agent 用的

### 2.3 成本待确认项

README 未公开定价——`fuyao.aicubes.cn` 注册后可见。"数据权限、调用频率和可访问 capability 以官网与账号授权为准"。**接入前必须确认**：免费额度/调用频率限制/历史数据回溯深度。

---

## 三、归纳总结

### 3.1 分阶段接入决策

```
阶段0（现状）：腾讯QT + 腾讯K线 + 手动日历 + i问财
    ↓ 痛点：涨停池/炸板池/龙虎榜/竞价缺失，日历手动，i问财不稳
阶段1（净增能力优先，不动现有链路）：
    + 涨跌停池/炸板池/连板数据（连板策略升级）
    + 集合竞价快照（弱转强窗口数据）
    + 交易日历（替换手动JSON）
    ↓
阶段2（按需替换）：
    ? 换手率直接取（替代股本计算）
    ? 龙虎榜（情绪周期跟踪）
    ? 财务/估值（基本面过滤层）
    ↓
阶段3（本地化研究）：
    ? marketdb DuckDB（回测数据本地化，替代每次拉腾讯）
    ↓
不可替换（永久保留）：
    ✗ 分时数据（VWAP/铁律⑳依赖腾讯minute接口——官方无分钟级）
```

### 3.2 六接入方式对本机的适用度

| 方式 | 本机适用度 | 理由 |
|------|-----------|------|
| Python SDK | ★★★★★ | 量化脚本直接 import，与现有架构最契合 |
| REST API | ★★★★ | 兜底方案，curl/urllib 即用 |
| CLI | ★★★ | 批量导出场景（marketdb 初始化） |
| Agent Skill | ★★★ | 可借鉴其 Skill 设计（契约镜像/自动路由） |
| MCP | ★★ | 本机已有 native-mcp，可加但非必须 |
| marketdb | ★★ | 回测量大时再上（DuckDB 占磁盘） |

---

## 四、趋势判断

### 趋势 1：传统金融数据商全面 Agent 化

> 依据：同花顺官方直接发布 Skill/MCP/CLI 全家桶，且 AGENTS.md/SKILL.md 是仓库一等公民。Wind/iFinD/东财等竞品会跟进——金融数据竞争从"给终端"转向"给 Agent"。

### 趋势 2：Agent Skill 成为数据服务的标配交付形态

> 依据：本仓库 Skill 设计（自动路由/契约镜像/凭据安全规范）展示了数据服务的 Skill 交付范式。README 明确"优先安装 Skill"而非 API 文档——服务方开始围绕 Agent 而非开发者设计入口。

---

## 五、关联分析

### 5.1 与 ths-auto-trader 项目（~/uclaw/project/ths-auto-trader/）的关联

ths-auto-trader 是本机同花顺客户端 UI 自动化项目（xdotool 时代 → API 时代演进）。本仓库是**同花顺官方数据 API**——与 ths-auto-trader 的交易执行层互补：

- ths-auto-trader：交易执行（下单/持仓管理）
- Financial-API：数据供给（行情/涨停池/龙虎榜）

两者组合 = 同花顺生态的完整"数据+执行"链路，且都是官方/半官方渠道。

### 5.2 与 stock-iron-rules 铁律引擎的关联

引擎当前数据源是腾讯 QT + 手动日历。可升级点：

- **铁律⑭（只跟龙头）**：涨停池/连板数据直接支持龙头判定（当前靠 limit_count 近似）
- **弱转强九要件**（08-21 学习日志待验证项）：集合竞价 9:25-9:35 窗口数据正是该策略的缺失前置——**官方竞价快照可能是解锁这个待验证策略的钥匙**
- **交易日历**：`is_trading_day()` 的手动 JSON 维护痛点消除
- **情绪周期量化**（08-21 待验证）：连板晋级率统计需要涨停池/炸板池数据——当前无稳定来源，官方 API 直接供给

### 5.3 与 iwencai-stock-screener 的关联

i问财自然语言选股接口不稳定（本机 skill 已记录痛点）。同花顺板块成分/热榜/异动的结构化 API 可替代 i问财的部分场景——**同一厂商的 API 版本**，稳定性必然优于网页逆向。

### 5.4 与 pm-skills/agents-from-scratch 笔记的关联

三个仓库共同指向同一趋势：**服务商围绕 Agent 设计交付物**（pm-skills 的 Skill 工厂 / LangChain 的 Agent Inbox / 同花顺的 Skill+MCP）。Agent Skills Standard 正在成为跨厂商的交付契约——本机 400+ Skill 体系与这个方向完全对齐。

---

## 六、拓展应用推荐

### 6.1 分阶段落地路线

**阶段 1（本周可做）**：
- 注册 fuyao.aicubes.cn 获取 API Key，确认免费额度/频率限制
- Python SDK 装入 venv，跑通"涨停池查询"（连板策略数据升级）

**阶段 2（确认额度后）**：
- 铁律引擎接入交易日历（替换手动 JSON——每年节假日手动维护的痛点终结）
- 集合竞价快照接入开盘侦察 cron（9:25-9:35 窗口）——为弱转强九要件验证铺路
- 涨停池/炸板池接入收盘总结（连板晋级率统计——情绪周期量化的数据基础）

**阶段 3（量化研究深化）**：
- marketdb 本地 DuckDB：回测数据本地化（280 日窗回测当前每次拉腾讯，可一次性落盘）
- 财务/估值快照：选股五要件加基本面过滤维度

### 6.2 借鉴其 Skill 设计

- **契约镜像模式**：references/ 内置 API 契约快照，只在真实调用时读 tools/list——本机调用外部 API 的 skill 可借鉴（减少运行时探测）
- **凭据安全规范**：Agent 不复述 Key/只写用户级凭据/不进 Git——明文化进本机 AGENTS.md
- **能力边界诚实声明**："请求未支持的数据时明确说明，不用模拟数据冒充"——与本机"不虚构结果"原则同构，值得在数据类 skill 中显式声明

### 6.3 必须保留的腾讯数据链路

**分时数据（VWAP）不可替换**——官方无分钟级。铁律⑳ VWAP 主力成本线和盘中提醒 cron 依赖腾讯 minute 接口，永久保留。

---

## 七、指南分析

### 7.1 项目质量

- **官方背书**：同花顺（HiThink）官方仓库，数据合规性无虞
- **接入方式全覆盖**：Skill/MCP/CLI/API/Python/marketdb 六路并进，场景表清晰
- **Agent-first 设计**：AGENTS.md + SKILL.md 是一等公民，凭据安全规范完整
- **能力边界诚实**：明示分钟 K/tick/海外/宏观/研报不在范围，"不用模拟数据冒充"
- **文档治理严格**：docs/api 是 REST 契约唯一来源，skill 契约镜像有同步脚本

### 7.2 待确认/局限

- **定价未公开**：免费额度/频率限制/历史回溯深度需注册后确认——**接入前第一步**
- **Star/Fork 数未显示**（页面渲染问题）——社区采用度待观察
- **分钟级缺失**：VWAP/盘中监控仍需腾讯源（双数据源长期并存）
- **Node.js CLI 与 Python 双栈**：维护成本对官方可控，对使用者是双依赖

---

## 八、金句摘录

> "通过一个统一的 API Key，即可查询 A股最新行情、集合竞价、财务报表、估值、指数、板块、公募基金资料与净值、涨跌停、炸板、个股异动、热榜和龙虎榜等数据。"

> "优先安装 hithink-finance Skill。Agent 会识别当前环境和任务，在 API、MCP、CLI 与 Python SDK 之间自动选择合适的能力。"

> "请求未支持的数据时，应明确说明，不使用模拟数据或静态示例冒充真实结果。"（能力边界诚实声明）

---

## 九、行动启示

- **立即行动**：注册官网确认定价/额度——这是后续一切决策的前提（免费额度够则阶段 1 本周启动）
- **净增能力优先于替换**：涨停池/炸板池/竞价/交易日历是现有链路没有的，先加增量不破坏现有稳定链路
- **分时永久保留腾讯**：官方无分钟级，VWAP 铁律⑳不受影响
- **弱转强九要件解锁**：集合竞价快照是 08-21 学习日志待验证项的缺失前置——接入后可启动本地回测（n>100 铁律）
- **情绪周期量化铺路**：连板晋级率统计（11-12%冰点/50-55%回暖/60%高涨锚点）从此有稳定数据源

---

> **延伸阅读**：
> - 仓库：https://github.com/HiThink-Tech/Financial-API
> - 官网/API Key：https://fuyao.aicubes.cn/
> - API 文档：https://fuyao.aicubes.cn/docs/
> - [ths-auto-trader 项目](~/uclaw/project/ths-auto-trader/) — 同花顺执行层互补
> - [stock-iron-rules](~/.hermes/skills/quant-trading/stock-iron-rules/) — 数据升级的主要消费方

## 相关笔记

- [QuantaAlpha 轨迹级进化因子挖掘](2026-08-23-QuantaAlpha轨迹级进化因子挖掘.md) — LLM 因子挖掘侧数据源
- [同花顺量化交易自动化的最新动向](~/explore/2026-05-19-ths-auto-trader-latest-dynamics.md) — 执行层互补（ths-auto-trader）
- [ATR 波动率与止损策略](~/explore/2026-06-13-atr-volatility-stop-loss-strategy-deep-dive.md) — 量价因子与风控