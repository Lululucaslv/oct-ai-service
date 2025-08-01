# 企业微信AI客服集成指南

## 概述

本指南将帮助您配置和部署"归芯"项目的企业微信AI客服系统。该系统基于LangChain RAG技术，能够智能回答技术问题并通过企业微信自动回复客户。

## 系统架构

```
企业微信客户群 → 企业微信API → FastAPI服务 → LangChain RAG智能体 → 知识库检索 → 智能回答
```

## 前置准备

### 1. 企业微信管理后台配置

#### 1.1 创建自建应用
1. 登录企业微信管理后台：https://work.weixin.qq.com/
2. 进入"应用管理" → "自建" → "创建应用"
3. 填写应用信息：
   - 应用名称：归芯AI客服
   - 应用介绍：智能技术支持助手
   - 应用logo：上传合适的图标

#### 1.2 获取应用凭证
创建应用后，记录以下信息：
- **企业ID (Corp ID)**: 在"我的企业" → "企业信息"中查看
- **应用Secret**: 在应用详情页面查看
- **应用ID (Agent ID)**: 在应用详情页面查看

#### 1.3 配置应用权限
1. 在应用详情页面，设置"可见范围"
2. 添加需要使用AI客服的部门或成员
3. 确保应用有"发送消息"权限

### 2. 服务器部署准备

#### 2.1 域名和SSL证书
- 准备一个公网可访问的域名（如：api.yourcompany.com）
- 配置SSL证书（企业微信要求HTTPS）

#### 2.2 服务器要求
- Linux服务器（推荐Ubuntu 20.04+）
- Docker和Docker Compose
- 至少2GB内存，10GB存储空间

## 配置步骤

### 1. 下载和配置代码

```bash
# 克隆代码仓库
git clone <repository_url>
cd daxiazhaoguang-ai

# 复制环境变量模板
cp .env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件，填入以下配置：

```bash
# Google API Key for Gemini LLM
GOOGLE_API_KEY=your_google_api_key_here

# WeChat Work Configuration
WECHAT_CORP_ID=your_corp_id_here
WECHAT_APP_SECRET=your_app_secret_here
WECHAT_AGENT_ID=your_agent_id_here
WECHAT_TOKEN=your_callback_token_here
WECHAT_ENCODING_AES_KEY=your_encoding_aes_key_here
```

#### 配置说明：

**GOOGLE_API_KEY**: 
- 访问 https://makersuite.google.com/app/apikey
- 创建新的API密钥
- 确保启用Gemini API访问权限

**WECHAT_CORP_ID**: 
- 企业微信管理后台 → "我的企业" → "企业信息" → "企业ID"

**WECHAT_APP_SECRET**: 
- 企业微信管理后台 → "应用管理" → 选择您的应用 → "Secret"

**WECHAT_AGENT_ID**: 
- 企业微信管理后台 → "应用管理" → 选择您的应用 → "AgentId"

**WECHAT_TOKEN**: 
- 自定义字符串（用于验证回调URL）
- 建议使用随机生成的32位字符串

**WECHAT_ENCODING_AES_KEY**: 
- 企业微信管理后台 → 应用详情 → "接收消息" → "设置API接收"
- 可以随机生成或手动设置43位字符串

### 3. 部署应用

```bash
# 构建和启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f daxiazhaoguang-ai
```

### 4. 配置企业微信回调URL

#### 4.1 设置回调URL
1. 进入企业微信管理后台
2. 选择您的应用 → "接收消息"
3. 点击"设置API接收"
4. 填写以下信息：
   - **URL**: `https://your-domain.com/wechat-hook`
   - **Token**: 与`.env`文件中的`WECHAT_TOKEN`保持一致
   - **EncodingAESKey**: 与`.env`文件中的`WECHAT_ENCODING_AES_KEY`保持一致

#### 4.2 验证回调URL
1. 点击"保存"按钮
2. 企业微信会向您的服务器发送验证请求
3. 如果配置正确，会显示"保存成功"

