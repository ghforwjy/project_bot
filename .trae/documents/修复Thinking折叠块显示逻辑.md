## 修复Thinking折叠块只在分析请求时显示

### 问题
当前Thinking折叠块在所有请求中都显示，但只有项目分析才需要这个信息收集过程。

### 修复步骤

#### 步骤1：修改handleSend函数
- 普通请求不再设置thinkingSteps
- 只有分析请求才设置thinkingSteps

#### 步骤2：修改Thinking折叠块显示逻辑
- Thinking折叠块只在thinkingSteps存在且不为空时显示
- 普通请求只显示"AI思考中..."的加载提示