# 前端后端集成说明

## 🎯 集成状态

✅ **已完成**:
- API客户端 (`lib/api.ts`) - 完整的后端API集成
- 认证系统 (`lib/auth.tsx`) - 用户登录/注册
- 照片存储更新 (`lib/photo-store.ts`) - 支持API和Mock数据切换
- 类型定义更新

## 🔧 环境配置

在 `webui` 目录下创建 `.env.local` 文件：

```bash
# API配置
NEXT_PUBLIC_API_URL=http://localhost:8003

# 开发模式配置
NEXT_PUBLIC_USE_MOCK_DATA=true

# 其他配置
NEXT_PUBLIC_APP_NAME=Momento AI Photo Management
```

## 🚀 启动步骤

### 1. 启动后端服务
```bash
cd /Users/yzm/code/108-momento/server
python start.py
```

### 2. 启动前端服务
```bash
cd /Users/yzm/code/108-momento/webui
npm run dev
```

## 🔄 数据模式切换

### Mock数据模式 (开发)
- 使用本地mock数据
- 不需要后端服务
- 适合前端开发测试

### API模式 (生产)
- 连接真实后端API
- 需要后端服务运行
- 支持用户认证、照片上传等

## 📝 主要功能

### 认证功能
- 用户注册/登录
- Token管理
- 自动登录状态保持

### 照片管理
- 照片上传 (支持拖拽)
- 照片列表展示
- 照片搜索和过滤
- 标签管理

### 搜索功能
- 文本搜索
- 标签筛选
- 分类筛选
- 相似照片推荐

## 🔧 开发建议

1. **开发阶段**: 使用Mock数据模式，快速迭代前端功能
2. **测试阶段**: 切换到API模式，测试前后端集成
3. **生产部署**: 配置正确的API URL和认证

## 📊 API端点

- `POST /api/v1/users/register` - 用户注册
- `POST /api/v1/users/login` - 用户登录
- `POST /api/v1/photos/upload` - 照片上传
- `GET /api/v1/photos` - 获取照片列表
- `GET /api/v1/search/photos` - 搜索照片
- `GET /health` - 健康检查

## 🎨 UI组件

- 使用shadcn/ui组件库
- 响应式设计
- 暗色/亮色主题支持
- 移动端适配
