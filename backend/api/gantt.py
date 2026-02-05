"""
甘特图相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Project, Task, ProjectCategory
from models.schemas import GanttData, GanttTask, ResponseModel, AllGanttData, ProjectCategoryGantt, ProjectGantt, ProjectPhase

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
        # 根据任务状态和时间字段优先级选择合适的时间字段
        start_date = None
        end_date = None
        start_time_type = "planned"
        end_time_type = "planned"
        
        if task.status == "pending":
            # 待处理状态：只使用计划时间
            start_date = task.planned_start_date
            end_date = task.planned_end_date
        elif task.status == "active":
            # 进行中状态：开始时间优先使用实际时间，结束时间使用计划时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
        elif task.status == "completed" or task.status == "cancelled":
            # 已完成或已取消状态：优先使用实际时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.actual_end_date or task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
            if task.actual_end_date:
                end_time_type = "actual"
        elif task.status == "delayed":
            # 延迟状态：开始时间优先使用实际时间，结束时间使用计划时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
        
        if start_date and end_date:
            gantt_task = GanttTask(
                id=f"task_{task.id}",
                name=task.name,
                description=task.description,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                progress=int(task.progress),
                assignee=task.assignee,
                custom_class=get_task_css_class(task.status),
                startTimeType=start_time_type,
                endTimeType=end_time_type
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
        project_description=project.description,
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


@router.get("/gantt/all", response_model=ResponseModel)
async def get_all_gantt_data(db: Session = Depends(get_db)):
    """获取所有项目的甘特图数据，按项目大类分组"""
    # 查询所有项目大类
    categories = db.query(ProjectCategory).all()
    category_map = {cat.id: cat for cat in categories}
    
    # 查询所有项目
    projects = db.query(Project).all()
    
    # 按项目大类分组
    category_projects = {}
    uncategorized_projects = []
    
    for project in projects:
        if project.category_id and project.category_id in category_map:
            category_id = project.category_id
            if category_id not in category_projects:
                category_projects[category_id] = []
            category_projects[category_id].append(project)
        else:
            uncategorized_projects.append(project)
    
    # 构建甘特图数据
    project_categories = []
    
    # 处理有大类的项目
    for category_id, cat_projects in category_projects.items():
        category = category_map[category_id]
        category_gantt = build_category_gantt(category, cat_projects, db)
        project_categories.append(category_gantt)
    
    # 处理未分类的项目
    if uncategorized_projects:
        # 创建一个"未分类"的大类
        uncategorized_category = ProjectCategoryGantt(
            id=0,
            name="未分类",
            projects=[]
        )
        
        for project in uncategorized_projects:
            project_gantt = build_project_gantt(project, db)
            uncategorized_category.projects.append(project_gantt)
        
        project_categories.append(uncategorized_category)
    
    # 构建完整的甘特图数据
    all_gantt_data = AllGanttData(
        project_categories=project_categories
    )
    
    return ResponseModel(data=all_gantt_data.dict())


def build_category_gantt(category: ProjectCategory, projects: list, db: Session) -> ProjectCategoryGantt:
    """构建项目大类的甘特图数据"""
    category_gantt = ProjectCategoryGantt(
        id=category.id,
        name=category.name,
        projects=[]
    )
    
    for project in projects:
        project_gantt = build_project_gantt(project, db)
        category_gantt.projects.append(project_gantt)
    
    return category_gantt


def build_project_gantt(project: Project, db: Session) -> ProjectGantt:
    """构建项目的甘特图数据"""
    # 查询项目的任务
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    
    # 转换为甘特图任务格式
    gantt_tasks = []
    for task in tasks:
        # 根据任务状态和时间字段优先级选择合适的时间字段
        start_date = None
        end_date = None
        start_time_type = "planned"
        end_time_type = "planned"
        
        if task.status == "pending":
            # 待处理状态：只使用计划时间
            start_date = task.planned_start_date
            end_date = task.planned_end_date
        elif task.status == "active":
            # 进行中状态：开始时间优先使用实际时间，结束时间使用计划时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
        elif task.status == "completed" or task.status == "cancelled":
            # 已完成或已取消状态：优先使用实际时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.actual_end_date or task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
            if task.actual_end_date:
                end_time_type = "actual"
        elif task.status == "delayed":
            # 延迟状态：开始时间优先使用实际时间，结束时间使用计划时间
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.planned_end_date
            if task.actual_start_date:
                start_time_type = "actual"
        
        if start_date and end_date:
            gantt_task = GanttTask(
                id=f"task_{task.id}",
                name=task.name,
                description=task.description,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                progress=int(task.progress),
                assignee=task.assignee or "",
                custom_class=get_task_css_class(task.status),
                startTimeType=start_time_type,
                endTimeType=end_time_type,
                project_id=project.id
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
    
    # 简单的阶段划分（可以根据实际需求扩展）
    phases = []
    if start_date and end_date:
        # 假设项目分为三个阶段：准备、执行、收尾
        total_days = (end_date - start_date).days
        if total_days > 0:
            phase1_end = start_date
            phase2_start = start_date
            phase2_end = end_date
            phase3_start = end_date
            
            if total_days >= 3:
                phase1_end = start_date
                phase2_start = start_date
                phase2_end = start_date
                phase3_start = start_date
                
                # 简单的三阶段划分
                phase1_end = start_date
                phase2_start = start_date
                phase2_end = end_date
                phase3_start = end_date
                
                # 计算阶段日期
                phase1_days = max(1, int(total_days * 0.3))
                phase2_days = max(1, int(total_days * 0.5))
                phase3_days = max(1, total_days - phase1_days - phase2_days)
                
                from datetime import timedelta
                phase1_end = start_date + timedelta(days=phase1_days)
                phase2_start = phase1_end
                phase2_end = phase2_start + timedelta(days=phase2_days)
                phase3_start = phase2_end
            
            phases = [
                ProjectPhase(
                    id="phase_1",
                    name="准备阶段",
                    start=start_date.strftime("%Y-%m-%d"),
                    end=phase1_end.strftime("%Y-%m-%d"),
                    description="项目启动和准备工作"
                ),
                ProjectPhase(
                    id="phase_2",
                    name="执行阶段",
                    start=phase2_start.strftime("%Y-%m-%d"),
                    end=phase2_end.strftime("%Y-%m-%d"),
                    description="项目主要实施工作"
                ),
                ProjectPhase(
                    id="phase_3",
                    name="收尾阶段",
                    start=phase3_start.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    description="项目验收和收尾工作"
                )
            ]
    
    project_gantt = ProjectGantt(
        id=project.id,
        name=project.name,
        description=project.description or "",
        start_date=start_date.strftime("%Y-%m-%d") if start_date else "",
        end_date=end_date.strftime("%Y-%m-%d") if end_date else "",
        progress=int(project.progress),
        tasks=gantt_tasks,
        phases=phases
    )
    
    return project_gantt
