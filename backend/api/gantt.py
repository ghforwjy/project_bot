"""
甘特图相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Project, Task
from models.schemas import GanttData, GanttTask, ResponseModel

router = APIRouter()


@router.get("/projects/{project_id}/gantt", response_model=ResponseModel)
async def get_gantt_data(project_id: int, db: Session = Depends(get_db)):
    """获取甘特图数据"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    # 转换为甘特图任务格式
    gantt_tasks = []
    for i, task in enumerate(tasks):
        if task.planned_start_date and task.planned_end_date:
            gantt_task = GanttTask(
                id=f"task_{task.id}",
                name=task.name,
                start=task.planned_start_date.strftime("%Y-%m-%d"),
                end=task.planned_end_date.strftime("%Y-%m-%d"),
                progress=int(task.progress),
                assignee=task.assignee,
                custom_class=get_task_css_class(task.status)
            )
            gantt_tasks.append(gantt_task)
    
    # 计算项目时间范围
    start_date = project.start_date
    end_date = project.end_date
    
    if tasks:
        task_starts = [t.planned_start_date for t in tasks if t.planned_start_date]
        task_ends = [t.planned_end_date for t in tasks if t.planned_end_date]
        
        if task_starts:
            start_date = min(task_starts) if not start_date or min(task_starts) < start_date else start_date
        if task_ends:
            end_date = max(task_ends) if not end_date or max(task_ends) > end_date else end_date
    
    data = GanttData(
        project_name=project.name,
        start_date=start_date.strftime("%Y-%m-%d") if start_date else "",
        end_date=end_date.strftime("%Y-%m-%d") if end_date else "",
        tasks=gantt_tasks
    )
    
    return ResponseModel(data=data.dict())


def get_task_css_class(status: str) -> str:
    """根据任务状态获取CSS类名"""
    status_class_map = {
        "pending": "bar-pending",
        "active": "bar-active",
        "completed": "bar-completed",
        "delayed": "bar-delayed",
        "cancelled": "bar-cancelled"
    }
    return status_class_map.get(status, "bar-default")
