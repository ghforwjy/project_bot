"""
测试甘特图tooltip功能 - 验证description字段是否正确显示
"""
import requests
import json
from typing import Dict, Any, List

class GanttTooltipTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")

    def test_description_field_exists(self) -> bool:
        """测试API返回的任务数据是否包含description字段"""
        try:
            print("\n=== 测试description字段存在性 ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("description字段存在性", False, 
                               f"API请求失败: {response.status_code}")
                return False
            
            data = response.json()
            categories = data.get("data", {}).get("project_categories", [])
            
            all_have_description = True
            task_count = 0
            
            for category in categories:
                for project in category.get("projects", []):
                    for task in project.get("tasks", []):
                        task_count += 1
                        
                        if 'description' not in task:
                            self.log_result("description字段存在性", False, 
                                           f"任务 '{task.get('name', '未命名')}' 缺少description字段")
                            all_have_description = False
            
            if task_count == 0:
                self.log_result("description字段存在性", False, "没有找到任何任务")
                return False
            
            if all_have_description:
                self.log_result("description字段存在性", True, 
                               f"所有 {task_count} 个任务都包含description字段")
            else:
                self.log_result("description字段存在性", False, 
                               "部分任务缺少description字段")
            
            return all_have_description
            
        except Exception as e:
            self.log_result("description字段存在性", False, f"测试失败: {e}")
            return False

    def test_description_content(self) -> bool:
        """测试description字段的内容"""
        try:
            print("\n=== 测试description字段内容 ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("description字段内容", False, "API请求失败")
                return False
            
            data = response.json()
            categories = data.get("data", {}).get("project_categories", [])
            
            tasks_with_description = 0
            total_tasks = 0
            
            for category in categories:
                for project in category.get("projects", []):
                    for task in project.get("tasks", []):
                        total_tasks += 1
                        description = task.get('description', '')
                        
                        if description:
                            tasks_with_description += 1
                            print(f"\n任务: {task['name']}")
                            print(f"  描述: {description[:100]}{'...' if len(description) > 100 else ''}")
            
            if total_tasks == 0:
                self.log_result("description字段内容", False, "没有找到任何任务")
                return False
            
            if tasks_with_description > 0:
                self.log_result("description字段内容", True, 
                               f"{tasks_with_description}/{total_tasks} 个任务有描述内容")
            else:
                self.log_result("description字段内容", False, 
                               "所有任务都没有描述内容")
            
            return tasks_with_description > 0
            
        except Exception as e:
            self.log_result("description字段内容", False, f"测试失败: {e}")
            return False

    def test_frontend_uses_description(self) -> bool:
        """测试前端是否使用description字段"""
        try:
            print("\n=== 测试前端使用description字段 ===")
            
            import os
            component_path = "e:\\mycode\\project_bot\\frontend\\src\\components\\gantt\\GanttChart.tsx"
            
            if not os.path.exists(component_path):
                self.log_result("前端使用description字段", False, 
                               f"GanttChart组件文件不存在: {component_path}")
                return False
            
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否使用task.description
            if 'task.description' not in content:
                self.log_result("前端使用description字段", False, 
                               "组件中未使用task.description字段")
                return False
            
            # 检查showTooltip函数
            if 'showTooltip' not in content:
                self.log_result("前端使用description字段", False, 
                               "组件中缺少showTooltip函数")
                return False
            
            self.log_result("前端使用description字段", True, 
                           "GanttChart组件正确使用task.description字段")
            
            return True
            
        except Exception as e:
            self.log_result("前端使用description字段", False, f"测试失败: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("甘特图Tooltip Description功能测试")
        print("=" * 60)
        
        tests = [
            ("description字段存在性测试", self.test_description_field_exists),
            ("description字段内容测试", self.test_description_content),
            ("前端使用description字段测试", self.test_frontend_uses_description),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"测试异常: {e}")
        
        # 打印测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过! 甘特图tooltip description功能正常")
        else:
            print("\n⚠️  部分测试失败,请检查上述错误信息")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed/total*100,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = GanttTooltipTester()
    results = tester.run_all_tests()
    
    # 保存测试结果到文件
    with open("e:\\mycode\\project_bot\\tests\\gantt_description_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: e:\\mycode\\project_bot\\tests\\gantt_description_test_results.json")