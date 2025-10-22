"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { apiClient, type User } from './api'
// import { SecureStorage, StorageKeys } from './secure-storage'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false) // 暂时禁用加载状态

  useEffect(() => {
    // 从Cookie恢复用户登录状态
    const initAuth = async () => {
      if (typeof window !== 'undefined') {
        try {
          const userCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('user_data='))
          
          if (userCookie) {
            const userData = decodeURIComponent(userCookie.split('=')[1])
            const user = JSON.parse(userData)
            setUser(user)
            console.log('🔍 [Auth] 从Cookie恢复用户登录状态:', user.username)
            
            // 恢复登录状态后，加载照片
            console.log('🔄 [Auth] 恢复登录后加载照片...')
            try {
              const { photoStore } = await import('./photo-store')
              await photoStore.loadPhotos()
              console.log('✅ [Auth] 照片加载完成')
            } catch (error) {
              console.error('❌ [Auth] 照片加载失败:', error)
            }
          }
        } catch (error) {
          console.error('Failed to parse user cookie:', error)
          // 清除无效的Cookie
          document.cookie = 'user_data=; path=/; max-age=0'
        }
      }
      setIsLoading(false)
    }
    
    initAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      console.log('🚀 [Auth] 开始登录...')
      
      // 调用后端API登录
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      console.log('📡 [Auth] API响应状态:', response.status)
      const data = await response.json()
      console.log('📦 [Auth] API响应数据:', data)

      if (!response.ok) {
        throw new Error(data.error || '登录失败')
      }

      console.log('✅ [Auth] 设置用户状态...')
      setUser(data.user)
      
      // 保存到Cookie（30天有效期）
      if (typeof window !== 'undefined') {
        const userData = JSON.stringify(data.user)
        const encodedData = encodeURIComponent(userData)
        document.cookie = `user_data=${encodedData}; path=/; max-age=${30 * 24 * 60 * 60}`
        console.log('🍪 [Auth] 用户数据已保存到Cookie')
      }
      
      console.log('✅ [Auth] 用户状态已设置')
      
      // 恢复照片加载功能
      console.log('🔄 [Auth] 开始加载照片...')
      try {
        const { photoStore } = await import('./photo-store')
        console.log('📦 [Auth] PhotoStore导入成功')
        await photoStore.loadPhotos()
        console.log('✅ [Auth] 照片加载完成')
      } catch (error) {
        console.error('❌ [Auth] 照片加载失败:', error)
        // 不抛出错误，让登录继续
      }
      
      console.log('🎉 [Auth] 登录完成！')
      
    } catch (error) {
      console.error('❌ [Auth] 登录失败:', error)
      throw error
    }
  }

  const register = async (username: string, email: string, password: string) => {
    try {
      console.log('🚀 [Auth] 开始注册...')
      
      // 调用后端API注册
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      })

      console.log('📡 [Auth] 注册API响应状态:', response.status)
      const data = await response.json()
      console.log('📦 [Auth] 注册API响应数据:', data)

      if (!response.ok) {
        throw new Error(data.error || '注册失败')
      }

      console.log('✅ [Auth] 设置用户状态...')
      setUser(data.user)
      
      // 保存到Cookie（30天有效期）
      if (typeof window !== 'undefined') {
        const userData = JSON.stringify(data.user)
        const encodedData = encodeURIComponent(userData)
        document.cookie = `user_data=${encodedData}; path=/; max-age=${30 * 24 * 60 * 60}`
        console.log('🍪 [Auth] 用户数据已保存到Cookie')
      }
      
      console.log('✅ [Auth] 用户状态已设置')
      
      // 注册后加载照片（虽然是新用户，但保持一致性）
      console.log('🔄 [Auth] 开始加载照片...')
      try {
        const { photoStore } = await import('./photo-store')
        console.log('📦 [Auth] PhotoStore导入成功')
        await photoStore.loadPhotos()
        console.log('✅ [Auth] 照片加载完成')
      } catch (error) {
        console.error('❌ [Auth] 照片加载失败:', error)
        // 不抛出错误，让注册继续
      }
      
      console.log('🎉 [Auth] 注册完成！')
      
    } catch (error) {
      console.error('❌ [Auth] 注册失败:', error)
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    
    // 清除Cookie
    if (typeof window !== 'undefined') {
      document.cookie = 'user_data=; path=/; max-age=0'
      console.log('🍪 [Auth] Cookie已清除')
    }
    
    console.log('🔓 [Auth] 用户已退出登录')
    
    // 清空内存中的照片数据
    try {
      const { photoStore } = require('./photo-store')
      photoStore.photos = []
      photoStore.cachedSnapshot = []
      photoStore.notifyListeners()
    } catch (error) {
      console.error('❌ [Auth] 照片数据清理失败:', error)
    }
  }

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
