"""
标签管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Tag, PhotoTag
from app.schemas import TagResponse, TagCreate, PhotoTagResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import get_current_user_id
from app.services.tag_service import TagService

router = APIRouter()


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    tag_service = TagService(db)
    tags = tag_service.get_tags(
        category=category,
        search=search,
        page=page,
        page_size=page_size
    )
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """获取单个标签详情"""
    tag_service = TagService(db)
    tag = tag_service.get_tag_by_id(tag_id)
    
    if not tag:
        raise NotFoundError("标签不存在")
    
    return tag


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    """创建新标签"""
    tag_service = TagService(db)
    tag = tag_service.create_tag(tag_data)
    return tag


@router.get("/photo/{photo_id}", response_model=List[PhotoTagResponse])
async def get_photo_tags(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取照片的标签"""
    tag_service = TagService(db)
    photo_tags = tag_service.get_photo_tags(photo_id, current_user_id)
    return photo_tags


@router.post("/photo/{photo_id}/tags")
async def add_photo_tags(
    photo_id: int,
    tag_ids: List[int],
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """为照片添加标签"""
    tag_service = TagService(db)
    success = tag_service.add_photo_tags(photo_id, tag_ids, current_user_id)
    
    if not success:
        raise NotFoundError("照片不存在")
    
    return {"success": True, "message": "标签添加成功"}


@router.delete("/photo/{photo_id}/tags/{tag_id}")
async def remove_photo_tag(
    photo_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """移除照片标签"""
    tag_service = TagService(db)
    success = tag_service.remove_photo_tag(photo_id, tag_id, current_user_id)
    
    if not success:
        raise NotFoundError("照片或标签不存在")
    
    return {"success": True, "message": "标签移除成功"}


@router.get("/popular/", response_model=List[TagResponse])
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取热门标签"""
    tag_service = TagService(db)
    tags = tag_service.get_popular_tags(limit)
    return tags
