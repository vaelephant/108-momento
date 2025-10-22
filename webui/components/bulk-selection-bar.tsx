/**
 * 批量操作栏组件
 * 
 * 功能：
 * - 显示选中照片数量
 * - 批量删除
 * - 批量添加标签
 * - 批量下载
 * - 全选/取消全选
 * 
 * 用法：
 * ```tsx
 * const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
 * 
 * <BulkSelectionBar
 *   selectedCount={selectedIds.size}
 *   onClearSelection={() => setSelectedIds(new Set())}
 *   onDelete={() => handleBatchDelete(selectedIds)}
 * />
 * ```
 */

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Trash2,
  Download,
  Tag,
  X,
  CheckSquare,
  Square,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface BulkSelectionBarProps {
  selectedCount: number
  totalCount?: number
  onClearSelection: () => void
  onSelectAll?: () => void
  onDelete?: () => void
  onAddTag?: () => void
  onDownload?: () => void
  className?: string
}

export function BulkSelectionBar({
  selectedCount,
  totalCount,
  onClearSelection,
  onSelectAll,
  onDelete,
  onAddTag,
  onDownload,
  className,
}: BulkSelectionBarProps) {
  // 如果没有选中任何项，不显示
  if (selectedCount === 0) return null

  const allSelected = totalCount !== undefined && selectedCount === totalCount

  return (
    <div
      className={cn(
        "fixed bottom-6 left-1/2 -translate-x-1/2 z-50",
        "bg-background border border-border rounded-lg shadow-lg",
        "px-6 py-4 flex items-center gap-4",
        "animate-in slide-in-from-bottom-4 duration-300",
        className
      )}
    >
      {/* 选中数量 */}
      <div className="flex items-center gap-2">
        <Badge variant="secondary" className="text-base px-3 py-1">
          {selectedCount}
        </Badge>
        <span className="text-sm font-medium">
          {selectedCount === 1 ? '张照片已选中' : '张照片已选中'}
        </span>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* 操作按钮 */}
      <div className="flex items-center gap-2">
        {/* 全选/取消全选 */}
        {onSelectAll && totalCount !== undefined && (
          <Button
            variant="outline"
            size="sm"
            onClick={allSelected ? onClearSelection : onSelectAll}
            className="gap-2"
          >
            {allSelected ? (
              <>
                <Square className="h-4 w-4" />
                取消全选
              </>
            ) : (
              <>
                <CheckSquare className="h-4 w-4" />
                全选 ({totalCount})
              </>
            )}
          </Button>
        )}

        {/* 添加标签 */}
        {onAddTag && (
          <Button
            variant="outline"
            size="sm"
            onClick={onAddTag}
            className="gap-2"
          >
            <Tag className="h-4 w-4" />
            添加标签
          </Button>
        )}

        {/* 下载 */}
        {onDownload && (
          <Button
            variant="outline"
            size="sm"
            onClick={onDownload}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            下载
          </Button>
        )}

        {/* 删除 */}
        {onDelete && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => {
              if (confirm(`确定要删除选中的 ${selectedCount} 张照片吗？`)) {
                onDelete()
              }
            }}
            className="gap-2"
          >
            <Trash2 className="h-4 w-4" />
            删除
          </Button>
        )}

        {/* 取消选择 */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onClearSelection}
          className="h-8 w-8"
          title="取消选择"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

/**
 * 批量选择模式Hook
 * 
 * 用法：
 * ```tsx
 * const {
 *   selectedIds,
 *   isSelected,
 *   toggleSelection,
 *   selectAll,
 *   clearSelection,
 * } = useBulkSelection(photos.map(p => p.id))
 * ```
 */
export function useBulkSelection(allIds: string[]) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const toggleSelection = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const isSelected = (id: string) => selectedIds.has(id)

  const selectAll = () => {
    setSelectedIds(new Set(allIds))
  }

  const clearSelection = () => {
    setSelectedIds(new Set())
  }

  return {
    selectedIds,
    selectedCount: selectedIds.size,
    isSelected,
    toggleSelection,
    selectAll,
    clearSelection,
  }
}

