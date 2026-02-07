"""
直接下载Whisper.cpp和模型文件
使用已知的有效下载链接
"""
import os
import requests
import zipfile
from pathlib import Path

# 配置
# 直接使用已知的有效下载链接
WHISPER_URL = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper.cpp-v1.5.4-windows-x64.zip"
MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-medium.bin"

WHISPER_DIR = Path("voice/whisper.cpp")
MODEL_DIR = Path("voice/models")


def download_file(url, output_path):
    """
    下载文件
    """
    print(f"开始下载: {url}")
    
    # 增加超时时间和重试机制
    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    
    response = session.get(url, stream=True, timeout=180)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=16384):  # 增加chunk大小
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"下载进度: {progress:.1f}%", end='\r')
    
    print(f"\n下载完成: {output_path}")


def extract_zip(zip_path, extract_dir):
    """
    解压ZIP文件
    """
    print(f"开始解压: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print(f"解压完成: {extract_dir}")


def main():
    """
    主函数
    """
    try:
        # 确保目录存在
        WHISPER_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        # 下载Whisper.cpp
        print("=== 下载Whisper.cpp ===")
        zip_path = WHISPER_DIR / "whisper.cpp.zip"
        download_file(WHISPER_URL, zip_path)
        
        # 解压文件
        extract_zip(zip_path, WHISPER_DIR)
        
        # 清理临时文件
        zip_path.unlink()
        
        print("\n✅ Whisper.cpp下载和解压完成！")
        
        # 检查main.exe是否存在
        main_exe = WHISPER_DIR / "main.exe"
        if main_exe.exists():
            print(f"✅ main.exe 存在: {main_exe}")
        else:
            # 可能在子目录中
            for root, dirs, files in os.walk(WHISPER_DIR):
                if "main.exe" in files:
                    main_exe = Path(root) / "main.exe"
                    print(f"✅ main.exe 存在: {main_exe}")
                    # 移动到根目录
                    if root != WHISPER_DIR:
                        print(f"移动 main.exe 到根目录...")
                        main_exe.rename(WHISPER_DIR / "main.exe")
                    break
            else:
                print("❌ main.exe 不存在，请检查下载是否成功")
        
        # 下载模型文件
        print("\n=== 下载模型文件 ===")
        model_path = MODEL_DIR / "medium.bin"
        download_file(MODEL_URL, model_path)
        
        print("\n✅ 模型文件下载完成！")
        
        # 检查文件大小
        if model_path.exists():
            file_size = model_path.stat().st_size / (1024 * 1024)
            print(f"✅ 模型文件大小: {file_size:.2f} MB")
            if file_size > 600:
                print("✅ 模型文件大小正常")
            else:
                print("⚠️  模型文件大小异常，可能下载不完整")
        else:
            print("❌ 模型文件不存在，请检查下载是否成功")
        
        print("\n=== 语音环境部署完成 ===")
        print("✅ Whisper.cpp 已下载并解压")
        print("✅ 模型文件 已下载")
        print("\n下一步：重启后端服务并测试语音识别功能")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
