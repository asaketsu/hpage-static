# ESP32 跑 AI：TinyML 三大神操作（科普笔记）

- 📅 2026-06-03
- ⭐ 2/5 — 科普向，核心技术点已在 tinyml-pipeline 项目中完整提取
- 🏷️ #TinyML #ESP32 #科普 #微信公众号
- 📰 半塘公社
- 🔗 https://mp.weixin.qq.com/s/rO7c0lNUiimEdDMyQ8rd7w
- 📂 关联项目: /home/jc/uclaw/project/tinyml-pipeline/

## 摘要

半塘公社的 TinyML 科普文章，以通俗语言介绍 ESP32 上运行 AI 的三个实战案例（手势识别、语音唤醒、跳绳计数）。内容对应我们已分析的 HollowMan6/TinyML-ESP32 项目（205⭐），核心技术点已完整提取为 tinyml-pipeline 项目。

## 核心要点

### TinyML 核心理念

- **本地推理**：模型压缩后塞进 MCU，毫秒级响应，数据不出房间
- **硬件成本**：ESP32-WROOM-32 开发板 ~¥30，集成麦克风+陀螺仪+LED
- **技术栈**：Arduino IDE + TensorFlow Lite for Microcontrollers

### 三步实战流程

1. **数据采集**：串口 115200 baud 导出传感器数据 → CSV
2. **模型训练**：PC 端 Jupyter Notebook 训练 → TFLite 量化
3. **模型部署**：TFLite → C 数组 → 刷入 ESP32

### 三个项目

| 项目 | 传感器 | 核心技术 | 效果 |
|------|--------|----------|------|
| 手势识别 | GY-25Z 陀螺仪 | 6轴数据分类 | 空中挥动控灯 |
| 语音唤醒 | I2S 麦克风 | FFT 频谱分析 | 语音开灯 |
| 跳绳计数 | 6轴姿态传感器 | 动作分类 | 自动过滤无效动作 |

### 关键论点

- **端侧智能是下一个万亿级赛道**：IoT 爆发下不可能每个设备都连服务器
- **"峰终定律"**：TinyML 的零延迟交互 = 用户体验峰值
- **隐私优势**：数据本地处理，无需上传云端

## 💡 与我们体系的对照

| 文章内容 | 我们的实践 | 状态 |
|---------|-----------|------|
| 3个 TinyML 项目 | 已完整提取为 tinyml-pipeline | ✅ 项目已落地 |
| IMU 6轴预处理 | imu_processor.py | ✅ 可运行 |
| FFT 音频处理 | audio_processor.py | ✅ 可运行 |
| TFLite→C 导出 | CExporter 模块 | ✅ 纯 Python |
| 训练流水线 | pipeline.py | ✅ 12/13 tests passed |

## 笔记者批注

1. 文章是典型的"技术科普→引流"结构，内容准确但深度有限，适合入门读者
2. 提到的"黑胡桃实验室"教程即 HollowMan6/TinyML-ESP32 的原始来源
3. "峰终定律"应用到端侧 AI 的观点有启发性，可作为产品论述的论据储备
4. 核心技术零新增——所有内容已在我们的 tinyml-pipeline 项目中以更高代码质量落地

## 相关笔记
- [TinyML-ESP32端到端训练流水线提取](2026-06-03-TinyML-ESP32端到端训练流水线提取.md)
- [CameraWifiMotion帧差法运动检测项目提取](2026-06-03-CameraWifiMotion帧差法运动检测项目提取.md)
