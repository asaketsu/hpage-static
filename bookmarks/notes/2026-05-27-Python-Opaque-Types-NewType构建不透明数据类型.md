# Python Opaque Types：NewType 构建不透明数据类型

来源：Deciphering Glyph (Glyph Lefkowitz)
链接：https://blog.glyph.im/2026/05/opaque-types-in-python.html
日期：2026-05-27
评分：⭐4/5
标签：#Python #类型系统 #API设计 #NewType #封装
关联：[Python 3.15 隐藏特性](2026-05-22-Python315-隐藏特性-被大新闻掩盖的实用改进.md) [Python Union Types](2026-05-24-net-11-c#-15-union-types.md)

## 核心问题

设计 Python 库时，如何暴露一个复杂配置对象，同时：
- 不暴露内部实现和构造函数
- 只允许通过受控的工厂方法创建
- 类型检查器能正确配合

## 解决方案：NewType + 私有类 + 公开工厂函数

```python
from dataclasses import dataclass
from typing import Literal, NewType

@dataclass
class _RealShipOpts:
    _speed: Literal["fast", "normal", "slow"]

ShippingOptions = NewType("ShippingOptions", _RealShipOpts)

def shipFast() -> ShippingOptions:
    return ShippingOptions(_RealShipOpts("fast"))

def shipNormal() -> ShippingOptions:
    return ShippingOptions(_RealShipOpts("normal"))
```

### 为什么有效

1. `_RealShipOpts` 以下划线开头 → 私有约定，IDE/类型检查器不推荐外部使用
2. `NewType` 创建一个公开类型别名 → 用户在类型注解中使用
3. 工厂函数（`shipFast`等）是唯一的构造入口 → 完全控制 API 表面
4. 未来内部实现可以任意演进，不影响公开接口

## 与其他方案的对比

| 方案 | 暴露构造函数 | 类型检查友好 | 演进性 |
|------|------------|------------|--------|
| 直接暴露 dataclass | ✅ 是 | ✅ | ❌ 差 |
| `__init__` 抛异常 | ✅ 是（误导） | ❌ | ❌ |
| `typing.NewType` 方案 | ❌ 否 | ✅ | ✅ 优 |

## 实际演进场景

初始版本只有 speed，后续可以无缝添加：
- carrier 选择
- 签名要求
- 跟踪选项
- 保价金额

所有内部变更对消费者透明——工厂函数签名不变。

## ⚡ 借鉴进化点

1. **Hermes Config 类型安全**：当前 Hermes 的 config.yaml 配置可以借鉴 NewType 模式，将复杂配置对象（如 provider config、model config）封装为不透明类型，只暴露验证过的工厂方法，防止用户传入无效配置。

2. **Skill 接口设计原则**：SKILL.md 的 frontmatter 定义本质是一种"约定接口"。可以用 NewType 思路——只暴露用户需要操作的字段，内部状态（skill_dir、linked_files）通过受控方法访问，减少用户犯错空间。

3. **Python 库 API 设计模式库**：将此模式归档为 Python 库设计参考，特别是 `typing.NewType` + 私有类 + 工厂函数的三件套组合，适用于任何需要"受控构造"的场景（配置对象、权限令牌、请求构建器）。

## 相关笔记
- [[2026-05-22-Python315-隐藏特性-被大新闻掩盖的实用改进]]
