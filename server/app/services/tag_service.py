"""
标签服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional
from datetime import datetime

from app.models import Tag, PhotoTag, Photo
from app.schemas import TagCreate, TagResponse, PhotoTagResponse
from app.core.exceptions import NotFoundError, ValidationError


class TagService:
    """标签服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tags(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> List[Tag]:
        """获取标签列表"""
        query = self.db.query(Tag)
        
        if category:
            query = query.filter(Tag.category == category)
        
        if search:
            query = query.filter(
                or_(
                    Tag.name.ilike(f"%{search}%"),
                    Tag.zh.ilike(f"%{search}%"),
                    Tag.ja.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(Tag.name).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
    
    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        """根据ID获取标签"""
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        return self.db.query(Tag).filter(Tag.name == name).first()
    
    def create_tag(self, tag_data: TagCreate) -> Tag:
        """创建标签"""
        # 检查标签是否已存在
        existing_tag = self.get_tag_by_name(tag_data.name)
        if existing_tag:
            raise ValidationError("标签已存在")
        
        tag = Tag(
            name=tag_data.name,
            zh=tag_data.zh,
            ja=tag_data.ja,
            category=tag_data.category,
            description=tag_data.description
        )
        
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        return tag
    
    def get_photo_tags(self, photo_id: int, user_id: int) -> List[PhotoTag]:
        """获取照片的标签"""
        return self.db.query(PhotoTag).join(Photo).filter(
            and_(
                PhotoTag.photo_id == photo_id,
                Photo.user_id == user_id
            )
        ).all()
    
    def add_photo_tags(self, photo_id: int, tag_ids: List[int], user_id: int) -> bool:
        """为照片添加标签"""
        # 检查照片是否存在且属于用户
        photo = self.db.query(Photo).filter(
            and_(Photo.id == photo_id, Photo.user_id == user_id)
        ).first()
        
        if not photo:
            return False
        
        # 检查标签是否存在
        tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        
        if len(tags) != len(tag_ids):
            raise ValidationError("部分标签不存在")
        
        # 添加标签关联
        for tag in tags:
            # 检查是否已存在
            existing = self.db.query(PhotoTag).filter(
                and_(
                    PhotoTag.photo_id == photo_id,
                    PhotoTag.tag_id == tag.id,
                    PhotoTag.source == "manual"
                )
            ).first()
            
            if not existing:
                photo_tag = PhotoTag(
                    photo_id=photo_id,
                    tag_id=tag.id,
                    source="manual",
                    confidence=1.0
                )
                self.db.add(photo_tag)
        
        self.db.commit()
        return True
    
    def remove_photo_tag(self, photo_id: int, tag_id: int, user_id: int) -> bool:
        """移除照片标签"""
        # 检查照片是否存在且属于用户
        photo = self.db.query(Photo).filter(
            and_(Photo.id == photo_id, Photo.user_id == user_id)
        ).first()
        
        if not photo:
            return False
        
        # 删除标签关联
        photo_tag = self.db.query(PhotoTag).filter(
            and_(
                PhotoTag.photo_id == photo_id,
                PhotoTag.tag_id == tag_id,
                PhotoTag.source == "manual"
            )
        ).first()
        
        if photo_tag:
            self.db.delete(photo_tag)
            self.db.commit()
            return True
        
        return False
    
    def get_popular_tags(self, limit: int = 20) -> List[Tag]:
        """获取热门标签"""
        return self.db.query(
            Tag,
            func.count(PhotoTag.tag_id).label('usage_count')
        ).join(PhotoTag).group_by(Tag.id).order_by(
            desc('usage_count')
        ).limit(limit).all()
    
    def search_tags(self, query: str, limit: int = 10) -> List[Tag]:
        """搜索标签"""
        return self.db.query(Tag).filter(
            or_(
                Tag.name.ilike(f"%{query}%"),
                Tag.zh.ilike(f"%{query}%"),
                Tag.ja.ilike(f"%{query}%")
            )
        ).limit(limit).all()
    
    def get_or_create_tag(self, name: str, category: str = "object") -> Tag:
        """获取或创建标签"""
        tag = self.get_tag_by_name(name)
        
        if not tag:
            tag_data = TagCreate(
                name=name,
                category=category
            )
            tag = self.create_tag(tag_data)
        
        return tag
