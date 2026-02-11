"""
豆包语音服务测试程序
用于测试WebSocket连接和认证
"""
import logging
import uuid
import json
import websocket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 认证信息
APP_ID = "3561884959"
ACCESS_TOKEN = "qwpFoXXzYTxjIWRiWwAjGEGlc_PDyK-h"
SECRET_KEY = "Vt-BXogJIF-BWKXO7ypzEZDaVZTwdxNM"
RESOURCE_ID = "volc.bigasr.sauc.duration"
WS_URL = "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel"

def on_message(ws, message):
    """
    处理收到的消息
    """
    if isinstance(message, bytes):
        logger.info(f"✅ 收到二进制响应，大小: {len(message)} bytes")
        # 解析响应
        parse_response(message)
    else:
        logger.info(f"✅ 收到文本响应: {message}")

def on_error(ws, error):
    """
    处理错误
    """
    logger.error(f"❌ WebSocket错误: {str(error)}")

def on_close(ws, close_status_code, close_msg):
    """
    处理连接关闭
    """
    logger.info(f"❌ 连接被关闭: {close_status_code} - {close_msg}")

def on_open(ws):
    """
    处理连接打开
    """
    logger.info("✅ WebSocket连接成功!")
    
    # 构建初始化请求
    init_request = {
        "user": {
            "uid": "test_user"
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
    
    # 构建初始化消息
    init_message = build_init_message(init_request, 1)
    
    logger.info("发送初始化请求...")
    ws.send(init_message)
    logger.info("初始化请求发送成功")

def test_websocket_connection():
    """
    测试WebSocket连接
    """
    logger.info("开始测试WebSocket连接")
    logger.info(f"WebSocket URL: {WS_URL}")
    logger.info(f"APP ID: {APP_ID}")
    logger.info(f"Access Token: {ACCESS_TOKEN}")
    logger.info(f"Resource ID: {RESOURCE_ID}")
    
    # 生成连接ID
    connect_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    
    # 构建认证头
    headers = {
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": request_id,
        "X-Api-Access-Key": ACCESS_TOKEN,
        "X-Api-App-Key": APP_ID,
        "X-Api-Connect-Id": connect_id
    }
    
    logger.info(f"认证头: {headers}")
    
    try:
        logger.info("尝试建立WebSocket连接...")
        
        # 创建WebSocket应用
        ws = websocket.WebSocketApp(
            WS_URL,
            header=[f"{k}: {v}" for k, v in headers.items()],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # 运行WebSocket应用
        import threading
        
        # 设置10秒后关闭连接
        def close_after_10s():
            import time
            time.sleep(10)
            ws.close()
        
        # 启动定时器
        timer = threading.Thread(target=close_after_10s)
        timer.daemon = True
        timer.start()
        
        # 运行WebSocket应用
        ws.run_forever(ping_interval=5, ping_timeout=3)
        
        logger.info("测试完成，关闭连接")
        return True
                
    except Exception as e:
        logger.error(f"❌ 测试过程发生异常: {str(e)}", exc_info=True)
        return False

def build_init_message(payload, seq):
    """
    构建初始化消息
    """
    import gzip
    
    # 序列化并压缩
    payload_bytes = json.dumps(payload).encode('utf-8')
    compressed_payload = gzip.compress(payload_bytes)
    
    # 构建消息
    header = bytearray(4)
    header[0] = (0b0001 << 4) | 0b0001  # version 1, header size 1
    header[1] = (0b0001 << 4) | 0b0001  # full client request, with sequence
    header[2] = (0b0001 << 4) | 0b0001  # JSON serialization, gzip compression
    header[3] = 0x00  # reserved
    
    # 构建完整消息
    message = bytearray(header)
    message.extend(seq.to_bytes(4, byteorder='big', signed=False))
    message.extend(len(compressed_payload).to_bytes(4, byteorder='big'))
    message.extend(compressed_payload)
    
    return bytes(message)

def parse_response(data):
    """
    解析WebSocket响应
    """
    import gzip
    
    try:
        if len(data) < 4:
            logger.warning("响应数据太短")
            return
        
        # 解析头部
        version = (data[0] >> 4) & 0x0F
        header_size = data[0] & 0x0F
        message_type = (data[1] >> 4) & 0x0F
        flags = data[1] & 0x0F
        serialization = (data[2] >> 4) & 0x0F
        compression = data[2] & 0x0F
        
        logger.info(f"响应头部: version={version}, type={message_type}, flags={flags}")
        
        # 解析payload
        payload_start = header_size * 4
        if flags & 0x01:
            payload_start += 4
        if flags & 0x04:
            payload_start += 4
        
        if message_type == 0b1001:  # server full response
            if payload_start + 4 <= len(data):
                payload_size = int.from_bytes(data[payload_start:payload_start+4], byteorder='big')
                payload_start += 4
                
                if payload_start + payload_size <= len(data):
                    payload = data[payload_start:payload_start+payload_size]
                    
                    # 解压缩
                    if compression == 0b0001:
                        try:
                            payload = gzip.decompress(payload)
                            logger.info("payload解压缩成功")
                        except Exception as e:
                            logger.error(f"payload解压缩失败: {e}")
                            return
                    
                    # 解析JSON
                    try:
                        response_data = json.loads(payload.decode('utf-8'))
                        logger.info(f"响应数据: {json.dumps(response_data, ensure_ascii=False)}")
                    except Exception as e:
                        logger.error(f"解析响应失败: {e}")
        
        elif message_type == 0b1111:  # error response
            logger.error("收到错误响应")
            if payload_start + 8 <= len(data):
                error_code = int.from_bytes(data[payload_start:payload_start+4], byteorder='big', signed=True)
                payload_size = int.from_bytes(data[payload_start+4:payload_start+8], byteorder='big')
                payload_start += 8
                
                if payload_start + payload_size <= len(data):
                    payload = data[payload_start:payload_start+payload_size]
                    
                    if compression == 0b0001:
                        try:
                            payload = gzip.decompress(payload)
                        except Exception as e:
                            logger.error(f"错误payload解压缩失败: {e}")
                            return
                    
                    try:
                        error_data = json.loads(payload.decode('utf-8'))
                        logger.error(f"错误信息: {json.dumps(error_data, ensure_ascii=False)}")
                    except Exception as e:
                        logger.error(f"解析错误响应失败: {e}")
        
    except Exception as e:
        logger.error(f"解析响应发生异常: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("豆包语音服务测试程序")
    logger.info("=" * 50)
    
    success = test_websocket_connection()
    
    logger.info("=" * 50)
    if success:
        logger.info("✅ 测试成功! WebSocket连接正常")
    else:
        logger.info("❌ 测试失败! WebSocket连接异常")