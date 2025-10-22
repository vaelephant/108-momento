// 安全的localStorage封装
"use client"

// 简单的数据加密/解密（生产环境应使用更安全的加密）
const encrypt = (text: string): string => {
  try {
    // 简单的Base64编码 + 简单混淆（仅用于演示）
    // 生产环境应使用crypto-js或Web Crypto API
    return btoa(encodeURIComponent(text))
  } catch (error) {
    console.error('Encryption failed:', error)
    return text // 如果加密失败，返回原文
  }
}

const decrypt = (encryptedText: string): string => {
  try {
    return decodeURIComponent(atob(encryptedText))
  } catch (error) {
    console.error('Decryption failed:', error)
    return encryptedText // 如果解密失败，返回原文
  }
}

// 安全的存储接口
export class SecureStorage {
  private static readonly PREFIX = 'momento_'
  private static readonly ENCRYPTED_SUFFIX = '_enc'

  // 存储敏感数据（加密）
  static setSecureItem(key: string, value: any): void {
    try {
      const jsonString = JSON.stringify(value)
      const encryptedValue = encrypt(jsonString)
      const storageKey = this.PREFIX + key + this.ENCRYPTED_SUFFIX
      localStorage.setItem(storageKey, encryptedValue)
      console.log('🔐 [SecureStorage] 数据已加密存储:', {
        key: storageKey,
        dataSize: jsonString.length,
        encryptedSize: encryptedValue.length
      })
    } catch (error) {
      console.error('Failed to store secure data:', error)
    }
  }

  // 读取敏感数据（解密）
  static getSecureItem<T>(key: string): T | null {
    try {
      const storageKey = this.PREFIX + key + this.ENCRYPTED_SUFFIX
      const encryptedValue = localStorage.getItem(storageKey)
      console.log('🔍 [SecureStorage] 尝试读取数据:', {
        key: storageKey,
        hasData: !!encryptedValue,
        dataLength: encryptedValue?.length || 0
      })
      
      if (!encryptedValue) return null
      
      const decryptedValue = decrypt(encryptedValue)
      const parsedData = JSON.parse(decryptedValue)
      console.log('🔓 [SecureStorage] 数据解密成功:', {
        key: storageKey,
        dataType: typeof parsedData,
        isArray: Array.isArray(parsedData),
        length: Array.isArray(parsedData) ? parsedData.length : 'N/A'
      })
      return parsedData
    } catch (error) {
      console.error('Failed to read secure data:', error)
      return null
    }
  }

  // 存储非敏感数据（不加密）
  static setItem(key: string, value: any): void {
    try {
      localStorage.setItem(this.PREFIX + key, JSON.stringify(value))
    } catch (error) {
      console.error('Failed to store data:', error)
    }
  }

  // 读取非敏感数据
  static getItem<T>(key: string): T | null {
    try {
      const value = localStorage.getItem(this.PREFIX + key)
      return value ? JSON.parse(value) : null
    } catch (error) {
      console.error('Failed to read data:', error)
      return null
    }
  }

  // 删除数据
  static removeItem(key: string): void {
    localStorage.removeItem(this.PREFIX + key)
    localStorage.removeItem(this.PREFIX + key + this.ENCRYPTED_SUFFIX)
  }

  // 清空所有应用数据
  static clear(): void {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(this.PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  }
}

// 数据分类和访问控制
export const StorageKeys = {
  // 敏感数据（加密存储）
  USER_DATA: 'user_data',
  AUTH_TOKEN: 'auth_token',
  
  // 非敏感数据（不加密）
  USER_PREFERENCES: 'user_preferences',
  UI_STATE: 'ui_state',
  
  // 照片数据（可能包含敏感信息，建议加密）
  USER_PHOTOS: 'user_photos',
} as const

// 数据过期管理
export class ExpiringStorage {
  static setItem(key: string, value: any, expirationHours: number = 24): void {
    const expirationTime = Date.now() + (expirationHours * 60 * 60 * 1000)
    const data = {
      value,
      expirationTime
    }
    SecureStorage.setSecureItem(key, data)
  }

  static getItem<T>(key: string): T | null {
    const data = SecureStorage.getSecureItem<{value: T, expirationTime: number}>(key)
    if (!data) return null

    if (Date.now() > data.expirationTime) {
      SecureStorage.removeItem(key)
      return null
    }

    return data.value
  }
}
