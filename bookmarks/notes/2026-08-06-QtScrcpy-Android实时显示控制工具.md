# QtScrcpy — Android 实时显示控制工具（31K⭐）

> **来源**：[github.com/barry-ran/qtscrcpy](https://github.com/barry-ran/qtscrcpy)
> **License**：Apache-2.0
> **Stars**：31K · **Forks**：3.7K
> **语言**：C++ (Qt + OpenGL + FFmpeg)
> **Topics**：android, qt
> **作者**：Rankun (Barry)，C++ 桌面客户端开发 / 音视频领域

---

## 一句话定义

> 基于 scrcpy 的 Qt 重写版——通过 USB 或网络实时显示和控制 Android 设备，**无需 root**，支持自定义按键映射和群控。

---

## 内容整理

### 核心特性

| 特性 | 指标 |
|------|------|
| **性能** | 30~60 fps |
| **画质** | 1920×1080 或更高 |
| **延迟** | 35~70ms |
| **启动** | ~1 秒显示第一帧 |
| **侵入性** | 设备端无需安装任何东西 |

### 与原版 scrcpy 对比

| 要点 | scrcpy | QtScrcpy |
|------|--------|----------|
| **UI 框架** | SDL | Qt |
| **视频编码** | FFmpeg | FFmpeg |
| **视频渲染** | SDL | OpenGL |
| **跨平台** | 自实现 | Qt 提供 |
| **语言** | C | C++ |
| **编程风格** | 同步 | **异步（Qt 信号槽）** |
| **自定义按键映射** | ❌ | ✅ |
| **构建** | meson+gradle | qmake 或 CMake |

QtScrcpy 的核心优势：
- Qt GUI 易于定制
- Qt 信号槽异步机制提升性能
- 支持多点触控
- 支持自定义按键映射（游戏脚本）

### 主要功能

- 实时显示 Android 设备屏幕
- 实时鼠标键盘控制
- 屏幕录制 / 截图
- 无线连接（WiFi）
- 多设备连接
- 全屏 / 置顶显示
- 拖拽安装 APK
- 拖拽传输文件
- 后台录制（仅录不显示）
- 剪贴板双向同步
- 群控（同时控制所有设备）
- 设备扬声器声音同步到电脑（Android 10+，基于 sndcpy）

### 自定义按键映射

这是 QtScrcpy 相对原版 scrcpy 的杀手级功能——可以编写脚本把键盘鼠标操作映射为手机的触摸和点击：

- 默认提供抖音和部分游戏脚本
- 内置 PUBG Mobile 键鼠映射
- 支持 GUI 编辑器 QuickAssistant（可视化编辑映射脚本）

### 群控功能

可以同时控制所有连接的手机——适用于批量操作场景。

### 作者商业产品

作者基于 QtScrcpy 开发了更专业的投屏软件 **QuickMirror**：
- 批量投屏 + 单独控制 + 批量控制
- 群组管理
- WiFi/OTG 投屏
- 单机管理 500+ 台手机（OTG 模式 + 低分辨率）
- USB 1080p 延迟 <30ms（同分辨率下市场最低）
- 纯 C++ GPU 渲染
- 支持闲鱼 App、三星手机中文输入
- 免费版支持 10 屏，功能不限

---

## 查询拓展

- QtScrcpy 的异步信号槽架构如何降低延迟？相比 scrcpy 的同步模型优势在哪？
- 自定义按键映射脚本格式是什么？能否用于自动化测试（UI Automation）？
- 群控功能的实现原理——如何保证多设备同步性？
- QuickMirror 单机管理 500+ 手机的技术架构？OTG 模式如何工作？
- scrcpy-server 的 Android 端实现机制——为什么不需要 root？

---

## 归纳总结

QtScrcpy 是 scrcpy 的 C++/Qt 重写版，31K Stars 说明其市场需求巨大。核心差异在于用 Qt 信号槽实现了异步架构，并增加了自定义按键映射和群控两个杀手级功能。作者后续基于此开发的 QuickMirror 商业版（单机 500+ 手机、30ms 延迟）展示了从开源到商业化的完整路径。

技术栈：C++ + Qt + OpenGL + FFmpeg + ADB，设备端通过 scrcpy-server（Android Java 应用）实现免 root 屏幕捕获。

---

## 趋势判断

- **Android 设备管理工具需求旺盛**：31K Stars 说明测试/开发/运营场景对批量 Android 设备控制有巨大需求
- **从开源到商业化的典型路径**：QtScrcpy（开源 31K⭐）→ QuickMirror（商业版）→ QuickAssistant（辅助工具），作者构建了完整产品矩阵
- **群控 + 按键映射 = 自动化测试/灰产双刃剑**：同一技术可用于 UI 自动化测试，也可用于批量操作
- **OTG 模式是差异化突破点**：单机 500+ 手机不依赖 WiFi/ADB，通过 USB OTG 直连，大幅降低部署复杂度

---

## 关联分析

- **与用户研究方向的关联**：用户研究具身智能和 AI Agent 工程化，QtScrcpy 可以作为 Android 设备的视觉控制层——用 AI Agent 驱动 Android UI 操作（截图→VLM 理解→按键映射→执行）
- **与 Hermes Agent 的关联**：QtScrcpy 的 ADB 控制能力可以集成到 Hermes 的终端工具中，让 Hermes 直接操控 Android 设备。剪贴板同步功能可以实现跨设备数据传递
- **与 ESP32/边缘 AI 的关联**：Android 设备作为边缘 AI 的显示和控制终端，QtScrcpy 提供远程操控通道
- **与自动化测试的关联**：QtScrcpy 的按键映射 + 群控功能可用于 Android App 的自动化测试，比 Appium 更轻量

---

*笔记创建：2026-08-06 · 来源：github.com/barry-ran/qtscrcpy*


## 相关笔记

- ESP32-CAM 车库门 AI 自主开发实战（同目录）— Android 设备远程控制交叉场景
- 暂无更多直接关联笔记（独立工具类项目）
