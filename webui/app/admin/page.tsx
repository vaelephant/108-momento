"use client"

import { AdminProvider, useAdmin } from "@/lib/admin-auth"
import { AdminLogin } from "@/components/admin/admin-login"
import { UserStats } from "@/components/admin/user-stats"
import { UserList } from "@/components/admin/user-list"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LogOut, Users, BarChart3, Settings, List } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

function AdminDashboard() {
  const { isAdmin, adminLogout } = useAdmin()
  const { toast } = useToast()

  const handleLogout = () => {
    adminLogout()
    toast({
      title: "已退出登录",
      description: "您已安全退出管理后台",
    })
  }

  if (!isAdmin) {
    return <AdminLogin />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Users className="h-7 w-7 text-primary" />
                <h1 className="text-4xl font-bold">Momento 管理后台</h1>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                退出登录
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* 欢迎卡片 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <BarChart3 className="h-7 w-7" />
                数据概览
              </CardTitle>
              <CardDescription className="text-lg">
                查看用户注册统计和系统使用情况
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-8 border rounded-lg bg-white shadow-sm">
                  <div className="text-4xl font-bold text-gray-900">Momento</div>
                  <p className="text-lg text-gray-600 mt-3">AI照片管理系统</p>
                </div>
                <div className="text-center p-8 border rounded-lg bg-white shadow-sm">
                  <div className="text-4xl font-bold text-gray-700">前端存储</div>
                  <p className="text-lg text-gray-600 mt-3">基于localStorage</p>
                </div>
                <div className="text-center p-8 border rounded-lg bg-white shadow-sm">
                  <div className="text-4xl font-bold text-red-600">实时统计</div>
                  <p className="text-lg text-gray-600 mt-3">动态数据更新</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 标签页内容 */}
          <Tabs defaultValue="stats" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-16">
              <TabsTrigger value="stats" className="flex items-center gap-2 text-lg">
                <BarChart3 className="h-6 w-6" />
                数据统计
              </TabsTrigger>
              <TabsTrigger value="users" className="flex items-center gap-2 text-lg">
                <List className="h-6 w-6" />
                用户列表
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="stats" className="space-y-6">
              <UserStats />
            </TabsContent>
            
            <TabsContent value="users" className="space-y-6">
              <UserList />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}

export default function AdminPage() {
  return (
    <AdminProvider>
      <AdminDashboard />
    </AdminProvider>
  )
}
