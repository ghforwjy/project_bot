"""
测试完整的请求-响应流程，模拟真实场景

场景：
1. 用户发送消息A（假设LLM处理慢，需要2秒）
2. 用户发送消息B（1秒后，打断）
3. 消息B的响应应该先返回
4. 消息A的响应应该被丢弃

这个测试程序模拟前端、后端和LLM的完整流程
"""
import sys
import os
import time
import threading
import json
from datetime import datetime

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.session_manager import get_session_manager


class TestFullFlow:
    """测试完整的请求-响应流程"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.session_id = "test_session_full_flow"
        self.session_manager.clear_session(self.session_id)
        self.results = []  # 存储响应结果
        self.lock = threading.Lock()
    
    def simulate_llm(self, message: str, delay: float) -> str:
        """
        模拟LLM调用
        
        Args:
            message: 用户消息
            delay: 延迟时间（秒）
            
        Returns:
            LLM响应
        """
        time.sleep(delay)
        
        # 根据消息内容生成响应
        if "把信创纳入" in message:
            return """我将把'信创工作'项目纳入'信创工作大类'。确认执行吗？"""
        elif "查询" in message:
            return """我将为你查询所有项目。确认执行吗？"""
        elif "确认" in message:
            return """好的，我现在执行操作。
```json
{"intent":"query_category","data":{}}
```
操作结果: 获取项目大类列表成功
项目大类列表: - 信创工作 (项目数: 0) - 信创工作大类 (项目数: 1)"""
        else:
            return f"收到您的消息：{message}"
    
    def process_message(self, message: str, delay: float) -> dict:
        """
        模拟后端处理消息的完整流程
        
        Args:
            message: 用户消息
            delay: LLM延迟（秒）
            
        Returns:
            响应结果
        """
        # 步骤1：开始请求
        request_id = self.session_manager.start_request(self.session_id)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到消息: {message} → request_id = {request_id}")
        
        # 步骤2：调用LLM
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 调用LLM，延迟 {delay}秒")
        llm_response = self.simulate_llm(message, delay)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] LLM返回: {llm_response[:50]}...")
        
        # 步骤3：检查请求是否已被取消
        is_cancelled = self.session_manager.is_cancelled(self.session_id, request_id)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查状态: is_cancelled = {is_cancelled}")
        
        # 步骤4：返回响应
        if is_cancelled:
            response = {
                "code": 409,
                "message": "请求已过时",
                "data": {"is_outdated": True}
            }
        else:
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "message_id": f"msg_{int(time.time())}",
                    "session_id": self.session_id,
                    "role": "assistant",
                    "content": llm_response,
                    "analysis": "",
                    "content_blocks": [],
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        # 存储结果
        with self.lock:
            self.results.append({
                "message": message,
                "request_id": request_id,
                "is_cancelled": is_cancelled,
                "response": response,
                "time": datetime.now().isoformat()
            })
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成处理: {message}")
        return response
    
    def test_interrupted_request(self):
        """
        测试被打断的请求
        
        场景：
        1. 用户发送消息A（LLM延迟2秒）
        2. 1秒后，用户发送消息B（LLM延迟1秒）
        3. 验证：消息B的响应有效，消息A的响应被取消
        """
        print("\n" + "=" * 80)
        print("【测试】被打断的请求流程")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        self.results = []
        
        # 创建线程模拟并发请求
        thread_a = threading.Thread(
            target=self.process_message,
            args=("把信创纳入信创项目大类", 2)  # 延迟2秒
        )
        
        thread_b = threading.Thread(
            target=self.process_message,
            args=("查询所有项目", 1)  # 延迟1秒
        )
        
        # 启动线程
        thread_a.start()
        time.sleep(1)  # 等待1秒，模拟用户思考时间
        thread_b.start()
        
        # 等待所有线程完成
        thread_a.join()
        thread_b.join()
        
        print("\n" + "-" * 80)
        print("测试结果分析")
        print("-" * 80)
        
        # 分析结果
        message_a_result = None
        message_b_result = None
        
        for result in self.results:
            if "把信创纳入" in result["message"]:
                message_a_result = result
            elif "查询所有项目" in result["message"]:
                message_b_result = result
        
        print(f"\n消息A（把信创纳入）:")
        print(f"  request_id: {message_a_result['request_id']}")
        print(f"  is_cancelled: {message_a_result['is_cancelled']}")
        print(f"  response code: {message_a_result['response']['code']}")
        
        print(f"\n消息B（查询所有项目）:")
        print(f"  request_id: {message_b_result['request_id']}")
        print(f"  is_cancelled: {message_b_result['is_cancelled']}")
        print(f"  response code: {message_b_result['response']['code']}")
        
        # 验证
        assert message_a_result['is_cancelled'], "消息A应该被取消"
        assert not message_b_result['is_cancelled'], "消息B应该有效"
        assert message_a_result['response']['code'] == 409, "消息A的响应应该是409"
        assert message_b_result['response']['code'] == 200, "消息B的响应应该是200"
        
        print("\n✅ 测试通过！")
        print("-" * 80)
        print("结论：")
        print("- 消息A被成功取消")
        print("- 消息B正常完成")
        print("- 只有消息B的响应会被前端显示")
        
        return True
    
    def test_normal_conversation(self):
        """
        测试正常的多轮对话
        
        场景：
        1. 用户发送消息A
        2. LLM返回响应A
        3. 用户发送消息B
        4. LLM返回响应B
        5. 验证：两个响应都有效
        """
        print("\n" + "=" * 80)
        print("【测试】正常多轮对话流程")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        self.results = []
        
        # 步骤1：用户发送消息A
        response_a = self.process_message("把信创纳入信创项目大类", 0.5)
        print(f"\n响应A: {response_a['message']}")
        
        # 步骤2：用户发送消息B（确认）
        response_b = self.process_message("确认", 0.3)
        print(f"\n响应B: {response_b['message']}")
        
        # 验证
        assert response_a['code'] == 200, "响应A应该有效"
        assert response_b['code'] == 200, "响应B应该有效"
        
        print("\n✅ 测试通过！")
        print("-" * 80)
        print("结论：")
        print("- 正常多轮对话中，所有响应都有效")
        print("- 只有被打断的请求才会被取消")
        
        return True


def run_all_tests():
    """
    运行所有测试
    """
    print("=" * 80)
    print("测试完整的请求-响应流程")
    print("=" * 80)
    
    test = TestFullFlow()
    
    tests = [
        test.test_normal_conversation,
        test.test_interrupted_request,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(" ✅ 通过")
        except AssertionError as e:
            print(f" ❌ 失败: {e}")
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
