# Blender 零成本生成三周期极小曲面（TPMS）晶格

> 来源：聚友三维智造实验室（微信公众号）
> 链接：https://mp.weixin.qq.com/s/Z-52MtHX8x2Un578DMa89w

# 一、什么是TPMS？

**三周期极小曲面（Triply Periodic Minimal Surface, TPMS）**是一类在三维空间中周期性重复、平均曲率为零的数学曲面。它们广泛存在于自然界中——蝴蝶翅膀的虹彩结构、海胆骨骼、昆虫翅膀的气管网络，都是 TPMS的杰作。

### 常见的TPMS类型

| **Gyroid (G)** | cos(x)sin(y) + cos(y)sin(z) + cos(z)sin(x) | 双连续、各向同性、强度最优 |
| **Schwarz P (Primitive)** | cos(x) + cos(y) + cos(z) | 简单立方对称、易于制造 |
| **Schwarz D (Diamond)** | sin(x)sin(y)sin(z) + sin(x)cos(y)cos(z) + cos(x)sin(y)cos(z) + cos(x)cos(y)sin(z) | 金刚石结构、高孔隙率 |
| **Neovius** | 3(cos(x)+cos(y)+cos(z)) + 4cos(x)cos(y)cos(z) | 复杂连通、高比表面积 |

### TPMS 的应用领域

•**航空航天**：轻量化晶格填充结构，减重30-50%

•**生物医学**：骨植入物多孔支架，促进骨长入

•**热管理**：换热器、散热器，增大换热面积

•**声学**：吸声材料、隔声结构

•**催化**：高比表面积催化剂载体

## 二、为什么选择Blender？

Blender作为一款开源免费的三维创作软件，为科研人员和工业设计师提供了零成本的强大工具。其程序化生成能力支持参数化驱动，只需调整一个参数，即可一键改变晶格密度、尺寸和形态。从建模到仿真、从渲染到 3D打印，Blender提供了一站式完整工作流。庞大的全球社区贡献了丰富的教程、插件和资产库，而内置的 Python API则实现了与 NumPy、SciPy等科学计算生态的无缝衔接。

## 三、Blender生成TPMS方法比较

## 方法一：原生几何节点生成TPMS

Blender的**几何节点（Geometry Nodes）**支持**体积（Volume）**和**Marching Cubes**，可直接生成TPMS。

### 方法二：Sverchok 插件生成 TPMS

**Sverchok**是Blender的节点式参数化建模插件，灵感来自Grasshopper，采用Python生态，更适合数学密集型生成。

### 两种生成路径对比

| 维度 | 几何节点 | Sverchok |
| **学习曲线** | 较陡，需理解体积/场概念 | 中等，Python 友好者更易上手 |
| **性能** | Blender 原生优化，GPU 加速潜力 | 依赖Python，大数据量较慢 |
| **灵活性** | 受限于Blender 节点库 | 无限，完整Python+NumPy+SciPy |
| **数学表达** | 节点连线，视觉化但冗长 | 直接代码，简洁精确 |
| **Marching Cubes** | 内置[体积→网格] | 需外接scikit-image 或自实现 |
| **参数化UI** | 原生支持，拖动调节 | 需自定义面板 |
| **与Blender 集成** | 完美，实时预览 | 良好，需手动刷新 |
| **版本稳定性** | 随Blender 更新，变化大 | 相对稳定，社区维护 |
| **应用场景** | 快速原型、视觉展示 | 数学研究、复杂过渡、多晶格混合 |

## 四、进阶资源

## •**Sverchok官方文档**：

## https://github.com/nortikin/sverchok

## •**TPMS 数学原理**：

https://en.wikipedia.org/wiki/Triply\_periodic\_minimal\_surface

•**Blender几何节点教程**：

https://docs.blender.org/manual/en/latest/modeling/geometry\_nodes/index.html

Blender凭借其开源、免费、强大的特性，已成为 TPMS 晶格生成的重要工具。无论是追求原生集成的**几何节点**，还是偏爱数学表达的**Sverchok**，都能实现从概念到实物的完整工作流。

**程序化生成**的核心价值在于：一次搭建，无限复用。调整一个参数，整个晶格结构随之更新——这正是参数化设计的魅力所在。

*“数学是自然的语言，而Blender是翻译它的画笔。”*

---

## 个人批注

TPMS（三周期极小曲面）是3D打印轻量化设计的核心技术之一。Blender 作为零成本工具生成 TPMS 晶格，降低了科研和工程门槛。两种路径各有优劣：
- **几何节点**：GPU 加速、实时预览，适合快速原型
- **Sverchok 插件**：完整 Python 生态，适合复杂数学表达和多晶格混合

关键知识点：
1. TPMS 本质是三维周期性重复、平均曲率为零的数学曲面，广泛存在于自然界
2. 四种常见类型：Gyroid（各向同性）、Schwarz P（简单立方）、Schwarz D（金刚石）、Neovius（高比表面积）
3. 应用领域：航空航天减重30-50%、骨植入物支架、换热器、吸声材料、催化剂载体
4. 核心价值：参数化驱动，调一个参数就能改变晶格密度/尺寸/形态


## 相关笔记
- [[2026-05-05-Claude-MCP直连Fusion-Blender-AI操控工业设计]] (关键词: blender)
- [[2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析]] (关键词: blender)
