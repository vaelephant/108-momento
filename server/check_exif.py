#!/usr/bin/env python3
"""
查询数据库中照片的EXIF信息

使用方法:
cd /Users/yzm/code/108-momento/server
python check_exif.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Photo
from sqlalchemy import desc, func
import json
from datetime import datetime

def main():
    db = SessionLocal()
    
    try:
        print('\n' + '='*70)
        print('📷 Momento 照片EXIF信息查询')
        print('='*70 + '\n')
        
        # 1. 总体统计
        total_photos = db.query(func.count(Photo.id)).scalar()
        photos_with_exif = db.query(func.count(Photo.id)).filter(Photo.exif_data.isnot(None)).scalar()
        photos_with_taken_at = db.query(func.count(Photo.id)).filter(Photo.taken_at.isnot(None)).scalar()
        
        print('📊 总体统计:')
        print(f'  总照片数: {total_photos}')
        print(f'  有EXIF数据: {photos_with_exif} ({photos_with_exif/total_photos*100:.1f}%)' if total_photos > 0 else '  有EXIF数据: 0')
        print(f'  有拍摄时间: {photos_with_taken_at}')
        print()
        
        if total_photos == 0:
            print('⚠️  数据库中还没有照片')
            return
        
        # 2. 最新上传的照片
        print('='*70)
        print('📸 最新上传的5张照片:')
        print('='*70 + '\n')
        
        recent_photos = db.query(Photo).order_by(desc(Photo.created_at)).limit(5).all()
        
        for i, photo in enumerate(recent_photos, 1):
            print(f'{i}. 照片ID: {photo.id}')
            print(f'   文件名: {photo.filename}')
            print(f'   上传时间: {photo.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
            
            if photo.taken_at:
                print(f'   📅 拍摄时间: {photo.taken_at.strftime("%Y-%m-%d %H:%M:%S")}')
            else:
                print(f'   📅 拍摄时间: 未记录')
            
            if photo.exif_data:
                camera = photo.exif_data.get('camera', '未知')
                location = photo.exif_data.get('location', '未知')
                print(f'   📷 相机: {camera}')
                print(f'   📍 位置: {location}')
                
                # 显示完整EXIF（格式化）
                print(f'   📊 完整EXIF:')
                exif_json = json.dumps(photo.exif_data, ensure_ascii=False, indent=6)
                for line in exif_json.split('\n'):
                    print(f'      {line}')
            else:
                print(f'   📷 EXIF数据: 未记录')
            
            print('-'*70 + '\n')
        
        # 3. 有拍摄时间的照片
        photos_with_time = db.query(Photo).filter(Photo.taken_at.isnot(None)).order_by(desc(Photo.taken_at)).limit(5).all()
        
        if photos_with_time:
            print('='*70)
            print('📅 按拍摄时间排序（最新5张）:')
            print('='*70 + '\n')
            
            for i, photo in enumerate(photos_with_time, 1):
                print(f'{i}. {photo.filename}')
                print(f'   拍摄时间: {photo.taken_at.strftime("%Y-%m-%d %H:%M:%S")}')
                if photo.exif_data and photo.exif_data.get('camera'):
                    print(f'   相机: {photo.exif_data.get("camera")}')
                print()
        
        # 4. 有GPS位置的照片
        photos_with_gps = db.query(Photo).filter(
            Photo.exif_data['latitude'].astext.isnot(None)
        ).order_by(desc(Photo.created_at)).limit(5).all()
        
        if photos_with_gps:
            print('='*70)
            print('📍 有GPS位置的照片:')
            print('='*70 + '\n')
            
            for i, photo in enumerate(photos_with_gps, 1):
                print(f'{i}. {photo.filename}')
                if photo.exif_data:
                    lat = photo.exif_data.get('latitude')
                    lng = photo.exif_data.get('longitude')
                    if lat and lng:
                        print(f'   GPS: {lat}, {lng}')
                    location = photo.exif_data.get('location')
                    if location:
                        print(f'   位置: {location}')
                print()
        
        # 5. 相机型号统计
        print('='*70)
        print('📷 相机型号统计:')
        print('='*70 + '\n')
        
        camera_stats = db.query(
            Photo.exif_data['camera'].astext.label('camera'),
            func.count(Photo.id).label('count')
        ).filter(
            Photo.exif_data['camera'].astext.isnot(None)
        ).group_by(
            Photo.exif_data['camera'].astext
        ).order_by(
            desc('count')
        ).all()
        
        if camera_stats:
            for camera, count in camera_stats:
                print(f'  {camera}: {count}张照片')
        else:
            print('  暂无相机信息')
        
        print('\n' + '='*70)
        print('✅ 查询完成')
        print('='*70 + '\n')
        
    except Exception as e:
        print(f'\n❌ 查询失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    main()

