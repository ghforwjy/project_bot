"""
测试多轮对话场景下的请求去重机制

场景：
1. 用户开始一个多轮对话（步骤1）
2. 用户发送新消息打断（步骤2）
3. 步骤1的LLM响应应该被丢弃

这个测试程序验证前端request_id去重机制是否正确工作
"""
import sys
import os
import json
import time
from datetime import datetime

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.session_manager import get_session_manager


class TestRequestDeduplication:
    """测试请求去重机制"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.session_id = "test_session_001"
        # 清理测试会话
        self.session_manager.clear_session(self.session_id)
    
    def test_normal_conversation(self):
        """测试正常多轮对话（不应该去重）"""
        print("\n" + "=" * 80)
        print("【测试1】正常多轮对话")
        print("=" * 80)
        
        # 步骤1：用户开始对话
        request_id_1 = self.session_manager.start_request(self.session_id)
        print(f"步骤1：start_request() → request_id = {request_id_1}")
        
        # 步骤1完成，检查
        is_cancelled_1 = self.session_manager.is_cancelled(self.session_id, request_id_1)
        print(f"步骤1完成：is_cancelled({request_id_1}) = {is_cancelled_1}")
        assert not is_cancelled_1, "正常完成，不应该被取消"
        
        # 步骤2：用户追问（独立请求）
        request_id_2 = self.session_manager.start_request(self.session_id)
        print(f"步骤2：start_request() → request_id = {request_id_2}")
        
        # 步骤2完成，检查
        is_cancelled_2 = self.session_manager.is_cancelled(self.session_id, request_id_2)
        print(f"步骤2完成：is_cancelled({request_id_2}) = {is_cancelled_2}")
        assert not is_cancelled_2, "正常完成，不应该被取消"
        
        # 验证：request_id不同，说明是两个独立请求
        assert request_id_1 != request_id_2, "两个请求应该有不同ID"
        
        print("✅ 正常多轮对话测试通过")
        return True
    
    def test_interrupted_conversation(self):
        """测试被打断的多轮对话（应该去重）"""
        print("\n" + "=" * 80)
        print("【测试2】被打断的多轮对话")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        
        # 步骤1：用户开始对话（假设LLM处理慢）
        request_id_1 = self.session_manager.start_request(self.session_id)
        print(f"步骤1：start_request() → request_id = {request_id_1}")
        
        # 步骤2：用户立即发送新消息（打断）
        request_id_2 = self.session_manager.start_request(self.session_id)
        print(f"步骤2（打断）：start_request() → request_id = {request_id_2}")
        
        # 验证：request_id被替换了
        print(f"\n验证：request_id_1 = {request_id_1}")
        print(f"验证：request_id_2 = {request_id_2}")
        print(f"验证：当前会话的request_id = {self.session_manager.get_active_request_id(self.session_id)}")
        
        # 步骤1完成（假设LLM终于返回了）
        is_cancelled_1 = self.session_manager.is_cancelled(self.session_id, request_id_1)
        print(f"\n步骤1完成：is_cancelled({request_id_1}) = {is_cancelled_1}")
        assert is_cancelled_1, "步骤1应该被取消（因为被步骤2打断了）"
        
        # 步骤2完成
        is_cancelled_2 = self.session_manager.is_cancelled(self.session_id, request_id_2)
        print(f"步骤2完成：is_cancelled({request_id_2}) = {is_cancelled_2}")
        assert not is_cancelled_2, "步骤2正常完成，不应该被取消"
        
        print("✅ 被打断的多轮对话测试通过")
        return True
    
    def test_rapid_messages(self):
        """测试快速连续发送消息"""
        print("\n" + "=" * 80)
        print("【测试3】快速连续发送消息")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        
        # 模拟用户快速发送3条消息
        request_ids = []
        for i in range(3):
            request_id = self.session_manager.start_request(self.session_id)
            request_ids.append(request_id)
            print(f"消息{i+1}：request_id = {request_id}")
            time.sleep(0.01)  # 模拟极短间隔
        
        # 只有最后一个请求有效
        active_id = self.session_manager.get_active_request_id(self.session_id)
        print(f"\n当前活跃的request_id = {active_id}")
        
        # 验证
        for i, rid in enumerate(request_ids[:-1]):
            is_cancelled = self.session_manager.is_cancelled(self.session_id, rid)
            print(f"消息{i+1}的request_id {rid}: is_cancelled = {is_cancelled}")
            assert is_cancelled, f"消息{i+1}应该被取消"
        
        # 最后一个请求有效
        is_cancelled = self.session_manager.is_cancelled(self.session_id, request_ids[-1])
        print(f"消息3的request_id {request_ids[-1]}: is_cancelled = {is_cancelled}")
        assert not is_cancelled, "最后一个请求应该有效"
        
        print("✅ 快速连续发送消息测试通过")
        return True
    
    def test_conversation_context(self):
        """测试多轮对话的上下文关联"""
        print("\n" + "=" * 80)
        print("【测试4】多轮对话上下文关联")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session(self.session_id)
        
        # 正常多轮对话流程
        print("\n--- 正常流程 ---")
        
        # 步骤1：用户开始对话
        req1 = self.session_manager.start_request(self.session_id)
        print(f"用户：把信创纳入信创项目大类")
        print(f"后端：start_request() → {req1}")
        print(f"状态：is_cancelled({req1}) = {self.session_manager.is_cancelled(self.session_id, req1)}")
        
        # 步骤2：用户确认
        req2 = self.session_manager.start_request(self.session_id)
        print(f"\n用户：确认")
        print(f"后端：start_request() → {req2}")
        print(f"状态：is_cancelled({req2}) = {self.session_manager.is_cancelled(self.session_id, req2)}")
        print(f"状态：is_cancelled({req1}) = {self.session_manager.is_cancelled(self.session_id, req1)}")
        
        # 步骤2完成，有效
        assert not self.session_manager.is_cancelled(self.session_id, req2)
        assert self.session_manager.is_cancelled(self.session_id, req1)
        print("验证：req2有效，req1被取消 ✅")
        
        print("\n--- 打断流程 ---")
        
        # 清理，重新开始
        self.session_manager.clear_session(self.session_id)
        
        # 步骤1：用户开始对话
        req1 = self.session_manager.start_request(self.session_id)
        print(f"\n用户（步骤1）：把信创纳入信创项目大类")
        print(f"后端：start_request() → {req1}")
        
        # 步骤2：用户打断（发送不相关消息）
        req2 = self.session_manager.start_request(self.session_id)
        print(f"\n用户（步骤2，打断）：顺便帮我查询一下所有项目")
        print(f"后端：start_request() → {req2}")
        
        # 验证
        print(f"\n验证结果：")
        print(f"- req1 ({req1}): is_cancelled = {self.session_manager.is_cancelled(self.session_id, req1)}")
        print(f"- req2 ({req2}): is_cancelled = {self.session_manager.is_cancelled(self.session_id, req2)}")
        
        assert self.session_manager.is_cancelled(self.session_id, req1), "步骤1应该被取消"
        assert not self.session_manager.is_cancelled(self.session_id, req2), "步骤2应该有效"
        
        print("✅ 多轮对话上下文关联测试通过")
        return True
    
    def test_multiple_sessions(self):
        """测试多个会话隔离"""
        print("\n" + "=" * 80)
        print("【测试5】多个会话隔离")
        print("=" * 80)
        
        # 清理
        self.session_manager.clear_session("session_A")
        self.session_manager.clear_session("session_B")
        
        # 会话A的请求
        req_a1 = self.session_manager.start_request("session_A")
        req_a2 = self.session_manager.start_request("session_A")
        
        # 会话B的请求
        req_b1 = self.session_manager.start_request("session_B")
        
        print(f"会话A - req_a1: {req_a1}")
        print(f"会话A - req_a2: {req_a2}")
        print(f"会话B - req_b1: {req_b1}")
        
        # 验证：会话A的req_a1应该被req_a2取消
        assert self.session_manager.is_cancelled("session_A", req_a1)
        assert not self.session_manager.is_cancelled("session_A", req_a2)
        
        # 验证：会话B的req_b1应该有效
        assert not self.session_manager.is_cancelled("session_B", req_b1)
        
        # 验证：会话A和会话B相互独立
        # 会话A不会影响会话B的请求状态
        active_a = self.session_manager.get_active_request_id("session_A")
        active_b = self.session_manager.get_active_request_id("session_B")
        print(f"\n会话A活跃request_id: {active_a}")
        print(f"会话B活跃request_id: {active_b}")
        
        assert active_a == req_a2, "会话A的活跃请求应该是req_a2"
        assert active_b == req_b1, "会话B的活跃请求应该是req_b1"
        assert active_a != active_b, "两个会话的活跃请求ID应该不同"
        
        print("✅ 多个会话隔离测试通过")
        return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("测试请求去重机制")
    print("=" * 80)
    
    test = TestRequestDeduplication()
    
    tests = [
        test.test_normal_conversation,
        test.test_interrupted_conversation,
        test.test_rapid_messages,
        test.test_conversation_context,
        test.test_multiple_sessions,
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
