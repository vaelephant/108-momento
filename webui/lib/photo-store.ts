"use client"

import { useSyncExternalStore } from "react"
import type { Photo } from "./types"
import { apiClient } from "./api"
// import { SecureStorage, StorageKeys } from "./secure-storage"

/**
 * 照片存储管理类
 * 
 * 功能：
 * - 管理照片列表数据
 * - 处理loading和error状态
 * - 实现订阅模式供React组件使用
 * 
 * 优化：
 * - 纯内存模式，避免SSR问题
 * - 缓存快照避免重复计算
 * - 统一错误处理
 */
class PhotoStore {
  private photos: Photo[] = []
  private listeners: Set<() => void> = new Set()
  private cachedSnapshot: Photo[] = []
  
  // 状态管理：loading和error
  public isLoading = false
  public error: string | null = null

  constructor() {
    // 纯内存模式，不使用localStorage
    console.log('📦 [Photo Store] 初始化（纯内存模式）')
  }

  /**
   * 获取照片列表
   * 返回缓存快照，避免直接暴露内部数组
   */
  getPhotos(): Photo[] {
    return this.cachedSnapshot
  }

  /**
   * 获取loading状态
   */
  getLoadingState(): boolean {
    return this.isLoading
  }

  /**
   * 获取错误信息
   */
  getError(): string | null {
    return this.error
  }

  /**
   * 从服务器加载照片列表
   * 包含完整的错误处理和状态管理
   */
  async loadPhotos(): Promise<void> {
    console.log('🚀 [Photo Store] 开始从数据库加载照片...')
    
    // 设置loading状态
    this.isLoading = true
    this.error = null
    this.notifyListeners()

    try {
      // 从Cookie获取用户信息
      if (typeof window !== 'undefined') {
        const userCookie = document.cookie
          .split('; ')
          .find(row => row.startsWith('user_data='))
        
        if (!userCookie) {
          console.log('📸 [Photo Store] 用户未登录，跳过加载')
          this.photos = []
          this.cachedSnapshot = []
          this.isLoading = false
          this.notifyListeners()
          return
        }

        const userData = decodeURIComponent(userCookie.split('=')[1])
        const user = JSON.parse(userData)
        
        console.log('📡 [Photo Store] 获取用户照片...', user.id)

        // 调用API从数据库获取照片
        const response = await fetch(`/api/photos/list?userId=${user.id}`)
        
        if (!response.ok) {
          throw new Error(`获取照片列表失败: ${response.status}`)
        }

        const data = await response.json()
        
        if (data.success && data.photos) {
          // 确保uploadedAt是Date对象
          this.photos = data.photos.map((photo: any) => ({
            ...photo,
            uploadedAt: new Date(photo.uploadedAt)
          }))
          this.cachedSnapshot = [...this.photos]
          
          console.log('📸 [Photo Store] 照片加载完成，共', this.photos.length, '张')
          
          // 打印前3张照片的信息
          if (this.photos.length > 0) {
            console.log('📸 [Photo Store] 前3张照片:')
            this.photos.slice(0, 3).forEach((photo, index) => {
              console.log(`  ${index + 1}. ${photo.title}`, photo.url)
            })
          }
        } else {
          this.photos = []
          this.cachedSnapshot = []
        }
      }
    } catch (error) {
      // 错误处理：记录错误信息
      console.error('❌ [Photo Store] 加载照片失败:', error)
      this.error = error instanceof Error ? error.message : '加载照片失败'
      this.photos = []
      this.cachedSnapshot = []
    } finally {
      // 无论成功失败都要清除loading状态
      this.isLoading = false
      this.notifyListeners()
    }
  }

