# 语音服务安装指南

## 概述
本指南提供了完整的语音服务安装步骤，包括Whisper.cpp的获取、模型文件的下载以及配置说明。

## 方法一：使用预编译的Whisper.cpp（推荐）

### 步骤1：下载预编译的Whisper.cpp
1. 访问 [Whisper.cpp 发布页面](https://github.com/ggml-org/whisper.cpp/releases)
2. 下载最新的Windows x64预编译版本（如果有）
3. 解压到 `backend/voice/whisper.cpp` 目录

### 步骤2：下载模型文件
1. 访问 [Whisper.cpp 模型页面](https://huggingface.co/ggerganov/whisper.cpp/tree/main/models)
2. 下载 `ggml-medium.bin` 模型文件
3. 保存到 `backend/voice/models` 目录

## 方法二：从源代码编译Whisper.cpp

### 前提条件
- Visual Studio 2022 或更高版本（带 C++ 开发工具）
- CMake
- Git

### 步骤1：编译源代码
1. 源代码已下载到 `backend/voice/whisper.cpp-source/whisper.cpp-master` 目录
2. 按照 `COMPILE_GUIDE.md` 中的说明编译项目

### 步骤2：下载模型文件
1. 编译完成后，运行模型下载脚本：
   ```
   cd backend/voice/whisper.cpp-source/whisper.cpp-master
   python models/download-ggml-model.py medium
   ```

## 方法三：使用替代语音识别服务

如果Whisper.cpp安装遇到困难，可以使用以下替代方案：

### 方案1：使用Web Speech API（浏览器内置）
- 优点：无需安装，直接在浏览器中使用
- 缺点：依赖网络连接，识别质量可能不如Whisper

### 方案2：使用云服务API
- 例如：Google Speech-to-Text、Azure Speech Service等
- 需要配置API密钥

## 配置说明

### 更新配置文件
编译或安装完成后，需要更新 `config.py` 中的路径配置：

```python
# 修改为实际的路径
WHISPER_PATH = "voice/whisper.cpp"  # 或编译后的路径
MODEL_PATH = "voice/models/medium.bin"  # 或编译目录中的模型路径
```

### 验证安装

运行以下命令验证语音服务是否正常：

```bash
# 检查Whisper.cpp是否存在
ls backend/voice/whisper.cpp

# 检查模型文件是否存在
ls backend/voice/models
```

## 故障排除

### 常见问题
1. **编译失败**：确保已安装所有必要的依赖项
2. **模型下载失败**：尝试使用不同的网络连接或手动下载
3. **语音识别无响应**：检查路径配置是否正确
4. **性能问题**：考虑使用更小的模型（如 small 或 base）

### 日志查看
语音服务的日志会输出到控制台，可用于排查问题：

```bash
# 启动后端服务时查看日志
python main.py
```

## 替代方案：使用模拟语音识别

如果所有安装方法都失败，语音服务会自动使用模拟识别结果，确保前端功能可以正常展示。

## 性能优化

1. **模型选择**：根据设备性能选择合适的模型
   - `tiny.bin`：最快，适合低性能设备
   - `base.bin`：平衡速度和质量
   - `small.bin`：较好的质量
   - `medium.bin`：高质量（推荐）
   - `large.bin`：最高质量，速度较慢

2. **线程配置**：在 `config.py` 中调整线程数以匹配CPU核心数

## 前端集成

前端语音组件已实现，包括：
- `VoiceButton.tsx`：语音录制按钮
- `VoiceVisualizer.tsx`：实时波形可视化
- `ChatPanel.tsx`：集成语音输入功能

前端会自动连接到后端语音服务，无需额外配置。
