/**
 * Loading Spinner 组件
 * 用途：显示加载状态，提供良好的用户体验
 * 
 * 使用场景：
 * - 照片列表加载
 * - AI处理中
 * - 搜索加载
 */

import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  text?: string
  className?: string
}

export function LoadingSpinner({ 
  size = "md", 
  text, 
  className 
}: LoadingSpinnerProps) {
  // 根据size参数设置图标大小
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12"
  }

  return (
    <div className={cn("flex flex-col items-center justify-center gap-2", className)}>
      {/* 旋转的加载图标 */}
      <Loader2 className={cn(sizeClasses[size], "animate-spin text-primary")} />
      
      {/* 可选的加载文字提示 */}
      {text && (
        <p className="text-sm text-muted-foreground">{text}</p>
      )}
    </div>
  )
}

/**
 * 全屏Loading组件
 * 用于整页加载场景
 */
export function FullPageLoading({ text = "加载中..." }: { text?: string }) {
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <LoadingSpinner size="lg" text={text} />
    </div>
  )
}

/**
 * 卡片Loading骨架屏
 * 用于照片卡片加载占位
 */
export function PhotoCardSkeleton() {
  return (
    <div className="animate-pulse">
      {/* 图片占位 */}
      <div className="aspect-square bg-muted rounded-lg mb-2" />
      
      {/* 标题占位 */}
      <div className="h-4 bg-muted rounded w-3/4 mb-2" />
      
      {/* 信息占位 */}
      <div className="flex justify-between">
        <div className="h-3 bg-muted rounded w-1/4" />
        <div className="h-3 bg-muted rounded w-1/3" />
      </div>
    </div>
  )
}

