"""
AI服务层 - 处理图像识别、标签生成等AI任务
"""
import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    BlipProcessor, BlipForConditionalGeneration,
    CLIPProcessor, CLIPModel
)
import logging

from app.config import settings
from app.core.exceptions import AIProcessingError

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.device = self._get_device()
        self.models = {}
        self._load_models()
    
    def _get_device(self) -> str:
        """获取计算设备"""
        if settings.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return settings.device
    
    def _load_models(self):
        """加载AI模型"""
        try:
            # 加载BLIP-2模型用于图像描述
            self.models['blip_processor'] = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            )
            self.models['blip_model'] = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            ).to(self.device)
            
            # 加载CLIP模型用于图像-文本匹配
            self.models['clip_processor'] = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )
            self.models['clip_model'] = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32"
            ).to(self.device)
            
            logger.info("AI模型加载完成")
            
        except Exception as e:
            logger.error(f"AI模型加载失败: {e}")
            raise AIProcessingError(f"模型加载失败: {e}")
    
    def process_photo_simple(self, photo_id: int, image_path: str):
        """简单的后台处理照片 - 使用混合AI服务"""
        try:
            logger.info(f"🚀 [AI] 开始处理照片 {photo_id}")
            
            # 使用混合AI服务
            from app.services.hybrid_ai_service import hybrid_ai_service
            result = hybrid_ai_service.process_photo_simple(photo_id, image_path)
            
            logger.info(f"✅ [AI] 照片 {photo_id} 处理完成")
            
        except Exception as e:
            logger.error(f"AI处理失败: {e}")
            # 不抛出异常，避免影响主流程
    
    def _process_photo_sync(self, photo_id: int, image_path: str):
        """同步处理照片"""
        try:
            # 加载图像
            image = self._load_image(image_path)
            if image is None:
                raise AIProcessingError("图像加载失败")
            
            # 生成图像描述
            caption = self._generate_caption(image)
            
            # 提取主色调
            dominant_colors = self._extract_dominant_colors(image)
            
            # 生成标签
            tags = self._generate_tags(image)
            
            # 生成图像嵌入
            embedding = self._generate_embedding(image)
            
            # 这里应该更新数据库
            # 暂时打印结果
            logger.info(f"照片 {photo_id} 处理完成:")
            logger.info(f"  描述: {caption}")
            logger.info(f"  主色调: {dominant_colors}")
            logger.info(f"  标签: {tags}")
            
        except Exception as e:
            logger.error(f"照片处理失败: {e}")
            raise AIProcessingError(f"照片处理失败: {e}")
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """加载图像"""
        try:
            if not os.path.exists(image_path):
                return None
            
            # 使用PIL加载图像
            image = Image.open(image_path).convert('RGB')
            
            # 转换为numpy数组
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"图像加载失败: {e}")
            return None
    
    def _generate_caption(self, image: np.ndarray) -> str:
        """生成图像描述"""
        try:
            # 转换图像格式
            pil_image = Image.fromarray(image)
            
            # 使用BLIP生成描述
            inputs = self.models['blip_processor'](pil_image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                out = self.models['blip_model'].generate(**inputs, max_length=50)
            
            caption = self.models['blip_processor'].decode(out[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            logger.error(f"描述生成失败: {e}")
            return "无法生成描述"
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[str]:
        """提取主色调"""
        try:
            # 重塑图像数据
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # 使用K-means聚类
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # 转换颜色格式
            colors = []
            for center in centers:
                r, g, b = center.astype(int)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_color)
            
            return colors
            
        except Exception as e:
            logger.error(f"颜色提取失败: {e}")
            return []
    
    def _generate_tags(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """生成标签"""
        try:
            # 预定义的标签候选
            tag_candidates = [
                "cat", "dog", "car", "tree", "building", "person", "food", "nature",
                "sky", "water", "mountain", "beach", "city", "street", "indoor", "outdoor"
            ]
            
            # 转换图像格式
            pil_image = Image.fromarray(image)
            
            # 使用CLIP进行图像-文本匹配
            inputs = self.models['clip_processor'](
                text=tag_candidates,
                images=pil_image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.models['clip_model'](**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # 提取高置信度的标签
            tags = []
            for i, prob in enumerate(probs[0]):
                if prob > 0.1:  # 置信度阈值
                    tags.append({
                        "name": tag_candidates[i],
                        "confidence": float(prob),
                        "source": "clip"
                    })
            
            return tags
            
        except Exception as e:
            logger.error(f"标签生成失败: {e}")
            return []
    
    def _generate_embedding(self, image: np.ndarray) -> Optional[List[float]]:
        """生成图像嵌入向量"""
        try:
            # 转换图像格式
            pil_image = Image.fromarray(image)
            
            # 使用CLIP生成嵌入
            inputs = self.models['clip_processor'](images=pil_image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                image_features = self.models['clip_model'].get_image_features(**inputs)
                # 归一化
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().tolist()[0]
            
        except Exception as e:
            logger.error(f"嵌入生成失败: {e}")
            return None
    
    def find_similar_images(self, query_image_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """查找相似图像"""
        try:
            # 生成查询图像的嵌入
            query_image = self._load_image(query_image_path)
            if query_image is None:
                return []
            
            query_embedding = self._generate_embedding(query_image)
            if query_embedding is None:
                return []
            
            # 这里应该与数据库中的嵌入进行相似度计算
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logger.error(f"相似图像搜索失败: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "device": self.device,
            "models_loaded": list(self.models.keys()),
            "cuda_available": torch.cuda.is_available(),
            "mps_available": torch.backends.mps.is_available()
        }
