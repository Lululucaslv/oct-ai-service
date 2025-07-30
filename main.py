from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import uuid
import time
from typing import Dict, Optional, List
from electricity_price_tool import create_electricity_price_tool
from power_generation_duration_tool import create_power_generation_duration_tool
from photovoltaic_capacity_tool import create_photovoltaic_capacity_tool
from policy_query_tool import create_policy_query_tool
from main_router_agent import create_main_router_agent, MainRouterAgent
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

session_agents: Dict[str, MainRouterAgent] = {}

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    result: str
    success: bool

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict

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

def get_or_create_agent(session_id: Optional[str]) -> tuple[MainRouterAgent, str]:
    """Get or create agent for session with memory management."""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if session_id not in session_agents:
        session_agents[session_id] = create_main_router_agent()
    
    return session_agents[session_id], session_id

@app.post("/ask_agent", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    """智能问答接口 - 主路由Agent (非流式)"""
    try:
        agent, session_id = get_or_create_agent(request.session_id)
        result = agent.query(request.query)
        success = not any(error_phrase in result for error_phrase in ["出现错误", "无法处理", "无法理解"])
        return QueryResponse(result=result, success=success)
    except Exception as e:
        return QueryResponse(result=f"系统错误: {str(e)}", success=False)

@app.post("/ask_agent_stream")
async def ask_agent_stream(request: QueryRequest):
    """智能问答接口 - 主路由Agent (流式响应) with session memory"""
    
    async def generate_stream():
        """Generate Server-Sent Events stream with session management"""
        try:
            agent, session_id = get_or_create_agent(request.session_id)
            
            session_data = json.dumps({'session_id': session_id, 'type': 'session'}, ensure_ascii=False)
            yield f"data: {session_data}\n\n".encode('utf-8')
            
            async for chunk in agent.query_stream(request.query):
                if chunk:
                    chunk_escaped = chunk.replace('\n', '\\n').replace('\r', '\\r')
                    data = json.dumps({'chunk': chunk_escaped, 'type': 'content'}, ensure_ascii=False)
                    yield f"data: {data}\n\n".encode('utf-8')
                    
            done_data = json.dumps({'type': 'done'}, ensure_ascii=False)
            yield f"data: {done_data}\n\n".encode('utf-8')
            
        except Exception as e:
            error_msg = f"系统错误: {str(e)}"
            error_data = json.dumps({'chunk': error_msg, 'type': 'error'}, ensure_ascii=False)
            yield f"data: {error_data}\n\n".encode('utf-8')
            done_data = json.dumps({'type': 'done'}, ensure_ascii=False)
            yield f"data: {done_data}\n\n".encode('utf-8')
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )

@app.post("/clear_session")
async def clear_session(request: dict):
    """Clear conversation memory for a specific session"""
    session_id = request.get("session_id")
    if session_id and session_id in session_agents:
        session_agents[session_id].clear_memory()
        return {"status": "success", "message": f"Session {session_id} memory cleared"}
    return {"status": "error", "message": "Session not found"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "services": ["electricity_price_tool", "power_generation_duration_tool", "photovoltaic_capacity_tool", "policy_query_tool", "main_router_agent"],
        "active_sessions": len(session_agents)
    }

@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "daxia-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "daxiazhaoguang"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message.content
                break
        
        if not user_message:
            user_message = "你好"
        
        agent, session_id = get_or_create_agent(None)
        
        if request.stream:
            async def generate_openai_stream():
                try:
                    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
                    created = int(time.time())
                    
                    initial_chunk = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {"role": "assistant", "content": ""},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(initial_chunk, ensure_ascii=False)}\n\n"
                    
                    async for chunk in agent.query_stream(user_message):
                        if chunk:
                            content_chunk = {
                                "id": response_id,
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": request.model,
                                "choices": [{
                                    "index": 0,
                                    "delta": {"content": chunk},
                                    "finish_reason": None
                                }]
                            }
                            yield f"data: {json.dumps(content_chunk, ensure_ascii=False)}\n\n"
                    
                    final_chunk = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_chunk = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": f"系统错误: {str(e)}"},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_openai_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            result = agent.query(user_message)
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_message),
                    "completion_tokens": len(result),
                    "total_tokens": len(user_message) + len(result)
                }
            }
            return response
            
    except Exception as e:
        return {
            "error": {
                "message": f"系统错误: {str(e)}",
                "type": "internal_server_error",
                "code": "internal_error"
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
