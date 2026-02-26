"""
Nuitka 打包脚本 - 将 Python 后端编译成可执行文件

使用方法:
    python build_nuitka.py              # 默认: onefile 模式 (单个 exe)
    python build_nuitka.py --standalone # standalone 模式 (目录)
    python build_nuitka.py --onefile    # onefile 模式 (单个 exe)
    python build_nuitka.py --help       # 显示帮助
"""
import os
import sys
import shutil
import subprocess
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
RELEASE_BASE_DIR = os.path.join(PROJECT_ROOT, "release")

APP_NAME = "project_assistant"
VERSION = "1.0.0"

# 根据模式确定输出目录
RELEASE_DIR = None  # 在 main() 中根据模式设置


def clean_build():
    """清理之前的构建文件"""
    print("=" * 50)
    print("清理构建目录...")
    
    dirs_to_clean = [
        os.path.join(DIST_DIR, "main.build"),
        os.path.join(DIST_DIR, "main.dist"),
        os.path.join(DIST_DIR, "main.onefile-build"),
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"  已删除: {dir_path}")
    
    # 删除 onefile 生成的 exe
    exe_path = os.path.join(DIST_DIR, f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        os.remove(exe_path)
        print(f"  已删除: {exe_path}")
    
    # 只清理默认的 release 目录（如果输出目录是 release）
    if RELEASE_DIR == os.path.join(RELEASE_BASE_DIR):
        if os.path.exists(RELEASE_DIR):
            try:
                shutil.rmtree(RELEASE_DIR)
                print(f"  已删除: {RELEASE_DIR}")
            except PermissionError:
                print(f"  警告: 无法删除 {RELEASE_DIR}，可能正在被使用")
                print(f"  尝试清空目录内容...")
                for item in os.listdir(RELEASE_DIR):
                    item_path = os.path.join(RELEASE_DIR, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        print(f"    已删除: {item}")
                    except PermissionError:
                        print(f"    无法删除: {item}（正在使用）")
    
    print("清理完成!")


def build_frontend():
    """构建前端"""
    print("=" * 50)
    print("构建前端...")
    
    os.chdir(FRONTEND_DIR)
    
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("  安装前端依赖...")
        result = subprocess.run(["npm", "install"], shell=True)
        if result.returncode != 0:
            print("  前端依赖安装失败!")
            return False
    
    result = subprocess.run(["npm", "run", "build"], shell=True)
    if result.returncode != 0:
        print("  前端构建失败!")
        return False
    
    print("前端构建完成!")
    return True


def build_backend(onefile=True):
    """使用 Nuitka 编译后端"""
    print("=" * 50)
    mode = "onefile" if onefile else "standalone"
    print(f"使用 Nuitka 编译后端 (模式: {mode})...")
    
    os.chdir(PROJECT_ROOT)
    
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
    ]
    
    if onefile:
        nuitka_cmd.append("--onefile")
    
    nuitka_cmd.extend([
        "--windows-console-mode=disable",
        f"--output-filename={APP_NAME}.exe",
        "--output-dir=dist",
        "--include-package=api",
        "--include-package=models",
        "--include-package=core",
        "--include-package=llm",
        "--include-package=services",
        "--include-package=voice",
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=sqlalchemy",
        "--include-package=pydantic",
        "--include-package=httpx",
        "--include-package=websockets",
        "--include-data-dir=frontend/dist=frontend/dist",
        # Note: data 和 .env 不打包进 exe，放在 release 目录中
        "--assume-yes-for-downloads",
        os.path.join(BACKEND_DIR, "main.py")
    ])
    
    print(f"  执行命令: {' '.join(nuitka_cmd)}")
    result = subprocess.run(nuitka_cmd)
    
    if result.returncode != 0:
        print("  Nuitka 编译失败!")
        return False
    
    print("后端编译完成!")
    return True


def create_release(onefile=True):
    """创建发布目录"""
    print("=" * 50)
    print("创建发布包...")
    
    os.makedirs(RELEASE_DIR, exist_ok=True)
    
    if onefile:
        # onefile 模式: 复制单个 exe
        exe_src = os.path.join(DIST_DIR, f"{APP_NAME}.exe")
        if not os.path.exists(exe_src):
            print(f"  错误: 找不到 {exe_src}")
            return False
        shutil.copy2(exe_src, os.path.join(RELEASE_DIR, f"{APP_NAME}.exe"))
        print(f"  已复制: {APP_NAME}.exe")
        
        # onefile 模式: 从项目根目录复制 data 目录和 .env（不打包进exe）
        data_src = os.path.join(PROJECT_ROOT, "data")
        if os.path.exists(data_src):
            data_dst = os.path.join(RELEASE_DIR, "data")
            if os.path.exists(data_dst):
                shutil.rmtree(data_dst)
            shutil.copytree(data_src, data_dst)
            print(f"  已复制: data/")
        else:
            # 如果项目根目录没有 data，创建空目录
            data_dst = os.path.join(RELEASE_DIR, "data")
            os.makedirs(data_dst, exist_ok=True)
            print(f"  已创建: data/")
        
        env_src = os.path.join(PROJECT_ROOT, ".env")
        if os.path.exists(env_src):
            shutil.copy2(env_src, os.path.join(RELEASE_DIR, ".env"))
            print(f"  已复制: .env")
        else:
            # 如果项目根目录没有 .env，创建一个空的
            env_dst = os.path.join(RELEASE_DIR, ".env")
            with open(env_dst, "w", encoding="utf-8") as f:
                f.write("# 配置文件\nPORT=8118\n")
            print(f"  已创建: .env")
    else:
        # standalone 模式: 复制整个目录
        main_dist = os.path.join(DIST_DIR, "main.dist")
        if not os.path.exists(main_dist):
            print(f"  错误: 找不到 {main_dist}")
            return False
        shutil.copytree(main_dist, RELEASE_DIR, dirs_exist_ok=True)
        print(f"  已复制: {RELEASE_DIR}")
    
    create_start_script()
    create_stop_script()
    create_bat_wrapper()
    create_config_template()
    create_readme(onefile)
    
    # 计算发布包大小
    total_size = 0
    for root, dirs, files in os.walk(RELEASE_DIR):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    print(f"  发布包大小: {total_size / 1024 / 1024:.2f} MB")
    
    print("发布包创建完成!")
    return True


def create_start_script():
    """创建启动脚本 (PowerShell版本)"""
    script_content = '''# Project Assistant Start Script
$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Read port from .env file
$envFile = Join-Path $scriptDir ".env"
$port = "8118"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -match "PORT=(\\d+)") {
        $port = $matches[1]
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Project Assistant v1.0.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already running
$process = Get-Process -Name "project_assistant" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Service is already running!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost:$port"
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "Starting service..." -ForegroundColor Green
Write-Host ""

# Check if exe exists
$exePath = Join-Path $scriptDir "project_assistant.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "Error: project_assistant.exe not found" -ForegroundColor Red
    Write-Host "Please run this script in the release directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start service
Start-Process -FilePath $exePath -WorkingDirectory $scriptDir

# Wait for service to start
Write-Host "Waiting for service to start..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Open browser
Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:$port"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Service started!" -ForegroundColor Green
Write-Host "  URL: http://localhost:$port" -ForegroundColor Green
Write-Host "  Run stop.ps1 to stop the service" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
'''
    
    script_path = os.path.join(RELEASE_DIR, "start.ps1")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    print(f"  已创建: {script_path}")


def create_stop_script():
    """创建停止脚本 (PowerShell版本)"""
    script_content = '''# Project Assistant Stop Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stop Project Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if process is running
$process = Get-Process -Name "project_assistant" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Stopping service..." -ForegroundColor Yellow
    Stop-Process -Name "project_assistant" -Force
    Write-Host "Service stopped!" -ForegroundColor Green
} else {
    Write-Host "Service is not running!" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
'''
    
    script_path = os.path.join(RELEASE_DIR, "stop.ps1")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    print(f"  已创建: {script_path}")


def create_bat_wrapper():
    """创建 .bat 包装脚本（双击运行）"""
    start_bat = '''@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
'''
    start_bat_path = os.path.join(RELEASE_DIR, "start.bat")
    with open(start_bat_path, "w", encoding="ascii") as f:
        f.write(start_bat)
    print(f"  已创建: {start_bat_path}")
    
    stop_bat = '''@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
'''
    stop_bat_path = os.path.join(RELEASE_DIR, "stop.bat")
    with open(stop_bat_path, "w", encoding="ascii") as f:
        f.write(stop_bat)
    print(f"  已创建: {stop_bat_path}")


def create_config_template():
    """创建配置文件模板"""
    config_content = '''# 项目管理助手配置文件
# 请根据实际情况填写

# 大模型配置 (豆包)
DOUBAO_API_KEY=your_api_key_here
DOUBAO_ENDPOINT=your_endpoint_here

# 语音服务配置 (豆包语音)
DOUBAO_VOICE_APPID=your_appid_here
DOUBAO_VOICE_ACCESS_TOKEN=your_access_token_here
DOUBAO_VOICE_SECRET_KEY=your_secret_key_here

# 其他配置
LOG_LEVEL=INFO
'''
    
    config_path = os.path.join(RELEASE_DIR, ".env.example")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  已创建: {config_path}")


def create_readme(onefile=True):
    """创建使用说明"""
    mode_note = "single exe file (~50MB)" if onefile else "directory (~200MB)"
    readme_content = f'''# Project Assistant v1.0.0

## Quick Start

1. Double-click `start.bat` to start the service
2. Browser will open http://localhost:8000 automatically
3. Double-click `stop.bat` to stop the service

## Build Mode

This release was built in **{"onefile" if onefile else "standalone"}** mode ({mode_note}).

## Configuration

To use LLM and voice features:

1. Copy `.env.example` to `.env`
2. Fill in your API keys
3. Restart the service

## System Requirements

- Windows 10/11 (64-bit)
- No Python installation required

## Notes

- First startup may take a few seconds
- If browser doesn't open automatically, visit http://localhost:8000 manually
- Database files are stored in the `data/` directory

## Files

- project_assistant.exe - Main program
- start.bat - Start script (double-click to run)
- stop.bat - Stop script (double-click to run)
- start.ps1 - PowerShell start script
- stop.ps1 - PowerShell stop script
- .env.example - Configuration template

---
Copyright (C) 2024
'''
    
    readme_path = os.path.join(RELEASE_DIR, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"  已创建: {readme_path}")


def check_nuitka():
    """检查 Nuitka 是否已安装"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Nuitka 版本: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    
    print("Nuitka 未安装，正在安装...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "nuitka", "ordered-set", "zstandard"]
    )
    return result.returncode == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="项目管理助手 - Nuitka 打包脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python build_nuitka.py                       # 默认: onefile 模式, 输出到 release
    python build_nuitka.py --onefile            # onefile 模式, 单个 exe (~50MB)
    python build_nuitka.py --standalone         # standalone 模式, 目录 (~200MB)
    python build_nuitka.py -o release_v1.0      # 指定输出目录
    python build_nuitka.py --standalone -o build # standalone 模式, 输出到 build
        """
    )
    parser.add_argument(
        "--standalone", 
        action="store_true",
        help="使用 standalone 模式 (生成目录, ~200MB, 启动更快)"
    )
    parser.add_argument(
        "--onefile", 
        action="store_true",
        help="使用 onefile 模式 (单个 exe, ~50MB, 默认)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出目录 (默认: release)"
    )
    
    args = parser.parse_args()
    
    # 确定模式: 默认 onefile
    onefile = not args.standalone
    
    # 确定输出目录
    global RELEASE_DIR
    if args.output:
        RELEASE_DIR = os.path.join(PROJECT_ROOT, args.output)
    else:
        # 默认输出目录：standalone 模式用 release_standalone，onefile 模式用 release
        RELEASE_DIR = os.path.join(PROJECT_ROOT, "release_standalone" if args.standalone else "release")
    
    print("=" * 50)
    print(f"  项目管理助手 - Nuitka 打包脚本")
    print(f"  版本: {VERSION}")
    print(f"  模式: {'onefile (单个exe)' if onefile else 'standalone (目录)'}")
    print(f"  输出: {RELEASE_DIR}")
    print("=" * 50)
    print()
    
    if not check_nuitka():
        print("错误: Nuitka 安装失败!")
        sys.exit(1)
    
    clean_build()
    
    if not build_frontend():
        print("错误: 前端构建失败!")
        sys.exit(1)
    
    if not build_backend(onefile=onefile):
        print("错误: 后端编译失败!")
        sys.exit(1)
    
    if not create_release(onefile=onefile):
        print("错误: 发布包创建失败!")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("  打包完成!")
    print(f"  发布目录: {RELEASE_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
