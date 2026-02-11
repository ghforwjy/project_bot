import asyncio
import aiohttp
import json
import struct
import gzip
import uuid
import logging
import os
import subprocess
import pyaudio
from typing import Optional, List, Dict, Any, Tuple, AsyncGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 常量定义
DEFAULT_SAMPLE_RATE = 16000

class ProtocolVersion:
    V1 = 0b0001

class MessageType:
    CLIENT_FULL_REQUEST = 0b0001
    CLIENT_AUDIO_ONLY_REQUEST = 0b0010
    SERVER_FULL_RESPONSE = 0b1001
    SERVER_ERROR_RESPONSE = 0b1111

class MessageTypeSpecificFlags:
    NO_SEQUENCE = 0b0000
    POS_SEQUENCE = 0b0001
    NEG_SEQUENCE = 0b0010
    NEG_WITH_SEQUENCE = 0b0011

class SerializationType:
    NO_SERIALIZATION = 0b0000
    JSON = 0b0001

class CompressionType:
    GZIP = 0b0001


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

class CommonUtils:
    @staticmethod
    def gzip_compress(data: bytes) -> bytes:
        return gzip.compress(data)

    @staticmethod
    def gzip_decompress(data: bytes) -> bytes:
        return gzip.decompress(data)

    @staticmethod
    def judge_wav(data: bytes) -> bool:
        if len(data) < 44:
            return False
        return data[:4] == b'RIFF' and data[8:12] == b'WAVE'

    @staticmethod
    def convert_wav_with_path(audio_path: str, sample_rate: int = DEFAULT_SAMPLE_RATE) -> bytes:
        try:
            cmd = [
                "ffmpeg", "-v", "quiet", "-y", "-i", audio_path,
                "-acodec", "pcm_s16le", "-ac", "1", "-ar", str(sample_rate),
                "-f", "wav", "-"
            ]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 尝试删除原始文件
            try:
                os.remove(audio_path)
            except OSError as e:
                logger.warning(f"Failed to remove original file: {e}")
                
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr.decode()}")
            raise RuntimeError(f"Audio conversion failed: {e.stderr.decode()}")

    @staticmethod
    def read_wav_info(data: bytes) -> Tuple[int, int, int, int, bytes]:
        if len(data) < 44:
            raise ValueError("Invalid WAV file: too short")
            
        # 解析WAV头
        chunk_id = data[:4]
        if chunk_id != b'RIFF':
            raise ValueError("Invalid WAV file: not RIFF format")
            
        format_ = data[8:12]
        if format_ != b'WAVE':
            raise ValueError("Invalid WAV file: not WAVE format")
            
        # 查找fmt子块
        pos = 12
        fmt_found = False
        audio_format = 0
        num_channels = 0
        sample_rate = 0
        bits_per_sample = 0
        
        while pos < len(data) - 8:
            subchunk_id = data[pos:pos+4]
            subchunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            
            if subchunk_id == b'fmt ':
                # 解析fmt子块
                audio_format = struct.unpack('<H', data[pos+8:pos+10])[0]
                num_channels = struct.unpack('<H', data[pos+10:pos+12])[0]
                sample_rate = struct.unpack('<I', data[pos+12:pos+16])[0]
                bits_per_sample = struct.unpack('<H', data[pos+22:pos+24])[0]
                fmt_found = True
            elif subchunk_id == b'data':
                # 找到data子块
                if not fmt_found:
                    raise ValueError("Invalid WAV file: fmt subchunk not found")
                
                wave_data = data[pos+8:pos+8+subchunk_size]
                return (
                    num_channels,
                    bits_per_sample // 8,
                    sample_rate,
                    subchunk_size // (num_channels * (bits_per_sample // 8)),
                    wave_data
                )
            
            # 跳过当前子块
            pos += 8 + subchunk_size
            
        raise ValueError("Invalid WAV file: no data subchunk found")

