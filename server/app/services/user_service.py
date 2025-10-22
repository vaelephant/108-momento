"""
用户服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.security import get_password_hash


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.get_user_by_username(user_data.username):
            raise ConflictError("用户名已存在")
        
        # 检查邮箱是否已存在
        if self.get_user_by_email(user_data.email):
            raise ConflictError("邮箱已存在")
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        # 检查用户名是否已被其他用户使用
        if user_update.username:
            existing_user = self.get_user_by_username(user_update.username)
            if existing_user and existing_user.id != user_id:
                raise ConflictError("用户名已被使用")
            user.username = user_update.username
        
        # 检查邮箱是否已被其他用户使用
        if user_update.email:
            existing_user = self.get_user_by_email(user_update.email)
            if existing_user and existing_user.id != user_id:
                raise ConflictError("邮箱已被使用")
            user.email = user_update.email
        
        # 更新其他字段
        if user_update.default_language is not None:
            user.default_language = user_update.default_language
        
        if user_update.auto_tagging is not None:
            user.auto_tagging = user_update.auto_tagging
        
        if user_update.privacy_level is not None:
            user.privacy_level = user_update.privacy_level
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        
        return True
