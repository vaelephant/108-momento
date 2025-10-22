-- Momento AI Photo Management System 数据库初始化脚本 - 简化版本

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    default_language VARCHAR(10) DEFAULT 'zh',
    auto_tagging BOOLEAN DEFAULT TRUE,
    privacy_level VARCHAR(20) DEFAULT 'private',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建照片表（不使用向量）
CREATE TABLE IF NOT EXISTS photos (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_path VARCHAR(500) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    width INTEGER,
    height INTEGER,
    exif_data JSONB,
    caption TEXT,
    dominant_colors TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    zh VARCHAR(100),
    ja VARCHAR(100),
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建照片标签关联表
CREATE TABLE IF NOT EXISTS photo_tags (
    photo_id BIGINT NOT NULL REFERENCES photos(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    confidence REAL CHECK (confidence BETWEEN 0 AND 1),
    bbox JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (photo_id, tag_id, source)
);

-- 创建标签别名表
CREATE TABLE IF NOT EXISTS tag_alias (
    alias VARCHAR(100) PRIMARY KEY,
    canonical VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建相册表
CREATE TABLE IF NOT EXISTS albums (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cover_photo_id BIGINT REFERENCES photos(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建相册照片关联表
CREATE TABLE IF NOT EXISTS album_photos (
    album_id BIGINT NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    photo_id BIGINT NOT NULL REFERENCES photos(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (album_id, photo_id)
);

-- 创建用户偏好设置表
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_language VARCHAR(10) DEFAULT 'zh',
    auto_tagging BOOLEAN DEFAULT TRUE,
    privacy_level VARCHAR(20) DEFAULT 'private',
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id);
CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos(created_at);
CREATE INDEX IF NOT EXISTS idx_photos_user_id_created_at ON photos(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category);
CREATE INDEX IF NOT EXISTS idx_tags_name_category ON tags(name, category);
CREATE INDEX IF NOT EXISTS idx_photo_tags_confidence ON photo_tags(confidence);
CREATE INDEX IF NOT EXISTS idx_photo_tags_source ON photo_tags(source);
CREATE INDEX IF NOT EXISTS idx_albums_user_id ON albums(user_id);
CREATE INDEX IF NOT EXISTS idx_albums_created_at ON albums(created_at);
CREATE INDEX IF NOT EXISTS idx_album_photos_sort_order ON album_photos(album_id, sort_order);

-- 插入基础标签数据
INSERT INTO tags (name, zh, ja, category, description) VALUES
('cat', '猫', '猫', 'object', '猫科动物'),
('dog', '狗', '犬', 'object', '犬科动物'),
('car', '汽车', '車', 'object', '机动车辆'),
('tree', '树', '木', 'object', '树木植物'),
('building', '建筑', '建物', 'object', '建筑物'),
('person', '人', '人', 'object', '人物'),
('food', '食物', '食べ物', 'object', '食物'),
('nature', '自然', '自然', 'scene', '自然风景'),
('sky', '天空', '空', 'scene', '天空'),
('water', '水', '水', 'scene', '水体'),
('mountain', '山', '山', 'scene', '山脉'),
('beach', '海滩', 'ビーチ', 'scene', '海滩'),
('city', '城市', '都市', 'scene', '城市景观'),
('street', '街道', '通り', 'scene', '街道'),
('indoor', '室内', '屋内', 'scene', '室内场景'),
('outdoor', '室外', '屋外', 'scene', '室外场景'),
('red', '红色', '赤', 'color', '红色'),
('blue', '蓝色', '青', 'color', '蓝色'),
('green', '绿色', '緑', 'color', '绿色'),
('yellow', '黄色', '黄', 'color', '黄色')
ON CONFLICT (name) DO NOTHING;
