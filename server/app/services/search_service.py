"""
搜索服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Tuple
from datetime import datetime

from app.models import Photo, PhotoTag, Tag
from app.schemas import PhotoSearchRequest, PhotoResponse, SimilarPhotoRequest
from app.core.exceptions import NotFoundError


class SearchService:
    """搜索服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_photos(
        self,
        user_id: int,
        search_request: PhotoSearchRequest
    ) -> Tuple[List[Photo], int]:
        """搜索照片"""
        query = self.db.query(Photo).filter(Photo.user_id == user_id)
        
        # 关键词搜索
        if search_request.query:
            query = query.filter(
                or_(
                    Photo.caption.ilike(f"%{search_request.query}%"),
                    Photo.filename.ilike(f"%{search_request.query}%")
                )
            )
        
        # 标签筛选
        if search_request.tags:
            query = query.join(PhotoTag).join(Tag).filter(
                Tag.name.in_(search_request.tags)
            )
        
        # 分类筛选
        if search_request.categories:
            query = query.join(PhotoTag).join(Tag).filter(
                Tag.category.in_(search_request.categories)
            )
        
        # 颜色筛选
        if search_request.colors:
            color_conditions = []
            for color in search_request.colors:
                color_conditions.append(
                    func.array_to_string(Photo.dominant_colors, ',').ilike(f"%{color}%")
                )
            query = query.filter(or_(*color_conditions))
        
        # 日期筛选
        if search_request.date_from:
            query = query.filter(Photo.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.filter(Photo.created_at <= search_request.date_to)
        
        # 置信度筛选
        if search_request.confidence_min is not None:
            query = query.join(PhotoTag).filter(
                PhotoTag.confidence >= search_request.confidence_min
            )
        
        if search_request.confidence_max is not None:
            query = query.join(PhotoTag).filter(
                PhotoTag.confidence <= search_request.confidence_max
            )
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        photos = query.order_by(desc(Photo.created_at)).offset(
            (search_request.page - 1) * search_request.page_size
        ).limit(search_request.page_size).all()
        
        return photos, total
    
    def find_similar_photos(
        self,
        user_id: int,
        photo_id: int,
        limit: int = 10
    ) -> List[Photo]:
        """查找相似照片"""
        from app.services.vector_service import vector_service
        
        # 获取目标照片
        target_photo = self.db.query(Photo).filter(
            and_(Photo.id == photo_id, Photo.user_id == user_id)
        ).first()
        
        if not target_photo:
            return []
        
        # 使用ChromaDB进行向量搜索
        try:
            # 这里需要从ChromaDB获取目标照片的向量
            # 暂时使用标签相似度作为备选方案
            similar_photos = self.db.query(Photo).join(PhotoTag).filter(
                and_(
                    Photo.user_id == user_id,
                    Photo.id != photo_id,
                    PhotoTag.tag_id.in_(
                        self.db.query(PhotoTag.tag_id).filter(
                            PhotoTag.photo_id == photo_id
                        )
                    )
                )
            ).distinct().limit(limit).all()
            
            return similar_photos
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    def get_tag_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """获取标签建议"""
        tags = self.db.query(Tag.name).filter(
            or_(
                Tag.name.ilike(f"%{query}%"),
                Tag.zh.ilike(f"%{query}%"),
                Tag.ja.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [tag.name for tag in tags]
    
    def get_color_suggestions(self, user_id: int) -> List[str]:
        """获取颜色建议"""
        colors = self.db.query(Photo.dominant_colors).filter(
            and_(
                Photo.user_id == user_id,
                Photo.dominant_colors.isnot(None)
            )
        ).all()
        
        # 提取所有颜色
        all_colors = []
        for color_array in colors:
            if color_array[0]:
                all_colors.extend(color_array[0])
        
        # 去重并返回
        return list(set(all_colors))
    
    def search_by_image(self, user_id: int, image_path: str, limit: int = 10) -> List[Photo]:
        """以图搜图"""
        # 这里需要实现图像特征提取和相似度计算
        # 暂时返回空列表
        return []
    
    def get_recent_photos(self, user_id: int, limit: int = 20) -> List[Photo]:
        """获取最近上传的照片"""
        return self.db.query(Photo).filter(
            Photo.user_id == user_id
        ).order_by(desc(Photo.created_at)).limit(limit).all()
    
    def get_photos_by_tag(
        self,
        user_id: int,
        tag_name: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Photo], int]:
        """根据标签获取照片"""
        query = self.db.query(Photo).join(PhotoTag).join(Tag).filter(
            and_(
                Photo.user_id == user_id,
                Tag.name == tag_name
            )
        )
        
        total = query.count()
        
        photos = query.order_by(desc(Photo.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return photos, total
