# Open Academic Paper Gen：引用核验级论文生成器（安装实录）

> **来源**：GitHub https://github.com/mmlong818/open-academic-paper-gen
> **记录日期**：2026-10-13（本机 Jetson Orin 安装实测）
> **License**：AGPL-3.0（网络服务需开源修改版）

**标签**：#论文生成 #引用核验 #LangGraph #文献检索 #学术工具

---

## 一、内容详细整理

### 1.1 一句话定位

**从一个研究主题到"每条引用都对照原文核验过"的论文初稿**——9 阶段多 Agent 流水线，核心卖点不是写作而是**反幻觉**：不信任写作模型，先建真实文献池，草稿中每条引用必须可机械核验（key 可解析 + DOI 真实 + 被引论文真支撑该论断）。

### 1.2 为什么存在（作者的问题意识）

LLM 能写流畅论文但会编造参考文献，或给真实文献安上它从未提出的论断。本项目的解法：
- 先检索真实文献（OpenAlex/Crossref/Semantic Scholar/arXiv 四源），有开放获取版就抓**全文**（不只是摘要）
- 草稿中每条引用 = 文献池中的一个 `[cite:KEY]` 标记（key=第一作者+年份+标题首词）
- 三道核验：key 解析 → DOI/元数据对 Crossref 核真 → **被引论文是否真支撑那句话**（有全文时给出 PDF 页码）
- 没通过的被标记，在受约束规则下修订（只能改被标记句子/引用候选文献/弱化说法），或留人工审阅
- 每阶段后有**人工审批闸门**（key_gates 默认；full_auto 全程无人值守）

### 1.3 九阶段流水线

| # | 阶段 | 职责 |
|---|---|---|
| 1 | Scoping | 主题→研究问题+中英文关键词（按文献比例） |
| 2 | Literature | 四源检索、去重、评分，中英文名额分配 |
| 3 | Cleaning | 补摘要、抓全文、LLM 筛选、引用链扩展、PRISMA 计数 |
| 4 | Trends | 分批综合 + 证据表（每篇一行：任务/方法/数据/指标/发现/局限） |
| 5 | Angle | 创新点诊断（问题/方法/数据/视角四层 + 最近已有工作 + 审稿人可能反对） |
| 6 | Outline | 章节结构 + 摘要 |
| 7 | Writing | 分节撰写，快模型为每节挑参考文献 |
| 8 | Verification | 三道引用核验 + 受约束修订 + **模拟三位审稿人**（逐字引用原文）+ 风格检查 |
| 9 | Export | Markdown/LaTeX + GB-T 7714/APA 7/数字编号 + RIS/BibTeX（只列实际引用且可解析的） |

### 1.4 架构

```
Next.js 16 前端 ──WS──▶ FastAPI + LangGraph 状态机 ──▶ PostgreSQL(必需) + Redis(可选, 降级内存推送)
                                                      │
                          OpenAlex · Crossref · Semantic Scholar · arXiv
                          LLM 双轨: fast(智谱优先→OpenAI降级) / strong(OpenAI优先→智谱降级)
```

## 二、查询拓展

### 2.1 引用核验三检查的工程含义
- 检查一（key 解析）：幻觉 key 渲染为 `[?KEY]` 方便搜索修正
- 检查二（layer1 存在性）：DOI 对 Crossref 404 再查 doi.org（覆盖 DataCite 注册的 arXiv DOI）；标题匹配后还要核对共同作者/年份（在线优先允许差1年）/起始页；**网络错误与无 DOI 默认通过——无法验证≠无效**
- 检查三（layer3 论断支撑）：快模型判"原文是否支撑这句话归给它的内容"；找不到的细节判"无法判断"不判"不支撑"；**不支撑只产生警告从不删引用**；有全文时警告带 PDF 物理页码

### 2.2 模型双轨路由
- fast 档：智谱优先，失败降级 OpenAI fast（glm-5.3-flash 筛选 1.6s/篇）
- strong 档：OpenAI 优先（gpt-6.1-sol），失败降级智谱——LangChain with_fallbacks 透明处理
- ⚠️ 论断核验/该引未引/审稿**硬需要 OpenAI key**（审稿无备用模型）
- 模型 ID 全部可通过 `OPENAI_MODEL_FAST/STRONG` `ZHIPU_MODEL_FAST/STRONG` 换

### 2.3 与我们体系的对照
- **论文计划匹配度极高**：用户铁律"每周一篇论文，新颖性+查重+官方格式（GB-T7714）"——本工具的 Export 层 GB-T 7714 + 三道核验 + 模拟审稿恰好对位查重和格式两关
- **查重环节增强**：Angle 阶段的"创新点诊断+最接近已有工作"= 我们 scholar-assist 手动做的查重的自动化版
- **PRISMA 流程**：文献筛选计数透明化（综述类论文的硬需求）

