"""
Celery 任务定义
"""
from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.services.ai_service import AIService
from app.services.photo_service import PhotoService
from app.services.tag_service import TagService
from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True)
def process_photo(self, photo_id: int, image_path: str):
    """处理照片的异步任务"""
    try:
        logger.info(f"开始处理照片 {photo_id}")
        
        # 更新任务状态
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "开始处理"}
        )
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化AI服务
            ai_service = AIService()
            
            # 更新状态
            self.update_state(
                state="PROGRESS",
                meta={"current": 20, "total": 100, "status": "AI模型加载中"}
            )
            
            # 处理图像
            result = ai_service._process_photo_sync(photo_id, image_path)
            
            # 更新状态
            self.update_state(
                state="PROGRESS",
                meta={"current": 80, "total": 100, "status": "保存结果"}
            )
            
            # 这里应该保存结果到数据库
            # 暂时跳过
            
            # 完成
            self.update_state(
                state="SUCCESS",
                meta={"current": 100, "total": 100, "status": "处理完成"}
            )
            
            logger.info(f"照片 {photo_id} 处理完成")
            
            return {
                "photo_id": photo_id,
                "status": "success",
                "result": result
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"照片处理失败: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task
def generate_tags(photo_id: int, image_path: str):
    """生成标签的异步任务"""
    try:
        logger.info(f"开始为照片 {photo_id} 生成标签")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化服务
            ai_service = AIService()
            tag_service = TagService(db)
            
            # 加载图像
            image = ai_service._load_image(image_path)
            if image is None:
                raise Exception("图像加载失败")
            
            # 生成标签
            tags = ai_service._generate_tags(image)
            
            # 保存标签到数据库
            for tag_data in tags:
                # 获取或创建标签
                tag = tag_service.get_or_create_tag(
                    name=tag_data["name"],
                    category="object"
                )
                
                # 创建照片标签关联
                # 这里需要实现PhotoTag的创建逻辑
            
            logger.info(f"照片 {photo_id} 标签生成完成")
            
            return {
                "photo_id": photo_id,
                "tags": tags,
                "status": "success"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"标签生成失败: {e}")
        raise


@celery_app.task
def generate_embedding(photo_id: int, image_path: str):
    """生成嵌入向量的异步任务"""
    try:
        logger.info(f"开始为照片 {photo_id} 生成嵌入向量")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 初始化AI服务
            ai_service = AIService()
            
            # 加载图像
            image = ai_service._load_image(image_path)
            if image is None:
                raise Exception("图像加载失败")
            
            # 生成嵌入向量
            embedding = ai_service._generate_embedding(image)
            
            if embedding:
                # 更新照片的嵌入向量
                photo_service = PhotoService(db)
                # 这里需要实现嵌入向量的保存逻辑
            
            logger.info(f"照片 {photo_id} 嵌入向量生成完成")
            
            return {
                "photo_id": photo_id,
                "embedding_length": len(embedding) if embedding else 0,
                "status": "success"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"嵌入向量生成失败: {e}")
        raise


@celery_app.task
def cleanup_old_tasks():
    """清理旧任务的定时任务"""
    try:
        logger.info("开始清理旧任务")
        
        # 这里可以实现任务清理逻辑
        # 比如删除超过一定时间的任务结果
        
        logger.info("旧任务清理完成")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"任务清理失败: {e}")
        raise
