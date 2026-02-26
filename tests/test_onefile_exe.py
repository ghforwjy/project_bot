"""
测试打包后的 onefile exe 是否能正确找到 data 和 .env 文件

这个测试程序会检查 release 目录下的 exe 运行时行为
"""
import os
import sys
import subprocess
from pathlib import Path


def test_exe_paths():
    """测试 exe 运行时的路径"""
    project_root = Path(__file__).parent.parent
    release_dir = project_root / "release"
    exe_path = release_dir / "project_assistant.exe"
    
    print("=" * 60)
    print("测试 onefile exe 路径")
    print("=" * 60)
    
    print(f"Release 目录: {release_dir}")
    print(f"  是否存在: {release_dir.exists()}")
    
    print(f"Exe 路径: {exe_path}")
    print(f"  是否存在: {exe_path.exists()}")
    
    # 检查 data 目录
    data_dir = release_dir / "data"
    print(f"Data 目录: {data_dir}")
    print(f"  是否存在: {data_dir.exists()}")
    if data_dir.exists():
        print(f"  内容: {list(data_dir.iterdir())}")
    
    # 检查 .env 文件
    env_file = release_dir / ".env"
    print(f".env 文件: {env_file}")
    print(f"  是否存在: {env_file.exists()}")
    
    print()
    
    # 创建一个测试脚本来检查 exe 运行时的路径
    test_script = '''
import sys
import os
from pathlib import Path

print("=== 运行时环境检查 ===")
print(f"sys.executable: {sys.executable}")
print(f"sys.argv[0]: {sys.argv[0]}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"__compiled__: {'__compiled__' in globals()}")
print(f"当前工作目录: {os.getcwd()}")

# 计算路径
if getattr(sys, 'frozen', False):
    if "__compiled__" in globals():
        exe_dir = Path(sys.argv[0]).resolve().parent
    else:
        exe_dir = Path(sys.executable).parent
else:
    exe_dir = Path(__file__).parent

print(f"计算的可执行文件目录: {exe_dir}")
print(f"  是否存在: {exe_dir.exists()}")

data_dir = exe_dir / "data"
print(f"数据目录: {data_dir}")
print(f"  是否存在: {data_dir.exists()}")

env_file = exe_dir / ".env"
print(f".env 文件: {env_file}")
print(f"  是否存在: {env_file.exists()}")

# 尝试创建 data 目录
try:
    data_dir.mkdir(exist_ok=True)
    print(f"  创建/确认 data 目录成功")
except Exception as e:
    print(f"  创建 data 目录失败: {e}")

# 尝试写入测试文件
test_file = data_dir / "test.txt"
try:
    test_file.write_text("test")
    print(f"  写入测试文件成功: {test_file}")
    test_file.unlink()
    print(f"  删除测试文件成功")
except Exception as e:
    print(f"  写入测试文件失败: {e}")
'''
    
    # 将测试脚本写入临时文件
    test_script_path = release_dir / "path_test.py"
    test_script_path.write_text(test_script, encoding="utf-8")
    
    print(f"测试脚本已创建: {test_script_path}")
    print()
    
    return True


def check_process_status():
    """检查进程状态"""
    print("=" * 60)
    print("检查进程状态")
    print("=" * 60)
    
    import subprocess
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq project_assistant.exe"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    if "project_assistant.exe" in result.stdout:
        print("✓ 进程正在运行")
    else:
        print("✗ 进程未运行")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("Onefile Exe 路径测试")
    print("*" * 60)
    print()
    
    test_exe_paths()
    check_process_status()
    
    print("*" * 60)
    print("测试完成")
    print("*" * 60)
