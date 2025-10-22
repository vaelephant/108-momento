/**
 * 防抖Hook
 * 
 * 用途：
 * - 延迟执行快速变化的值
 * - 常用于搜索输入，避免频繁触发API请求
 * 
 * 原理：
 * - 当值改变时，等待delay毫秒
 * - 如果在delay期间值再次改变，重新计时
 * - 只有值稳定delay毫秒后才更新
 * 
 * @param value - 需要防抖的值
 * @param delay - 延迟时间（毫秒），默认500ms
 * @returns 防抖后的值
 * 
 * @example
 * ```tsx
 * const [searchTerm, setSearchTerm] = useState('')
 * const debouncedSearch = useDebounce(searchTerm, 300)
 * 
 * useEffect(() => {
 *   // 只在用户停止输入300ms后才执行搜索
 *   if (debouncedSearch) {
 *     performSearch(debouncedSearch)
 *   }
 * }, [debouncedSearch])
 * ```
 */

import { useState, useEffect } from 'react'

export function useDebounce<T>(value: T, delay: number = 500): T {
  // 存储防抖后的值
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    // 设置定时器，延迟更新
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // 清理函数：如果value在delay期间改变，清除之前的定时器
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay]) // 只在value或delay改变时重新执行

  return debouncedValue
}

/**
 * 防抖回调Hook
 * 
 * 用途：
 * - 延迟执行函数调用
 * - 避免频繁触发昂贵的操作
 * 
 * @param callback - 需要防抖的函数
 * @param delay - 延迟时间（毫秒）
 * @returns 防抖后的函数
 * 
 * @example
 * ```tsx
 * const handleSearch = useDebouncedCallback((query: string) => {
 *   fetch(`/api/search?q=${query}`)
 * }, 300)
 * 
 * <input onChange={(e) => handleSearch(e.target.value)} />
 * ```
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 500
): (...args: Parameters<T>) => void {
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null)

  return (...args: Parameters<T>) => {
    // 如果有待执行的定时器，先清除
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // 设置新的定时器
    const newTimeoutId = setTimeout(() => {
      callback(...args)
    }, delay)

    setTimeoutId(newTimeoutId)
  }
}

