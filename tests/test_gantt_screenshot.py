"""
测试甘特图进度条和任务条高度是否一致
使用 Playwright 截图查看实际效果
"""
from playwright.sync_api import sync_playwright
import time

def test_gantt_chart():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # 访问甘特图页面
        page.goto('http://localhost:5173/')
        print("页面已加载")
        
        # 等待页面渲染完成
        time.sleep(3)
        
        # 截图
        page.screenshot(path='e:/mycode/project_bot/tests/gantt_screenshot.png', full_page=True)
        print("截图已保存到 tests/gantt_screenshot.png")
        
        # 获取任务条和进度条的尺寸信息
        task_bars = page.locator('.gantt-task-bar').all()
        progress_bars = page.locator('.gantt-task-progress').all()
        
        print(f"\n找到 {len(task_bars)} 个任务条")
        print(f"找到 {len(progress_bars)} 个进度条")
        
        # 检查前几个任务条的尺寸
        for i, task_bar in enumerate(task_bars[:3]):
            box = task_bar.bounding_box()
            if box:
                print(f"\n任务条 {i+1}:")
                print(f"  位置: x={box['x']:.1f}, y={box['y']:.1f}")
                print(f"  尺寸: width={box['width']:.1f}, height={box['height']:.1f}")
        
        # 检查前