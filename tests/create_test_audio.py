#!/usr/bin/env python3
"""
创建测试音频文件
"""
import wave
import numpy as np

# 配置参数
sample_rate = 16000  # 16kHz采样率
channels = 1         # 1通道
width = 2            # 16位
seconds = 3          # 3秒音频

# 创建WAV文件
with wave.open('test_audio.wav', 'w') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(width)
    wf.setframerate(sample_rate)
    
    # 生成简单的正弦波
    for i in range(seconds * sample_rate):
        # 440Hz的正弦波
        value = int(32767 * np.sin(2 * np.pi * 440 * i / sample_rate))
        # 转换为16位PCM
        wf.writeframes(value.to_bytes(2, byteorder='little', signed=True))

print("测试音频文件已创建: test_audio.wav")
print(f"采样率: {sample_rate}Hz")
print(f"通道数: {channels}")
print(f"位深度: {width * 8}位")
print(f"时长: {seconds}秒")
