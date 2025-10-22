"""
向量搜索服务 - 使用ChromaDB
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """向量搜索服务"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化ChromaDB客户端"""
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="photo_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("✅ ChromaDB向量服务初始化完成")
    
    def add_photo_embedding(
        self, 
        photo_id: int, 
        embedding: List[float], 
        metadata: Dict[str, Any]
    ) -> bool:
        """添加照片向量"""
        try:
            self.collection.add(
                ids=[str(photo_id)],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            logger.info(f"✅ 照片 {photo_id} 向量已添加")
            return True
        except Exception as e:
            logger.error(f"❌ 添加向量失败: {e}")
            return False
    
    def search_similar_photos(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似照片"""
        try:
            # 构建查询条件
            where = {}
            if user_id:
                where["user_id"] = user_id
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where if where else None
            )
            
            similar_photos = []
            if results['ids'] and results['ids'][0]:
                for i, photo_id in enumerate(results['ids'][0]):
                    similar_photos.append({
                        'photo_id': int(photo_id),
                        'distance': results['distances'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
            
            return similar_photos
            
        except Exception as e:
            logger.error(f"❌ 向量搜索失败: {e}")
            return []
    
    def update_photo_embedding(
        self, 
        photo_id: int, 
        embedding: List[float], 
        metadata: Dict[str, Any]
    ) -> bool:
        """更新照片向量"""
        try:
            self.collection.update(
                ids=[str(photo_id)],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            logger.info(f"✅ 照片 {photo_id} 向量已更新")
            return True
        except Exception as e:
            logger.error(f"❌ 更新向量失败: {e}")
            return False
    
    def delete_photo_embedding(self, photo_id: int) -> bool:
        """删除照片向量"""
        try:
            self.collection.delete(ids=[str(photo_id)])
            logger.info(f"✅ 照片 {photo_id} 向量已删除")
            return True
        except Exception as e:
            logger.error(f"❌ 删除向量失败: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_embeddings": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {"error": str(e)}


# 全局向量服务实例
vector_service = VectorService()
