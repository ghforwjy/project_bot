"""
验证语音服务安装状态
"""
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.voice.config import voice_config
from backend.voice.whisper_integration import WhisperIntegration
from backend.voice.whisper_python_integration import WhisperPythonIntegration


def check_directories():
    """
    检查必要的目录是否存在
    """
    print("=== 检查目录结构 ===")
    
    # 检查Whisper.cpp目录
    whisper_dir = voice_config.WHISPER_PATH
    if os.path.exists(whisper_dir):
        print(f"✅ Whisper.cpp目录存在: {whisper_dir}")
        # 检查是否有可执行文件
        files = os.listdir(whisper_dir)
        exe_files = [f for f in files if f.endswith('.exe')]
        if exe_files:
            print(f"✅ 找到可执行文件: {exe_files}")
        else:
            print("⚠️  未找到可执行文件")
    else:
        print(f"❌ Whisper.cpp目录不存在: {whisper_dir}")
    
    # 检查模型目录
    model_dir = os.path.dirname(voice_config.MODEL_PATH)
    if os.path.exists(model_dir):
        print(f"✅ 模型目录存在: {model_dir}")
        # 检查是否有模型文件
        files = os.listdir(model_dir)
        model_files = [f for f in files if f.endswith('.bin')]
        if model_files:
            print(f"✅ 找到模型文件: {model_files}")
        else:
            print("⚠️  未找到模型文件")
    else:
        print(f"❌ 模型目录不存在: {model_dir}")


def check_whisper_integration():
    """
    检查Whisper集成是否正常
    """
    print("\n=== 检查Whisper集成 ===")
    
    try:
        # 检查Python版本的Whisper
        print("\n检查Python版本的Whisper:")
        python_whisper = WhisperPythonIntegration()
        python_available = python_whisper.is_available()
        print(f"✅ Python Whisper是否可用: {python_available}")
        
        if python_available:
            python_status = python_whisper.get_status()
            print(f"✅ Python Whisper状态信息: {python_status}")
            print("✅ 将使用Python版本的Whisper进行语音识别")
        else:
            print("⚠️  Python Whisper不可用")
        
        # 检查C++版本的Whisper
        print("\n检查C++版本的Whisper:")
        cpp_whisper = WhisperIntegration()
        cpp_available = cpp_whisper.is_available()
        print(f"✅ C++ Whisper是否可用: {cpp_available}")
        
        if cpp_available:
            cpp_status = cpp_whisper.get_status()
            print(f"✅ C++ Whisper状态信息: {cpp_status}")
        else:
            print("⚠️  C++ Whisper不可用")
        
        # 总结
        if python_available or cpp_available:
            print("\n✅ Whisper集成正常，可以使用实际的语音识别功能")
        else:
            print("\n⚠️  所有Whisper版本都不可用，将使用模拟识别结果")
            
    except Exception as e:
        print(f"❌ Whisper集成检查失败: {e}")


def check_configuration():
    """
    检查配置是否正确
    """
    print("\n=== 检查配置 ===")
    
    print(f"Whisper.cpp路径: {voice_config.WHISPER_PATH}")
    print(f"模型路径: {voice_config.MODEL_PATH}")
    print(f"采样率: {voice_config.SAMPLE_RATE}")
    print(f"语言: {voice_config.LANGUAGE}")
    print(f"线程数: {voice_config.THREADS}")


def main():
    """
    主函数
    """
    print("语音服务安装验证\n")
    
    check_directories()
    check_configuration()
    check_whisper_integration()
    
    print("\n=== 验证完成 ===")
    print("请根据上面的检查结果进行相应的配置和安装。")
    print("详细安装指南请参考: VOICE_SERVICE_INSTALLATION.md")


if __name__ == "__main__":
    main()
