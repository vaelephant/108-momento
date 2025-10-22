# 🚀 优化功能快速使用指南

## 1️⃣ Loading 和错误提示

### 在任何组件中显示Loading
```tsx
import { LoadingSpinner } from "@/components/loading-spinner"

// 小型loading（适合按钮）
<LoadingSpinner size="sm" />

// 中型loading（适合卡片）
<LoadingSpinner size="md" text="加载中..." />

// 大型loading（适合页面）
<LoadingSpinner size="lg" text="正在处理..." />
```

### 骨架屏占位
```tsx
import { PhotoCardSkeleton } from "@/components/loading-spinner"

{isLoading && (
  <div className="grid grid-cols-4 gap-4">
    {Array.from({ length: 8 }).map((_, i) => (
      <PhotoCardSkeleton key={i} />
    ))}
  </div>
)}
```

### 错误提示
```tsx
import { ErrorMessage } from "@/components/error-message"

{error && (
  <ErrorMessage
    message={error}
    type="error"
    onRetry={() => refetch()}
  />
)}
```

## 2️⃣ 照片详情对话框

### 基础使用
```tsx
import { PhotoDetailDialog } from "@/components/photo-detail-dialog"
import { useState } from "react"

function MyComponent() {
  const [selectedPhoto, setSelectedPhoto] = useState(null)
  const [open, setOpen] = useState(false)

  return (
    <>
      {/* 照片卡片 */}
      <PhotoCard 
        photo={photo}
        onClick={() => {
          setSelectedPhoto(photo)
          setOpen(true)
        }}
      />

      {/* 详情对话框 */}
      <PhotoDetailDialog
        photo={selectedPhoto}
        open={open}
        onOpenChange={setOpen}
      />
    </>
  )
}
```

### 带导航的完整示例
```tsx
<PhotoDetailDialog
  photo={selectedPhoto}
  open={open}
  onOpenChange={setOpen}
  // 上一张
  onPrevious={() => {
    const index = photos.findIndex(p => p.id === selectedPhoto.id)
    if (index > 0) setSelectedPhoto(photos[index - 1])
  }}
  // 下一张
  onNext={() => {
    const index = photos.findIndex(p => p.id === selectedPhoto.id)
    if (index < photos.length - 1) setSelectedPhoto(photos[index + 1])
  }}
  // 删除
  onDelete={(id) => {
    deletePhoto(id)
    setOpen(false)
  }}
/>
```

### 键盘快捷键
- `ESC` - 关闭对话框
- `←` - 上一张照片
- `→` - 下一张照片

## 3️⃣ 批量选择和操作

### 完整实现
```tsx
import { BulkSelectionBar, useBulkSelection } from "@/components/bulk-selection-bar"
import { PhotoCard } from "@/components/photo-card"
import { useState } from "react"

function PhotoGallery() {
  const [photos, setPhotos] = useState([...])
  
  // 使用批量选择Hook
  const {
    selectedIds,
    selectedCount,
    isSelected,
    toggleSelection,
    selectAll,
    clearSelection
  } = useBulkSelection(photos.map(p => p.id))

  // 批量选择模式开关
  const [selectionMode, setSelectionMode] = useState(false)

  return (
    <>
      {/* 工具栏 */}
      <Button onClick={() => setSelectionMode(!selectionMode)}>
        {selectionMode ? '退出选择' : '批量选择'}
      </Button>

      {/* 照片网格 */}
      <div className="grid grid-cols-4 gap-4">
        {photos.map(photo => (
          <PhotoCard
            key={photo.id}
            photo={photo}
            selectable={selectionMode}
            selected={isSelected(photo.id)}
            onToggleSelect={(checked) => toggleSelection(photo.id)}
          />
        ))}
      </div>

      {/* 批量操作栏 */}
      <BulkSelectionBar
        selectedCount={selectedCount}
        totalCount={photos.length}
        onClearSelection={clearSelection}
        onSelectAll={selectAll}
        onDelete={async () => {
          await deletePhotos(Array.from(selectedIds))
          clearSelection()
        }}
        onDownload={() => {
          downloadPhotos(Array.from(selectedIds))
        }}
      />
    </>
  )
}
```

## 4️⃣ 搜索防抖

### 简单搜索
```tsx
import { useDebounce } from "@/hooks/use-debounce"
import { useState } from "react"

function SearchBar() {
  const [query, setQuery] = useState('')
  // 防抖：用户停止输入300ms后才更新
  const debouncedQuery = useDebounce(query, 300)

  // 使用防抖后的值进行搜索
  useEffect(() => {
    if (debouncedQuery) {
      performSearch(debouncedQuery)
    }
  }, [debouncedQuery])

  return (
    <Input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="搜索..."
    />
  )
}
```

### 防抖函数
```tsx
import { useDebouncedCallback } from "@/hooks/use-debounce"

function AutoSaveForm() {
  // 防抖保存函数
  const debouncedSave = useDebouncedCallback(
    (data) => saveToServer(data),
    500
  )

  return (
    <textarea
      onChange={(e) => {
        // 每次输入都会调用，但实际只在停止输入500ms后执行
        debouncedSave(e.target.value)
      }}
    />
  )
}
```

## 5️⃣ AI状态显示

### PhotoCard自动显示AI状态
照片卡片会自动根据`ai_status`显示相应的徽章：

- **pending** - 不显示徽章
- **processing** - 🔄 "AI分析中" 动画
- **completed** - ✨ "AI已标注" 绿色
- **failed** - ❌ "AI失败" 红色

只需确保Photo对象包含正确的`ai_status`字段：