class AsrRequestHeader:
    def __init__(self):
        self.message_type = MessageType.CLIENT_FULL_REQUEST
        self.message_type_specific_flags = MessageTypeSpecificFlags.POS_SEQUENCE
        self.serialization_type = SerializationType.JSON
        self.compression_type = CompressionType.GZIP
        self.reserved_data = bytes([0x00])

    def with_message_type(self, message_type: int) -> 'AsrRequestHeader':
        self.message_type = message_type
        return self

    def with_message_type_specific_flags(self, flags: int) -> 'AsrRequestHeader':
        self.message_type_specific_flags = flags
        return self

    def with_serialization_type(self, serialization_type: int) -> 'AsrRequestHeader':
        self.serialization_type = serialization_type
        return self

    def with_compression_type(self, compression_type: int) -> 'AsrRequestHeader':
        self.compression_type = compression_type
        return self

    def with_reserved_data(self, reserved_data: bytes) -> 'AsrRequestHeader':
        self.reserved_data = reserved_data
        return self

    def to_bytes(self) -> bytes:
        header = bytearray()
        header.append((ProtocolVersion.V1 << 4) | 1)
        header.append((self.message_type << 4) | self.message_type_specific_flags)
        header.append((self.serialization_type << 4) | self.compression_type)
        header.extend(self.reserved_data)
        return bytes(header)

    @staticmethod
    def default_header() -> 'AsrRequestHeader':
        return AsrRequestHeader()

class RequestBuilder:
    @staticmethod
    def new_auth_headers() -> Dict[str, str]:
        reqid = str(uuid.uuid4())
        return {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Request-Id": reqid,
            "X-Api-Access-Key": config.access_key,
            "X-Api-App-Key": config.app_key
        }

    @staticmethod
    def new_full_client_request(seq: int) -> bytes:  # 添加seq参数
        header = AsrRequestHeader.default_header() \
            .with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        
        payload = {
            "user": {
                "uid": "demo_uid"
            },
            "audio": {
                "format": "wav",
                "codec": "raw",
                "rate": 16000,
                "bits": 16,
                "channel": 1
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
                "show_utterances": True,
                "enable_nonstream": False
            }
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        compressed_payload = CommonUtils.gzip_compress(payload_bytes)
        payload_size = len(compressed_payload)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))  # 使用传入的seq
        request.extend(struct.pack('>I', payload_size))
        request.extend(compressed_payload)
        
        return bytes(request)

    @staticmethod
    def new_audio_only_request(seq: int, segment: bytes, is_last: bool = False) -> bytes:
        header = AsrRequestHeader.default_header()
        if is_last:  # 最后一个包特殊处理
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.NEG_WITH_SEQUENCE)
            seq = -seq  # 设为负值
        else:
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        header.with_message_type(MessageType.CLIENT_AUDIO_ONLY_REQUEST)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))
        
        compressed_segment = CommonUtils.gzip_compress(segment)
        request.extend(struct.pack('>I', len(compressed_segment)))
        request.extend(compressed_segment)
        
        return bytes(request)

class AsrResponse:
    def __init__(self):
        self.code = 0
        self.event = 0
        self.is_last_package = False
        self.payload_sequence = 0
        self.payload_size = 0
        self.payload_msg = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "event": self.event,
            "is_last_package": self.is_last_package,
            "payload_sequence": self.payload_sequence,
            "payload_size": self.payload_size,
            "payload_msg": self.payload_msg
        }

