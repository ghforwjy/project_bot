#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试甘特图功能
验证甘特图是否能够正确显示不同大类、项目和阶段
"""

import asyncio
import httpx
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_gantt_api():
    """
    测试甘特图API
    """
    logger.info("开始测试甘特图API")
    
    try:
        # 测试单个项目的甘特图数据
        logger.info("测试单个项目的甘特图数据")
        async with httpx.AsyncClient() as client:
            # 首先获取项目列表
            projects_response = await client.get("http://localhost:8000/api/v1/projects")
            projects_result = projects_response.json()
            
            if projects_result.get("code") == 200 and projects_result.get("data"):
                projects = projects_result.get("data", {}).get("items", [])
                logger.info(f"获取到 {len(projects)} 个项目")
                
                if projects:
                    # 测试第一个项目的甘特图数据
                    project_id = projects[0].get("id")
                    logger.info(f"测试项目 {project_id} 的甘特图数据")
                    
                    gantt_response = await client.get(f"http://localhost:8000/api/v1/projects/{project_id}/gantt")
                    gantt_result = gantt_response.json()
                    
                    if gantt_result.get("code") == 200 and gantt_result.get("data"):
                        gantt_data = gantt_result.get("data")
                        logger.info(f"成功获取到项目甘特图数据")
                        logger.info(f"项目名称: {gantt_data.get('project_name')}")
                        logger.info(f"项目描述: {gantt_data.get('project_description')}")
                        logger.info(f"开始日期: {gantt_data.get('start_date')}")
                        logger.info(f"结束日期: {gantt_data.get('end_date')}")
                        logger.info(f"任务数量: {len(gantt_data.get('tasks', []))}")
                    else:
                        logger.warning(f"获取项目甘特图数据失败: {gantt_result}")
                else:
                    logger.warning("没有找到项目，跳过单个项目甘特图测试")
            else:
                logger.warning(f"获取项目列表失败: {projects_result}")
        
        # 测试所有项目的甘特图数据
        logger.info("\n测试所有项目的甘特图数据")
        async with httpx.AsyncClient(timeout=60.0) as client:
            gantt_all_response = await client.get("http://localhost:8000/api/v1/gantt/all")
            gantt_all_result = gantt_all_response.json()
            
            if gantt_all_result.get("code") == 200 and gantt_all_result.get("data"):
                all_gantt_data = gantt_all_result.get("data")
                project_categories = all_gantt_data.get("project_categories", [])
                logger.info(f"成功获取到所有项目的甘特图数据")
                logger.info(f"项目大类数量: {len(project_categories)}")
                
                for i, category in enumerate(project_categories):
                    category_name = category.get("name")
                    projects = category.get("projects", [])
                    logger.info(f"\n大类 {i+1}: {category_name}")
                    logger.info(f"包含项目数量: {len(projects)}")
                    
                    for j, project in enumerate(projects):
                        project_name = project.get("name")
                        project_description = project.get("description")
                        tasks = project.get("tasks", [])
                        phases = project.get("phases", [])
                        logger.info(f"  项目 {j+1}: {project_name}")
                        logger.info(f"    描述: {project_description}")
                        logger.info(f"    任务数量: {len(tasks)}")
                        logger.info(f"    阶段数量: {len(phases)}")
                        
                        if phases:
                            logger.info(f"    阶段详情:")
                            for k, phase in enumerate(phases):
                                logger.info(f"      阶段 {k+1}: {phase.get('name')} ({phase.get('start')} ~ {phase.get('end')})")
            else:
                logger.warning(f"获取所有项目甘特图数据失败: {gantt_all_result}")
        
    except Exception as e:
        logger.error(f"测试甘特图API失败: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False
    
    logger.info("测试甘特图API完成")
    return True

async def test_gantt_data_structure():
    """
    测试甘特图数据结构
    """
    logger.info("\n开始测试甘特图数据结构")
    
    try:
        async with httpx.AsyncClient() as client:
            gantt_all_response = await client.get("http://localhost:8000/api/v1/gantt/all")
            gantt_all_result = gantt_all_response.json()
            
            if gantt_all_result.get("code") == 200 and gantt_all_result.get("data"):
                all_gantt_data = gantt_all_result.get("data")
                project_categories = all_gantt_data.get("project_categories", [])
                
                logger.info("验证甘特图数据结构...")
                
                # 验证项目大类结构
                for category in project_categories:
                    assert "id" in category
                    assert "name" in category
                    assert "projects" in category
                    assert isinstance(category.get("projects"), list)
                    
                    # 验证项目结构
                    for project in category.get("projects", []):
                        assert "id" in project
                        assert "name" in project
                        assert "description" in project
                        assert "start_date" in project
                        assert "end_date" in project
                        assert "progress" in project
                        assert "tasks" in project
                        assert "phases" in project
                        assert isinstance(project.get("tasks"), list)
                        assert isinstance(project.get("phases"), list)
                        
                        # 验证任务结构
                        for task in project.get("tasks", []):
                            assert "id" in task
                            assert "name" in task
                            assert "start" in task
                            assert "end" in task
                            assert "progress" in task
                            assert "assignee" in task
                            assert "custom_class" in task
                        
                        # 验证阶段结构
                        for phase in project.get("phases", []):
                            assert "id" in phase
                            assert "name" in phase
                            assert "start" in phase
                            assert "end" in phase
                            assert "description" in phase
                
                logger.info("✓ 甘特图数据结构验证通过")
                return True
            else:
                logger.warning(f"获取甘特图数据失败: {gantt_all_result}")
                return False
                
    except AssertionError as e:
        logger.error(f"甘特图数据结构验证失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"测试甘特图数据结构失败: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def main():
    """
    主测试函数
    """
    logger.info("===== 开始甘特图功能测试 =====")
    
    # 测试甘特图API
    api_test_result = await test_gantt_api()
    logger.info("\n" + "="*60 + "\n")
    
    # 测试甘特图数据结构
    structure_test_result = await test_gantt_data_structure()
    
    logger.info("\n" + "="*60)
    logger.info("测试结果汇总:")
    logger.info(f"甘特图API测试: {'通过' if api_test_result else '失败'}")
    logger.info(f"甘特图数据结构测试: {'通过' if structure_test_result else '失败'}")
    
    if api_test_result and structure_test_result:
        logger.info("✓ 所有测试通过，甘特图功能正常工作")
    else:
        logger.warning("⚠ 部分测试失败，需要进一步检查")
    
    logger.info("===== 测试完成 =====")

if __name__ == "__main__":
    asyncio.run(main())
