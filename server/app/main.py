"""
FastAPI 主应用入口
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import create_tables
from app.api.v1 import photos, tags, albums, users, search
from app.core.exceptions import MomentoException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动 Momento AI Photo Management System...")
    create_tables()
    print("✅ 数据库表创建完成")
    
    yield
    
    # 关闭时执行
    print("👋 关闭 Momento AI Photo Management System...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI驱动的智能相册管理系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)


# 全局异常处理
@app.exception_handler(MomentoException)
async def momento_exception_handler(request, exc: MomentoException):
    """自定义异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.data
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTP_ERROR",
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR",
            "data": None
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    from app.database import health_check as db_health_check
    
    # 检查数据库连接
    db_health = db_health_check()
    
    # 简化Celery检查 - 只检查配置是否存在
    celery_status = "configured" if settings.celery_broker_url else "not_configured"
    
    return {
        "success": True,
        "message": "服务运行正常",
        "data": {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "status": "healthy",
            "database": db_health,
            "celery": celery_status,
            "config": {
                "debug": settings.debug,
                "database_url": settings.database_url.replace(settings.database_url.split('@')[0].split('//')[1], "***") if '@' in settings.database_url else settings.database_url,
                "redis_url": settings.redis_url,
                "upload_dir": settings.upload_dir,
                "model_cache_dir": settings.model_cache_dir
            }
        }
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "success": True,
        "message": f"欢迎使用 {settings.app_name}",
        "data": {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "docs_url": "/docs",
            "api_prefix": settings.api_v1_prefix
        }
    }


# 注册API路由
app.include_router(photos.router, prefix=f"{settings.api_v1_prefix}/photos", tags=["照片管理"])
app.include_router(tags.router, prefix=f"{settings.api_v1_prefix}/tags", tags=["标签管理"])
app.include_router(albums.router, prefix=f"{settings.api_v1_prefix}/albums", tags=["相册管理"])
app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["用户管理"])
app.include_router(search.router, prefix=f"{settings.api_v1_prefix}/search", tags=["搜索功能"])

# 添加静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