class ResponseParser:
    @staticmethod
    def parse_response(msg: bytes) -> AsrResponse:
        response = AsrResponse()
        
        header_size = msg[0] & 0x0f
        message_type = msg[1] >> 4
        message_type_specific_flags = msg[1] & 0x0f
        serialization_method = msg[2] >> 4
        message_compression = msg[2] & 0x0f
        
        payload = msg[header_size*4:]
        
        # 解析message_type_specific_flags
        if message_type_specific_flags & 0x01:
            response.payload_sequence = struct.unpack('>i', payload[:4])[0]
            payload = payload[4:]
        if message_type_specific_flags & 0x02:
            response.is_last_package = True
        if message_type_specific_flags & 0x04:
            response.event = struct.unpack('>i', payload[:4])[0]
            payload = payload[4:]
            
        # 解析message_type
        if message_type == MessageType.SERVER_FULL_RESPONSE:
            response.payload_size = struct.unpack('>I', payload[:4])[0]
            payload = payload[4:]
        elif message_type == MessageType.SERVER_ERROR_RESPONSE:
            response.code = struct.unpack('>i', payload[:4])[0]
            response.payload_size = struct.unpack('>I', payload[4:8])[0]
            payload = payload[8:]
            
        if not payload:
            return response
            
        # 解压缩
        if message_compression == CompressionType.GZIP:
            try:
                payload = CommonUtils.gzip_decompress(payload)
            except Exception as e:
                logger.error(f"Failed to decompress payload: {e}")
                return response
                
        # 解析payload
        try:
            if serialization_method == SerializationType.JSON:
                response.payload_msg = json.loads(payload.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to parse payload: {e}")
            
        return response

class AsrWsClient:
    def __init__(self, url: str, segment_duration: int = 200):
        self.seq = 1
        self.url = url
        self.segment_duration = segment_duration
        self.conn = None
        self.session = None  # 添加session引用
        self.recording = False  # 添加录音标志

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.conn and not self.conn.closed:
            await self.conn.close()
        if self.session and not self.session.closed:
            await self.session.close()
        
    async def read_audio_data(self, file_path: str) -> bytes:
        try:
            # 无论音频文件是什么格式，都将其转换为16000 Hz、1通道、16位的WAV格式
            logger.info("Converting audio to 16kHz, 1-channel, 16-bit WAV format...")
            content = CommonUtils.convert_wav_with_path(file_path, 16000)
            
            return content
        except Exception as e:
            logger.error(f"Failed to read audio data: {e}")
            raise
            
    def get_segment_size(self, content: bytes) -> int:
        try:
            channel_num, samp_width, frame_rate, _, _ = CommonUtils.read_wav_info(content)[:5]
            size_per_sec = channel_num * samp_width * frame_rate
            segment_size = size_per_sec * self.segment_duration // 1000
            return segment_size
        except Exception as e:
            logger.error(f"Failed to calculate segment size: {e}")
            raise
            
    async def create_connection(self) -> None:
        headers = RequestBuilder.new_auth_headers()
        try:
            self.conn = await self.session.ws_connect(  # 使用self.session
                self.url,
                headers=headers
            )
            logger.info(f"Connected to {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise
            
    async def send_full_client_request(self) -> None:
        request = RequestBuilder.new_full_client_request(self.seq)
        self.seq += 1  # 发送后递增
        try:
            await self.conn.send_bytes(request)
            logger.info(f"Sent full client request with seq: {self.seq-1}")
            
            msg = await self.conn.receive()
            if msg.type == aiohttp.WSMsgType.BINARY:
                response = ResponseParser.parse_response(msg.data)
                logger.info(f"Received response: {response.to_dict()}")
            else:
                logger.error(f"Unexpected message type: {msg.type}")
        except Exception as e:
            logger.error(f"Failed to send full client request: {e}")
            raise
            
    async def send_messages(self, segment_size: int, content: bytes) -> AsyncGenerator[None, None]:
        audio_segments = self.split_audio(content, segment_size)
        total_segments = len(audio_segments)
        
        for i, segment in enumerate(audio_segments):
            is_last = (i == total_segments - 1)
            request = RequestBuilder.new_audio_only_request(
                self.seq, 
                segment,
                is_last=is_last
            )
            await self.conn.send_bytes(request)
            logger.info(f"Sent audio segment with seq: {self.seq} (last: {is_last})")
            
            if not is_last:
                self.seq += 1
                
            await asyncio.sleep(self.segment_duration / 1000) # 逐个发送，间隔时间模拟实时流
            # 让出控制权，允许接受消息
            yield
            
    async def recv_messages(self) -> AsyncGenerator[AsrResponse, None]:
        try:
            async for msg in self.conn:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    response = ResponseParser.parse_response(msg.data)
                    yield response
                    
                    if response.is_last_package or response.code != 0:
                        break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {msg.data}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.info("WebSocket connection closed")
                    break
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            raise
            
    async def start_audio_stream(self, segment_size: int, content: bytes) -> AsyncGenerator[AsrResponse, None]:
        async def sender():
            async for _ in self.send_messages(segment_size, content):
                pass
                
        # 启动发送和接收任务
        sender_task = asyncio.create_task(sender())
        
        try:
            async for response in self.recv_messages():
                yield response
        finally:
            sender_task.cancel()
            try:
                await sender_task
            except asyncio.CancelledError:
                pass
                
    @staticmethod
    def split_audio(data: bytes, segment_size: int) -> List[bytes]:
        if segment_size <= 0:
            return []
            
        segments = []
        for i in range(0, len(data), segment_size):
            end = i + segment_size
            if end > len(data):
                end = len(data)
            segments.append(data[i:end])
        return segments
        
    def detect_and_record(self, rate=16000, channels=1, width=2, chunk=1024, silence_threshold=1000, silence_duration=2.0):
        """
        检测语音并录音（同步方法，在后台线程中运行）
        - 等待检测到语音（音量超过阈值）
        - 检测到语音后开始录音
        - 检测到停顿（静音）后停止录音
        """
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def create_wav_header(data_size: int, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
            """创建WAV文件头"""
            byte_rate = sample_rate * channels * bits_per_sample // 8
            block_align = channels * bits_per_sample // 8
            
            header = bytearray()
            # RIFF chunk
            header.extend(b'RIFF')
            header.extend(struct.pack('<I', 36 + data_size))  # Chunk size
            header.extend(b'WAVE')
            # fmt sub-chunk
            header.extend(b'fmt ')
            header.extend(struct.pack('<I', 16))  # Subchunk1Size (16 for PCM)
            header.extend(struct.pack('<H', 1))   # AudioFormat (1 for PCM)
            header.extend(struct.pack('<H', channels))  # NumChannels
            header.extend(struct.pack('<I', sample_rate))  # SampleRate
            header.extend(struct.pack('<I', byte_rate))  # ByteRate
            header.extend(struct.pack('<H', block_align))  # BlockAlign
            header.extend(struct.pack('<H', bits_per_sample))  # BitsPerSample
            # data sub-chunk
            header.extend(b'data')
            header.extend(struct.pack('<I', data_size))  # Subchunk2Size
            
            return bytes(header)
        
        def record_thread():
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(width),
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=chunk)
            
            try:
                silence_counter = 0
                recording = False
                chunk_duration = chunk / rate  # 每个chunk的持续时间（秒）
                audio_buffer = bytearray()  # 用于累积音频数据
                
                chunk_count = 0
                max_recording_duration = 30  # 最大录音时长30秒
                recording_start_time = None
                
                while True:
                    data = stream.read(chunk)
                    chunk_count += 1
                    
                    # 计算音频能量
                    audio_energy = sum(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                    for i in range(0, len(data), 2))
                    
                    # 每100个chunk打印一次音频能量（用于调试）
                    if chunk_count % 100 == 0:
                        logger.info(f"音频能量: {audio_energy}, 阈值: {silence_threshold}, 录音状态: {recording}")
                    
                    if not recording:
                        # 检测是否开始说话
                        if audio_energy > silence_threshold:
                            recording = True
                            recording_start_time = chunk_count * chunk_duration
                            logger.info(f"检测到语音，开始录音... (音频能量: {audio_energy})")
                            silence_counter = 0
                            audio_buffer.extend(data)
                    else:
                        # 正在录音，检测是否停顿
                        current_duration = chunk_count * chunk_duration - recording_start_time
                        
                        # 检查是否超过最大录音时长
                        if current_duration >= max_recording_duration:
                            logger.info(f"录音超过最大时长{max_recording_duration}秒，自动结束")
                            wav_data = create_wav_header(len(audio_buffer)) + bytes(audio_buffer)
                            result_queue.put(('done', wav_data))
                            break
                        
                        if audio_energy > silence_threshold:
                            silence_counter = 0
                            audio_buffer.extend(data)
                            if chunk_count % 50 == 0:  # 减少日志输出频率
                                logger.info(f"继续录音... (时长: {current_duration:.1f}s, 缓冲区大小: {len(audio_buffer)})")
                        else:
                            silence_counter += chunk_duration
                            if silence_counter >= silence_duration:
                                # 检测到停顿，停止录音
                                logger.info(f"检测到停顿，录音结束 (总时长: {current_duration:.1f}s)")
                                recording = False
                                silence_counter = 0
                                
                                # 将累积的音频数据包装成WAV格式
                                wav_data = create_wav_header(len(audio_buffer)) + bytes(audio_buffer)
                                
                                result_queue.put(('done', wav_data))
                                break
                            else:
                                # 还在停顿检测中，继续累积数据
                                audio_buffer.extend(data)
                    
                    # 短暂休眠，避免占用过多CPU
                    import time
                    time.sleep(0.01)
            
            finally:
                logger.info("录音结束")
                stream.stop_stream()
                stream.close()
                p.terminate()
        
        # 启动录音线程
        thread = threading.Thread(target=record_thread)
        thread.start()
        
        # 等待录音完成
        thread.join()
        
        # 获取结果
        status, wav_data = result_queue.get()
        return wav_data

    async def execute_realtime_streaming(self) -> AsyncGenerator[AsrResponse, None]:
        """
        实时流式语音识别
        流程：建立连接 -> 发送初始化 -> 一边录音一边发送 -> 一边接收识别结果
        """
        if not self.url:
            raise ValueError("URL is empty")
            
        self.seq = 1
        
        try:
            # 1. 创建WebSocket连接
            logger.info("步骤1: 建立WebSocket连接...")
            await self.create_connection()
            
            # 2. 发送完整客户端请求
            logger.info("步骤2: 发送初始化请求...")
            await self.send_full_client_request()
            
            # 3. 启动录音和流式发送（在后台线程中录音，通过队列传递数据）
            logger.info("步骤3: 开始录音并流式发送...")
            import threading
            import queue
            
            audio_queue = queue.Queue()
            stop_recording = threading.Event()
            
            def record_and_stream():
                """录音线程：持续录音，将数据放入队列"""
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=16000,
                                input=True,
                                frames_per_buffer=1024)
                
                logger.info("录音线程已启动，请开始说话...")
                
                try:
                    silence_counter = 0
                    recording = False
                    chunk_duration = 1024 / 16000  # 每个chunk的持续时间（秒）
                    chunk_count = 0
                    max_silence = 2.0  # 停顿2秒结束录音
                    
                    while not stop_recording.is_set():
                        data = stream.read(1024, exception_on_overflow=False)
                        chunk_count += 1
                        
                        # 计算音频能量
                        audio_energy = sum(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                        for i in range(0, len(data), 2))
                        
                        if not recording:
                            # 检测是否开始说话
                            if audio_energy > 1000:
                                recording = True
                                logger.info(f"检测到语音，开始录音...")
                                audio_queue.put(('audio', data))
                        else:
                            # 正在录音
                            if audio_energy > 1000:
                                silence_counter = 0
                                audio_queue.put(('audio', data))
                            else:
                                silence_counter += chunk_duration
                                if silence_counter >= max_silence:
                                    # 检测到停顿，结束录音
                                    logger.info(f"检测到停顿，录音结束")
                                    audio_queue.put(('done', None))
                                    break
                                else:
                                    # 还在停顿检测中，继续发送
                                    audio_queue.put(('audio', data))
                    
                    if not recording:
                        # 一直没有检测到语音
                        logger.info("未检测到语音")
                        audio_queue.put(('done', None))
                        
                finally:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    logger.info("录音线程已结束")
            
            # 启动录音线程
            record_thread = threading.Thread(target=record_and_stream)
            record_thread.start()
            
            # 4. 从队列读取音频数据并发送，同时接收识别结果
            logger.info("步骤4: 流式发送音频并接收识别结果...")
            
            sending_done = False
            
            async def send_audio():
                """异步任务：从队列读取音频并发送"""
                nonlocal sending_done
                audio_buffer = bytearray()
                
                def create_wav_header(data_size: int) -> bytes:
                    """创建WAV文件头"""
                    sample_rate = 16000
                    channels = 1
                    bits_per_sample = 16
                    byte_rate = sample_rate * channels * bits_per_sample // 8
                    block_align = channels * bits_per_sample // 8
                    
                    header = bytearray()
                    header.extend(b'RIFF')
                    header.extend(struct.pack('<I', 36 + data_size))
                    header.extend(b'WAVE')
                    header.extend(b'fmt ')
                    header.extend(struct.pack('<I', 16))
                    header.extend(struct.pack('<H', 1))
                    header.extend(struct.pack('<H', channels))
                    header.extend(struct.pack('<I', sample_rate))
                    header.extend(struct.pack('<I', byte_rate))
                    header.extend(struct.pack('<H', block_align))
                    header.extend(struct.pack('<H', bits_per_sample))
                    header.extend(b'data')
                    header.extend(struct.pack('<I', data_size))
                    return bytes(header)
                
                while not sending_done:
                    try:
                        # 使用 asyncio 的 run_in_executor 来从同步队列读取
                        loop = asyncio.get_event_loop()
                        msg_type, data = await loop.run_in_executor(None, audio_queue.get, True, 0.1)
                        
                        if msg_type == 'audio':
                            # 累积音频数据
                            audio_buffer.extend(data)
                            
                            # 每累积约1秒的数据就发送一次（16000 * 2 = 32000 bytes）
                            if len(audio_buffer) >= 32000:
                                # 包装成WAV格式
                                wav_data = create_wav_header(len(audio_buffer)) + bytes(audio_buffer)
                                
                                # 发送音频数据
                                request = RequestBuilder.new_audio_only_request(
                                    self.seq, 
                                    wav_data,
                                    is_last=False
                                )
                                await self.conn.send_bytes(request)
                                logger.info(f"发送音频包 seq={self.seq}, size={len(wav_data)}")
                                self.seq += 1
                                
                                # 清空缓冲区
                                audio_buffer.clear()
                                
                        elif msg_type == 'done':
                            # 录音结束，发送最后一个包
                            if len(audio_buffer) > 0:
                                wav_data = create_wav_header(len(audio_buffer)) + bytes(audio_buffer)
                                request = RequestBuilder.new_audio_only_request(
                                    self.seq, 
                                    wav_data,
                                    is_last=True
                                )
                                await self.conn.send_bytes(request)
                                logger.info(f"发送最后一个音频包 seq={self.seq}, size={len(wav_data)}")
                                self.seq += 1
                            else:
                                # 发送空包作为结束标记
                                request = RequestBuilder.new_audio_only_request(
                                    self.seq, 
                                    b'',
                                    is_last=True
                                )
                                await self.conn.send_bytes(request)
                                logger.info("发送空包结束")
                            
                            sending_done = True
                            break
                    except queue.Empty:
                        await asyncio.sleep(0.01)
                        continue
            
            # 启动发送任务
            send_task = asyncio.create_task(send_audio())
            
            # 接收识别结果
            try:
                async for msg in self.conn:
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        response = ResponseParser.parse_response(msg.data)
                        yield response
                        
                        # 打印识别结果
                        if response.payload_msg:
                            if 'result' in response.payload_msg:
                                result_text = response.payload_msg['result'].get('text', '')
                                if result_text:
                                    logger.info(f"【识别结果】: {result_text}")
                            elif 'error' in response.payload_msg:
                                logger.error(f"识别错误: {response.payload_msg['error']}")
                        
                        # 检查是否收到最终响应
                        if response.is_last_package:
                            logger.info("收到最终识别结果")
                            break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket错误: {msg.data}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        logger.info("WebSocket连接已关闭")
                        break
            finally:
                # 停止发送任务
                sending_done = True
                await send_task
                stop_recording.set()
                record_thread.join()
                  
        except Exception as e:
            logger.error(f"ASR执行错误: {e}")
            raise
        finally:
            if self.conn:
                await self.conn.close()

    async def execute(self, file_path: str) -> AsyncGenerator[AsrResponse, None]:
        if not file_path:
            raise ValueError("File path is empty")
            
        if not self.url:
            raise ValueError("URL is empty")
            
        self.seq = 1
        
        try:
            # 1. 读取音频文件
            content = await self.read_audio_data(file_path)
            
            # 2. 计算分段大小
            segment_size = self.get_segment_size(content)
            
            # 3. 创建WebSocket连接
            await self.create_connection()
            
            # 4. 发送完整客户端请求
            await self.send_full_client_request()
            
            # 5. 启动音频流处理
            async for response in self.start_audio_stream(segment_size, content):
                yield response
                
        except Exception as e:
            logger.error(f"Error in ASR execution: {e}")
            raise
        finally:
            if self.conn:
                await self.conn.close()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ASR WebSocket Client")
    parser.add_argument("--file", type=str, help="Audio file path")
    parser.add_argument("--realtime", action="store_true", help="Use real-time audio input")

    #wss://openspeech.bytedance.com/api/v3/sauc/bigmodel
    #wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async
    #wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_nostream
    parser.add_argument("--url", type=str, default="wss://openspeech.bytedance.com/api/v3/sauc/bigmodel", 
                       help="WebSocket URL")
    parser.add_argument("--seg-duration", type=int, default=200, 
                       help="Audio duration(ms) per packet, default:200")
    
    args = parser.parse_args()
    
    if not args.file and not args.realtime:
        parser.error("Either --file or --realtime must be specified")
    
    async with AsrWsClient(args.url, args.seg_duration) as client:  # 使用async with
        try:
            if args.realtime:
                logger.info("Starting real-time streaming ASR processing...")
                async for response in client.execute_realtime_streaming():
                    # 识别结果已经在方法内部打印了，这里可以选择是否打印详细响应
                    pass
            else:
                async for response in client.execute(args.file):
                    logger.info(f"Received response: {json.dumps(response.to_dict(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"ASR processing failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

    # 用法：
    # python3 sauc_websocket_demo.py --file /Users/bytedance/code/python/eng_ddc_itn.wav