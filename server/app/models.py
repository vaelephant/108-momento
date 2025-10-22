"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# from pgvector.sqlalchemy import Vector  # 使用ChromaDB替代
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 用户偏好设置
    default_language = Column(String(10), default="zh")
    auto_tagging = Column(Boolean, default=True)
    privacy_level = Column(String(20), default="private")
    
    # 关系
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    albums = relationship("Album", back_populates="user", cascade="all, delete-orphan")


class Photo(Base):
    """照片表"""
    __tablename__ = "photos"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger)
    width = Column(Integer)
    height = Column(Integer)
    exif_data = Column(JSONB)
    caption = Column(Text)
    dominant_colors = Column(Text)  # 改为TEXT，存储逗号分隔或JSON字符串
    # embedding = Column(Vector(768))  # 使用ChromaDB替代pgvector
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 新增字段 - 照片分类优化
    taken_at = Column(DateTime(timezone=True))  # 实际拍摄时间（从EXIF读取）
    location = Column(String(200))  # 拍摄地点
    location_lat = Column(Float)  # 纬度
    location_lng = Column(Float)  # 经度
    ai_status = Column(String(20), default='pending')  # AI处理状态: pending/processing/completed/failed
    ai_error = Column(Text)  # AI处理错误信息
    
    # 关系
    user = relationship("User", back_populates="photos")
    tags = relationship("PhotoTag", back_populates="photo", cascade="all, delete-orphan")
    album_photos = relationship("AlbumPhoto", back_populates="photo", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_photos_created_at', 'created_at'),
        Index('idx_photos_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_photos_taken_at', 'taken_at'),
        Index('idx_photos_ai_status', 'ai_status'),
    )


class Tag(Base):
    """标签表（归一化到标准词表）"""
    __tablename__ = "tags"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # 统一英文key，如 "cat"
    zh = Column(String(100))  # 中文显示
    ja = Column(String(100))  # 日文显示
    category = Column(String(50), index=True)  # object/scene/action/brand/color/style...
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 新增字段 - 标签优化
    use_count = Column(Integer, default=0, index=True)  # 标签使用次数统计
    parent_tag_id = Column(BigInteger, ForeignKey("tags.id"))  # 父标签ID（支持层级）
    
    # 关系
    photo_tags = relationship("PhotoTag", back_populates="tag", cascade="all, delete-orphan")
    parent_tag = relationship("Tag", remote_side=[id], backref="child_tags")
    
    # 索引
    __table_args__ = (
        Index('idx_tags_category', 'category'),
        Index('idx_tags_name_category', 'name', 'category'),
        Index('idx_tags_use_count', 'use_count'),
    )


class PhotoTag(Base):
    """照片-标签关联表（多对多，含置信度、来源）"""
    __tablename__ = "photo_tags"
    
    photo_id = Column(BigInteger, ForeignKey("photos.id"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tags.id"), primary_key=True)
    source = Column(String(50), primary_key=True)  # 'ai' | 'manual' (简化后只用这两个值)
    confidence = Column(Float, nullable=False)  # 0-1之间的置信度
    bbox = Column(JSONB)  # 可选：检测框 [x,y,w,h]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    photo = relationship("Photo", back_populates="tags")
    tag = relationship("Tag", back_populates="photo_tags")
    
    # 索引
    __table_args__ = (
        Index('idx_photo_tags_confidence', 'confidence'),
        Index('idx_photo_tags_source', 'source'),
    )


class TagAlias(Base):
    """标签别名/同义词映射表"""
    __tablename__ = "tag_alias"
    
    alias = Column(String(100), primary_key=True)  # 'kitty'
    canonical = Column(String(100), nullable=False)  # 'cat'
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Album(Base):
    """相册表"""
    __tablename__ = "albums"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    cover_photo_id = Column(BigInteger, ForeignKey("photos.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="albums")
    cover_photo = relationship("Photo", foreign_keys=[cover_photo_id])
    album_photos = relationship("AlbumPhoto", back_populates="album", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_albums_user_id', 'user_id'),
        Index('idx_albums_created_at', 'created_at'),
    )


class AlbumPhoto(Base):
    """相册-照片关联表"""
    __tablename__ = "album_photos"
    
    album_id = Column(BigInteger, ForeignKey("albums.id"), primary_key=True)
    photo_id = Column(BigInteger, ForeignKey("photos.id"), primary_key=True)
    sort_order = Column(Integer, default=0)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    album = relationship("Album", back_populates="album_photos")
    photo = relationship("Photo", back_populates="album_photos")
    
    # 索引
    __table_args__ = (
        Index('idx_album_photos_sort_order', 'album_id', 'sort_order'),
    )


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"
    
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    default_language = Column(String(10), default="zh")
    auto_tagging = Column(Boolean, default=True)
    privacy_level = Column(String(20), default="private")
    theme = Column(String(20), default="light")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User")
