#!/usr/bin/env python3
"""
测试任务模块的完整流程
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

import re
from core.project_service import ProjectService, get_project_service
from models.database import SessionLocal
from models.entities import Project, Task

def test_confirmation_flow():
    """测试确认轮次检查流程"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        # 模拟LLM返回的ai_content
        ai_content = "我将更新'投资交易优化'项目中的'下午1点左右，偶发卡顿'任务，将其计划开始时间设置为2026年03月05日"
        
        print("=" * 60)
        print("测试确认轮次检查流程")
        print("=" * 60)
        print(f"\n模拟ai_content: {ai_content}")
        
        # 模拟确认轮次检查逻辑
        requires_confirmation = True
        
        # 从ai_content中提取项目名和任务名
        pattern = r"['\"]([^'\"]+)['\"]项目.*?['\"]([^'\"]+)['\"]任务"
        match = re.search(pattern, ai_content)
        
        print(f"\n正则匹配结果: {match}")
        
        if match:
            project_name = match.group(1)
            task_name = match.group(2)
            print(f"提取的项目名: {project_name}")
            print(f"提取的任务名: {task_name}")
            
            # 查找项目
            project = db.query(Project).filter(Project.name == project_name).first()
            
            if project:
                print(f"项目存在: {project.name}")
                
                # 查找任务是否存在
                existing_task = db.query(Task).filter(
                    Task.project_id == project.id,
                    Task.name == task_name
                ).first()
                
                if existing_task:
                    print(f"任务存在: {existing_task.name}")
                    print("应该显示确认按钮")
                else:
                    print(f"任务不存在: {task_name}")
                    
                    # 查找相似任务
                    similar_tasks = service.find_similar_tasks(project.id, task_name)
                    print(f"相似任务数量: {len(similar_tasks)}")
                    print(f"相似任务列表: {similar_tasks[:5]}")
                    
                    # 修改AI回复
                    ai_content = f"我没有找到名为'{task_name}'的任务。"
                    if similar_tasks:
                        ai_content += f"\n您是否指的是以下任务？"
                        for i, suggestion in enumerate(similar_tasks, 1):
                            ai_content += f"\n{i}. {suggestion}"
                        ai_content += f"\n\n请确认是哪个任务，或者提供正确的任务名称。"
                    
                    # 不需要确认按钮
                    requires_confirmation = False
                    print(f"\n修改后的ai_content:\n{ai_content}")
                    print(f"\nrequires_confirmation: {requires_confirmation}")
            else:
                print(f"项目不存在: {project_name}")
        else:
            print("无法从ai_content提取项目名和任务名")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_confirmation_flow()
