#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试甘特图是否正确返回项目负责人
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_gantt_assignee():
    """测试甘特图数据是否包含项目负责人"""
    print("=" * 60)
    print("测试：甘特图数据中的项目负责人")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/gantt/all", timeout=10)
        if response.status_code != 200:
            print(f"错误：获取甘特图数据失败，状态码 {response.status_code}")
            return False
        
        result = response.json()
        gantt_data = result.get("data", {})
        categories = gantt_data.get("project_categories", [])
        
        print("\n项目列表及负责人：")
        print("-" * 60)
        
        for category in categories:
            category_name = category.get("name")
            print(f"\n📁 大类: {category_name}")
            
            for project in category.get("projects", []):
                project_name = project.get("name")
                assignee = project.get("assignee")
                
                if assignee:
                    print(f"  📂 {project_name} - 负责人: {assignee}")
                else:
                    print(f"  📂 {project_name} - 负责人: 未设置")
        
        print("\n" + "=" * 60)
        print("✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"错误：请求失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_gantt_assignee()
