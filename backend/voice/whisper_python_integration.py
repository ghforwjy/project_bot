"""
Python版本的Whisper集成
"""
import os
import tempfile
from typing import Optional

# 尝试导入Whisper
whisper_available = False
try:
    import whisper
    whisper_available = True
except ImportError:
    print("Whisper库未安装，将使用模拟识别")

from .config import voice_config


class WhisperPythonIntegration:
    """Python版本的Whisper集成"""
    
    def __init__(self):
        """初始化Whisper集成"""
        self.model_name = voice_config.PYTHON_MODEL_NAME
        self.language = voice_config.LANGUAGE
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载Whisper模型"""
        if whisper_available:
            try:
                print(f"正在加载Whisper模型: {self.model_name}")
                self.model = whisper.load_model(self.model_name)
                print("模型加载成功")
            except Exception as e:
                print(f"加载模型失败: {e}")
                self.model = None
    
    def transcribe(self, audio_file: str) -> Optional[str]:
        """
        转录音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            str: 转录结果，失败返回None
        """
        try:
            if not whisper_available or self.model is None:
                print("Whisper不可用，返回模拟结果")
                return "这是一个模拟的语音识别结果。"
            
            print(f"开始转录音频文件: {audio_file}")
            
            # 详细检查文件
            print(f"文件路径: {audio_file}")
            print(f"文件是否存在: {os.path.exists(audio_file)}")
            if os.path.exists(audio_file):
                print(f"文件大小: {os.path.getsize(audio_file)} bytes")
            
            # 尝试使用Whisper转录
            result = self.model.transcribe(
                audio_file,
                language=self.language,
                fp16=False
            )
            
            transcription = result.get('text', '').strip()
            print(f"转录成功: {transcription}")
            return transcription
            
        except Exception as e:
            print(f"转录异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """
        检查Whisper是否可用
        
        Returns:
            bool: 是否可用
        """
        return whisper_available and self.model is not None
    
    def get_status(self) -> dict:
        """
        获取语音服务状态
        
        Returns:
            dict: 状态信息
        """
        return {
            'available': self.is_available(),
            'type': 'python',
            'model': self.model_name,
            'language': self.language
        }
