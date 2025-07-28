# 大侠找光 AI 工具集

一个基于LangChain和FastAPI构建的智能光伏行业查询系统，为光伏从业者提供专业、准确的数据查询和政策咨询服务。

## 🌟 项目特色

- **🧠 智能路由**: 基于自然语言理解的智能查询路由系统
- **🔧 模块化设计**: 四个独立AI工具，可单独使用或协同工作
- **⚡ 高性能**: FastAPI异步服务，支持高并发查询
- **🎯 专业领域**: 专注光伏行业，提供精准的行业数据和政策信息
- **🔄 容错设计**: Mock模式支持，确保系统稳定性

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
创建 `.env` 文件：
```bash
BASE_URL=https://test.daxiazhaoguang.com/server/
DAXIA_API_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here  # 可选
```

### 启动服务
```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 测试查询
```bash
curl -X POST "http://localhost:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "北京市的有效发电小时数是多少？"}'
```

## 🛠️ 核心功能

### 1. 电价查询工具
- 支持上网电价、脱硫煤电价、工商业电价查询
- 智能城市名称解析和格式化
- 覆盖全国主要城市和地区

### 2. 有效发电小时数查询工具
- 基于地理位置的发电效率数据
- 支持多种城市格式输入
- 提供历史数据和趋势分析

### 3. 光伏承载力查询工具
- 多级地理位置解析（省市区县）
- 承载力状态和可开放容量查询
- 详细的台变数据和汇总信息

### 4. 政策查询工具
- 多条件政策搜索引擎
- 支持地区、主题、电站模式等复杂筛选
- 政策内容摘要和分类整理

### 5. 主路由智能体
- 自然语言意图识别
- 智能工具选择和路由
- 多工具协同调用和结果整合

## 📊 API 端点

### 统一查询入口 (推荐)
```
POST /ask_agent
```
智能路由到合适的工具，支持复杂查询和多工具协同。

### 独立工具端点
- `POST /query_electricity_price` - 电价查询
- `POST /query_power_generation_duration` - 发电小时数查询
- `POST /query_photovoltaic_capacity` - 光伏承载力查询
- `POST /query_policies` - 政策查询

### 系统端点
- `GET /health` - 健康检查
- `GET /docs` - API文档 (Swagger UI)

## 🧪 测试用例

### 单一工具调用
```bash
curl -X POST "http://localhost:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "安徽淮南的工商电价是多少？"}'
```

### 复杂查询
```bash
curl -X POST "http://localhost:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "查找全国范围内关于户用屋顶光伏的并网接入政策"}'
```

### 多工具协同
```bash
curl -X POST "http://localhost:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "我想了解一下河南开封的光伏承载力，顺便再看看那边有什么相关的补贴政策。"}'
```

## 🏗️ 系统架构

```
用户查询 → FastAPI服务 → 主路由智能体 → 工具选择 → 具体工具执行 → 结果整合 → 用户响应
```

### 技术栈
- **AI框架**: LangChain
- **服务框架**: FastAPI
- **语言模型**: OpenAI GPT-3.5-turbo
- **HTTP客户端**: requests
- **数据验证**: Pydantic

## 📁 项目结构

```
daxiazhaoguang-ai/
├── main.py                           # FastAPI主服务
├── main_router_agent.py              # 主路由智能体
├── electricity_price_tool.py         # 电价查询工具
├── power_generation_duration_tool.py # 发电小时数查询工具
├── photovoltaic_capacity_tool.py     # 光伏承载力查询工具
├── policy_query_tool.py              # 政策查询工具
├── requirements.txt                  # 依赖包清单
├── .env                             # 环境变量配置
├── README.md                        # 项目说明
├── API_DOCUMENTATION.md             # API文档
├── DEPLOYMENT_GUIDE.md              # 部署指南
└── DELIVERABLE_PACKAGE.md           # 交付物说明
```

## 🔧 配置说明

### Mock模式
系统支持Mock模式，无需外部API即可演示所有功能：
- 在各工具文件中设置 `USE_MOCK_DATA = True`
- 适用于演示、测试和开发环境

### 生产模式
- 配置真实的API token和OpenAI key
- 设置 `USE_MOCK_DATA = False`
- 确保网络连接到外部API服务

## 📈 性能特性

- **响应时间**: 单次查询通常在2-5秒内完成
- **并发支持**: 异步处理，支持多并发请求
- **容错能力**: Mock模式确保高可用性
- **扩展性**: 模块化设计，易于添加新功能

## 🛡️ 安全特性

- 环境变量管理敏感信息
- 输入验证和参数清理
- HTTPS外部API调用
- 错误信息安全处理

## 📚 文档资源

- [API文档](API_DOCUMENTATION.md) - 完整的API接口说明
- [部署指南](DEPLOYMENT_GUIDE.md) - 详细的部署和运维指南
- [交付物说明](DELIVERABLE_PACKAGE.md) - 项目交付物清单

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- **项目负责人**: LucasLv
- **开发团队**: Devin AI
- **版本**: v1.0.0
- **发布日期**: 2025年7月24日

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
