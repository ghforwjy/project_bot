"""
获取Whisper.cpp的最新版本号
"""
import requests
import re


def get_latest_version():
    """
    获取Whisper.cpp的最新版本号
    
    Returns:
        str: 最新版本号，如 "v1.5.5"
    """
    try:
        # 访问GitHub releases页面
        url = "https://github.com/ggml-org/whisper.cpp/releases"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 使用正则表达式查找版本号
        # 匹配格式如 v1.5.5 的版本号
        version_pattern = r"releases/tag/(v\d+\.\d+\.\d+)"
        matches = re.findall(version_pattern, response.text)
        
        if matches:
            # 去重并按版本号排序
            unique_versions = list(set(matches))
            # 简单的版本号排序（假设格式为 vX.Y.Z）
            unique_versions.sort(key=lambda v: tuple(map(int, v[1:].split('.'))), reverse=True)
            return unique_versions[0]
        else:
            print("未找到版本号")
            return None
            
    except Exception as e:
        print(f"获取版本号失败: {e}")
        return None


if __name__ == "__main__":
    latest_version = get_latest_version()
    if latest_version:
        print(f"最新版本: {latest_version}")
    else:
        print("获取最新版本失败")
