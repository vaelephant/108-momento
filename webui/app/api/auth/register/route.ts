import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { DatabaseService } from '@/lib/database'

export async function POST(request: NextRequest) {
  try {
    const { username, email, password } = await request.json()

    // 验证输入
    if (!username || !email || !password) {
      return NextResponse.json(
        { error: '用户名、邮箱和密码都是必填项' },
        { status: 400 }
      )
    }

    // 检查用户名是否已存在
    const existingUser = await DatabaseService.findUserByUsername(username)
    if (existingUser) {
      return NextResponse.json(
        { error: '用户名已存在' },
        { status: 400 }
      )
    }

    // 检查邮箱是否已存在
    const existingEmail = await DatabaseService.findUserByEmail(email)
    if (existingEmail) {
      return NextResponse.json(
        { error: '邮箱已被注册' },
        { status: 400 }
      )
    }

    // 加密密码
    const hashed_password = await bcrypt.hash(password, 10)

    // 创建用户
    const user = await DatabaseService.createUser({
      username,
      email,
      hashed_password
    })

    // 返回用户信息（不包含密码）
    const { hashed_password: _, ...userWithoutPassword } = user

    return NextResponse.json({
      success: true,
      user: userWithoutPassword
    })

  } catch (error) {
    console.error('注册失败:', error)
    return NextResponse.json(
      { error: '注册失败，请重试' },
      { status: 500 }
    )
  }
}
