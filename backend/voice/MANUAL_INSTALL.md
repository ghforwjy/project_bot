# Whisper.cpp 手动安装指南

由于网络原因，自动下载可能失败。请按照以下步骤手动安装配置：

## 1. 下载 Whisper.cpp

### 步骤1：访问 GitHub 发布页
- 打开浏览器，访问：[Whisper.cpp Releases](https://github.com/ggerganov/whisper.cpp/releases)

### 步骤2：下载 Windows 版本
- 找到最新版本的 Windows 预编译版本（如 `whisper.cpp-v1.5.4-windows-x64.zip`）
- 点击下载该 ZIP 文件

### 步骤3：解压文件
- 将下载的 ZIP 文件解压到 `backend/voice/whisper.cpp/` 目录
- 确保 `main.exe` 文件存在于该目录中

## 2. 下载模型文件

### 步骤1：访问模型下载页
- 打开浏览器，访问：[Whisper Models](https://huggingface.co/ggerganov/whisper.cpp/tree/main/models)

### 步骤2：下载 medium 模型
- 找到 `ggml-medium.bin` 文件
- 点击下载该文件

### 步骤3：保存模型
- 将下载的 `ggml-medium.bin` 文件重命名为 `medium.bin`
- 保存到 `backend/voice/models/` 目录

## 3. 验证安装

### 目录结构检查
确保目录结构如下：

```
backend/voice/
├── whisper.cpp/
│   ├── main.exe        # ✅ 必须存在
│   └── ...             # 其他文件
├── models/
│   └── medium.bin      # ✅ 必须存在
└── ...
```

### 测试命令
打开命令提示符，进入 `backend/voice/whisper.cpp/` 目录，运行：

```bash
# 测试 Whisper.cpp 是否正常工作
main.exe --help
```

如果看到帮助信息，则安装成功。

## 4. 配置文件

编辑 `backend/voice/config.py` 文件，确保配置正确：

```python
@dataclass
class VoiceConfig:
    # Whisper.cpp配置
    WHISPER_PATH: str = "voice/whisper.cpp"  # Whisper.cpp目录
    MODEL_PATH: str = "voice/models/medium.bin"  # 模型文件路径
    
    # 识别配置
    LANGUAGE: str = "zh"  # 语言代码
    THREADS: int = 4  # 线程数
    
    # 其他配置...
```

## 5. 常见问题

### 问题1：找不到 main.exe
- 检查解压是否正确
- 确保下载的是 Windows 版本

### 问题2：模型文件大小异常
- medium.bin 文件大小应约为 700MB
- 如果太小，可能下载不完整

### 问题3：运行时出现错误
- 确保 FFmpeg 已安装并在系统 PATH 中
- 检查模型文件路径是否正确

## 6. 替代方案

如果上述方法仍有问题，可以考虑使用其他语音识别服务：

### 在线服务
- **百度语音识别** - 有免费额度
- **科大讯飞** - 中文识别准确率高
- **Azure Speech** - 多语言支持

### 本地服务
- **Vosk** - 轻量级本地语音识别
- **PocketSphinx** - 资源占用极低

请根据实际情况选择合适的方案。
