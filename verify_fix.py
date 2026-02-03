import requests

# 验证修复效果
# 检查特定会话的消息是否能完整返回
session_id = 'session_1770019277559'

print(f'验证会话 {session_id} 的消息加载情况...')

# 调用后端API
response = requests.get(f'http://localhost:8000/api/v1/chat/history?session_id={session_id}')

if response.status_code == 200:
    data = response.json()
    total_messages = data.get('data', {}).get('total', 0)
    items = data.get('data', {}).get('items', [])
    
    print(f'Status code: {response.status_code}')
    print(f'Total messages: {total_messages}')
    print(f'Number of items returned: {len(items)}')
    
    if items:
        # 打印第一条消息（最早的）
        first_msg = items[0]
        print(f'\nFirst message (earliest):')
        print(f'Role: {first_msg.get("role")}')
        print(f'Content: {first_msg.get("content", "")[:100]}...')
        print(f'Timestamp: {first_msg.get("timestamp")}')
        
        # 打印最后一条消息（最新的）
        last_msg = items[-1]
        print(f'\nLast message (latest):')
        print(f'Role: {last_msg.get("role")}')
        print(f'Content: {last_msg.get("content", "")[:100]}...')
        print(f'Timestamp: {last_msg.get("timestamp")}')
        
        # 验证消息是否按时间顺序排列
        timestamps = [msg.get('timestamp') for msg in items]
        is_sorted = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
        print(f'\nMessages are in chronological order: {is_sorted}')
        
    print('\n修复验证完成！')
else:
    print(f'Error: {response.status_code}')
    print(f'Response: {response.text}')
