/**
 * 照片详情对话框
 * 
 * 功能：
 * - 大图预览
 * - 显示EXIF信息
 * - 显示AI分析结果
 * - 标签管理
 * - 照片信息编辑
 * 
 * 优化：
 * - 键盘快捷键（ESC关闭，左右箭头切换）
 * - 图片懒加载
 * - 响应式布局
 */

"use client"

import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { Photo } from "@/lib/types"
import { CATEGORIES } from "@/lib/types"
import {
  Calendar,
  MapPin,
  FileImage,
  Ruler,
  Camera,
  Sparkles,
  X,
  ChevronLeft,
  ChevronRight,
  Download,
  Trash2,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface PhotoDetailDialogProps {
  photo: Photo | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onPrevious?: () => void
  onNext?: () => void
  onDelete?: (photoId: string) => void
}

export function PhotoDetailDialog({
  photo,
  open,
  onOpenChange,
  onPrevious,
  onNext,
  onDelete,
}: PhotoDetailDialogProps) {
  // 键盘快捷键
  useEffect(() => {
    if (!open) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "Escape":
          onOpenChange(false)
          break
        case "ArrowLeft":
          onPrevious?.()
          break
        case "ArrowRight":
          onNext?.()
          break
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [open, onOpenChange, onPrevious, onNext])

  if (!photo) return null

  const categoryLabel = CATEGORIES.find((cat) => cat.value === photo.category)?.label || photo.category
  const uploadDate = photo.uploadedAt instanceof Date ? photo.uploadedAt : new Date(photo.uploadedAt)

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl h-[90vh] p-0 gap-0">
        {/* 关闭按钮 */}
        <button
          onClick={() => onOpenChange(false)}
          className="absolute right-4 top-4 z-10 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">关闭</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 h-full">
          {/* 左侧：图片预览 */}
          <div className="lg:col-span-2 relative bg-black flex items-center justify-center">
            {/* 图片 */}
            <img
              src={photo.url || "/placeholder.svg"}
              alt={photo.title}
              className="max-w-full max-h-full object-contain"
            />

            {/* 导航按钮 */}
            {onPrevious && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                onClick={onPrevious}
              >
                <ChevronLeft className="h-6 w-6" />
              </Button>
            )}
            {onNext && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                onClick={onNext}
              >
                <ChevronRight className="h-6 w-6" />
              </Button>
            )}
          </div>

          {/* 右侧：详细信息 */}
          <ScrollArea className="h-full">
            <div className="p-6 space-y-6">
              {/* 标题和分类 */}
              <div>
                <DialogHeader>
                  <DialogTitle className="text-2xl">{photo.title}</DialogTitle>
                </DialogHeader>
                <Badge variant="secondary" className="mt-2">
                  {categoryLabel}
                </Badge>
              </div>

              <Separator />

              {/* AI描述 */}
              {photo.description && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Sparkles className="h-4 w-4 text-blue-500" />
                    AI描述
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {photo.description}
                  </p>
                </div>
              )}

              {/* AI标签 */}
              {photo.tags && photo.tags.length > 0 && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">标签</div>
                  <div className="flex flex-wrap gap-2">
                    {photo.tags.map((tag, index) => (
                      <Badge
                        key={index}
                        variant={tag.source === 'ai' ? 'default' : 'secondary'}
                        className={cn(
                          tag.source === 'ai' && "bg-blue-500/90 hover:bg-blue-600/90"
                        )}
                      >
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <Separator />

              {/* 照片信息 */}
              <div className="space-y-3">
                <div className="text-sm font-medium">照片信息</div>
                
                {/* 上传时间 */}
                <div className="flex items-center gap-3 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">上传时间:</span>
                  <span>{uploadDate.toLocaleDateString("zh-CN", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                  })}</span>
                </div>

                {/* 文件名 */}
                <div className="flex items-center gap-3 text-sm">
                  <FileImage className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">文件名:</span>
                  <span className="truncate">{photo.filename || "未知"}</span>
                </div>

                {/* 文件大小 */}
                {photo.fileSize && (
                  <div className="flex items-center gap-3 text-sm">
                    <FileImage className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">大小:</span>
                    <span>{formatFileSize(photo.fileSize)}</span>
                  </div>
                )}

                {/* 尺寸 */}
                {photo.width && photo.height && (
                  <div className="flex items-center gap-3 text-sm">
                    <Ruler className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">尺寸:</span>
                    <span>{photo.width} × {photo.height} px</span>
                  </div>
                )}

                {/* 地点（如果有） */}
                {photo.location && (
                  <div className="flex items-center gap-3 text-sm">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">地点:</span>
                    <span>{photo.location}</span>
                  </div>
                )}

                {/* 相机信息（如果有EXIF） */}
                {photo.exif_data?.camera && (
                  <div className="flex items-center gap-3 text-sm">
                    <Camera className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">相机:</span>
                    <span>{photo.exif_data.camera}</span>
                  </div>
                )}
              </div>

              <Separator />

              {/* 操作按钮 */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={() => {
                    // 下载图片
                    const link = document.createElement('a')
                    link.href = photo.url
                    link.download = photo.filename || 'photo.jpg'
                    link.click()
                  }}
                >
                  <Download className="h-4 w-4" />
                  下载
                </Button>
                
                {onDelete && (
                  <Button
                    variant="destructive"
                    className="gap-2"
                    onClick={() => {
                      if (confirm('确定要删除这张照片吗？')) {
                        onDelete(photo.id)
                        onOpenChange(false)
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                    删除
                  </Button>
                )}
              </div>
            </div>
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  )
}

