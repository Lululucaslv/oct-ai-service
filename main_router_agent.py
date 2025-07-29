import os
from typing import List, Any
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from dotenv import load_dotenv

from electricity_price_tool import create_electricity_price_tool
from power_generation_duration_tool import create_power_generation_duration_tool
from photovoltaic_capacity_tool import create_photovoltaic_capacity_tool
from policy_query_tool import create_policy_query_tool
from business_knowledge_tool import create_business_knowledge_tool

load_dotenv()

class MainRouterAgent:
    """Main Router Agent that intelligently routes queries to appropriate tools."""
    
    def __init__(self):
        self.tools = self._load_tools()
        self.llm = self._setup_llm()
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
        """Create the main prompt template for the agent."""
        
        template = """你是"大侠找光"AI智能助手，专门帮助用户查询光伏相关信息。

你的角色和能力：
- 你是一个专业的光伏行业智能顾问
- 你可以理解用户的自然语言问题，并智能地选择合适的工具来回答
- 你可以同时调用多个工具来提供全面的答案
- 你的回答应该专业、准确、用户友好

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
- 判断需要使用哪个或哪些工具来回答问题
- 如果问题涉及多个方面，可以依次调用多个工具
- 将工具返回的结果整合成完整、连贯的回答

请使用以下格式进行思考和行动：

Question: 用户的问题
Thought: 我需要分析这个问题并决定使用哪些工具
Action: 选择的工具名称
Action Input: 传递给工具的输入
Observation: 工具返回的结果
... (如果需要，可以重复 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回答

开始！

Question: {input}
Thought: {agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor."""
        if not self.llm:
            return None
        
        prompt = self._create_main_prompt()
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            max_execution_time=60
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
        """Process user query and return streaming response."""
        if not self.agent_executor:
            mock_response = self._mock_query_response(user_input)
            words = mock_response.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield f" {word}"
            return
        
        try:
            async for event in self.agent_executor.astream({"input": user_input}):
                if isinstance(event, dict):
                    for key, value in event.items():
                        if key == "agent" and isinstance(value, dict):
                            if "messages" in value:
                                for message in value["messages"]:
                                    if hasattr(message, "content") and message.content:
                                        content = message.content.strip()
                                        if content:
                                            yield content
                        
                        elif key == "tools" and isinstance(value, dict):
                            if "messages" in value:
                                for message in value["messages"]:
                                    if hasattr(message, "content") and message.content:
                                        yield f"\nObservation: {message.content}"
                        
                        elif key == "messages" and isinstance(value, list):
                            for message in value:
                                if hasattr(message, "content") and message.content:
                                    content = message.content.strip()
                                    if content:
                                        if hasattr(message, "type"):
                                            if message.type == "ai":
                                                yield content
                                            elif message.type == "human":
                                                yield f"\nObservation: {content}"
                                        else:
                                            yield content
                        
                        elif key == "actions" and isinstance(value, list):
                            for action in value:
                                if hasattr(action, "tool") and hasattr(action, "tool_input"):
                                    yield f"\nAction: {action.tool}"
                                    yield f"\nAction Input: {action.tool_input}"
                        
                        elif key == "steps" and isinstance(value, list):
                            for step in value:
                                if hasattr(step, "action") and hasattr(step, "observation"):
                                    action = step.action
                                    if hasattr(action, "tool") and hasattr(action, "tool_input"):
                                        yield f"\nAction: {action.tool}"
                                        yield f"\nAction Input: {action.tool_input}"
                                    yield f"\nObservation: {step.observation}"
                        
                        elif key == "output" and isinstance(value, str):
                            yield f"\nFinal Answer: {value}"
                                
        except Exception as e:
            yield f"处理查询时出现错误：{str(e)}"
    
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
