"""
照片服务层

功能：
- 照片CRUD操作
- 照片搜索和过滤
- 标签管理
- 统计信息

优化：
- 集成缩略图生成
- 批量操作支持
- 性能优化
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import os
import logging

from app.models import Photo, PhotoTag, Tag
from app.schemas import PhotoCreate, PhotoUpdate, PhotoResponse, PhotoStatsResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.services.thumbnail_service import ThumbnailService

logger = logging.getLogger(__name__)


class PhotoService:
    """照片服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_photo(
        self,
        user_id: int,
        filename: str,
        storage_path: str,
        file_size: int,
        caption: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        exif_data: Optional[dict] = None,
        generate_thumbnails: bool = True
    ) -> Photo:
        """
        创建照片记录
        
        Args:
            user_id: 用户ID
            filename: 文件名
            storage_path: 存储路径
            file_size: 文件大小
            caption: 标题
            width: 宽度
            height: 高度
            exif_data: EXIF数据
            generate_thumbnails: 是否生成缩略图
            
        Returns:
            创建的Photo对象
        """
        # 创建照片记录
        photo = Photo(
            user_id=user_id,
            filename=filename,
            storage_path=storage_path,
            file_size=file_size,
            caption=caption,
            width=width,
            height=height,
            exif_data=exif_data
        )
        
        # 生成缩略图
        if generate_thumbnails and os.path.exists(storage_path):
            try:
                logger.info(f"📸 开始生成缩略图: {filename}")
                thumbnails = ThumbnailService.generate_thumbnails(storage_path)
                
                # 将缩略图路径存储到数据库（可选）
                # 这里我们可以将路径存到exif_data中
                if photo.exif_data is None:
                    photo.exif_data = {}
                photo.exif_data['thumbnails'] = {
                    'small': os.path.basename(thumbnails.get('small', '')),
                    'medium': os.path.basename(thumbnails.get('medium', '')),
                    'large': os.path.basename(thumbnails.get('large', ''))
                }
                
                logger.info(f"✅ 缩略图生成成功: {filename}")
            except Exception as e:
                logger.error(f"❌ 缩略图生成失败: {e}")
                # 失败不影响照片上传
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        return photo
    
    def get_photo_by_id(self, photo_id: int, user_id: int) -> Optional[Photo]:
        """根据ID获取照片"""
        return self.db.query(Photo).filter(
            and_(Photo.id == photo_id, Photo.user_id == user_id)
        ).first()
    
    def get_photos_by_user(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Photo], int]:
        """获取用户的照片列表"""
        query = self.db.query(Photo).filter(Photo.user_id == user_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        photos = query.order_by(desc(Photo.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return photos, total
    
    def update_photo(
        self,
        photo_id: int,
        user_id: int,
        photo_update: PhotoUpdate
    ) -> Optional[Photo]:
        """更新照片信息"""
        photo = self.get_photo_by_id(photo_id, user_id)
        
        if not photo:
            return None
        
        # 更新字段
        if photo_update.caption is not None:
            photo.caption = photo_update.caption
        
        if photo_update.dominant_colors is not None:
            photo.dominant_colors = photo_update.dominant_colors
        
        photo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(photo)
        
        return photo
    
    def delete_photo(self, photo_id: int, user_id: int) -> bool:
        """删除照片"""
        photo = self.get_photo_by_id(photo_id, user_id)
        
        if not photo:
            return False
        
        # 删除物理文件
        try:
            if os.path.exists(photo.storage_path):
                os.remove(photo.storage_path)
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        # 删除数据库记录
        self.db.delete(photo)
        self.db.commit()
        
        return True
    
    def get_user_photo_stats(self, user_id: int) -> PhotoStatsResponse:
        """获取用户照片统计信息"""
        # 总照片数
        total_photos = self.db.query(Photo).filter(Photo.user_id == user_id).count()
        
        # 总文件大小
        total_size = self.db.query(func.sum(Photo.file_size)).filter(
            Photo.user_id == user_id
        ).scalar() or 0
        
        # 标签统计
        tag_counts = self.db.query(
            Tag.name,
            func.count(PhotoTag.tag_id).label('count')
        ).join(PhotoTag).join(Photo).filter(
            Photo.user_id == user_id
        ).group_by(Tag.name).all()
        
        tag_counts_dict = {tag.name: count for tag, count in tag_counts}
        
        # 分类统计
        category_counts = self.db.query(
            Tag.category,
            func.count(PhotoTag.tag_id).label('count')
        ).join(PhotoTag).join(Photo).filter(
            Photo.user_id == user_id
        ).group_by(Tag.category).all()
        
        category_counts_dict = {category: count for category, count in category_counts}
        
        # 最近上传的照片
        recent_photos = self.db.query(Photo).filter(
            Photo.user_id == user_id
        ).order_by(desc(Photo.created_at)).limit(5).all()
        
        return PhotoStatsResponse(
            total_photos=total_photos,
            total_size=total_size,
            tag_counts=tag_counts_dict,
            category_counts=category_counts_dict,
            recent_uploads=recent_photos
        )
    
    def add_photo_tags(self, photo_id: int, tag_ids: List[int], user_id: int) -> bool:
        """为照片添加标签"""
        photo = self.get_photo_by_id(photo_id, user_id)
        
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
        photo = self.get_photo_by_id(photo_id, user_id)
        
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
    
    def update_photo_ai_data(
        self,
        photo_id: int,
        caption: Optional[str] = None,
        tags: Optional[List[dict]] = None,
        category: Optional[str] = None,
        dominant_colors: Optional[str] = None,
        mood: Optional[str] = None
    ) -> bool:
        """更新照片的AI分析结果"""
        try:
            # 不需要user_id，直接通过photo_id查询
            photo = self.db.query(Photo).filter(Photo.id == photo_id).first()
            
            if not photo:
                return False
            
            # 更新字段
            if caption:
                photo.caption = caption
            
            if dominant_colors:
                photo.dominant_colors = dominant_colors
            
            # 如果有标签，创建或关联标签
            if tags:
                for tag_data in tags:
                    tag_name = tag_data.get('name') if isinstance(tag_data, dict) else str(tag_data)
                    confidence = tag_data.get('confidence', 0.8) if isinstance(tag_data, dict) else 0.8
                    
                    # 查找或创建标签
                    tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name, category=category or 'other')
                        self.db.add(tag)
                        self.db.flush()  # 获取tag.id
                    
                    # 检查是否已存在关联
                    existing = self.db.query(PhotoTag).filter(
                        and_(
                            PhotoTag.photo_id == photo_id,
                            PhotoTag.tag_id == tag.id,
                            PhotoTag.source == "ai"
                        )
                    ).first()
                    
                    if not existing:
                        photo_tag = PhotoTag(
                            photo_id=photo_id,
                            tag_id=tag.id,
                            source="ai",
                            confidence=float(confidence)
                        )
                        self.db.add(photo_tag)
            
            photo.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"更新AI数据失败: {e}")
            return False
