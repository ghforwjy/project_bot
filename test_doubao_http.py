import base64
import json
import logging
import os
import time
from typing import Dict, Any

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_http_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # 填入控制台获取的app id和access token
        self.auth = {
            "app_key": "3561884959",
            "access_key": "qwpFoXXzYTxjIWRiWwAjGEGlc_PDyK-h"
        }

    @property
    def app_key(self) -> str:
        return self.auth["app_key"]

    @property
    def access_key(self) -> str:
        return self.auth["access_key"]

config = Config()

class DoubaoHTTPTest:
    def __init__(self):
        self.app_key = config.app_key
        self.access_key = config.access_key
        self.api_url = "https://aip.baidubce.com/rest/2.0/speech/v1/asr/recognize"
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"

    def get_access_token(self) -> str:
        """
        获取百度语音识别API的访问令牌
        """
        params = {
            "grant_type": "client_credentials",
            "client_id": self.app_key,
            "client_secret": self.access_key
        }

        try:
            response = requests.get(self.token_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    def encode_audio(self, audio_path: str) -> str:
        """
        读取并编码音频文件
        """
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # 编码为Base64
            encoded = base64.b64encode(audio_bytes).decode("utf-8")
            return encoded
        except Exception as e:
            logger.error(f"Failed to encode audio file: {e}")
            raise

    def recognize(self, audio_path: str) -> Dict[str, Any]:
        """
        调用语音识别API
        """
        try:
            # 获取访问令牌
            access_token = self.get_access_token()
            logger.info(f"Got access token: {access_token[:20]}...")

            # 编码音频文件
            audio_data = self.encode_audio(audio_path)
            logger.info(f"Encoded audio file, size: {len(audio_data)} bytes")

            # 构建请求参数
            params = {
                "appid": self.app_key,
                "access_token": access_token,
                "format": "wav",
                "rate": 16000,
                "channel": 1,
                "cuid": "project_assistant",
                "lan": "zh"
            }

            # 构建请求体
            data = {
                "audio": audio_data
            }

            # 发送请求
            logger.info("Sending recognition request...")
            response = requests.post(
                self.api_url,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            # 处理响应
            response_data = response.json()
            logger.info(f"Received response: {json.dumps(response_data, ensure_ascii=False)}")

            if response_data.get("err_no") == 0:
                result = response_data.get("result", [])
                text = "".join(result)
                logger.info(f"Recognition successful: {text}")
                return {
                    "success": True,
                    "text": text,
                    "confidence": response_data.get("confidence", 0.0),
                    "provider": "doubao"
                }
            else:
                error_msg = response_data.get("err_msg", "Unknown error")
                logger.error(f"Recognition failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"API error: {error_msg}"
                }

        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return {
                "success": False,
                "error": f"Recognition error: {str(e)}"
            }


def main():
    # 测试文件路径
    audio_path = "F:/mycode/project_bot/project_bot/voice/testrecord.wav"

    # 创建测试实例
    test = DoubaoHTTPTest()

    # 调用语音识别
    result = test.recognize(audio_path)

    # 打印结果
    logger.info(f"Final result: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
