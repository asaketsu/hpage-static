# Agent Harness 自我修复架构：四层自动闭环

> 来源：AI 极未来（微信公众号）| 原文主题：Opik 开源平台的四层自动闭环架构
> 核心论点：可观测性止步于"发生了什么"，真正的瓶颈是 trace 之后的一切——诊断、修复、验证、防复发。这四步必须自动化形成飞轮。

---

## 一、问题定义：为什么可观测性在规模化时失效

当前大多数 Agent 可观测性平台的局限：

| 层面 | 谁做 | 说明 |
|------|------|------|
| 发生了什么 | 平台自动 | Trace/span/指标 |
| 为什么发生 | 👤 手动 | 翻 trace、形成假设 |
| 怎么修 | 👤 手动 | 写补丁、祈祷不搞坏 |
| 怎么防 | 👤 手动 | 加测试、回归检查 |

**瓶颈不在可观测性本身**，而是 trace 出现后必须发生的一切。虚线左边自动运行，虚线右边消耗人力——这才是生产环境 debug 的真正痛点。

每次模型升级引入新故障模式，每个新工具增加新边界情况，harness 复杂度增长速度**远超任何团队手动修复的能力**。

---

## 二、四层自动闭环架构

> 来源平台：Opik（开源），核心理念：循环应被自动化。

### 2.1 第一层：Tracing（埋点）

- 每次 LLM 调用、工具执行、检索步骤通过装饰器自动埋点
- 开箱支持 50+ 框架
- 每条 trace 记录**当时活跃的 Agent 配置**，保证完全可复现

### 2.2 第二层：Trace → 修复代码

其他平台止步于"给你看 trace"。Opik 的关键差异：

1. 内置编程 Agent 读取 span 树
2. 识别故障模式、解释因果链
3. 连接代码仓库后升级为完整修复模式：
   - 读源码 → 定位问题行 → 提出 diff → **你批准** → 用原始失败输入重跑验证 → 锁定为回归测试

**人的参与被压缩到"审批"这一个动作**——从诊断者变成审核者。

### 2.3 第三层：自然语言测试套件

传统评估：标注数据集 + 数值指标 + 浮点数比较 → 符合研究员思维，不符合工程师思维。

替代方案——用自然语言写断言：

```python
suite = opik.TestSuite("agent-v2")
suite.add_assertion("响应必须包含具体交易细节，不能只给数量")
suite.add_assertion("响应绝不能暴露未授权信息")
suite.run_tests()
```

底层转换为 **LLM-as-Judge** 检查，清晰的通过/失败。

**关键变化**：每个调试过的失败 trace **自动变成新的测试用例**。测试套件从真实生产故障中增长。

### 2.4 第四层：Agent Sandbox

- 不是 prompt playground（只改系统提示词重跑一次 LLM 调用）
- **端到端运行完整埋点的 Agent**
- 换模型、改提示词、加工具，观察整个系统在完整 span 树上的响应
- 非开发人员也能安全测试配置

---

## 三、飞轮效应

四层拼在一起形成一个自强化循环：

```
埋点 → 生产失败 → 自动诊断 → 提出修复 → 人工批准
  ↑                                         ↓
  ← 回归测试锁定 ← 验证通过 ← Sandbox 重跑 ←
```

**每个周期，harness 都变得更难被打破。** 这是复利效应——不是线性改善，而是指数级加固。

---

## 四、五条核心启示

| # | 启示 | 含义 |
|---|------|------|
| 1 | 可观测性 ≠ 可修复性 | 知道发生了什么 ≠ 知道怎么修 |
| 2 | 写代码的 Agent 不应该给自己打分 | 诊断和修复需要独立视角 |
| 3 | 每次失败都应该变成防御 | 回归测试从真实故障生长，不是合成数据 |
| 4 | 人的瓶颈在审批而非诊断 | 把人从"找问题"中解放，聚焦"判断修复方案是否正确" |
| 5 | Harness 是活的工程制品 | 不是部署完就不动的配置文件，随每次生产失败变强 |

---

## 五、差距分析：Hermes vs 四层架构

| 我们的实践 | 对应文中概念 | 差距 |
|-----------|-------------|------|
| evolver SCAN→FIX→VERIFY | Trace→诊断→修复→验证 | ⚠️ 已有核心循环，缺回归锁定 |
| error-case-library + Eval Loop | 自然语言测试套件 | ⚠️ 有 eval 回写，缺回归断言机制 |
| skill-ab-testing | Agent Sandbox | ⚠️ 有 A/B 测试但非完整沙箱 |
| session_search | Trace 可复现 | ⚠️ 有历史回放但缺配置快照 |
| content-judge (LLM-as-Judge) | 自然语言断言 | ✅ 已有 |
| PRM 多数投票评分 | 质量评估 | ✅ 已有 |
| 执行/评判分离原则 | "Agent 不应给自己打分" | ✅ 已有（evolver Constraints） |
| 反馈驱动规则自适应 | Harness 自我修复 | ⚠️ 有反馈链但缺自动 diff 生成 |

**最大差距**：缺少从"修复完成"到"回归锁定"的自动化闭环。修复了但不防复发 = 半途而废。

---

## 六、借鉴落实情况

### ① 有利进化（已落实）

| 借鉴点 | 落实动作 | 验证 |
|--------|---------|------|
| Trace→修复→回归测试飞轮 | patch evolver VERIFY 阶段：增加回归锁定步骤 + regression-tests.jsonl 格式 | `grep -c "回归锁定" evolver/SKILL.md` = 4 ✅ |
| 每次失败变防御 | patch error-case-library：增加回归锁定机制 + 飞轮检查 + 复利指标 | `grep -c "回归锁定" error-case-library/SKILL.md` = 2 ✅ |

### ② 有价值（Memory 记录）

- Opik 开源平台（github.com/comet-ml/opik）：四层自动闭环 Agent 可观测性，50+ 框架支持

### ③ 知识库（仅笔记）

- 四层架构参考框架
- Cursor harness 工程投入经验
- "Harness 是活的工程制品"理念

---

*关联：[[2026-06-11-Jim-Fan机器人终局-VLA与遥操作的路线图]] · [[evolver]] · [[error-case-library]] · [[content-judge]]*


## 相关笔记
- [Agent 架构关键变化：Harness 正在成为新后端](2026-05-26-Agent架构关键变化-Harness成为新后端.md) (关键词: agent, harness)
- [让AI自己做增长：基于OPC和Harness思想的自主增长系统探索](2026-05-25-高德OPC自主增长系统-Harness多Agent架构.md) (关键词: agent, harness)
- [Agent Harness Engineering：从 Prompt 到 Harness 的范式跃迁](2026-05-25-Agent-Harness-Engineering-从Prompt到Harness的范式跃迁.md) (关键词: agent, harness)
- [Agent 两条路线：Harness vs Protocol-Native](2026-05-31-agent两条路线-harness-vs-protocol.md) (关键词: agent, harness)