## 测试验证

### 1. API健康检查

```bash
curl https://your-domain.com/health
```

预期响应：
```json
{
  "status": "healthy",
  "services": {
    "oct_database_agent": "华侨城数据库问答智能体",
    "wechat_rag_agent": "企业微信RAG智能体",
    "wechat_api_handler": "企业微信API处理器"
  }
}
```

### 2. 知识库状态检查

```bash
curl https://your-domain.com/wechat/knowledge-base-info
```

### 3. 企业微信API状态检查

```bash
curl https://your-domain.com/wechat/api-status
```

### 4. RAG对话测试

```bash
curl -X POST https://your-domain.com/wechat/rag-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Arduino Uno有多少个数字引脚？",
    "user_id": "test_user"
  }'
```

### 5. 企业微信消息测试

在企业微信中：
1. 找到您创建的AI客服应用
2. 发送测试消息："你好"
3. 等待AI回复

## 知识库管理

### 1. 添加技术文档

将您的技术文档放入 `knowledge_base/` 目录：

```bash
# 支持的文件格式
knowledge_base/
├── product_manual.md
├── technical_specs.md
├── troubleshooting_guide.md
└── api_documentation.md
```

### 2. 重建知识库

```bash
# 删除现有向量数据库
rm -rf vector_store/

# 重启服务以重建知识库
docker-compose restart daxiazhaoguang-ai
```

## 监控和维护

### 1. 日志监控

```bash
# 实时查看日志
docker-compose logs -f daxiazhaoguang-ai

# 查看最近100行日志
docker-compose logs --tail=100 daxiazhaoguang-ai
```

### 2. 性能监控

```bash
# 查看容器资源使用情况
docker stats daxiazhaoguang-ai_daxiazhaoguang-ai_1
```

### 3. 备份和恢复

```bash
# 备份知识库和配置
tar -czf backup-$(date +%Y%m%d).tar.gz knowledge_base/ vector_store/ .env

# 恢复备份
tar -xzf backup-20240101.tar.gz
docker-compose restart
```

## 故障排除

### 1. 常见问题

**问题**: 企业微信回调URL验证失败
- 检查服务器是否可以通过HTTPS访问
- 确认Token和EncodingAESKey配置正确
- 查看服务器日志中的错误信息

**问题**: AI回复不准确
- 检查知识库文档是否完整
- 确认Gemini API密钥有效
- 查看RAG检索结果是否相关

**问题**: 消息发送失败
- 检查企业微信应用权限设置
- 确认Corp ID和App Secret正确
- 验证用户是否在应用可见范围内

### 2. 调试命令

```bash
# 检查容器状态
docker-compose ps

# 进入容器调试
docker-compose exec daxiazhaoguang-ai bash

# 重启特定服务
docker-compose restart daxiazhaoguang-ai

# 查看详细错误日志
docker-compose logs daxiazhaoguang-ai | grep ERROR
```

### 3. 联系支持

如果遇到无法解决的问题，请提供以下信息：
- 错误日志截图
- 配置文件内容（隐藏敏感信息）
- 问题复现步骤
- 服务器环境信息

## 安全建议

1. **定期更新密钥**: 定期轮换API密钥和Token
2. **访问控制**: 限制服务器访问权限
3. **日志审计**: 定期检查访问日志
4. **备份策略**: 建立定期备份机制
5. **监控告警**: 设置异常情况告警

## 扩展功能

### 1. 多语言支持
- 在知识库中添加多语言文档
- 修改系统提示词支持多语言回复

### 2. 自定义回复模板
- 编辑 `wechat_rag_agent.py` 中的系统提示词
- 添加特定场景的回复模板

### 3. 用户权限管理
- 实现基于用户ID的权限控制
- 添加管理员命令功能

### 4. 数据分析
- 收集用户问题统计
- 分析知识库覆盖率
- 优化回复质量

---

**版本**: v1.0  
**更新日期**: 2025年1月  
**维护团队**: 归芯项目技术团队
