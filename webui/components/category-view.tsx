"use client"

import { useSyncExternalStore, useMemo } from "react"
import { PhotoCard } from "./photo-card"
import { photoStore } from "@/lib/photo-store"
import { CATEGORIES } from "@/lib/types"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ImageOff } from "lucide-react"

interface CategoryViewProps {
  searchQuery?: string
}

export function CategoryView({ searchQuery = "" }: CategoryViewProps) {
  const allPhotos = useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.getPhotos(),
    () => photoStore.getPhotos(),
  )
  
  // 根据搜索词过滤照片
  const photos = useMemo(() => {
    if (!searchQuery.trim()) return allPhotos
    
    const query = searchQuery.toLowerCase()
    return allPhotos.filter(photo => {
      if (photo.title?.toLowerCase().includes(query)) return true
      if (photo.description?.toLowerCase().includes(query)) return true
      if (photo.tags?.some(tag => tag.name.toLowerCase().includes(query))) return true
      return false
    })
  }, [allPhotos, searchQuery])

  // Group photos by category
  const photosByCategory = CATEGORIES.map((category) => ({
    ...category,
    photos: photos.filter((photo) => photo.category === category.value),
  })).filter((category) => category.photos.length > 0)

  if (photos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
          <ImageOff className="h-12 w-12 text-muted-foreground" />
        </div>
        <p className="text-foreground text-xl font-semibold mb-2">还没有照片</p>
        <p className="text-muted-foreground">点击上方按钮上传您的第一张照片</p>
      </div>
    )
  }

  if (photosByCategory.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
          <ImageOff className="h-12 w-12 text-muted-foreground" />
        </div>
        <p className="text-foreground text-xl font-semibold mb-2">没有已分类的照片</p>
      </div>
    )
  }

  return (
    <Accordion type="multiple" defaultValue={photosByCategory.map((cat) => cat.value)} className="space-y-6">
      {photosByCategory.map((category) => (
        <AccordionItem
          key={category.value}
          value={category.value}
          className="border border-border/50 rounded-2xl px-6 bg-card/50 backdrop-blur-sm shadow-sm hover:shadow-md transition-shadow"
        >
          <AccordionTrigger className="hover:no-underline py-6">
            <div className="flex items-center gap-4">
              <h2 className="text-2xl font-bold">{category.label}</h2>
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-semibold">
                {category.photos.length}
              </span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pt-2 pb-6">
              {category.photos.map((photo) => (
                <PhotoCard key={photo.id} photo={photo} />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}
