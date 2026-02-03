"""
测试项目大类API的请求-响应流程

目标：验证前端是否能正确获取后端数据

设计原则：
- 聊天请求（/chat/messages）：使用session_id隔离，同一会话中的多个请求去重
- API请求（/projects, /project-categories等）：使用session_id + path隔离
- 不同类型的请求互不影响
"""
import sys
import os
import time
import threading

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.session_manager import get_session_manager


class TestProjectCategories:
    """测试项目大类API"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.session_id = "test_project_categories"
        self.session_manager.clear_session(self.session_id)
        self.results = []
        self.lock = threading.Lock()
    
    def test_concurrent_requests(self):
        """
        测试并发请求场景
        
        场景：
        1. 前端同时发送多个不同类型的请求
        2. 验证每个请求是否正确返回（使用路径隔离）
        """
        print("\n" + "=" * 80)
        print("【测试】并发请求场景（使用路径隔离）")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        self.results = []
        
        # 模拟前端发送3个不同类型的请求
        request_configs = [
            {"name": "获取项目列表", "path": "/projects"},
            {"name": "获取项目大类", "path": "/project-categories"},
            {"name": "获取任务列表", "path": "/tasks"},
        ]
        
        threads = []
        
        def make_request(config):
            """模拟HTTP请求"""
            # 步骤1：开始请求（使用路径隔离）
            request_id = self.session_manager.start_api_request(self.session_id, config['path'])
            print(f"[{config['name']}] 开始请求: request_id = {request_id}")
            
            # 步骤2：模拟网络延迟
            time.sleep(0.1)
            
            # 步骤3：检查请求状态（使用路径隔离）
            is_cancelled = self.session_manager.is_cancelled(self.session_id, request_id, config['path'])
            print(f"[{config['name']}] 请求完成: is_cancelled = {is_cancelled}")
            
            # 步骤4：记录结果
            with self.lock:
                self.results.append({
                    "name": config['name'],
                    "request_id": request_id,
                    "path": config['path'],
                    "is_cancelled": is_cancelled,
                    "success": not is_cancelled
                })
        
        # 并发发送请求
        for config in request_configs:
            t = threading.Thread(target=make_request, args=(config,))
            threads.append(t)
            t.start()
        
        # 等待所有请求完成
        for t in threads:
            t.join()
        
        # 分析结果
        print("\n" + "-" * 80)
        print("测试结果")
        print("-" * 80)
        
        for result in self.results:
            print(f"{result['name']}:")
            print(f"  request_id: {result['request_id']}")
            print(f"  path: {result['path']}")
            print(f"  is_cancelled: {result['is_cancelled']}")
            print(f"  success: {result['success']}")
        
        # 验证：所有请求都应该成功（因为使用路径隔离）
        success_count = sum(1 for r in self.results if r['success'])
        print(f"\n成功请求数: {success_count}/{len(self.results)}")
        
        # 验证：所有请求都应该成功
        assert success_count == len(self.results), f"期望{len(self.results)}个请求全部成功，实际{success_count}个"
        
        print("\n✅ 所有请求都成功完成（路径隔离生效）")
        return True
    
    def test_chat_request_dedup(self):
        """
        测试聊天请求去重
        
        场景：
        1. 同一会话中发送多个聊天请求
        2. 只有最后一个请求应该成功
        """
        print("\n" + "=" * 80)
        print("【测试】聊天请求去重")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        self.results = []
        
        # 模拟同一会话中连续发送3个聊天请求
        chat_requests = ["消息A", "消息B", "消息C"]
        
        def make_chat_request(message, index):
            """模拟聊天请求"""
            # 步骤1：开始聊天请求（使用@chat路径）
            request_id = self.session_manager.start_chat_request(self.session_id)
            print(f"[聊天请求{index+1}] {message}: request_id = {request_id}")
            
            # 步骤2：模拟LLM延迟（越后面的请求延迟越短）
            time.sleep(0.2 - index * 0.05)
            
            # 步骤3：检查请求状态（使用@chat路径）
            is_cancelled = self.session_manager.is_chat_request_cancelled(self.session_id, request_id)
            print(f"[聊天请求{index+1}] 完成: is_cancelled = {is_cancelled}")
            
            # 步骤4：记录结果
            with self.lock:
                self.results.append({
                    "message": message,
                    "request_id": request_id,
                    "is_cancelled": is_cancelled,
                    "success": not is_cancelled
                })
        
        # 依次发送请求（模拟用户快速发送多条消息）
        for i, message in enumerate(chat_requests):
            make_chat_request(message, i)
            time.sleep(0.02)  # 极短间隔
        
        # 分析结果
        print("\n" + "-" * 80)
        print("测试结果")
        print("-" * 80)
        
        for result in self.results:
            print(f"消息'{result['message']}':")
            print(f"  request_id: {result['request_id']}")
            print(f"  is_cancelled: {result['is_cancelled']}")
            print(f"  success: {result['success']}")
        
        # 验证：只有最后一个请求成功
        success_count = sum(1 for r in self.results if r['success'])
        print(f"\n成功请求数: {success_count}/{len(self.results)}")
        
        # 验证：只有最后一个请求成功
        assert success_count == 1, f"期望1个请求成功，实际{success_count}个"
        
        # 验证：最后一个请求是"消息C"
        last_success = [r for r in self.results if r['success']][0]
        assert last_success['message'] == "消息C", f"期望最后一个成功的是'消息C'，实际是'{last_success['message']}'"
        
        print("\n✅ 聊天请求去重测试通过（只有最后一个请求成功）")
        return True
    
    def test_session_isolation(self):
        """
        测试会话隔离
        
        场景：
        1. 两个不同的会话发送请求
        2. 验证一个会话的请求不会影响另一个会话
        """
        print("\n" + "=" * 80)
        print("【测试】会话隔离")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session("session_A")
        self.session_manager.clear_session("session_B")
        
        # 会话A发送2个聊天请求
        request_a1 = self.session_manager.start_chat_request("session_A")
        request_a2 = self.session_manager.start_chat_request("session_A")
        
        # 会话B发送1个API请求
        request_b1 = self.session_manager.start_api_request("session_B", "/projects")
        
        print(f"会话A - 聊天请求1: {request_a1}")
        print(f"会话A - 聊天请求2: {request_a2}")
        print(f"会话B - API请求1: {request_b1}")
        
        # 验证
        is_a1_cancelled = self.session_manager.is_chat_request_cancelled("session_A", request_a1)
        is_a2_cancelled = self.session_manager.is_chat_request_cancelled("session_A", request_a2)
        is_b1_cancelled = self.session_manager.is_cancelled("session_B", request_b1, "/projects")
        
        print(f"\n验证结果:")
        print(f"会话A 聊天请求1 is_cancelled: {is_a1_cancelled} (期望: True)")
        print(f"会话A 聊天请求2 is_cancelled: {is_a2_cancelled} (期望: False)")
        print(f"会话B API请求1 is_cancelled: {is_b1_cancelled} (期望: False)")
        
        # 验证结果
        assert is_a1_cancelled, "会话A的聊天请求1应该被请求2取消"
        assert not is_a2_cancelled, "会话A的聊天请求2应该有效"
        assert not is_b1_cancelled, "会话B的API请求应该有效"
        
        print("\n✅ 会话隔离测试通过")
        return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("测试项目大类API的请求-响应流程")
    print("=" * 80)
    
    test = TestProjectCategories()
    
    tests = [
        test.test_concurrent_requests,
        test.test_session_isolation,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(" ✅ 通过")
            else:
                failed += 1
                print(" ❌ 失败")
        except AssertionError as e:
            print(f" ❌ 断言失败: {e}")
            failed += 1
        except Exception as e:
            print(f" ❌ 出错: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
