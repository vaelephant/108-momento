# 数据库迁移说明文档

## 📋 概述

本迁移脚本用于优化Momento照片管理系统的数据库结构，提升照片分类和搜索功能。

## 🎯 优化目标

- **照片分类**: 支持按时间、地点、AI状态分类
- **智能搜索**: 优化标签+描述的组合搜索
- **热门标签**: 自动统计标签使用次数
- **数据规范**: 统一字段类型和约束

## 📊 主要变更

### 1. `photos` 表优化

| 变更类型 | 字段 | 说明 |
|---------|------|------|
| **修改** | `dominant_colors` | 从 `ARRAY(String)` 改为 `TEXT`，更兼容 |
| **新增** | `taken_at` | 实际拍摄时间（从EXIF读取） |
| **新增** | `location` | 拍摄地点名称 |
| **新增** | `location_lat` | 拍摄地点纬度 |
| **新增** | `location_lng` | 拍摄地点经度 |
| **新增** | `ai_status` | AI处理状态 (pending/processing/completed/failed) |
| **新增** | `ai_error` | AI处理错误信息 |

### 2. `tags` 表增强

| 变更类型 | 字段 | 说明 |
|---------|------|------|
| **新增** | `use_count` | 标签使用次数（自动更新） |
| **新增** | `parent_tag_id` | 父标签ID（支持标签层级） |

### 3. `photo_tags` 表规范化

| 变更类型 | 字段 | 说明 |
|---------|------|------|
| **修改** | `source` | 统一为 `'ai'` 或 `'manual'`，删除其他值 |
| **新增** | 约束 | 添加 `CHECK` 约束确保值规范 |

### 4. 新增功能

- ✅ 全文搜索索引（照片描述 + 标签）
- ✅ 热门标签视图 (`v_popular_tags`)
- ✅ 用户统计视图 (`v_user_photo_stats`)
- ✅ 智能搜索函数 (`search_photos()`)
- ✅ 标签使用次数自动更新触发器

## 🚀 执行迁移

### 方法1: 使用Python脚本（推荐）

```bash
cd server
python run_migration.py
```

脚本会：
1. 检查数据库连接
2. 显示迁移内容
3. 要求用户确认
4. 执行迁移
5. 验证结果
6. 显示统计信息

### 方法2: 直接使用SQL

```bash
psql -d momento -f sql/migration_optimize_for_classification.sql
```

## ⚠️ 注意事项

### 迁移前

1. **备份数据库**
   ```bash
   pg_dump momento > backup_$(date +%Y%m%d).sql
   ```

2. **停止应用服务**
   ```bash
   # 停止FastAPI
   pkill -f "python start.py"
   
   # 停止Next.js
   pkill -f "npm run dev"
   ```

3. **检查当前数据**
   ```sql
   -- 检查照片数量
   SELECT COUNT(*) FROM photos;
   
   -- 检查标签数量
   SELECT COUNT(*) FROM tags;
   ```

### 迁移后

1. **更新代码**
   - ✅ `server/app/models.py` 已更新
   - ⚠️  需要更新使用 `dominant_colors` 的代码

2. **重启服务**
   ```bash
   cd server && python start.py
   cd webui && npm run dev
   ```

3. **验证功能**
   - 上传新照片测试AI标签
   - 测试搜索功能
   - 检查标签统计

## 📖 新功能使用示例

### 1. 智能搜索照片

```sql
-- 搜索包含"山峰"的照片
SELECT * FROM search_photos(
    p_user_id := 1,
    p_search_text := '山峰',
    p_limit := 20,
    p_offset := 0
);
```

### 2. 查询热门标签

```sql
-- 查看最常用的10个标签
SELECT * FROM v_popular_tags LIMIT 10;
```

### 3. 用户照片统计

```sql
-- 查看所有用户的照片统计
SELECT * FROM v_user_photo_stats;
```

### 4. 按AI状态查询

```python
# 查询AI处理完成的照片
photos = db.query(Photo).filter(
    Photo.user_id == user_id,
    Photo.ai_status == 'completed'
).all()
```

### 5. 按地点搜索

```python
# 查询某个地点附近的照片（50km范围内）
from sqlalchemy import func

photos = db.query(Photo).filter(
    Photo.location_lat.isnot(None),
    func.earth_distance(
        func.ll_to_earth(Photo.location_lat, Photo.location_lng),
        func.ll_to_earth(target_lat, target_lng)
    ) < 50000  # 50km
).all()
```

## 🔍 性能优化建议

### 1. 定期更新统计信息

```sql
-- 手动更新表统计信息
ANALYZE photos;
ANALYZE tags;
ANALYZE photo_tags;
```

### 2. 清理无用标签

```sql
-- 删除未使用的标签
DELETE FROM tags WHERE use_count = 0 AND created_at < NOW() - INTERVAL '30 days';
```

### 3. 重建索引

```sql
-- 如果查询变慢，重建索引
REINDEX TABLE photos;
REINDEX TABLE tags;
REINDEX TABLE photo_tags;
```

## 🐛 故障排除

### 问题1: 迁移失败

**错误**: `column "dominant_colors" is of type text[] but expression is of type text`

**解决**:
```sql
-- 强制转换类型
ALTER TABLE photos ALTER COLUMN dominant_colors TYPE text USING array_to_string(dominant_colors, ',');
```

### 问题2: 触发器不工作

**检查**:
```sql
-- 查看触发器状态
SELECT * FROM pg_trigger WHERE tgname = 'trg_update_tag_use_count';
```

**修复**:
```sql
-- 重新创建触发器
DROP TRIGGER IF EXISTS trg_update_tag_use_count ON photo_tags;
CREATE TRIGGER trg_update_tag_use_count
AFTER INSERT OR DELETE ON photo_tags
FOR EACH ROW
EXECUTE FUNCTION update_tag_use_count();
```

### 问题3: 搜索函数报错

**错误**: `function search_photos does not exist`

**解决**:
```bash
# 重新执行迁移脚本
psql -d momento -f sql/migration_optimize_for_classification.sql
```

## 📚 相关文档

- [PostgreSQL全文搜索](https://www.postgresql.org/docs/current/textsearch.html)
- [SQLAlchemy关系](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [FastAPI后台任务](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## 💡 后续优化建议

1. **地理围栏搜索**: 使用 PostGIS 扩展实现更精确的地理位置搜索
2. **相似图片搜索**: 集成向量数据库（如Milvus）实现以图搜图
3. **智能相册**: 基于AI标签自动创建主题相册
4. **时间轴优化**: 添加事件聚类，自动识别旅行、活动等
5. **隐私保护**: 添加人脸识别和自动打码功能

## 🙋 获取帮助

如有问题，请查看：
1. 日志文件: `server/logs/`
2. 数据库日志: PostgreSQL错误日志
3. 创建Issue: 在项目仓库中提交问题

---

**最后更新**: 2025-10-22
**版本**: 1.0.0