## 三、归纳总结

### 3.1 核心设计哲学（可迁移）

- **不信任写作模型**：写作与核验彻底分离，核验依据是"文献池里实际存在的论文"
- **引用可机械核验**：`[cite:KEY]` 标记制替代 (作者, 年份) 行文式——核验是确定性的，不靠模型自觉
- **警告而非删除**：所有核验失败只标记不自动删（"误报并不罕见，请当作需要对照原文核实的线索"）
- **无法验证≠无效**：网络错误/无 DOI 默认通过，保守设计

### 3.2 成本结构
- 筛选每篇 1 次 fast 调用（SCREENING_CONCURRENCY=8 并发）
- 论断支撑检查每篇被引论文 1 次 fast 调用
- 三审稿人 ≈ 单审稿人 3 倍（REVIEW_PANEL 可关）
- evals 离线回放对比改动前后（幻觉率/支撑判定/审稿意见数）

## 四、趋势判断

### 趋势1：学术 LLM 工具的护城河在"核验"不在"生成"
依据：生成已是红海，本项目差异化全在 layer3 论断级核验+PDF 页码定位+受约束修订——工程量远大于写作本身。

### 趋势2：开源学术工具链在补齐"综述自动化"最后一环
依据：检索（Elicit）→ 阅读（Stork）→ 写作（本项目）→ 审稿（本项目内嵌），PRISMA+证据表表明目标用户是系统综述作者。

## 五、关联分析

### 5.1 与周论文产线的关联
我们 weekly-paper/weekly-paper-review 流程（选题→查新→写作→格式→归档）中"查新+格式"两步可直接引用本工具产出作为交叉验证；尤其 GB-T 7714 导出与我们 paper 格式要求一致。

### 5.2 与 scholar-assist/deep-analysis 的关联
我们现有的"检索+精读+结构化"链路偏分析，本工具偏成稿+核验。互补：deep-analysis 出深度理解，oapg 出可核验初稿。

### 5.3 与 paper-humanizer 的关联
paper-humanizer（降 AIGC 检测）与本工具（提高引用真实性）是同一问题的两面——真实性内核 + 表达外衣。

## 六、金句摘录

> 「一篇看起来引用齐全的草稿，仍可能完全不能用。」— 引用数量≠引用质量。

> 「网络错误与无 DOI 默认通过：无法验证不等于无效。」— 保守核验的边界意识。

> 「把每条警告当作需要对照原文核实的线索，而不是裁决。」— 工具谦逊性声明。

## 七、行动启示

- **安装定位**：本机实测安装路径（Jetson Orin，Python 3.12 + Node 24 + Docker），详见第八节
- **key 策略**：无 OpenAI key 时全双轨压 sensenova glm-5.2 可跑通 fast 链路，但审稿/论断核验层质量打折（见安装实录）
- **使用边界**：产出是"草稿"非成品，每条警告需人工对照原文；学术诚信责任在使用者

## 八、安装实录（本机 Jetson Orin，2026-10-13）

### 8.1 环境依赖盘点
- ✅ Python 3.12.11（miniforge3）
- ✅ Node v24.15.0（要求 20+）
- ✅ Docker 29.4.2（提供 PostgreSQL/Redis 容器）
- ❌ pnpm → `npm install -g pnpm` 补装
- ❌ 本机无 psql/redis → 用 docker compose 的 postgres:16-alpine + redis:7-alpine

### 8.2 安装步骤（实测顺序）
```bash
# 1) 代码
git clone https://github.com/mmlong818/open-academic-paper-gen.git
cd open-academic-paper-gen

# 2) 后端(建议独立 venv)
cd backend && python3 -m venv .venv && .venv/bin/pip install -e . && cd ..

# 3) 前端
cd frontend && pnpm install
# sharp 构建脚本被忽略时: pnpm approve-builds sharp
cd ..

# 4) 基础设施(镜像拉取慢, 需耐心; 遇 registry EOF 重试即可)
docker compose up -d postgres redis

# 5) 配置 .env(见下)
# 6) 启动
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080   # 后端
cd frontend && pnpm dev                                            # 前端
# 打开 http://localhost:3000
```

### 8.3 ⚠️ 坑表（本机实测踩到的）

1. **venv 迁移失效**：backend/.venv 内嵌绝对路径（shebang/pth 都指向旧路径），项目目录迁走后 venv 必须在新位置重建（`rm -rf .venv && python3 -m venv .venv && pip install -e .`）
2. **docker pull 慢/EOF**：registry-1.docker.io 直连不稳，postgres:16-alpine + redis:7-alpine 共 ~330MB，`docker compose up` 卡住时手动 `docker pull` 分开拉
3. **pnpm 忽略构建脚本**：Next.js 16 的 sharp@0.34.5 默认被 pnpm 跳过，`pnpm approve-builds sharp` 放行（图像优化需要）
4. **无 OpenAI key 的降级配置**：`OPENAI_BASE_URL` 环境变量可把"OpenAI 轨"指到任何兼容端点（openai SDK 自动读取），全双轨压 sensenova glm-5.2 可跑通；但审稿层质量依赖真 OpenAI strong 模型
5. **zai coding plan 额度**：实测 1013 14:2x 5h 窗口耗尽（17:00 重置）——配工具 key 时避开与交互会话抢同一额度
6. **内存压力**：Jetson 7.4GB 总内存，前端 pnpm build + 后端 + pg + redis 并行时留意 swap；实测 pnpm install 期间系统内存 5.1GB 已用

