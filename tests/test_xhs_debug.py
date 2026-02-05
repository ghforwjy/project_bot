"""
小红书采集工具调试程序
用于诊断页面加载问题
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.xiaohongshu_collector import XiaoHongShuCollector


async def debug_search_page():
    """调试搜索页面"""
    
    print("="*60)
    print("🔧 小红书搜索页面调试")
    print("="*60)
    
    keyword = "稀土"
    
    async with XiaoHongShuCollector(headless=False, use_system_chrome=True) as collector:
        # 检查登录
        is_logged_in = await collector.check_login_status()
        if not is_logged_in:
            print("⚠️ 需要登录")
            await collector.login()
        
        # 访问搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        print(f"\n🌐 访问: {search_url}")
        
        await collector.page.goto(search_url, timeout=60000)
        print("✅ 页面加载完成")
        
        # 等待更长时间让内容加载
        print("⏳ 等待内容加载...")
        await asyncio.sleep(5)
        
        # 截图保存
        screenshot_path = "tests/xiaohongshu_search_debug.png"
        await collector.page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 截图已保存: {screenshot_path}")
        
        # 获取页面标题
        title = await collector.page.title()
