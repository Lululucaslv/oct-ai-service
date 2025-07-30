import os
from typing import List, Any
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from electricity_price_tool import create_electricity_price_tool
from power_generation_duration_tool import create_power_generation_duration_tool
from photovoltaic_capacity_tool import create_photovoltaic_capacity_tool
from policy_query_tool import create_policy_query_tool
from business_knowledge_tool import create_business_knowledge_tool

load_dotenv()

class MainRouterAgent:
    """Main Router Agent that intelligently routes queries to appropriate tools with conversation memory."""
    
    def __init__(self):
        self.tools = self._load_tools()
        self.llm = self._setup_llm()
        self.memory = self._setup_memory()
        self.agent_executor = self._create_agent_executor()
    
    def _load_tools(self) -> List[BaseTool]:
        """Load all available tools."""
        tools = [
            create_electricity_price_tool(),
            create_power_generation_duration_tool(),
            create_photovoltaic_capacity_tool(),
            create_policy_query_tool(),
            create_business_knowledge_tool()
        ]
        return tools
    
    def _setup_memory(self) -> ConversationBufferMemory:
        """Setup conversation memory for multi-round dialogue."""
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
    
    def _setup_llm(self) -> ChatGoogleGenerativeAI:
        """Setup the Google Gemini language model with fallback logic."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found, using mock setup")
            return None
        
        try:
            print("Attempting to initialize Gemini 2.5 Flash model...")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                google_api_key=api_key
            )
        except Exception as e:
            print(f"Failed to initialize gemini-2.5-flash: {str(e)}")
            print("Falling back to gemini-1.5-flash-latest...")
            try:
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash-latest",
                    temperature=0,
                    google_api_key=api_key
                )
            except Exception as fallback_e:
                print(f"Fallback model also failed: {str(fallback_e)}")
                print("Using mock setup due to model initialization failures")
                return None
    
    def _create_main_prompt(self) -> PromptTemplate:
        """Create the main prompt template for the agent with conversation memory."""
        
        template = """你是"大侠找光"AI智能助手，专门帮助用户查询光伏相关信息。

你的角色和能力：
- 你是一个专业的光伏行业智能顾问
- 你可以理解用户的自然语言问题，并智能地选择合适的工具来回答
- 你可以同时调用多个工具来提供全面的答案
- 你的回答应该专业、准确、用户友好
- 你需要根据之前的对话历史（chat_history）来理解用户的当前问题

对话历史：
{chat_history}

可用工具：
{tools}

工具名称：{tool_names}

工具使用指南：
1. query_electricity_price: 当用户询问电价相关问题时使用（上网电价、脱硫煤电价、工商业电价）
2. query_power_generation_duration: 当用户询问发电小时数或发电时长相关问题时使用
3. query_photovoltaic_capacity: 当用户询问光伏承载力、可开放容量相关问题时使用
4. query_policies: 当用户询问政策、法规、补贴、标准等相关问题时使用
5. query_business_knowledge_base: 当用户询问关于公司业务、投资策略、项目要求等非结构化、解释性的问题时使用

思考过程：
- 仔细分析用户的问题，识别其中的关键信息和意图
- 查看对话历史，理解上下文中提到的地点、参数等信息
- 如果用户使用了"那边"、"这里"等指代词，从对话历史中找到具体的地理位置
- 判断需要使用哪个或哪些工具来回答问题
- 如果问题涉及多个方面，可以依次调用多个工具
- 将工具返回的结果整合成完整、连贯的回答

请使用以下格式进行思考和行动：

