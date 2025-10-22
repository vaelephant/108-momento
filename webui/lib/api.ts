/**
 * API客户端 - 与后端FastAPI服务集成
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

export interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at: string
}

export interface Photo {
  id: number
  user_id: number
  storage_path: string
  filename: string
  file_size?: number
  width?: number
  height?: number
  caption?: string
  dominant_colors?: string[]
  created_at: string
  updated_at: string
  tags?: Tag[]
}

export interface Tag {
  id: number
  name: string
  category?: string
  confidence?: number
}

export interface Album {
  id: number
  user_id: number
  name: string
  description?: string
  cover_photo_id?: number
  created_at: string
  updated_at: string
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
    this.token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // 认证相关
  async register(username: string, email: string, password: string): Promise<ApiResponse<User>> {
    return this.request('/api/v1/users/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    })
  }

  async login(username: string, password: string): Promise<ApiResponse<{ access_token: string; user: User }>> {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch(`${this.baseURL}/api/v1/users/login`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`)
    }

    const data = await response.json()
    
    if (data.success && data.data?.access_token) {
      this.token = data.data.access_token
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', data.data.access_token)
      }
    }

    return data
  }

  async logout(): Promise<void> {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  // 照片相关
  async uploadPhoto(file: File, caption?: string): Promise<ApiResponse<Photo>> {
    if (!this.token) {
      throw new Error('Authentication required')
    }

    const formData = new FormData()
    formData.append('file', file)
    if (caption) {
      formData.append('caption', caption)
    }

    const response = await fetch(`${this.baseURL}/api/v1/photos/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }

    return response.json()
  }

  async getPhotos(page: number = 1, limit: number = 20): Promise<ApiResponse<Photo[]>> {
    if (!this.token) {
      throw new Error('Authentication required')
    }
    return this.request(`/api/v1/photos?page=${page}&limit=${limit}`)
  }

  async getPhoto(id: number): Promise<ApiResponse<Photo>> {
    return this.request(`/api/v1/photos/${id}`)
  }

  async deletePhoto(id: number): Promise<ApiResponse<void>> {
    return this.request(`/api/v1/photos/${id}`, {
      method: 'DELETE',
    })
  }

  // 搜索相关
  async searchPhotos(
    query?: string,
    tags?: string[],
    categories?: string[],
    colors?: string[],
    dateFrom?: string,
    dateTo?: string,
    page: number = 1,
    limit: number = 20
  ): Promise<ApiResponse<Photo[]>> {
    const params = new URLSearchParams()
    if (query) params.append('query', query)
    if (tags?.length) params.append('tags', tags.join(','))
    if (categories?.length) params.append('categories', categories.join(','))
    if (colors?.length) params.append('colors', colors.join(','))
    if (dateFrom) params.append('date_from', dateFrom)
    if (dateTo) params.append('date_to', dateTo)
    params.append('page', page.toString())
    params.append('limit', limit.toString())

    return this.request(`/api/v1/search/photos?${params.toString()}`)
  }

  async findSimilarPhotos(photoId: number, limit: number = 10): Promise<ApiResponse<Photo[]>> {
    return this.request(`/api/v1/search/similar/${photoId}?limit=${limit}`)
  }

  // 标签相关
  async getTags(): Promise<ApiResponse<Tag[]>> {
    return this.request('/api/v1/tags')
  }

  async createTag(name: string, category?: string): Promise<ApiResponse<Tag>> {
    return this.request('/api/v1/tags', {
      method: 'POST',
      body: JSON.stringify({ name, category }),
    })
  }

  // 相册相关
  async getAlbums(): Promise<ApiResponse<Album[]>> {
    return this.request('/api/v1/albums')
  }

  async createAlbum(name: string, description?: string): Promise<ApiResponse<Album>> {
    return this.request('/api/v1/albums', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    })
  }

  async addPhotoToAlbum(albumId: number, photoId: number): Promise<ApiResponse<void>> {
    return this.request(`/api/v1/albums/${albumId}/photos/${photoId}`, {
      method: 'POST',
    })
  }

  // 健康检查
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient()
export default apiClient
