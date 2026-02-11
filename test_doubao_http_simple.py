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
        logging.FileHandler('test_http_simple_run.log'),
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
        self.api_url = "https://openspeech.bytedance.com/api/v3/sauc/bigmodel"

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
            # 编码音频文件
            audio_data = self.encode_audio(audio_path)
            logger.info(f"Encoded audio file, size: {len(audio_data)} bytes")

            # 构建请求头
            headers = {
                "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
                "X-Api-Request-Id": str(time.time()),
                "X-Api-Access-Key": self.access_key,
                "X-Api-App-Key": self.app_key,
                "X-Api-Connect-Id": str(time.time()),
                "Content-Type": "application/json"
            }

            # 构建请求体
            data = {
                "audio": audio_data,
                "config": {
                    "encoding": "wav",
                    "sample_rate_hertz": 16000,
                    "language_code": "zh-CN"
                }
            }

            # 发送请求
            logger.info("Sending recognition request...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            # 处理响应
            response_data = response.json()
            logger.info(f"Received response: {json.dumps(response_data, ensure_ascii=False)}")

            return {
                "success": True,
                "data": response_data
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
