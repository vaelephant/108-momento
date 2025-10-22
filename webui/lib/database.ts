import { Pool } from 'pg'

// 数据库连接池
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
})

export interface User {
  id: number
  username: string
  email: string
  hashed_password: string
  created_at: string
  updated_at: string
}

export interface CreateUserData {
  username: string
  email: string
  hashed_password: string
}

export class DatabaseService {
  // 创建用户
  static async createUser(userData: CreateUserData): Promise<User> {
    const client = await pool.connect()
    try {
      const query = `
        INSERT INTO users (username, email, hashed_password, created_at, updated_at)
        VALUES ($1, $2, $3, NOW(), NOW())
        RETURNING id, username, email, hashed_password, created_at, updated_at
      `
      const values = [userData.username, userData.email, userData.hashed_password]
      const result = await client.query(query, values)
      return result.rows[0]
    } finally {
      client.release()
    }
  }

  // 根据用户名查找用户
  static async findUserByUsername(username: string): Promise<User | null> {
    const client = await pool.connect()
    try {
      const query = 'SELECT * FROM users WHERE username = $1'
      const result = await client.query(query, [username])
      return result.rows[0] || null
    } finally {
      client.release()
    }
  }

  // 根据邮箱查找用户
  static async findUserByEmail(email: string): Promise<User | null> {
    const client = await pool.connect()
    try {
      const query = 'SELECT * FROM users WHERE email = $1'
      const result = await client.query(query, [email])
      return result.rows[0] || null
    } finally {
      client.release()
    }
  }

  // 获取所有用户
  static async getAllUsers(): Promise<User[]> {
    const client = await pool.connect()
    try {
      const query = 'SELECT * FROM users ORDER BY created_at DESC'
      const result = await client.query(query)
      return result.rows
    } finally {
      client.release()
    }
  }

  // 获取用户统计
  static async getUserStats(): Promise<{
    totalUsers: number
    recentUsers: User[]
  }> {
    const client = await pool.connect()
    try {
      // 获取总用户数
      const totalResult = await client.query('SELECT COUNT(*) as count FROM users')
      const totalUsers = parseInt(totalResult.rows[0].count)

      // 获取最近注册的10个用户
      const recentResult = await client.query(`
        SELECT * FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
      `)
      const recentUsers = recentResult.rows

      return { totalUsers, recentUsers }
    } finally {
      client.release()
    }
  }

  // 测试数据库连接
  static async testConnection(): Promise<boolean> {
    try {
      const client = await pool.connect()
      await client.query('SELECT 1')
      client.release()
      return true
    } catch (error) {
      console.error('Database connection failed:', error)
      return false
    }
  }
}

export default DatabaseService
