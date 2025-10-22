"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class LanguageEnum(str, Enum):
    """支持的语言"""
    ZH = "zh"
    EN = "en"
    JA = "ja"


class PrivacyLevelEnum(str, Enum):
    """隐私级别"""
    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"


class TagCategoryEnum(str, Enum):
    """标签分类"""
    OBJECT = "object"
    SCENE = "scene"
    ACTION = "action"
    BRAND = "brand"
    COLOR = "color"
    STYLE = "style"
    EMOTION = "emotion"
    PERSON = "person"


class TagSourceEnum(str, Enum):
    """标签来源"""
    RAM = "ram"
    CLIP = "clip"
    MANUAL = "manual"
    DETECTOR = "detector"


# 基础响应模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    default_language: Optional[LanguageEnum] = None
    auto_tagging: Optional[bool] = None
    privacy_level: Optional[PrivacyLevelEnum] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    default_language: str
    auto_tagging: bool
    privacy_level: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 标签相关模型
class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., max_length=100)
    zh: Optional[str] = Field(None, max_length=100)
    ja: Optional[str] = Field(None, max_length=100)
    category: TagCategoryEnum
    description: Optional[str] = None


class TagCreate(TagBase):
    """标签创建模型"""
    pass


class TagResponse(TagBase):
    """标签响应模型"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 照片相关模型
class PhotoBase(BaseModel):
    """照片基础模型"""
    caption: Optional[str] = None
    dominant_colors: Optional[List[str]] = None


class PhotoCreate(PhotoBase):
    """照片创建模型"""
    filename: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    exif_data: Optional[Dict[str, Any]] = None


class PhotoUpdate(PhotoBase):
    """照片更新模型"""
    caption: Optional[str] = None
    dominant_colors: Optional[List[str]] = None


class PhotoResponse(PhotoBase):
    """照片响应模型"""
    id: int
    user_id: int
    storage_path: str
    filename: str
    file_size: int
    width: Optional[int]
    height: Optional[int]
    exif_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    tags: List['PhotoTagResponse'] = []
    
    model_config = ConfigDict(from_attributes=True)


class PhotoListResponse(BaseModel):
    """照片列表响应模型"""
    photos: List[PhotoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# 照片标签相关模型
class PhotoTagBase(BaseModel):
    """照片标签基础模型"""
    tag_id: int
    source: TagSourceEnum
    confidence: float = Field(..., ge=0, le=1)
    bbox: Optional[Dict[str, Any]] = None


class PhotoTagCreate(PhotoTagBase):
    """照片标签创建模型"""
    pass


class PhotoTagUpdate(BaseModel):
    """照片标签更新模型"""
    confidence: Optional[float] = Field(None, ge=0, le=1)
    bbox: Optional[Dict[str, Any]] = None


class PhotoTagResponse(PhotoTagBase):
    """照片标签响应模型"""
    photo_id: int
    created_at: datetime
    tag: TagResponse
    
    model_config = ConfigDict(from_attributes=True)


# 相册相关模型
class AlbumBase(BaseModel):
    """相册基础模型"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    is_public: bool = False


class AlbumCreate(AlbumBase):
    """相册创建模型"""
    cover_photo_id: Optional[int] = None


class AlbumUpdate(AlbumBase):
    """相册更新模型"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_photo_id: Optional[int] = None


class AlbumResponse(AlbumBase):
    """相册响应模型"""
    id: int
    user_id: int
    cover_photo_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    photo_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)


# 搜索和筛选模型
class PhotoSearchRequest(BaseModel):
    """照片搜索请求模型"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[TagCategoryEnum]] = None
    colors: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    confidence_min: Optional[float] = Field(None, ge=0, le=1)
    confidence_max: Optional[float] = Field(None, ge=0, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SimilarPhotoRequest(BaseModel):
    """相似照片搜索请求模型"""
    photo_id: int
    limit: int = Field(10, ge=1, le=50)


# 上传相关模型
class UploadResponse(BaseModel):
    """上传响应模型"""
    photo_id: int
    filename: str
    file_size: int
    message: str = "上传成功"


class BatchUploadResponse(BaseModel):
    """批量上传响应模型"""
    success_count: int
    failed_count: int
    failed_files: List[str] = []
    photo_ids: List[int] = []


# 统计相关模型
class PhotoStatsResponse(BaseModel):
    """照片统计响应模型"""
    total_photos: int
    total_size: int
    tag_counts: Dict[str, int]
    category_counts: Dict[str, int]
    recent_uploads: List[PhotoResponse]


# 更新前向引用
PhotoResponse.model_rebuild()
PhotoTagResponse.model_rebuild()
