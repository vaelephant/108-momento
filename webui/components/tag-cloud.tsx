"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth"
import { Badge } from "@/components/ui/badge"
import { Tag } from "lucide-react"

interface PopularTag {
  id: number
  name: string
  zh: string | null
  category: string
  useCount: number
  photoCount: number
}

interface TagCloudProps {
  onTagClick?: (tagName: string) => void
}

export function TagCloud({ onTagClick }: TagCloudProps) {
  const [tags, setTags] = useState<PopularTag[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    if (!user) {
      setTags([])
      setLoading(false)
      return
    }

    const fetchTags = async () => {
      try {
        const response = await fetch(`/api/tags/popular?userId=${user.id}&limit=20`)
        const data = await response.json()
        
        if (data.success) {
          setTags(data.tags)
        }
      } catch (error) {
        console.error('获取热门标签失败:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchTags()
  }, [user])

  if (loading || tags.length === 0) {
    return null
  }

  const maxCount = Math.max(...tags.map((t) => t.photoCount))
  const minCount = Math.min(...tags.map((t) => t.photoCount))

  const getTagSize = (count: number) => {
    if (maxCount === minCount) return "text-sm"
    const ratio = (count - minCount) / (maxCount - minCount)
    if (ratio > 0.75) return "text-base font-semibold"
    if (ratio > 0.5) return "text-sm font-medium"
    if (ratio > 0.25) return "text-sm"
    return "text-xs"
  }

  return (
    <div>
      <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
        <Tag className="h-3 w-3" />
        热门标签
      </h3>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const displayName = tag.zh || tag.name
          return (
            <Badge
              key={tag.id}
              variant="secondary"
              className={`${getTagSize(tag.photoCount)} cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors`}
              onClick={() => onTagClick?.(tag.name)}
            >
              {displayName}
              <span className="ml-1 text-xs opacity-60">({tag.photoCount})</span>
            </Badge>
          )
        })}
      </div>
    </div>
  )
}
