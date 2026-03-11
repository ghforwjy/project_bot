"""
测试完整的任务名称更新流程
"""
import sys
import os
import json

# 添加backend目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from models.database import get_db
from core.project_service import get_project_service

def test_task_rename_full():
    """测试完整的任务名称更新流程"""
    # 获取数据库会话
    db: Session = next(get_db())
    
    try:
        # 获取项目服务
        project_service = get_project_service(db)
        
        # 测试数据
        project_name = "投资交易优化"
        old_task_name = "下午1点左右偶发卡卡顿"
        new_task_name = "下午1点左右系统偶发卡顿"
        
        # 查找任务
        from models.entities import Project, Task
        project = db.query(Project).filter(Project.name == project_name).first()
        
        if not project:
            print(f"项目 '{project_name}' 不存在")
            return
        
        task = db.query(Task).filter(
            Task.project_id == project.id,
            Task.name == old_task_name
        ).first()
        
        if not task:
            print(f"任务 '{old_task_name}' 不存在于项目 '{project_name}' 中")
            return
        
        print(f"找到任务: {task.name}")
        print(f"当前任务名称: {task.name}")
        
        # 模拟AI生成的指令格式
        ai_instruction = {
            "intent": "update_task",
            "data": {
                "project_name": project_name,
                "tasks": [{
                    "name": old_task_name,
                    "new_name": new_task_name
                }]
            },
            "content": f"已将'{project_name}'项目中'{old_task_name}'任务的名称更新为'{new_task_name}'",
            "requires_confirmation": False
        }
        
        print(f"\n模拟AI指令: {json.dumps(ai_instruction, ensure_ascii=False)}")
        
        # 测试更新任务名称
        task_data = ai_instruction["data"]["tasks"][0]
        result = project_service.update_task(project_name, old_task_name, task_data)
        print(f"\n更新结果: {result}")
        
        if result["success"]:
            # 重新查询任务，验证名称是否更新
            updated_task = db.query(Task).filter(Task.id == task.id).first()
            print(f"更新后任务名称: {updated_task.name}")
            
            if updated_task.name == new_task_name:
                print("✓ 任务名称更新成功！")
            else:
                print("✗ 任务名称更新失败！")
        else:
            print(f"更新失败: {result['message']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_task_rename_full()
