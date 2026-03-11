#!/usr/bin/env python3
"""
LangChain聊天功能性能测试
"""
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_response_time():
    """
    测试API响应时间
    """
    print("=== 测试API响应时间 ===")
    
    test_cases = [
        "创建一个名为'测试项目'的项目",
        "查询项目'测试项目'的信息",
        "你好，今天天气怎么样"
    ]
    
    for user_input in test_cases:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/chat/langchain/messages",
            json={"message": user_input, "session_id": f"test_session_{int(time.time())}"},
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"\n测试输入: {user_input}")
        print(f"响应时间: {response_time:.4f} 秒")
        print(f"响应状态: {response.status_code}")


def test_concurrent_requests():
    """
    测试并发请求
    """
    print("\n=== 测试并发请求 ===")
    
    import concurrent.futures
    
    def send_request(i):
        user_input = f"测试请求 {i}"
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat/langchain/messages",
            json={"message": user_input, "session_id": f"test_session_{int(time.time())}_{i}"},
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        return end_time - start_time, response.status_code
    
    # 发送10个并发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, i) for i in range(10)]
        
        response_times = []
        for future in concurrent.futures.as_completed(futures):
            response_time, status_code = future.result()
            response_times.append(response_time)
            print(f"请求响应时间: {response_time:.4f} 秒, 状态码: {status_code}")
        
        avg_response_time = sum(response_times) / len(response_times)
        print(f"\n平均响应时间: {avg_response_time:.4f} 秒")
        print(f"最大响应时间: {max(response_times):.4f} 秒")
        print(f"最小响应时间: {min(response_times):.4f} 秒")


if __name__ == "__main__":
    print("开始LangChain聊天功能性能测试")
    print("=" * 80)
    
    try:
        test_response_time()
        test_concurrent_requests()
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
    
    print("\n" + "=" * 80)
    print("LangChain聊天功能性能测试结束")
