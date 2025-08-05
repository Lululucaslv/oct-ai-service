from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import asyncio
import json
import uuid
import time
from typing import Dict, Optional, List
import logging
import os
logger = logging.getLogger(__name__)

from oct_database_agent_supabase import get_oct_agent_supabase
from pydantic import BaseModel

app = FastAPI(title="华侨城 AI 问答服务", description="OCT AI Q&A API Service")

class OCTQueryRequest(BaseModel):
    query: str

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

@app.post("/ask_oct")
async def ask_oct_question(request: QueryRequest):
    """OCT database Q&A endpoint"""
    try:
        oct_agent = get_oct_agent_supabase()
        
        result = await oct_agent.ask_question(request.query)
        
        return {
            "question": request.query,
            "answer": result.get("answer", ""),
            "status": result.get("status", "error"),
            "success": result.get("status") == "success"
        }
        
    except Exception as e:
        return {
            "question": request.query,
            "answer": f"系统错误: {str(e)}",
            "status": "error",
            "success": False
        }

@app.get("/oct/database_info")
async def get_oct_database_info():
    """Get OCT database schema information"""
    try:
        oct_agent = get_oct_agent_supabase()
        return oct_agent.get_database_info()
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "services": {
            "oct_database_agent": "华侨城数据库问答智能体"
        },
        "database": "Supabase PostgreSQL"
    }

handler = app
