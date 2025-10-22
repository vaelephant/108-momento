-- 查询最新上传照片的EXIF信息
-- 使用方法: psql -d momento -f check_exif_data.sql

\echo '=========================================='
\echo '📷 最新上传照片的EXIF信息'
\echo '=========================================='
\echo ''

-- 查询最新5张照片的完整信息
SELECT 
    id AS "照片ID",
    filename AS "文件名",
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS "上传时间",
    TO_CHAR(taken_at, 'YYYY-MM-DD HH24:MI:SS') AS "拍摄时间",
    exif_data->>'camera' AS "相机",
    exif_data->>'location' AS "GPS位置",
    exif_data->>'latitude' AS "纬度",
    exif_data->>'longitude' AS "经度",
    CASE 
        WHEN exif_data IS NOT NULL THEN '✅ 有'
        ELSE '❌ 无'
    END AS "EXIF数据"
FROM photos
ORDER BY created_at DESC
LIMIT 5;

\echo ''
\echo '=========================================='
\echo '📊 EXIF数据统计'
\echo '=========================================='
\echo ''

-- 统计有无EXIF数据的照片数量
SELECT 
    COUNT(*) AS "总照片数",
    COUNT(exif_data) AS "有EXIF数据",
    COUNT(*) - COUNT(exif_data) AS "无EXIF数据",
    ROUND(COUNT(exif_data)::numeric / COUNT(*)::numeric * 100, 2) || '%' AS "EXIF覆盖率"
FROM photos;

\echo ''
\echo '=========================================='
\echo '📅 有拍摄时间的照片'
\echo '=========================================='
\echo ''

-- 查询有拍摄时间的照片
SELECT 
    id AS "照片ID",
    filename AS "文件名",
    TO_CHAR(taken_at, 'YYYY-MM-DD HH24:MI:SS') AS "拍摄时间",
    exif_data->>'camera' AS "相机型号"
FROM photos
WHERE taken_at IS NOT NULL
ORDER BY taken_at DESC
LIMIT 10;

\echo ''
\echo '=========================================='
\echo '📍 有GPS位置的照片'
\echo '=========================================='
\echo ''

-- 查询有GPS信息的照片
SELECT 
    id AS "照片ID",
    filename AS "文件名",
    exif_data->>'location' AS "位置",
    exif_data->>'latitude' AS "纬度",
    exif_data->>'longitude' AS "经度"
FROM photos
WHERE exif_data->>'latitude' IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;

\echo ''
\echo '=========================================='
\echo '📷 相机型号统计'
\echo '=========================================='
\echo ''

-- 统计不同相机型号的照片数量
SELECT 
    exif_data->>'camera' AS "相机型号",
    COUNT(*) AS "照片数量"
FROM photos
WHERE exif_data->>'camera' IS NOT NULL
GROUP BY exif_data->>'camera'
ORDER BY COUNT(*) DESC;

\echo ''
\echo '=========================================='
\echo '🔍 查看完整EXIF数据示例'
\echo '=========================================='
\echo ''

-- 查看最新一张有EXIF的照片的完整数据
SELECT 
    id AS "照片ID",
    filename AS "文件名",
    jsonb_pretty(exif_data) AS "完整EXIF数据"
FROM photos
WHERE exif_data IS NOT NULL
ORDER BY created_at DESC
LIMIT 1;

