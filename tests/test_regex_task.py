import re

content = "我将更新'投资交易优化'项目中的'下午1点左右，偶发卡顿'任务，将其计划开始时间设置为2026年03月05日"

# 当前的正则
pattern1 = r"['\"]([^'\"]+)['\"]项目.*?['\"]([^'\"]+)['\"]任务"
match1 = re.search(pattern1, content)
print(f"正则1: {pattern1}")
print(f"匹配结果: {match1}")
if match1:
    print(f"groups: {match1.groups()}")

# 修正的正则：项目名后面可能没有引号
pattern2 = r"['\"]([^'\"]+)['\"]项目.*?['\"]([^'\"]+)['\"]"
match2 = re.search(pattern2, content)
print(f"\n正则2: {pattern2}")
print(f"匹配结果: {match2}")
if match2:
    print(f"groups: {match2.groups()}")

# 更宽松的正则
pattern3 = r"['\"]([^'\"]+)['\"].*?项目.*?['\"]([^'\"]+)['\"]"
match3 = re.search(pattern3, content)
print(f"\n正则3: {pattern3}")
print(f"匹配结果: {match3}")
if match3:
    print(f"groups: {match3.groups()}")
