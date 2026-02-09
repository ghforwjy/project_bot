"""
语音API路由
"""
import os
import tempfile
import logging
import time
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from .doubao_streaming_integration import DoubaoStreamingVoiceIntegration

from .whisper_integration import WhisperIntegration
from .whisper_python_integration import WhisperPythonIntegration
from .doubao_voice_integration import DoubaoVoiceIntegration
from .audio_processor import AudioProcessor
from .config import voice_config, ensure_directories

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

# 全局语音识别实例
current_whisper = None
current_doubao = None
current_provider = None


def get_voice_provider():
    """
    获取当前配置的语音服务提供商
    """
    # 从配置中获取提供商
    provider = voice_config.PROVIDER
    
    # 从环境变量中获取（优先级更高）
    env_provider = os.getenv('VOICE_PROVIDER')
    if env_provider:
        provider = env_provider
    
    return provider


def get_voice_service():
    """
    获取当前配置的语音服务实例
    """
    global current_whisper, current_doubao, current_provider
    
    # 获取当前提供商
    provider = get_voice_provider()
    
    # 如果提供商没有变化且实例已存在，直接返回
    if current_provider == provider:
        if provider == "whisper" and current_whisper:
            return current_whisper
        elif provider == "doubao" and current_doubao:
            return current_doubao
    
    # 提供商变化或实例不存在，重新初始化
    current_provider = provider
    
    if provider == "whisper":
        # 优先使用Python版本的Whisper集成
        python_whisper = WhisperPythonIntegration()
        if python_whisper.is_available():
            current_whisper = python_whisper
            logger.info("使用Python版本的Whisper集成")
        else:
            current_whisper = WhisperIntegration()
            logger.info("使用C++版本的Whisper集成")
        current_doubao = None
        return current_whisper
    
    elif provider == "doubao":
        current_doubao = DoubaoVoiceIntegration()
        logger.info("使用豆包语音识别集成")
        current_whisper = None
        return current_doubao
    
    elif provider == "doubao_streaming":
        current_doubao = DoubaoStreamingVoiceIntegration()
        logger.info("使用豆包流式语音识别集成")
        current_whisper = None
        return current_doubao
    
    else:
        # 默认使用Whisper
        python_whisper = WhisperPythonIntegration()
        if python_whisper.is_available():
            current_whisper = python_whisper
        else:
            current_whisper = WhisperIntegration()
        logger.info(f"未知的提供商: {provider}，默认使用Whisper")
        current_provider = "whisper"
        current_doubao = None
        return current_whisper


