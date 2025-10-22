import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { DatabaseService } from '@/lib/database'

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json()

    // 验证输入
    if (!username || !password) {
      return NextResponse.json(
        { error: '用户名和密码都是必填项' },
        { status: 400 }
      )
    }

    // 查找用户
    const user = await DatabaseService.findUserByUsername(username)
    if (!user) {
      return NextResponse.json(
        { error: '用户名或密码错误' },
        { status: 401 }
      )
    }

    // 验证密码
    const isValidPassword = await bcrypt.compare(password, user.hashed_password)
    if (!isValidPassword) {
      return NextResponse.json(
        { error: '用户名或密码错误' },
        { status: 401 }
      )
    }

    // 生成JWT token
    const jwt = require('jsonwebtoken')
    const secretKey = process.env.SECRET_KEY || 'your-secret-key-here-change-in-production'
    
    console.log('🔑 [Next.js API] 生成JWT token:')
    console.log('  - 用户ID:', user.id)
    console.log('  - SECRET_KEY:', secretKey.substring(0, 10) + '...')
    console.log('  - 算法: HS256 (默认)')
    
    const token = jwt.sign(
      { 
        sub: user.id,  // FastAPI期望的字段名
        username: user.username,
        email: user.email 
      },
      secretKey,
      { expiresIn: '30d' }
    )
    
    console.log('✅ [Next.js API] JWT token生成成功:', token.substring(0, 20) + '...')

    // 返回用户信息和token
    const { hashed_password: _, ...userWithoutPassword } = user

    return NextResponse.json({
      success: true,
      user: userWithoutPassword,
      token: token
    })

  } catch (error) {
    console.error('登录失败:', error)
    return NextResponse.json(
      { error: '登录失败，请重试' },
      { status: 500 }
    )
  }
}
