"""
OpenAI图像处理服务
"""
import base64
import logging
import os
from typing import Dict, Any, List, Optional
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI图像处理服务"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.is_initialized = bool(api_key)
        logger.info(f"OpenAI服务初始化: {'成功' if self.is_initialized else '失败'}")
    
    def _encode_image(self, image_path: str) -> str:
        """将图像编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            raise
    
    def _resize_image(self, image_path: str, max_size: int = 1024) -> str:
        """调整图像大小以符合API要求"""
        try:
            with Image.open(image_path) as img:
                # 计算新尺寸
                width, height = img.size
                if max(width, height) > max_size:
                    if width > height:
                        new_width = max_size
                        new_height = int(height * max_size / width)
                    else:
                        new_height = max_size
                        new_width = int(width * max_size / height)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 保存临时文件
                    temp_path = image_path.replace('.', '_resized.')
                    img.save(temp_path, quality=85)
                    return temp_path
                return image_path
        except Exception as e:
            logger.error(f"图像调整失败: {e}")
            return image_path
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """使用OpenAI分析图像"""
        if not self.is_initialized:
            raise Exception("OpenAI服务未初始化")
        
        try:
            logger.info(f"🔍 [OpenAI] 开始分析图像: {image_path}")
            
            # 调整图像大小
            processed_image_path = self._resize_image(image_path)
            
            # 编码图像
            base64_image = self._encode_image(processed_image_path)
            
            # 构建请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """请详细分析这张图片，提供以下信息：
1. 图片描述（简洁明了的中文描述）
2. 主要物体和场景
3. 颜色特征（主要颜色和色调）
4. 情感氛围（图片传达的情感）
5. 关键词标签（用逗号分隔，适合搜索）
6. 图片类型（如：风景、人物、食物、建筑等）

请用JSON格式返回结果，包含以下字段：
- description: 图片描述
- objects: 主要物体列表
- colors: 颜色特征
- mood: 情感氛围
- tags: 关键词标签
- category: 图片类型"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            logger.info("📤 [OpenAI] 发送请求到API...")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info(f"✅ [OpenAI] API响应成功")
                
                # 解析JSON响应
                try:
                    import json
                    
                    # 尝试从Markdown代码块中提取JSON
                    if content.startswith("```json") and content.endswith("```"):
                        json_str = content[7:-3].strip()
                    elif content.startswith("```") and content.endswith("```"):
                        json_str = content[3:-3].strip()
                    else:
                        json_str = content.strip()
                    
                    analysis = json.loads(json_str)
                    
                    # 打印调试信息
                    print(f"🔍 [OpenAI] 解析结果:")
                    print(f"  - description: {analysis.get('description', 'N/A')}")
                    print(f"  - colors: {analysis.get('colors', 'N/A')}")
                    print(f"  - mood: {analysis.get('mood', 'N/A')}")
                    print(f"  - tags: {analysis.get('tags', 'N/A')}")
                    print(f"  - category: {analysis.get('category', 'N/A')}")
                    
                    # 处理tags字段（可能是字符串或列表）
                    tags_value = analysis.get("tags", "")
                    if isinstance(tags_value, list):
                        tags = tags_value
                    elif isinstance(tags_value, str):
                        tags = [t.strip() for t in tags_value.split(",") if t.strip()]
                    else:
                        tags = []
                    
                    return {
                        "success": True,
                        "description": analysis.get("description", ""),
                        "objects": analysis.get("objects", []),
                        "colors": analysis.get("colors", ""),
                        "mood": analysis.get("mood", ""),
                        "tags": tags,
                        "category": analysis.get("category", "other"),
                        "raw_response": content
                    }
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试提取关键信息
                    return self._parse_text_response(content)
            else:
                logger.error(f"❌ [OpenAI] API请求失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return {
                    "success": False,
                    "error": f"API请求失败: {response.status_code}",
                    "description": "无法分析图片",
                    "tags": [],
                    "category": "other"
                }
                
        except Exception as e:
            logger.error(f"❌ [OpenAI] 图像分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "description": "分析失败",
                "tags": [],
                "category": "other"
            }
        finally:
            # 清理临时文件
            if processed_image_path != image_path and os.path.exists(processed_image_path):
                try:
                    os.remove(processed_image_path)
                except:
                    pass
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """解析文本响应（当JSON解析失败时）"""
        try:
            # 简单的文本解析
            lines = content.split('\n')
            description = ""
            tags = []
            
            for line in lines:
                line = line.strip()
                if "描述" in line or "description" in line.lower():
                    description = line.split(":", 1)[-1].strip()
                elif "标签" in line or "tags" in line.lower():
                    tag_text = line.split(":", 1)[-1].strip()
                    tags = [tag.strip() for tag in tag_text.split(",") if tag.strip()]
            
            return {
                "success": True,
                "description": description or content[:200],
                "objects": [],
                "colors": "",
                "mood": "",
                "tags": tags,
                "category": "other",
                "raw_response": content
            }
        except:
            return {
                "success": True,
                "description": content[:200],
                "objects": [],
                "colors": "",
                "mood": "",
                "tags": [],
                "category": "other",
                "raw_response": content
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "type": "openai",
            "model": self.model,
            "initialized": self.is_initialized,
            "features": ["image_analysis", "object_detection", "color_analysis", "mood_analysis"]
        }