@router.post("/voice/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    """
    音频转文字
    
    Args:
        file: 音频文件
        
    Returns:
        JSON: 转录结果
    """
    try:
        logger.info("开始处理语音转文字请求")
        # 确保目录存在
        ensure_directories()
        
        # 检查文件大小
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        logger.info(f"收到音频文件: {file.filename}, 大小: {file_size} bytes")
        
        if file_size > voice_config.MAX_FILE_SIZE:
            logger.warning(f"文件大小超过限制: {file_size} > {voice_config.MAX_FILE_SIZE}")
            raise HTTPException(
                status_code=413, 
                detail=f"文件大小超过限制: {voice_config.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # 保存上传的文件
        logger.info(f"准备保存上传文件: {file.filename}")
        logger.info(f"文件大小: {file_size} bytes")
        logger.info(f"文件扩展名: {os.path.splitext(file.filename)[1]}")
        
        with tempfile.NamedTemporaryFile(
            suffix=os.path.splitext(file.filename)[1],
            delete=False
        ) as temp_file:
            content = await file.read()
            written_size = temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"临时文件保存成功: {temp_file_path}")
        logger.info(f"写入文件大小: {written_size} bytes")
        logger.info(f"临时文件实际大小: {os.path.getsize(temp_file_path)} bytes")
        
        wav_file = None
        
        try:
            # 获取语音服务实例
            whisper = get_voice_service()
            provider = get_voice_provider()
            logger.info(f"使用语音服务提供商: {provider}")
            
            # 检查服务是否可用
            if not whisper.is_available():
                logger.warning(f"{provider}服务不可用，返回模拟结果")
                # 如果服务不可用，返回模拟结果
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 200,
                        "message": "语音识别成功（模拟）",
                        "data": {
                            "text": "这是一个模拟的语音识别结果。请检查语音服务配置。",
                            "duration": 2.5
                        }
                    }
                )
            
            # 检查是否使用Python版本的Whisper
            is_python_whisper = hasattr(whisper, 'model_name')
            is_doubao = hasattr(whisper, '_get_access_token')
            
            if is_python_whisper:
                # Python版本的Whisper支持多种音频格式，不需要转换
                logger.info("使用Python版本的Whisper，跳过音频格式转换")
                transcription_file = temp_file_path
            elif is_doubao:
                # 豆包语音识别也支持直接处理
                logger.info("使用豆包语音识别，跳过音频格式转换")
                transcription_file = temp_file_path
            else:
                # C++版本的Whisper需要WAV格式
                wav_file = temp_file_path + ".wav"
                logger.info(f"开始转换音频格式: {temp_file_path} -> {wav_file}")
                
                if not AudioProcessor.convert_to_wav(temp_file_path, wav_file):
                    logger.error("音频格式转换失败")
                    raise HTTPException(
                        status_code=400,
                        detail="音频格式转换失败"
                    )
                
                logger.info("音频格式转换成功")
                transcription_file = wav_file
            
            # 验证音频
            audio_info = AudioProcessor.validate_audio(transcription_file)
            if audio_info:
                logger.info(f"音频验证成功: {audio_info}")
                
                # 检查音频时长
                duration = AudioProcessor.get_audio_duration(transcription_file)
                logger.info(f"音频时长: {duration}秒")
                
                if duration and duration > voice_config.MAX_AUDIO_DURATION:
                    logger.warning(f"音频时长超过限制: {duration} > {voice_config.MAX_AUDIO_DURATION}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"音频时长超过限制: {voice_config.MAX_AUDIO_DURATION}秒"
                    )
            else:
                logger.warning("音频验证失败，将尝试直接转录")
            
            # 检查文件是否存在
            if not os.path.exists(transcription_file):
                logger.error(f"转录文件不存在: {transcription_file}")
                # 打印当前目录和文件列表，用于调试
                logger.error(f"当前目录: {os.getcwd()}")
                temp_dir = os.path.dirname(transcription_file)
                if os.path.exists(temp_dir):
                    logger.error(f"临时目录中的文件: {os.listdir(temp_dir)[:5]}")  # 只显示前5个文件
                raise HTTPException(
                    status_code=500,
                    detail="转录文件不存在"
                )
            
            logger.info(f"转录文件存在，大小: {os.path.getsize(transcription_file)} bytes")
            
            # 对于Python版本的Whisper，尝试将文件复制到当前目录以避免路径问题
            if is_python_whisper:
                try:
                    # 创建一个简单的文件名
                    simple_filename = f"audio_{os.getpid()}.wav"
                    simple_path = os.path.join(os.getcwd(), simple_filename)
                    
                    # 复制文件
                    import shutil
                    shutil.copy2(transcription_file, simple_path)
                    
                    logger.info(f"文件复制成功: {simple_path}")
                    logger.info(f"复制后文件大小: {os.path.getsize(simple_path)} bytes")
                    
                    # 使用复制后的文件进行转录
                    transcription_file = simple_path
                    logger.info(f"使用复制后的文件进行转录: {transcription_file}")
                except Exception as e:
                    logger.warning(f"文件复制失败，继续使用原路径: {e}")
            
            # 转录音频
            logger.info("开始语音识别")
            logger.info(f"使用的语音服务: {provider}")
            if is_python_whisper:
                logger.info(f"当前模型: {voice_config.PYTHON_MODEL_NAME}")
            logger.info(f"转录文件路径: {transcription_file}")
            logger.info(f"转录文件大小: {os.path.getsize(transcription_file)} bytes")
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                transcription = whisper.transcribe(transcription_file)
            except Exception as whisper_error:
                logger.error(f"语音识别过程发生异常: {str(whisper_error)}")
                logger.error(f"异常堆栈: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"语音识别异常: {str(whisper_error)}"
                )
            
            # 记录结束时间和耗时
            end_time = time.time()
            duration_seconds = end_time - start_time
            logger.info(f"语音识别完成，耗时: {duration_seconds:.2f} 秒")
            
            if not transcription:
                logger.error("语音识别返回空结果")
                raise HTTPException(
                    status_code=500,
                    detail="语音识别失败"
                )
            
            logger.info(f"语音识别成功: {transcription}")
            logger.info(f"识别结果长度: {len(transcription)} 字符")
            
            return JSONResponse(
                status_code=200,
                content={
                    "code": 200,
                    "message": "语音识别成功",
                    "data": {
                        "text": transcription,
                        "duration": duration_seconds
                    }
                }
            )
            
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                logger.info(f"清理临时文件: {temp_file_path}")
                os.unlink(temp_file_path)
            if 'wav_file' in locals() and wav_file and os.path.exists(wav_file):
                logger.info(f"清理临时文件: {wav_file}")
                os.unlink(wav_file)
            # 清理复制到当前目录的文件
            if 'simple_path' in locals() and simple_path and os.path.exists(simple_path):
                try:
                    logger.info(f"清理复制的文件: {simple_path}")
                    os.unlink(simple_path)
                except Exception as e:
                    logger.warning(f"清理复制文件失败: {e}")
                
    except HTTPException as e:
        logger.error(f"HTTP错误: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"语音识别异常: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"语音识别异常: {str(e)}"
        )


@router.get("/voice/status")
async def get_voice_status():
    """
    获取语音服务状态
    
    Returns:
        JSON: 服务状态
    """
    try:
        # 获取当前语音服务
        whisper = get_voice_service()
        provider = get_voice_provider()
        
        # 获取服务状态
        status = whisper.get_status()
        status['provider'] = provider
        status['available_providers'] = [p['value'] for p in voice_config.AVAILABLE_PROVIDERS]
        
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "获取状态成功",
                "data": status
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取状态失败: {str(e)}"
        )

@router.post("/voice/config")
async def configure_voice(
    provider: str = "whisper",
    language: str = "zh",
    model: str = "medium",
    threads: int = 4
):
    """
    配置语音参数
    
    Args:
        provider: 服务提供商 (whisper or doubao)
        language: 语言代码
        model: 模型名称（仅Whisper使用）
        threads: 线程数
        
    Returns:
        JSON: 配置结果
    """
    try:
        # 更新配置
        voice_config.PROVIDER = provider
        voice_config.LANGUAGE = language
        if model:
            voice_config.PYTHON_MODEL_NAME = model
        voice_config.THREADS = threads
        
        # 更新环境变量（用于当前进程）
        os.environ['VOICE_PROVIDER'] = provider
        os.environ['VOICE_LANGUAGE'] = language
        if model:
            os.environ['PYTHON_MODEL_NAME'] = model
        os.environ['VOICE_THREADS'] = str(threads)
        
        # 重新初始化语音服务
        get_voice_service()
        
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "配置成功",
                "data": {
                    "provider": provider,
                    "language": language,
                    "model": model,
                    "threads": threads
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"配置失败: {str(e)}"
        )


@router.websocket("/voice/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    流式语音识别WebSocket端点
    
    前端通过WebSocket发送音频数据，后端实时返回识别结果
    """
    await websocket.accept()
    
    try:
        # 初始化豆包流式语音识别客户端
        doubao_streaming = DoubaoStreamingVoiceIntegration()
        
        # 检查服务是否可用
        if not doubao_streaming.is_available():
            await websocket.send_json({
                "type": "error",
                "message": "Doubao streaming voice service not available"
            })
            await websocket.close(code=1000, reason="Service not available")
            return
        
        # 处理流式连接
        await doubao_streaming.handle_stream(websocket)
        
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
            await websocket.close(code=1000, reason=str(e))
        except:
            pass
