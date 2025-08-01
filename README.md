# OCT PoC - 华侨城项目概念验证

## 项目概述
本项目为华侨城(OCT)项目的概念验证(PoC)，演示从PPT文件提取数据、存储到PostgreSQL数据库，并通过n8n工作流生成Excel报告的完整流程。

## 项目结构
```
oct-poc/
├── docker-compose.yml          # PostgreSQL容器配置
├── setup.sql                   # 数据库设置和数据插入脚本
├── OCT_PoC_Workflow.json      # n8n工作流配置文件
├── extract_ppt_and_setup_db.py # 数据库设置和验证脚本
├── generate_excel_report.py    # Excel报告生成脚本
├── poc_extraction_report.xlsx  # 最终生成的Excel报告
└── README.md                   # 本文档
```

## 数据表结构

### h1_carry_over_performance (结转业绩表)
- `project_name`: 项目名称
- `period`: 期间 (上半年实际/下半年预计)
- `units_transferred`: 结转套数
- `revenue`: 收入(万元)
- `gross_profit`: 毛利(万元)
- `taxes_and_surcharges`: 税金及附加(万元)
- `period_expenses`: 期间费用(万元)
- `net_profit`: 净利润(万元)

### h1_collections_performance (回款业绩表)
- `project_name`: 项目名称
- `annual_target`: 全年目标(万元)
- `h1_budget`: 上半年预算(万元)
- `h1_actual`: 上半年实际(万元)
- `h1_completion_rate`: 上半年完成率
- `annual_completion_rate`: 年度完成率

## 数据来源
数据来源于《昆山康盛半年度工作报告-终稿.pptx》文件中的关键表格：
- 幻灯片4: 上半年经营指标完成情况--结转
- 幻灯片6: 上半年经营指标完成情况--回款
- 幻灯片10: 下半年经营指标预计--结转
- 幻灯片12: 下半年经营指标预计--回款

## 快速开始

### 1. 启动PostgreSQL数据库
```bash
cd /home/ubuntu/oct-poc
docker-compose up -d
```

### 2. 设置数据库和插入数据
```bash
python3 extract_ppt_and_setup_db.py
```

### 3. 生成Excel报告
```bash
python3 generate_excel_report.py
```

### 4. 使用n8n工作流 (可选)
1. 安装n8n: `npm install -g n8n`
2. 启动n8n: `n8n start`
3. 访问 http://localhost:5678
4. 导入 `OCT_PoC_Workflow.json`
5. 配置PostgreSQL连接:
   - Host: localhost
   - Port: 5432
   - Database: oct_poc
   - Username: oct_user
   - Password: oct_password
6. 执行工作流生成Excel报告

## 验证步骤

### 数据库连接测试
```bash
psql -h localhost -U oct_user -d oct_poc
```

### 查询数据验证
```sql
-- 查看结转业绩数据
SELECT * FROM h1_carry_over_performance;

-- 查看回款业绩数据
SELECT * FROM h1_collections_performance;
```

## 交付物说明

### 1. setup.sql
- 创建数据库表结构
- 插入从PPT提取的实际数据
- 设置索引和权限
- 包含数据验证查询

### 2. OCT_PoC_Workflow.json
- n8n工作流配置文件
- 包含PostgreSQL查询节点
- 包含Excel生成节点
- 支持中文列名和工作表名称

### 3. poc_extraction_report.xlsx
- 双工作表Excel文件
- "结转业绩"工作表：包含项目结转数据
- "回款业绩"工作表：包含项目回款数据
- 专业格式化和样式

## 技术特点

### 数据完整性
- 从PPT文件中准确提取表格数据
- 保持原始数据的完整性和格式
- 支持中文项目名称和字段名

### 自动化流程
- Docker容器化部署
- 自动化数据库设置
- 一键生成Excel报告
- n8n可视化工作流

### 扩展性设计
- 模块化代码结构
- 易于添加新的数据表
- 支持不同数据源集成
- 可配置的报告格式

## 项目数据概览

### 主要项目
- **水月周庄**: 昆山康盛核心住宅项目
- **水月源岸**: 昆山康盛主要收入来源
- **铂尔曼酒店**: 酒店业务板块
- **滁州欢乐明湖**: 滁州康金项目

### 关键指标
- 上半年总收入: 54,484万元
- 下半年预计收入: 51,737万元
- 年度回款目标: 255,255万元
- 上半年实际回款: 62,569万元

## 联系信息
本PoC项目由Devin AI开发，用于演示华侨城项目的数据提取和报告生成能力。
