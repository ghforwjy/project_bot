"""
小红书采集工具调试程序
用于诊断页面加载问题
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.xiaohongshu_collector import XiaoHongShuCollector


async def debug_search():
    """调试搜索功能"""
    
    print("="*60)
    print("🐛 小红书采集工具调试模式")
    print("="*60)
    
    async with XiaoHongShuCollector(headless=False, use_system_chrome=True) as collector:
        # 检查登录状态
        print("\n1️⃣ 检查登录状态...")
        is_logged_in = await collector.check_login_status()
        print(f"   登录状态: {'已登录' if is_logged_in else '未登录'}")
        
        if not is_logged_in:
            print("\n⚠️ 需要登录，等待登录完成...")
            await collector.login()
        
        # 访问搜索页面
        keyword = "稀土"
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        
        print(f"\n2️⃣ 访问搜索页面: {search_url}")
        await collector.page.goto(search_url, timeout=60000)
        
        print("   等待页面加载...")
        await asyncio.sleep(5)
        
        # 截图查看页面状态
        screenshot_path = "tests/debug_screenshot_1.png"
        await collector.page.screenshot(path=screenshot_path, full_page=True)
        print(f"   📸 已保存截图: {screenshot_path}")
        
        # 获取页面标题
        title = await collector.page.title()
        print(f"   页面标题: {title}")
        
        # 获取当前URL
        current_url = collector.page.url
        print(f"   当前URL: {current_url}")
        
        # 尝试多种选择器查找笔记
        print(f"\n3️⃣ 查找笔记元素...")
        
        selectors = [
            '.note-item',
            '.search-note-item',
            '[class*="note-item"]',
            '[class*="search"] [class*="item"]',
            'section .item',
            'div[data-v-]',
            '.feeds-page > div',
        ]
        
        for selector in selectors:
            try:
                count = await collector.page.locator(selector).count()
                print(f"   选择器 '{selector}': {count} 个元素")
                
                if count > 0:
                    # 获取第一个元素的HTML
                    first_elem = collector.page.locator(selector).first
                    html = await first_elem.inner_html()
                    print(f"   第一个元素HTML前200字符: {html[:200]}")
                    break
            except Exception as e:
                print(f"   选择器 '{selector}': 错误 - {e}")
        
        # 滚动页面
        print(f"\n4️⃣ 滚动页面加载更多...")
        for i in range(3):
            await collector.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            print(f"   滚动 {i+1}/3")
        
        # 再次截图
        screenshot_path2 = "tests/debug_screenshot_2.png"
        await collector.page.screenshot(path=screenshot_path2, full_page=True)
        print(f"   📸 已保存截图: {screenshot_path2}")
        
        # 获取页面所有文本内容
        print(f"\n5️⃣ 页面文本内容预览:")
        try:
            body_text = await collector.page.locator('body').text_content()
            # 过滤出包含关键词的部分
            lines = body_text.split('\n')
            relevant_lines = [line.strip() for line in lines if keyword in line or '笔记' in line or '结果' in line]
            for line in relevant_lines[:10]:
                if line:
                    print(f"   {line[:100]}")
        except Exception as e:
            print(f"   获取文本失败: {e}")
        
        print("\n" + "="*60)
        print("✅ 调试完成")
        print("请查看 tests/debug_screenshot_*.png 了解页面状态")
        print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(debug_search())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
