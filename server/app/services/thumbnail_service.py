"""
缩略图生成服务

功能：
- 自动生成多种尺寸的缩略图
- 优化图片质量和文件大小
- 支持多种图片格式

尺寸规格：
- small: 200x200 (列表缩略图)
- medium: 600x600 (预览图)
- large: 1200x1200 (详情页)
- original: 保留原图

优化：
- 使用Pillow高效处理
- 保持宽高比
- WebP格式压缩
"""

from PIL import Image
import io
import os
from pathlib import Path
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class ThumbnailService:
    """缩略图生成服务"""
    
    # 预定义的缩略图尺寸
    SIZES = {
        'small': (200, 200),      # 列表缩略图
        'medium': (600, 600),     # 预览图
        'large': (1200, 1200),    # 详情页
    }
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    
    # 图片质量设置
    QUALITY = {
        'small': 80,
        'medium': 85,
        'large': 90,
    }
    
    @staticmethod
    def generate_thumbnails(
        image_path: str,
        output_dir: str = None
    ) -> Dict[str, str]:
        """
        生成所有尺寸的缩略图
        
        Args:
            image_path: 原始图片路径
            output_dir: 输出目录（默认为原图同目录）
            
        Returns:
            包含各尺寸缩略图路径的字典
            {
                'small': '/path/to/small.webp',
                'medium': '/path/to/medium.webp',
                'large': '/path/to/large.webp',
                'original': '/path/to/original.jpg'
            }
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 获取文件信息
            file_path = Path(image_path)
            if file_path.suffix.lower() not in ThumbnailService.SUPPORTED_FORMATS:
                raise ValueError(f"不支持的图片格式: {file_path.suffix}")
            
            # 设置输出目录
            if output_dir is None:
                output_dir = file_path.parent
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # 打开原图
            with Image.open(image_path) as img:
                # 转换RGBA为RGB（处理PNG透明背景）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 存储结果
                result = {'original': image_path}
                
                # 生成各尺寸缩略图
                for size_name, (width, height) in ThumbnailService.SIZES.items():
                    try:
                        # 创建副本避免修改原图
                        thumb = img.copy()
                        
                        # 保持宽高比缩放
                        thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
                        
                        # 生成文件名
                        output_filename = f"{file_path.stem}_{size_name}.webp"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        # 保存为WebP格式（更好的压缩比）
                        thumb.save(
                            output_path,
                            'WEBP',
                            quality=ThumbnailService.QUALITY[size_name],
                            method=6  # 最佳压缩
                        )
                        
                        result[size_name] = output_path
                        
                        logger.info(f"✅ 生成缩略图: {size_name} ({thumb.size}) -> {output_path}")
                        
                    except Exception as e:
                        logger.error(f"❌ 生成 {size_name} 缩略图失败: {e}")
                        # 如果某个尺寸失败，使用原图
                        result[size_name] = image_path
                
                return result
                
        except Exception as e:
            logger.error(f"❌ 缩略图生成失败: {e}")
            # 失败时返回原图
            return {
                'original': image_path,
                'small': image_path,
                'medium': image_path,
                'large': image_path,
            }
    
    @staticmethod
    def generate_thumbnail_bytes(
        image_bytes: bytes,
        size: Tuple[int, int] = (600, 600),
        quality: int = 85
    ) -> bytes:
        """
        从字节流生成缩略图字节流
        
        Args:
            image_bytes: 原始图片字节
            size: 目标尺寸
            quality: 图片质量 (1-100)
            
        Returns:
            缩略图字节流
        """
        try:
            # 从字节流打开图片
            with Image.open(io.BytesIO(image_bytes)) as img:
                # 转换为RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 缩放
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 保存到字节流
                output = io.BytesIO()
                img.save(output, 'WEBP', quality=quality, method=6)
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"❌ 生成缩略图字节流失败: {e}")
            return image_bytes
    
    @staticmethod
    def optimize_image(
        image_path: str,
        max_size: int = 2000,
        quality: int = 85
    ) -> str:
        """
        优化图片：减小文件大小，限制尺寸
        
        Args:
            image_path: 图片路径
            max_size: 最大边长（像素）
            quality: 图片质量
            
        Returns:
            优化后的图片路径
        """
        try:
            with Image.open(image_path) as img:
                # 如果图片过大，缩小
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 转换为RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 覆盖原文件
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                
                logger.info(f"✅ 优化图片: {image_path}")
                return image_path
                
        except Exception as e:
            logger.error(f"❌ 优化图片失败: {e}")
            return image_path


# 便捷函数
def create_thumbnails(image_path: str, output_dir: str = None) -> Dict[str, str]:
    """创建缩略图的便捷函数"""
    service = ThumbnailService()
    return service.generate_thumbnails(image_path, output_dir)