  /**
   * 添加照片
   * 
   * @param file - 照片文件
   * @param caption - 标题
   * @param exifData - EXIF信息（拍摄时间、地点、相机等）
   */
  async addPhoto(file: File, caption?: string, exifData?: any): Promise<Photo> {
    this.isLoading = true
    this.notifyListeners()

    try {
      // 从Cookie获取当前用户ID
      if (typeof window === 'undefined') {
        throw new Error('服务端渲染，无法访问Cookie')
      }
      
      const userCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('user_data='))
      
      if (!userCookie) {
        throw new Error('用户未登录')
      }
      
      const userData = decodeURIComponent(userCookie.split('=')[1])
      const user = JSON.parse(userData)

      // 准备上传数据
      const formData = new FormData()
      formData.append('file', file)
      if (caption) {
        formData.append('caption', caption)
      }
      formData.append('userId', user.id.toString())
      
      // 添加EXIF信息
      if (exifData) {
        // 提取关键EXIF字段
        const exifToSend = {
          dateTaken: exifData.dateTaken?.toISOString(),
          location: exifData.location,
          camera: exifData.camera,
          latitude: exifData.latitude,
          longitude: exifData.longitude,
          make: exifData.make,
          model: exifData.model,
        }
        formData.append('exifData', JSON.stringify(exifToSend))
        console.log('📷 [Photo Store] 附加EXIF信息:', exifToSend)
      }

      // 简化认证，直接使用用户ID
      console.log('🔍 [Photo Store] 使用用户ID进行认证:')
      console.log('  - 用户ID:', user.id)
      console.log('  - 用户名:', user.username)

      // 调用后端API上传并处理照片
      console.log('🚀 开始上传照片到API...')
      const response = await fetch('/api/photos/upload', {
        method: 'POST',
        body: formData,
      })
      
      console.log('📡 API响应状态:', response.status)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '上传失败')
      }

      const result = await response.json()
      const photoData = result.photo

      // 创建照片对象
      const newPhoto: Photo = {
        id: photoData.id,
        url: photoData.url,
        title: photoData.title || file.name.replace(/\.[^/.]+$/, ""),
        category: photoData.category || 'other',
        uploadedAt: new Date(photoData.uploadedAt),
        description: photoData.description,
        tags: photoData.tags || [],
        userId: photoData.userId,
        aiProcessed: photoData.aiProcessed,
        aiError: photoData.aiError,
        exif_data: photoData.exif_data, // 添加EXIF数据
      }
      
      console.log('📸 [Photo Store] 创建照片对象:')
      console.log('  - 照片ID:', newPhoto.id)
      console.log('  - 照片URL:', newPhoto.url)
      console.log('  - 上传时间:', newPhoto.uploadedAt)
      console.log('  - 时间类型:', typeof newPhoto.uploadedAt)
      console.log('  - EXIF数据:', newPhoto.exif_data ? '有' : '无')
      if (newPhoto.exif_data?.dateTaken) {
        console.log('  - 拍摄时间:', newPhoto.exif_data.dateTaken)
      }

      this.photos.unshift(newPhoto)
      this.cachedSnapshot = [...this.photos]
      
      console.log('📸 [Photo Store] 照片已添加到内存:')
      console.log('  - 总照片数:', this.photos.length)
      console.log('  - 新照片ID:', newPhoto.id)
      
      this.notifyListeners()
      return newPhoto
    } catch (error) {
      console.error('Failed to add photo:', error)
      throw error
    } finally {
      this.isLoading = false
      this.notifyListeners()
    }
  }

  async searchPhotos(query: string): Promise<Photo[]> {
    try {
      // 前端搜索 - 在本地照片中搜索
      return this.photos.filter(photo => 
        photo.title.toLowerCase().includes(query.toLowerCase()) ||
        photo.description?.toLowerCase().includes(query.toLowerCase()) ||
        photo.tags?.some(tag => tag.name.toLowerCase().includes(query.toLowerCase()))
      )
    } catch (error) {
      console.error('Search failed:', error)
      return []
    }
  }

  private transformApiPhoto(apiPhoto: any): Photo {
    // 构建完整的图片URL
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'
    const imageUrl = apiPhoto.storage_path.startsWith('http') 
      ? apiPhoto.storage_path 
      : `${baseUrl}${apiPhoto.storage_path}`

    return {
      id: apiPhoto.id.toString(),
      url: imageUrl,
      title: apiPhoto.caption || apiPhoto.filename || 'Untitled',
      category: this.inferCategory(apiPhoto.tags) || 'other',
      uploadedAt: new Date(apiPhoto.created_at),
      description: apiPhoto.caption,
      tags: apiPhoto.tags?.map((tag: any) => tag.name) || [],
    }
  }

  private inferCategory(tags: any[]): string | null {
    if (!tags || tags.length === 0) return null
    
    const tagNames = tags.map(tag => tag.name?.toLowerCase() || '')
    
    // 根据标签推断分类
    if (tagNames.some(tag => ['nature', 'landscape', 'forest', 'mountain', 'ocean'].includes(tag))) {
      return 'nature'
    }
    if (tagNames.some(tag => ['city', 'urban', 'street', 'building', 'architecture'].includes(tag))) {
      return 'urban'
    }
    if (tagNames.some(tag => ['portrait', 'person', 'people', 'face'].includes(tag))) {
      return 'portrait'
    }
    if (tagNames.some(tag => ['food', 'restaurant', 'cooking', 'meal'].includes(tag))) {
      return 'food'
    }
    if (tagNames.some(tag => ['travel', 'vacation', 'trip', 'journey'].includes(tag))) {
      return 'travel'
    }
    
    return null
  }

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => listener())
  }
}

export const photoStore = new PhotoStore()

export function usePhotos(): Photo[] {
  return useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.getPhotos(),
    () => photoStore.getPhotos(),
  )
}

export function usePhotosLoading(): boolean {
  return useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.getLoadingState(),
    () => photoStore.getLoadingState(),
  )
}
