# nTop Automate CLI 完整测试文档

- 📅 2026-05-12
- ⭐5/5 — 官方CLI自动化接口，生产级可用
- 🏷️ #nTop #nTopology #增材设计 #CLI自动化 #参数化设计
- 📰 官方文档 + 社区实践
- 🔗 https://learn.ntop.com/courses/330-ntop-automate/

## 摘要

nTop Automate 是 nTop 官方提供的命令行接口，用于在无 GUI 环境下自动化运行 nTop Notebook 工作流。支持 scalar、enum、vector、file path 等多种输入类型，可批量生成设计变体，是 DOE/MDO 集成的标准方案。本文档涵盖完整命令参数、JSON 输入/输出格式、Python 集成模板及测试用例。

## 核心内容

### 一、命令参数全表

```
ntopcl [OPTIONS] <notebook.ntop>

位置参数：
  <notebook.ntop>          要执行的 nTop Notebook 文件路径

选项参数：
  -h, --help               显示帮助信息
  -i <value>               按顺序传入输入参数（仅 scalar/text）
  -j <input.json>          从 JSON 文件读取输入参数（支持所有类型）
  -o <output.json>         将输出结果写入 JSON 文件
  -t                       生成输入 JSON 模板文件（不执行）
  -s                       保存缓存到 GUI 可读格式（调试用）
  -u <email>               用户邮箱（云授权登录）
  -w <password>            用户密码（云授权登录）
  -v <level>               日志详细程度：0=静默, 1=标准, 2=详细
  --version                显示版本号
```

### 二、JSON 输入格式

用 `ntopcl -t notebook.ntop` 自动生成模板：

```json
{
  "inputs": [
    {
      "name": "Beam_Length",
      "type": "scalar",
      "unit": "mm",
      "values": [100.0]
    },
    {
      "name": "Beam_Width",
      "type": "scalar",
      "unit": "mm",
      "values": [20.0]
    },
    {
      "name": "Material",
      "type": "enum",
      "values": ["Titanium"]
    },
    {
      "name": "Enable_Lattice",
      "type": "boolean",
      "values": [true]
    },
    {
      "name": "Load_Direction",
      "type": "vector",
      "values": [[0.0, 0.0, -1.0]]
    },
    {
      "name": "Reference_Point",
      "type": "point",
      "values": [[0.0, 0.0, 0.0]]
    },
    {
      "name": "Import_File",
      "type": "file path",
      "values": ["C:/models/part.step"]
    },
    {
      "name": "Design_Note",
      "type": "text",
      "values": ["Test variant A"]
    },
    {
      "name": "Iteration_Count",
      "type": "integer",
      "values": [5]
    }
  ]
}
```

### 三、JSON 输出格式

```json
{
  "outputs": [
    {
      "name": "Mass",
      "type": "scalar",
      "value": 42.7,
      "unit": "g"
    },
    {
      "name": "Max_Stress",
      "type": "scalar",
      "value": 312.5,
      "unit": "MPa"
    },
    {
      "name": "Safety_Factor",
      "type": "scalar",
      "value": 1.8
    },
    {
      "name": "Volume_Fraction",
      "type": "scalar",
      "value": 0.35
    },
    {
      "name": "Export_Path",
      "type": "file path",
      "value": "C:/output/optimized_part.stl"
    },
    {
      "name": "Lattice_Density_Map",
      "type": "file path",
      "value": "C:/output/density_map.vtk"
    }
  ],
  "status": "completed",
  "execution_time_seconds": 127.4
}
```

### 四、输入类型速查

| type | values 格式 | 示例 |
|------|-------------|------|
| `scalar` | `[float]` | `[100.0]` |
| `integer` | `[int]` | `[5]` |
| `boolean` | `[bool]` | `[true]` |
| `text` | `[string]` | `["variant_A"]` |
| `enum` | `[string]` | `["Titanium"]` |
| `vector` | `[[x,y,z]]` | `[[1.0, 0.0, 0.0]]` |
| `point` | `[[x,y,z]]` | `[[0.0, 0.0, 0.0]]` |
| `file path` | `["path"]` | `["C:/models/part.step"]` |

### 五、Python 集成模板

```python
import subprocess
import json
import os

def run_ntop(notebook_path, params: dict, output_json="output.json", verbose=2):
    """执行 nTop Notebook 并返回结果"""
    
    # 构造输入 JSON
    inputs = []
    for name, value in params.items():
        input_entry = {"name": name}
        
        if isinstance(value, bool):
            input_entry["type"] = "boolean"
        elif isinstance(value, int):
            input_entry["type"] = "integer"
        elif isinstance(value, float):
            input_entry["type"] = "scalar"
        elif isinstance(value, str) and os.path.isfile(value):
            input_entry["type"] = "file path"
        elif isinstance(value, str):
            input_entry["type"] = "text"
        elif isinstance(value, (list, tuple)) and len(value) == 3:
            input_entry["type"] = "vector"
        
        input_entry["values"] = [value] if not isinstance(value, list) else [value]
        inputs.append(input_entry)
    
    input_path = "_ntop_input.json"
    with open(input_path, "w") as f:
        json.dump({"inputs": inputs}, f, indent=2)
    
    # 构造命令
    cmd = ["ntopcl", f"-v{verbose}", "-j", input_path, "-o", output_json, notebook_path]
    
    # 执行
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"nTop 执行失败 (code {result.returncode})")
    
    # 读取输出
    with open(output_json) as f:
        return json.load(f)


# === 使用示例 ===
results = run_ntop(
    notebook_path="C:/ntop/lattice_opt.ntop",
    params={
        "Beam_Length": 100.0,
        "Beam_Width": 20.0,
        "Material": "Ti6Al4V",
        "Enable_Lattice": True,
        "Load_Direction": [0.0, 0.0, -1.0],
        "Import_File": "C:/models/bracket.step",
    }
)

for out in results["outputs"]:
    print(f"  {out['name']}: {out['value']} {out.get('unit', '')}")
```

