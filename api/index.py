from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="华侨城 AI 问答服务", description="OCT AI Q&A API Service")

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
    return {"status": "healthy", "service": "OCT AI Q&A"}
