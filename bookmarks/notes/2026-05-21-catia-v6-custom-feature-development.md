# CATIA V6 自定义特征开发全链路：从 OSM 声明到会话集成

来源：微信公众号（安亭吴彦祖）
链接：https://mp.weixin.qq.com/s/tljTmc0a1FA52TEe0vuPew
日期：2026-05-21
评分：⭐4.5/5（罕见的 V6 自定义特征中文深度教程，从声明到部署的完整链路）
标签：#CATIA #V6 #自定义特征 #OSM #FeatureModelerExt #CAD二次开发 #PLM
关联：[2026-05-21-catia-vba-batch-body-processing](2026-05-21-catia-vba-batch-body-processing.md)

---

## 摘要

一篇系统性的 CATIA V6 自定义特征开发教程。文章将整个开发链路拆解为三层：声明层（OSM 定义 StartUp/协议/扩展元数据）、模型层（FeatureModelerExt Facade API 实例化/扩展/更新/删除）、会话层（可视化/导航/编辑/Provider 接入交互环境）。涵盖了从 Catalog 创建、Credentials 注册、base feature 与 extension feature 两条路线，到最终的规格树/可视化/上下文菜单集成的完整流程。

## 核心内容

### 四个核心对象

| 对象 | 作用 | 类比 |
|------|------|------|
| StartUp | 特征模板（定义属性/协议） | 类定义（Class） |
| CATfct Catalog | 承载 StartUp 的目录文件 | 类库（Assembly） |
| Applicative Container | 特征实例的落地容器 | 对象池/命名空间 |
| Feature Instance | 运行时创建的具体特征 | 对象实例 |

### V6 vs 旧方式的关键变化

1. **Catalog 管理**：不再建议通过旧式 C++ 目录 API 直接创建/升级，统一走 OSM + `CATfctEditorAssistant`
2. **运行时访问**：不再手工打开 Catalog 查 StartUp，围绕 Facade API（CATFmCredentials / CATFmStartUpFacade / CATFmFeatureFacade / CATFmContainerFacade）
3. **对象环境**：以 PLM Representation / Technological Representation 为中心，容器/导航/可视化/交互需放在完整产品上下文

核心思路：**先声明式定义，再运行时实例化，再按场景挂行为**。

### 两条开发路线

**Base Feature 路线**（从零定义新特征）：
```
OSM 定义 StartUp → CATfctEditorAssistant 生成 Catalog → Credentials 注册 →
CATFmStartUpFacade.InstantiateIn() 实例化 → 封装业务接口 → 接入行为/可视化/交互
```

**Extension Feature 路线**（给已有特征追加业务语义）：
```
OSM 用 #extension 定义扩展 StartUp → 指定 Extends/Container →
CATFmFeatureFacade.AddExtension() 挂载 → 初始化参数和关联 → 补行为层
```

### 开发步骤（10 步）

**Step 1: Catalog 管理**

```bash
# 创建空 Catalog
CATfctEditorAssistant -create-new-catalog -catalog-name MyCatalog.CATfct \
  -with-client-id MyClientId -into-directory <output-dir>

# 从已有 Catalog 导出 OSM（反向工程）
CATfctEditorAssistant -describe-as-osm -catalog-name MyCatalog.CATfct \
  -with-client-id MyClientId -as MyCatalog.osm -into-directory <output-dir>

# 根据 OSM 升级 Catalog
CATfctEditorAssistant -update-catalog -catalog-name MyCatalog.CATfct \
  -with-client-id MyClientId -with-osm MyCatalog.osm -into-directory <output-dir>
```

关键原则：**维护 OSM，不是维护 CATfct**。CATfct 是生成产物。

**Step 2: OSM 中定义 StartUp**

Base Feature 示例：
```
document `MyCatalog.CATfct` {
  container CATFeatCont #root {
    feature MyPoint #startup {
      double X #in
      double Y #in
      double Z #in
      #interface::CATIUseEntity = metadata_CommonProtocol
    }
  }
}

metadata metadata_CommonProtocol {
  `implementInterface` = true
  `implementCopyPasteAspect` = true
  `implementDeleteAspect` = true
  `implementUpdateAspect` = true
}
```

三个关键标记：
- `#startup`：声明为可实例化模板
- `#in`：区分 specification 属性
- `#interface::CATIUseEntity`：接入通用协议