### 8.4 .env 关键配置（无 OpenAI key 版）
```env
DATABASE_URL=postgresql+asyncpg://papergen:papergen_dev@localhost:5558/papergen
REDIS_URL=redis://:redis_dev@localhost:6400/0
# 全双轨走 sensenova(OpenAI 兼容)
OPENAI_API_KEY=<sensenova-key>
OPENAI_BASE_URL=https://token.sensenova.cn/v1
ZHIPU_API_KEY=<sensenova-key>
ZHIPU_BASE_URL=https://token.sensenova.cn/v1
OPENAI_MODEL_FAST=glm-5.2   OPENAI_MODEL_STRONG=glm-5.2
ZHIPU_MODEL_FAST=glm-5.2    ZHIPU_MODEL_STRONG=glm-5.2
```

### 8.5 关键配置开关速查
| 开关 | 默认 | 说明 |
|---|---|---|
| VERIFY_CITATION_SUPPORT | true | 检查三论断支撑（快模型调用×被引数） |
| VERIFY_UNCITED_CLAIMS | false | 该引未引检查（每节1次调用） |
| REVIEW_DRAFT / REVIEW_PANEL | true | 模拟审稿/三审稿人（成本3×） |
| CITATION_GRAPH_OUTLINE | false | 综述类：按引用图主题群组织章节 |
| 协作模式 | key_gates | 每阶段暂停待审批；full_auto 全程无人值守 |

## 九、指南分析

### 9.1 值得抄的工程模式
1. **key 标记制**：`[cite:KEY]` 让引用核验从语义判断降为确定性查找——任何"AI 写作+引用"系统都该先定这样的标记协议
2. **核验不删只警告**：误报率不低的场景下，"标记+人工审"比"自动修"安全
3. **受约束修订的采纳条件**：不引入其他 key + 大部分未标记句子逐字保留才采纳——防修订越改越乱
4. **evals 离线回放**：固定题目冻结文献池，改动前后同一文献池对比——可迁移到我们任何 LLM 工程

### 9.2 局限（作者自己列的，用前必读）
- `(作者, 年份)` 式引用不核验（只认 `[cite:KEY]`）
- 中文期刊很少开放获取 → 中文题目的全文证据/引用链扩展收益远小于英文
- 检查三"不支撑"误报不罕见，是线索不是裁决
- 中文数据库检索器（CNKI/万方/维普）是占位，需机构权限，仓库不提供
- AGPL-3.0：改了做网络服务必须开源

### 9.3 责任声明要点
产出是草稿，依赖前必须读被引原文逐条核实；使用方对学术诚信负责（机构要求时披露 AI 辅助）；勿提交 API key/.env。

## 十、拓展应用推荐

### 10.1 同类替代与互补工具
| 工具 | 定位 | 与本工具关系 |
|---|---|---|
| Elicit | 文献检索+数据抽取 | 上游——检索强但不写稿不核验 |
| scite.ai | 引用语境标注（支持/反驳） | 与检查三（论断支撑）同思路，但 scite 是人工标注库，本工具是逐句 LLM 判定 |
| Consensus | 研究结论搜索 | 偏结论速查，无成稿能力 |
| 我们自建 scholar-assist | 检索+阅读+结构化 | 互补——它出深度分析，oapg 出可核验初稿 |

### 10.2 可迁移到我们体系的三件
1. **`[cite:KEY]` 标记协议**：任何"AI 写作+引用"场景先定标记制，把语义核验降为确定性查找——我们 weekly-paper 写作环节可引入
2. **三道核验分层设计**（存在性→元数据→论断支撑）：可裁剪成轻量版挂到笔记/论文产出的自检链
3. **evals 离线回放**：固定题目+冻结文献池，改动前后同池对比——可迁移到任何 LLM 工程的回归测试

### 10.3 适用人群判断
- ✅ 系统综述/文献综述型论文（PRISMA+证据表+引用链扩展全是为它设计）
- ✅ 需要 GB-T 7714 格式的中文投稿（导出层直接对口）
- ⚠️ 实验型论文的研究方法章节（工具只覆盖文献侧，实验设计不管）
- ❌ 中文数据库密集型题目（CNKI 检索器是占位，中文 OA 文献少）
