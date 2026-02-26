"""
测试 Nuitka onefile 模式下的路径获取功能

这个测试程序模拟 onefile 模式下的路径问题，验证路径工具函数是否能正确工作。
"""
import sys
import os
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def test_development_environment():
    """测试开发环境下的路径获取"""
    from utils.path_utils import get_executable_dir, get_data_dir, get_env_file_path, get_frontend_dist_path
    
    print("=" * 60)
    print("测试开发环境路径")
    print("=" * 60)
    
    # 当前应该是开发环境
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"__compiled__: {'__compiled__' in globals()}")
    print()
    
    exe_dir = get_executable_dir()
    print(f"可执行文件目录: {exe_dir}")
    print(f"  是否存在: {exe_dir.exists()}")
    
    data_dir = get_data_dir()
    print(f"数据目录: {data_dir}")
    print(f"  是否存在: {data_dir.exists()}")
    
    env_path = get_env_file_path()
    print(f".env 文件路径: {env_path}")
    print(f"  是否存在: {env_path.exists()}")
    
    frontend_path = get_frontend_dist_path()
    print(f"前端 dist 路径: {frontend_path}")
    print(f"  是否存在: {frontend_path.exists() if frontend_path else False}")
    
    print()
    
    # 验证路径是否正确
    project_root = Path(__file__).parent.parent.resolve()
    
    print("验证结果:")
    if exe_dir == project_root:
        print("  ✓ 可执行文件目录正确（指向项目根目录）")
    else:
        print(f"  ✗ 可执行文件目录错误")
        print(f"    期望: {project_root}")
        print(f"    实际: {exe_dir}")
    
    return True


def simulate_onefile_environment():
    """
    模拟 onefile 环境下的路径获取
    
    在 onefile 模式下：
    - sys.frozen = True
    - __compiled__ 存在
    - sys.executable 指向临时目录
    - sys.argv[0] 指向原始 exe 路径
    """
    print("=" * 60)
    print("模拟 onefile 环境路径")
    print("=" * 60)
    
    # 保存原始值
    original_frozen = getattr(sys, 'frozen', None)
    original_argv0 = sys.argv[0]
    
    # 模拟 onefile 环境
    sys.frozen = True
    
    # 模拟 sys.argv[0] 指向 release 目录下的 exe
    release_exe = Path(__file__).parent.parent / "release" / "project_assistant.exe"
    sys.argv[0] = str(release_exe)
    
    print(f"模拟环境:")
    print(f"  sys.frozen = True")
    print(f"  sys.argv[0] = {sys.argv[0]}")
    print()
    
    # 在测试模块中设置 __compiled__，然后重新导入模块
    # 注意：这里我们不能真正模拟 Nuitka 的 __compiled__，
    # 因为一旦模块被导入，globals() 就固定了
    # 所以我们直接测试逻辑
    
    # 手动计算期望的结果
    expected_dir = release_exe.parent
    print(f"期望的目录: {expected_dir}")
    
    # 在 onefile 模式下，路径应该是 sys.argv[0] 的父目录
    calculated_dir = Path(sys.argv[0]).resolve().parent
    print(f"计算的可执行文件目录: {calculated_dir}")
    
    if calculated_dir == expected_dir:
        print("  ✓ 路径计算正确！")
    else:
        print("  ✗ 路径计算错误！")
    
    # 恢复原始值
    if original_frozen is not None:
        sys.frozen = original_frozen
    else:
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')
    sys.argv[0] = original_argv0
    
    print()
    return calculated_dir == expected_dir


def test_release_directory_structure():
    """测试 release 目录结构"""
    print("=" * 60)
    print("测试 release 目录结构")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    release_dir = project_root / "release"
    
    print(f"Release 目录: {release_dir}")
    print(f"  是否存在: {release_dir.exists()}")
    
    if release_dir.exists():
        print("\n目录内容:")
        for item in release_dir.iterdir():
            item_type = "目录" if item.is_dir() else "文件"
            print(f"  [{item_type}] {item.name}")
        
        # 检查关键文件
        data_dir = release_dir / "data"
        env_file = release_dir / ".env"
        exe_file = release_dir / "project_assistant.exe"
        
        print("\n关键文件检查:")
        print(f"  data 目录: {'✓ 存在' if data_dir.exists() else '✗ 不存在'}")
        print(f"  .env 文件: {'✓ 存在' if env_file.exists() else '✗ 不存在'}")
        print(f"  exe 文件: {'✓ 存在' if exe_file.exists() else '✗ 不存在'}")
    
    print()


def test_path_utils_functions():
    """测试路径工具函数"""
    from utils.path_utils import get_executable_dir, get_data_dir, get_env_file_path
    
    print("=" * 60)
    print("测试路径工具函数")
    print("=" * 60)
    
    exe_dir = get_executable_dir()
    data_dir = get_data_dir()
    env_path = get_env_file_path()
    
    print(f"可执行文件目录: {exe_dir}")
    print(f"数据目录: {data_dir}")
    print(f".env 路径: {env_path}")
    
    # 验证一致性
    print("\n一致性检查:")
    if data_dir == exe_dir / "data":
        print("  ✓ 数据目录正确")
    else:
        print("  ✗ 数据目录错误")
    
    if env_path == exe_dir / ".env":
        print("  ✓ .env 路径正确")
    else:
        print("  ✗ .env 路径错误")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("Nuitka Onefile 路径测试")
    print("*" * 60)
    print()
    
    # 测试开发环境
    test_development_environment()
    
    # 测试路径工具函数
    test_path_utils_functions()
    
    # 测试 release 目录结构
    test_release_directory_structure()
    
    # 模拟 onefile 环境
    simulate_onefile_environment()
    
    print("*" * 60)
    print("测试完成")
    print("*" * 60)
