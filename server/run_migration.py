#!/usr/bin/env python3
"""
数据库迁移执行脚本
用途：执行表结构优化迁移
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_migration():
    """执行数据库迁移"""
    
    # 获取数据库连接
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ 错误: 未找到 DATABASE_URL 环境变量")
        print("请确保 .env 文件中配置了 DATABASE_URL")
        sys.exit(1)
    
    print("=" * 60)
    print("📊 数据库优化迁移工具")
    print("=" * 60)
    print(f"\n📡 连接数据库...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    try:
        # 创建数据库引擎
        engine = create_engine(database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ 数据库连接成功")
            print(f"   版本: {version.split(',')[0]}\n")
        
        # 读取迁移SQL文件
        sql_file = os.path.join(os.path.dirname(__file__), 'sql', 'migration_optimize_for_classification.sql')
        
        if not os.path.exists(sql_file):
            print(f"❌ 错误: 找不到迁移文件")
            print(f"   路径: {sql_file}")
            sys.exit(1)
        
        print(f"📄 读取迁移脚本...")
        print(f"   文件: {sql_file}\n")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 询问用户确认
        print("⚠️  准备执行数据库迁移")
        print("\n将要执行的操作：")
        print("  1. 修改 photos 表（添加字段、修改类型）")
        print("  2. 修改 tags 表（添加统计字段）")
        print("  3. 优化 photo_tags 表（统一source值）")
        print("  4. 创建全文搜索索引")
        print("  5. 创建统计视图和触发器")
        print("  6. 创建搜索辅助函数\n")
        
        response = input("确认执行迁移？(yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ 迁移已取消")
            sys.exit(0)
        
        # 执行迁移
        print("\n🚀 开始执行迁移...\n")
        
        with engine.begin() as conn:
            # 执行SQL
            conn.execute(text(migration_sql))
            print("✅ 迁移执行成功！\n")
        
        # 验证迁移结果
        print("🔍 验证迁移结果...\n")
        
        with engine.connect() as conn:
            # 检查新增字段
            checks = [
                ("photos表 - taken_at字段", 
                 "SELECT column_name FROM information_schema.columns WHERE table_name='photos' AND column_name='taken_at'"),
                ("photos表 - location字段", 
                 "SELECT column_name FROM information_schema.columns WHERE table_name='photos' AND column_name='location'"),
                ("photos表 - ai_status字段", 
                 "SELECT column_name FROM information_schema.columns WHERE table_name='photos' AND column_name='ai_status'"),
                ("tags表 - use_count字段", 
                 "SELECT column_name FROM information_schema.columns WHERE table_name='tags' AND column_name='use_count'"),
                ("photo_tags表 - source约束", 
                 "SELECT constraint_name FROM information_schema.table_constraints WHERE table_name='photo_tags' AND constraint_name='chk_photo_tags_source'"),
                ("搜索函数", 
                 "SELECT proname FROM pg_proc WHERE proname='search_photos'"),
            ]
            
            all_ok = True
            for check_name, check_sql in checks:
                result = conn.execute(text(check_sql))
                if result.fetchone():
                    print(f"   ✅ {check_name}")
                else:
                    print(f"   ❌ {check_name} - 未找到")
                    all_ok = False
        
        print("\n" + "=" * 60)
        if all_ok:
            print("🎉 迁移完成！所有检查通过")
        else:
            print("⚠️  迁移完成，但部分检查未通过，请手动检查")
        print("=" * 60)
        
        # 显示统计信息
        print("\n📊 数据库统计:")
        with engine.connect() as conn:
            # 照片数量
            result = conn.execute(text("SELECT COUNT(*) FROM photos"))
            photo_count = result.fetchone()[0]
            print(f"   照片总数: {photo_count}")
            
            # 标签数量
            result = conn.execute(text("SELECT COUNT(*) FROM tags"))
            tag_count = result.fetchone()[0]
            print(f"   标签总数: {tag_count}")
            
            # AI处理状态统计
            result = conn.execute(text("""
                SELECT ai_status, COUNT(*) 
                FROM photos 
                WHERE ai_status IS NOT NULL 
                GROUP BY ai_status
            """))
            print(f"\n   AI处理状态:")
            for status, count in result:
                print(f"     - {status}: {count}")
            
            # 标签使用统计
            result = conn.execute(text("""
                SELECT name, zh, use_count 
                FROM tags 
                WHERE use_count > 0 
                ORDER BY use_count DESC 
                LIMIT 5
            """))
            print(f"\n   热门标签 (Top 5):")
            for name, zh, count in result:
                tag_display = zh if zh else name
                print(f"     - {tag_display}: {count}次")
        
        print("\n💡 提示:")
        print("   - 新增字段可能需要更新代码中的模型定义")
        print("   - 可以使用 search_photos() 函数进行智能搜索")
        print("   - 标签使用次数会自动更新\n")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        print("\n错误详情:")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

