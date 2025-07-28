from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from electricity_price_tool import create_electricity_price_tool
from power_generation_duration_tool import create_power_generation_duration_tool
from photovoltaic_capacity_tool import create_photovoltaic_capacity_tool
from policy_query_tool import create_policy_query_tool
from main_router_agent import create_main_router_agent
from pydantic import BaseModel

app = FastAPI(title="大侠找光 AI 工具集", description="电价查询工具API服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

electricity_tool = create_electricity_price_tool()
power_generation_tool = create_power_generation_duration_tool()
photovoltaic_tool = create_photovoltaic_capacity_tool()
policy_tool = create_policy_query_tool()
main_agent = create_main_router_agent()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    result: str
    success: bool

@app.get("/")
async def root():
    return {"message": "大侠找光 AI 工具集 - 智能问答系统 & 专业工具服务"}

@app.post("/query_electricity_price", response_model=QueryResponse)
async def query_electricity_price(request: QueryRequest):
    """查询电价接口"""
    try:
        result = electricity_tool._run(request.query)
        success = not result.startswith("电价查询失败")
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.post("/query_power_generation_duration", response_model=QueryResponse)
async def query_power_generation_duration(request: QueryRequest):
    """查询有效发电小时数接口"""
    try:
        result = power_generation_tool._run(request.query)
        success = not result.startswith("有效发电小时数查询失败")
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.post("/query_photovoltaic_capacity", response_model=QueryResponse)
async def query_photovoltaic_capacity(request: QueryRequest):
    """查询光伏承载力接口"""
    try:
        result = photovoltaic_tool._run(request.query)
        success = not result.startswith("光伏承载力查询失败")
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.post("/query_policies", response_model=QueryResponse)
async def query_policies(request: QueryRequest):
    """查询政策接口"""
    try:
        result = policy_tool._run(request.query)
        success = not result.startswith("政策查询失败")
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.post("/ask_agent", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    """智能问答接口 - 主路由Agent"""
    try:
        result = main_agent.query(request.query)
        success = not any(error_phrase in result for error_phrase in ["出现错误", "无法处理", "无法理解"])
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["electricity_price_tool", "power_generation_duration_tool", "photovoltaic_capacity_tool", "policy_query_tool", "main_router_agent"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