Question: 用户的问题
Thought: 我需要分析这个问题并决定使用哪些工具，同时考虑对话历史中的上下文信息
Action: 选择的工具名称
Action Input: 传递给工具的输入
Observation: 工具返回的结果
... (如果需要，可以重复 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回答

重要提示：
- 每个 Thought 后必须跟一个 Action
- 如果无法确定具体参数，直接给出 Final Answer 询问用户
- 保持格式严格一致，避免格式错误
- 充分利用对话历史来理解用户的指代和上下文

开始！

Question: {input}
Thought: {agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names", "chat_history"]
        )
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with enhanced error handling and memory."""
        if not self.llm:
            return None
        
        prompt = self._create_main_prompt()
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors="Check your output and make sure it conforms to the expected format. Try again.",
            max_iterations=10,
            max_execution_time=30,
            early_stopping_method="force"
        )
    
    def query(self, user_input: str) -> str:
        """Process user query and return response."""
        if not self.agent_executor:
            return self._mock_query_response(user_input)
        
        try:
            result = self.agent_executor.invoke({"input": user_input})
            return result.get("output", "抱歉，我无法处理您的问题。")
        except Exception as e:
            return f"处理查询时出现错误：{str(e)}"
    
    async def query_stream(self, user_input: str):
        """Process user query and return streaming response with improved error handling, deduplication, and memory."""
        if not self.agent_executor:
            mock_response = self._mock_query_response(user_input)
            words = mock_response.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield f" {word}"
            return
        
        yielded_content = set()
        
        try:
            async for event in self.agent_executor.astream({"input": user_input}):
                if isinstance(event, dict):
                    for key, value in event.items():
                        if key == "agent" and isinstance(value, dict):
                            if "messages" in value:
                                for message in value["messages"]:
                                    if hasattr(message, "content") and message.content:
                                        content = message.content.strip()
                                        if content and content not in yielded_content:
                                            if "Invalid Format:" not in content and "_Exception" not in content:
                                                yielded_content.add(content)
                                                yield content
                        
                        elif key == "tools" and isinstance(value, dict):
                            if "messages" in value:
                                for message in value["messages"]:
                                    if hasattr(message, "content") and message.content:
                                        obs_content = f"\nObservation: {message.content}"
                                        if obs_content not in yielded_content:
                                            yielded_content.add(obs_content)
                                            yield obs_content
                        
                        elif key == "output" and isinstance(value, str):
                            final_content = f"\nFinal Answer: {value}"
                            if final_content not in yielded_content:
                                yielded_content.add(final_content)
                                yield final_content
                                
        except Exception as e:
            error_msg = f"处理查询时出现错误：{str(e)}"
            if error_msg not in yielded_content:
                yield error_msg
    
    def clear_memory(self):
        """Clear conversation memory for a new session."""
        self.memory.clear()
    
    def _mock_query_response(self, user_input: str) -> str:
        """Mock response for testing without OpenAI API."""
        user_input_lower = user_input.lower()
        
        has_capacity = any(keyword in user_input for keyword in ["承载力", "可开放容量", "光伏承载"])
        has_policy = any(keyword in user_input for keyword in ["政策", "补贴", "法规", "标准"])
        
        if has_capacity and has_policy:
            capacity_result = self.tools[2]._run(user_input)
            policy_result = self.tools[3]._run(user_input)
            return f"[模拟路由] 检测到多工具查询需求：\n\n📊 光伏承载力信息：\n{capacity_result}\n\n📋 相关政策信息：\n{policy_result}"
        
        elif any(keyword in user_input for keyword in ["电价", "上网电价", "工商电价", "脱硫煤电价"]):
            tool = self.tools[0]  # electricity_price_tool
            return f"[模拟路由] 检测到电价查询，调用电价工具：\n{tool._run(user_input)}"
        
        elif any(keyword in user_input for keyword in ["发电小时", "发电时长", "有效发电"]):
            tool = self.tools[1]  # power_generation_duration_tool
            return f"[模拟路由] 检测到发电小时数查询，调用发电小时数工具：\n{tool._run(user_input)}"
        
        elif has_capacity:
            tool = self.tools[2]  # photovoltaic_capacity_tool
            return f"[模拟路由] 检测到光伏承载力查询，调用光伏承载力工具：\n{tool._run(user_input)}"
        
        elif has_policy or any(keyword in user_input for keyword in ["并网"]):
            tool = self.tools[3]  # policy_query_tool
            return f"[模拟路由] 检测到政策查询，调用政策工具：\n{tool._run(user_input)}"
        
        elif any(keyword in user_input for keyword in ["投资", "合作", "业务", "项目", "门槛", "周期", "模式", "地面", "屋顶"]):
            tool = self.tools[4]  # business_knowledge_tool
            return f"[模拟路由] 检测到业务咨询，调用业务知识库工具：\n{tool._run(user_input)}"
        
        else:
            return "抱歉，我无法理解您的问题。请询问关于电价、发电小时数、光伏承载力、政策或业务相关的问题。"

def create_main_router_agent():
    """Create and return the main router agent."""
    return MainRouterAgent()

def test_agent():
    """Test the main router agent with the specified test cases."""
    agent = create_main_router_agent()
    
    test_cases = [
        "安徽淮南的工商电价是多少？",
        "查找全国范围内关于户用屋顶光伏的并网接入政策",
        "我想了解一下河南开封的光伏承载力，顺便再看看那边有什么相关的补贴政策。"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {query}")
        print(f"{'='*60}")
        result = agent.query(query)
        print(f"Agent回答:\n{result}")

if __name__ == "__main__":
    test_agent()
