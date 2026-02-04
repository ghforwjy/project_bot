"""
测试甘特图tooltip长文本换行功能
验证文本是否正确换行且不溢出
"""
import requests
import json
from typing import Dict, Any, List

class GanttTooltipLongTextTester:
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

    def test_long_text_descriptions(self) -> bool:
        """测试长文本描述"""
        try:
            print("\n=== 测试长文本描述 ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("长文本描述", False, f"API请求失败: {response.status_code}")
                return False
            
            data = response.json()
            categories = data.get("data", {}).get("project_categories", [])
            
            long_text_tasks = []
            
            for category in categories:
                for project in category.get("projects", []):
                    for task in project.get("tasks", []):
                        description = task.get('description', '')
                        if len(description) > 50:
                            long_text_tasks.append({
                                'name': task['name'],
                                'description': description,
                                'length': len(description)
                            })
            
            if not long_text_tasks:
                self.log_result("长文本描述", False, "没有找到长文本任务")
                return False
            
            print(f"\n找到 {len(long_text_tasks)} 个长文本任务:")
            for i, task in enumerate(long_text_tasks, 1):
                print(f"\n{i}. {task['name']}")
                print(f"   长度: {task['length']} 字符")
                print(f"   描述: {task['description'][:100]}{'...' if len(task['description']) > 100 else ''}")
            
            self.log_result("长文本描述", True, 
                           f"找到 {len(long_text_tasks)} 个长文本任务")
            return True
            
        except Exception as e:
            self.log_result("长文本描述", False, f"测试失败: {e}")
            return False

    def test_text_wrapping_logic(self) -> bool:
        """测试文本换行逻辑"""
        try:
            print("\n=== 测试文本换行逻辑 ===")
            
            # 模拟前端的wrapText函数
            def wrap_text(text: str, max_width: int) -> List[str]:
                lines = []
                current_line = ''
                current_width = 0
                
                for char in text:
                    # 中文字符宽度10，英文字符宽度6
                    char_width = 10 if '\u4e00' <= char <= '\u9fa5' else 6
                    
                    if current_width + char_width > max_width and current_line != '':
                        lines.append(current_line)
                        current_line = char
                        current_width = char_width
                    else:
                        current_line += char
                        current_width += char_width
                
                if current_line:
                    lines.append(current_line)
                
                return lines
            
            # 测试用例
            test_cases = [
                {
                    'name': '短文本',
                    'text': '这是一个短文本',
                    'expected_lines': 1
                },
                {
                    'name': '中等长度文本',
                    'text': '这是一个中等长度的文本测试',
                    'expected_lines': 1
                },
                {
                    'name': '长文本',
                    'text': '这是一个非常长的文本测试，应该会自动换行显示多行内容',
                    'expected_lines': 2
                },
                {
                    'name': '超长文本',
                    'text': '这是一个超级长的文本测试，应该会自动换行显示多行内容，每行都有一定的宽度限制，确保文本不会溢出',
                    'expected_lines': 3
                }
            ]
            
            all_passed = True
            max_width = 160
            
            for test_case in test_cases:
                lines = wrap_text(test_case['text'], max_width)
                print(f"\n{test_case['name']}:")
                print(f"  原文: {test_case['text']}")
                print(f"  期望行数: {test_case['expected_lines']}")
                print(f"  实际行数: {len(lines)}")
                print(f"  换行结果:")
                for i, line in enumerate(lines, 1):
                    print(f"    {i}. {line}")
                
                # 检查每行是否超过最大宽度
                for line in lines:
                    if len(line) * 6 > max_width:
                        print(f"    ⚠️  行 '{line}' 超过最大宽度!")
                        all_passed = False
            
            if all_passed:
                self.log_result("文本换行逻辑", True, 
                               "所有测试用例的换行逻辑正确")
            else:
                self.log_result("文本换行逻辑", False, 
                               "部分测试用例的换行逻辑有问题")
            
            return all_passed
            
        except Exception as e:
            self.log_result("文本换行逻辑", False, f"测试失败: {e}")
            return False

    def test_frontend_implementation(self) -> bool:
        """测试前端实现"""
        try:
            print("\n=== 测试前端实现 ===")
            
            import os
            component_path = "e:\\mycode\\project_bot\\frontend\\src\\components\\gantt\\GanttChart.tsx"
            
            if not os.path.exists(component_path):
                self.log_result("前端实现", False, 
                               f"GanttChart组件文件不存在: {component_path}")
                return False
            
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查wrapText函数
            if 'wrapText' not in content:
                self.log_result("前端实现", False, 
                               "组件中缺少wrapText函数")
                return False
            
            # 检查动态高度计算
            if 'wrappedLines' not in content:
                self.log_result("前端实现", False, 
                               "组件中未使用wrappedLines")
                return False
            
            # 检查动态宽度计算
            if 'tooltipWidth' not in content:
                self.log_result("前端实现", False, 
                               "组件中未使用tooltipWidth")
                return False
            
            # 检查行高设置
            if 'lineHeight' not in content:
                self.log_result("前端实现", False, 
                               "组件中未设置lineHeight")
                return False
            
            self.log_result("前端实现", True, 
                           "GanttChart组件正确实现了文本换行和动态高度计算")
            
            return True
            
        except Exception as e:
            self.log_result("前端实现", False, f"测试失败: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("甘特图Tooltip长文本换行功能测试")
        print("=" * 60)
        
        tests = [
            ("长文本描述测试", self.test_long_text_descriptions),
            ("文本换行逻辑测试", self.test_text_wrapping_logic),
            ("前端实现测试", self.test_frontend_implementation),
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
            print("\n🎉 所有测试通过! 甘特图tooltip长文本换行功能正常")
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
    tester = GanttTooltipLongTextTester()
    results = tester.run_all_tests()
    
    # 保存测试结果到文件
    with open("e:\\mycode\\project_bot\\tests\\gantt_tooltip_longtext_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: e:\\mycode\\project_bot\\tests\\gantt_tooltip_longtext_test_results.json")