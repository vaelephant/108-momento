"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { 
  Users, 
  Search, 
  Calendar, 
  Mail, 
  Image, 
  MoreHorizontal,
  UserPlus,
  Trash2,
  Eye
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at: string
  photoCount: number
  lastActive?: string
}

export function UserList() {
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [sortBy, setSortBy] = useState<"username" | "created_at" | "photoCount">("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")

  useEffect(() => {
    loadUsers()
  }, [])

  useEffect(() => {
    filterAndSortUsers()
  }, [users, searchTerm, sortBy, sortOrder])

  const loadUsers = async () => {
    setIsLoading(true)
    
    try {
      // 从数据库获取用户列表
      const response = await fetch('/api/users')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '获取用户列表失败')
      }

      const allUsers: User[] = data.users
      
      // 从localStorage获取照片数据
      const allPhotos: any[] = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key?.startsWith('user_photos_') || key === 'user_photos') {
          const photoData = localStorage.getItem(key)
          if (photoData) {
            try {
              const photos = JSON.parse(photoData)
              allPhotos.push(...photos)
            } catch (e) {
              console.error('Failed to parse photo data:', e)
            }
          }
        }
      }

      const usersWithPhotoCount = allUsers.map(user => ({
        ...user,
        photoCount: allPhotos.filter(photo => photo.userId === user.id).length,
        lastActive: user.updated_at
      }))
      
      setUsers(usersWithPhotoCount)
    } catch (error) {
      console.error('Failed to load users:', error)
      setUsers([])
    } finally {
      setIsLoading(false)
    }
  }

  const filterAndSortUsers = () => {
    let filtered = users.filter(user => 
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    )

    // 排序
    filtered.sort((a, b) => {
      let aValue, bValue
      
      switch (sortBy) {
        case "username":
          aValue = a.username.toLowerCase()
          bValue = b.username.toLowerCase()
          break
        case "created_at":
          aValue = new Date(a.created_at).getTime()
          bValue = new Date(b.created_at).getTime()
          break
        case "photoCount":
          aValue = a.photoCount
          bValue = b.photoCount
          break
        default:
          return 0
      }

      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    setFilteredUsers(filtered)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getInitials = (username: string) => {
    return username.charAt(0).toUpperCase()
  }

  const handleSort = (field: "username" | "created_at" | "photoCount") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortBy(field)
      setSortOrder("desc")
    }
  }

  const handleDeleteUser = (userId: number) => {
    if (confirm('确定要删除这个用户吗？此操作不可撤销。')) {
      // 删除用户数据
      localStorage.removeItem('user_data')
      localStorage.removeItem(`user_data_${userId}`)
      localStorage.removeItem('user_photos')
      localStorage.removeItem(`user_photos_${userId}`)
      
      // 重新加载用户列表
      loadUsers()
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>加载用户列表中...</p>
        </div>
      </div>
    )
  }

  return (
    <Card className="bg-white shadow-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Users className="h-7 w-7 text-gray-700" />
              用户列表
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              共 {users.length} 个注册用户
            </CardDescription>
          </div>
          <Button onClick={loadUsers} variant="outline" size="sm" className="border-gray-300 text-gray-700">
            刷新
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* 搜索和筛选 */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-500" />
            <Input
              placeholder="搜索用户名或邮箱..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 h-11 text-base border-gray-300"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-base text-gray-600">排序:</span>
            <Button
              variant={sortBy === "username" ? "default" : "outline"}
              size="sm"
              onClick={() => handleSort("username")}
              className="text-sm border-gray-300 text-gray-700"
            >
              用户名
            </Button>
            <Button
              variant={sortBy === "created_at" ? "default" : "outline"}
              size="sm"
              onClick={() => handleSort("created_at")}
              className="text-sm border-gray-300 text-gray-700"
            >
              注册时间
            </Button>
            <Button
              variant={sortBy === "photoCount" ? "default" : "outline"}
              size="sm"
              onClick={() => handleSort("photoCount")}
              className="text-sm border-gray-300 text-gray-700"
            >
              照片数
            </Button>
          </div>
        </div>

        {/* 用户表格 */}
        {filteredUsers.length > 0 ? (
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>用户</TableHead>
                  <TableHead>邮箱</TableHead>
                  <TableHead>照片数</TableHead>
                  <TableHead>注册时间</TableHead>
                  <TableHead>最后活跃</TableHead>
                  <TableHead className="w-[50px]">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-primary/10 text-primary text-base">
                            {getInitials(user.username)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium text-base">{user.username}</div>
                          <div className="text-sm text-muted-foreground">ID: {user.id}</div>
                        </div>
                      </div>
                    </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Mail className="h-5 w-5 text-gray-500" />
                            <span className="text-base text-gray-900">{user.email}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Image className="h-5 w-5 text-gray-500" />
                            <Badge variant="secondary" className="text-sm bg-red-100 text-red-800">
                              {user.photoCount} 张
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-gray-500" />
                            <span className="text-base text-gray-900">
                              {formatDate(user.created_at)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className="text-base text-gray-600">
                            {user.lastActive ? formatDate(user.lastActive) : '未知'}
                          </span>
                        </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem className="text-base">
                            <Eye className="h-4 w-4 mr-2" />
                            查看详情
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-destructive text-base"
                            onClick={() => handleDeleteUser(user.id)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            删除用户
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-12">
            <Users className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-medium mb-2">
              {searchTerm ? '未找到匹配的用户' : '暂无用户数据'}
            </h3>
            <p className="text-base text-muted-foreground">
              {searchTerm ? '尝试调整搜索条件' : '用户注册后将显示在这里'}
            </p>
          </div>
        )}

      </CardContent>
    </Card>
  )
}
