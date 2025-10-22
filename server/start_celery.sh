#!/bin/bash

# Celery Worker 启动脚本

echo "🔄 启动 Celery Worker..."

# 激活虚拟环境
source venv/bin/activate

# 启动Celery Worker
celery -A app.celery_app worker --loglevel=info --queues=photo_processing,ai_processing
