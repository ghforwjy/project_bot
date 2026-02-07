"""
豆包语音识别集成
"""
import os
import json
import time
import httpx
import base64
import logging
from typing import Optional, Dict, Any

from .config import VoiceConfig

logger = logging.getLogger(__name__)


class DoubaoVoiceIntegration:
    """
    豆包语音识别集成类
    使用火山引擎语音识别API
    """
    
    def __init__(self):
        """
        初始化豆包语音识别集成
        """
        self.config = VoiceConfig()
        self.access_token = None
        self.token_expiry = 0
        
    def is_available(self) -> bool:
        """
        检查豆包语音识别是否可用
        
        Returns:
            bool: 是否可用
        """
        # 检查必要的配置是否存在
        if not self.config.DOUBAO_APPID:
            logger.warning("Doubao voice: APPID not configured")
            return False
        
        if not self.config.DOUBAO_ACCESS_TOKEN:
            logger.warning("Doubao voice: Access token not configured")
            return False
        
        if not self.config.DOUBAO_SECRET_KEY:
            logger.warning("Doubao voice: Secret key not configured")
            return False
        
        return True
    
    async def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            **kwargs: 额外参数
            
        Returns:
            Dict[str, Any]: 转录结果
        """
        try:
            # 检查服务是否可用
            if not self.is_available():
                return {
                    "success": False,
                    "error": "Doubao voice service not available"
                }
            
            # 获取访问令牌
            access_token = await self._get_access_token()
            if not access_token:
                return {
                    "success": False,
                    "error": "Failed to get access token"
                }
            
            # 读取并编码音频文件
            audio_data = await self._encode_audio(audio_path)
            if not audio_data:
                return {
                    "success": False,
                    "error": "Failed to read audio file"
                }
            
            # 构建请求参数
            params = {
                "appid": self.config.DOUBAO_APPID,
                "access_token": access_token,
                "format": "wav",
                "rate": 16000,
                "channel": 1,
                "cuid": "project_assistant",
                "token": access_token,
                "lan": "zh"
            }
            
            # 构建请求体
            data = {
                "audio": audio_data
            }
            
            # 发送请求
            logger.info(f"Sending transcription request to Doubao voice API")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.config.DOUBAO_API_URL,
                    params=params,
                    json=data
                )
            
            # 处理响应
            response_data = response.json()
            
            if response.status_code == 200:
                if response_data.get("err_no") == 0:
                    result = response_data.get("result", [])
                    text = "".join(result)
                    
                    logger.info(f"Doubao voice transcription successful: {text[:50]}...")
                    
                    return {
                        "success": True,
                        "text": text,
                        "confidence": response_data.get("confidence", 0.0),
                        "provider": "doubao"
                    }
                else:
                    error_msg = response_data.get("err_msg", "Unknown error")
                    logger.error(f"Doubao voice API error: {error_msg}")
                    return {
                        "success": False,
                        "error": f"API error: {error_msg}"
                    }
            else:
                logger.error(f"Doubao voice API request failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Request failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Doubao voice transcription error: {str(e)}")
            return {
                "success": False,
                "error": f"Transcription error: {str(e)}"
            }
    
    async def _get_access_token(self) -> Optional[str]:
        """
        获取访问令牌
        
        Returns:
            Optional[str]: 访问令牌
        """
        # 检查令牌是否有效
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        # 这里直接返回配置中的访问令牌
        # 实际项目中可能需要根据APPID和Secret Key动态获取
        self.access_token = self.config.DOUBAO_ACCESS_TOKEN
        self.token_expiry = time.time() + 3600  # 假设1小时有效期
        
        return self.access_token
    
    async def _encode_audio(self, audio_path: str) -> Optional[str]:
        """
        读取并编码音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            Optional[str]: Base64编码的音频数据
        """
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            # 编码为Base64
            encoded = base64.b64encode(audio_bytes).decode("utf-8")
            return encoded
            
        except Exception as e:
            logger.error(f"Failed to encode audio file: {str(e)}")
            return None
