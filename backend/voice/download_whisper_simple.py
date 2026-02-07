"""
简化版Whisper.cpp下载脚本
"""
import os
import requests
import zipfile
from pathlib import Path

# 配置
WHISPER_URL = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper.cpp-v1.5.4-windows-x64.zip"
WHISPER_DIR = Path("voice/whisper.cpp")


def download_file(url, output_path):
    """
    下载文件
    """
    print(f"开始下载: {url}")
    
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
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
        
        # 下载文件
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
            print("❌ main.exe 不存在，请检查下载是否成功")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
