#!/usr/bin/env python3
"""
配置检查脚本
"""
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import test_connection, health_check
from app.celery_app import celery_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_environment():
    """检查环境配置"""
    logger.info("🔍 检查环境配置...")
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️  未找到 .env 文件")
        return False
    
    logger.info("✅ .env 文件存在")
    return True


def check_database_config():
    """检查数据库配置"""
    logger.info("🗄️  检查数据库配置...")
    
    try:
        # 测试数据库连接
        if test_connection():
            logger.info("✅ 数据库连接成功")
            
            # 获取健康检查信息
            health = health_check()
            logger.info(f"📊 数据库健康状态: {health['status']}")
            logger.info(f"⏱️  响应时间: {health.get('response_time_ms', 'N/A')}ms")
            
            return True
        else:
            logger.error("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库检查异常: {e}")
        return False


def check_redis_config():
    """检查Redis配置"""
    logger.info("🔴 检查Redis配置...")
    
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        logger.info("✅ Redis连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ Redis连接失败: {e}")
        return False


def check_celery_config():
    """检查Celery配置"""
    logger.info("🔄 检查Celery配置...")
    
    try:
        # 检查Celery应用配置
        logger.info(f"📊 Celery配置:")
        logger.info(f"  - Broker: {settings.celery_broker_url}")
        logger.info(f"  - Backend: {settings.celery_result_backend}")
        logger.info(f"  - 时区: {settings.celery_timezone}")
        
        # 测试Celery连接
        celery_app.control.inspect().ping()
        logger.info("✅ Celery连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ Celery连接失败: {e}")
        return False


def check_directories():
    """检查必要目录"""
    logger.info("📁 检查必要目录...")
    
    directories = [
        settings.upload_dir,
        settings.model_cache_dir,
        "logs",
        "temp"
    ]
    
    all_exist = True
    for directory in directories:
        if Path(directory).exists():
            logger.info(f"✅ 目录存在: {directory}")
        else:
            logger.warning(f"⚠️  目录不存在: {directory}")
            all_exist = False
    
    return all_exist


def check_ai_models():
    """检查AI模型配置"""
    logger.info("🤖 检查AI模型配置...")
    
    try:
        # 检查模型目录
        model_dir = Path(settings.model_cache_dir)
        if not model_dir.exists():
            logger.warning(f"⚠️  模型目录不存在: {model_dir}")
            return False
        
        logger.info(f"✅ 模型目录存在: {model_dir}")
        logger.info(f"📊 设备配置: {settings.device}")
        logger.info(f"⏱️  AI超时: {settings.ai_timeout}秒")
        
        return True
    except Exception as e:
        logger.error(f"❌ AI模型配置检查失败: {e}")
        return False


def print_config_summary():
    """打印配置摘要"""
    logger.info("📋 配置摘要:")
    logger.info(f"  - 应用名称: {settings.app_name}")
    logger.info(f"  - 版本: {settings.app_version}")
    logger.info(f"  - 调试模式: {settings.debug}")
    logger.info(f"  - 数据库: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    logger.info(f"  - Redis: {settings.redis_url}")
    logger.info(f"  - 上传目录: {settings.upload_dir}")
    logger.info(f"  - 模型目录: {settings.model_cache_dir}")
    logger.info(f"  - 设备: {settings.device}")


def main():
    """主函数"""
    logger.info("🚀 Momento AI Photo Management System 配置检查")
    logger.info("=" * 60)
    
    checks = [
        ("环境配置", check_environment),
        ("目录结构", check_directories),
        ("数据库配置", check_database_config),
        ("Redis配置", check_redis_config),
        ("Celery配置", check_celery_config),
        ("AI模型配置", check_ai_models),
    ]
    
    results = []
    for name, check_func in checks:
        logger.info(f"\n🔍 检查 {name}...")
        try:
            result = check_func()
            results.append((name, result))
            if result:
                logger.info(f"✅ {name} 检查通过")
            else:
                logger.error(f"❌ {name} 检查失败")
        except Exception as e:
            logger.error(f"❌ {name} 检查异常: {e}")
            results.append((name, False))
    
    # 打印配置摘要
    print_config_summary()
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("📊 检查结果总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  - {name}: {status}")
    
    logger.info(f"\n🎯 总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        logger.info("🎉 所有配置检查通过！系统可以启动。")
        return True
    else:
        logger.error("⚠️  部分配置检查失败，请修复后重试。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
