-- =====================================================
-- 数据库优化迁移脚本 - 照片分类和搜索优化
-- 创建时间: 2025-10-22
-- 用途: 优化照片分类、标签搜索和AI处理相关的表结构
-- =====================================================

-- =====================================================
-- 1. 修改 photos 表
-- =====================================================

-- 1.1 修改 dominant_colors 字段类型（从 ARRAY 改为 TEXT）
DO $$ 
BEGIN
    -- 先备份现有数据（如果有）
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'photos' AND column_name = 'dominant_colors'
    ) THEN
        -- 创建临时列存储转换后的数据
        ALTER TABLE photos ADD COLUMN IF NOT EXISTS dominant_colors_temp TEXT;
        
        -- 将 ARRAY 转换为逗号分隔的字符串
        UPDATE photos 
        SET dominant_colors_temp = array_to_string(dominant_colors, ',')
        WHERE dominant_colors IS NOT NULL;
        
        -- 删除旧列
        ALTER TABLE photos DROP COLUMN IF EXISTS dominant_colors;
        
        -- 重命名新列
        ALTER TABLE photos RENAME COLUMN dominant_colors_temp TO dominant_colors;
    ELSE
        -- 如果列不存在，直接创建
        ALTER TABLE photos ADD COLUMN IF NOT EXISTS dominant_colors TEXT;
    END IF;
END $$;

-- 1.2 添加实际拍摄时间字段（从EXIF读取）
ALTER TABLE photos ADD COLUMN IF NOT EXISTS taken_at TIMESTAMP WITH TIME ZONE;
COMMENT ON COLUMN photos.taken_at IS '实际拍摄时间（从EXIF读取），区别于created_at（上传时间）';

-- 1.3 添加地理位置相关字段
ALTER TABLE photos ADD COLUMN IF NOT EXISTS location VARCHAR(200);
ALTER TABLE photos ADD COLUMN IF NOT EXISTS location_lat DOUBLE PRECISION;
ALTER TABLE photos ADD COLUMN IF NOT EXISTS location_lng DOUBLE PRECISION;

COMMENT ON COLUMN photos.location IS '拍摄地点名称（从EXIF GPS或用户输入）';
COMMENT ON COLUMN photos.location_lat IS '拍摄地点纬度';
COMMENT ON COLUMN photos.location_lng IS '拍摄地点经度';

-- 1.4 添加AI处理状态字段
ALTER TABLE photos ADD COLUMN IF NOT EXISTS ai_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE photos ADD COLUMN IF NOT EXISTS ai_error TEXT;

COMMENT ON COLUMN photos.ai_status IS 'AI处理状态: pending/processing/completed/failed';
COMMENT ON COLUMN photos.ai_error IS 'AI处理错误信息';

-- 1.5 为新字段创建索引
CREATE INDEX IF NOT EXISTS idx_photos_taken_at ON photos(taken_at);
CREATE INDEX IF NOT EXISTS idx_photos_location ON photos(location_lat, location_lng) WHERE location_lat IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_photos_ai_status ON photos(ai_status);

-- =====================================================
-- 2. 修改 tags 表
-- =====================================================

-- 2.1 添加使用次数统计字段
ALTER TABLE tags ADD COLUMN IF NOT EXISTS use_count INTEGER DEFAULT 0;
COMMENT ON COLUMN tags.use_count IS '标签使用次数，用于热门标签排序';

-- 2.2 添加标签层级字段（可选，支持父子关系）
ALTER TABLE tags ADD COLUMN IF NOT EXISTS parent_tag_id BIGINT;
ALTER TABLE tags ADD CONSTRAINT fk_tags_parent 
    FOREIGN KEY (parent_tag_id) REFERENCES tags(id) ON DELETE SET NULL;

COMMENT ON COLUMN tags.parent_tag_id IS '父标签ID，支持标签分类层级';

-- 2.3 创建索引
CREATE INDEX IF NOT EXISTS idx_tags_use_count ON tags(use_count DESC);
CREATE INDEX IF NOT EXISTS idx_tags_parent ON tags(parent_tag_id);

-- =====================================================
-- 3. 优化 photo_tags 表
-- =====================================================

-- 3.1 更新现有的 source 字段值，统一为 'ai' 或 'manual'
UPDATE photo_tags SET source = 'ai' 
WHERE source IN ('ram', 'clip', 'detector', 'blip', 'openai');

UPDATE photo_tags SET source = 'manual' 
WHERE source NOT IN ('ai', 'manual');

-- 3.2 添加约束确保 source 只能是 'ai' 或 'manual'
ALTER TABLE photo_tags DROP CONSTRAINT IF EXISTS chk_photo_tags_source;
ALTER TABLE photo_tags ADD CONSTRAINT chk_photo_tags_source 
    CHECK (source IN ('ai', 'manual'));

COMMENT ON COLUMN photo_tags.source IS '标签来源: ai（AI自动生成） 或 manual（用户手动添加）';

-- =====================================================
-- 4. 创建全文搜索索引（PostgreSQL）
-- =====================================================

-- 4.1 为照片描述创建全文搜索索引
CREATE INDEX IF NOT EXISTS idx_photos_caption_fts ON photos 
USING gin(to_tsvector('simple', COALESCE(caption, '')));

-- 4.2 为标签名称创建全文搜索索引
CREATE INDEX IF NOT EXISTS idx_tags_name_fts ON tags 
USING gin(to_tsvector('simple', COALESCE(name, '') || ' ' || COALESCE(zh, '')));

