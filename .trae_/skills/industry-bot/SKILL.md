---
name: "industry-bot"
description: "搜索指定产业的上下游产业链及对应上市公司，生成JSON格式调研报告。Invoke when user asks for industry chain research, upstream/downstream analysis, or listed companies in a specific industry."
---

# Industry Bot - 产业链调研助手

## 功能说明

本 skill 用于帮助用户调研指定产业的上下游产业链结构，以及各环节对应的上市公司信息，最终生成结构化的 JSON 格式调研结果。

## 使用场景

当用户需要以下信息时调用本 skill：
- 某个产业的上下游产业链分析
- 特定行业的上市公司梳理
- 产业链结构调研报告
- 行业竞争格局分析

## 工作流程

### 1. 信息收集

使用 WebSearch 工具搜索以下信息：
- `{产业名称} 产业链 上游 下游`
- `{产业名称} 上市公司 龙头`
- `{产业名称} 行业分析 竞争格局`

### 2. 数据整理

根据搜索结果，整理产业链结构：
- **上游**：原材料、零部件、技术提供方
- **中游**：生产制造、加工组装
- **下游**：销售渠道、终端应用、客户群体

### 3. 上市公司信息

为每个产业链环节列出相关上市公司：
- 公司名称
- 股票代码
- 主营业务
- 市场地位（龙头/重要参与者/其他）

### 4. 输出格式

生成标准 JSON 格式：

```json
{
  "industry_name": "产业名称",
  "research_date": "YYYY-MM-DD",
  "chain_structure": {
    "upstream": {
      "description": "上游环节描述",
      "companies": [
        {
          "name": "公司名称",
          "stock_code": "股票代码",
          "business": "主营业务",
          "position": "市场地位"
        }
      ]
    },
    "midstream": {
      "description": "中游环节描述",
      "companies": [...]
    },
    "downstream": {
      "description": "下游环节描述",
      "companies": [...]
    }
  },
  "summary": "产业整体分析总结"
}
```

## 示例

用户输入："帮我调研新能源汽车产业链"

执行步骤：
1. 搜索"新能源汽车产业链 上游 下游"
2. 搜索"新能源汽车 上市公司 龙头"
3. 搜索"锂电池 电机 电控 上市公司"
4. 整理数据并生成 JSON 报告

## 注意事项

1. 搜索时使用中文关键词获取更准确的国内产业信息
2. 上市公司信息以 A 股为主，可包含港股、美股中概股
3. 数据需标注来源和调研日期
4. 如搜索结果不完整，需提示用户可能存在的遗漏
5. 对于敏感或实时变动较大的信息（如股价），建议用户二次核实
