"""
下载Whisper.cpp源代码并提供编译指南
"""
import os
import requests
import zipfile
import tempfile
from tqdm import tqdm

# 配置
WHISPER_SOURCE_URL = "https://github.com/ggml-org/whisper.cpp/archive/refs/heads/master.zip"
SOURCE_DIR = "voice/whisper.cpp-source"


def ensure_directories():
    """
    确保目录存在
    """
    os.makedirs(SOURCE_DIR, exist_ok=True)


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


def create_compile_guide():
    """
    创建编译指南
    """
    guide_content = """
# Whisper.cpp 编译指南

## 前提条件
1. 安装 Visual Studio 2022 或更高版本（带 C++ 开发工具）
2. 安装 CMake
3. 安装 Git

## 编译步骤

### 方法 1: 使用 Visual Studio
1. 打开 Visual Studio
2. 选择 "文件" -> "打开" -> "文件夹"
3. 浏览到 `voice/whisper.cpp-source/whisper.cpp-master` 目录
4. Visual Studio 会自动检测 CMake 项目
5. 等待 CMake 配置完成
6. 选择 "生成" -> "生成解决方案"

### 方法 2: 使用 CMake 命令行
1. 打开命令提示符或 PowerShell
2. 导航到源代码目录：
   ```
   cd voice/whisper.cpp-source/whisper.cpp-master
   ```
3. 创建构建目录：
   ```
   mkdir build
   cd build
   ```
4. 配置 CMake：
   ```
   cmake ..
   ```
5. 编译项目：
   ```
   cmake --build . --config Release
   ```

## 编译完成后
编译完成后，可执行文件会在 `build/Release` 目录中生成。

## 下载模型文件
编译完成后，需要下载模型文件：
1. 导航到源代码目录：
   ```
   cd voice/whisper.cpp-source/whisper.cpp-master
   ```
2. 运行模型下载脚本：
   ```
   python models/download-ggml-model.py medium
   ```

## 配置路径
编译完成后，需要更新 `config.py` 中的路径配置：
- WHISPER_PATH: 指向编译生成的可执行文件目录
- MODEL_PATH: 指向下载的模型文件路径

## 故障排除
- 如果编译失败，请确保已安装所有必要的依赖项
- 如果遇到 CMake 配置错误，请检查 Visual Studio 是否正确安装
- 如果模型下载失败，可以手动从 Hugging Face 下载：
  https://huggingface.co/ggerganov/whisper.cpp/tree/main/models

"""
    
    guide_path = os.path.join(SOURCE_DIR, "COMPILE_GUIDE.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"编译指南已创建: {guide_path}")


def main():
    """
    主函数
    """
    try:
        ensure_directories()
        
        # 下载源代码
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
            temp_zip_path = temp_zip.name
        
        download_file(WHISPER_SOURCE_URL, temp_zip_path)
        extract_zip(temp_zip_path, SOURCE_DIR)
        
        # 清理临时文件
        if os.path.exists(temp_zip_path):
            os.unlink(temp_zip_path)
        
        # 创建编译指南
        create_compile_guide()
        
        print("\n✅ 源代码下载完成!")
        print("请按照 COMPILE_GUIDE.md 的说明进行编译")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
