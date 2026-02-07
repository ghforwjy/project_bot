"""
语音服务配置
"""
import os
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """语音服务配置"""
    # 服务提供商配置
    PROVIDER: str = "whisper"  # 服务提供商: whisper or doubao
    
    # Whisper.cpp配置（仅在使用C++版本时使用）
    WHISPER_PATH: str = "voice/whisper.cpp"
    MODEL_PATH: str = "voice/models/medium.bin"
    
    # Python Whisper配置
    PYTHON_MODEL_NAME: str = "medium"
    
    # 可用的Whisper模型列表
    AVAILABLE_MODELS = [
        {"value": "tiny", "label": "Tiny (最快，质量最低)", "size": "~39MB", "speed": "极快", "quality": "一般"},
        {"value": "base", "label": "Base (快速，质量较低)", "size": "~74MB", "speed": "很快", "quality": "较好"},
        {"value": "small", "label": "Small (平衡速度和質量)", "size": "~244MB", "speed": "快", "quality": "高"},
        {"value": "medium", "label": "Medium (高质量，推荐)", "size": "~769MB", "speed": "中等", "quality": "很高"},
        {"value": "large", "label": "Large (最高质量，最慢)", "size": "~1550MB", "speed": "慢", "quality": "最高"},
    ]
    
    # 豆包语音识别配置
    DOUBAO_APPID: str = os.getenv('DOUBAO_VOICE_APPID', '3561884959')
    DOUBAO_ACCESS_TOKEN: str = os.getenv('DOUBAO_VOICE_ACCESS_TOKEN', 'qwpFoXXzYTxjIWRiWwAjGEGlc_PDyK-h')
    DOUBAO_SECRET_KEY: str = os.getenv('DOUBAO_VOICE_SECRET_KEY', 'Vt-BXogJIF-BWKXO7ypzEZDaVZTwdxNM')
    DOUBAO_API_URL: str = "https://aip.baidubce.com/rest/2.0/speech/v1/asr/recognize"
    DOUBAO_TOKEN_URL: str = "https://aip.baidubce.com/oauth/2.0/token"
    
    # 可用的服务提供商列表
    AVAILABLE_PROVIDERS = [
        {"value": "whisper", "label": "Whisper (本地，支持离线)", "description": "本地运行的语音识别，支持多种模型大小"},
        {"value": "doubao", "label": "豆包语音 (云端，准确率高)", "description": "基于火山引擎的语音识别服务"},
    ]
    
    # 音频配置
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    
    # 识别配置
    LANGUAGE: str = "zh"
    THREADS: int = 4
    BEAM_SIZE: int = 5
    
    # API配置
    MAX_AUDIO_DURATION: int = 60  # 最大录音时长（秒）
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 最大文件大小（10MB）


# 创建全局配置实例
voice_config = VoiceConfig()


# 确保目录存在
def ensure_directories():
    """确保语音服务所需目录存在"""
    os.makedirs(voice_config.WHISPER_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(voice_config.MODEL_PATH), exist_ok=True)
