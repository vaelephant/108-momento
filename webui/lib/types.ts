export interface PhotoTag {
  name: string
  confidence?: number
  source?: 'ai' | 'manual'
}

export interface Photo {
  id: string
  url: string
  title: string
  category: string
  uploadedAt: Date
  description?: string
  tags?: PhotoTag[]
  userId?: number
  aiProcessed?: boolean
  aiError?: string
  dominantColors?: string
  // AI处理状态
  ai_status?: 'pending' | 'processing' | 'completed' | 'failed'
  // 文件信息
  filename?: string
  fileSize?: number
  width?: number
  height?: number
  // EXIF数据
  exif_data?: {
    camera?: string
    thumbnails?: {
      small?: string
      medium?: string
      large?: string
    }
    [key: string]: any
  }
  // 地理位置
  location?: string
}

export type PhotoCategory = "nature" | "urban" | "portrait" | "food" | "travel" | "other"

export const CATEGORIES: { value: PhotoCategory; label: string }[] = [
  { value: "nature", label: "自然" },
  { value: "urban", label: "城市" },
  { value: "portrait", label: "人像" },
  { value: "food", label: "美食" },
  { value: "travel", label: "旅行" },
  { value: "other", label: "其他" },
]
