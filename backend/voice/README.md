# 语音服务配置说明

## 1. 安装依赖

### 1.1 系统依赖
- **FFmpeg** - 用于音频格式转换
  - Windows: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)
  - 确保 `ffmpeg` 和 `ffprobe` 在系统PATH中

### 1.2 Python依赖
```bash
# 进入backend目录
cd backend

# 安装依赖
pip install -r requirements.txt
```

## 2. 下载Whisper.cpp

### 2.1 下载预编译版本
1. 访问 [Whisper.cpp Releases](https://github.com/ggerganov/whisper.cpp/releases)
2. 下载适用于Windows的预编译版本（包含 `main.exe`）
3. 解压到 `backend/voice/whisper.cpp/` 目录

### 2.2 目录结构
```
backend/voice/
├── whisper.cpp/
│   ├── main.exe        # Whisper.cpp主程序
│   └── ...             # 其他文件
├── models/
│   └── medium.bin      # 模型文件
└── ...
```

## 3. 下载模型文件

### 3.1 推荐模型
- **medium.bin** - 平衡准确率和性能（约700MB）
  - 下载地址: [Whisper Models](https://huggingface.co/ggerganov/whisper.cpp/tree/main/models)

### 3.2 模型说明
| 模型 | 大小 | 准确率 | 速度 |
|------|------|--------|------|
| tiny | ~74MB | 低 | 快 |
| base | ~142MB | 中低 | 较快 |
| small | ~466MB | 中 | 中等 |
| medium | ~1.5GB | 高 | 较慢 |
| large | ~2.9GB | 很高 | 很慢 |

## 4. 配置文件

编辑 `backend/voice/config.py` 文件，根据实际情况修改配置：

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

## 5. 测试语音服务

### 5.1 启动后端服务
```bash
cd backend
python main.py
```

### 5.2 测试API

#### 获取服务状态
```bash
curl http://localhost:8000/api/v1/voice/status
```

#### 测试语音识别
```bash
curl -X POST "http://localhost:8000/api/v1/voice/transcribe" \
  -F "file=@test.wav"
```

## 6. 常见问题

### 6.1 服务不可用
- 检查 `main.exe` 是否存在
- 检查模型文件是否正确下载
- 检查FFmpeg是否安装并在PATH中

### 6.2 识别失败
- 确保音频文件格式正确
- 确保音频文件时长不超过60秒
- 尝试使用更大的模型（如medium或large）

### 6.3 性能问题
- 调整 `THREADS` 参数
- 考虑使用较小的模型
- 确保系统有足够的内存

## 7. 性能优化

### 7.1 模型选择
- 生产环境推荐: medium模型
- 开发环境可选: small模型

### 7.2 硬件加速
- 支持CUDA的系统可编译GPU版本
- 参考 [Whisper.cpp文档](https://github.com/ggerganov/whisper.cpp) 进行GPU加速配置
