#!/usr/bin/env python3
"""
API测试脚本 - 验证服务是否正常运行
"""
import requests
import json

def test_api():
    """测试API端点"""
    base_url = "http://localhost:8003"
    
    print("🧪 测试API端点...")
    print("=" * 50)
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查: 通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print()
    
    # 测试API文档
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档: 可访问")
            print(f"   文档地址: {base_url}/docs")
        else:
            print(f"❌ API文档失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档异常: {e}")
    
    print()
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径: 可访问")
        else:
            print(f"❌ 根路径失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径异常: {e}")
    
    print()
    print("🎯 测试完成！")
    print(f"📚 完整API文档: {base_url}/docs")
    print(f"🔧 健康检查: {base_url}/health")

if __name__ == "__main__":
    test_api()
