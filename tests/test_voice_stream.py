#!/usr/bin/env python3
"""
测试后端流式语音识别功能
"""
import asyncio
import websockets
import json
import time

async def test_voice_stream():
    """测试语音流式识别"""
    print("开始测试语音流式识别...")
    
    # WebSocket服务器URL
    url = "ws://localhost:8000/api/v1/voice/stream"
    print(f"尝试连接到: {url}")
    
    # 设置连接超时
    timeout = 5.0
    websocket = None
    
    try:
        # 连接WebSocket服务器
        print("正在建立WebSocket连接...")
        
        # 使用asyncio.wait_for设置连接超时
        websocket = await asyncio.wait_for(
            websockets.connect(url),
            timeout=timeout
        )
        
        print("WebSocket连接已建立")
        
        # 读取完整的WAV文件数据
        with open("test_audio.wav", "rb") as f:
            wav_data = f.read()
        
        print(f"WAV文件大小: {len(wav_data)} bytes")
        
        # 分块发送音频数据
        chunk_size = 32000  # 每次发送约1秒的音频数据
        for i in range(0, len(wav_data), chunk_size):
            chunk = wav_data[i:i+chunk_size]
            print(f"发送音频数据: {len(chunk)} bytes")
            await websocket.send(chunk)
            
            # 等待服务器返回结果
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                result = json.loads(response)
                if result.get("type") == "recognition_result":
                    print(f"识别结果: {result.get('text')}")
                elif result.get("type") == "error":
                    print(f"错误: {result.get('message')}")
                    break
            except asyncio.TimeoutError:
                # 超时，继续发送数据
                pass
            
            # 模拟实时录音，添加短暂延迟
            time.sleep(0.2)
        
        # 发送结束信号
        print("发送结束信号")
        await websocket.send(b"END")
        
        # 等待最终结果，设置超时
        try:
            # 只等待最多5秒的最终结果
            async with asyncio.timeout(5.0):
                while True:
                    response = await websocket.recv()
                    result = json.loads(response)
                    if result.get("type") == "recognition_result":
                        print(f"最终识别结果: {result.get('text')}")
                    elif result.get("type") == "error":
                        print(f"错误: {result.get('message')}")
                        break
        except asyncio.TimeoutError:
            print("等待最终结果超时，结束测试")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
            
    except asyncio.TimeoutError:
        print(f"连接WebSocket服务器超时（{timeout}秒）")
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        # 确保WebSocket连接被关闭
        if websocket:
            try:
                await websocket.close()
                print("WebSocket连接已关闭")
            except:
                pass
    
    print("测试完成")

if __name__ == "__main__":
    # 检查测试音频文件是否存在
    import os
    if not os.path.exists("test_audio.wav"):
        print("错误: 测试音频文件 test_audio.wav 不存在")
        print("请创建一个16kHz采样率、1通道、16位的WAV音频文件用于测试")
        exit(1)
    
    # 运行测试
    asyncio.run(test_voice_stream())
