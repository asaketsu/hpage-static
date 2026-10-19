# Google Fonts 国内直连使用笔记

## 核心发现

`fonts.googleapis.com` 和 `fonts.gstatic.com` 在国内服务器可以通过代理（`http://192.168.2.2:7890`）正常访问，HTTP 200 响应正常。两个域名均返回有效内容，CSS API 和字体文件下载均无问题。

**注意**：国内裸连（无代理）情况因地区和运营商而异，部分地区 DNS 解析到 Google 北京节点可用，部分地区解析到海外 IP 被墙。我们的服务器走统一代理，所以完全可用。

## 一、基础使用

### HTML 引入方式

```html
<!-- 单个字体，指定字重 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">

<!-- 多个字体合并请求 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=Roboto+Mono:wght@400&display=swap" rel="stylesheet">
```

### CSS 引入方式

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
```

### CSS 使用

```css
body {
    font-family: 'Noto Sans SC', sans-serif;
}

h1 {
    font-family: 'Roboto Mono', monospace;
    font-weight: 700;
}
```

## 二、CSS2 API（推荐）

Google Fonts v2 API 比 v1 更灵活，支持可变字体轴范围：

```
https://fonts.googleapis.com/css2?family=<字体名>:<轴>=<值>&display=swap
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `family` | 字体名，空格用`+`替代 | `Noto+Sans+SC` |
| `wght` | 字重，支持范围写法 | `wght@400;700` 或 `wght@100..900` |
| `ital` | 斜体，0或1 | `ital,wght@0,400;1,700` |
| `display` | 加载策略 | `swap`（推荐）、`block`、`fallback`、`optional` |
| `subset` | 字体子集 | `subset=chinese-simplified` |

### display 参数对比

| 值 | 行为 | 适用场景 |
|----|------|---------|
| `swap` | 先用系统字体，加载完切换 | ✅ 最佳实践，推荐 |
| `fallback` | 短时间阻塞，超时用系统字体 | 需要统一视觉的场景 |
| `optional` | 浏览器决定，可能不下载 | 弱网环境 |
| `block` | 阻塞渲染直到字体加载 | 不推荐，白屏风险 |

### 可变字体范围语法

```
# 指定字重
wght@400;700

# 范围（可变字体）
wght@100..900

# 多轴组合
ital,wght@0,400;0,700;1,400
```

## 三、常用中文/等宽字体推荐

### 中文

| 字体 | 字重范围 | 特点 |
|------|---------|------|
| `Noto Sans SC` | 100-900 | 思源黑体，Google 主推中文无衬线 |
| `Noto Serif SC` | 200-900 | 思源宋体，中文衬线 |
| `LXGW WenKai` | 300-700 | 霞鹜文楷，手写风格 |
| `Ma Shan Zheng` | 400 | 马善政楷书，书法风格 |

### 英文等宽（适合代码）

| 字体 | 字重 | 特点 |
|------|------|------|
| `Roboto Mono` | 100-700 | Google 官方等宽 |
| `JetBrains Mono` | 100-800 | 连字支持，开发者最爱 |
| `Fira Code` | 300-700 | 连字丰富 |
| `Source Code Pro` | 200-900 | Adobe 开源 |

## 四、Material Icons / Symbols

图标字体也走 Google Fonts，同一个域名：

```html
<!-- Material Symbols（推荐新版） -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">

<!-- Material Icons（旧版） -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
```

```html
<span class="material-symbols-outlined">home</span>
<span class="material-icons">settings</span>
```

## 五、性能优化建议

### 减少请求体积

```
# 只请求需要的字重和子集
css2?family=Noto+Sans+SC:wght@400;700&display=swap

# 而不是
css?family=Noto+Sans+SC  ← 全部字重，文件巨大
```

### 预连接

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

### 合并请求

多个字体写在一个 URL 里，减少 HTTP 请求：

```
css2?family=FontA:wght@400&family=FontB:wght@700&display=swap
```

### 按需子集

中文动辄数 MB，Google 会根据浏览器 Accept-Language 自动返回对应子集。也可以手动指定：

```
css2?family=Noto+Sans+SC&subset=chinese-simplified
```

## 六、国内备用方案

如果目标用户无代理，可用以下镜像替换域名：

| 原域名 | 镜像 | 状态 |
|--------|------|------|
| `fonts.googleapis.com` | `fonts.lug.ustc.edu.cn` | ✅ 中科大维护 |
| `fonts.googleapis.com` | `fonts.font.im` | ✅ 可用 |
| `fonts.googleapis.com` | `fonts.geekzu.org` | ⚠️ 不确定 |
| `fonts.gstatic.com` | `fonts-gstatic.lug.ustc.edu.cn` | ✅ 中科大维护 |

替换方法：只需把 URL 中的域名替换即可，路径不变。

### 自托管方案（最稳定）

如果对稳定性要求高，可以下载字体文件到本地服务器：

```bash
# 下载 CSS
curl -s "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" -o fonts.css

# 从 CSS 中提取字体 URL 并下载
grep -oP 'https://fonts\.gstatic\.com/[^)]+' fonts.css | while read url; do
    filename=$(basename "$url")
    curl -s "$url" -o "fonts/$filename"
    sed -i "s|$url|./fonts/$filename|g" fonts.css
done
```

## 七、实战示例

### 笔记/文档 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Sans SC', sans-serif; }
        code, pre { font-family: 'JetBrains Mono', monospace; }
        h1, h2, h3 { font-weight: 700; }
    </style>
</head>
```

### Python 生成的 HTML 中使用

```python
FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">'

html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
{FONT_LINK}
<style>
body {{ font-family: 'Noto Sans SC', sans-serif; background: #fafafa; }}
</style>
</head><body>...</body></html>"""
```

## 八、注意事项

1. **HTTPS 必须** — Google Fonts 已全面强制 HTTPS，HTTP 请求会被 301 重定向
2. **字体名中的空格用 `+` 替代** — `Noto Sans SC` → `Noto+Sans+SC`
3. **中文文件较大** — Noto Sans SC 完整版约 7MB，Google 会按子集拆分，但单个字重仍有数百 KB
4. **font-display: swap** — 几乎总是应该加上，避免白屏
5. **preconnect** — 加在 `<head>` 最前面，提前建立连接减少延迟
6. **版本稳定性** — Google Fonts 的 URL 是永久链接，不会变更，但字体版本会静默更新


## 相关笔记
- [[2026-04-05-Google-Gemma4-open-source]] (关键词: google)
