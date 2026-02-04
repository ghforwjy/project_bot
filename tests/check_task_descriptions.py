"""
查看数据库中的实际任务数据,确认description字段的真实情况
"""
import sqlite3
import json
from typing import Dict, Any, List

def get_database_path():
    """获取数据库路径"""
    import os
    db_path = "e:\\mycode\\project_bot\\backend\\project_bot.db"
    return db_path

def query_tasks_with_descriptions() -> List[Dict[str, Any]]:
    """查询所有任务及其描述"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 查询任务表结构
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        print("=" * 80)
        print("tasks表结构:")
        print("=" * 80)
        for col in columns:
            print(f"  {col[1]:20s} {col[2]:15s} NOT NULL: {not col[3]}")
        print()
        
        # 查询所有任务
        cursor.execute("""
            SELECT 
                t.id,
                t.project_id,
                t.name,
                t.description,
                t.deliverable,
                t.assignee,
                t.progress,
                t.status,
                p.name as project_name
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            ORDER BY t.id
        """)
        
        tasks = cursor.fetchall()
        
        print("=" * 80)
        print(f"找到 {len(tasks)} 个任务:")
        print("=" * 80)
        
        for task in tasks:
            print(f"\n任务ID: {task['id']}")
            print(f"  项目: {task['project_name']}")
            print(f"  名称: {task['name']}")
            print(f"  描述(description): {task['description'] or '(空)'}")
            print(f"  交付物(deliverable): {task['deliverable'] or '(空)'}")
            print(f"  负责人: {task['assignee'] or '(空)'}")
            print(f"  进度: {task['progress']}%")
            print(f"  状态: {task['status']}")
        
        return [dict(task) for task in tasks]
        
    except Exception as e:
        print(f"查询失败: {e}")
        return []
    finally:
        conn.close()

def check_gantt_api_response():
    """检查甘特图API的实际返回数据"""
    import requests
    
    print("\n" + "=" * 80)
    print("检查甘特图API返回数据:")
    print("=" * 80)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/gantt/all", timeout=10)
        
        if response.status_code != 200:
            print(f"API请求失败: {response.status_code}")
            return
        
        data = response.json()
        categories = data.get("data", {}).get("project_categories", [])
        
        for category in categories:
            print(f"\n大类: {category['name']}")
            for project in category.get("projects", []):
                print(f"  项目: {project['name']}")
                for task in project.get("tasks", []):
                    print(f"    任务: {task['name']}")
                    print(f"      字段: {list(task.keys())}")
                    if 'description' in task:
                        print(f"      description: {task['description']}")
                    else:
                        print(f"      description: (不存在)")
        
    except Exception as e:
        print(f"API请求失败: {e}")

if __name__ == "__main__":
    import os
    
    print("检查数据库中的任务数据...")
    tasks = query_tasks_with_descriptions()
    
    print("\n" + "=" * 80)
    print("检查甘特图API返回数据...")
    check_gantt_api_response()
    
    print("\n" + "=" * 80)
    print("总结:")
    print("=" * 80)
    
    if tasks:
        has_description = sum(1 for t in tasks if t.get('description'))
        has_deliverable = sum(1 for t in tasks if t.get('deliverable'))
        
        print(f"总任务数: {len(tasks)}")
        print(f"有description的任务: {has_description}")
        print(f"有deliverable的任务: {has_deliverable}")
        
        if has_description > 0:
            print("\n有description的任务示例:")
            for task in tasks[:3]:
                if task.get('description'):
                    print(f"  - {task['name']}: {task['description']}")
        
        if has_deliverable > 0:
            print("\n有deliverable的任务示例:")
            for task in tasks[:3]:
                if task.get('deliverable'):
                    print(f"  - {task['name']}: {task['deliverable']}")