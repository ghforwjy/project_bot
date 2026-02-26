"""
便携式打包脚本 - 将项目打包成可独立运行的便携版
使用方法: python build_portable.py
"""
import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
RELEASE_DIR = PROJECT_ROOT / "release"
PYTHON_VERSION = "3.11.9"
PYTHON_EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

def log(msg):
    print(f"[BUILD] {msg}")

def clean_release():
    """清理 release 目录"""
    if RELEASE_DIR.exists():
        log(f"清理 release 目录: {RELEASE_DIR}")
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, dest):
    """下载文件"""
    log(f"下载: {url}")
    urllib.request.urlretrieve(url, dest)

def setup_embedded_python():
    """设置嵌入式 Python 环境"""
    python_dir = RELEASE_DIR / "python"
    python_dir.mkdir(exist_ok=True)
    
    python_zip = RELEASE_DIR / "python_embed.zip"
    if not python_zip.exists():
        download_file(PYTHON_EMBED_URL, python_zip)
    
    log("解压 Python 嵌入式版本...")
    with zipfile.ZipFile(python_zip, 'r') as zip_ref:
        zip_ref.extractall(python_dir)
    python_zip.unlink()
    
    get_pip = python_dir / "get-pip.py"
    download_file(GET_PIP_URL, get_pip)
    
    pth_file = python_dir / f"python{PYTHON_VERSION.replace('.', '')}._pth"
    if pth_file.exists():
        log("修改 ._pth 文件以启用 site-packages...")
        with open(pth_file, 'a', encoding='utf-8') as f:
            f.write("\nimport site\n")
    
    log("安装 pip...")
    python_exe = python_dir / "python.exe"
    subprocess.run([str(python_exe), str(get_pip), "--no-warn-script-location"], 
                   check=True, cwd=str(python_dir))
    
    return python_dir

def install_dependencies(python_dir):
    """安装项目依赖"""
    log("安装项目依赖...")
    python_exe = python_dir / "python.exe"
    requirements = PROJECT_ROOT / "requirements.txt"
    
    subprocess.run([
        str(python_exe), "-m", "pip", "install", 
        "-r", str(requirements),
        "--target", str(python_dir / "Lib" / "site-packages"),
        "--no-warn-script-location",
        "-q"
    ], check=True)

def copy_backend():
    """复制后端代码"""
    log("复制后端代码...")
    backend_src = PROJECT_ROOT / "backend"
    backend_dst = RELEASE_DIR / "backend"
    
    ignore_patterns = [
        "__pycache__", "*.pyc", "*.pyo", ".pytest_cache",
        "tests", "*.db", "*.sqlite", "*.log", "whisper.cpp-source",
        "models/*.bin"
    ]
    
    def ignore_func(directory, contents):
        ignored