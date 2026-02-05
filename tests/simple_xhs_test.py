"""
小红书采集简化测试
使用方法：
1. 先手动在Chrome浏览器登录小红书
2. 然后运行此程序
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright


async def main():
    print("="*60)
    print("🍠 小红书采集测试（简化版）")
    print("="*60)
    
    # 启动浏览器
    playwright = await async_playwright().start()
    
    # 使用系统Chrome
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    browser = await playwright.chromium.launch(
        headless=False,
        executable_path=chrome_path
    )
    
    context = await browser.new_context()
    page = await context.new_page()
    
    print("\n1️⃣ 请先手动登录小红书")
    print("   正在打开登录页面...")
    
    await page.goto("https://www.xiaohongshu.com/login", timeout=60000)
    
    # 等待用户手动登录
    input("\n⏳ 请完成登录后按回车键继续...")
    
    # 验证登录
    await page.goto("https://www.xiaohongshu.com", timeout=30000)
    await asyncio.sleep(2)
    
    # 搜索稀土
    keyword = "稀土"
    print(f"\n2️⃣ 搜索关键词: {keyword}")
    
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
    await page.goto(search_url, timeout=60000)
    await asyncio.sleep(5)
    
    # 截图
    await page.screenshot(path="tests/search_result.png", full_page=True)
    print(f"   📸 已保存截图: tests/search_result.png")
    
    # 尝试获取笔记
    print("\n3️⃣ 尝试获取笔记...")
    
    # 滚动几次加载内容
    for i in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
    
    # 获取页面文本
    body_text = await page.locator('body').text_content()
    
    # 检查是否有搜索结果
    if '登录后查看' in body_text:
        print("   ❌ 需要登录才能查看搜索结果")
    else:
        print("   ✅ 页面已加载")
        
        # 尝试多种选择器
        selectors = [
            'div[class*="note"]',
            'div[class*="card"]',
            'section div',
            '[class*="feed"] > div',
        ]
        
        for selector in selectors:
            try:
                items = await page.locator(selector).all()
                if len(items) > 5:  # 找到足够多的元素
                    print(f"   ✓ 使用选择器 '{selector}' 找到 {len(items)} 个元素")
                    
                    # 提取前5个笔记的标题
                    notes = []
                    for item in items[:5]:
                        text = await item.text_content()
                        if text and len(text.strip()) > 10:
                            notes.append(text.strip()[:100])
                    
                    print("\n📄 前5条笔记预览:")
                    for i, note in enumerate(notes, 1):
                        print(f"   {i}. {note}...")
                    break
            except:
                continue
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    
    # 保持浏览器打开，方便查看
    input("\n按回车键关闭浏览器...")
    
    await browser.close()
    await playwright.stop()


if __name__ == "__main__":
    asyncio.run(main())
