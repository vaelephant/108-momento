"""
照片管理API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Photo, User, PhotoTag, Tag
from app.schemas import (
    PhotoResponse, PhotoCreate, PhotoUpdate, PhotoListResponse,
    UploadResponse, BatchUploadResponse, PhotoStatsResponse
)
from app.core.exceptions import NotFoundError, FileError, ValidationError
from app.core.security import get_current_user_id
from app.services.photo_service import PhotoService
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_photo(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    user_id: int = Form(...),
    exif_data: Optional[str] = Form(None),  # EXIF信息（JSON字符串）
    db: Session = Depends(get_db)
):
    """
    上传单张照片并保存EXIF信息
    
    Args:
        file: 照片文件
        caption: 照片标题
        user_id: 用户ID
        exif_data: EXIF信息（JSON字符串），包含拍摄时间、地点、相机等
    """
    print(f"🚀 [FastAPI] 开始处理照片上传请求")
    print(f"👤 [FastAPI] 用户ID: {user_id}")
    print(f"📁 [FastAPI] 文件名: {file.filename}")
    print(f"📝 [FastAPI] 描述: {caption}")
    print(f"📷 [FastAPI] EXIF数据: {'✅ 已提供' if exif_data else '❌ 无'}")
    
    try:
        # 验证文件类型
        if not file.filename:
            print("❌ [FastAPI] 文件名为空")
            raise ValidationError("文件名不能为空")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        print(f"📄 [FastAPI] 文件扩展名: {file_ext}")
        
        if file_ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"]:
            print(f"❌ [FastAPI] 不支持的文件类型: {file_ext}")
            raise ValidationError(f"不支持的文件类型: {file_ext}")
        
        # 读取文件内容
        print("📖 [FastAPI] 读取文件内容...")
        file_content = await file.read()
        file_size = len(file_content)
        print(f"📊 [FastAPI] 文件大小: {file_size} bytes")
        
        # 验证文件大小
        if file_size > 50 * 1024 * 1024:  # 50MB
            print(f"❌ [FastAPI] 文件大小超过限制: {file_size} bytes")
            raise ValidationError("文件大小不能超过50MB")
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        storage_path = f"uploads/{user_id}/{unique_filename}"
        print(f"💾 [FastAPI] 存储路径: {storage_path}")
        
        # 确保目录存在
        upload_dir = os.path.dirname(storage_path)
        print(f"📁 [FastAPI] 创建目录: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        print("💾 [FastAPI] 保存文件到磁盘...")
        with open(storage_path, "wb") as f:
            f.write(file_content)
        print(f"✅ [FastAPI] 文件保存成功: {storage_path}")
        
        # 解析EXIF数据
        exif_dict = None
        taken_at = None
        location = None
        camera_info = None
        
        if exif_data:
            try:
                import json
                from dateutil import parser
                
                exif_dict = json.loads(exif_data)
                print(f"📷 [FastAPI] 解析EXIF数据成功")
                
                # 提取拍摄时间
                if exif_dict.get('dateTaken'):
                    taken_at = parser.parse(exif_dict['dateTaken'])
                    print(f"📅 [FastAPI] 拍摄时间: {taken_at}")
                
                # 提取位置信息
                if exif_dict.get('location'):
                    location = exif_dict['location']
                    print(f"📍 [FastAPI] 位置: {location}")
                
                # 提取相机信息
                if exif_dict.get('camera'):
                    camera_info = exif_dict['camera']
                    print(f"📷 [FastAPI] 相机: {camera_info}")
                    
                # 保存完整的EXIF数据到exif_data字段
                if not exif_dict.get('camera') and exif_dict.get('make'):
                    exif_dict['camera'] = camera_info
                    
            except Exception as e:
                print(f"⚠️ [FastAPI] 解析EXIF数据失败: {e}")
        
        # 创建照片记录（包含EXIF信息）
        print("💾 [FastAPI] 创建数据库记录...")
        photo_service = PhotoService(db)
        photo = photo_service.create_photo(
            user_id=user_id,
            filename=file.filename,
            storage_path=storage_path,
            file_size=file_size,
            caption=caption,
            exif_data=exif_dict  # 传递完整的EXIF数据
        )
        
        # 如果有拍摄时间，更新照片记录
        if taken_at:
            photo.taken_at = taken_at
            db.commit()
            print(f"📅 [FastAPI] 更新拍摄时间: {taken_at}")
        
        print(f"✅ [FastAPI] 数据库记录创建成功，照片ID: {photo.id}")
        
        # 使用FastAPI后台任务处理AI标签生成
        print("🤖 [FastAPI] 开始AI处理...")
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()
            
            # 添加后台任务
            background_tasks.add_task(ai_service.process_photo_simple, photo.id, storage_path)
            
            print("✅ [FastAPI] AI处理任务已启动")
        except Exception as e:
            print(f"❌ [FastAPI] AI处理失败: {e}")
        
        print(f"🎉 [FastAPI] 照片上传完成，ID: {photo.id}")
        print(f"📁 [FastAPI] 实际存储文件名: {unique_filename}")
        return UploadResponse(
            photo_id=photo.id,
            filename=unique_filename,  # 返回实际存储的UUID文件名
            file_size=file_size,
            message="上传成功"
        )
        
    except Exception as e:
        print(f"❌ [FastAPI] 上传失败: {str(e)}")
        print(f"❌ [FastAPI] 错误类型: {type(e).__name__}")
        import traceback
        print(f"❌ [FastAPI] 错误堆栈: {traceback.format_exc()}")
        raise FileError(f"上传失败: {str(e)}")


@router.post("/upload/batch", response_model=BatchUploadResponse)
async def upload_photos_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """批量上传照片"""
    success_count = 0
    failed_count = 0
    failed_files = []
    photo_ids = []
    
    for file in files:
        try:
            # 验证文件
            if not file.filename:
                failed_files.append(f"{file.filename}: 文件名不能为空")
                failed_count += 1
                continue
            
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"]:
                failed_files.append(f"{file.filename}: 不支持的文件类型")
                failed_count += 1
                continue
            
            # 读取文件内容
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > 50 * 1024 * 1024:
                failed_files.append(f"{file.filename}: 文件大小超过50MB")
                failed_count += 1
                continue
            
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            storage_path = f"uploads/{current_user_id}/{unique_filename}"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # 保存文件
            with open(storage_path, "wb") as f:
                f.write(file_content)
            
            # 创建照片记录
            photo_service = PhotoService(db)
            photo = photo_service.create_photo(
                user_id=current_user_id,
                filename=file.filename,
                storage_path=storage_path,
                file_size=file_size
            )
            
            photo_ids.append(photo.id)
            success_count += 1
            
        except Exception as e:
            failed_files.append(f"{file.filename}: {str(e)}")
            failed_count += 1
    
    return BatchUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_files=failed_files,
        photo_ids=photo_ids
    )


@router.get("/", response_model=PhotoListResponse)
async def get_photos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取照片列表"""
    photo_service = PhotoService(db)
    photos, total = photo_service.get_photos_by_user(
        user_id=current_user_id,
        page=page,
        page_size=page_size
    )
    
    return PhotoListResponse(
        photos=photos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取单张照片详情"""
    photo_service = PhotoService(db)
    photo = photo_service.get_photo_by_id(photo_id, current_user_id)
    
    if not photo:
        raise NotFoundError("照片不存在")
    
    return photo


@router.patch("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新照片信息"""
    photo_service = PhotoService(db)
    photo = photo_service.update_photo(photo_id, current_user_id, photo_update)
    
    if not photo:
        raise NotFoundError("照片不存在")
    
    return photo


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除照片"""
    photo_service = PhotoService(db)
    success = photo_service.delete_photo(photo_id, current_user_id)
    
    if not success:
        raise NotFoundError("照片不存在")
    
    return {"success": True, "message": "照片删除成功"}


@router.get("/stats/overview", response_model=PhotoStatsResponse)
async def get_photo_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取照片统计信息"""
    photo_service = PhotoService(db)
    stats = photo_service.get_user_photo_stats(current_user_id)
    
    return stats
