import sqlite3

# 连接数据库
conn = sqlite3.connect('e:/mycode/project_bot/data/app.db')
cursor = conn.cursor()

# 检查特定会话的消息
session_id = 'session_1770019277559'
try:
    # 查询会话的消息数量
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE session_id = ?', (session_id,))
    count = cursor.fetchone()[0]
    print(f'Found {count} messages for session: {session_id}')
    
    # 查询最新的10条消息
    cursor.execute('''
        SELECT id, role, content, timestamp 
        FROM conversations 
        WHERE session_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (session_id,))
    
    rows = cursor.fetchall()
    print('\nLatest 10 messages:')
    for i, row in enumerate(rows, 1):
        print(f'\n{i}. ID: {row[0]}')
        print(f'   Role: {row[1]}')
        print(f'   Timestamp: {row[3]}')
        print(f'   Content: {row[2][:200]}...' if len(row[2]) > 200 else f'   Content: {row[2]}')
    
    # 检查是否有消息被删除的情况
    if count == 0:
        print('\nWARNING: No messages found for this session!')
    else:
        print(f'\nSUCCESS: Session has {count} messages stored in database.')
        
finally:
    conn.close()
