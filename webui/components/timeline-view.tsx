/**
 * 时间轴视图组件
 * 
 * 功能：
 * - 按时间分组显示照片
 * - 支持搜索过滤
 * - Loading状态显示
 * - 空状态处理
 * 
 * 优化：
 * - 使用useMemo缓存过滤结果
 * - 防抖搜索避免频繁渲染
 */

"use client"

import { useSyncExternalStore, useMemo, useState } from "react"
import { PhotoCard } from "./photo-card"
import { PhotoDetailDialog } from "./photo-detail-dialog"
import { photoStore } from "@/lib/photo-store"
import { LoadingSpinner, PhotoCardSkeleton } from "./loading-spinner"
import { EmptyState } from "./error-message"
import type { Photo } from "@/lib/types"
import { ImageOff, Search } from "lucide-react"

interface TimelineViewProps {
  searchQuery?: string
}

export function TimelineView({ searchQuery = "" }: TimelineViewProps) {
  // 照片详情对话框状态
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  // 从photo store获取照片数据
  const allPhotos = useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.getPhotos(),
    () => photoStore.getPhotos(),
  )
  
  // 获取loading状态
  const isLoading = useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.isLoading,
    () => photoStore.isLoading,
  )
  
  /**
   * 根据搜索词过滤照片
   * 使用useMemo避免每次渲染都重新过滤
   * 
   * 支持的搜索类型：
   * - 标题、描述、标签
   * - 时间（年-月格式：2024-10）
   * - 地理位置（GPS坐标）
   * - 相机型号
   */
  const photos = useMemo(() => {
    // 如果没有搜索词，返回所有照片
    if (!searchQuery.trim()) return allPhotos
    
    const query = searchQuery.toLowerCase()
    return allPhotos.filter(photo => {
      // 搜索标题
      if (photo.title?.toLowerCase().includes(query)) return true
      
      // 搜索描述
      if (photo.description?.toLowerCase().includes(query)) return true
      
      // 搜索标签
      if (photo.tags?.some(tag => tag.name.toLowerCase().includes(query))) return true
      
      // 搜索EXIF信息
      if (photo.exif_data) {
        // 搜索相机型号
        if (photo.exif_data.camera?.toLowerCase().includes(query)) return true
        
        // 搜索地理位置
        if (photo.exif_data.location?.toLowerCase().includes(query)) return true
        
        // 搜索拍摄时间（年-月格式）
        if (photo.exif_data.dateTaken) {
          const date = new Date(photo.exif_data.dateTaken)
          const yearMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
          if (yearMonth.includes(query)) return true
        }
      }
      
      // 搜索上传时间（作为回退，当没有EXIF时间时）
      if (photo.uploadedAt) {
        const uploadDate = photo.uploadedAt instanceof Date ? photo.uploadedAt : new Date(photo.uploadedAt)
        if (!isNaN(uploadDate.getTime())) {
          const yearMonth = `${uploadDate.getFullYear()}-${String(uploadDate.getMonth() + 1).padStart(2, '0')}`
          if (yearMonth.includes(query)) return true
        }
      }
      
      return false
    })
  }, [allPhotos, searchQuery])

  console.log('📸 [TimelineView] 总照片数:', allPhotos.length)
  console.log('🔍 [TimelineView] 搜索词:', searchQuery)
  console.log('📸 [TimelineView] 过滤后:', photos.length)
  
  // 调试：输出前3张照片的时间信息
  if (allPhotos.length > 0) {
    console.log('📅 前3张照片的时间信息:')
    allPhotos.slice(0, 3).forEach((photo, i) => {
      const exifDate = photo.exif_data?.dateTaken
      const uploadDate = photo.uploadedAt
      console.log(`  ${i+1}. ${photo.title}:`)
      console.log(`     EXIF时间: ${exifDate || '无'}`)
      console.log(`     上传时间: ${uploadDate || '无'}`)
      if (uploadDate) {
        const date = uploadDate instanceof Date ? uploadDate : new Date(uploadDate)
        const yearMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
        console.log(`     格式化: ${yearMonth}`)
      }
    })
  }

  // Group photos by year and month
  const groupedPhotos = photos.reduce(
    (acc, photo) => {
      // 优先使用EXIF拍摄时间，否则使用上传时间
      let displayDate: Date
      
      if (photo.exif_data?.dateTaken) {
        displayDate = new Date(photo.exif_data.dateTaken)
      } else {
        displayDate = photo.uploadedAt instanceof Date ? photo.uploadedAt : new Date(photo.uploadedAt)
      }
      
      const year = displayDate.getFullYear()
      const month = displayDate.getMonth()
      const key = `${year}-${month}`

      if (!acc[key]) {
        acc[key] = {
          year,
          month,
          photos: [],
        }
      }
      acc[key].photos.push(photo)
      return acc
    },
    {} as Record<string, { year: number; month: number; photos: Photo[] }>,
  )

  const sortedGroups = Object.values(groupedPhotos).sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year
    return b.month - a.month
  })

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ]

  // Loading状态：显示骨架屏
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {/* 显示8个骨架屏占位 */}
        {Array.from({ length: 8 }).map((_, i) => (
          <PhotoCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  // 空状态：区分"无照片"和"搜索无结果"
  if (photos.length === 0) {
    // 如果有搜索词但无结果
    if (searchQuery.trim()) {
      return (
        <EmptyState
          icon={<Search className="h-16 w-16" />}
          title="未找到匹配的照片"
          description={`没有找到包含"${searchQuery}"的照片`}
        />
      )
    }
    
    // 完全没有照片
    return (
      <EmptyState
        icon={<ImageOff className="h-16 w-16" />}
        title="还没有照片"
        description="点击上方按钮上传您的第一张照片"
      />
    )
  }

  // 正常显示：按时间分组的照片列表
  return (
    <div className="space-y-12">
      {sortedGroups.map((group) => (
        <div key={`${group.year}-${group.month}`} className="space-y-6">
          {/* 时间标题 */}
          <div className="flex items-baseline gap-3 border-b border-border pb-3">
            <h2 className="text-2xl font-semibold text-foreground">{group.year}</h2>
            <span className="text-muted-foreground">·</span>
            <p className="text-base text-muted-foreground">{monthNames[group.month]}</p>
          </div>
          
          {/* 照片网格 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {group.photos.map((photo) => (
              <PhotoCard 
                key={photo.id} 
                photo={photo}
                onClick={() => {
                  setSelectedPhoto(photo)
                  setDetailOpen(true)
                }}
              />
            ))}
          </div>
        </div>
      ))}

      {/* 照片详情对话框 */}
      <PhotoDetailDialog
        photo={selectedPhoto}
        open={detailOpen}
        onOpenChange={setDetailOpen}
        onPrevious={() => {
          if (!selectedPhoto) return
          const currentIndex = photos.findIndex(p => p.id === selectedPhoto.id)
          if (currentIndex > 0) {
            setSelectedPhoto(photos[currentIndex - 1])
          }
        }}
        onNext={() => {
          if (!selectedPhoto) return
          const currentIndex = photos.findIndex(p => p.id === selectedPhoto.id)
          if (currentIndex < photos.length - 1) {
            setSelectedPhoto(photos[currentIndex + 1])
          }
        }}
        onDelete={async (photoId) => {
          // TODO: 实现删除功能
          console.log('删除照片:', photoId)
        }}
      />
    </div>
  )
}
