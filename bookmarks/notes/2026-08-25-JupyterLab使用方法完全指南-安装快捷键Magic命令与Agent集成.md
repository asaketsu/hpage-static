# JupyterLab 使用方法完全指南 — 安装/快捷键/Magic 命令/扩展生态/本机 Agent 集成

> **来源**：综合整理——[JupyterLab 官方文档](https://jupyterlab.readthedocs.io/en/stable/user/commands.html)、[Kanaries 安装与启动指南](https://docs.kanaries.net/zh/topics/Python/how-to-start-juypter-lab)、[Dataquest 28 Tips](https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts)、[博客园快捷键速查](https://www.cnblogs.com/luzhanshi/articles/18825342)
> **记录日期**：2026-08-25
> **定位**：数据科学/机器学习探索的交互工作台——Notebook 的进化版（JupyterLab 4.x）

**标签**：#JupyterLab #Notebook #数据科学 #快捷键 #MagicCommands #IPython #LLaMA-Factory对接

---

### 7 模块索引

| 模块 | 对应章节 |
|------|---------|
| tag 标签 | 头部标签行 |
| 出处 | 头部出处行 |
| 内容整理 | 第一~四章（安装/界面/快捷键/Magic） |
| 查询拓展 | 第五章（本机 Agent 集成 + 核心理念） |
| 归纳总结 | 第六章（速查总表） |
| 趋势判断 | 第七章 |
| 关联分析 | 第八章 |
| 拓展应用推荐 | 第九章 |
| 指南分析 | 第十章 |

---

## 一句话总纲

> **JupyterLab 是 Jupyter Notebook 的现代进化：单窗口多面板（Notebook/终端/文件/Markdown/CSV 实时预览）、可拖拽分屏、命令面板驱动，加 IPython Magic 命令（%timeit/%%time/%debug/%store）和扩展生态（Git/LSP/Variable Inspector）。本机场景：数据探索交互工作台 + jupyter-live-kernel skill（hamelnb）让 Agent 以有状态 REPL 方式用同一个内核执行——人机共用一套 Notebook 生态。**

---

## 一、内容整理

### 1.1 安装与启动

```bash
# 安装（两种方式等价）
pip install jupyterlab
conda install -c conda-forge jupyterlab

# 启动（本机 headless 推荐）
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password=''

# 远程访问（SSH 隧道）
ssh -L 8888:localhost:8888 user@remote-server
# 本地浏览器打开 http://localhost:8888
```

**常用启动标志**：`--port` 端口 / `--notebook-dir` 起始目录 / `--no-browser` 不自动开浏览器（服务器场景）。

### 1.2 界面结构

| 区域 | 功能 |
|------|------|
| **左侧边栏** | 文件浏览器（导航/右键新建/拖拽上传）、运行中的内核和终端、命令/扩展管理 |
| **主工作区** | 可缩放/可分割的标签面板——拖标签到边缘即并排分屏（水平或垂直） |
| **启动器 Launcher** | File > New Launcher，选择 Notebook/Console/Terminal 模板 |
| **命令面板** | `Ctrl+Shift+C`（旧）或 `Ctrl+Shift+P`——输入命令名直接执行 |

**分屏工作流**：Notebook + 终端并排（右边装包左边跑代码）、>Notebook 对照另一个 Notebook、Markdown 编辑与预览同屏。

### 1.3 双模式快捷键速查

**两种模式**：命令模式（蓝/灰边框，Esc 进入）<---> 编辑模式（绿边框，Enter 进入）。

| 快捷键（命令模式） | 动作 |
|------|------|
| `Shift+Enter` / `Ctrl+Enter` / `Alt+Enter` | 运行并跳下 / 运行不跳 / 运行并在下方插入 |
| `Y` / `M` | 转 Code / 转 Markdown cell |
| `1`~`4` | 转 Heading 1~4 |
| `A` / `B` | 上方 / 下方插入 cell |
| `C` / `X` / `V` | 复制 / 剪切 / 粘贴 cell |
| `D,D` | 删除 cell |
| `Z` / `Shift+Z` | 撤销 / 重做 |
| `L` | cell 行号开关 |
| `0,0` | 重启内核 |
| `Ctrl+Shift+T` | 重开最近关闭的文档 |
| `Ctrl+S` | 保存 Notebook |

| 快捷键（编辑模式） | 动作 |
|------|------|
| `Tab` | 代码补全 |
| `Shift+Tab` | 函数签名/工具提示 |
| `Ctrl+/` | 注释/取消注释 |
| `Ctrl+Shift+-` | 在光标处拆分为两个 cell |
| `Ctrl+]` / `Ctrl+[` | 缩进 / 取消缩进 |

### 1.4 IPython Magic 命令（生产力核心）

查看全部：`%lsmagic`

| Magic | 功能 | 示例 |
|-------|------|------|
| `%timeit` / `%%time` | 计时（多次 vs 单次） | `%%time` 整 cell 计时；`%timeit func()` 循环计时 |
| `%run` | 执行外部 Python 脚本 | `%run train.py`（可带参数） |
| `%load` | 把外部文件加载进 cell | `%load model.py` |
| `%who` / `%whos` | 查看命名空间变量 | `%whos` 带类型/大小 |
| `%store` | 跨会话保存变量 | `%store model` → 新会话 `%store -r model` |
| `%debug` | 进入事后调试器 | 异常后 `%debug` 即进 pdbtrace |
| `%cd` | 切换工作目录 | 支持书签和历史导航 |
| `%matplotlib inline` | 图内嵌显示 | Notebook 标配 |
| `!` 前缀 | 任意 shell 命令 | `!pip list` / `!nvidia-smi` |

---

## 二、查询拓展

### 2.1 本机 Agent 集成：jupyter-live-kernel skill（hamelnb）

本机已装 `jupyter-live-kernel` skill——Agent 通过 CLI 使用**同一个** Jupyter 内核做有状态迭代：

```bash
# 核心操作（--compact 省 token）
uv run "$SCRIPT" servers --compact            # 查运行中的 server
uv run "$SCRIPT" execute --path scratch.ipynb --code 'x = 42' --compact   # 有状态执行
uv run "$SCRIPT" variables --path scratch.ipynb list --compact            # 查变量
uv run "$SCRIPT" restart-run-all --path nb.ipynb --save-outputs --compact # 全量验证
```

**关键**：kernel 复用 JupyterLab 的 Python 环境——包装进 jupyterlab 工具环境即可（`uv tool install jupyterlab` 场景）。变量/导入跨 execute 调用持久。

### 2.2 与虚拟环境绑定（多内核）

```bash
# 每个项目一个 venv + 注册内核
python -m venv .venv && source .venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=myenv --display-name="My Env"
# JupyterLab 启动器里选 My Env 即用该内核
```

**Docker 可复现**：`jupyter/datascience-notebook` 等官方镜像一键起环境（宿主机映射 8888）。

### 2.3 为什么用它：Notebook 的"白盒迭代"哲学

与"纯 C++ 手写神经网络"系列同构：**Notebook 是"边看结果边改"的 REPL 升级版**——每 cell 的输出立即可见（执行计数 `[1][2][*]`），适合数据探索/ML 实验/API 探索类任务；对比 `execute_code`（一次性脚本）与 terminal（shell 编译），Notebook 在有状态迭代场景胜出。

---

## 三、归纳总结：速查总表

| 场景 | 用哪个 | 一句话 |
|------|--------|--------|
| 数据探索/ML 实验 | **JupyterLab** | 有状态、逐 cell、可视化 |
| 一次性脚本 | execute_code / .py | 无状态、自动化、可进 CI |
| Shell/编译/服务 | terminal | 系统级操作 |
| **本机 Agent 迭代** | jupyter-live-kernel skill | CLI 驱动同一内核 |
| 多人协作 | JupyterHub / notebook 导出 | nbconvert → HTML/PDF |

**核心四连**：`Esc` 进命令模式 → `A/B` 插 cell → `Shift+Enter` 运行 → `%timeit`/`%debug` 检查。

---

## 四、趋势判断

### 趋势 1：JupyterLab 从"个人交互台"走向"Agent 执行后端"

> 依据：本机已落地——jupyter-live-kernel（hamelnb）让 Agent 用 CLI 驱动 Notebook 内核做有状态执行，与 Jupyter AI 扩展（LLM 对话 cell）同向。2026 年的 Notebook 不只是人用，也是 Agent 的"白盒可审计执行环境"（每 cell 输出可查看，比黑盒 until 更可控）。

### 趋势 2：扩展生态 pip 化简化

> JupyterLab 4.x 大部分扩展改 pip 安装（无需 Node.js 编译）——jupyterlab-git/LSP/Variable Inspector 装完即用，扩展门槛大幅降低。

---

## 五、关联分析

| 笔记 | 关系 |
|------|------|
| [Hermes-NotebookLM 知识管理](2026-05-05-Hermes-NotebookLM知识管理自动挡.md) | 文档型知识管理 vs 代码型交互 |
| [AI 科研工具生态](explore/2026-06-05-AI科研工具生态2026-智能化工具链.md) | JupyterLab 是科研工具链核心件 |
| [纯 C++ 手写神经网络](2026-08-25-纯C++手写神经网络-从矩阵乘法到反向传播全拆解.md) | "白盒理解"哲学同源 |
| [SPSS 科研统计](2026-06-01-SPSS科研统计分析与AI结合深入.md) | 统计分析的 Python 侧入口 |

---

## 六、拓展应用推荐

1. **本机团队工作流**：新主题探索先开 scratch.ipynb（Agent 侧），沉淀结论后转正式笔记——与 session 恢复机制互补
2. **微调实验台**：Qwen3-VL 多模态微调 YAML 调参用 Notebook 逐 cell 跑（配合 jupyter-live-kernel 检查中间变量）
3. **飞机结构数据分析**：载荷谱/疲劳试验数据探索用 Notebook + pandas + 可视化，输出图表直接进笔记
4. **扩展安装候选**：`jupyterlab-git`（版本管理）、`jupyterlab-lsp`（代码补全）、`jupyterlab-variableinspector`（变量面板）

---

## 七、指南分析

**质量**：★★★★☆——官方文档准确（命令面板/快捷键/扩展均可验证），Kanaries 中文指南实操性高（安装/启动/SSH 隧道/空白页修复），Dataquest 的 Magic 命令示例清晰。局限：各来源对"命令面板快捷键"表述不一（`Ctrl+Shift+C` vs `Ctrl+Shift+P`，4.x 已统一为 `Ctrl+Shift+C` 打开命令面板），笔记以官方 commands.html 为准。

**故障排除速查**：
| 现象 | 解法 |
|------|------|
| 命令找不到 | pip 装 python 环境而非系统；检查 `jupyter lab --version` |
| 端口冲突 | 换 `--port 8889` |
| kernel 错误/连不上 | 重启内核；重装 ipykernel |
| 空白页面 | 清缓存/换浏览器；`jupyter lab --LabApp.default_url='/lab?reset'` 重置工作区 |


## 相关笔记

- [开源多模态微调实战-Qwen3-VL-2B加LLaMA-Factory全流程](./2026-08-25-开源多模态微调实战-Qwen3-VL-2B加LLaMA-Factory全流程.md) — 同日姊妹篇，JupyterLab 即其微调工作台