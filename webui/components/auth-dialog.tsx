"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuth } from "@/lib/auth"
import { useToast } from "@/hooks/use-toast"
import { LogIn, UserPlus } from "lucide-react"

export function AuthDialog() {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { login, register, isAuthenticated, user, logout } = useAuth()
  const { toast } = useToast()

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget)
    const username = formData.get("username") as string
    const password = formData.get("password") as string

    try {
      await login(username, password)
      toast({
        title: "登录成功",
        description: "欢迎回来！",
      })
      setOpen(false)
    } catch (error) {
      toast({
        title: "登录失败",
        description: "用户名或密码错误",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget)
    const username = formData.get("username") as string
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    try {
      await register(username, email, password)
      toast({
        title: "注册成功",
        description: "欢迎加入Momento！",
      })
      setOpen(false)
    } catch (error) {
      toast({
        title: "注册失败",
        description: "用户名或邮箱可能已存在",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    toast({
      title: "已退出登录",
      description: "感谢使用Momento！",
    })
  }

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">
          欢迎，{user.username}
        </span>
        <Button variant="outline" size="sm" onClick={handleLogout}>
          退出
        </Button>
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <LogIn className="h-4 w-4 mr-2" />
          登录
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>欢迎使用Momento</DialogTitle>
          <DialogDescription>
            登录或注册以开始管理您的照片
          </DialogDescription>
        </DialogHeader>
        
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">登录</TabsTrigger>
            <TabsTrigger value="register">注册</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-username">用户名</Label>
                <Input
                  id="login-username"
                  name="username"
                  placeholder="输入用户名"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password">密码</Label>
                <Input
                  id="login-password"
                  name="password"
                  type="password"
                  placeholder="输入密码"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "登录中..." : "登录"}
              </Button>
            </form>
          </TabsContent>
          
          <TabsContent value="register">
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-username">用户名</Label>
                <Input
                  id="register-username"
                  name="username"
                  placeholder="输入用户名"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="register-email">邮箱</Label>
                <Input
                  id="register-email"
                  name="email"
                  type="email"
                  placeholder="输入邮箱"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="register-password">密码</Label>
                <Input
                  id="register-password"
                  name="password"
                  type="password"
                  placeholder="输入密码"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "注册中..." : "注册"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
