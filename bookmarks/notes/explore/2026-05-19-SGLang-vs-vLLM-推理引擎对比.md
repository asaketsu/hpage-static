# SGLang vs vLLM：LLM 推理引擎对比 2026

> 📅 嗅探时间：2026-05-19 | 来源：LocalAI Master、CSDN、Reddit | 类型：llm-inference

## 核心对比

| 指标 | SGLang | vLLM | 差异 |
|------|--------|------|------|
| **吞吐量 (H100, Llama 3.1 8B)** | 16,215 tok/s | 12,553 tok/s | SGLang +29% |
| **输出 Token 吞吐量** | 893.82 tok/s | 412.99 tok/s | SGLang +116% |
| **TTFT (首字延迟)** | 79.42 ms | 102.65 ms | SGLang 快 23% |
| **ITL (token 间延迟)** | 6.03 ms | 7.14 ms | SGLang 快 16% |

## 核心技术差异

### SGLang
- **核心创新：RadixAttention**
  - 基于 radix tree 的 KV cache 管理
  - 自动发现并复用请求间的共享前缀
  - 无需手动配置
- **适用场景**：多轮对话、DeepSeek 类模型、高吞吐场景
- **部署规模**：全球 400,000+ GPU，xAI (Grok 3)、Microsoft Azure 使用

### vLLM
- **核心创新：PagedAttention**
  - KV cache 类似虚拟内存的页式分配
  - 内存浪费从 60-80% 降至 <4%
  - 同硬件支持 2-4x 更多并发请求
- **适用场景**：批量处理、兼容性优先、内存受限场景
- **起源**：UC Berkeley Sky Computing Lab

## 选型建议

| 场景 | 推荐引擎 | 理由 |
|------|----------|------|
| 多轮对话/Agent | SGLang | RadixAttention 自动前缀缓存 |
| DeepSeek 类模型 | SGLang | 官方优化支持 |
| 高吞吐生产 | SGLang | +29% 吞吐量 |
| 内存受限 | vLLM | PagedAttention 内存效率 |
| 兼容性优先 | vLLM | 生态成熟，社区广泛 |
| 批量推理 | vLLM | 批处理优化 |

## 2026 年趋势

- **DeepSeek-V3 发布后**：SGLang 和 vLLM 性能差距缩小
- **竞争焦点**：DeepGEMM、MLA 等优化技术
- **混合部署**：部分场景可结合两者优势

## 标签

`#SGLang` `#vLLM` `#LLM推理` `#RadixAttention` `#PagedAttention` `#性能对比`

---
*生成时间：2026-05-19 | 来源：web_search + browser_extract*


---
## 相关笔记
- [A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研](./2026-05-16-A股量化策略回测框架对比-backtrader-vs-vnpy-vs-自研.md)
- [simulated-vs-live-trading-differences](./2026-05-16-simulated-vs-live-trading-differences.md)
