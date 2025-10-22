import { NextRequest, NextResponse } from 'next/server'
import { Pool } from 'pg'

// 数据库连接池
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
})

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get('userId')
    const limit = parseInt(searchParams.get('limit') || '20')

    if (!userId) {
      return NextResponse.json(
        { error: '缺少用户ID' },
        { status: 400 }
      )
    }

    console.log('🏷️  [Tags API] 获取热门标签, 用户:', userId)

    const client = await pool.connect()
    try {
      // 查询用户照片的热门标签
      const query = `
        SELECT 
          t.id,
          t.name,
          t.zh,
          t.category,
          t.use_count,
          COUNT(DISTINCT pt.photo_id) as photo_count
        FROM tags t
        JOIN photo_tags pt ON t.id = pt.tag_id
        JOIN photos p ON pt.photo_id = p.id
        WHERE p.user_id = $1
        GROUP BY t.id, t.name, t.zh, t.category, t.use_count
        ORDER BY photo_count DESC, t.use_count DESC
        LIMIT $2
      `
      
      const result = await client.query(query, [userId, limit])
      
      console.log('🏷️  [Tags API] 查询到', result.rows.length, '个标签')
      
      const tags = result.rows.map(row => ({
        id: row.id,
        name: row.name,
        zh: row.zh,
        category: row.category,
        useCount: row.use_count,
        photoCount: parseInt(row.photo_count)
      }))

      return NextResponse.json({
        success: true,
        tags: tags,
        count: tags.length
      })

    } finally {
      client.release()
    }

  } catch (error) {
    console.error('❌ [Tags API] 获取热门标签失败:', error)
    return NextResponse.json(
      { error: '获取热门标签失败' },
      { status: 500 }
    )
  }
}

