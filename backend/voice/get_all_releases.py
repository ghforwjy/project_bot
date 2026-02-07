"""
获取所有Whisper.cpp的发布信息，找到有Windows x64预编译版本的最新发布
"""
import requests


def get_all_releases():
    """
    获取所有Whisper.cpp的发布信息
    
    Returns:
        list: 发布信息列表
    """
    try:
        # GitHub API URL
        api_url = "https://api.github.com/repos/ggerganov/whisper.cpp/releases"
        
        # 发送请求
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        releases = response.json()
        
        return releases
        
    except Exception as e:
        print(f"获取发布信息失败: {e}")
        return []


def find_latest_windows_release(releases):
    """
    找到有Windows x64预编译版本的最新发布
    
    Args:
        releases: 发布信息列表
    
    Returns:
        dict: 包含Windows x64预编译版本的最新发布信息
    """
    for release in releases:
        # 检查是否有Windows x64资产
        windows_assets = []
        for asset in release.get('assets', []):
            if 'windows' in asset.get('name', '').lower() and 'x64' in asset.get('name', '').lower():
                windows_assets.append({
                    'name': asset.get('name'),
                    'browser_download_url': asset.get('browser_download_url')
                })
        
        if windows_assets:
            return {
                'tag_name': release.get('tag_name'),
                'windows_assets': windows_assets,
                'published_at': release.get('published_at')
            }
    
    return None


if __name__ == "__main__":
    releases = get_all_releases()
    if releases:
        print(f"找到 {len(releases)} 个发布版本")
        
        # 找到有Windows x64预编译版本的最新发布
        windows_release = find_latest_windows_release(releases)
        
        if windows_release:
            print(f"有Windows x64预编译版本的最新发布: {windows_release.get('tag_name')}")
            print(f"发布时间: {windows_release.get('published_at')}")
            print("Windows x64 资产:")
            for asset in windows_release.get('windows_assets', []):
                print(f"- {asset.get('name')}: {asset.get('browser_download_url')}")
        else:
            print("未找到有Windows x64预编译版本的发布")
    else:
        print("获取发布信息失败")
