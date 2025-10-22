import { NextRequest, NextResponse } from 'next/server'
import { DatabaseService } from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    const users = await DatabaseService.getAllUsers()
    
    // 移除密码字段
    const usersWithoutPasswords = users.map(({ hashed_password, ...user }) => user)

    return NextResponse.json({
      success: true,
      users: usersWithoutPasswords
    })

  } catch (error) {
    console.error('获取用户列表失败:', error)
    return NextResponse.json(
      { error: '获取用户列表失败' },
      { status: 500 }
    )
  }
}
