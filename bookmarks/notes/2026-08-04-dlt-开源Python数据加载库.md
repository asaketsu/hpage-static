# dlt — 开源 Python 数据加载库（ELT）

> **来源**：[github.com/dlt-hub/dlt](https://github.com/dlt-hub/dlt)
> **官网**：[dlthub.com/docs](https://dlthub.com/docs)
> **License**：Apache-2.0
> **Stars**：5.7K · **Forks**：575 · **Language**：Python
> **支持**：Python 3.10–3.14

---

## 一句话定义

> **data load tool (dlt)** — 开源 Python 库，把杂乱的数据源自动加载为结构良好、带类型的 dataset。

核心定位：**它是一个库，不是一个平台。** `pip install` 进现有代码即可，保留你的工作流和其他工具。无黑箱——干净的 Python 接口、人类可读的文件格式、可检视的 schema、无隐藏副作用。

---

## 核心能力速览

| 能力 | 说明 |
|------|------|
| **Extract** | REST API / SQL 数据库 / S3/GCS/Azure 文件 / DataFrame / Arrow，5000+ source |
| **Load** | 20+ 目标（DuckDB / BigQuery / Snowflake / Postgres / Redshift / Databricks / Athena / ClickHouse / Iceberg / Delta …） |
| **Normalize** | 自动推断 schema、类型映射、嵌套数据展开 |
| **Transform** | 内置 Ibis 表达式 → Python 写、SQL 出 |
| **Incremental** | `dlt.sources.incremental` 只加载新/变更行 |
| **Schema Contract** | `evolve` / `freeze` / `discard` 三模式管控表结构漂移 |
| **Credentials** | `secrets.toml` / env vars 自动注入 |
| **LLM 原生** | 从底层为 LLM 和 coding agent 设计，支持 prompt → pipeline 单次生成 |

---

## Quick Start

### 声明式加载 REST API → DuckDB

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# 1. 声明式描述 API
source = rest_api_source({
    "client": {"base_url": "https://pokeapi.co/api/v2/"},
    "resources": [
        {"name": "pokemon", "endpoint": {"path": "pokemon", "params": {"limit": 1000}}},
    ],
})

# 2. 指定目标
pipeline = dlt.pipeline(
    pipeline_name="pokemon",
    destination="duckdb",
    dataset_name="pokemon_data",
)

# 3. Extract → Normalize → Load
print(pipeline.run(source))

# 4. 直接读回 DataFrame
print(pipeline.dataset().pokemon.df())
```

### 任意 Python 可迭代对象 → 表

```python
import dlt

@dlt.resource(table_name="players", primary_key="id", write_disposition="merge")
def players():
    yield {"id": 1, "name": "Magnus", "rating": 2839}
    yield {"id": 2, "name": "Pragg", "rating": 2758}

dlt.pipeline(destination="duckdb", dataset_name="chess").run(players())
```

---

## 数据源（Extract）

### REST API — 声明式描述 + 过滤/映射

```python
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/v1",
        "paginator": {"type": "cursor", "cursor_path": "next_cursor"},
    },
    "resources": [
        {
            "name": "guests",
            "endpoint": {"path": "events/guests"},
            "processing_steps": [
                {"filter": lambda r: r["approval_status"] == "approved"},
                {"map": lambda r: {**r, "email": r["email"].lower()}},
            ],
        },
    ],
})
```

### SQL 数据库 — 直接反射表结构

```python
from dlt.sources.sql_database import sql_database
source = sql_database("mysql+pymysql://user:***@host/db")
```

### 文件（S3/GCS/Azure/本地）

```python
from dlt.sources.filesystem import filesystem, read_csv_duckdb

source = (
    filesystem(bucket_url="s3://my-bucket/data", file_glob="*.csv")
    | read_csv_duckdb()
).with_name("events")
```

### DataFrame & Arrow

```python
import pandas as pd
df = pd.DataFrame({"event": ["dlt summit", "DuckCon"], "signups": [1240, 860]})
dlt.pipeline(destination="duckdb", dataset_name="events").run(df, table_name="events")
```

---

## 目标（Load）— 换一个字符串

同一 resource 跑到任何目标，只需改 `destination` 字符串，dlt 自动处理：

- **Credentials** → `secrets.toml` / env vars 自动注入
- **DDL** → 目标方言的 `CREATE TABLE`
- **Type mapping** → 源类型转目标类型
- **Staging** → 需要时走 S3 / GCS
- **Schema drift** → 运行时 `ALTER TABLE`

```python
pipeline = dlt.pipeline(
    pipeline_name="luma",
    destination="duckdb",       # → snowflake, bigquery, postgres, redshift, databricks,
    dataset_name="luma_data",   #   athena, clickhouse, motherduck, filesystem (S3/GCS/Azure),
)                               #   iceberg, delta, ... and custom reverse-ETL destinations
```

---

## 装饰器声明意图

```python
import dlt