-- =====================================================
-- 5. 创建用于统计的视图（可选）
-- =====================================================

-- 5.1 热门标签视图
CREATE OR REPLACE VIEW v_popular_tags AS
SELECT 
    t.id,
    t.name,
    t.zh,
    t.category,
    COUNT(pt.photo_id) as photo_count,
    t.use_count
FROM tags t
LEFT JOIN photo_tags pt ON t.id = pt.tag_id
GROUP BY t.id, t.name, t.zh, t.category, t.use_count
ORDER BY photo_count DESC, t.use_count DESC;

COMMENT ON VIEW v_popular_tags IS '热门标签统计视图，按使用次数排序';

-- 5.2 用户照片统计视图
CREATE OR REPLACE VIEW v_user_photo_stats AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT p.id) as total_photos,
    COUNT(DISTINCT CASE WHEN p.ai_status = 'completed' THEN p.id END) as ai_processed_photos,
    SUM(p.file_size) as total_size,
    MAX(p.created_at) as last_upload_at
FROM users u
LEFT JOIN photos p ON u.id = p.user_id
GROUP BY u.id, u.username;

COMMENT ON VIEW v_user_photo_stats IS '用户照片统计视图';

-- =====================================================
-- 6. 创建触发器：自动更新标签使用次数
-- =====================================================

-- 6.1 创建触发器函数
CREATE OR REPLACE FUNCTION update_tag_use_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- 插入时增加计数
        UPDATE tags SET use_count = use_count + 1 WHERE id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        -- 删除时减少计数
        UPDATE tags SET use_count = GREATEST(use_count - 1, 0) WHERE id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 6.2 创建触发器
DROP TRIGGER IF EXISTS trg_update_tag_use_count ON photo_tags;
CREATE TRIGGER trg_update_tag_use_count
AFTER INSERT OR DELETE ON photo_tags
FOR EACH ROW
EXECUTE FUNCTION update_tag_use_count();

COMMENT ON FUNCTION update_tag_use_count() IS '自动更新标签使用次数的触发器函数';

-- =====================================================
-- 7. 数据初始化和清理
-- =====================================================

-- 7.1 初始化现有标签的 use_count
UPDATE tags t
SET use_count = (
    SELECT COUNT(*) 
    FROM photo_tags pt 
    WHERE pt.tag_id = t.id
)
WHERE use_count = 0;

-- 7.2 更新已有照片的 ai_status
UPDATE photos 
SET ai_status = 'completed' 
WHERE caption IS NOT NULL OR EXISTS (
    SELECT 1 FROM photo_tags WHERE photo_id = photos.id AND source = 'ai'
);

UPDATE photos 
SET ai_status = 'failed' 
WHERE ai_status = 'pending' AND created_at < NOW() - INTERVAL '1 hour';

-- =====================================================
-- 8. 创建搜索辅助函数
-- =====================================================

-- 8.1 按标签和描述搜索照片的函数
CREATE OR REPLACE FUNCTION search_photos(
    p_user_id BIGINT,
    p_search_text TEXT,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    photo_id BIGINT,
    photo_url VARCHAR,
    caption TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        p.id as photo_id,
        p.storage_path as photo_url,
        p.caption,
        p.created_at,
        (
            -- 计算相关性分数
            ts_rank(to_tsvector('simple', COALESCE(p.caption, '')), plainto_tsquery('simple', p_search_text)) +
            COALESCE((
                SELECT MAX(pt.confidence)
                FROM photo_tags pt
                JOIN tags t ON pt.tag_id = t.id
                WHERE pt.photo_id = p.id 
                AND (t.name ILIKE '%' || p_search_text || '%' OR t.zh ILIKE '%' || p_search_text || '%')
            ), 0)
        ) as relevance
    FROM photos p
    WHERE p.user_id = p_user_id
    AND (
        to_tsvector('simple', COALESCE(p.caption, '')) @@ plainto_tsquery('simple', p_search_text)
        OR EXISTS (
            SELECT 1 FROM photo_tags pt
            JOIN tags t ON pt.tag_id = t.id
            WHERE pt.photo_id = p.id 
            AND (t.name ILIKE '%' || p_search_text || '%' OR t.zh ILIKE '%' || p_search_text || '%')
        )
    )
    ORDER BY relevance DESC, p.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_photos IS '按标签和描述搜索照片，返回相关性排序的结果';

-- =====================================================
-- 9. 性能优化建议
-- =====================================================

-- 9.1 分析表以更新统计信息
ANALYZE photos;
ANALYZE tags;
ANALYZE photo_tags;

-- =====================================================
-- 迁移完成
-- =====================================================

-- 打印完成信息
DO $$
BEGIN
    RAISE NOTICE '=========================================';
    RAISE NOTICE '数据库优化迁移完成！';
    RAISE NOTICE '优化内容：';
    RAISE NOTICE '  ✓ photos表：字段类型优化、添加地理位置和AI状态';
    RAISE NOTICE '  ✓ tags表：添加使用次数统计和层级支持';
    RAISE NOTICE '  ✓ photo_tags表：统一source字段值';
    RAISE NOTICE '  ✓ 全文搜索索引：优化搜索性能';
    RAISE NOTICE '  ✓ 视图和触发器：自动统计和更新';
    RAISE NOTICE '  ✓ 搜索函数：智能照片搜索';
    RAISE NOTICE '=========================================';
END $$;

