/**
 * 错误提示组件
 * 用途：统一的错误信息展示
 * 
 * 功能：
 * - 显示错误图标和消息
 * - 提供重试按钮
 * - 支持不同的错误类型样式
 */

import { AlertCircle, RefreshCw, WifiOff, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface ErrorMessageProps {
  title?: string
  message: string
  type?: "error" | "warning" | "network"
  onRetry?: () => void
  className?: string
}

export function ErrorMessage({ 
  title = "出错了",
  message, 
  type = "error",
  onRetry,
  className 
}: ErrorMessageProps) {
  // 根据错误类型选择图标
  const Icon = type === "network" ? WifiOff : type === "warning" ? AlertTriangle : AlertCircle

  return (
    <Alert variant={type === "warning" ? "default" : "destructive"} className={className}>
      <Icon className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="mt-2">
        {/* 错误消息 */}
        <p className="mb-3">{message}</p>
        
        {/* 重试按钮（如果提供了onRetry回调） */}
        {onRetry && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRetry}
            className="gap-2"
          >
            <RefreshCw className="h-3 w-3" />
            重试
          </Button>
        )}
      </AlertDescription>
    </Alert>
  )
}

/**
 * 空状态组件
 * 用于无数据时的友好提示
 */
interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {/* 图标 */}
      {icon && (
        <div className="mb-4 text-muted-foreground">
          {icon}
        </div>
      )}
      
      {/* 标题 */}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      
      {/* 描述 */}
      {description && (
        <p className="text-sm text-muted-foreground mb-4 max-w-sm">
          {description}
        </p>
      )}
      
      {/* 操作按钮 */}
      {action}
    </div>
  )
}

