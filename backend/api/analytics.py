"""分析相关API路由"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from models.database import get_db
from services.analytics.core import ProjectAnalyzer
from services.analytics.data_fetcher import ProjectDataFetcher
from services.analytics.llm_integration import LLMIntegration
from models.schemas import ResponseModel

router = APIRouter()

# 初始化分析服务
analyzer = ProjectAnalyzer()
data_fetcher = ProjectDataFetcher()
llm_integration = LLMIntegration()


@router.get("/analytics/projects", response_model=ResponseModel)
async def get_projects_analytics():
    """获取项目分析数据"""
    try:
        # 获取项目数据
        data = await data_fetcher.get_all_data()
        projects = data.get("projects", [])
        
        # 分析项目数据
        analysis = analyzer.analyze(projects)
        
        return ResponseModel(data=analysis)
    except Exception as e:
        print(f"Error in get_projects_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/projects/{project_id}", response_model=ResponseModel)
async def get_single_project_analytics(project_id: int):
    """获取单个项目的分析数据"""
    try:
        # 获取项目数据
        data = await data_fetcher.get_project_data(project_id)
        project = data.get("project")
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # 分析单个项目
        analysis = analyzer.analyze_single_project(project)
        
        return ResponseModel(data=analysis)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_single_project_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/query", response_model=ResponseModel)
async def handle_analytics_query(query_data: Dict[str, Any]):
    """处理分析查询"""
    try:
        user_query = query_data.get("query", "")
        context = query_data.get("context", "")
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # 定义信息收集步骤
        progress_steps = [
            {"id": "analysis_step_1", "title": "理解分析需求", "description": "分析用户输入的消息，识别具体的分析需求", "status": "in_progress"},
            {"id": "analysis_step_2", "title": "获取项目列表", "description": "从数据库中获取所有项目的基本信息", "status": "pending"},
            {"id": "analysis_step_3", "title": "收集任务数据", "description": "为每个项目获取详细的任务数据", "status": "pending"},
            {"id": "analysis_step_4", "title": "执行数据分析", "description": "计算项目概览、任务情况和识别关键项目", "status": "pending"},
            {"id": "analysis_step_5", "title": "生成分析报告", "description": "基于分析结果生成详细的项目分析报告", "status": "pending"},
            {"id": "analysis_step_6", "title": "整合分析结果", "description": "将分析报告整合到最终回复中", "status": "pending"}
        ]
        
        # 步骤1: 理解分析需求
        import time
        time.sleep(0.5)  # 模拟处理时间
        progress_steps[0]["status"] = "completed"
        progress_steps[1]["status"] = "in_progress"
        
        # 步骤2: 获取项目数据
        data = await data_fetcher.get_all_data()
        projects = data.get("projects", [])
        time.sleep(0.5)  # 模拟处理时间
        progress_steps[1]["status"] = "completed"
        progress_steps[2]["status"] = "in_progress"
        
        # 步骤3: 收集任务数据
        # 任务数据已经在get_all_data中收集
        time.sleep(0.5)  # 模拟处理时间
        progress_steps[2]["status"] = "completed"
        progress_steps[3]["status"] = "in_progress"
        
        # 步骤4: 分析项目数据
        analysis = analyzer.analyze(projects)
        time.sleep(0.5)  # 模拟处理时间
        progress_steps[3]["status"] = "completed"
        progress_steps[4]["status"] = "in_progress"
        
        # 步骤5: 生成回答
        if context:
            # 后续问题
            response = llm_integration.generate_follow_up_response(analysis, user_query, context)
        else:
            # 首次查询
            response = llm_integration.generate_response(analysis, user_query)
        time.sleep(0.5)  # 模拟处理时间
        progress_steps[4]["status"] = "completed"
        progress_steps[5]["status"] = "in_progress"
        
        # 步骤6: 整合分析结果
        time.sleep(0.3)  # 模拟处理时间
        progress_steps[5]["status"] = "completed"
        
        # 返回分析结果
        return ResponseModel(
            data={
                "response": response,
                "analysis": analysis,
                "progress_steps": progress_steps
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in handle_analytics_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/health", response_model=ResponseModel)
async def analytics_health_check():
    """分析服务健康检查"""
    try:
        # 测试数据获取
        data = await data_fetcher.get_all_data()
        
        return ResponseModel(
            data={
                "status": "healthy",
                "project_count": len(data.get("projects", []))
            }
        )
    except Exception as e:
        print(f"Error in analytics_health_check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
