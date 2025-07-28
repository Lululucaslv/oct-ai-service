# 大侠找光 AI 工具集部署指南

## 环境要求

### 系统要求
- Python 3.8+
- 操作系统: Linux/macOS/Windows
- 内存: 最少2GB，推荐4GB+
- 磁盘空间: 最少1GB

### 依赖包
所有依赖已在 `requirements.txt` 中定义：
```
langchain
langchain-openai
fastapi
uvicorn
requests
python-dotenv
pydantic
```

## 快速部署

### 1. 环境准备
```bash
# 克隆或下载项目代码
cd daxiazhaoguang-ai

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置
创建 `.env` 文件：
```bash
# API配置
BASE_URL=https://test.daxiazhaoguang.com/server/
DAXIA_API_TOKEN=your_daxia_token_here

# OpenAI配置 (可选，用于真实LLM调用)
OPENAI_API_KEY=your_openai_api_key_here
```

**重要说明:**
- 如果没有配置 `OPENAI_API_KEY`，系统将自动使用Mock模式
- Mock模式下所有功能正常，适合演示和测试
- `DAXIA_API_TOKEN` 用于访问真实的光伏数据API

### 3. 启动服务
```bash
# 开发模式启动
python main.py

# 或使用uvicorn启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 验证部署
```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 测试智能查询
curl -X POST "http://localhost:8000/ask_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "北京市的有效发电小时数是多少？"}'
```

## 生产环境部署

### 使用Docker (推荐)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用Gunicorn
```bash
# 安装gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 配置说明

### 工具配置
每个工具都支持独立配置：

1. **Mock模式控制**: 在各工具文件中设置 `USE_MOCK_DATA = True/False`
2. **API超时设置**: 可在工具中调整requests超时参数
3. **重试机制**: 支持API调用失败时的重试逻辑

### 性能调优
```python
# main.py 中可调整的参数
app = FastAPI(
    title="大侠找光 AI 工具集",
    description="光伏行业智能查询服务",
    version="1.0.0",
    docs_url="/docs",  # API文档地址
    redoc_url="/redoc"  # 备用文档地址
)
```

## 监控和日志

### 日志配置
系统使用Python标准logging模块，可通过以下方式配置：
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康检查
- 端点: `GET /health`
- 返回所有服务状态
- 可用于负载均衡器健康检查

### 性能监控
建议集成以下监控工具：
- **Prometheus**: 指标收集
- **Grafana**: 可视化监控
- **ELK Stack**: 日志分析

## 故障排除

### 常见问题

1. **端口占用**
```bash
# 查找占用端口的进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

2. **依赖安装失败**
```bash
# 升级pip
pip install --upgrade pip
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

3. **API调用失败**
- 检查网络连接
- 验证API token有效性
- 查看详细错误日志

### 调试模式
```bash
# 启用详细日志
export PYTHONPATH=.
python -m uvicorn main:app --log-level debug --reload
```

## 安全建议

1. **环境变量**: 敏感信息使用环境变量，不要硬编码
2. **HTTPS**: 生产环境必须使用HTTPS
3. **防火墙**: 限制不必要的端口访问
4. **更新**: 定期更新依赖包和系统补丁
5. **备份**: 定期备份配置和数据

## 扩展开发

### 添加新工具
1. 创建新的工具类，继承 `BaseTool`
2. 实现 `_run` 方法
3. 在 `main_router_agent.py` 中注册新工具
4. 更新主提示词模板

### API扩展
1. 在 `main.py` 中添加新端点
2. 定义请求/响应模型
3. 实现业务逻辑
4. 更新API文档

## 技术支持

如遇到部署问题，请检查：
1. Python版本兼容性
2. 依赖包版本冲突
3. 网络连接状态
4. 环境变量配置
5. 日志错误信息

建议在测试环境先验证部署流程，确认无误后再部署到生产环境。
