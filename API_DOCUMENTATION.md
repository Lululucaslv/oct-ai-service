# 大侠找光 AI 工具集 API 文档

## 项目概述

"大侠找光"AI智能体系统是一个基于LangChain和FastAPI构建的模块化AI应用，专门为光伏行业提供智能查询服务。系统包含四个核心工具和一个主路由智能体，能够智能地理解用户查询并调用相应工具提供准确信息。

## 系统架构

### 核心组件
1. **电价查询工具** (`electricity_price_tool.py`) - 查询上网电价、脱硫煤电价、工商业电价
2. **有效发电小时数查询工具** (`power_generation_duration_tool.py`) - 查询指定城市的有效发电小时数
3. **光伏承载力查询工具** (`photovoltaic_capacity_tool.py`) - 查询光伏承载力和可开放容量
4. **政策查询工具** (`policy_query_tool.py`) - 多条件政策搜索
5. **主路由智能体** (`main_router_agent.py`) - 智能路由和多工具协同

### 技术栈
- **后端框架**: FastAPI
- **AI框架**: LangChain
- **语言模型**: OpenAI GPT-3.5-turbo (可选，支持Mock模式)
- **HTTP客户端**: requests
- **环境管理**: python-dotenv

## API 端点

### 1. 健康检查
```
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "services": [
    "electricity_price_tool",
    "power_generation_duration_tool", 
    "photovoltaic_capacity_tool",
    "policy_query_tool",
    "main_router_agent"
  ]
}
```

### 2. 统一智能查询入口 (推荐使用)
```
POST /ask_agent
```

**请求体:**
```json
{
  "query": "用户的自然语言查询"
}
```

**响应体:**
```json
{
  "result": "智能体的回答结果",
  "success": true
}
```

### 3. 独立工具端点

#### 电价查询
```
POST /query_electricity_price
```

#### 发电小时数查询
```
POST /query_power_generation_duration
```

#### 光伏承载力查询
```
POST /query_photovoltaic_capacity
```

#### 政策查询
```
POST /query_policies
```

所有独立工具端点使用相同的请求/响应格式。

## 验收测试用例

### 测试用例1: 单一工具调用
**请求:**
```bash
curl -X POST "http://your-server:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "安徽淮南的工商电价是多少？"}'
```

**预期行为:** 智能体识别电价查询意图，调用电价工具，返回安徽省-淮南市的工商加权电价。

### 测试用例2: 复杂工具调用
**请求:**
```bash
curl -X POST "http://your-server:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "查找全国范围内关于户用屋顶光伏的并网接入政策"}'
```

**预期行为:** 智能体识别政策查询意图，解析多个参数(全国范围、户用屋顶、并网接入)，返回相关政策信息。

### 测试用例3: 多工具组合调用
**请求:**
```bash
curl -X POST "http://your-server:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "我想了解一下河南开封的光伏承载力，顺便再看看那边有什么相关的补贴政策。"}'
```

**预期行为:** 智能体识别双重意图，依次调用光伏承载力工具和政策工具，整合两个工具的响应。

## 错误处理

系统具备完善的错误处理机制：
- API请求失败时返回详细错误信息
- 参数解析失败时提供友好提示
- 网络异常时进行适当重试和降级处理

## 性能特性

- **响应时间**: 单次查询通常在2-5秒内完成
- **并发支持**: FastAPI异步处理，支持多并发请求
- **容错能力**: Mock模式确保在外部API不可用时仍能提供服务
- **扩展性**: 模块化设计，易于添加新工具和功能

## 安全考虑

- 所有外部API调用使用HTTPS
- 敏感信息通过环境变量管理
- 输入验证和参数清理
- 错误信息不暴露内部实现细节
