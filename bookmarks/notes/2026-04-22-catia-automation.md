　　
# catia-automation

## 项目信息
构型类型：Python
功能标签：工具、Python

## 项目简介
　　# catia-automation Fluent Python API for CATIA V5 automation, built on [pycatia](https://github.com/evereux/pycatia). --- ## Overview `catia-automation` wraps the pycatia COM interface in a clean, chainable Python API. Instead of writing hundreds of lines of low-level COM calls, you can create parts, apply features, and export files with a single fluent expression. ```python from catia_automation import CATIADesigner with CATIADesigner() as d:     d.create_part("Bracket") \      .box(100,



## 相关笔记
- [[catia_automation]] (关键词: automation, catia)
- [[2026-04-22-CATIA-接入-AI-大模型原理]] (关键词: catia)
- [[2026-05-12-网络安全-security-automation]] (关键词: automation)
