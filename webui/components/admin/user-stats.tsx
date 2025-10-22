"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Users, Calendar, Image, Database } from "lucide-react"
import { format, subDays } from "date-fns"

interface UserStats {
  totalUsers: number
  totalPhotos: number
  recentUsers: Array<{
    id: number
    username: string
    email: string
    created_at: string
    photoCount: number
  }>
  dailyStats: Array<{
    date: string
    newUsers: number
    newPhotos: number
  }>
}

export function UserStats() {
  const [stats, setStats] = useState<UserStats>({
    totalUsers: 0,
    totalPhotos: 0,
    recentUsers: [],
    dailyStats: []
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setIsLoading(true)
    
    try {
      // 从数据库获取统计数据
      const response = await fetch('/api/stats')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '获取统计数据失败')
      }

      const { totalUsers, recentUsers } = data.stats
      
      // 从localStorage获取照片数据（照片仍然使用localStorage）
      const allPhotoData = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key?.startsWith('user_photos_') || key === 'user_photos') {
          const photoData = localStorage.getItem(key)
          if (photoData) {
            try {
              const photos = JSON.parse(photoData)
              allPhotoData.push(...photos)
            } catch (e) {
              console.error('Failed to parse photo data:', e)
            }
          }
        }
      }

      const totalPhotos = allPhotoData.length

      // 获取最近用户（按创建时间排序）
      const recentUsersWithPhotoCount = recentUsers
        .slice(0, 10)
        .map(user => ({
          ...user,
          photoCount: allPhotoData.filter(photo => photo.userId === user.id).length
        }))

      // 计算每日统计（最近7天）
      const dailyStatsMap = new Map<string, { newUsers: number; newPhotos: number }>()
      
      // 初始化最近7天的日期
      for (let i = 0; i < 7; i++) {
        const date = subDays(new Date(), i)
        const dateString = format(date, 'yyyy-MM-dd')
        dailyStatsMap.set(dateString, { newUsers: 0, newPhotos: 0 })
      }

      // 统计用户注册
      recentUsers.forEach(user => {
        const userDate = format(new Date(user.created_at), 'yyyy-MM-dd')
        if (dailyStatsMap.has(userDate)) {
          dailyStatsMap.get(userDate)!.newUsers++
        }
      })

      // 统计照片上传
      allPhotoData.forEach(photo => {
        const photoDate = format(new Date(photo.uploadedAt), 'yyyy-MM-dd')
        if (dailyStatsMap.has(photoDate)) {
          dailyStatsMap.get(photoDate)!.newPhotos++
        }
      })

      const dailyStats = Array.from(dailyStatsMap.entries())
        .sort(([dateA], [dateB]) => new Date(dateA).getTime() - new Date(dateB).getTime())
        .map(([date, data]) => ({ date, ...data }))

      setStats({
        totalUsers,
        totalPhotos,
        averagePhotos: totalUsers > 0 ? totalPhotos / totalUsers : 0,
        recentUsers: recentUsersWithPhotoCount,
        dailyStats,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="bg-white shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-6 w-24 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-6 w-6 bg-gray-200 rounded animate-pulse"></div>
              </CardHeader>
              <CardContent>
                <div className="h-12 w-16 bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="h-4 w-20 bg-gray-200 rounded animate-pulse"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-white shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-medium">总用户数</CardTitle>
            <Users className="h-6 w-6 text-gray-700" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-gray-900">{stats.totalUsers}</div>
            <p className="text-base text-gray-600">
              注册用户总数
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-medium">总照片数</CardTitle>
            <Image className="h-6 w-6 text-gray-700" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-gray-900">{stats.totalPhotos}</div>
            <p className="text-base text-gray-600">
              上传照片总数
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-lg font-medium">平均照片</CardTitle>
            <Database className="h-6 w-6 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-red-600">
              {stats.totalUsers > 0 ? Math.round(stats.totalPhotos / stats.totalUsers) : 0}
            </div>
            <p className="text-base text-gray-600">
              每用户平均照片数
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 最近用户 */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-xl">最近注册用户</CardTitle>
          <CardDescription className="text-lg">最近注册的10个用户</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.recentUsers.length > 0 ? (
              stats.recentUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-6 border rounded-lg bg-gray-50">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-lg text-gray-900">{user.username}</span>
                      <Badge variant="secondary" className="text-base bg-red-100 text-red-800">{user.photoCount} 张照片</Badge>
                    </div>
                    <p className="text-lg text-gray-600">{user.email}</p>
                    <p className="text-base text-gray-500">
                      注册时间: {formatDate(user.created_at)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                暂无用户数据
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 每日统计 */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-xl">最近7天统计</CardTitle>
          <CardDescription className="text-lg">每日新增用户和照片数量</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.dailyStats.length > 0 ? (
              stats.dailyStats.map((day, index) => (
                <div key={day.date} className="flex items-center justify-between p-5 border rounded-lg bg-gray-50">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-6 w-6 text-gray-600" />
                    <span className="font-medium text-lg text-gray-900">{formatDate(day.date)}</span>
                  </div>
                  <div className="flex gap-4">
                    <Badge variant="outline" className="text-base border-gray-300 text-gray-700">
                      +{day.newUsers} 用户
                    </Badge>
                    <Badge variant="outline" className="text-base border-red-300 text-red-700">
                      +{day.newPhotos} 照片
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                暂无统计数据
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}