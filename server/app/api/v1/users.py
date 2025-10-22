"""
用户管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    get_current_user_id
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    user_service = UserService(db)
    
    # 检查用户名是否已存在
    if user_service.get_user_by_username(user_data.username):
        raise ConflictError("用户名已存在")
    
    # 检查邮箱是否已存在
    if user_service.get_user_by_email(user_data.email):
        raise ConflictError("邮箱已存在")
    
    # 创建用户
    user = user_service.create_user(user_data)
    
    return user


@router.post("/login")
async def login_user(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取当前用户信息"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user_id)
    
    if not user:
        raise NotFoundError("用户不存在")
    
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新当前用户信息"""
    user_service = UserService(db)
    
    # 检查用户名是否已被其他用户使用
    if user_update.username:
        existing_user = user_service.get_user_by_username(user_update.username)
        if existing_user and existing_user.id != current_user_id:
            raise ConflictError("用户名已被使用")
    
    # 检查邮箱是否已被其他用户使用
    if user_update.email:
        existing_user = user_service.get_user_by_email(user_update.email)
        if existing_user and existing_user.id != current_user_id:
            raise ConflictError("邮箱已被使用")
    
    user = user_service.update_user(current_user_id, user_update)
    
    if not user:
        raise NotFoundError("用户不存在")
    
    return user


@router.delete("/me")
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除当前用户账户"""
    user_service = UserService(db)
    success = user_service.delete_user(current_user_id)
    
    if not success:
        raise NotFoundError("用户不存在")
    
    return {"success": True, "message": "账户删除成功"}
