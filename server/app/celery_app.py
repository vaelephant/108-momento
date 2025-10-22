"""
Celery 任务队列配置
"""
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# 创建Celery应用
celery_app = Celery(
    "momento",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# 更新Celery配置
# celery_app.conf.update(settings.celery_config)  # 暂时注释掉，避免配置错误

# 任务路由配置
celery_app.conf.task_routes = {
    "app.tasks.process_photo": {"queue": "photo_processing"},
    "app.tasks.generate_tags": {"queue": "ai_processing"},
    "app.tasks.generate_embedding": {"queue": "ai_processing"},
    "app.tasks.cleanup_old_tasks": {"queue": "maintenance"},
}

# 任务结果配置
celery_app.conf.result_expires = 3600  # 1小时
celery_app.conf.result_persistent = True

# 任务重试配置
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

# 监控配置
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True

# 序列化配置
celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"

# 时区配置
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# 任务执行配置
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 30 * 60  # 30分钟
celery_app.conf.task_soft_time_limit = 25 * 60  # 25分钟
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_max_tasks_per_child = 1000

# 连接池配置
celery_app.conf.broker_pool_limit = 10
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_connection_retry = True
celery_app.conf.broker_connection_max_retries = 10

# 任务结果后端配置
celery_app.conf.result_backend_transport_options = {
    'master_name': 'mymaster',
    'visibility_timeout': 3600,
}

# 信号处理器
@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Worker启动时的处理"""
    logger.info("🚀 Celery Worker 启动完成")
    logger.info(f"📊 配置信息:")
    logger.info(f"  - Broker: {settings.celery_broker_url}")
    logger.info(f"  - Backend: {settings.celery_result_backend}")
    logger.info(f"  - 时区: {settings.celery_timezone}")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Worker关闭时的处理"""
    logger.info("👋 Celery Worker 正在关闭...")


# 任务装饰器配置
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def test_task(self):
    """测试任务"""
    logger.info("🧪 执行测试任务")
    return {"status": "success", "message": "测试任务执行成功"}


# 健康检查任务
@celery_app.task
def health_check_task():
    """健康检查任务"""
    try:
        from app.database import health_check
        db_health = health_check()
        return {
            "status": "healthy",
            "database": db_health,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
