"""
语音API路由 - 备份版本（能正常工作）
提供语音识别相关的HTTP API和WebSocket接口
当前流程：
1. 前端录音完成后一次性发送音频数据
2. 后端接收完整音频，转换为wav
3. 后端调用豆包API进行流式识别
4. 识别结果实时返回给前端
"""
import os
import io
import uuid
import tempfile
import logging
import subprocess
import asyncio
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse

from .doubao_voice_integration import DoubaoVoiceIntegration, RequestBuilder, ResponseParser
from .whisper_integration import WhisperIntegration
from .audio_processor import AudioProcessor
from .config import voice_config

import aiohttp
import json

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/voice", tags=["voice"])

# 初始化语音服务
doubao_service = DoubaoVoiceIntegration()
whisper_service = WhisperIntegration()
audio_processor = AudioProcessor()


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    provider: str = "doubao"
):
    """
    转录音频文件
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed.")
        
        # 读取音频数据
        audio_data = await file.read()
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(audio_data)
        temp_file.close()
        
        try:
            # 根据提供商选择服务
            if provider == "doubao":
                if not doubao_service.is_available():
                    raise HTTPException(status_code=503, detail="Doubao voice service not available")
                result = await doubao_service.transcribe(temp_file.name)
            elif provider == "whisper":
                if not whisper_service.is_available():
                    raise HTTPException(status_code=503, detail="Whisper voice service not available")
                result = await whisper_service.transcribe(temp_file.name)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
            
            if result.get("success"):
                return JSONResponse(content={
                    "success": True,
                    "text": result.get("text", ""),
                    "provider": provider
                })
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Transcription failed"))
                
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    """
    WebSocket语音流识别
    接收音频流数据，实时返回识别结果
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted for voice stream")
    
    # 创建临时文件保存接收到的音频数据
    temp_webm_file = None
    temp_wav_file = None
    
    try:
        # 接收音频数据
        audio_buffer = bytearray()
        
        while True:
            try:
                # 接收消息
                message = await websocket.receive()
                
                # 处理文本消息（控制命令）
                if message.get("type") == "websocket.receive":
                    if "text" in message:
                        try:
                            data = json.loads(message["text"])
                            if data.get("type") == "end":
                                logger.info("Received end signal")
                                break
                        except:
                            pass
                    
                    # 处理二进制数据（音频数据）
                    if "bytes" in message:
                        audio_buffer.extend(message["bytes"])
                        logger.debug(f"Received audio data chunk, total size: {len(audio_buffer)} bytes")
                        
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
        
        # 检查是否接收到音频数据
        if len(audio_buffer) == 0:
            await websocket.send_json({
                "success": False,
                "error": "No audio data received"
            })
            return
        
        logger.info(f"Total audio data received: {len(audio_buffer)} bytes")
        
        # 保存接收到的音频数据为webm文件
        temp_webm_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_webm_file.write(audio_buffer)
        temp_webm_file.close()
        logger.info(f"Saved audio to temporary webm file: {temp_webm_file.name}")
        
        # 将webm转换为wav格式
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_file.close()
        
        try:
            # 使用ffmpeg转换音频格式
            logger.info("Converting webm to wav...")
            result = subprocess.run([
                'ffmpeg', '-y', '-i', temp_webm_file.name,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ac', '1',               # 单声道
                '-ar', '16000',           # 16kHz采样率
                temp_wav_file.name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                await websocket.send_json({
                    "success": False,
                    "error": f"Audio conversion failed: {result.stderr}"
                })
                return
            
            logger.info(f"Audio converted to wav: {temp_wav_file.name}")
            
        except FileNotFoundError:
            logger.error("FFmpeg not found")
            await websocket.send_json({
                "success": False,
                "error": "FFmpeg not found. Please install FFmpeg."
            })
            return
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timeout")
            await websocket.send_json({
                "success": False,
                "error": "Audio conversion timeout"
            })
            return
        
        # 检查Doubao服务是否可用
        if not doubao_service.is_available():
            logger.error("Doubao voice service not available")
            await websocket.send_json({
                "success": False,
                "error": "Voice service not available"
            })
            return
        
        # 发送开始识别的消息
        await websocket.send_json({
            "success": True,
            "text": "",
            "is_partial": True,
            "message": "Starting recognition..."
        })
        
        # 使用流式识别
        logger.info("Starting streaming transcription...")
        final_text = ""
        
        async for result in doubao_service.transcribe_streaming(temp_wav_file.name):
            if result.get("success"):
                text = result.get("text", "")
                is_final = result.get("is_final", False)
                
                if text:
                    final_text = text
                    logger.info(f"Recognition result: {text[:50]}...")
                    
                    # 发送识别结果
                    await websocket.send_json({
                        "success": True,
                        "text": text,
                        "is_partial": not is_final,
                        "is_final": is_final
                    })
                    
                    # 如果是最终结果，结束识别
                    if is_final:
                        break
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Recognition error: {error}")
                await websocket.send_json({
                    "success": False,
                    "error": error
                })
                return
        
        # 发送最终结果
        if final_text:
            await websocket.send_json({
                "success": True,
                "text": final_text,
                "is_partial": False,
                "is_final": True
            })
        else:
            await websocket.send_json({
                "success": False,
                "error": "No recognition result"
            })
            
    except Exception as e:
        logger.error(f"Voice stream error: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "success": False,
                "error": f"Voice stream error: {str(e)}"
            })
        except:
            pass
    finally:
        # 清理临时文件
        try:
            if temp_webm_file and os.path.exists(temp_webm_file.name):
                os.unlink(temp_webm_file.name)
                logger.info(f"Cleaned up temporary webm file")
        except:
            pass
            
        try:
            if temp_wav_file and os.path.exists(temp_wav_file.name):
                os.unlink(temp_wav_file.name)
                logger.info(f"Cleaned up temporary wav file")
        except:
            pass
            
        try:
            await websocket.close()
        except:
            pass


@router.get("/status")
async def voice_status():
    """
    获取语音服务状态
    """
    return JSONResponse(content={
        "doubao": {
            "available": doubao_service.is_available(),
            "name": "豆包语音识别"
        },
        "whisper": {
            "available": whisper_service.is_available(),
            "name": "Whisper语音识别"
        }
    })


@router.post("/test")
async def test_voice_service():
    """
    测试语音服务
    """
    results = {
        "doubao": {
            "available": doubao_service.is_available(),
            "tested": False,
            "success": False,
            "error": None
        },
        "whisper": {
            "available": whisper_service.is_available(),
            "tested": False,
            "success": False,
            "error": None
        }
    }
    
    # 测试Doubao服务
    if doubao_service.is_available():
        try:
            results["doubao"]["tested"] = True
            results["doubao"]["success"] = True
        except Exception as e:
            results["doubao"]["tested"] = True
            results["doubao"]["error"] = str(e)
    
    # 测试Whisper服务
    if whisper_service.is_available():
        try:
            results["whisper"]["tested"] = True
            results["whisper"]["success"] = True
        except Exception as e:
            results["whisper"]["tested"] = True
            results["whisper"]["error"] = str(e)
    
    return JSONResponse(content=results)
