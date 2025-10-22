/**
 * 主页面组件
 * 
 * 功能：
 * - 时间轴和分类视图切换
 * - 搜索功能（带防抖）
 * - 标签云快速过滤
 * - 用户认证状态管理
 * 
 * 优化：
 * - 使用防抖避免频繁搜索
 * - 状态提升便于组件间通信
 */

"use client"

import { useState, useSyncExternalStore, useEffect } from "react"
import { TimelineView } from "@/components/timeline-view"
import { CategoryView } from "@/components/category-view"
import { TagCloud } from "@/components/tag-cloud"
import { ExifFilters } from "@/components/exif-filters"
import { Header } from "@/components/header"
import { ApiTest } from "@/components/api-test"

import { Clock, Grid3x3 } from "lucide-react"
import { Toaster } from "@/components/ui/toaster"
import { useAuth } from "@/lib/auth"
import { useDebounce } from "@/hooks/use-debounce"
import { photoStore } from "@/lib/photo-store"

export default function Home() {
  const [activeView, setActiveView] = useState<"timeline" | "categories">("timeline")
  const [searchQuery, setSearchQuery] = useState("")
  const { isAuthenticated } = useAuth()

  // 获取所有照片用于EXIF筛选
  const allPhotos = useSyncExternalStore(
    (callback) => photoStore.subscribe(callback),
    () => photoStore.getPhotos(),
    () => photoStore.getPhotos(),
  )

  // 处理EXIF筛选
  const handleExifFilter = (filter: { type: 'time' | 'location' | 'camera', value: string }) => {
    // 根据筛选类型设置搜索词
    setSearchQuery(filter.value)
  }

  // 搜索防抖：用户停止输入300ms后才执行搜索
  // 避免每次输入都重新过滤照片列表，提升性能
  const debouncedSearch = useDebounce(searchQuery, 300)

  return (
    <div className="min-h-screen bg-background">
      <Header 
        activeView={activeView} 
        onViewChange={setActiveView}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <div className="flex">
        {/* 主内容区域：占满屏幕宽度，不使用container */}
        <main className="flex-1 px-6 py-6">
          {!isAuthenticated ? (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
              <div className="text-center space-y-4 max-w-3xl mx-auto">
                
                <div className="mt-8 pt-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                  <p className="text-xl italic animate-in fade-in duration-1500 delay-300 leading-relaxed">
                    "Sometimes you will never know the value of a moment, until it becomes a memory."<br />
                    <span className="text-lg opacity-90">"有时候，只有当一个瞬间成为回忆时，你才知道它的价值。"</span>
                  </p>
                  <p className="text-xl mt-6 font-serif opacity-80 animate-in fade-in slide-in-from-right-2 duration-700 delay-700">
                    —— Dr. Seuss
                  </p>
                </div>
                
              </div>
              {/* <div className="animate-in fade-in slide-in-from-bottom-2 duration-1000 delay-500">
                <ApiTest />
              </div> */}
            </div>
          ) : (
            // 使用防抖后的搜索词，减少不必要的重新渲染
            activeView === "timeline" ? <TimelineView searchQuery={debouncedSearch} /> : <CategoryView searchQuery={debouncedSearch} />
          )}
        </main>

        {/* 右侧边栏：标签云 */}
        <aside className="w-64 border-l border-border p-6 sticky top-[57px] h-[calc(100vh-57px)] overflow-y-auto hidden lg:block">
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">视图</h3>
              <div className="space-y-1">
                <button
                  onClick={() => setActiveView("timeline")}
                  className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                    activeView === "timeline"
                      ? "bg-secondary text-foreground font-medium"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`}
                >
                  <Clock className="h-4 w-4 inline mr-2" />
                  时间轴
                </button>
                <button
                  onClick={() => setActiveView("categories")}
                  className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                    activeView === "categories"
                      ? "bg-secondary text-foreground font-medium"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`}
                >
                  <Grid3x3 className="h-4 w-4 inline mr-2" />
                  分类
                </button>
              </div>
            </div>

            {/* EXIF筛选：时间、地点、相机 */}
            {isAuthenticated && allPhotos.length > 0 && (
              <ExifFilters 
                photos={allPhotos}
                onFilterChange={handleExifFilter}
              />
            )}

            {/* 分类 */}
            <div>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">分类</h3>
              <div className="space-y-1 text-sm">
                <div className="px-3 py-1.5 text-muted-foreground hover:text-foreground cursor-pointer">自然</div>
                <div className="px-3 py-1.5 text-muted-foreground hover:text-foreground cursor-pointer">城市</div>
                <div className="px-3 py-1.5 text-muted-foreground hover:text-foreground cursor-pointer">人像</div>
                <div className="px-3 py-1.5 text-muted-foreground hover:text-foreground cursor-pointer">美食</div>
                <div className="px-3 py-1.5 text-muted-foreground hover:text-foreground cursor-pointer">旅行</div>
              </div>
            </div>

            {/* AI标签云 */}
            <TagCloud onTagClick={(tagName) => setSearchQuery(tagName)} />
          </div>
        </aside>
      </div>

      <Toaster />
    </div>
  )
}
