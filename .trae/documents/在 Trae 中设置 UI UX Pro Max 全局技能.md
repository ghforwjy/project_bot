# 在 Trae 中设置 UI UX Pro Max 全局技能

## 任务目标
将 UI UX Pro Max skill 添加到 Trae 的全局技能中，使其在所有项目中都能使用。

## 实施步骤

### 1. 了解 UI UX Pro Max skill 的结构
- 访问 GitHub 仓库 https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- 分析 skill 的文件结构和内容，特别是 SKILL.md 文件
- 了解 skill 的触发条件、执行步骤和输出结果

### 2. 准备 skill 文件
- 在 E:\mycode\ 目录下创建 skills 目录
- 在 E:\mycode\skills\ 目录下创建 ui-ux-pro-max 目录
- 克隆 UI UX Pro Max skill 仓库到 E:\mycode\skills\ui-ux-pro-max 目录
- 确保文件结构符合 Trae 的技能要求
- 重点关注 SKILL.md 文件，确保其包含必要的元数据、触发条件、执行步骤和输出定义

### 3. 在 Trae 中创建全局技能
- 打开 Trae IDE
- 导航到：设置 —> 规则和技能 —> 技能模块
- 点击「创建」按钮
- 选择「全局技能」类型
- 导入 E:\mycode\skills\ui-ux-pro-max 目录中的技能文件
- 配置技能的基本信息，如名称、描述等

### 4. 验证技能设置
- 确认技能已成功添加到全局技能列表中
- 测试技能是否能被正确触发
- 验证技能的执行效果是否符合预期

### 5. 优化和调整
- 根据测试结果，调整技能的触发条件和执行步骤
- 确保技能在不同场景下都能稳定运行
- 优化技能的性能和可用性

## 预期结果
- UI UX Pro Max skill 成功添加到 Trae 的全局技能中
- 技能可以在所有项目中被自动或手动触发
- 技能能够按照预期提供设计智能，帮助构建专业的 UI/UX

## 注意事项
- 确保技能文件结构符合 Trae 的要求
- 重点关注技能的元数据和触发条件，确保其能被正确识别和触发
- 测试技能在不同场景下的表现，确保其稳定性和可靠性
- 遵循 Trae 的技能开发最佳实践，确保技能的可维护性和可扩展性