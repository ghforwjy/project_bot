"""
小红书采集工具测试程序
用于测试采集稀土投资相关博主的内容

使用方法：
1. 先修改 target_user_id 为你要测试的博主ID
2. 运行: python tests/test_xiaohongshu_collector.py
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.xiaohongshu_collector import XiaoHongShuCollector


async def test_collect_rare_earth_blogger():
    """测试采集稀土投资博主的笔记"""
    
    # ==================== 配置区域 ====================
    # 请在这里填入你要测试的博主用户ID
    # 用户ID可以从博主主页URL获取: https://www.xiaohongshu.com/user/profile/xxxx
    target_user_id = ""  # 例如: "5f3c2b1a000000000101cdef"
    
    # 采集数量
    max_notes = 10
    
    # 是否获取详细内容
    get_detail = True
    # =================================================
    
    if not target_user_id:
        print("❌ 请先在代码中设置 target_user_id")
        print("\n如何获取用户ID：")
        print("1. 在小红书App或网页版找到目标博主")
        print("2. 进入博主主页，复制URL中 profile/ 后面的部分")
        print("3. 例如: https://www.xiaohongshu.com/user/profile/5f3c2b1a000000000101cdef")
        print("   用户ID就是: 5f3c2b1a000000000101cdef")
        return
    
    print("="*60)
    print("🧪 小红书采集工具测试")
    print("="*60)
    print(f"目标用户ID: {target_user_id}")
    print(f"采集数量: {max_notes}")
    print(f"获取详情: {'是' if get_detail else '否'}")
    print("="*60)
    
    async with XiaoHongShuCollector(headless=False, use_system_chrome=True) as collector:
        # 检查登录状态
        is_logged_in = await collector.check_login_status()
        
        if not is_logged_in:
            print("\n⚠️ 需要登录小红书")
            print("请在弹出的浏览器窗口中完成登录...")
            await collector.login()
        
        # 获取笔记列表
        print(f"\n🔍 开始采集笔记...")
        notes = await collector.get_user_notes(target_user_id, max_notes)
        
        if not notes:
            print("❌ 未获取到任何笔记")
            return
        
        print(f"\n📊 成功获取 {len(notes)} 条笔记列表")
        
        # 显示前几条笔记的标题
        print("\n📄 笔记标题预览:")
        for i, note in enumerate(notes[:5], 1):
            title = note.get('title', '无标题')[:50]
            print(f"  {i}. {title}...")
        
        # 如果需要详细内容
        if get_detail:
            print(f"\n📖 正在获取 {len(notes)} 条笔记的详细内容...")
            detailed_notes = []
            for i, note in enumerate(notes, 1):
                print(f"\n[{i}/{len(notes)}] ", end="", flush=True)
                detail = await collector.get_note_detail(note['url'])
                if detail:
                    detailed_notes.append(detail)
                    content_preview = detail.get('content', '')[:100]
                    print(f"✓ {content_preview}...")
                else:
                    detailed_notes.append(note)
                    print("✗ 获取失败")
                await asyncio.sleep(1)  # 避免请求过快
            notes = detailed_notes
        
        # 保存数据
        filename = collector.save_to_json(notes, username=target_user_id)
        
        print("\n" + "="*60)
        print("✅ 测试完成！")
        print(f"📊 共采集 {len(notes)} 条笔记")
        print(f"💾 数据已保存到: {filename}")
        print("="*60)
        
        return filename


async def test_search_rare_earth_keywords():
    """测试在小红书搜索稀土相关关键词"""
    
    print("="*60)
    print("🔍 小红书稀土关键词搜索测试")
    print("="*60)
    
    keywords = ["稀土", "稀土投资", "北方稀土", "金力永磁"]
    
    async with XiaoHongShuCollector(headless=False, use_system_chrome=True) as collector:
        # 检查登录状态
        is_logged_in = await collector.check_login_status()
        
        if not is_logged_in:
            print("\n⚠️ 需要登录小红书")
            await collector.login()
        
        # 尝试搜索关键词
        for keyword in keywords:
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            print(f"\n🔍 搜索: {keyword}")
            print(f"   URL: {search_url}")
            
            try:
                await collector.page.goto(search_url, timeout=30000)
                await asyncio.sleep(3)
                
                # 获取搜索结果数量
                result_items = await collector.page.locator('.note-item, .search-note-item, [class*="note"]').count()
                print(f"   找到约 {result_items} 条相关笔记")
                
            except Exception as e:
                print(f"   ⚠️ 搜索失败: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='小红书采集工具测试')
    parser.add_argument('--mode', choices=['collect', 'search'], default='collect',
                       help='测试模式: collect=采集博主, search=搜索关键词')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'collect':
            asyncio.run(test_collect_rare_earth_blogger())
        else:
            asyncio.run(test_search_rare_earth_keywords())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
