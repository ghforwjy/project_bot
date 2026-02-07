"""
Whisper.cpp集成
"""
import os
import subprocess
import tempfile
from typing import Optional

from .config import voice_config


class WhisperIntegration:
    """Whisper.cpp集成"""
    
    def __init__(self):
        """初始化Whisper集成"""
        self.whisper_path = voice_config.WHISPER_PATH
        self.model_path = voice_config.MODEL_PATH
        self.language = voice_config.LANGUAGE
        self.threads = voice_config.THREADS
        self.beam_size = voice_config.BEAM_SIZE
    
    def transcribe(self, audio_file: str) -> Optional[str]:
        """
        转录音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            str: 转录结果，失败返回None
        """
        try:
            # 构建whisper.cpp命令
            # 注意：需要下载whisper.cpp和模型文件
            cmd = [
                os.path.join(self.whisper_path, 'main.exe'),
                '-m', self.model_path,
                '-f', audio_file,
                '-l', self.language,
                '-t', str(self.threads),
                '-bs', str(self.beam_size),
                '--no-timestamps',
                '--print-colors', 'False'
            ]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # 提取转录结果
                # whisper.cpp的输出格式需要根据实际情况调整
                output = result.stdout
                
                # 简单处理：去除多余信息，只保留文本
                lines = output.split('\n')
                transcription = []
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith(']'):
                        transcription.append(line)
                
                return ' '.join(transcription)
            else:
                print(f"转录失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"转录异常: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        检查Whisper.cpp是否可用
        
        Returns:
            bool: 是否可用
        """
        try:
            # 检查main.exe是否存在
            main_exe = os.path.join(self.whisper_path, 'main.exe')
            if not os.path.exists(main_exe):
                return False
            
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_status(self) -> dict:
        """
        获取语音服务状态
        
        Returns:
            dict: 状态信息
        """
        return {
            'available': self.is_available(),
            'whisper_path': self.whisper_path,
            'model_path': self.model_path,
            'language': self.language,
            'threads': self.threads
        }
