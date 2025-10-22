#!/usr/bin/env python3
"""
测试ChromaDB向量服务
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_service import vector_service
import numpy as np

def test_chroma():
    """测试ChromaDB功能"""
    print("🔍 测试ChromaDB向量服务")
    print("=" * 40)
    
    # 测试添加向量
    test_embedding = np.random.rand(768).tolist()
    metadata = {
        "user_id": 1,
        "filename": "test.jpg",
        "caption": "测试图片"
    }
    
    success = vector_service.add_photo_embedding(
        photo_id=1,
        embedding=test_embedding,
        metadata=metadata
    )
    
    if success:
        print("✅ 向量添加成功")
    else:
        print("❌ 向量添加失败")
        return
    
    # 测试搜索
    similar = vector_service.search_similar_photos(
        query_embedding=test_embedding,
        limit=5
    )
    
    print(f"🔍 找到 {len(similar)} 个相似结果")
    
    # 测试统计信息
    stats = vector_service.get_collection_stats()
    print(f"📊 集合统计: {stats}")
    
    print("✅ ChromaDB测试完成")

if __name__ == "__main__":
    test_chroma()
