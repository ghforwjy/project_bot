"""
小红书博主笔记采集工具
用于采集指定博主的公开笔记内容，进行观点分析

使用说明：
1. 首次运行需要扫码登录
2. 登录状态会保存在 xhs_session.json 中
3. 后续运行会自动使用保存的登录状态
4. 采集的数据仅用于个人分析，请遵守相关法律法规

环境要求：
- pip install playwright
- playwright install chromium  (如果下载失败，可以使用系统Chrome)
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class XiaoHongShuCollector:
    """小红书数据采集器"""
    
    def __init__(self, headless: bool = False, use_system_chrome: bool = True):
        self.headless = headless
        self.use_system_chrome = use_system_chrome
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_file = os.path.join("tests", "xhs_session.json")
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.playwright = await async_playwright().start()
        
        # 尝试使用系统 Chrome 或 Playwright 自带的 Chromium
        try:
            if self.use_system_chrome:
                # 尝试使用系统安装的 Chrome
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.environ.get('LOCALAPPDATA', '') + r"\Google\Chrome\Application\chrome.exe",
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    print(f"🌐 使用系统 Chrome: {chrome_path}")
                    self.browser = await self.playwright.chromium.launch(
                        headless=self.headless,
                        executable_path=chrome_path,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                        ]
                    )
                else:
                    print("⚠️ 未找到系统 Chrome，使用 Playwright Chromium")
                    self.browser = await self.playwright.chromium.launch(
                        headless=self.headless,
                        args=['--disable-blink-features=AutomationControlled']
                    )
            else:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
        except Exception as e:
            print(f"⚠️ 启动浏览器失败: {e}")
            print("尝试使用 Playwright 默认 Chromium...")
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
        # 尝试加载保存的登录状态
        if os.path.exists(self.session_file):
            print(f"📂 发现已保存的登录状态: {self.session_file}")
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)
                self.context = await self.browser.new_context(storage_state=storage_state)
            except Exception as e:
                print(f"⚠️ 加载登录状态失败: {e}")
                self.context = await self.browser.new_context()
        else:
            print("🆕 首次使用，需要登录")
            self.context = await self.browser.new_context()
            
        self.page = await self.context.new_page()
        
        # 设置页面视窗大小和反检测
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.evaluate("""() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        }""")
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def check_login_status(self) -> bool:
        """检查是否已登录"""
        try:
            print("🔍 检查登录状态...")
            
            # 先访问首页检查
            await self.page.goto("https://www.xiaohongshu.com", timeout=30000)
            await asyncio.sleep(3)
            
            current_url = self.page.url
            
            # 如果重定向到登录页，说明未登录
            if '/login' in current_url:
                print("⚠️ 未登录（在登录页面）")
                return False
            
            # 检查是否有用户头像或发布按钮
            avatar = await self.page.locator('.avatar img, .user-avatar, [class*="avatar"]').count()
            publish_btn = await self.page.locator('.publish-btn, [class*="publish"]').count()
            
            if avatar > 0 or publish_btn > 0:
                print("✅ 首页已登录")
                
                # 再检查搜索页面是否也需要登录
                print("🔍 检查搜索页面权限...")
                await self.page.goto("https://www.xiaohongshu.com/search_result?keyword=test", timeout=30000)
                await asyncio.sleep(3)
                
                # 检查页面内容是否包含"登录后查看"
                page_text = await self.page.locator('body').text_content()
                if '登录后查看' in page_text or '扫码' in page_text:
                    print("⚠️ 搜索页面需要重新登录")
                    return False
                
                print("✅ 搜索页面已登录")
                return True
            else:
                print("⚠️ 未检测到登录状态")
                return False
        except Exception as e:
            print(f"❌ 检查登录状态失败: {e}")
            return False
            
    async def login(self):
        """执行登录流程"""
        print("\n" + "="*50)
        print("📝 登录小红书")
        print("="*50)
        print("请在弹出的浏览器窗口中完成登录")
        print("支持方式：手机号/微信/QQ/微博/扫码")
        print("="*50)
        print("\n⚠️ 重要提示：")
        print("- 请等待二维码完全加载后再扫码")
        print("- 扫码后需要在手机上确认登录")
        print("- 登录完成后请在这里按回车键继续")
        print("="*50 + "\n")
        
        # 访问登录页面
        await self.page.goto("https://www.xiaohongshu.com/login", timeout=60000)
        
        print("🔔 浏览器已打开，请完成登录操作")
        print("（如果二维码过期，请在浏览器中刷新页面）\n")
        
        # 等待用户按回车确认
        input("⏳ 登录完成后请按回车键继续...")
        
        # 验证登录状态
        await self.page.goto("https://www.xiaohongshu.com", timeout=30000)
        await asyncio.sleep(2)
        
        avatar = await self.page.locator('.avatar img, .user-avatar').count()
        if avatar > 0:
            print("✅ 登录成功！")
        else:
            print("⚠️ 可能未登录成功，但继续执行...")
        
        # 保存登录状态
        try:
            storage_state = await self.context.storage_state()
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, ensure_ascii=False, indent=2)
            print(f"💾 登录状态已保存到: {self.session_file}")
        except Exception as e:
            print(f"⚠️ 保存登录状态失败: {e}")
            
        await asyncio.sleep(2)
            
    async def get_user_notes(self, user_id: str, max_notes: int = 30) -> List[Dict]:
        """
        获取指定用户的笔记列表
        
        Args:
            user_id: 用户ID（可从用户主页URL中获取，如 https://www.xiaohongshu.com/user/profile/xxx 中的 xxx）
            max_notes: 最多采集的笔记数量
            
        Returns:
            笔记列表，每个笔记包含标题、内容、点赞数等信息
        """
        notes = []
        user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        
        print(f"\n🔍 正在访问用户主页: {user_url}")
        await self.page.goto(user_url, timeout=60000)
        await asyncio.sleep(3)
        
        # 获取用户名
        try:
            username_elem = await self.page.locator('.user-name, [class*="nickname"], h1').first
            username = await username_elem.text_content() if username_elem else "未知用户"
            print(f"👤 目标用户: {username.strip()}")
        except:
            username = "未知用户"
            
        # 等待笔记列表加载
        print("⏳ 等待笔记列表加载...")
        await asyncio.sleep(2)
        
        # 滚动加载更多笔记
        scroll_count = 0
        max_scroll = (max_notes // 6) + 5  # 估算滚动次数
        last_note_count = 0
        no_change_count = 0
        
        while scroll_count < max_scroll and len(notes) < max_notes and no_change_count < 3:
            # 获取当前页面的笔记元素
            # 小红书的笔记选择器可能会变化，这里使用多种可能的选择器
            selectors = [
                '.feeds-page .note-item',
                '.user-notes .note-item', 
                '[class*="note-item"]',
                '.feeds-container > div > div',
                '.note-container',
            ]
            
            note_items = []
            for selector in selectors:
                try:
                    items = await self.page.locator(selector).all()
                    if len(items) > len(note_items):
                        note_items = items
                except:
                    continue
                    
            print(f"📄 当前页面找到 {len(note_items)} 个笔记元素")
            
            # 解析笔记
            for item in note_items[len(notes):max_notes]:
                try:
                    note_data = await self._extract_note_info(item)
                    if note_data and note_data not in notes:
                        notes.append(note_data)
                        title = note_data.get('title', '无标题')[:40]
                        print(f"  ✓ {title}...")
                except Exception as e:
                    continue
                    
            # 检查是否有新内容
            if len(notes) == last_note_count:
                no_change_count += 1
            else:
                no_change_count = 0
            last_note_count = len(notes)
            
            if len(notes) >= max_notes:
                break
                
            # 滚动页面加载更多
            print(f"🔄 滚动页面加载更多... ({scroll_count + 1}/{max_scroll})")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            scroll_count += 1
            
        print(f"\n✅ 共采集到 {len(notes)} 条笔记")
        return notes
        
    async def _extract_note_info(self, note_element) -> Optional[Dict]:
        """从笔记元素中提取信息"""
        try:
            # 获取笔记链接
            link_elem = await note_element.locator('a').first
            href = await link_elem.get_attribute('href') if link_elem else None
            
            if not href:
                return None
                
            note_id = href.split('/')[-1].split('?')[0] if href else None
            
            # 获取标题 - 尝试多种选择器
            title = ""
            for title_selector in ['.title', '.note-title', '[class*="title"]', 'span']:
                try:
                    title_elem = await note_element.locator(title_selector).first
                    if title_elem:
                        title = await title_elem.text_content() or ""
                        if title.strip():
                            break
                except:
                    continue
            
            # 获取封面图
            cover_url = ""
            try:
                img_elem = await note_element.locator('img').first
                if img_elem:
                    cover_url = await img_elem.get_attribute('src') or ""
            except:
                pass
            
            # 获取点赞数
            like_count = "0"
            try:
                for like_selector in ['.like-count', '.count', '[class*="like"]', '[class*="count"]']:
                    like_elem = await note_element.locator(like_selector).first
                    if like_elem:
                        like_count = await like_elem.text_content() or "0"
                        if like_count.strip():
                            break
            except:
                pass
            
            return {
                "note_id": note_id,
                "title": title.strip() if title else "",
                "cover_url": cover_url,
                "like_count": like_count.strip() if like_count else "0",
                "url": f"https://www.xiaohongshu.com{href}" if href.startswith('/') else href
            }
        except Exception as e:
            return None
            
    async def get_note_detail(self, note_url: str) -> Optional[Dict]:
        """
        获取单条笔记的详细内容
        
        Args:
            note_url: 笔记链接
            
        Returns:
            包含完整内容的笔记信息
        """
        print(f"📖 获取详情: {note_url[:60]}...")
        
        try:
            await self.page.goto(note_url, timeout=60000)
            await asyncio.sleep(3)
            
            # 提取标题
            title = ""
            for title_selector in ['.title', 'h1', '[class*="title"]', '.note-title']:
                try:
                    title_elem = await self.page.locator(title_selector).first
                    if title_elem:
                        title = await title_elem.text_content() or ""
                        if title.strip():
                            break
                except:
                    continue
            
            # 提取正文内容
            content = ""
            for content_selector in ['.note-content .desc', '.content .desc', '[class*="content"] [class*="desc"]', '.desc']:
                try:
                    content_elem = await self.page.locator(content_selector).first
                    if content_elem:
                        content = await content_elem.text_content() or ""
                        if content.strip():
                            break
                except:
                    continue
            
            # 提取作者信息
            author = ""
            try:
                for author_selector in ['.author .name', '.user-info .name', '[class*="author"]']:
                    author_elem = await self.page.locator(author_selector).first
                    if author_elem:
                        author = await author_elem.text_content() or ""
                        if author.strip():
                            break
            except:
                pass
            
            # 提取互动数据
            stats = {"likes": "0", "collects": "0", "comments": "0"}
            try:
                # 尝试获取各种统计数据
                stat_elements = await self.page.locator('[class*="count"], [class*="like"], [class*="collect"], [class*="comment"]').all()
                for elem in stat_elements:
                    text = await elem.text_content() or ""
                    class_attr = await elem.get_attribute('class') or ""
                    if 'like' in class_attr.lower():
                        stats['likes'] = text.strip()
                    elif 'collect' in class_attr.lower():
                        stats['collects'] = text.strip()
                    elif 'comment' in class_attr.lower():
                        stats['comments'] = text.strip()
            except:
                pass
            
            # 提取发布时间
            publish_time = ""
            try:
                for time_selector in ['.time', '.publish-time', '[class*="time"]', 'time']:
                    time_elem = await self.page.locator(time_selector).first
                    if time_elem:
                        publish_time = await time_elem.text_content() or ""
                        if publish_time.strip():
                            break
            except:
                pass
            
            # 提取图片
            images = []
            try:
                img_elements = await self.page.locator('.note-content img, .content img, [class*="note"] img').all()
                for img in img_elements[:9]:  # 最多9张图
                    src = await img.get_attribute('src')
                    if src and 'http' in src:
                        images.append(src)
            except:
                pass
            
            return {
                "title": title.strip(),
                "content": content.strip(),
                "author": author.strip(),
                "publish_time": publish_time.strip(),
                "url": note_url,
                "statistics": stats,
                "images": images,
                "crawl_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 获取详情失败: {e}")
            return None
            
    def save_to_json(self, data: List[Dict], filename: str = None, username: str = ""):
        """保存数据到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_username = "".join(c for c in username if c.isalnum() or c in '_-')[:20]
            filename = f"xiaohongshu_notes_{safe_username}_{timestamp}.json"
            
        # 确保在tests目录下
        filepath = os.path.join("tests", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
        output = {
            "source": "小红书",
            "crawl_time": datetime.now().isoformat(),
            "total_count": len(data),
            "target_user": username,
            "notes": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 数据已保存到: {filepath}")
        return filepath


async def main():
    """主函数"""
    print("="*60)
    print("🍠 小红书博主笔记采集工具")
    print("="*60)
    print("\n使用说明：")
    print("1. 首次运行需要扫码登录小红书")
    print("2. 登录状态会保存，下次自动使用")
    print("3. 采集的数据仅用于个人分析")
    print("4. 请遵守相关法律法规和小红书用户协议")
    print("="*60 + "\n")
    
    # 用户输入
    print("如何获取用户ID：")
    print("  1. 打开目标博主的小红书主页")
    print("  2. 查看浏览器地址栏，格式如：")
    print("     https://www.xiaohongshu.com/user/profile/5f3c2b1a000000000101cdef")
    print("  3. 复制 profile/ 后面的部分（即 5f3c2b1a000000000101cdef）")
    print()
    
    user_id = input("请输入博主用户ID: ").strip()
    if not user_id:
        print("❌ 用户ID不能为空")
        return
        
    try:
        max_notes = int(input("请输入要采集的笔记数量（默认20）: ") or "20")
    except:
        max_notes = 20
        
    get_detail = input("是否获取笔记详细内容？(y/n，默认n）: ").strip().lower() == 'y'
    
    # 启动采集器
    async with XiaoHongShuCollector(headless=False, use_system_chrome=True) as collector:
        # 检查登录状态
        is_logged_in = await collector.check_login_status()
        
        if not is_logged_in:
            await collector.login()
            
        # 获取笔记列表
        notes = await collector.get_user_notes(user_id, max_notes)
        
        if not notes:
            print("⚠️ 未获取到任何笔记")
            return
            
        # 如果需要详细内容，逐个获取
        if get_detail:
            print(f"\n📖 正在获取 {len(notes)} 条笔记的详细内容...")
            detailed_notes = []
            for i, note in enumerate(notes, 1):
                print(f"\n[{i}/{len(notes)}] ", end="")
                detail = await collector.get_note_detail(note['url'])
                if detail:
                    detailed_notes.append(detail)
                else:
                    detailed_notes.append(note)
                await asyncio.sleep(1)  # 避免请求过快
            notes = detailed_notes
            
        # 保存数据
        filename = collector.save_to_json(notes, username=user_id)
        
        print("\n" + "="*60)
        print("✅ 采集完成！")
        print(f"📊 共采集 {len(notes)} 条笔记")
        print(f"💾 数据已保存到: {filename}")
        print("\n提示：")
        print("- 数据文件位于 tests/ 目录下")
        print("- 可以使用 JSON 查看器或文本编辑器打开")
        print("- 建议定期删除 xhs_session.json 以重新登录")
        print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
