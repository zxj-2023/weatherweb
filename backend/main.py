from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from typing import List


from config import APP_HOST, APP_PORT, APP_DEBUG, CORS_ORIGINS

from apps.weather.weather import weather
from apps.user.user import user
from apps.ai.ai import ai_router

app = FastAPI(
    title="智能天气提醒助手",
    description="一个提供实时天气信息和智能提醒的Web应用",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

#接口
app.include_router(weather,prefix="/api/weather",tags=["天气信息接口"])
app.include_router(user,prefix="/api",tags=["用户管理接口"])
app.include_router(ai_router,prefix="/api/ai",tags=["AI聊天接口"])

@app.get("/")
async def root():
    """根路径重定向到前端页面"""
    return FileResponse("../frontend/index.html")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "智能天气提醒助手"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_DEBUG
    )
