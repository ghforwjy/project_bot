"""
路径工具函数 - 处理 Nuitka onefile 模式下的路径问题
"""
import os
import sys
from pathlib import Path


def is_nuitka_compiled():
    """
    检查是否在 Nuitka 编译环境中运行
    
    Returns:
        bool: 是否在 Nuitka 编译环境中
    """
    return "__compiled__" in globals()


def get_executable_dir():
    """
    获取可执行文件所在目录
    
    在 Nuitka onefile 模式下，sys.executable 指向临时目录，
    需要使用特殊方法获取原始 exe 所在目录
    
    Returns:
        Path: 可执行文件所在目录
    """
    if getattr(sys, 'frozen', False):
        # 打包环境
        if is_nuitka_compiled():
            # Nuitka 编译环境
            # 在 onefile 模式下，sys.argv[0] 指向原始 exe
            original_exe = Path(sys.argv[0]).resolve()
            return original_exe.parent
        else:
            # PyInstaller 等其他打包工具
            return Path(sys.executable).parent
    else:
        # 开发环境：返回项目根目录
        # 使用 resolve() 来解析 .. 等路径
        return Path(__file__).parent.parent.parent.resolve()


def get_data_dir():
    """
    获取数据目录路径
    
    Returns:
        Path: 数据目录路径
    """
    return get_executable_dir() / "data"


def get_env_file_path():
    """
    获取 .env 文件路径
    
    Returns:
        Path: .env 文件路径
    """
    return get_executable_dir() / ".env"


def get_frontend_dist_path():
    """
    获取前端静态文件路径
    
    Returns:
        Path: 前端 dist 目录路径，如果不存在返回 None
    """
    # 检查是否在 Nuitka 打包环境中运行
    if is_nuitka_compiled():
        # Nuitka 打包后，资源文件在当前目录
        base_path = Path(__file__).parent
        frontend_path = base_path / "frontend" / "dist"
        if frontend_path.exists():
            return frontend_path
    
    # 打包环境：使用 exe 同级目录
    if getattr(sys, 'frozen', False):
        base_path = get_executable_dir()
        frontend_path = base_path / "frontend" / "dist"
        if frontend_path.exists():
            return frontend_path
    
    # 开发环境路径
    dev_path = Path(__file__).parent.parent / "frontend" / "dist"
    if dev_path.exists():
        return dev_path.resolve()
    
    return None
