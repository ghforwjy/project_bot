"""
音频处理模块
"""
import os
import subprocess
from typing import Optional


class AudioProcessor:
    """音频处理器"""
    
    @staticmethod
    def convert_to_wav(input_file: str, output_file: str) -> bool:
        """
        转换音频文件为WAV格式
        
        Args:
            input_file: 输入音频文件路径
            output_file: 输出WAV文件路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 使用ffmpeg转换音频
            # 注意：需要安装ffmpeg
            cmd = [
                'ffmpeg', '-y',
                '-i', input_file,
                '-ar', '16000',  # 16kHz采样率
                '-ac', '1',       # 单声道
                '-f', 'wav',
                output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"音频转换失败: {e}")
            return False
    
    @staticmethod
    def validate_audio(file_path: str) -> Optional[dict]:
        """
        验证音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            dict: 音频信息，失败返回None
        """
        try:
            # 使用ffprobe获取音频信息
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name,sample_rate,channels,duration',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            
            return None
            
        except Exception as e:
            print(f"音频验证失败: {e}")
            return None
    
    @staticmethod
    def get_audio_duration(file_path: str) -> Optional[float]:
        """
        获取音频时长
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            float: 时长（秒），失败返回None
        """
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            
            return None
            
        except Exception as e:
            print(f"获取音频时长失败: {e}")
            return None
