#!/usr/bin/env python3
"""
Momento AI Photo Management System 启动脚本 - 简化版本
"""
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def main():
    """主函数"""
    logger.info("🎯 Momento AI Photo Management System")
    logger.info("=" * 50)
    
    # 1. 检查Python版本
    if sys.version_info < (3, 8):
        logger.error("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    logger.info(f"✅ Python版本: {sys.version}")
    
    # 2. 检查依赖包
    try:
        import fastapi, uvicorn, sqlalchemy
        logger.info("✅ 核心依赖包检查通过")
    except ImportError as e:
        logger.error(f"❌ 缺少依赖包: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 3. 创建必要目录
    directories = ['uploads', 'models', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"📁 创建目录: {directory}")
    
    # 4. 设置数据库
    try:
        logger.info("🗄️  设置数据库...")
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
    
    # 5. 启动服务器
    try:
        port = "8003"
        logger.info("🚀 启动FastAPI服务器...")
        logger.info(f"📡 API服务: http://localhost:{port}")
        logger.info(f"📚 API文档: http://localhost:{port}/docs")
        logger.info("🛑 按 Ctrl+C 停止服务")
        
        # 启动uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', port,
            '--reload'
        ])
        
    except KeyboardInterrupt:
        logger.info("👋 服务已停止")
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")


if __name__ == "__main__":
    main()
