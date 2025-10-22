"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'

interface AdminContextType {
  isAdmin: boolean
  adminLogin: (password: string) => boolean
  adminLogout: () => void
}

const AdminContext = createContext<AdminContextType | undefined>(undefined)

export function AdminProvider({ children }: { children: React.ReactNode }) {
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    // 从Cookie检查admin状态
    if (typeof window !== 'undefined') {
      const adminCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('admin_logged_in='))
      
      if (adminCookie) {
        const adminStatus = adminCookie.split('=')[1]
        setIsAdmin(adminStatus === 'true')
        console.log('🔍 [Admin] 从Cookie恢复管理员状态')
      }
    }
  }, [])

  const adminLogin = (password: string): boolean => {
    // 简单的admin密码验证（实际应用中应该更安全）
    const adminPassword = 'admin123' // 默认密码
    if (password === adminPassword) {
      if (typeof window !== 'undefined') {
        document.cookie = `admin_logged_in=true; path=/; max-age=${30 * 24 * 60 * 60}`
        console.log('🍪 [Admin] 管理员状态已保存到Cookie')
      }
      setIsAdmin(true)
      return true
    }
    return false
  }

  const adminLogout = () => {
    if (typeof window !== 'undefined') {
      document.cookie = 'admin_logged_in=; path=/; max-age=0'
      console.log('🍪 [Admin] Cookie已清除')
    }
    setIsAdmin(false)
  }

  const value = {
    isAdmin,
    adminLogin,
    adminLogout,
  }

  return <AdminContext.Provider value={value}>{children}</AdminContext.Provider>
}

export function useAdmin() {
  const context = useContext(AdminContext)
  if (context === undefined) {
    throw new Error('useAdmin must be used within an AdminProvider')
  }
  return context
}
