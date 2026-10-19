# Scrapling 自适应网页解析库实战评测

> 号称网站改版自动适应、比 BeautifulSoup 快 784 倍的 Python 网页解析库。
> 59,873 Star · 作者 D4Vinci · MIT License
> 仓库：https://github.com/D4Vinci/Scrapling
> 文档：https://scrapling.readthedocs.io/

## 一、核心卖点

- **自适应解析**：网站改版后自动重新定位元素（换 class、调层级仍能匹配）
- **反检测绕过**：StealthyFetcher 内置 TLS 指纹伪装，自动完成 Cloudflare 验证
- **命令行工具**：`scrapling extract get 'url' output.md` 零代码提取
- **Spider 框架**：内置并发爬虫，支持 Ctrl+C 暂停/恢复
- **MCP Server**：AI 工具直接调用，网页内容先清洗再传 AI 减少 Token
- **极致性能**：解析速度基准 2.02ms，BS4 慢 784 倍、PyQuery 慢 12 倍

## 二、自适应原理

选取元素时不仅记录 CSS 选择器，还记录**多维特征指纹**：

| 维度 | 说明 |
|------|------|
| 文本内容 | 元素内文字 |
| 属性值 | id、class、data-* 等 |
| DOM 结构位置 | 在树中的层级路径 |
| 相邻元素关系 | 前后兄弟、父级子级 |
| 样式特征 | 计算后的视觉属性 |

改版后用智能相似度算法在所有候选元素中匹配最像原始目标的那一个。

### 实测自适应覆盖度

| 改版幅度 | 结果 |
|----------|------|
| class 名变更 | ✅ 通过 |
| DOM 层级调整（3 层变化） | ✅ 通过 |
| 页面完全重写 | ❌ 失败 |

> 覆盖率约 70-80%，中小幅度改版有效，全面重构无法挽救。

## 三、性能基准

| 库 | 解析耗时 | 相对速度 |
|----|---------|---------|
| **Scrapling** | **2.02ms** | **1.0x** |
| Parsel / Scrapy | 2.04ms | 1.01x |
| Raw Lxml | 2.54ms | 1.26x |
| PyQuery | 24.17ms | ~12x |
| Selectolax | 82.63ms | ~41x |
| BeautifulSoup + Lxml | 1584ms | ~784x |
| BS4 + html5lib | 3392ms | ~1679x |

## 四、6 大核心能力详解

### 1. 自适应解析

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('https://example.com', headless=True)

# 首次：记录特征指纹
products = page.css('.product', auto_save=True)

# 改版后：自动匹配
products = page.css('.product', adaptive=True)
```

### 2. Cloudflare 绕过

```python
page = StealthyFetcher.fetch(
    'https://nopecha.com/demo/cloudflare',
    headless=True,
    solve_cloudflare=True
)
```

实测：10 次请求，10 次成功，全程约 8 秒。

### 3. CLI 命令行

```bash
# 提取为 Markdown
scrapling extract get 'https://example.com' content.md

# 按 CSS 选择器提取
scrapling extract get 'https://example.com' content.txt \
  --css-selector '#main-content' --impersonate 'chrome'

# 带浏览器验证
scrapling extract stealthy-fetch 'https://example.com' \
  output.html --css-selector '#data' --solve-cloudflare
```

### 4. Spider 框架

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
result.items.to_json("quotes.json")
```

特性：Ctrl+C 暂停恢复、HTTP+浏览器混合会话、流式输出。

### 5. MCP Server

配置后 Claude Desktop / Cursor / Claude Code 等 AI 工具可直接调用。
网页内容先清洗为结构化数据再传 AI，大幅减少 Token。

### 6. 性能

底层基于 Lxml C 扩展，解析速度与 Parsel/Scrapy 同级。

## 五、对比矩阵

| 维度 | Scrapling | Playwright | Scrapy |
|------|-----------|------------|--------|
| 自适应改版 | ✅ 自动 | ❌ 手写 | ❌ |
| 浏览器验证 | ✅ 开箱即用 | ⚠️ 自写 | ❌ |
| CLI 提取 | ✅ 一行 | ❌ | ❌ |
| Spider 框架 | ✅ 内置 | ❌ | ✅ |
| 暂停/恢复 | ✅ | ❌ | ⚠️ 需配置 |
| AI 集成 | ✅ MCP | ❌ | ❌ |
| 典型代码量 | ~5 行 | ~25 行 | ~40 行 |

> 定位：Scrapling = Playwright 浏览器能力 + Scrapy 工程框架 + 自研自适应算法

## 六、已知不足

| 问题 | 说明 |
|------|------|
| 新手门槛 | CLI 降低门槛但 Spider/代理仍需写 Python |
| 自适应非银弹 | 大改版仍失效，需监控脚本状态 |
| 资源消耗 | 每 Chromium 实例 200-500MB 内存 |
| 生态早期 | 核心强但插件不如 Scrapy 丰富 |
| 合规前提 | 仅供教育研究，须遵守 robots.txt |

## 七、5 条实操建议

1. **先 CLI，再 API** — `scrapling extract get` 一条命令试水
2. **自适应从第一天开启** — `auto_save=True` 记录指纹，`adaptive=True` 兜底
3. **大数据量用缓存开发** — Spider `crawldir` 缓存响应，避免重复请求
4. **验证站点加 `network_idle=True`** — 等网络完成再提取，配合 `solve_cloudflare`
5. **遵守 robots.txt** — Spider 自带 `robots_txt_obey` 参数

## 八、适用人群

| ✅ 适合 | ❌ 不适合 |
|---------|----------|
| 被改版折磨的网页自动化开发者 | 偶尔 requests 获取一两个页面 |
| 需要绕过浏览器验证的数据工程师 | 完全不懂 Python |
| AI Agent 需要自动获取网页信息 | 不了解 robots.txt 基本规则 |
| 公开数据研究/学术调研批量采集 | 对性能和内存极度敏感 |
| 想从 Scrapy 迁移到更现代框架的团队 | 深度绑定 Scrapy 中间件生态 |


## 相关笔记
- [[google-fonts-china-direct-access]]
