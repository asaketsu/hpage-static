# Hermes 个人知识管理 RAG 方案（远飞哥）

- 📅 2026-05-05
- ⭐ 3/5 — 实战数据有参考价值，技术方案我们已有更好替代
- 🏷️ #RAG #知识管理 #Ollama #ChromaDB #Hermes #向量检索
- 📰 远飞哥 / 微信公众号「飞哥的技术与烟火」
- 🔗 https://mp.weixin.qq.com/s/KJcGq1VdPaHpKdXErjI-LQ

## 摘要

作者在 Hermes Agent 上搭建本地 RAG 系统：Ollama（qwen3-embedding:4b）做向量化，ChromaDB 存储，Python 脚本实现增量更新和语义查询。核心目标是"用自然语言问出自己写过的一切笔记"。45天使用后，知识查找耗时从18分钟降到42秒，"这个我写过"的命中率从40%升到89%。

## 核心内容

**架构决策：本地运行 + 增量更新 + 语义搜索**

本地运行（Ollama + ChromaDB 全在本机，数据不出机器）。增量更新（只向量化改动文件，相对路径做 ID 去重覆盖而非新增）。统一查询入口（Obsidian 和独立 wiki 都走同一个 query-wiki.py）。语义而非关键字（搜"怎么抗风险"能匹配到"杠铃策略""反脆弱"）。

**笔记预处理（clean_markdown）**

去掉 YAML frontmatter（元数据不该被搜索匹配）。去掉 [[wikilinks]] 但保留文字（搜内容不是搜链接语法）。去掉图片和 URL。保留纯文本做向量化。

**Ollama Embedding API 注意事项**

返回格式是 `{"embeddings": [[0.1, 0.2, ...]]}` 不是 `{"embedding": {...}}`，取值用 `result["embeddings"][0]`。这个坑容易踩。

**45天使用数据**

知识查找耗时从18分钟降到42秒。重复内容产出从每周3.2次降到接近0。"这个我写过"命中率从40%升到89%。意外收益：倒逼笔记整理、知识跨领域串联、写作加速。

**踩坑记录**

Obsidian 有些 GBK 编码笔记，用 chardet 自动检测。短文本（<50字符）向量化被跳过需特殊处理。向量数据库过大（10W字符1000+笔记）查询变慢，可换小模型（1.5b 快3倍精度差8%）或定期清理。

## 🔍 借鉴点

增量更新用相对路径做 ID 去重 → 简洁有效，我们的 rag-index-rebuild skill 可参考此模式
Ollama embedding API 返回 embeddings[0] 不是 embedding → 如启用 Ollama RAG 需注意
n_results=3 作为查询甜点值 → 太多干扰太少遗漏，值得记住
clean_markdown 预处理模式（去 frontmatter/wikilinks/图片） → RAG 索引通用最佳实践

## 🔗 关联性

- 关联已有 skill：rag-index-rebuild — 我们的 RAG 索引重建方案，覆盖更全面
- 关联已有 skill：hybrid-search — 混合语义+关键词搜索，比纯向量方案更鲁棒
- 关联工具：Ollama — 我们有但暂不常驻（8GB 易卡死），未来离线场景可启用
- 关联工具：ChromaDB — 本地向量库，轻量但不如云端方案灵活

## 💡 启发

知识管理的终点不是整理，是让知识自己开口说话——这个理念与我们的笔记系统方向一致。但本地 RAG 在 Jetson 8GB 设备上资源紧张，当前我们的 hybrid-search + skill 索引方案更实际。未来如果 Ollama 常驻或设备升级，可以考虑更重的本地 RAG。

作者提到"倒逼笔记整理"是个有价值的副产品——RAG 质量取决于输入质量，这个正向循环值得关注。

## 🔮 预判

短期：本地 RAG 方案在个人知识管理领域会持续流行，Ollama 生态是主要推动力。
中期：Hermes 等 Agent 框架会内置 RAG 能力，手动搭建脚本的需求下降。
长期：知识管理的核心不是技术方案，而是持续记录的习惯和输入质量。

## 相关笔记

- [2026-05-05-Gemini图片风格复刻Prompt工作流](2026-05-05-Gemini图片风格复刻Prompt工作流.md)
