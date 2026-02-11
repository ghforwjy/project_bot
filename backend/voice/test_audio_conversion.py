"""
测试音频格式转换
测试如何将前端发送的音频数据转换为 WAV 格式
"""
import tempfile
import os
import subprocess
import struct
import wave

def test_webm_conversion():
    """测试 webm 转 wav"""
    print("=" * 50)
    print("测试1: 创建一个简单的 webm 文件并转换")
    print("=" * 50)
    
    # 创建一个测试用的 webm 文件（使用 ffmpeg 生成）
    test_webm = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
    
    # 使用 ffmpeg 生成一个测试音频
    print(f"生成测试音频: {test_webm.name}")
    result = subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=1',
        '-acodec', 'libopus', '-b:a', '64k',
        test_webm.name
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"生成测试音频失败: {result.stderr}")
        return
    
    print(f"测试音频生成成功，大小: {os.path.getsize(test_webm.name)} bytes")
    
    # 尝试转换为 wav
    test_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    print(f"\n尝试转换为 WAV: {test_wav.name}")
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', test_webm.name,
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        test_wav.name
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"转换失败: {result.stderr}")
    else:
        print(f"转换成功，输出大小: {os.path.getsize(test_wav.name)} bytes")
        
        # 检查 wav 文件头
        with open(test_wav.name, 'rb') as f:
            header = f.read(44)
            print(f"\nWAV 文件头: {header[:12]}")
            if header.startswith(b'RIFF') and header[8:12] == b'WAVEfmt ':
                print("✓ WAV 文件头正确")
            else:
                print("✗ WAV 文件头不正确")
    
    # 清理
    os.unlink(test_webm.name)
    if os.path.exists(test_wav.name):
        os.unlink(test_wav.name)


def test_wav_header_detection():
    """测试 WAV 文件头检测"""
    print("\n" + "=" * 50)
    print("测试2: WAV 文件头检测")
    print("=" * 50)
    
    # 创建一个有效的 WAV 文件
    test_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    # 使用 ffmpeg 生成测试音频
    print(f"生成测试 WAV: {test_wav.name}")
    result = subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=1',
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        test_wav.name
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"生成测试音频失败: {result.stderr}")
        return
    
    # 读取文件头
    with open(test_wav.name, 'rb') as f:
        data = f.read()
    
    print(f"文件大小: {len(data)} bytes")
    print(f"前12字节: {data[:12]}")
    print(f"是否以 RIFF 开头: {data.startswith(b'RIFF')}")
    print(f"第8-12字节是否为 WAVEfmt : {data[8:12] == b'WAVEfmt '}")
    
    # 测试检测逻辑
    is_wav = data.startswith(b'RIFF') and data[8:12] == b'WAVEfmt '
    print(f"\n检测结果: {'WAV' if is_wav else '非WAV'}")
    
    os.unlink(test_wav.name)


def test_concatenated_webm():
    """测试拼接的 webm 数据"""
    print("\n" + "=" * 50)
    print("测试3: 拼接的 webm 数据")
    print("=" * 50)
    
    # 创建两个小的 webm 文件
    webm1 = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
    webm2 = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
    
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=0.5',
        '-acodec', 'libopus', '-b:a', '64k',
        webm1.name
    ], capture_output=True)
    
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=2000:duration=0.5',
        '-acodec', 'libopus', '-b:a', '64k',
        webm2.name
    ], capture_output=True)
    
    # 读取两个文件
    with open(webm1.name, 'rb') as f:
        data1 = f.read()
    with open(webm2.name, 'rb') as f:
        data2 = f.read()
    
    print(f"文件1大小: {len(data1)} bytes")
    print(f"文件2大小: {len(data2)} bytes")
    
    # 拼接数据
    concatenated = data1 + data2
    print(f"拼接后大小: {len(concatenated)} bytes")
    
    # 尝试转换
    concatenated_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
    concatenated_file.write(concatenated)
    concatenated_file.close()
    
    test_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    print(f"\n尝试转换拼接的文件...")
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', concatenated_file.name,
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        test_wav.name
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"✗ 转换失败: {result.stderr}")
    else:
        print(f"✓ 转换成功，输出大小: {os.path.getsize(test_wav.name)} bytes")
    
    os.unlink(webm1.name)
    os.unlink(webm2.name)
    os.unlink(concatenated_file.name)
    if os.path.exists(test_wav.name):
        os.unlink(test_wav.name)


def test_media_recorder_simulation():
    """模拟 MediaRecorder 的行为"""
    print("\n" + "=" * 50)
    print("测试4: 模拟 MediaRecorder 分片发送")
    print("=" * 50)
    
    # 创建一个测试音频
    test_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=2',
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        test_wav.name
    ], capture_output=True)
    
    # 读取音频
    with open(test_wav.name, 'rb') as f:
        full_data = f.read()
    
    print(f"完整音频大小: {len(full_data)} bytes")
    
    # 模拟分片（每200ms）
    chunk_size = 16000 * 2 * 200 // 1000  # 200ms
    chunks = []
    for i in range(0, len(full_data), chunk_size):
        chunk = full_data[i:i+chunk_size]
        chunks.append(chunk)
        print(f"分片 {len(chunks)}: {len(chunk)} bytes")
    
    print(f"\n总分片数: {len(chunks)}")
    
    # 拼接分片
    reconstructed = bytearray()
    for chunk in chunks:
        reconstructed.extend(chunk)
    
    print(f"拼接后大小: {len(reconstructed)} bytes")
    print(f"是否与原始数据一致: {bytes(reconstructed) == full_data}")
    
    # 检查 WAV 文件头
    is_wav = reconstructed.startswith(b'RIFF') and reconstructed[8:12] == b'WAVEfmt '
    print(f"WAV 文件头检测: {'✓ 正确' if is_wav else '✗ 不正确'}")
    
    os.unlink(test_wav.name)


if __name__ == "__main__":
    print("音频格式转换测试程序")
    print("=" * 50)
    
    # 运行所有测试
    test_webm_conversion()
    test_wav_header_detection()
    test_concatenated_webm()
    test_media_recorder_simulation()
    
    print("\n" + "=" * 50)
    print("所有测试完成")
    print("=" * 50)
