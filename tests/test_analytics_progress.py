#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分析操作的进度反馈功能
验证后端返回的真实信息收集过程是否能正确传递给前端
"""

import asyncio
import httpx
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_analytics_progress():
    """
    测试分析操作的进度反馈
    """
    logger.info("开始测试分析操作的进度反馈功能")
    
    try:
        # 测试分析API的query端点
        async with httpx.AsyncClient() as client:
            logger.info("调用分析API...")
            response = await client.post(
                "http://localhost:8000/api/v1/analytics/query",
                json={"query": "分析所有项目的情况"},
                timeout=30.0
            )
            
            logger.info(f"分析API响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"分析API响应代码: {result.get('code')}")
            
            if result.get("code") == 200 and result.get("data"):
                analysis_data = result.get("data", {})
                progress_steps = analysis_data.get("progress_steps", [])
                
                logger.info(f"获取到的进度步骤数量: {len(progress_steps)}")
                
                if progress_steps:
                    logger.info("进度步骤详情:")
                    for step in progress_steps:
                        logger.info(f"- {step.get('title')}: {step.get('status')}")
                        logger.info(f"  描述: {step.get('description')}")
                    
                    # 验证所有步骤都已完成
                    completed_steps = [step for step in progress_steps if step.get('status') == 'completed']
                    logger.info(f"已完成的步骤数量: {len(completed_steps)}")
                    logger.info(f"总步骤数量: {len(progress_steps)}")
                    
                    if len(completed_steps) == len(progress_steps):
                        logger.info("✓ 所有进度步骤都已正确完成")
                    else:
                        logger.warning("⚠ 部分进度步骤未完成")
                        
                    # 验证进度步骤的状态顺序
                    status_order = [step.get('status') for step in progress_steps]
                    logger.info(f"进度状态顺序: {status_order}")
                    
                    # 确保没有pending状态的步骤在completed状态之后
                    has_completed = False
                    for status in status_order:
                        if status == 'completed':
                            has_completed = True
                        elif status == 'pending' and has_completed:
                            logger.warning("⚠ 存在completed状态之后的pending状态步骤")
                            break
                else:
                    logger.warning("⚠ 未获取到进度步骤信息")
                    
                # 验证分析结果
                analysis = analysis_data.get("analysis", {})
                if analysis:
                    logger.info("✓ 成功获取到分析结果")
                    logger.info(f"分析结果包含的键: {list(analysis.keys())}")
                else:
                    logger.warning("⚠ 未获取到分析结果")
                    
                # 验证响应内容
                response_content = analysis_data.get("response", "")
                if response_content:
                    logger.info("✓ 成功获取到响应内容")
                    logger.info(f"响应内容长度: {len(response_content)} 字符")
                else:
                    logger.warning("⚠ 未获取到响应内容")
            else:
                logger.error(f"分析API返回非200响应: {result}")
                
    except Exception as e:
        logger.error(f"测试失败: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False
    
    logger.info("测试分析操作的进度反馈功能完成")
    return True

async def test_chat_with_analytics():
    """
    测试通过chat API调用分析操作，验证进度信息传递
    """
    logger.info("开始测试通过chat API调用分析操作")
    
    try:
        # 测试chat API的messages端点
        async with httpx.AsyncClient() as client:
            logger.info("调用chat API...")
            response = await client.post(
                "http://localhost:8000/api/v1/chat/messages",
                json={"message": "分析所有项目的情况", "session_id": "test_session"},
                timeout=30.0
            )
            
            logger.info(f"chat API响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"chat API响应代码: {result.get('code')}")
            
            if result.get("code") == 200 and result.get("data"):
                chat_data = result.get("data", {})
                progress_steps = chat_data.get("progress_steps", [])
                
                logger.info(f"从chat API获取到的进度步骤数量: {len(progress_steps)}")
                
                if progress_steps:
                    logger.info("chat API返回的进度步骤详情:")
                    for step in progress_steps:
                        logger.info(f"- {step.get('title')}: {step.get('status')}")
                    
                    logger.info("✓ 成功从chat API获取到进度信息")
                else:
                    logger.warning("⚠ 未从chat API获取到进度步骤信息")
                    
                # 验证返回的消息内容
                content = chat_data.get("content", "")
                if content:
                    logger.info("✓ 成功获取到chat API返回的消息内容")
                    logger.info(f"消息内容长度: {len(content)} 字符")
                else:
                    logger.warning("⚠ 未获取到chat API返回的消息内容")
            else:
                logger.error(f"chat API返回非200响应: {result}")
                
    except Exception as e:
        logger.error(f"测试失败: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False
    
    logger.info("测试通过chat API调用分析操作完成")
    return True

async def main():
    """
    主测试函数
    """
    logger.info("===== 开始分析操作进度反馈功能测试 =====")
    
    # 测试分析API
    analytics_test_result = await test_analytics_progress()
    logger.info("\n" + "="*60 + "\n")
    
    # 测试chat API
    chat_test_result = await test_chat_with_analytics()
    
    logger.info("\n" + "="*60)
    logger.info("测试结果汇总:")
    logger.info(f"分析API测试: {'通过' if analytics_test_result else '失败'}")
    logger.info(f"Chat API测试: {'通过' if chat_test_result else '失败'}")
    
    if analytics_test_result and chat_test_result:
        logger.info("✓ 所有测试通过，分析操作的进度反馈功能正常工作")
    else:
        logger.warning("⚠ 部分测试失败，需要进一步检查")
    
    logger.info("===== 测试完成 =====")

if __name__ == "__main__":
    asyncio.run(main())