@dlt.resource(
    primary_key="id",
    write_disposition="merge",                       # 按 primary key upsert
    columns={"email": {"x-annotation-pii": True}},   # 类型标注 + 列注释
    schema_contract={"columns": "freeze"},           # 拒绝意外列
)
def events(
    updated_at=dlt.sources.incremental("updated_at"),  # 只加载新/变更行
):
    yield from fetch_events(since=updated_at.last_value)

@dlt.source
def luma(api_key: str = dlt.secrets.value):
    return events(), guests()   # 将多个 resource 放在共享 config/auth 后面
```

### Schema Contract 三模式

| 模式 | 行为 | 应用层 |
|------|------|--------|
| **evolve** | 接受并适配 schema 变化 | tables / columns / data_type |
| **freeze** | 拒绝整条记录 | tables / columns / data_type |
| **discard** | 丢弃有问题的行/列 | tables / columns / data_type |

---

## Dataset API — 读回数据

Pipeline 是持久的。用 `dlt.attach` 按名称重连，以适合你工具的格式读回任何表：

```python
pipeline = dlt.attach(pipeline_name="luma", destination="duckdb", dataset_name="luma_data")

dataset = pipeline.dataset()
dataset.tables               # ['events', 'guests', ...]

guests = dataset.guests      # 惰性 dlt.Relation
guests.df()                  # pandas DataFrame
guests.arrow()               # pyarrow.Table (zero-copy)
guests.to_ibis()             # ibis expression — 惰性、可组合
```

---

## Transform with Ibis — Python in, SQL out

把任何已加载的表提升为 Ibis 表达式，用 Python 组合 group-by / join / window function，dlt 编译为目标方言的 SQL。**不取结果就不执行**：

```python
import ibis

guests = pipeline.dataset().guests.to_ibis()

guests_by_event = (
    guests
    .group_by("event_id")
    .aggregate(n_guests=ibis._.api_id.count())
)

guests_by_event.to_pyarrow()   # 编译为 SQL 并在目标上执行
```

---

## LLM 原生设计

> dlt 及其文档**从底层为 LLM 和 coding agent 设计**。

- 配合 [dlthub.com/context](https://dlthub.com/context) 和 [LLM-native workflow](https://dlthub.com/docs/dlt-ecosystem/llm-tooling/llm-native-workflow)
- 从 prompt 到可运行的 pipeline，跨越 5000+ source，**通常一次就能生成**
- 类型化、声明式原语，让 LLM 能理解和操作

---

## 安装

```sh
pip install dlt

# 按需安装 extras
pip install "dlt[duckdb]"        # 本地 DuckDB 目标
pip install "dlt[bigquery]"      # 或 snowflake, postgres, redshift, databricks, athena, ...
pip install "dlt[s3]"            # 或 gs, az 用于云文件系统
pip install "dlt[sql_database]"  # 从任何 SQL 数据库读取
pip install "dlt[hub]"           # 数据质量、转换、AI
```

---

## 版本管理

`dlt` 遵循 `MAJOR.MINOR.PATCH` 语义化版本：
- `major`：破坏性变更和移除的废弃功能
- `minor`：新功能，有时含自动迁移
- `patch`：bug 修复

建议用兼容版本限定符 `dlt~=1.23.0`（允许 >=1.23.0 且 <1.24.0）。

---

## 适用场景

| 场景 | 为什么用 dlt |
|------|-------------|
| **AI Agent 数据加载** | LLM 原生设计，prompt → pipeline 单次生成 |
| **ELT 管道原型** | Colab / Lambda / Airflow / 本地笔记本，drop-in 即用 |
| **多目标切换** | 换一个字符串，同一代码从 DuckDB 切到 BigQuery |
| **API 数据采集** | 声明式 REST API 描述，自动分页/schema 推断/类型映射 |
| **增量同步** | `dlt.sources.incremental` 只加载新数据 |
| **数据质量管控** | Schema Contract + 列标注 + 数据类型冻结 |

---

## 📎 关键链接

- 📖 文档：[dlthub.com/docs](https://dlthub.com/docs)
- 🏪 5000+ Source：[dlthub.com/workspace](https://dlthub.com/workspace)
- 🤖 LLM Context：[dlthub.com/context](https://dlthub.com/context)
- 💬 Slack 社区：[dlthub.com/community](https://dlthub.com/community)
- 📋 公开路线图：[GitHub Project](https://github.com/orgs/dlt-hub/projects/9)

---

*笔记创建：2026-08-04 · 来源：github.com/dlt-hub/dlt README*


## 相关笔记

- 暂无直接关联笔记（Python 数据加载/ELT 工具，近期笔记库中独立条目）
- [数据治理-data-quality](./2026-05-08-数据治理-data-quality.md) — 数据质量管理方法论，dlt 管线的数据质量保障参考
