"""
使用GitHub API获取Whisper.cpp的最新发布信息
"""
import requests


def get_latest_release():
    """
    使用GitHub API获取Whisper.cpp的最新发布信息
    
    Returns:
        dict: 包含发布信息的字典，包括版本号和下载链接
    """
    try:
        # GitHub API URL
        api_url = "https://api.github.com/repos/ggml-org/whisper.cpp/releases/latest"
        
        # 发送请求
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        release_data = response.json()
        
        # 提取版本号
        tag_name = release_data.get('tag_name')
        
        # 提取Windows x64的下载链接
        windows_assets = []
        for asset in release_data.get('assets', []):
            if 'windows-x64' in asset.get('name', '').lower():
                windows_assets.append({
                    'name': asset.get('name'),
                    'browser_download_url': asset.get('browser_download_url')
                })
        
        return {
            'tag_name': tag_name,
            'windows_assets': windows_assets,
            'published_at': release_data.get('published_at')
        }
        
    except Exception as e:
        print(f"获取发布信息失败: {e}")
        return None


if __name__ == "__main__":
    release_info = get_latest_release()
    if release_info:
        print(f"最新发布: {release_info.get('tag_name')}")
        print(f"发布时间: {release_info.get('published_at')}")
        print("Windows x64 资产:")
        for asset in release_info.get('windows_assets', []):
            print(f"- {asset.get('name')}: {asset.get('browser_download_url')}")
    else:
        print("获取发布信息失败")
