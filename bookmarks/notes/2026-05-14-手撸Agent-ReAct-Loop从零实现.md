# 手撸一个 Agent — 从零实现 ReAct Loop

- 📅 2026-05-14
- ⭐ 3/5 — 清晰的入门教程，ReAct Loop 状态机讲得明白，避坑清单有实用价值
- 🏷️ #Agent #ReAct #LLM #FunctionCall #Python #状态机
- 📰 AI副业轻创（姚毛毛）
- 🔗 https://mp.weixin.qq.com/s/X3VZbYAhuFKlMqiTTsYlvw

## 摘要

不用任何 Agent 框架，纯 Python + OpenAI API，<50 行实现完整 ReAct Loop。核心是一个 5 步状态机：发消息→判断tool_calls→执行工具→结果回写messages→循环。文章配套 4 个实战避坑点和面试题解析。

## 核心内容

### 1. ReAct Loop 状态机
```
[1] messages → LLM
[2] 有 tool_calls？
  ├─ 无 → 输出回答，结束
  └─ 有 → [3] 执行工具
[4] 结果加入 messages（role: tool）
[5] step+1，回到[1]（除非 ≥ max_steps）
```

### 2. 四个代码组件
- **工具定义**：字符串入/出，简单纯粹
- **tools JSON**：description 决定 LLM 是否调用，写得精准调得准
- **execute_tool**：函数名分发器，映射到真实 Python 函数
- **run_agent**：主循环，messages + max_steps 防死循环

### 3. 避坑清单（4个）
1. **忘记加 tool 结果到 messages** → LLM 看不到数据，无限重复调同一工具
2. **max_steps 设置** → 建议 10-15 + 重复检测（连续两次同参数→强制停止）
3. **tool_choice="auto"** → 模型可能不调工具，用 "required" 或指定函数名强制
4. **工具执行失败** → 必须把错误返回给 LLM，否则基于错误假设推理

### 4. 递归 vs 循环
- 用循环：递归有栈溢出风险，循环更容易加停止条件和中间日志

## 🔍 借鉴点

- **重复检测逻辑**：连续两次调同一工具且参数相同→强制停止。这是生产环境必备的防御机制，Hermes 可借鉴
- **工具错误必须回传 LLM**：简单但容易被忽略的实践，确保 LLM 知道工具失败而非假设成功
- **max_steps = 10-15**：合理默认值参考

## 🔗 关联性

- 关联已有笔记：[[2026-05-14-HTML-Anything-Agent驱动HTML编辑器]] — 同为 Agent 生态
- 关联已有 skill：state-machine-loop — Hermes 的状态机循环实现
- 关联已有 Memory：Agent架构（Workflow包Agent，Prompt分层）

## 💡 启发

- **Agent = 会循环的模型 + 能执行的工具**：这个定义精准且实用，剥离框架后的本质
- **description 即 ACI（Agent-Computer Interface）**：工具描述不仅是文档，是 LLM 的操作手册，写得不好 Agent 就废了
- **50 行代码讲清原理** > 500 行框架 demo — 好的技术教学应该是"剥洋葱"而非"堆积木"

## 🔮 预判

- ReAct Loop 是 Agent 的"Hello World"，后续会演化出更复杂的状态机（Plan-Execute、Multi-Agent Orchestration）
- 重复检测和错误恢复会成为 Agent 框架的标准内置能力
- Function Call 协议（文章预告的下篇）是理解 Agent 行为的关键

## 相关笔记
- [[2026-05-14-HTML-Anything-Agent驱动HTML编辑器]] - Agent 生态项目
- [[2026-05-14-Agent工程4月实践]] - Agent 工程方法论


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
