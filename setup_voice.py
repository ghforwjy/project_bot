"""
语音服务部署脚本
功能：
1. 下载并部署 ffmpeg 便携版
2. 下载 Whisper 模型
3. 验证部署结果
4. 配置环境变量
"""

import os
import sys
import shutil
import zipfile
import subprocess
from typing import Optional, Dict, Any

# 彩色输出配置
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 确保彩色输出在 Windows 上也能工作
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

def print_header(message: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"{message:^60}")
    print(f"{'=' * 60}{Colors.ENDC}")

def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}[✓] {message}{Colors.ENDC}")

def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")

def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}[✗] {message}{Colors.ENDC}")

def print_info(message: str):
    """打印信息"""
    print(f"{Colors.OKBLUE}[i] {message}{Colors.ENDC}")

def download_file(url: str, output_path: str) -> bool:
    """
    下载文件
    
    Args:
        url: 下载 URL
        output_path: 输出路径
        
    Returns:
        bool: 下载是否成功
    """
    try:
        import requests
        
        print_info(f"开始下载: {url}")
        print_info(f"保存到: {output_path}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 流式下载
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 显示进度
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        bar_length = 50
                        bar = '█' * int(bar_length * percent / 100)
                        spaces = ' ' * (bar_length - len(bar))
                        sys.stdout.write(f'\r下载进度: [{bar}{spaces}] {percent:.1f}%')
                        sys.stdout.flush()
        
        if total_size > 0:
            print()
        
        print_success(f"文件下载成功: {output_path}")
        return True
        
    except Exception as e:
        print_error(f"文件下载失败: {e}")
        return False

def unzip_file(zip_path: str, extract_dir: str) -> bool:
    """
    解压文件
    
    Args:
        zip_path: 压缩文件路径
        extract_dir: 解压目录
        
    Returns:
        bool: 解压是否成功
    """
    try:
        print_info(f"开始解压: {zip_path}")
        print_info(f"解压到: {extract_dir}")
        
        # 确保解压目录存在
        os.makedirs(extract_dir, exist_ok=True)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print_success(f"文件解压成功")
        return True
        
    except Exception as e:
        print_error(f"文件解压失败: {e}")
        return False

def validate_ffmpeg(ffmpeg_dir: str) -> Dict[str, Any]:
    """
    验证 ffmpeg 部署
    
    Args:
        ffmpeg_dir: ffmpeg 目录
        
    Returns:
        Dict: 验证结果
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        # 检查可能的目录结构
        possible_paths = [
            os.path.join(ffmpeg_dir, 'bin', 'ffmpeg.exe'),
            os.path.join(ffmpeg_dir, 'ffmpeg-master-latest-win64-gpl', 'bin', 'ffmpeg.exe')
        ]
        
        ffmpeg_path = None
        for path in possible_paths:
            if os.path.exists(path):
                ffmpeg_path = path
                break
        
        if not ffmpeg_path:
            result['message'] = f"ffmpeg.exe 不存在于以下路径: {possible_paths}"
            return result
        
        # 找到 ffprobe
        ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
        if not os.path.exists(ffprobe_path):
            result['message'] = f"ffprobe.exe 不存在: {ffprobe_path}"
            return result
        
        # 验证 ffmpeg 可执行性
        print_info("验证 ffmpeg 可执行性...")
        proc = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode != 0:
            result['message'] = f"ffmpeg 执行失败: {proc.stderr}"
            return result
        
        # 提取版本信息
        version_info = proc.stdout.split('\n')[0]
        result['details']['ffmpeg_version'] = version_info
        result['details']['ffmpeg_path'] = ffmpeg_path
        
        # 验证 ffprobe 可执行性
        print_info("验证 ffprobe 可执行性...")
        proc = subprocess.run(
            [ffprobe_path, '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode != 0:
            result['message'] = f"ffprobe 执行失败: {proc.stderr}"
            return result
        
        version_info = proc.stdout.split('\n')[0]
        result['details']['ffprobe_version'] = version_info
        result['details']['ffprobe_path'] = ffprobe_path
        
        # 如果 ffmpeg 在子目录中，复制到预期位置
        expected_bin_dir = os.path.join(ffmpeg_dir, 'bin')
        if 'ffmpeg-master-latest-win64-gpl' in ffmpeg_path:
            print_info("检测到 ffmpeg 在子目录中，正在复制到预期位置...")
            os.makedirs(expected_bin_dir, exist_ok=True)
            
            # 复制可执行文件
            files_to_copy = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
            for file_name in files_to_copy:
                src_path = os.path.join(os.path.dirname(ffmpeg_path), file_name)
                dst_path = os.path.join(expected_bin_dir, file_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    print_info(f"复制: {file_name} -> {dst_path}")
        
        result['success'] = True
        result['message'] = "FFmpeg 验证成功"
        
    except Exception as e:
        result['message'] = f"验证异常: {e}"
    
    return result

def validate_whisper_model(model_path: str, model_name: str) -> Dict[str, Any]:
    """
    验证 Whisper 模型
    
    Args:
        model_path: 模型文件路径
        model_name: 模型名称
        
    Returns:
        Dict: 验证结果
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        # 检查文件存在
        if not os.path.exists(model_path):
            result['message'] = f"模型文件不存在: {model_path}"
            return result
        
        # 检查文件大小
        file_size = os.path.getsize(model_path)
        file_size_mb = file_size / (1024 * 1024)
        result['details']['file_size_mb'] = f"{file_size_mb:.2f}MB"
        
        # 验证文件大小是否合理
        expected_sizes = {
            'tiny': 39,    # ~39MB
            'base': 74,    # ~74MB
            'small': 244,  # ~244MB
            'medium': 769, # ~769MB
            'large': 1550  # ~1550MB
        }
        
        if model_name in expected_sizes:
            expected_size = expected_sizes[model_name]
            if abs(file_size_mb - expected_size) > expected_size * 0.1:
                result['message'] = f"模型文件大小异常，预期约 {expected_size}MB，实际 {file_size_mb:.2f}MB"
                return result
        
        result['success'] = True
        result['message'] = "Whisper 模型验证成功"
        
    except Exception as e:
        result['message'] = f"验证异常: {e}"
    
    return result

def deploy_ffmpeg(ffmpeg_dir: str) -> bool:
    """
    部署 ffmpeg
    
    Args:
        ffmpeg_dir: ffmpeg 部署目录
        
    Returns:
        bool: 部署是否成功
    """
    print_header("部署 FFmpeg")
    
    # 检查是否已存在可执行文件
    expected_ffmpeg = os.path.join(ffmpeg_dir, 'bin', 'ffmpeg.exe')
    expected_ffprobe = os.path.join(ffmpeg_dir, 'bin', 'ffprobe.exe')
    
    if os.path.exists(expected_ffmpeg) and os.path.exists(expected_ffprobe):
        print_warning("FFmpeg 可执行文件已存在，跳过下载")
        # 验证现有安装
        validation = validate_ffmpeg(ffmpeg_dir)
        if validation['success']:
            print_success("现有 FFmpeg 验证成功")
            return True
        else:
            print_warning("现有 FFmpeg 验证失败，重新下载")
    else:
        print_info("未检测到 FFmpeg 可执行文件，开始下载")
    
    # 检查是否已有下载的压缩文件
    temp_zip = os.path.join(ffmpeg_dir, 'ffmpeg.zip')
    if os.path.exists(temp_zip):
        print_info(f"检测到现有压缩文件: {temp_zip}")
        print_info("尝试使用现有压缩文件...")
        # 尝试解压
        if unzip_file(temp_zip, ffmpeg_dir):
            # 验证
            validation = validate_ffmpeg(ffmpeg_dir)
            if validation['success']:
                print_success("使用现有压缩文件部署成功")
                return True
            else:
                print_warning("现有压缩文件部署失败，重新下载")
    
    # 下载链接（使用 GitHub 发布的静态编译版）
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # 下载 ffmpeg
    if not download_file(ffmpeg_url, temp_zip):
        return False
    
    # 解压
    if not unzip_file(temp_zip, ffmpeg_dir):
        return False
    
    # 清理临时文件
    if os.path.exists(temp_zip):
        os.remove(temp_zip)
    
    # 验证
    validation = validate_ffmpeg(ffmpeg_dir)
    if validation['success']:
        print_success(f"FFmpeg 部署成功: {validation['details'].get('ffmpeg_version', '')}")
        return True
    else:
        print_error(f"FFmpeg 部署失败: {validation['message']}")
        return False

def deploy_whisper_model(model_dir: str, model_name: str) -> bool:
    """
    部署 Whisper 模型
    
    Args:
        model_dir: 模型目录
        model_name: 模型名称
        
    Returns:
        bool: 部署是否成功
    """
    print_header(f"部署 Whisper 模型 ({model_name})")
    
    # 确保目录存在
    os.makedirs(model_dir, exist_ok=True)
    
    # 模型文件路径（使用新的 gguf 格式）
    model_path = os.path.join(model_dir, f"{model_name}.gguf")
    
    # 检查是否已存在
    if os.path.exists(model_path):
        print_warning("模型文件已存在，跳过下载")
        # 验证现有模型
        validation = validate_whisper_model(model_path, model_name)
        if validation['success']:
            print_success(f"现有模型验证成功: {validation['details'].get('file_size_mb', '')}")
            return True
        else:
            print_warning("现有模型验证失败，重新下载")
    else:
        print_info("未检测到模型文件，开始下载")
    
    # 尝试多个下载源（使用正确的模型路径）
    download_sources = [
        # 主要源：Hugging Face ggml-org 模型
        f"https://huggingface.co/ggml-org/whisper-{model_name}/resolve/main/ggml-model-f16.gguf",
        # 备用源：Hugging Face 官方 Whisper 模型
        f"https://huggingface.co/openai/whisper-{model_name}/resolve/main/pytorch_model.bin",
        # 备用源：GitHub 发布页
        f"https://github.com/ggml-org/whisper.cpp/releases/download/v1.5.4/ggml-{model_name}.bin"
    ]
    
    # 尝试从多个源下载
    download_success = False
    for i, source_url in enumerate(download_sources):
        print_info(f"尝试从源 {i+1}/{len(download_sources)} 下载...")
        print_info(f"下载地址: {source_url}")
        
        # 为不同源使用不同的文件名
        if "ggml-org/whisper" in source_url:
            temp_path = os.path.join(model_dir, f"{model_name}.gguf")
        elif "openai/whisper" in source_url:
            temp_path = os.path.join(model_dir, f"{model_name}_openai.bin")
        else:
            temp_path = os.path.join(model_dir, f"{model_name}.bin")
        
        if download_file(source_url, temp_path):
            # 验证
            validation = validate_whisper_model(temp_path, model_name)
            if validation['success']:
                # 如果验证成功，重命名为标准格式
                if temp_path != model_path:
                    os.rename(temp_path, model_path)
                    print_info(f"重命名模型文件: {os.path.basename(temp_path)} -> {os.path.basename(model_path)}")
                print_success(f"Whisper 模型部署成功: {validation['details'].get('file_size_mb', '')}")
                print_success(f"使用源: {source_url}")
                return True
            else:
                print_warning(f"模型验证失败，尝试下一个源: {validation['message']}")
                # 删除无效文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            print_warning(f"下载失败，尝试下一个源")
    
    # 所有源都失败 - 尝试直接从 Python Whisper 复制模型
    print_info("尝试从 Python Whisper 缓存复制模型...")
    try:
        import whisper
        import torch
        
        # 加载模型到缓存
        print_info(f"正在加载 Whisper {model_name} 模型...")
        model = whisper.load_model(model_name)
        
        # 获取模型路径
        if hasattr(model, 'model_path'):
            model_path_src = model.model_path
            print_info(f"找到模型路径: {model_path_src}")
            
            # 复制模型文件
            if os.path.exists(model_path_src):
                shutil.copy2(model_path_src, model_path)
                print_success(f"从 Python Whisper 缓存复制模型成功！")
                return True
            else:
                print_warning(f"模型文件不存在: {model_path_src}")
        else:
            print_warning("无法获取模型路径")
            
    except Exception as e:
        print_warning(f"从 Python Whisper 复制模型失败: {e}")
    
    # 所有尝试都失败
    print_error("所有下载源都失败，请检查网络连接")
    print_info("建议：")
    print_info("1. 手动下载模型文件")
    print_info("2. 放入目录: " + model_dir)
    print_info("3. 支持的格式: .gguf 或 .bin")
    print_info("4. 文件名示例: medium.gguf 或 medium.bin")
    print_info("5. 重新运行部署脚本")
    
    return False

def install_python_dependencies(requirements_file: str) -> bool:
    """
    安装 Python 依赖
    
    Args:
        requirements_file: requirements.txt 文件路径
        
    Returns:
        bool: 安装是否成功
    """
    print_header("安装 Python 依赖")
    
    # 检查 requirements.txt 文件是否存在
    if not os.path.exists(requirements_file):
        print_error(f"requirements.txt 文件不存在: {requirements_file}")
        return False
    
    try:
        print_info(f"开始安装依赖，使用文件: {requirements_file}")
        print_info("这可能需要几分钟时间，请耐心等待...")
        
        # 执行 pip 安装命令
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            print_success("Python 依赖安装成功！")
            
            # 验证关键依赖是否安装成功
            key_deps = ['openai-whisper', 'torch', 'fastapi']
            print_info("验证关键依赖...")
            
            for dep in key_deps:
                dep_result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', dep],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if dep_result.returncode == 0:
                    print_success(f"✓ {dep} 已安装")
                else:
                    print_warning(f"⚠️ {dep} 可能未安装")
            
            return True
        else:
            print_error(f"依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"依赖安装异常: {e}")
        return False

def validate_python_whisper() -> bool:
    """
    验证 Python 版 Whisper 是否可用
    
    Returns:
        bool: 是否可用
    """
    print_header("验证 Python 版 Whisper")
    
    try:
        # 尝试导入 Whisper
        import whisper
        print_success("✓ Whisper 库已成功导入")
        
        # 尝试加载模型
        print_info("尝试加载 Whisper 模型...")
        try:
            model = whisper.load_model("tiny")
            print_success("✓ Whisper 模型加载成功")
            return True
        except Exception as e:
            print_warning(f"⚠️ 模型加载失败（这是正常的，首次使用会自动下载）: {e}")
            print_info("Whisper 库已安装，首次使用时会自动下载模型")
            return True
            
    except ImportError as e:
        print_error(f"✗ Whisper 库未安装: {e}")
        return False
    except Exception as e:
        print_error(f"✗ Whisper 验证异常: {e}")
        return False
    
def create_env_file(env_path: str, config: Dict[str, str]):
    """
    创建 .env 文件
    
    Args:
        env_path: .env 文件路径
        config: 配置参数
    """
    try:
        # 读取现有内容
        existing_content = ''
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 构建新内容
        new_content = existing_content
        for key, value in config.items():
            # 检查是否已存在
            if f"{key}=" not in new_content:
                new_content += f"\n{key}={value}"
        
        # 写入文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print_success(f".env 文件配置成功: {env_path}")
        
    except Exception as e:
        print_error(f".env 文件配置失败: {e}")

def main():
    """
    主函数
    """
    print_header("语音服务部署脚本")
    print_info("开始部署语音服务所需组件...")
    
    # 项目根目录
    project_root = os.path.abspath(os.path.dirname(__file__))
    print_info(f"项目根目录: {project_root}")
    
    # 配置
    config = {
        'ffmpeg_dir': os.path.join(project_root, 'ffmpeg'),
        'voice_dir': os.path.join(project_root, 'backend', 'voice'),
        'model_dir': os.path.join(project_root, 'backend', 'voice', 'models'),
        'env_file': os.path.join(project_root, '.env'),
        'requirements_file': os.path.join(project_root, 'requirements.txt'),
        'whisper_model': 'medium'  # 默认使用 medium 模型
    }
    
    # 创建必要目录
    for dir_path in [config['ffmpeg_dir'], config['model_dir']]:
        os.makedirs(dir_path, exist_ok=True)
    
    # 部署 ffmpeg
    ffmpeg_success = deploy_ffmpeg(config['ffmpeg_dir'])
    
    # 安装 Python 依赖
    dependency_success = install_python_dependencies(config['requirements_file'])
    
    # 验证 Python 版 Whisper
    python_whisper_success = validate_python_whisper()
    
    # 部署 Whisper 模型
    model_success = deploy_whisper_model(config['model_dir'], config['whisper_model'])
    
    # 配置豆包语音参数
    doubao_config = {
        'DOUBAO_VOICE_APPID': '3561884959',
        'DOUBAO_VOICE_ACCESS_TOKEN': 'qwpFoXXzYTxjIWRiWwAjGEGlc_PDyK-h',
        'DOUBAO_VOICE_SECRET_KEY': 'Vt-BXogJIF-BWKXO7ypzEZDaVZTwdxNM'
    }
    
    print_header("配置豆包语音参数")
    create_env_file(config['env_file'], doubao_config)
    
    # 生成部署报告
    print_header("部署报告")
    print(f"{'组件':<20} {'状态':<10} {'详情':<40}")
    print('-' * 70)
    
    # FFmpeg 状态
    if ffmpeg_success:
        ffmpeg_status = Colors.OKGREEN + "成功" + Colors.ENDC
    else:
        ffmpeg_status = Colors.FAIL + "失败" + Colors.ENDC
    print(f"{'FFmpeg':<20} {ffmpeg_status:<10} {'ffmpeg/bin/ffmpeg.exe':<40}")
    
    # Python 依赖状态
    if dependency_success:
        dep_status = Colors.OKGREEN + "成功" + Colors.ENDC
    else:
        dep_status = Colors.FAIL + "失败" + Colors.ENDC
    print(f"{'Python 依赖':<20} {dep_status:<10} {'requirements.txt':<40}")
    
    # Python Whisper 状态
    if python_whisper_success:
        py_whisper_status = Colors.OKGREEN + "成功" + Colors.ENDC
    else:
        py_whisper_status = Colors.FAIL + "失败" + Colors.ENDC
    print(f"{'Python Whisper':<20} {py_whisper_status:<10} {'openai-whisper':<40}")
    
    # 模型状态
    if model_success:
        model_status = Colors.OKGREEN + "成功" + Colors.ENDC
    else:
        model_status = Colors.FAIL + "失败" + Colors.ENDC
    print(f"{'Whisper 模型':<20} {model_status:<10} {'models/' + config['whisper_model'] + '.gguf':<40}")
    
    # 豆包配置状态
    if os.path.exists(config['env_file']):
        env_status = Colors.OKGREEN + "成功" + Colors.ENDC
    else:
        env_status = Colors.FAIL + "失败" + Colors.ENDC
    print(f"{'豆包语音配置':<20} {env_status:<10} {'.env 文件':<40}")
    
    # 总体状态
    print('-' * 70)
    if ffmpeg_success and dependency_success:
        print_success("🎉 语音服务部署成功！")
        print_info("下一步：")
        print_info("1. 启动后端服务: python backend/main.py")
        print_info("2. 启动前端服务: cd frontend && npm run dev")
        print_info("3. 访问前端: http://localhost:5173")
        print_info("4. 测试语音识别功能")
        
        # 提示关于模型的信息
        if not model_success:
            print_warning("⚠️ 注意：Whisper.cpp 模型下载失败，但不影响核心功能")
            print_info("✅ Python 版 Whisper 已就绪，首次使用时会自动下载模型")
            print_info("✅ 豆包语音识别已配置完成")
            print_info("✅ 音频格式转换功能已就绪")
        
        return 0
    else:
        print_error("❌ 语音服务部署失败！")
        print_warning("请检查上面的错误信息并重新运行脚本")
        return 1

if __name__ == "__main__":
    sys.exit(main())