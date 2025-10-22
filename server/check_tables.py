#!/usr/bin/env python3
"""
检查数据库表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import engine
from sqlalchemy import text

def check_tables():
    """检查数据库表"""
    print("🔍 检查数据库表...")
    print(f"数据库URL: {settings.database_url}")
    
    try:
        with engine.connect() as conn:
            # 查询所有表
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            
            if tables:
                print(f"✅ 找到 {len(tables)} 个表:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("❌ 没有找到任何表")
                
            # 检查pgvector扩展
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
            if result.fetchone():
                print("✅ pgvector扩展已安装")
            else:
                print("⚠️  pgvector扩展未安装")
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    check_tables()
