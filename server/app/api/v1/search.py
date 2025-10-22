"""
搜索功能API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    PhotoSearchRequest, PhotoListResponse, SimilarPhotoRequest,
    PhotoResponse
)
from app.core.security import get_current_user_id
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/photos", response_model=PhotoListResponse)
async def search_photos(
    query: Optional[str] = Query(None, description="搜索关键词"),
    tags: Optional[str] = Query(None, description="标签筛选，逗号分隔"),
    categories: Optional[str] = Query(None, description="分类筛选，逗号分隔"),
    colors: Optional[str] = Query(None, description="颜色筛选，逗号分隔"),
    date_from: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    confidence_min: Optional[float] = Query(None, ge=0, le=1, description="最小置信度"),
    confidence_max: Optional[float] = Query(None, ge=0, le=1, description="最大置信度"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """搜索照片"""
    search_service = SearchService(db)
    
    # 构建搜索请求
    search_request = PhotoSearchRequest(
        query=query,
        tags=tags.split(",") if tags else None,
        categories=categories.split(",") if categories else None,
        colors=colors.split(",") if colors else None,
        date_from=date_from,
        date_to=date_to,
        confidence_min=confidence_min,
        confidence_max=confidence_max,
        page=page,
        page_size=page_size
    )
    
    # 执行搜索
    photos, total = search_service.search_photos(current_user_id, search_request)
    
    return PhotoListResponse(
        photos=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/similar", response_model=List[PhotoResponse])
async def find_similar_photos(
    similar_request: SimilarPhotoRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """查找相似照片"""
    search_service = SearchService(db)
    similar_photos = search_service.find_similar_photos(
        current_user_id, similar_request.photo_id, similar_request.limit
    )
    return similar_photos


@router.get("/tags/suggestions")
async def get_tag_suggestions(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取标签建议"""
    search_service = SearchService(db)
    suggestions = search_service.get_tag_suggestions(query, limit)
    return {
        "success": True,
        "data": suggestions
    }


@router.get("/colors")
async def get_color_suggestions(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取颜色建议"""
    search_service = SearchService(db)
    colors = search_service.get_color_suggestions(current_user_id)
    return {
        "success": True,
        "data": colors
    }
