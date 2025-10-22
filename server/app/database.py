"""
数据库连接和会话管理 - 简化版本
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 元数据对象
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_connection() -> bool:
    """测试数据库连接"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ 数据库连接测试成功")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        return False


def create_tables():
    """创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建完成")
    except Exception as e:
        logger.error(f"❌ 数据库表创建失败: {e}")
        raise


def drop_tables():
    """删除所有表"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 数据库表删除完成")
    except Exception as e:
        logger.error(f"❌ 数据库表删除失败: {e}")
        raise


def health_check() -> dict:
    """数据库健康检查"""
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "数据库连接正常"}
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return {"status": "unhealthy", "error": str(e)}
