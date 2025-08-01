import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import HTTPException
import psycopg2
from psycopg2 import sql
import logging
import google.generativeai as genai
import re
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OCTDatabaseAgent:
    def __init__(self):
        self.db_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'oct_user',
            'password': 'oct_password',
            'database': 'oct_poc'
        }
        self.llm = None
        self._initialize_llm()
        self._test_database_connection()
    
    def _test_database_connection(self):
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.db_params)
            conn.close()
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
    
    def _initialize_llm(self):
        """Initialize Gemini LLM"""
        try:
            gemini_api_key = os.getenv('GOOGLE_API_KEY')
            if not gemini_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            genai.configure(api_key=gemini_api_key)
            self.llm = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info("Gemini LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise HTTPException(status_code=500, detail=f"LLM initialization failed: {e}")
    
    def _execute_sql_query(self, query: str) -> list:
        """Execute SQL query and return results"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            conn.close()
            
            return [dict(zip(columns, row)) for row in results]
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise e
    
    def _generate_sql_from_question(self, question: str) -> str:
        """Generate SQL query from natural language question using Gemini"""
        try:
            schema_info = """
数据库包含以下表格：
1. h1_carry_over_performance - 上半年经营指标完成情况(结转)
   - project_name: 项目名称 (VARCHAR)
   - period: 期间 (VARCHAR) - '上半年实际' 或 '下半年预计'
   - units_transferred: 结转套数 (INTEGER)
   - revenue: 收入(万元) (DECIMAL)
   - gross_profit: 毛利(万元) (DECIMAL)
   - taxes_and_surcharges: 税金及附加(万元) (DECIMAL)
   - period_expenses: 期间费用(万元) (DECIMAL)
   - net_profit: 净利润(万元) (DECIMAL)

2. h1_collections_performance - 上半年经营指标完成情况(回款)
   - project_name: 项目名称 (VARCHAR)
   - annual_target: 全年目标(万元) (DECIMAL)
   - h1_budget: 上半年预算(万元) (DECIMAL)
   - h1_actual: 上半年实际(万元) (DECIMAL)
   - h1_completion_rate: 上半年完成率 (VARCHAR)
   - annual_completion_rate: 年度完成率 (VARCHAR)
"""
            
            prompt = f"""你是一个专业的华侨城集团数据分析师。根据用户问题生成PostgreSQL查询语句。

{schema_info}

用户问题: {question}

请生成一个PostgreSQL查询语句来回答这个问题。只返回SQL语句，不要包含任何解释或其他文本。
如果问题涉及多个项目的汇总，请使用SUM函数。
如果问题询问数据来源，请在查询中包含表名信息。

SQL查询:"""

            response = self.llm.generate_content(prompt)
            sql_query = response.text.strip()
            
            sql_query = re.sub(r'```sql\s*', '', sql_query)
            sql_query = re.sub(r'```\s*$', '', sql_query)
            sql_query = sql_query.strip()
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise e
    
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return """你是一个专业的华侨城集团数据分析师。你需要根据用户的问题，生成并执行PostgreSQL查询语句，以从数据库中找到答案。

数据库包含以下表格：
1. h1_carry_over_performance - 上半年经营指标完成情况(结转)
   - project_name: 项目名称
   - period: 期间 (上半年实际/下半年预计)
   - units_transferred: 结转套数
   - revenue: 收入(万元)
   - gross_profit: 毛利(万元)
   - taxes_and_surcharges: 税金及附加(万元)
   - period_expenses: 期间费用(万元)
   - net_profit: 净利润(万元)

2. h1_collections_performance - 上半年经营指标完成情况(回款)
   - project_name: 项目名称
   - annual_target: 全年目标(万元)
   - h1_budget: 上半年预算(万元)
   - h1_actual: 上半年实际(万元)
   - h1_completion_rate: 上半年完成率
   - annual_completion_rate: 年度完成率

在回答时，请：
1. 使用中文回答
2. 表述清晰、专业
3. 如果涉及金额，请使用合适的单位（万元、亿元等）
4. 如果用户询问数据来源，请说明来自哪个表格
5. 如果查询结果为空，请礼貌地说明没有找到相关数据"""

    async def ask_question(self, question: str) -> Dict[str, Any]:
        """Process user question and return answer"""
        try:
            sql_query = self._generate_sql_from_question(question)
            logger.info(f"Generated SQL: {sql_query}")
            
            results = self._execute_sql_query(sql_query)
            
            answer = self._format_answer(question, sql_query, results)
            
            return {
                "question": question,
                "sql_query": sql_query,
                "raw_results": results,
                "answer": answer,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "answer": f"抱歉，处理您的问题时出现错误：{str(e)}",
                "status": "error"
            }
    
    def _format_answer(self, question: str, sql_query: str, results: list) -> str:
        """Format the query results into a user-friendly answer"""
        try:
            if not results:
                return "抱歉，没有找到相关数据。"
            
            results_text = str(results)
            
            prompt = f"""作为华侨城集团数据分析师，请根据以下查询结果回答用户问题。

用户问题: {question}
执行的SQL查询: {sql_query}
查询结果: {results_text}

请用中文提供专业、清晰的回答。如果涉及金额，请使用合适的单位（万元、亿元等）。
如果用户询问数据来源，请说明数据来自相应的数据表。

回答:"""

            response = self.llm.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error formatting answer: {e}")
            if len(results) == 1:
                result = results[0]
                return f"查询结果：{result}"
            else:
                return f"查询到 {len(results)} 条记录：{results}"
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name IN ('h1_carry_over_performance', 'h1_collections_performance')
                ORDER BY table_name, ordinal_position
            """)
            
            schema_info = cursor.fetchall()
            cursor.close()
            conn.close()
            
            tables = {}
            for table_name, column_name, data_type in schema_info:
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(f"{column_name} ({data_type})")
            
            return {
                "tables": tables,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {
                "error": str(e),
                "status": "error"
            }

oct_agent = None

def get_oct_agent() -> OCTDatabaseAgent:
    """Get or create OCT database agent instance"""
    global oct_agent
    if oct_agent is None:
        oct_agent = OCTDatabaseAgent()
    return oct_agent

async def test_agent_with_cases():
    """Test the agent with the required test cases"""
    agent = get_oct_agent()
    
    test_cases = [
        "昆山康盛上半年的结转收入是多少？",
        "上半年水月周庄和水月源岸的总回款是多少？", 
        "滁州康金上半年的净利润是多少？这个数据是哪里来的？"
    ]
    
    results = []
    for i, question in enumerate(test_cases, 1):
        print(f"\n=== 测试用例 {i} ===")
        print(f"问题: {question}")
        
        result = await agent.ask_question(question)
        results.append(result)
        
        print(f"回答: {result['answer']}")
        print(f"状态: {result['status']}")
        print("-" * 50)
    
    return results

if __name__ == "__main__":
    asyncio.run(test_agent_with_cases())
