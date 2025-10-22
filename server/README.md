# Momento AI Photo Management System

AI驱动的智能相册管理系统后端服务

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- 8GB+ RAM (用于AI模型)

### 安装步骤

1. **克隆项目**
```bash
cd server
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

5. **启动服务**
```bash
python start.py
```

### 使用Docker (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📁 项目结构

```
server/
├── app/                    # 应用代码
│   ├── api/               # API路由
│   │   └── v1/           # API v1版本
│   ├── core/             # 核心功能
│   ├── services/         # 业务逻辑层
│   ├── models.py         # 数据库模型
│   ├── schemas.py        # Pydantic模型
│   ├── database.py       # 数据库连接
│   ├── config.py         # 配置管理
│   ├── main.py           # 应用入口
│   ├── celery_app.py     # Celery配置
│   └── tasks.py          # 异步任务
├── sql/                  # SQL脚本
│   └── init.sql         # 数据库初始化
├── requirements.txt      # Python依赖
├── docker-compose.yml   # Docker编排
├── Dockerfile          # Docker镜像
├── start.py            # 启动脚本
├── setup_database.py   # 数据库设置
└── README.md           # 项目说明
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | `postgresql://momento:momento@localhost:5432/momento` |
| `REDIS_URL` | Redis连接URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT密钥 | `your-secret-key-change-in-production` |
| `UPLOAD_DIR` | 文件上传目录 | `./uploads` |
| `MODEL_CACHE_DIR` | AI模型缓存目录 | `./models` |
| `DEVICE` | 计算设备 | `auto` (auto/cpu/cuda/mps) |

### 数据库配置

1. **安装PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# 下载并安装PostgreSQL
```

2. **创建数据库**
```bash
sudo -u postgres psql
CREATE DATABASE momento;
CREATE USER momento WITH PASSWORD 'momento';
GRANT ALL PRIVILEGES ON DATABASE momento TO momento;
\q
```

3. **启用pgvector扩展**
```bash
# 安装pgvector扩展
# Ubuntu/Debian
sudo apt-get install postgresql-15-pgvector

# 在数据库中启用
psql -d momento -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 🎯 API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/upload` | POST | 上传照片 |
| `/api/v1/photos` | GET | 获取照片列表 |
| `/api/v1/photos/{id}` | GET | 获取照片详情 |
| `/api/v1/tags` | GET | 获取标签列表 |
| `/api/v1/search/photos` | GET | 搜索照片 |
| `/api/v1/albums` | GET | 获取相册列表 |

## 🤖 AI功能

### 支持的AI模型

- **BLIP-2**: 图像描述生成
- **CLIP**: 图像-文本匹配和标签生成
- **自定义模型**: 可扩展支持更多模型

### AI处理流程

1. **照片上传** → 触发异步AI处理任务
2. **图像分析** → 生成描述、标签、主色调
3. **向量化** → 生成图像嵌入向量
4. **存储结果** → 保存到数据库

## 🔄 异步任务

使用Celery处理AI任务：

```bash
# 启动Celery Worker
celery -A app.celery_app worker --loglevel=info

# 启动Celery Beat (定时任务)
celery -A app.celery_app beat --loglevel=info
```

## 📊 数据库设计

### 主要表结构

- **users**: 用户信息
- **photos**: 照片元数据
- **tags**: 标签库
- **photo_tags**: 照片标签关联
- **albums**: 相册
- **album_photos**: 相册照片关联

### 向量搜索

使用pgvector扩展支持向量相似度搜索：

```sql
-- 创建向量索引
CREATE INDEX ON photos USING ivfflat (embedding vector_cosine_ops);

-- 相似度搜索
SELECT * FROM photos 
WHERE embedding <-> '[0.1,0.2,...]'::vector < 0.5
ORDER BY embedding <-> '[0.1,0.2,...]'::vector;
```

## 🚀 部署

### 生产环境部署

1. **使用Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **配置Nginx反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **配置SSL证书**
```bash
# 使用Let's Encrypt
certbot --nginx -d your-domain.com
```

## 🔍 监控和日志

### 日志配置

- 应用日志: `logs/app.log`
- 错误日志: `logs/error.log`
- Celery日志: `logs/celery.log`

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
python -c "from app.database import engine; print(engine.connect())"
```

## 🛠️ 开发

### 代码规范

```bash
# 格式化代码
black app/

# 排序导入
isort app/

# 代码检查
flake8 app/
```

### 测试

```bash
# 运行测试
pytest tests/

# 覆盖率报告
pytest --cov=app tests/
```

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础照片管理功能
- AI标签生成
- 向量搜索
- RESTful API

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
