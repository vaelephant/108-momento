"""
相册服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime

from app.models import Album, AlbumPhoto, Photo
from app.schemas import AlbumCreate, AlbumUpdate, AlbumResponse
from app.core.exceptions import NotFoundError, ValidationError


class AlbumService:
    """相册服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_albums_by_user(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[Album]:
        """获取用户的相册列表"""
        return self.db.query(Album).filter(
            Album.user_id == user_id
        ).order_by(desc(Album.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
    
    def get_album_by_id(self, album_id: int, user_id: int) -> Optional[Album]:
        """根据ID获取相册"""
        return self.db.query(Album).filter(
            and_(Album.id == album_id, Album.user_id == user_id)
        ).first()
    
    def create_album(self, user_id: int, album_data: AlbumCreate) -> Album:
        """创建相册"""
        album = Album(
            user_id=user_id,
            name=album_data.name,
            description=album_data.description,
            cover_photo_id=album_data.cover_photo_id,
            is_public=album_data.is_public
        )
        
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        
        return album
    
    def update_album(
        self,
        album_id: int,
        user_id: int,
        album_update: AlbumUpdate
    ) -> Optional[Album]:
        """更新相册"""
        album = self.get_album_by_id(album_id, user_id)
        
        if not album:
            return None
        
        # 更新字段
        if album_update.name is not None:
            album.name = album_update.name
        
        if album_update.description is not None:
            album.description = album_update.description
        
        if album_update.is_public is not None:
            album.is_public = album_update.is_public
        
        if album_update.cover_photo_id is not None:
            # 验证封面照片是否属于用户
            if album_update.cover_photo_id:
                photo = self.db.query(Photo).filter(
                    and_(
                        Photo.id == album_update.cover_photo_id,
                        Photo.user_id == user_id
                    )
                ).first()
                
                if not photo:
                    raise ValidationError("封面照片不存在")
            
            album.cover_photo_id = album_update.cover_photo_id
        
        album.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(album)
        
        return album
    
    def delete_album(self, album_id: int, user_id: int) -> bool:
        """删除相册"""
        album = self.get_album_by_id(album_id, user_id)
        
        if not album:
            return False
        
        self.db.delete(album)
        self.db.commit()
        
        return True
    
    def add_photos_to_album(
        self,
        album_id: int,
        photo_ids: List[int],
        user_id: int
    ) -> bool:
        """向相册添加照片"""
        album = self.get_album_by_id(album_id, user_id)
        
        if not album:
            return False
        
        # 验证照片是否属于用户
        photos = self.db.query(Photo).filter(
            and_(
                Photo.id.in_(photo_ids),
                Photo.user_id == user_id
            )
        ).all()
        
        if len(photos) != len(photo_ids):
            raise ValidationError("部分照片不存在")
        
        # 添加照片到相册
        for photo in photos:
            # 检查是否已在相册中
            existing = self.db.query(AlbumPhoto).filter(
                and_(
                    AlbumPhoto.album_id == album_id,
                    AlbumPhoto.photo_id == photo.id
                )
            ).first()
            
            if not existing:
                album_photo = AlbumPhoto(
                    album_id=album_id,
                    photo_id=photo.id
                )
                self.db.add(album_photo)
        
        self.db.commit()
        return True
    
    def remove_photo_from_album(
        self,
        album_id: int,
        photo_id: int,
        user_id: int
    ) -> bool:
        """从相册移除照片"""
        album = self.get_album_by_id(album_id, user_id)
        
        if not album:
            return False
        
        # 删除相册照片关联
        album_photo = self.db.query(AlbumPhoto).filter(
            and_(
                AlbumPhoto.album_id == album_id,
                AlbumPhoto.photo_id == photo_id
            )
        ).first()
        
        if album_photo:
            self.db.delete(album_photo)
            self.db.commit()
            return True
        
        return False
    
    def get_album_photos(
        self,
        album_id: int,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[Photo]:
        """获取相册中的照片"""
        return self.db.query(Photo).join(AlbumPhoto).filter(
            and_(
                AlbumPhoto.album_id == album_id,
                Photo.user_id == user_id
            )
        ).order_by(AlbumPhoto.sort_order, desc(AlbumPhoto.added_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
    
    def get_album_photo_count(self, album_id: int, user_id: int) -> int:
        """获取相册照片数量"""
        return self.db.query(AlbumPhoto).join(Album).filter(
            and_(
                AlbumPhoto.album_id == album_id,
                Album.user_id == user_id
            )
        ).count()
