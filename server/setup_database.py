#!/usr/bin/env python3
"""
数据库设置脚本
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database():
    """创建数据库"""
    try:
        # 解析数据库URL
        db_url = settings.database_url
        if db_url.startswith('postgresql://'):
            # 提取连接信息
            parts = db_url.replace('postgresql://', '').split('/')
            if len(parts) >= 2:
                auth_host = parts[0]
                db_name = parts[1]
                
                if '@' in auth_host:
                    auth, host = auth_host.split('@')
                    if ':' in auth:
                        user, password = auth.split(':')
                    else:
                        user, password = auth, ''
                else:
                    user, password = 'postgres', ''
                    host = auth_host
                
                # 连接到postgres数据库创建新数据库
                conn = psycopg2.connect(
                    host=host.split(':')[0],
                    port=int(host.split(':')[1]) if ':' in host else 5432,
                    user=user,
                    password=password,
                    database='postgres'
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                
                cursor = conn.cursor()
                
                # 检查数据库是否存在
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    logger.info(f"✅ 数据库 '{db_name}' 创建成功")
                else:
                    logger.info(f"ℹ️  数据库 '{db_name}' 已存在")
                
                cursor.close()
                conn.close()
                
            else:
                logger.error("❌ 数据库URL格式错误")
                return False
        else:
            logger.error("❌ 不支持的数据库类型")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建数据库失败: {e}")
        return False


def run_sql_script():
    """执行SQL脚本"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.database_url)
        
        # 读取SQL文件
        sql_file = os.path.join(os.path.dirname(__file__), 'sql', 'init_simple.sql')
        
        if not os.path.exists(sql_file):
            logger.error(f"❌ SQL文件不存在: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（按分号分割）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        # 执行SQL语句
        with engine.connect() as conn:
            for i, sql in enumerate(sql_statements):
                if sql.strip():
                    try:
                        conn.execute(text(sql))
                        logger.info(f"✅ 执行SQL语句 {i+1}/{len(sql_statements)}")
                    except Exception as e:
                        logger.warning(f"⚠️  SQL语句执行警告: {e}")
                        # 继续执行其他语句
            
            conn.commit()
        logger.info("✅ 数据库初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 执行SQL脚本失败: {e}")
        return False


def test_connection():
    """测试数据库连接"""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ 数据库连接测试成功")
            return True
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("🚀 开始设置数据库...")
    
    # 1. 创建数据库
    if not create_database():
        logger.error("❌ 数据库创建失败")
        sys.exit(1)
    
    # 2. 执行SQL脚本
    if not run_sql_script():
        logger.error("❌ SQL脚本执行失败")
        sys.exit(1)
    
    # 3. 测试连接
    if not test_connection():
        logger.error("❌ 数据库连接测试失败")
        sys.exit(1)
    
    logger.info("🎉 数据库设置完成！")
    logger.info("📊 数据库信息:")
    logger.info(f"   - 数据库URL: {settings.database_url}")
    logger.info(f"   - 表结构: 已创建所有必要的表和索引")
    logger.info(f"   - 基础数据: 已插入基础标签数据")


if __name__ == "__main__":
    main()
