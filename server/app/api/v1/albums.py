"""
相册管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Album, AlbumPhoto
from app.schemas import AlbumResponse, AlbumCreate, AlbumUpdate
from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import get_current_user_id
from app.services.album_service import AlbumService

router = APIRouter()


@router.get("/", response_model=List[AlbumResponse])
async def get_albums(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取相册列表"""
    album_service = AlbumService(db)
    albums = album_service.get_albums_by_user(
        user_id=current_user_id,
        page=page,
        page_size=page_size
    )
    return albums


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取相册详情"""
    album_service = AlbumService(db)
    album = album_service.get_album_by_id(album_id, current_user_id)
    
    if not album:
        raise NotFoundError("相册不存在")
    
    return album


@router.post("/", response_model=AlbumResponse)
async def create_album(
    album_data: AlbumCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建相册"""
    album_service = AlbumService(db)
    album = album_service.create_album(current_user_id, album_data)
    return album


@router.patch("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    album_update: AlbumUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新相册"""
    album_service = AlbumService(db)
    album = album_service.update_album(album_id, current_user_id, album_update)
    
    if not album:
        raise NotFoundError("相册不存在")
    
    return album


@router.delete("/{album_id}")
async def delete_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除相册"""
    album_service = AlbumService(db)
    success = album_service.delete_album(album_id, current_user_id)
    
    if not success:
        raise NotFoundError("相册不存在")
    
    return {"success": True, "message": "相册删除成功"}


@router.post("/{album_id}/photos")
async def add_photos_to_album(
    album_id: int,
    photo_ids: List[int],
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """向相册添加照片"""
    album_service = AlbumService(db)
    success = album_service.add_photos_to_album(
        album_id, photo_ids, current_user_id
    )
    
    if not success:
        raise NotFoundError("相册不存在")
    
    return {"success": True, "message": "照片添加成功"}


@router.delete("/{album_id}/photos/{photo_id}")
async def remove_photo_from_album(
    album_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """从相册移除照片"""
    album_service = AlbumService(db)
    success = album_service.remove_photo_from_album(
        album_id, photo_id, current_user_id
    )
    
    if not success:
        raise NotFoundError("相册或照片不存在")
    
    return {"success": True, "message": "照片移除成功"}
