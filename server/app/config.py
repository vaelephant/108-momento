"""
应用配置管理 - 支持.env文件读取
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # 加载.env文件


class Settings:
    """应用配置 - 支持.env文件"""
    
    def __init__(self):
        
        # 应用基础配置
        self.app_name = os.getenv("APP_NAME", "Momento AI Photo Management")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # 数据库配置
        self.database_url = os.getenv("DATABASE_URL")
        self.database_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        # Redis配置
        self.redis_url = os.getenv("REDIS_URL")
        
        # 文件存储配置
        self.upload_dir = "./uploads"
        self.max_file_size =  52428800  # 50MB
        
        # AI模型配置
        self.model_cache_dir = "./models"
        self.device = os.getenv("DEVICE", "auto")
        
        # AI服务配置
        self.ai_cv_enabled = os.getenv("AI_CV_ENABLED", "true").lower() == "true"
        self.ai_api_enabled = os.getenv("AI_API_ENABLED", "true").lower() == "true"  # 启用外部API
        self.ai_api_provider = os.getenv("AI_API_PROVIDER", "openai")  # local, qwen, openai
        
        # 通义千问配置
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "")
        self.qwen_model = os.getenv("QWEN_MODEL", "qwen-vl-plus")
        
        # OpenAI配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")  # 使用最新的GPT-4o模型
        
        # AI处理配置
        self.ai_max_workers = int(os.getenv("AI_MAX_WORKERS", "4"))
        self.ai_timeout = int(os.getenv("AI_TIMEOUT", "30"))
        self.ai_retry_count = int(os.getenv("AI_RETRY_COUNT", "3"))
        
        # 任务队列配置
        self.celery_broker_url = os.getenv("CELERY_BROKER_URL")
        self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
        
        # 安全配置
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # API配置
        self.api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3007,http://127.0.0.1:3007")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # 确保必要目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [self.upload_dir, self.model_cache_dir, "logs", "temp"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def print_config(self):
        """打印当前配置"""
        print("🔧 当前配置:")
        print(f"  - 应用名称: {self.app_name}")
        print(f"  - 版本: {self.app_version}")
        print(f"  - 调试模式: {self.debug}")
        print(f"  - 数据库: {self.database_url}")
        print(f"  - Redis: {self.redis_url}")
        print(f"  - 上传目录: {self.upload_dir}")
        print(f"  - 模型目录: {self.model_cache_dir}")
        print(f"  - 设备: {self.device}")
        print(f"  - AI传统CV: {'启用' if self.ai_cv_enabled else '禁用'}")
        print(f"  - AI外部API: {'启用' if self.ai_api_enabled else '禁用'}")
        print(f"  - AI服务提供商: {self.ai_api_provider}")
    
    def validate_config(self):
        """验证配置是否完整"""
        required = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            print(f"❌ 缺少: {', '.join(missing)}")
            return False
        print("✅ 配置OK")
        return True
    
    def get_ai_config(self):
        """获取AI配置信息"""
        return {
            "cv_enabled": self.ai_cv_enabled,
            "api_enabled": self.ai_api_enabled,
            "api_provider": self.ai_api_provider,
            "max_workers": self.ai_max_workers,
            "timeout": self.ai_timeout,
            "retry_count": self.ai_retry_count,
            "features": {
                "traditional_cv": self.ai_cv_enabled,
                "external_api": self.ai_api_enabled,
                "qwen_available": bool(self.qwen_api_key),
                "openai_available": bool(self.openai_api_key)
            }
        }
    
    def is_ai_api_available(self):
        """检查AI API是否可用"""
        if not self.ai_api_enabled:
            return False
        
        if self.ai_api_provider == "qwen":
            return bool(self.qwen_api_key)
        elif self.ai_api_provider == "openai":
            return bool(self.openai_api_key)
        else:
            return True  # local模式总是可用


# 全局配置实例
settings = Settings()

# 测试配置
if __name__ == "__main__":
    print("🔧 配置测试")
    print("=" * 40)
    settings.print_config()
    print("\n🔍 配置验证:")
    settings.validate_config()
    print("\n✅ 测试完成")
