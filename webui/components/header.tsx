"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Logo } from "@/components/logo"
import { AuthDialog } from "@/components/auth-dialog"
import { PhotoUpload } from "@/components/photo-upload"
import { useAuth } from "@/lib/auth"
import { useAdmin } from "@/lib/admin-auth"
import { List, LayoutGrid, Settings, User, LogOut, Search } from "lucide-react"
import Link from "next/link"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface HeaderProps {
  activeView: "timeline" | "categories"
  onViewChange: (view: "timeline" | "categories") => void
  searchQuery?: string
  onSearchChange?: (query: string) => void
}

export function Header({ activeView, onViewChange, searchQuery = "", onSearchChange }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth()
  const { isAdmin } = useAdmin()

  return (
    <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b border-border z-50">
      <div className="w-full px-6 py-3">
        <div className="flex items-center justify-between gap-4">
          {/* 左侧：Logo */}
          <div className="flex items-center">
            <Logo />
          </div>
            
          {/* 中间：搜索框 */}
          {isAuthenticated && onSearchChange && (
            <div className="flex-1 max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="搜索照片标签..."
                  value={searchQuery}
                  onChange={(e) => onSearchChange(e.target.value)}
                  className="pl-9 h-9 w-full"
                />
              </div>
            </div>
          )}

          {/* 右侧：操作按钮 */}
          <div className="flex items-center gap-2">
            {/* 视图切换按钮 */}
            {isAuthenticated && (
              <div className="flex items-center gap-1 border border-border rounded-lg p-1">
                <Button
                  variant={activeView === "timeline" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => onViewChange("timeline")}
                  className="h-8 w-8 p-0"
                  title="时间轴视图"
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button
                  variant={activeView === "categories" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => onViewChange("categories")}
                  className="h-8 w-8 p-0"
                  title="分类视图"
                >
                  <LayoutGrid className="h-4 w-4" />
                </Button>
              </div>
            )}

            {/* 上传照片或登录按钮 */}
            {isAuthenticated ? <PhotoUpload /> : <AuthDialog />}

            {/* 用户菜单 */}
            {isAuthenticated && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    <User className="h-4 w-4" />
                    <span className="hidden md:inline">{user?.username}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user?.username}</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {isAdmin && (
                    <>
                      <DropdownMenuItem asChild>
                        <Link href="/admin" className="cursor-pointer">
                          <Settings className="h-4 w-4 mr-2" />
                          管理后台
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                    </>
                  )}
                  <DropdownMenuItem onClick={logout} className="cursor-pointer text-destructive">
                    <LogOut className="h-4 w-4 mr-2" />
                    退出登录
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

