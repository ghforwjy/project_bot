"""
下载Whisper.cpp和模型文件
"""
import os
import requests
import zipfile
import tempfile
from tqdm import tqdm

# 配置
WHISPER_RELEASE_URL = "https://github.com/ggml-org/whisper.cpp/releases/download/v1.8.3/whisper.cpp-v1.8.3-windows-x64.zip"
MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-medium.bin"

WHISPER_DIR = "voice/whisper.cpp"
MODEL_DIR = "voice/models"
MODEL_PATH = os.path.join(MODEL_DIR, "medium.bin")


def ensure_directories():
    """确保目录存在"""
    os.makedirs(WHISPER_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)


def download_file(url: str, output_path: str):
    """
    下载文件
    
    Args:
        url: 下载URL
        output_path: 输出文件路径
    """
    print(f"开始下载: {url}")
    
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


def extract_zip(zip_path: str, extract_dir: str):
    """
    解压ZIP文件
    
    Args:
        zip_path: ZIP文件路径
        extract_dir: 解压目录
    """
    print(f"开始解压: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print(f"解压完成: {extract_dir}")


def main():
    """主函数"""
    try:
        ensure_directories()
        
        # 下载Whisper.cpp
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
            temp_zip_path = temp_zip.name
        
        download_file(WHISPER_RELEASE_URL, temp_zip_path)
        extract_zip(temp_zip_path, WHISPER_DIR)
        
        # 清理临时文件
        if os.path.exists(temp_zip_path):
            os.unlink(temp_zip_path)
        
        # 下载模型文件
        download_file(MODEL_URL, MODEL_PATH)
        
        # 验证下载结果
        main_exe = os.path.join(WHISPER_DIR, "main.exe")
        
        if os.path.exists(main_exe) and os.path.exists(MODEL_PATH):
            print("\n✅ 下载配置完成!")
            print(f"Whisper.cpp 路径: {main_exe}")
            print(f"模型文件路径: {MODEL_PATH}")
        else:
            print("\n❌ 下载配置失败!")
            print(f"检查文件是否存在:")
            print(f"- main.exe: {os.path.exists(main_exe)}")
            print(f"- medium.bin: {os.path.exists(MODEL_PATH)}")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
