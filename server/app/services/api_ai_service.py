"""
外部AI API服务 - 最简单的方案
使用第三方AI服务，无需本地模型
"""
import requests
import json
import base64
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class APIAIService:
    """外部AI API服务"""
    
    def __init__(self):
        # 可以配置不同的AI服务
        self.services = {
            'openai': {
                'url': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-4-vision-preview',
                'api_key': 'your-openai-api-key'
            },
            'qwen': {
                'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/generation',
                'model': 'qwen-vl-plus',
                'api_key': 'your-qwen-api-key'
            },
            'local': {
                'url': 'http://localhost:8000/api/v1/analyze',
                'model': 'local-model'
            }
        }
        self.current_service = 'local'  # 默认使用本地服务
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """分析图像"""
        try:
            # 读取图像文件
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 编码为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 调用AI服务
            result = self._call_ai_api(image_base64)
            
            return result
            
        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            return self._get_fallback_result()
    
    def _call_ai_api(self, image_base64: str) -> Dict[str, Any]:
        """调用AI API"""
        service_config = self.services[self.current_service]
        
        if self.current_service == 'local':
            return self._call_local_api(image_base64)
        elif self.current_service == 'openai':
            return self._call_openai_api(image_base64, service_config)
        elif self.current_service == 'qwen':
            return self._call_qwen_api(image_base64, service_config)
        else:
            return self._get_fallback_result()
    
    def _call_local_api(self, image_base64: str) -> Dict[str, Any]:
        """调用本地API"""
        try:
            response = requests.post(
                self.services['local']['url'],
                json={
                    'image': image_base64,
                    'tasks': ['caption', 'tags', 'colors']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"本地API调用失败: {response.status_code}")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"本地API调用异常: {e}")
            return self._get_fallback_result()
    
    def _call_openai_api(self, image_base64: str, config: Dict) -> Dict[str, Any]:
        """调用OpenAI API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': '请分析这张图片，生成描述、标签和主色调'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{image_base64}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 500
            }
            
            response = requests.post(
                config['url'],
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_openai_response(result)
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {e}")
            return self._get_fallback_result()
    
    def _call_qwen_api(self, image_base64: str, config: Dict) -> Dict[str, Any]:
        """调用通义千问API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': '请分析这张图片，生成中文描述、标签和主色调'
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{image_base64}'
                                    }
                                }
                            ]
                        }
                    ]
                },
                'parameters': {
                    'max_tokens': 500
                }
            }
            
            response = requests.post(
                config['url'],
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_qwen_response(result)
            else:
                logger.error(f"通义千问API调用失败: {response.status_code}")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"通义千问API调用异常: {e}")
            return self._get_fallback_result()
    
    def _parse_openai_response(self, response: Dict) -> Dict[str, Any]:
        """解析OpenAI响应"""
        try:
            content = response['choices'][0]['message']['content']
            return {
                'caption': content,
                'tags': self._extract_tags_from_text(content),
                'colors': self._extract_colors_from_text(content),
                'source': 'openai'
            }
        except:
            return self._get_fallback_result()
    
    def _parse_qwen_response(self, response: Dict) -> Dict[str, Any]:
        """解析通义千问响应"""
        try:
            content = response['output']['choices'][0]['message']['content']
            return {
                'caption': content,
                'tags': self._extract_tags_from_text(content),
                'colors': self._extract_colors_from_text(content),
                'source': 'qwen'
            }
        except:
            return self._get_fallback_result()
    
    def _extract_tags_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取标签"""
        # 简单的关键词提取
        keywords = ['照片', '图片', '图像', '风景', '人物', '建筑', '自然', '城市']
        tags = []
        
        for keyword in keywords:
            if keyword in text:
                tags.append({
                    'name': keyword,
                    'confidence': 0.8,
                    'source': 'text_analysis'
                })
        
        return tags
    
    def _extract_colors_from_text(self, text: str) -> List[str]:
        """从文本中提取颜色"""
        colors = ['红色', '蓝色', '绿色', '黄色', '白色', '黑色', '灰色']
        found_colors = []
        
        for color in colors:
            if color in text:
                found_colors.append(f"#{color}")
        
        return found_colors if found_colors else ['#000000']
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """获取备用结果"""
        return {
            'caption': '照片分析中...',
            'tags': [
                {'name': '照片', 'confidence': 0.5, 'source': 'fallback'}
            ],
            'colors': ['#808080'],
            'source': 'fallback'
        }
    
    def set_service(self, service_name: str):
        """设置AI服务"""
        if service_name in self.services:
            self.current_service = service_name
            logger.info(f"AI服务已切换到: {service_name}")
        else:
            logger.error(f"未知的AI服务: {service_name}")

# 全局API AI服务实例
api_ai_service = APIAIService()
