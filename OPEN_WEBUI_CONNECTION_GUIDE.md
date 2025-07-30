# Open WebUI 连接指南

## 概述
本指南说明如何将"大侠找光"AI智能体集成到Open WebUI中，通过LiteLLM代理服务实现标准OpenAI格式的API调用。

## 架构说明
```
Open WebUI → LiteLLM代理 (端口4000) → 大侠找光FastAPI服务 (端口8000)
```

## 部署步骤

### 1. 启动服务
使用Docker Compose启动所有服务：
```bash
docker-compose up -d
```

这将启动：
- `daxiazhaoguang-ai`: 主AI服务 (端口8000)
- `litellm-proxy`: LiteLLM代理服务 (端口4000)

### 2. 验证服务状态
检查服务是否正常运行：
```bash
# 检查AI服务
curl http://localhost:8000/health

# 检查LiteLLM代理
curl http://localhost:4000/health

# 测试OpenAI兼容端点
curl http://localhost:8000/v1/models
```

### 3. Open WebUI配置

#### 3.1 访问管理员设置
1. 登录Open WebUI管理员账户
2. 进入"设置" → "模型"页面

#### 3.2 添加自定义模型
在模型配置中添加以下信息：

**API基础URL**: `http://<服务器IP>:4000`
- 如果Open WebUI与服务在同一台机器上：`http://localhost:4000`
- 如果在不同机器上：`http://YOUR_SERVER_IP:4000`

**模型名称**: `daxia-agent`

**API密钥**: 任意值（例如：`sk-fake-key`）

#### 3.3 保存配置
点击"保存"完成模型添加

## 使用方法

### 在Open WebUI中使用
1. 在对话界面选择"daxia-agent"模型
2. 开始与"大侠找光"AI智能体对话
3. 支持多轮对话和上下文记忆

### 支持的功能
- **电价查询**: 查询脱硫煤电价、上网电价、工商加权电价
- **发电时长查询**: 查询光伏发电等效利用小时数
- **光伏承载力查询**: 查询分布式光伏承载力
- **政策查询**: 查询光伏补贴政策信息
- **业务知识问答**: 基于知识库的业务相关问题解答
- **多轮对话**: 支持上下文理解和会话记忆

### 示例对话
```
用户: 我想了解一下河南开封的光伏承载力
AI: [调用光伏承载力工具，返回开封地区数据]

用户: 那边的补贴政策呢？
AI: [理解"那边"指河南开封，调用政策查询工具]
```

## 技术细节

### 服务配置
- **LiteLLM配置文件**: `litellm_config.yaml`
- **模型标识**: `daxia-agent`
- **内部路由**: 请求转发到 `/ask_agent_stream` 端点
- **响应格式**: OpenAI兼容的流式响应

### 网络配置
- **Docker网络**: `daxiazhaoguang-network`
- **服务依赖**: LiteLLM代理依赖于主AI服务
- **端口映射**: 
  - 8000 → FastAPI服务
  - 4000 → LiteLLM代理

### 故障排除

#### 连接问题
1. 确认所有服务正常运行：`docker-compose ps`
2. 检查端口是否被占用：`netstat -tlnp | grep :4000`
3. 查看服务日志：`docker-compose logs litellm-proxy`

#### 模型不可用
1. 验证LiteLLM配置：`docker exec -it daxiazhaoguang-ai-litellm-proxy-1 cat /app/litellm_config.yaml`
2. 检查模型列表：`curl http://localhost:4000/v1/models`
3. 重启代理服务：`docker-compose restart litellm-proxy`

#### API调用失败
1. 测试直接API调用：
```bash
curl -X POST "http://localhost:4000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-fake-key" \
  -d '{
    "model": "daxia-agent",
    "messages": [{"role": "user", "content": "测试消息"}],
    "stream": false
  }'
```

## 支持与维护
如遇问题，请检查：
1. Docker容器状态
2. 网络连接
3. 配置文件格式
4. 服务日志输出

更多技术支持请参考项目文档或联系开发团队。