Extension Feature 示例：
```
feature `MyLineExtension` #startup #extension {
  component Param1 #in
  specobject BaseLine #in #auto_update
  #creation::parameter = metadata_Extension
  #interface::CATIUseEntity = metadata_CommonProtocol
}

metadata metadata_Extension {
  IsLocal = true
  Extends = ["MyLine"]
  Container = "MyExtensionCont"
  ContType = "MyExtensionCont"
}
```

四个要点：
- `#extension`：依附在 base feature 上，非独立特征
- `Extends`：指定可扩展的基础特征列表
- `Container` / `ContType`：指定扩展实例的落地容器
- `#auto_update`：base feature 变化时自动触发扩展更新

**Step 3: NLS 资源文件**

`CNext/resources/msgcatalog` 下的 CATNls：
```
MyPoint="Point";
MyLineExtension="Relimited Line";
```

没有 NLS，界面显示的晚绑定类型名会非常生硬。

**Step 4: Credentials 注册**

```cpp
static HRESULT RetrieveCredentials(CATFmCredentials*& credentials) {
    static CATFmCredentials uniqueCredential;
    CATUnicodeString clientId("MyClientId");
    CATUnicodeString partnerId("MyPartner");
    
    uniqueCredential.RegisterAsApplicationBasedOn(CATFmFeatureModelerID, partnerId);
    uniqueCredential.RegisterAsCatalogOwner("MyCatalog", clientId);
    
    credentials = &uniqueCredential;
    return S_OK;
}
```

关键：clientId 必须与 CATfctEditorAssistant 生成时一致。涉及多个 Catalog 则每个都要注册。

**Step 5: 实例化 Base Feature**

```cpp
CATFmContainerFacade containerFacade(*credentials, iContainer);
CATFmStartUpFacade startUpFacade(*credentials, "`MyPoint`@`MyCatalog.CATfct`");

CATFmFeatureFacade featureFacade;
startUpFacade.InstantiateIn(containerFacade, featureFacade);

featureFacade.QueryInterfaceOnFeature(IID_IMyPoint, (void**)&oPoint);
```

三 Facade 职责：
- **ContainerFacade**：装到哪里去
- **StartUpFacade**：按哪个模板装
- **FeatureFacade**：装出来后怎么操作

**Step 6: 创建 Extension Feature**

```cpp
CATFmFeatureFacade baseFacade(*credentials, iBaseFeature);
CATFmFeatureFacade extensionFacade(*credentials);

baseFacade.AddExtension("`MyLineExtension`@`MyCatalog.CATfct`", extensionFacade);

// 初始化：关联 base feature
CATFmAttributeValue attrValue;
attrValue.SetFeature(iBaseFeature);
extensionFacade.SetValue("BaseLine", attrValue);
```

**Step 7: 封装业务接口**

不要让上层命令直接读写 CATFmAttributeValue。封装为 `SetParam1()/GetParam1()/GetBaseFeature()` 等接口，把约束/默认值/一致性检查收口到接口内部。

**Step 8: CATIFmFeatureBehaviorCustomization**

三个关键方法：

| 方法 | 职责 | 要点 |
|------|------|------|
| Build() | update 时重算结果 | sp_in 属性变化后触发，发 CATModify 通知 |
| CanBeRemoved() | 控制删除权限 | Extension 默认不可删，需显式放行 |
| BeforeRemove() | 删除前清理 | 解除外部引用、清理附属对象、回收联动数据 |

**Step 9: 删除/更新协议**

三种删除路径：
- `DeleteSelf()`：在扩展自己的 FeatureFacade 上调用
- `RemoveExtension()`：在 base feature 上移除指定扩展
- `DataCommonProtocolServices::Delete()`：公共删除服务（含 CanDelete 校验）

DeleteSelf ≠ 公共删除服务。要让公共删除可用，需同时满足 OSM 中启用 CATIUseEntity + CanBeRemoved() 放行。

**Step 10: 可视化/规格树/交互**

| 层次 | 接口 | 职责 |
|------|------|------|
| 可视化 | CATI3DGeoVisu | 3D 表示生成 |
| 可视化 | CATIModelEvents | 模型→视图变更通知 |
| 可视化 | CATIVisProperties | 颜色/线宽等图形属性 |
| 规格树 | CATINavigateObject | 进入规格树导航 |
| 规格树 | CATINavigateProvider | 容器暴露子对象给规格树 |
| 交互 | CATIEdit | 双击编辑 |
| 交互 | CATICSOFilter | 上下文菜单过滤 |

