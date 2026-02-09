"""
豆包实时流式语音识别集成
"""
import os
import json
import time
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, AsyncGenerator

from .config import VoiceConfig
from .doubaoVoice.sauc_websocket_demo import AsrWsClient, AsrResponse, ResponseParser

logger = logging.getLogger(__name__)


class DoubaoStreamingVoiceIntegration:
    """
    豆包实时流式语音识别集成类
    使用WebSocket与前端通信，实现实时语音识别
    """
    
    def __init__(self):
        """
        初始化豆包流式语音识别集成
        """
        self.config = VoiceConfig()
        self.url = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel"
        self.clients = {}
    
    def is_available(self) -> bool:
        """
        检查豆包流式语音识别是否可用
        
        Returns:
            bool: 是否可用
        """
        # 检查必要的配置是否存在
        if not self.config.DOUBAO_APPID:
            logger.warning("Doubao streaming voice: APPID not configured")
            return False
        
        if not self.config.DOUBAO_ACCESS_TOKEN:
            logger.warning("Doubao streaming voice: Access token not configured")
            return False
        
        return True
    
    async def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """
        转录音频文件（非流式，保持兼容性）
        
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
                    "error": "Doubao streaming voice service not available"
                }
            
            # 使用现有的AsrWsClient进行文件转录
            async with AsrWsClient(self.url) as client:
                logger.info(f"Transcribing audio file: {audio_path}")
                
                # 执行转录
                results = []
                async for response in client.execute(audio_path):
                    if response.payload_msg and 'result' in response.payload_msg:
                        text = response.payload_msg['result'].get('text', '')
                        if text:
                            results.append(text)
                
                if results:
                    final_text = "".join(results)
                    logger.info(f"Doubao streaming voice transcription successful: {final_text[:50]}...")
                    
                    return {
                        "success": True,
                        "text": final_text,
                        "provider": "doubao_streaming"
                    }
                else:
                    logger.error("Doubao streaming voice transcription returned no results")
                    return {
                        "success": False,
                        "error": "Transcription returned no results"
                    }
                    
        except Exception as e:
            logger.error(f"Doubao streaming voice transcription error: {str(e)}")
            return {
                "success": False,
                "error": f"Transcription error: {str(e)}"
            }
    
    async def handle_stream(self, websocket) -> None:
        """
        处理WebSocket流式连接
        
        Args:
            websocket: FastAPI WebSocket连接
        """
        # 生成客户端ID
        client_id = str(time.time())
        logger.info(f"New WebSocket connection: {client_id}")
        
        try:
            # 初始化豆包流式语音识别客户端
            async with AsrWsClient(self.url) as client:
                # 建立与豆包的WebSocket连接
                await client.create_connection()
                
                # 发送初始化请求
                await client.send_full_client_request()
                
                # 双向通信
                # 导入RequestBuilder
                from .doubaoVoice.sauc_websocket_demo import RequestBuilder
                
                async def receive_from_frontend():
                    """接收前端发送的音频数据"""
                    while True:
                        try:
                            # 接收前端发送的音频数据
                            audio_data = await websocket.receive_bytes()
                            
                            # 发送给豆包
                            if audio_data:
                                # 检查是否为结束标记
                                if len(audio_data) == 4 and audio_data == b'END':
                                    logger.info(f"Received end signal from frontend: {client_id}")
                                    # 使用RequestBuilder构建结束请求
                                    request = RequestBuilder.new_audio_only_request(
                                        client.seq, 
                                        b'',
                                        is_last=True
                                    )
                                    await client.conn.send_bytes(request)
                                    logger.debug(f"Sent end signal to Doubao: {len(request)} bytes")
                                    break
                                
                                # 使用RequestBuilder构建音频请求
                                request = RequestBuilder.new_audio_only_request(
                                    client.seq, 
                                    audio_data,
                                    is_last=False
                                )
                                await client.conn.send_bytes(request)
                                logger.debug(f"Sent audio data to Doubao: {len(request)} bytes")
                                # 递增seq，因为每个音频包都需要不同的seq
                                client.seq += 1
                        except Exception as e:
                            error_msg = f"Error receiving from frontend: {e}"
                            logger.error(error_msg)
                            try:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": error_msg
                                })
                            except:
                                pass
                            break
                
                async def send_to_frontend():
                    """发送识别结果给前端"""
                    while True:
                        try:
                            # 接收豆包返回的识别结果
                            msg = await client.conn.receive()
                            
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                # 解析豆包返回的结果
                                response = ResponseParser.parse_response(msg.data)
                                
                                if response.payload_msg:
                                    if 'result' in response.payload_msg:
                                        text = response.payload_msg['result'].get('text', '')
                                        if text:
                                            # 发送识别结果给前端
                                            await websocket.send_json({
                                                "type": "recognition_result",
                                                "text": text
                                            })
                                            logger.debug(f"Sent recognition result to frontend: {text}")
                                    elif 'error' in response.payload_msg:
                                        error = response.payload_msg['error']
                                        error_msg = f"Doubao recognition error: {error}"
                                        logger.error(error_msg)
                                        await websocket.send_json({
                                            "type": "error",
                                            "message": error_msg
                                        })
                                        break
                                
                                # 检查是否为最后一个包
                                if response.is_last_package:
                                    logger.info(f"Received final recognition result")
                                    break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                error_msg = f"Doubao WebSocket error: {msg.data}"
                                logger.error(error_msg)
                                await websocket.send_json({
                                    "type": "error",
                                    "message": error_msg
                                })
                                break
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                logger.info(f"Doubao WebSocket connection closed")
                                break
                        except Exception as e:
                            error_msg = f"Error sending to frontend: {e}"
                            logger.error(error_msg)
                            try:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": error_msg
                                })
                            except:
                                pass
                            break
                
                # 创建任务
                receive_task = asyncio.create_task(receive_from_frontend())
                send_task = asyncio.create_task(send_to_frontend())
                
                # 等待任一任务完成
                done, pending = await asyncio.wait(
                    [receive_task, send_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # 取消未完成的任务
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
        except Exception as e:
            error_msg = f"WebSocket stream handling error: {e}"
            logger.error(error_msg)
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": error_msg
                })
            except:
                pass
        finally:
            logger.info(f"WebSocket connection closed: {client_id}")
            try:
                # 关闭WebSocket连接
                await websocket.close(code=1000, reason="Stream completed")
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
                pass
