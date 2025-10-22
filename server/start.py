#!/usr/bin/env python3
"""
Momento AI Photo Management System 启动脚本 - 简化版本
"""
import sys
import subprocess
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from logo import MomentoLogo

# 加载环境变量
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def display_system_info():
    """显示系统配置信息"""
    logger.info("\n" + "=" * 70)
    logger.info("📋 系统配置信息")
    logger.info("=" * 70)
    
    # 应用信息
    app_name = os.getenv("APP_NAME", "Momento AI Photo Management")
    app_version = os.getenv("APP_VERSION", "1.0.0")
    logger.info(f"📱 应用名称: {app_name}")
    logger.info(f"🏷️  版本号: {app_version}")
    
    # AI配置信息
    ai_api_enabled = os.getenv("AI_API_ENABLED", "true").lower() == "true"
    ai_api_provider = os.getenv("AI_API_PROVIDER", "openai")
    
    logger.info("\n🤖 AI处理配置:")
    logger.info(f"   - AI API状态: {'✅ 已启用' if ai_api_enabled else '❌ 已禁用'}")
    logger.info(f"   - AI服务提供商: {ai_api_provider.upper()}")
    
    if ai_api_provider == "openai":
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        logger.info(f"   - OpenAI模型: {openai_model}")
        logger.info(f"   - API密钥状态: {'✅ 已配置' if openai_key else '❌ 未配置'}")
        if openai_key:
            logger.info(f"   - API密钥: {openai_key[:8]}...{openai_key[-4:]}")
    elif ai_api_provider == "qwen":
        qwen_model = os.getenv("QWEN_MODEL", "qwen-vl-plus")
        qwen_key = os.getenv("QWEN_API_KEY", "")
        logger.info(f"   - 通义千问模型: {qwen_model}")
        logger.info(f"   - API密钥状态: {'✅ 已配置' if qwen_key else '❌ 未配置'}")
    
    # AI处理参数
    ai_max_workers = os.getenv("AI_MAX_WORKERS", "4")
    ai_timeout = os.getenv("AI_TIMEOUT", "30")
    ai_retry_count = os.getenv("AI_RETRY_COUNT", "3")
    logger.info(f"   - 最大并发数: {ai_max_workers}")
    logger.info(f"   - 处理超时: {ai_timeout}秒")
    logger.info(f"   - 重试次数: {ai_retry_count}次")
    
    # 数据库信息
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        # 隐藏密码
        if "@" in database_url:
            parts = database_url.split("@")
            db_info = "@" + parts[1] if len(parts) > 1 else database_url
        else:
            db_info = database_url
        logger.info(f"\n🗄️  数据库: {db_info}")
    
    # 存储信息
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size = int(os.getenv("MAX_FILE_SIZE", "52428800")) / 1024 / 1024
    logger.info(f"\n💾 存储配置:")
    logger.info(f"   - 上传目录: {upload_dir}")
    logger.info(f"   - 最大文件大小: {max_file_size:.0f}MB")
    
    # CORS配置
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    logger.info(f"\n🌐 CORS配置:")
    for origin in cors_origins.split(","):
        logger.info(f"   - {origin.strip()}")
    
    logger.info("=" * 70 + "\n")


def main():
    """主函数"""
    # 显示Logo
    app_version = os.getenv("APP_VERSION", "1.0.0")
    MomentoLogo.print_banner(version=app_version, colored=True)
    
    # 1. 检查Python版本
    if sys.version_info < (3, 8):
        logger.error("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    logger.info(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 2. 检查依赖包
    try:
        import fastapi, uvicorn, sqlalchemy
        logger.info("✅ 核心依赖包检查通过")
    except ImportError as e:
        logger.error(f"❌ 缺少依赖包: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 3. 显示系统配置信息
    display_system_info()
    
    # 4. 创建必要目录
    logger.info("📁 创建必要目录...")
    directories = ['uploads', 'models', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    logger.info(f"✅ 目录创建完成: {', '.join(directories)}")
    
    # 5. 设置数据库
    try:
        logger.info("\n🗄️  设置数据库...")
        result = subprocess.run([sys.executable, 'setup_database.py'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ 数据库设置完成")
        else:
            logger.error(f"❌ 数据库设置失败: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 数据库设置异常: {e}")
        sys.exit(1)
    
    # 6. 启动服务器
    try:
        port = "8003"
        logger.info("\n" + "=" * 70)
        logger.info("🚀 启动FastAPI服务器...")
        logger.info("=" * 70)
        logger.info(f"📡 API服务: http://localhost:{port}")
        logger.info(f"📚 API文档: http://localhost:{port}/docs")
        logger.info(f"🎨 管理界面: http://localhost:{port}/admin")
        logger.info("")
        logger.info("💡 提示:")
        logger.info("   - 上传照片后，AI会自动分析并打标签")
        logger.info("   - 处理过程可在终端查看实时日志")
        logger.info("   - 标签可用于搜索和分类管理")
        logger.info("")
        logger.info("🛑 按 Ctrl+C 停止服务")
        logger.info("=" * 70 + "\n")
        
        # 启动uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', port,
            '--reload'
        ])
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("👋 服务已停止")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")


if __name__ == "__main__":
    main()
