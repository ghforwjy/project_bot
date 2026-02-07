"""
直接下载Whisper模型文件
"""
import os
import requests
from tqdm import tqdm

# 配置
# 使用GitHub作为替代源
MODEL_URL = "https://github.com/ggml-org/whisper.cpp/raw/master/models/ggml-medium.bin"
MODEL_DIR = "voice/models"
MODEL_PATH = os.path.join(MODEL_DIR, "medium.bin")


def ensure_directories():
    """
    确保目录存在
    """
    os.makedirs(MODEL_DIR, exist_ok=True)


def download_file(url: str, output_path: str):
    """
    下载文件
    
    Args:
        url: 下载URL
        output_path: 输出文件路径
    """
    print(f"开始下载模型文件: {url}")
    
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as file, tqdm(
        desc=os.path.basename(output_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    
    print(f"下载完成: {output_path}")


def main():
    """
    主函数
    """
    try:
        ensure_directories()
        
        # 下载模型文件
        download_file(MODEL_URL, MODEL_PATH)
        
        # 验证下载结果
        if os.path.exists(MODEL_PATH):
            file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)  # 转换为MB
            print(f"\n✅ 模型文件下载完成!")
            print(f"模型文件路径: {MODEL_PATH}")
            print(f"文件大小: {file_size:.2f} MB")
        else:
            print(f"\n❌ 模型文件下载失败!")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
