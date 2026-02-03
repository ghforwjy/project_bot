"""数据获取模块"""
from typing import Dict, Any, List
import httpx

class ProjectDataFetcher:
    """项目数据获取器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化数据获取器"""
        self.base_url = base_url
        self.api_prefix = f"{base_url}/api/v1"
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """获取所有项目数据"""
        url = f"{self.api_prefix}/projects"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("items", [])
    
    async def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目的任务数据"""
        url = f"{self.api_prefix}/projects/{project_id}/tasks"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("items", [])
    
    async def get_all_data(self) -> Dict[str, Any]:
        """获取所有项目和任务数据"""
        # 获取项目列表
        projects = await self.get_all_projects()
        
        # 为每个项目获取任务数据
        for project in projects:
            project_id = project.get("id")
            if project_id:
                try:
                    tasks = await self.get_project_tasks(project_id)
                    project["tasks"] = tasks
                except Exception as e:
                    print(f"Error fetching tasks for project {project_id}: {e}")
                    project["tasks"] = []
        
        return {"projects": projects}
    
    async def get_project_data(self, project_id: int) -> Dict[str, Any]:
        """获取单个项目的详细数据"""
        # 获取项目列表
        projects = await self.get_all_projects()
        
        # 找到指定项目
        project = next((p for p in projects if p.get("id") == project_id), None)
        
        if not project:
            return {"error": "Project not found"}
        
        # 获取项目任务
        try:
            tasks = await self.get_project_tasks(project_id)
            project["tasks"] = tasks
        except Exception as e:
            print(f"Error fetching tasks for project {project_id}: {e}")
            project["tasks"] = []
        
        return {"project": project}
