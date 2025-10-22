/**
 * 照片卡片组件
 * 
 * 功能：
 * - 显示照片缩略图
 * - 展示AI生成的标签
 * - 显示AI处理状态
 * - 悬停效果
 * 
 * 优化：
 * - 添加AI状态徽章（处理中/完成/失败）
 * - 图片懒加载
 * - 悬停放大效果
 */

import type { Photo } from "@/lib/types"
import { CATEGORIES } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Sparkles, Loader2, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface PhotoCardProps {
  photo: Photo
  onClick?: () => void
  // 批量选择相关
  selectable?: boolean
  selected?: boolean
  onToggleSelect?: (checked: boolean) => void
}

export function PhotoCard({ 
  photo, 
  onClick, 
  selectable = false,
  selected = false,
  onToggleSelect 
}: PhotoCardProps) {
  const categoryLabel = CATEGORIES.find((cat) => cat.value === photo.category)?.label || photo.category

  // 判断AI处理状态
  const hasAITags = photo.tags && photo.tags.some(tag => tag.source === 'ai')
  const aiStatus = photo.ai_status || (hasAITags ? 'completed' : 'pending')

  // 处理点击事件
  const handleClick = (e: React.MouseEvent) => {
    // 如果是批量选择模式，点击卡片切换选中状态
    if (selectable && onToggleSelect) {
      e.stopPropagation()
      onToggleSelect(!selected)
    } else if (onClick) {
      onClick()
    }
  }

  return (
    <div 
      className={cn(
        "group cursor-pointer relative",
        selected && "ring-2 ring-primary ring-offset-2 rounded-lg"
      )}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          if (selectable && onToggleSelect) {
            onToggleSelect(!selected)
          } else {
            onClick?.()
          }
        }
      }}
    >
      <div className="relative aspect-square overflow-hidden rounded-lg bg-muted mb-2">
        {/* 批量选择复选框 */}
        {selectable && (
          <div className="absolute top-2 left-2 z-10">
            <Checkbox
              checked={selected}
              onCheckedChange={(checked) => {
                onToggleSelect?.(checked as boolean)
              }}
              className="bg-white/90 backdrop-blur-sm"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        )}
        {/* 照片图片 */}
        <img
          src={photo.url || "/placeholder.svg"}
          alt={photo.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300" />
        
        {/* AI状态徽章（右上角） */}
        <div className="absolute top-2 right-2">
          {aiStatus === 'processing' && (
            <Badge variant="secondary" className="gap-1 backdrop-blur-sm">
              <Loader2 className="h-3 w-3 animate-spin" />
              <span className="text-xs">AI分析中</span>
            </Badge>
          )}
          {aiStatus === 'completed' && hasAITags && (
            <Badge variant="default" className="gap-1 backdrop-blur-sm bg-green-500/90 hover:bg-green-600/90">
              <Sparkles className="h-3 w-3" />
              <span className="text-xs">AI已标注</span>
            </Badge>
          )}
          {aiStatus === 'failed' && (
            <Badge variant="destructive" className="gap-1 backdrop-blur-sm">
              <AlertCircle className="h-3 w-3" />
              <span className="text-xs">AI失败</span>
            </Badge>
          )}
        </div>
        
        {/* AI标签徽章（左上角，如果有复选框则下移） */}
        {photo.tags && photo.tags.length > 0 && (
          <div className={cn(
            "absolute left-2 flex flex-wrap gap-1 max-w-[60%]",
            selectable ? "top-12" : "top-2"
          )}>
            {photo.tags.slice(0, 3).map((tag, index) => (
              <Badge 
                key={index} 
                variant={tag.source === 'ai' ? 'default' : 'secondary'}
                className={cn(
                  "text-xs opacity-90 backdrop-blur-sm",
                  tag.source === 'ai' && "bg-blue-500/90 hover:bg-blue-600/90"
                )}
              >
                {tag.name}
              </Badge>
            ))}
            {photo.tags.length > 3 && (
              <Badge variant="outline" className="text-xs opacity-90 backdrop-blur-sm bg-black/20">
                +{photo.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </div>

      <div className="px-1">
        <h3 className="font-medium text-sm text-foreground mb-1 line-clamp-1">{photo.title}</h3>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{categoryLabel}</span>
          <time>
            {(() => {
              // 优先显示EXIF拍摄时间，否则显示上传时间
              let displayDate: Date
              if (photo.exif_data?.dateTaken) {
                displayDate = new Date(photo.exif_data.dateTaken)
              } else {
                displayDate = photo.uploadedAt instanceof Date ? photo.uploadedAt : new Date(photo.uploadedAt)
              }
              return displayDate.toLocaleDateString("zh-CN", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
              })
            })()}
          </time>
        </div>
        
        {/* AI描述 */}
        {photo.description && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {photo.description}
          </p>
        )}
      </div>
    </div>
  )
}
