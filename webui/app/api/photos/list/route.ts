import { NextRequest, NextResponse } from 'next/server'
import { Pool } from 'pg'

// 数据库连接池
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
})

export async function GET(request: NextRequest) {
  try {
    // 从查询参数获取用户ID
    const searchParams = request.nextUrl.searchParams
    const userId = searchParams.get('userId')

    if (!userId) {
      return NextResponse.json(
        { error: '缺少用户ID' },
        { status: 400 }
      )
    }

    console.log('📡 [Photos API] 获取用户照片列表:', userId)

    // 从数据库查询用户的照片和标签
    const client = await pool.connect()
    try {
      // 先查询照片
      const photosQuery = `
        SELECT 
          id,
          filename,
          storage_path,
          file_size,
          caption,
          created_at,
          taken_at,
          exif_data,
          user_id,
          dominant_colors
        FROM photos 
        WHERE user_id = $1 
        ORDER BY created_at DESC
      `
      const photosResult = await client.query(photosQuery, [userId])

      console.log('📸 [Photos API] 查询到', photosResult.rows.length, '张照片')

      // 为每张照片查询标签
      const photos = await Promise.all(photosResult.rows.map(async (row) => {
        // storage_path 格式: uploads/{user_id}/{filename}
        const photoUrl = `/${row.storage_path}`
        
        // 查询照片的标签
        const tagsQuery = `
          SELECT t.name, pt.confidence, pt.source
          FROM photo_tags pt
          JOIN tags t ON pt.tag_id = t.id
          WHERE pt.photo_id = $1
          ORDER BY pt.confidence DESC
        `
        const tagsResult = await client.query(tagsQuery, [row.id])
        const tags = tagsResult.rows.map(tag => ({
          name: tag.name,
          confidence: tag.confidence,
          source: tag.source
        }))
        
        console.log('🏷️  [Photos API] 照片', row.id, '标签:', tags.map(t => t.name).join(', '))
        
        // 构建EXIF数据
        const exifData = row.exif_data ? {
          ...row.exif_data,
          dateTaken: row.taken_at  // 使用数据库的taken_at字段
        } : undefined
        
        if (exifData) {
          console.log('📅 [Photos API] 照片', row.id, 'EXIF拍摄时间:', row.taken_at)
        }
        
        return {
          id: row.id.toString(),
          url: photoUrl,
          title: row.caption || row.filename.replace(/\.[^/.]+$/, ""),
          category: 'other',
          uploadedAt: row.created_at,
          description: row.caption,
          tags: tags,
          userId: row.user_id,
          aiProcessed: tags.length > 0,
          aiError: null,
          dominantColors: row.dominant_colors,
          exif_data: exifData,  // 添加EXIF数据
        }
      }))

      return NextResponse.json({
        success: true,
        photos: photos,
        count: photos.length
      })

    } finally {
      client.release()
    }

  } catch (error) {
    console.error('❌ [Photos API] 获取照片列表失败:', error)
    return NextResponse.json(
      { error: '获取照片列表失败' },
      { status: 500 }
    )
  }
}

