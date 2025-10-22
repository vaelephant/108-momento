import { NextRequest, NextResponse } from 'next/server'
import { DatabaseService } from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    const stats = await DatabaseService.getUserStats()
    
    // 移除密码字段
    const recentUsersWithoutPasswords = stats.recentUsers.map(({ hashed_password, ...user }) => user)

    return NextResponse.json({
      success: true,
      stats: {
        totalUsers: stats.totalUsers,
        recentUsers: recentUsersWithoutPasswords
      }
    })

  } catch (error) {
    console.error('获取统计数据失败:', error)
    return NextResponse.json(
      { error: '获取统计数据失败' },
      { status: 500 }
    )
  }
}
