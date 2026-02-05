"""
测试历史对话选择功能和新对话创建功能
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_create_session():
    """测试创建新会话"""
    print("\n=== 测试创建新会话 ===")
    
    response = requests.post(f"{BASE_URL}/chat/sessions")
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200 and "data" in data:
            session_id = data["data"].get("session_id")
            print(f"✓ 新会话创建成功，会话ID: {session_id}")
            return session_id
        else:
            print(f"✗ 新会话创建失败: {data.get('message')}")
            return None
    else:
        print(f"✗ 请求失败: {response.text}")
        return None

def test_get_sessions():
    """测试获取会话列表"""
    print("\n=== 测试获取会话列表 ===")
    
    response = requests.get(f"{BASE_URL}/chat/sessions")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200 and "data" in data:
            sessions = data["data"].get("sessions", [])
            print(f"✓ 获取会话列表成功，共 {len(sessions)} 个会话")
            for session in sessions:
                print(f"  - {session['id']}: {session['name']} ({session['timestamp']})")
            return sessions
        else:
            print(f"✗ 获取会话列表失败: {data.get('message')}")
            return []
    else:
        print(f"✗ 请求失败: {response.text}")
        return []

def test_batch_delete_sessions(session_ids):
    """测试批量删除会话"""
    print(f"\n=== 测试批量删除会话 (共 {len(session_ids)} 个) ===")
    
    response = requests.delete(
        f"{BASE_URL}/chat/sessions/batch",
        json={"session_ids": session_ids}
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            deleted_sessions = data["data"].get("deleted_sessions", 0)
            deleted_messages = data["data"].get("deleted_messages", 0)
            print(f"✓ 批量删除成功，删除了 {deleted_sessions} 个会话，{deleted_messages} 条消息")
            return True
        else:
            print(f"✗ 批量删除失败: {data.get('message')}")
            return False
    else:
        print(f"✗ 请求失败: {response.text}")
        return False

def test_delete_single_session(session_id):
    """测试删除单个会话"""
    print(f"\n=== 测试删除单个会话 {session_id} ===")
    
    response = requests.delete(f"{BASE_URL}/chat/sessions/{session_id}")
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            deleted_messages = data["data"].get("deleted_messages", 0)
            print(f"✓ 删除会话成功，删除了 {deleted_messages} 条消息")
            return True
        else:
            print(f"✗ 删除会话失败: {data.get('message')}")
            return False
    else:
        print(f"✗ 请求失败: {response.text}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试历史对话选择功能和新对话创建功能")
    print("=" * 60)
    
    # 测试1: 创建多个新会话
    print("\n【测试1】创建多个新会话")
    created_session_ids = []
    for i in range(3):
        session_id = test_create_session()
        if session_id:
            created_session_ids.append(session_id)
        time.sleep(0.5)  # 避免请求过快
    
    print(f"\n✓ 共创建了 {len(created_session_ids)} 个新会话")
    
    # 测试2: 获取会话列表
    print("\n【测试2】获取会话列表")
    sessions = test_get_sessions()
    
    # 测试3: 批量删除会话
    if len(created_session_ids) >= 2:
        print("\n【测试3】批量删除会话")
        # 删除前2个会话
        session_ids_to_delete = created_session_ids[:2]
        test_batch_delete_sessions(session_ids_to_delete)
    else:
        print("\n【测试3】跳过批量删除测试（会话数量不足）")
    
    # 测试4: 删除单个会话
    if len(created_session_ids) > 2:
        print("\n【测试4】删除单个会话")
        test_delete_single_session(created_session_ids[2])
    
    # 测试5: 再次获取会话列表，验证删除结果
    print("\n【测试5】验证删除结果")
    sessions_after = test_get_sessions()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