```tsx
const photo = {
  id: '1',
  url: '/photo.jpg',
  title: 'My Photo',
  ai_status: 'completed', // 'pending' | 'processing' | 'completed' | 'failed'
  tags: [
    { name: '自然', source: 'ai' },
    { name: '山', source: 'ai' }
  ]
}
```

## 6️⃣ 缩略图使用

### 后端自动生成
照片上传时会自动生成缩略图：

```python
from app.services.photo_service import PhotoService

# 创建照片记录（自动生成缩略图）
photo = photo_service.create_photo(
    user_id=user_id,
    filename="photo.jpg",
    storage_path="/path/to/photo.jpg",
    file_size=1024000,
    generate_thumbnails=True  # 默认为True
)

# 缩略图路径存储在 exif_data.thumbnails
thumbnails = photo.exif_data.get('thumbnails', {})
small_url = thumbnails.get('small')    # 200x200
medium_url = thumbnails.get('medium')  # 600x600
large_url = thumbnails.get('large')    # 1200x1200
```

### 前端使用缩略图
```tsx
// 根据场景选择合适的尺寸
const getThumbnailUrl = (photo: Photo, size: 'small' | 'medium' | 'large') => {
  const thumbnails = photo.exif_data?.thumbnails
  if (!thumbnails) return photo.url
  
  const filename = thumbnails[size]
  if (!filename) return photo.url
  
  // 构建缩略图URL
  return `/uploads/${filename}`
}

// 列表使用小图
<img src={getThumbnailUrl(photo, 'small')} />

// 预览使用中图
<img src={getThumbnailUrl(photo, 'medium')} />

// 详情使用大图
<img src={getThumbnailUrl(photo, 'large')} />
```

## 🎨 完整示例

### 完整的照片列表页面
```tsx
"use client"

import { useState, useEffect } from "react"
import { useDebounce } from "@/hooks/use-debounce"
import { PhotoCard } from "@/components/photo-card"
import { PhotoDetailDialog } from "@/components/photo-detail-dialog"
import { BulkSelectionBar, useBulkSelection } from "@/components/bulk-selection-bar"
import { LoadingSpinner, PhotoCardSkeleton } from "@/components/loading-spinner"
import { ErrorMessage, EmptyState } from "@/components/error-message"

export default function PhotoGallery() {
  // 状态管理
  const [photos, setPhotos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPhoto, setSelectedPhoto] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectionMode, setSelectionMode] = useState(false)

  // 防抖搜索
  const debouncedSearch = useDebounce(searchQuery, 300)

  // 批量选择
  const {
    selectedIds,
    selectedCount,
    isSelected,
    toggleSelection,
    selectAll,
    clearSelection
  } = useBulkSelection(photos.map(p => p.id))

  // 加载照片
  useEffect(() => {
    loadPhotos()
  }, [debouncedSearch])

  async function loadPhotos() {
    try {
      setLoading(true)
      setError(null)
      const data = await fetch(`/api/photos?q=${debouncedSearch}`)
      setPhotos(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Loading状态
  if (loading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <PhotoCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  // 错误状态
  if (error) {
    return (
      <ErrorMessage
        message={error}
        type="error"
        onRetry={loadPhotos}
      />
    )
  }

  // 空状态
  if (photos.length === 0) {
    return (
      <EmptyState
        title="没有照片"
        description="点击上传按钮添加照片"
      />
    )
  }

  return (
    <div>
      {/* 工具栏 */}
      <div className="flex gap-2 mb-4">
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="搜索照片..."
        />
        <Button onClick={() => setSelectionMode(!selectionMode)}>
          {selectionMode ? '退出选择' : '批量选择'}
        </Button>
      </div>

      {/* 照片网格 */}
      <div className="grid grid-cols-4 gap-4">
        {photos.map(photo => (
          <PhotoCard
            key={photo.id}
            photo={photo}
            onClick={() => {
              if (!selectionMode) {
                setSelectedPhoto(photo)
                setDetailOpen(true)
              }
            }}
            selectable={selectionMode}
            selected={isSelected(photo.id)}
            onToggleSelect={() => toggleSelection(photo.id)}
          />
        ))}
      </div>

      {/* 照片详情 */}
      <PhotoDetailDialog
        photo={selectedPhoto}
        open={detailOpen}
        onOpenChange={setDetailOpen}
        onPrevious={() => {
          const index = photos.findIndex(p => p.id === selectedPhoto.id)
          if (index > 0) setSelectedPhoto(photos[index - 1])
        }}
        onNext={() => {
          const index = photos.findIndex(p => p.id === selectedPhoto.id)
          if (index < photos.length - 1) setSelectedPhoto(photos[index + 1])
        }}
        onDelete={(id) => {
          deletePhoto(id)
          setDetailOpen(false)
        }}
      />

      {/* 批量操作 */}
      <BulkSelectionBar
        selectedCount={selectedCount}
        totalCount={photos.length}
        onClearSelection={clearSelection}
        onSelectAll={selectAll}
        onDelete={async () => {
          await deletePhotos(Array.from(selectedIds))
          clearSelection()
          loadPhotos()
        }}
      />
    </div>
  )
}
```

## 📱 移动端适配提示

### 响应式网格
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {/* 照片卡片 */}
</div>
```

### 触摸优化
```tsx
<PhotoCard
  photo={photo}
  onClick={onClick}
  className="touch-manipulation" // 优化触摸响应
/>
```

## 🎯 性能建议

1. **使用缩略图** - 列表只加载small尺寸
2. **启用懒加载** - PhotoCard已内置`loading="lazy"`
3. **防抖搜索** - 避免频繁请求
4. **虚拟滚动** - 照片超过100张时考虑使用
5. **分页加载** - 按需加载更多照片

---

更多详细信息请查看 [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)

