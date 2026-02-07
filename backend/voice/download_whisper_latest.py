"""
最新版Whisper.cpp下载脚本
自动查找最新版本并下载
"""
import os
import requests
import zipfile
from pathlib import Path
import re

# 配置
GITHUB_API_URL = "https://api.github.com/repos/ggerganov/whisper.cpp/releases/latest"
WHISPER_DIR = Path("voice/whisper.cpp")
MODEL_DIR = Path("voice/models")


def get_latest_release():
    """
    获取最新的Whisper.cpp版本
    """
    print("正在查询最新的Whisper.cpp版本...")
    
    response = requests.get(GITHUB_API_URL, timeout=30)
    response.raise_for_status()
    
    release = response.json()
    tag_name = release.get("tag_name")
    
    # 查找Windows版本的下载链接
    windows_asset = None
    for asset in release.get("assets", []):
        if "windows" in asset.get("name", "").lower() and "x64" in asset.get("name", "").lower():
            windows_asset = asset
            break
    
    if not windows_asset:
        raise Exception("未找到Windows版本的Whisper.cpp")
    
    download_url = windows_asset.get("browser_download_url")
    asset_name = windows_asset.get("name")
    
    print(f"找到最新版本: {tag_name}")
    print(f"下载链接: {download_url}")
    print(f"文件名: {asset_name}")
    
    return download_url, asset_name


def download_file(url, output_path):
    """
    下载文件
    """
    print(f"开始下载: {url}")
    
    response = requests.get(url, stream=True, timeout=120)
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


def download_model():
    """
    下载模型文件
    """
    print("\n开始下载模型文件...")
    
    # 最新的模型下载地址
    model_url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-medium.bin"
    model_path = MODEL_DIR / "medium.bin"
    
    download_file(model_url, model_path)
    
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
        download_url, asset_name = get_latest_release()
        
        zip_path = WHISPER_DIR / asset_name
        download_file(download_url, zip_path)
        
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
        download_model()
        
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
