# 项目安装指南

本文档介绍如何安装和配置项目所需的依赖和模型文件。

## 目录

- [1. FFmpeg 安装](#1-ffmpeg-安装)
- [2. Whisper.cpp 安装](#2-whispercpp-安装)
- [3. 模型文件下载](#3-模型文件下载)
- [4. 目录结构说明](#4-目录结构说明)
- [5. 配置文件](#5-配置文件)
- [6. 验证安装](#6-验证安装)
- [7. 常见问题](#7-常见问题)

---

## 1. FFmpeg 安装

### 1.1 下载 FFmpeg

**下载地址**: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

**推荐版本**: FFmpeg 8.0.1 或更高版本

**下载步骤**:
1. 访问上述下载地址
2. 选择 "Windows builds from gyan.dev"
3. 下载 "ffmpeg-git-full.7z" 或 "ffmpeg-release-essentials.zip"

### 1.2 安装 FFmpeg

**方法一：使用预编译版本（推荐）**

1. 解压下载的文件
2. 将以下文件复制到项目目录：
   ```
   E:\mycode\project_bot\ffmpeg\
   ├── ffmpeg.exe
   ├── ffplay.exe
   └── ffprobe.exe
   ```

**方法二：添加到系统PATH**

1. 将 FFmpeg 解压到任意目录（如 `C:\ffmpeg`）
2. 将该目录添加到系统环境变量 PATH 中
3. 重启命令提示符，验证安装：
   ```bash
   ffmpeg -version
   ffprobe -version
   ```

**推荐**: 使用方法一，将文件放在项目 `ffmpeg/` 目录下，避免依赖系统配置。

---

## 2. Whisper.cpp 安装

### 2.1 下载 Whisper.cpp

**下载地址**: [https://github.com/ggerganov/whisper.cpp/releases](https://github.com/ggerganov/whisper.cpp/releases)

**下载步骤**:
1. 访问上述 GitHub Releases 页面
2. 找到最新版本的 Windows 预编译版本
3. 下载 `whisper.cpp-v1.5.4-windows-x64.zip`（或更新版本）

### 2.2 安装 Whisper.cpp

**安装步骤**:
1. 解压下载的 ZIP 文件
2. 将解压后的文件复制到项目目录：
   ```
   E:\mycode\project_bot\backend\voice\whisper.cpp\
   ├── main.exe          # 主程序
   └── ...              # 其他文件
   ```

**注意**: 确保 `main.exe` 文件存在于 `backend/voice/whisper.cpp/` 目录中。

---

## 3. 模型文件下载

### 3.1 模型选择

| 模型 | 大小 | 准确率 | 速度 | 推荐场景 |
|------|------|--------|------|----------|
| tiny | ~74MB | 低 | 快 | 测试/开发 |
| base | ~142MB | 中低 | 较快 | 轻量级应用 |
| small | ~466MB | 中 | 中等 | 一般应用 |
| **medium** | ~1.5GB | **高** | **较慢** | **生产环境（推荐）** |
| large | ~2.9GB | 很高 | 很慢 | 高精度需求 |

**推荐**: 生产环境使用 `medium` 模型，开发环境可使用 `small` 模型。

### 3.2 下载模型

**下载地址**: [https://huggingface.co/ggerganov/whisper.cpp/tree/main/models](https://huggingface.co/ggerganov/whisper.cpp/tree/main/models)

**下载步骤**:
1. 访问上述 Hugging Face 模型页面
2. 找到 `ggml-medium.bin` 文件（或其他模型）
3. 点击下载该文件

### 3.3 安装模型

**安装步骤**:
1. 将下载的模型文件重命名为 `medium.bin`（如果使用medium模型）
2. 复制到项目目录：
   ```
   E:\mycode\project_bot\backend\voice\models\
   └── medium.bin
   ```

**注意**: 
- 文件大小约 1.5GB，下载需要一些时间
- 确保下载完整，文件大小应约为 1.5GB

---

## 4. 目录结构说明

安装完成后，项目目录结构应如下：

```
E:\mycode\project_bot\
├── backend/
│   ├── voice/
│   │   ├── whisper.cpp/
│   │   │   └── main.exe          # ✅ Whisper.cpp 主程序
│   │   ├── models/
│   │   │   └── medium.bin         # ✅ 模型文件
│   │   ├── config.py                 # 配置文件
│   │   └── ...                      # 其他文件
│   └── ...
├── ffmpeg/
│   ├── ffmpeg.exe                # ✅ FFmpeg 主程序
│   ├── ffplay.exe                # ✅ FFplay 播放器
│   └── ffprobe.exe               # ✅ FFprobe 探测器
└── ...
```

**关键文件**:
- ✅ `backend/voice/whisper.cpp/main.exe` - Whisper.cpp 主程序
- ✅ `backend/voice/models/medium.bin` - 模型文件
- ✅ `ffmpeg/ffmpeg.exe` - FFmpeg 主程序
- ✅ `ffmpeg/ffprobe.exe` - FFprobe 探测器

---

## 5. 配置文件

编辑 `backend/voice/config.py` 文件，根据实际情况修改配置：

```python
@dataclass
class VoiceConfig:
    # Whisper.cpp配置
    WHISPER_PATH: str = "voice/whisper.cpp"  # Whisper.cpp目录（相对于backend/）
    MODEL_PATH: str = "voice/models/medium.bin"  # 模型文件路径（相对于backend/）
    
    # 识别配置
    LANGUAGE: str = "zh"  # 语言代码（zh=中文，en=英文）
    THREADS: int = 4  # 线程数（建议4-8）
    
    # 其他配置...
```

**配置说明**:
- `WHISPER_PATH`: Whisper.cpp 可执行文件所在目录（相对于 `backend/`）
- `MODEL_PATH`: 模型文件路径（相对于 `backend/`）
- `LANGUAGE`: 识别语言（`zh`=中文，`en`=英文）
- `THREADS`: 并行线程数（建议设置为 CPU 核心数）

---

## 6. 验证安装

### 6.1 验证 FFmpeg

```bash
cd E:\mycode\project_bot\ffmpeg
ffmpeg -version
```

**预期输出**: 显示 FFmpeg 版本信息

### 6.2 验证 Whisper.cpp

```bash
cd E:\mycode\project_bot\backend\voice\whisper.cpp
main.exe --help
```

**预期输出**: 显示 Whisper.cpp 帮助信息

### 6.3 验证模型文件

```bash
cd E:\mycode\project_bot\backend\voice\models
dir medium.bin
```

**预期输出**: 显示模型文件信息（大小应约为 1.5GB）

### 6.4 测试语音服务

1. 启动后端服务：
   ```bash
   cd E:\mycode\project_bot\backend
   python main.py
   ```

2. 测试语音识别 API：
   ```bash
   curl -X POST "http://localhost:8000/api/v1/voice/transcribe" \
     -F "file=@test.wav"
   ```

**预期输出**: 返回识别结果 JSON

---

## 7. 常见问题

### 7.1 FFmpeg 相关问题

**问题**: `ffmpeg` 命令不可用

**解决方案**:
1. 检查 `ffmpeg/` 目录下是否有 `ffmpeg.exe`
2. 如果使用系统 PATH 方式，确保已添加到环境变量
3. 重启命令提示符

**问题**: 音频格式转换失败

**解决方案**:
1. 确保下载的是完整版 FFmpeg（包含所有编解码器）
2. 检查音频文件是否损坏

### 7.2 Whisper.cpp 相关问题

**问题**: `main.exe` 运行失败

**解决方案**:
1. 确保下载的是 Windows 版本（不是 Linux 或 macOS）
2. 检查文件是否完整解压
3. 尝试以管理员权限运行

**问题**: 识别速度很慢

**解决方案**:
1. 使用较小的模型（如 `small` 或 `base`）
2. 增加 `THREADS` 参数
3. 考虑使用 GPU 加速版本

**问题**: 识别准确率低

**解决方案**:
1. 使用更大的模型（如 `large`）
2. 确保音频质量良好
3. 检查语言设置是否正确

### 7.3 模型文件相关问题

**问题**: 模型文件下载不完整

**解决方案**:
1. 检查文件大小（medium.bin 应约为 1.5GB）
2. 重新下载模型文件
3. 使用下载工具（如 aria2）支持断点续传

**问题**: 模型文件找不到

**解决方案**:
1. 检查 `config.py` 中的 `MODEL_PATH` 配置
2. 确保模型文件在正确的目录
3. 检查文件名是否正确（应为 `medium.bin`）

### 7.4 服务相关问题

**问题**: 语音识别 API 返回错误

**解决方案**:
1. 检查后端服务是否正常运行
2. 检查 FFmpeg 和 Whisper.cpp 是否正确安装
3. 查看后端日志获取详细错误信息

---

## 8. 替代方案

如果 Whisper.cpp 安装或使用遇到问题，可以考虑以下替代方案：

### 8.1 在线语音识别服务

- **百度语音识别** - 有免费额度，中文识别准确
- **科大讯飞** - 中文识别准确率高
- **Azure Speech** - 多语言支持

### 8.2 本地语音识别

- **Vosk** - 轻量级本地语音识别
- **PocketSphinx** - 开源，资源占用极低

请根据实际需求和场景选择合适的方案。

---

## 9. 性能优化建议

### 9.1 硬件要求

- **CPU**: 推荐四核及以上
- **内存**: 推荐 8GB 及以上（使用 medium 模型）
- **磁盘**: 至少 5GB 可用空间

### 9.2 性能调优

1. **模型选择**:
   - 开发环境: `small` 模型（速度快）
   - 生产环境: `medium` 模型（准确率高）

2. **线程配置**:
   - 设置 `THREADS` 为 CPU 核心数
   - 避免设置过高导致系统卡顿

3. **GPU 加速**:
   - 如有 NVIDIA GPU，可编译 GPU 版本
   - 参考 [Whisper.cpp 文档](https://github.com/ggerganov/whisper.cpp) 进行配置

---

## 10. 快速安装检查清单

安装完成后，请检查以下项目：

- [ ] FFmpeg 已下载并放置在 `ffmpeg/` 目录
- [ ] Whisper.cpp 已下载并放置在 `backend/voice/whisper.cpp/` 目录
- [ ] 模型文件已下载并放置在 `backend/voice/models/` 目录
- [ ] `config.py` 配置文件已更新
- [ ] FFmpeg 可以通过命令行调用
- [ ] Whisper.cpp 可以通过命令行调用
- [ ] 后端服务可以正常启动
- [ ] 语音识别 API 可以正常调用

如果所有项目都已完成，则安装成功！

---

## 11. 联系与支持

如果遇到问题：

1. 查看项目 README.md 获取更多信息
2. 查看 `backend/voice/` 目录下的其他文档
3. 提交 Issue 到项目仓库

---

**最后更新**: 2026-02-07
**文档版本**: 1.0
