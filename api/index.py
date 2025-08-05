from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="华侨城 AI 问答服务", description="OCT AI Q&A API Service")

class QueryRequest(BaseModel):
    query: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "华侨城 AI 问答服务", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "OCT AI Q&A", "version": "1.0.1"}

@app.post("/ask_oct")
async def ask_oct_question(request: QueryRequest):
    """OCT database Q&A endpoint - simplified version for testing"""
    try:
        return {
            "question": request.query,
            "answer": f"这是一个测试响应，您询问了：{request.query}。OCT数据库连接功能正在开发中。",
            "status": "success",
            "success": True
        }
    except Exception as e:
        return {
            "question": request.query,
            "answer": f"系统错误: {str(e)}",
            "status": "error",
            "success": False
        }