关键经验：**特征负责"能力"，容器负责"把能力接进会话框架"**。容器侧的 Provider 注册同样关键。

### Applicative Container 的三重职责

1. **实例化目标**：承接 InstantiateIn 或 extension 自动落地
2. **工厂**：封装 Root/Point/Line 等对象的业务创建过程
3. **Provider Owner**：加载时注册规格树/可视化/上下文 Provider

### 工程组织

```
模块结构：
├── modeler 模块：业务接口、FeatureBehaviorCustomization、可视化实现
├── command 模块：CATIEdit、状态命令、对话框、CSO 过滤
├── CNext/resources/graphic/    — CATfct
├── CNext/resources/msgcatalog/ — CATNls
└── CNext/code/dictionary/      — dico 声明

dico 条目示例：
MyFeature IMyFeature libMyModeler
MyFeature CATIFmFeatureBehaviorCustomization libMyModeler
MyFeature CATI3DGeoVisu libMyModeler
MyFeature CATIEdit libMyCommand
```

dico 没配好 → 接口实现等于没接上。

## 最容易踩的坑

| 坑 | 症状 | 解法 |
|----|------|------|
| 只写 OSM 没补运行时行为 | 能建对象但看不到/不能编辑/不能进规格树 | 逐步补齐 Build/Visu/Navigate |
| CATfct 没放回 runtime view | 改了 OSM 但会话仍加载旧目录 | 更新后放回 CNext/resources/graphic |
| Credentials 对不上 | API 静默失败 | client-id 和 RegisterAsCatalogOwner 名一致 |
| 扩展缺 #creation::parameter | 容器定位和创建出错 | 旧目录迁移时高频遗漏 |
| DeleteSelf ≠ 公共删除 | 删除不触发校验 | 分清谁调用、走哪条协议、是否需要 owner |
| Extension 默认不支持 Copy/Paste | 复制粘贴失败 | 根据数据语义单独设计 |

## 最小落地模板

按顺序推进，每步确认通过再往下：

1. Base feature → OSM + Catalog + Credentials + InstantiateIn 跑通
2. 业务接口 → 最简属性读写
3. Build() → update 能跑
4. CATI3DGeoVisu + CATIModelEvents → 模型改了能驱动显示
5. CATINavigateObject + 容器 Provider → 能进规格树
6. CATIEdit + 对话框 + 上下文命令 → 完整交互

Extension 路线替换第 1 步：先把 #extension + #creation::parameter + AddExtension() 跑通。

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 可迁移思路 |
|---|-----|---------|-----------|
| 1 | 声明→实例→行为三层分离 | OSM 声明 / Facade 实例化 / BehaviorCustomization 行为 | 软件架构通用模式：DSL 声明 → 运行时引擎 → 行为钩子。类似 React 的 JSX → VirtualDOM → Lifecycle hooks |
| 2 | Facade 模式统一访问 | ContainerFacade/StartUpFacade/FeatureFacade 各司其职 | 复杂 API 的封装范式：每个 Facade 管一个关注点，避免上帝对象 |
| 3 | Credentials 权限模型 | 先注册再访问，clientId 必须一致 | 任何需要权限控制的系统都适用：先授权再操作，ID 必须匹配 |
| 4 | 维护源文件而非生成物 | 维护 OSM，不维护 CATfct | 类比"维护源码不维护编译产物"，所有系统都应遵循 |
| 5 | 容器三重职责 | 实例化目标 + 工厂 + Provider Owner | 容器/上下文对象的设计模式：不只是存储，还承担创建和暴露职责 |

## 能力边界

1. **仅覆盖 3DEXPERIENCE V6**：不适用于 V5 的 CATIA 特征开发（V5 用不同的 CAA API）
2. **假设有 CAADoc 环境**：文档引用路径均指向本地安装的 CAADoc
3. **代码片段为伪代码级别**：不是可直接编译的完整示例，需要理解上下文后自行补全
4. **未覆盖测试/调试方法**：没有讨论如何在 V6 开发环境中调试自定义特征


## 相关笔记
- [[catia-automation.md]]
- [[catia_automation.md]]
- [[2026-05-05-Zero-to-CAD-Agent闭环合成百万级可执行CAD程序.md]]
- [[2026-04-22-CATIA-接入-AI-大模型原理.md]]
