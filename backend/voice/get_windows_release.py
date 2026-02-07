"""
获取Whisper.cpp的Windows可执行文件下载链接
"""
import requests
import json


def get_windows_release_assets():
    """
    获取Whisper.cpp的Windows可执行文件下载链接
    
    Returns:
        list: Windows资产列表
    """
    try:
        # 尝试ggml-org仓库
        repositories = [
            "ggml-org/whisper.cpp",
            "ggerganov/whisper.cpp"
        ]
        
        for repo in repositories:
            print(f"检查仓库: {repo}")
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            
            response = requests.get(api_url, timeout=30)
            if response.status_code == 200:
                release_data = response.json()
                
                # 提取Windows资产
                windows_assets = []
                for asset in release_data.get('assets', []):
                    asset_name = asset.get('name', '').lower()
                    if 'windows' in asset_name:
                        windows_assets.append({
                            'name': asset.get('name'),
                            'browser_download_url': asset.get('browser_download_url'),
                            'size': asset.get('size')
                        })
                
                if windows_assets:
                    print(f"找到Windows资产: {len(windows_assets)} 个")
                    for asset in windows_assets:
                        print(f"- {asset['name']}: {asset['browser_download_url']}")
                    return windows_assets
                else:
                    print(f"未找到Windows资产")
            else:
                print(f"获取仓库信息失败: {response.status_code}")
        
        return []
        
    except Exception as e:
        print(f"发生错误: {e}")
        return []


def get_all_releases_with_windows():
    """
    获取所有包含Windows资产的发布
    
    Returns:
        list: 包含Windows资产的发布列表
    """
    try:
        repo = "ggml-org/whisper.cpp"
        api_url = f"https://api.github.com/repos/{repo}/releases"
        
        response = requests.get(api_url, timeout=30, params={"per_page": 50})
        if response.status_code == 200:
            releases = response.json()
            
            windows_releases = []
            for release in releases:
                windows_assets = []
                for asset in release.get('assets', []):
                    asset_name = asset.get('name', '').lower()
                    if 'windows' in asset_name:
                        windows_assets.append({
                            'name': asset.get('name'),
                            'browser_download_url': asset.get('browser_download_url')
                        })
                
                if windows_assets:
                    windows_releases.append({
                        'tag_name': release.get('tag_name'),
                        'published_at': release.get('published_at'),
                        'windows_assets': windows_assets
                    })
            
            return windows_releases
        
        return []
        
    except Exception as e:
        print(f"发生错误: {e}")
        return []


if __name__ == "__main__":
    print("=== 获取Windows可执行文件下载链接 ===")
    
    # 尝试获取最新发布的Windows资产
    windows_assets = get_windows_release_assets()
    
    if not windows_assets:
        print("\n=== 检查所有包含Windows资产的发布 ===")
        windows_releases = get_all_releases_with_windows()
        
        if windows_releases:
            print(f"找到 {len(windows_releases)} 个包含Windows资产的发布")
            for release in windows_releases[:5]:  # 只显示前5个
                print(f"\n发布版本: {release['tag_name']}")
                print(f"发布时间: {release['published_at']}")
                print("Windows资产:")
                for asset in release['windows_assets']:
                    print(f"- {asset['name']}: {asset['browser_download_url']}")
        else:
            print("未找到任何包含Windows资产的发布")
    
    print("\n=== 完成 ===")
