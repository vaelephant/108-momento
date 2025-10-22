/**
 * EXIF筛选组件
 * 
 * 功能：
 * - 按时间筛选（按年、月）
 * - 按地理位置筛选
 * - 显示相机型号
 * 
 * 数据来源：
 * - 从照片的EXIF数据中提取
 * - taken_at: 拍摄时间
 * - location: GPS位置
 * - camera: 相机型号
 */

"use client"

import { useMemo } from "react"
import { Calendar, MapPin, Camera } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { Photo } from "@/lib/types"

interface ExifFiltersProps {
  photos: Photo[]
  onFilterChange?: (filter: { type: 'time' | 'location' | 'camera', value: string }) => void
}

export function ExifFilters({ photos, onFilterChange }: ExifFiltersProps) {
  /**
   * 按拍摄时间分组（年-月）
   */
  const timeGroups = useMemo(() => {
    console.log('🔍 [ExifFilters] 开始处理照片，总数:', photos.length)
    const groups = new Map<string, number>()
    
    photos.forEach((photo, index) => {
      // 优先使用EXIF拍摄时间，否则使用上传时间
      let date: Date | null = null
      
      if (photo.exif_data?.dateTaken) {
        date = new Date(photo.exif_data.dateTaken)
        if (index < 3) {
          console.log(`  📷 照片${index+1}: ${photo.title}`)
          console.log(`     EXIF时间: ${photo.exif_data.dateTaken}`)
          console.log(`     解析后: ${date.toISOString()}`)
        }
      } else if (photo.uploadedAt) {
        date = photo.uploadedAt instanceof Date ? photo.uploadedAt : new Date(photo.uploadedAt)
        if (index < 3) {
          console.log(`  📷 照片${index+1}: ${photo.title}`)
          console.log(`     上传时间: ${photo.uploadedAt}`)
        }
      }
      
      if (date && !isNaN(date.getTime())) {
        const yearMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
        groups.set(yearMonth, (groups.get(yearMonth) || 0) + 1)
      }
    })
    
    console.log('📅 [ExifFilters] 时间分组结果:', Array.from(groups.entries()))
    
    // 排序：最新的在前
    return Array.from(groups.entries())
      .sort((a, b) => b[0].localeCompare(a[0]))
      .slice(0, 12) // 只显示最近12个月
  }, [photos])

  /**
   * 简化位置显示
   * 例如: "31.230416, 121.473701" -> "上海"
   */
  const simplifyLocation = (location: string): string => {
    // 如果是GPS坐标，显示坐标的前几位
    if (location.includes(',')) {
      const [lat, lng] = location.split(',').map(s => s.trim())
      const latShort = parseFloat(lat).toFixed(1)
      const lngShort = parseFloat(lng).toFixed(1)
      return `${latShort}, ${lngShort}`
    }
    return location
  }

  /**
   * 提取地理位置（简化显示）
   */
  const locations = useMemo(() => {
    const locationMap = new Map<string, number>()
    
    photos.forEach(photo => {
      if (photo.exif_data?.location) {
        const location = photo.exif_data.location
        // 简化GPS坐标显示
        const simplified = simplifyLocation(location)
        locationMap.set(simplified, (locationMap.get(simplified) || 0) + 1)
      }
    })
    
    return Array.from(locationMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10) // 最多显示10个位置
  }, [photos])

  /**
   * 提取相机型号
   */
  const cameras = useMemo(() => {
    const cameraMap = new Map<string, number>()
    
    photos.forEach(photo => {
      if (photo.exif_data?.camera) {
        const camera = photo.exif_data.camera
        cameraMap.set(camera, (cameraMap.get(camera) || 0) + 1)
      }
    })
    
    return Array.from(cameraMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
  }, [photos])

  /**
   * 格式化年月显示
   */
  const formatYearMonth = (yearMonth: string): string => {
    const [year, month] = yearMonth.split('-')
    const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', 
                        '7月', '8月', '9月', '10月', '11月', '12月']
    return `${year}年${monthNames[parseInt(month) - 1]}`
  }

  return (
    <div className="space-y-6">
      {/* 时间轴 */}
      {timeGroups.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <Calendar className="h-3 w-3" />
            时间轴
          </h3>
          <div className="space-y-1">
            {timeGroups.map(([yearMonth, count]) => (
              <button
                key={yearMonth}
                onClick={() => onFilterChange?.({ type: 'time', value: yearMonth })}
                className="w-full flex items-center justify-between px-3 py-1.5 text-sm rounded-md hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors"
              >
                <span>{formatYearMonth(yearMonth)}</span>
                <Badge variant="secondary" className="text-xs">
                  {count}
                </Badge>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 地理位置 */}
      {locations.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <MapPin className="h-3 w-3" />
            拍摄地点
          </h3>
          <div className="space-y-1">
            {locations.map(([location, count]) => (
              <button
                key={location}
                onClick={() => onFilterChange?.({ type: 'location', value: location })}
                className="w-full flex items-center justify-between px-3 py-1.5 text-sm rounded-md hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors group"
                title={location}
              >
                <span className="truncate">{location}</span>
                <Badge variant="secondary" className="text-xs ml-2 flex-shrink-0">
                  {count}
                </Badge>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 相机型号 */}
      {cameras.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <Camera className="h-3 w-3" />
            相机型号
          </h3>
          <div className="flex flex-wrap gap-2">
            {cameras.map(([camera, count]) => (
              <button
                key={camera}
                onClick={() => onFilterChange?.({ type: 'camera', value: camera })}
                className="inline-flex items-center gap-1.5 px-2 py-1 text-xs rounded-md bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
                title={camera}
              >
                <span className="max-w-[120px] truncate">{camera}</span>
                <Badge variant="outline" className="text-[10px] px-1 py-0 h-4">
                  {count}
                </Badge>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