### 六、批量执行

JSON `values` 支持多值数组，一次调用批量跑多个变体：

```json
{
  "inputs": [
    {
      "name": "Beam_Length",
      "type": "scalar",
      "unit": "mm",
      "values": [80.0, 100.0, 120.0, 150.0]
    },
    {
      "name": "Lattice_Density",
      "type": "scalar",
      "unit": "ratio",
      "values": [0.2, 0.3, 0.4, 0.5]
    }
  ]
}
```

输出对应每个变体的结果数组。

### 七、典型调用流程

```powershell
# 1. 生成输入模板
ntopcl -t my_notebook.ntop
# → 生成 my_notebook_inputs_template.json

# 2. 编辑模板，填入实际参数
notepad my_notebook_inputs_template.json

# 3. 执行并获取输出
ntopcl -v2 -j my_notebook_inputs.json -o results.json my_notebook.ntop

# 4. 查看结果
type results.json
```

### 八、已知坑点

| 坑 | 解法 |
|----|------|
| `-i` 传参必须严格按 Notebook 输入顺序 | 用 `-j` JSON 方式，靠 name 匹配，不怕顺序 |
| scalar 传参不带单位可能报错 | 加单位 `"100.0 mm"` 或用 JSON 的 `unit` 字段 |
| 路径用反斜杠可能解析失败 | 统一用正斜杠 `C:/models/` |
| 大型 Notebook 执行超时 | Python 调用设 `timeout=3600` 或更长 |
| License 本地锁死 | 云授权用 `-u -w`，或确保本机有浮动 License |
| 输出文件被覆盖 | 每次 `-o` 指定不同文件名 |

### 九、测试用例清单

| # | 用例 | 输入方式 | 预期结果 |
|---|------|----------|----------|
| 1 | 基础执行 | `-j` JSON 文件 | 正常生成输出 JSON |
| 2 | 模板生成 | `-t` | 生成正确的输入模板 |
| 3 | 详细日志 | `-v2` | 输出完整执行日志 |
| 4 | 批量变体 | `values` 多值数组 | 每个变体都有独立输出 |
| 5 | 云授权登录 | `-u -w` | 成功认证并执行 |
| 6 | 错误处理 | 无效参数 | 返回非零 exit code + stderr |
| 7 | 文件路径输入 | `file path` 类型 | 正确读取 STEP/STL 文件 |
| 8 | 向量/点输入 | `vector`/`point` 类型 | 正确解析三维坐标 |
| 9 | 布尔/枚举输入 | `boolean`/`enum` 类型 | 正确传递开关和选项 |
| 10 | 输出文件生成 | `-o` 指定路径 | 生成 STEP/STL 等几何文件 |

## 🔍 借鉴点

- **JSON 模板自动生成** → 先用 `-t` 生成模板再编辑，避免手动编写格式错误
- **Python 胶水层** → 用 `run_ntop()` 函数封装，批量循环时只需改 params 字典
- **values 数组批量** → 一次调用跑多个变体，比 Python 循环更省 License 开销
- **`-s` 调试模式** → 保存缓存到 GUI 可读格式，验证输入参数是否正确

## 🔗 关联性

- 关联已有 skill：[[productivity/officecli]] — 类似 OfficeCLI 的 CLI 自动化模式
- 关联技术栈：[[devops/cronjob]] — nTop 批量执行可接入 cron 定时任务
- 关联技术栈：[[mlops/evaluation]] — 批量变体输出可用于 DOE 实验设计评估

## 💡 启发

- nTop Automate 的 JSON 输入/输出模式是典型的 **数据驱动设计** 范式，与参数化 CAD 的通用接口模式一致（如 FreeCAD 的 `FreeCADCmd`、Fusion 的 API）
- 批量执行时 `values` 数组的并行度取决于 nTop License 的并发槽位，实际测试需确认 License 类型
- 输出中的 `execution_time_seconds` 可用于性能监控和瓶颈分析

## 🔮 预判

- nTop 未来版本可能增加 **并行批量执行** 原生支持（当前靠 Python 循环或 values 数组）
- 云授权模式 `-u -w` 适合 CI/CD 流水线集成，未来可结合 Jenkins/GitHub Actions
- 与 DOE 工具（如 optiSLang、ModeFrontier）的集成场景会增加，CLI 接口是标准桥梁

## 相关笔记

- [[2026-05-12-OfficeCLI 自动化集成]] - Office 文档自动化流水线
- [[2026-05-12-cronjob 批量任务调度]] - 定时任务与批处理
