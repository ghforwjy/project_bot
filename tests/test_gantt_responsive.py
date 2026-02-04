import time
import os
from playwright.sync_api import sync_playwright

# 测试甘特图的响应式设计
def test_gantt_responsive():
    """测试甘特图在不同屏幕尺寸下的显示效果"""
    # 创建测试结果目录
    test_dir = "e:\\mycode\\project_bot\\tests\\gantt_responsive_test"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        try:
            # 打开甘特图页面
            page = context.new_page()
            page.goto("http://localhost:5173/")
            
            # 等待甘特图加载
            page.wait_for_selector(".gantt-chart", timeout=10000)
            
            # 测试不同屏幕尺寸
            viewports = [
                {"name": "desktop", "width": 1920, "height": 1080},
                {"name": "laptop", "width": 1366, "height": 768},
                {"name": "tablet", "width": 768, "height": 1024},
                {"name": "mobile", "width": 375, "height": 667}
            ]
            
            for viewport in viewports:
                print(f"测试 {viewport['name']} 尺寸: {viewport['width']}x{viewport['height']}")
                
                # 设置视口大小
                page.set_viewport_size({
                    "width": viewport["width"],
                    "height": viewport["height"]
                })
                
                # 等待页面适应
                time.sleep(2)
                
                # 截图
                screenshot_path = os.path.join(test_dir, f"gantt_{viewport['name']}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  截图保存到: {screenshot_path}")
                
                # 检查甘特图元素是否存在
                if page.is_visible(".gantt-chart"):
                    print("  ✅ 甘特图可见")
                else:
                    print("  ❌ 甘特图不可见")
                
                # 检查任务条是否存在
                task_bars = page.query_selector_all(".gantt-task-bar")
                print(f"  ✅ 发现 {len(task_bars)} 个任务条")
            
        finally:
            # 关闭浏览器
            browser.close()
    
    print("\n测试完成！")
    print(f"测试结果和截图保存在: {test_dir}")

if __name__ == "__main__":
    test_gantt_responsive()
