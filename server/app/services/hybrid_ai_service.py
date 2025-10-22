"""
混合AI服务 - 结合传统CV和外部API
"""
import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
import logging
import hashlib
import colorsys
from datetime import datetime
import requests
import base64
import json

from app.config import settings
from app.core.exceptions import AIProcessingError

logger = logging.getLogger(__name__)

class HybridAIService:
    """混合AI服务 - 传统CV + 外部API"""
    
    def __init__(self):
        self.is_initialized = True
        self.api_enabled = settings.ai_api_enabled
        self.cv_enabled = settings.ai_cv_enabled
        self.api_provider = settings.ai_api_provider
        logger.info("混合AI服务初始化完成")
    
    def process_photo_simple(self, photo_id: int, image_path: str):
        """简单的后台处理照片 - 混合方案"""
        try:
            print(f"🚀 [混合AI] 开始处理照片 {photo_id}")
            logger.info(f"🚀 [混合AI] 开始处理照片 {photo_id}")
            
            # 更新AI状态为processing
            try:
                from app.database import get_db
                from app.models import Photo
                db = next(get_db())
                photo = db.query(Photo).filter(Photo.id == photo_id).first()
                if photo:
                    photo.ai_status = 'processing'
                    db.commit()
                    print(f"📝 [混合AI] 更新照片状态为 processing")
            except Exception as e:
                print(f"⚠️  [混合AI] 更新状态失败: {e}")
            
            final_result = {}
            
            # 1. 快速传统CV处理（立即返回）
            if self.cv_enabled:
                cv_result = self._process_with_cv(image_path)
                print(f"📊 [传统CV] 处理完成: {cv_result}")
                logger.info(f"📊 [传统CV] 处理完成: {cv_result}")
                final_result = cv_result
            
            # 2. 外部API处理（异步，不阻塞）
            if self.api_enabled and settings.is_ai_api_available():
                try:
                    print(f"🌐 [混合AI] 开始调用外部API...")
                    api_result = self._process_with_api(image_path)
                    print(f"🤖 [外部API] 处理完成")
                    print(f"  - 描述: {api_result.get('caption', 'N/A')}")
                    print(f"  - 标签: {[tag.get('name') if isinstance(tag, dict) else tag for tag in api_result.get('tags', [])]}")
                    print(f"  - 分类: {api_result.get('category', 'N/A')}")
                    print(f"  - 情绪: {api_result.get('mood', 'N/A')}")
                    logger.info(f"🤖 [外部API] 处理完成")
                    logger.info(f"  - 描述: {api_result.get('caption', 'N/A')}")
                    logger.info(f"  - 标签: {api_result.get('tags', [])}")
                    logger.info(f"  - 分类: {api_result.get('category', 'N/A')}")
                    logger.info(f"  - 情绪: {api_result.get('mood', 'N/A')}")
                    final_result = api_result  # API结果优先
                except Exception as e:
                    print(f"⚠️  [混合AI] 外部API处理失败: {e}")
                    logger.warning(f"外部API处理失败，使用传统CV结果: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            # 3. 保存结果到数据库
            if final_result and not final_result.get('error'):
                try:
                    print(f"💾 [混合AI] 开始保存结果到数据库...")
                    from app.database import get_db
                    from app.services.photo_service import PhotoService
                    
                    db = next(get_db())
                    photo_service = PhotoService(db)
                    
                    # 更新照片的AI分析结果
                    photo_service.update_photo_ai_data(
                        photo_id=photo_id,
                        caption=final_result.get('caption', ''),
                        tags=final_result.get('tags', []),
                        category=final_result.get('category', 'other'),
                        dominant_colors=final_result.get('colors', ''),
                        mood=final_result.get('mood', '')
                    )
                    
                    # 更新AI状态为completed
                    photo = db.query(Photo).filter(Photo.id == photo_id).first()
                    if photo:
                        photo.ai_status = 'completed'
                        photo.ai_error = None
                        db.commit()
                    
                    print(f"💾 [混合AI] AI结果已保存到数据库")
                    logger.info(f"💾 [混合AI] AI结果已保存到数据库")
                    
                except Exception as e:
                    print(f"❌ [混合AI] 保存AI结果到数据库失败: {e}")
                    logger.error(f"保存AI结果到数据库失败: {e}")
                    import traceback
                    print(traceback.format_exc())
                    
                    # 更新AI状态为failed
                    try:
                        from app.models import Photo
                        photo = db.query(Photo).filter(Photo.id == photo_id).first()
                        if photo:
                            photo.ai_status = 'failed'
                            photo.ai_error = str(e)
                            db.commit()
                    except:
                        pass
            
            print(f"✅ [混合AI] 照片 {photo_id} 处理完成")
            logger.info(f"✅ [混合AI] 照片 {photo_id} 处理完成")
            
        except Exception as e:
            print(f"❌ [混合AI] 混合AI处理失败: {e}")
            logger.error(f"混合AI处理失败: {e}")
            import traceback
            print(traceback.format_exc())
            
            # 更新AI状态为failed
            try:
                from app.database import get_db
                from app.models import Photo
                db = next(get_db())
                photo = db.query(Photo).filter(Photo.id == photo_id).first()
                if photo:
                    photo.ai_status = 'failed'
                    photo.ai_error = str(e)[:500]  # 限制错误信息长度
                    db.commit()
                    print(f"📝 [混合AI] 更新照片状态为 failed")
            except Exception as update_error:
                print(f"⚠️  [混合AI] 更新失败状态失败: {update_error}")
            
            # 不抛出异常，避免影响主流程
    
    def _process_with_cv(self, image_path: str) -> Dict[str, Any]:
        """使用传统计算机视觉处理"""
        try:
            # 加载图像
            image = self._load_image(image_path)
            if image is None:
                return {"error": "图像加载失败"}
            
            # 快速特征提取
            result = {
                "caption": self._generate_simple_caption(image),
                "colors": self._extract_dominant_colors(image),
                "tags": self._generate_simple_tags(image),
                "features": self._extract_basic_features(image),
                "source": "traditional_cv"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"传统CV处理失败: {e}")
            return {"error": str(e)}
    
    def _process_with_api(self, image_path: str) -> Dict[str, Any]:
        """使用外部API处理"""
        try:
            logger.info("🌐 [混合AI] 使用外部API处理...")
            
            # 根据配置选择API服务
            if self.api_provider == "openai" and settings.openai_api_key:
                from app.services.openai_service import OpenAIService
                openai_service = OpenAIService(settings.openai_api_key, settings.openai_model)
                result = openai_service.analyze_image(image_path)
                
                if result.get("success"):
                    return {
                        "caption": result.get("description", ""),
                        "tags": [{"name": tag, "confidence": 0.9} for tag in result.get("tags", [])],
                        "objects": result.get("objects", []),
                        "colors": result.get("colors", ""),
                        "mood": result.get("mood", ""),
                        "category": result.get("category", "other"),
                        "source": "openai_api"
                    }
                else:
                    logger.warning(f"OpenAI处理失败: {result.get('error', '未知错误')}")
                    raise Exception(f"OpenAI处理失败: {result.get('error', '未知错误')}")
            
            elif self.api_provider == "qwen" and settings.qwen_api_key:
                # 这里可以集成通义千问API
                logger.info("通义千问API集成待实现")
                raise Exception("通义千问API尚未实现")
            
            else:
                logger.warning(f"未配置的API提供商: {self.api_provider}")
                raise Exception(f"未配置的API提供商: {self.api_provider}")
            
        except Exception as e:
            logger.error(f"外部API处理失败: {e}")
            return {"error": str(e)}
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """加载图像"""
        try:
            if not os.path.exists(image_path):
                return None
            
            image = Image.open(image_path).convert('RGB')
            image_array = np.array(image)
            return image_array
            
        except Exception as e:
            logger.error(f"图像加载失败: {e}")
            return None
    
    def _generate_simple_caption(self, image: np.ndarray) -> str:
        """生成简单描述"""
        try:
            height, width = image.shape[:2]
            aspect_ratio = width / height
            
            if aspect_ratio > 1.5:
                orientation = "横向"
            elif aspect_ratio < 0.7:
                orientation = "竖向"
            else:
                orientation = "方形"
            
            # 分析颜色
            colors = self._extract_dominant_colors(image, k=3)
            if colors:
                color_desc = f"主色调{colors[0]}"
            else:
                color_desc = "彩色"
            
            return f"{orientation}照片，{color_desc}，尺寸{width}x{height}"
            
        except Exception as e:
            logger.error(f"描述生成失败: {e}")
            return "照片分析中..."
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[str]:
        """提取主色调"""
        try:
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            colors = []
            for center in centers:
                r, g, b = center.astype(int)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_color)
            
            return colors
            
        except Exception as e:
            logger.error(f"颜色提取失败: {e}")
            return []
    
    def _generate_simple_tags(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """生成简单标签"""
        try:
            tags = []
            height, width = image.shape[:2]
            aspect_ratio = width / height
            
            # 尺寸标签
            if aspect_ratio > 1.5:
                tags.append({"name": "横向", "confidence": 0.9, "source": "geometry"})
            elif aspect_ratio < 0.7:
                tags.append({"name": "竖向", "confidence": 0.9, "source": "geometry"})
            else:
                tags.append({"name": "方形", "confidence": 0.9, "source": "geometry"})
            
            # 颜色标签
            colors = self._extract_dominant_colors(image, k=3)
            if colors:
                color_name = self._get_color_name(colors[0])
                tags.append({"name": color_name, "confidence": 0.7, "source": "color"})
            
            # 复杂度标签
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (height * width)
            
            if edge_density > 0.1:
                tags.append({"name": "复杂", "confidence": 0.6, "source": "complexity"})
            else:
                tags.append({"name": "简单", "confidence": 0.6, "source": "complexity"})
            
            return tags
            
        except Exception as e:
            logger.error(f"标签生成失败: {e}")
            return []
    
    def _extract_basic_features(self, image: np.ndarray) -> Dict[str, Any]:
        """提取基本特征"""
        try:
            height, width = image.shape[:2]
            
            # 颜色直方图
            hist_r = cv2.calcHist([image], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [32], [0, 256])
            hist_b = cv2.calcHist([image], [2], None, [32], [0, 256])
            
            # 归一化
            hist_r = hist_r.flatten() / np.sum(hist_r)
            hist_g = hist_g.flatten() / np.sum(hist_g)
            hist_b = hist_b.flatten() / np.sum(hist_b)
            
            # 边缘特征
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (height * width)
            
            return {
                "size": {"width": width, "height": height},
                "aspect_ratio": width / height,
                "edge_density": float(edge_density),
                "color_histogram": {
                    "r": hist_r.tolist(),
                    "g": hist_g.tolist(),
                    "b": hist_b.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return {}
    
    def _get_color_name(self, hex_color: str) -> str:
        """根据十六进制颜色获取颜色名称"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            if s < 0.2:
                if v > 0.8:
                    return "白色"
                elif v < 0.3:
                    return "黑色"
                else:
                    return "灰色"
            elif h < 0.1 or h > 0.9:
                return "红色"
            elif 0.1 <= h < 0.3:
                return "黄色"
            elif 0.3 <= h < 0.5:
                return "绿色"
            elif 0.5 <= h < 0.7:
                return "青色"
            elif 0.7 <= h < 0.9:
                return "蓝色"
            else:
                return "紫色"
        except:
            return "彩色"
    
    def enable_api(self, enabled: bool = True):
        """启用/禁用外部API"""
        self.api_enabled = enabled
        logger.info(f"外部API {'已启用' if enabled else '已禁用'}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "type": "hybrid",
            "traditional_cv": self.cv_enabled,
            "external_api": self.api_enabled,
            "api_provider": self.api_provider,
            "features": ["color_analysis", "shape_analysis", "texture_analysis"],
            "initialized": self.is_initialized,
            "config": settings.get_ai_config()
        }

# 全局混合AI服务实例
hybrid_ai_service = HybridAIService()
