/**
 * 照片上传组件
 * 
 * 功能：
 * - 多文件上传
 * - 拖拽上传
 * - 照片预览
 * - 自动提取EXIF信息（拍摄时间、地点、相机信息）
 * - AI自动标注
 */

"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Upload, X, ImagePlus, Calendar, MapPin, Camera } from "lucide-react"
import { CATEGORIES } from "@/lib/types"
import { photoStore } from "@/lib/photo-store"
import { useToast } from "@/hooks/use-toast"
import exifr from "exifr"

// EXIF信息接口
interface ExifInfo {
  dateTaken?: Date
  location?: string
  camera?: string
  latitude?: number
  longitude?: number
  make?: string
  model?: string
  [key: string]: any
}

export function PhotoUpload() {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState("")
  const [description, setDescription] = useState("")
  const [tags, setTags] = useState("")
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [exifInfo, setExifInfo] = useState<ExifInfo | null>(null)
  const { toast } = useToast()

  /**
   * 提取照片EXIF信息
   * 包括拍摄时间、GPS位置、相机信息等
   */
  const extractExifData = async (file: File): Promise<ExifInfo> => {
    try {
      // 使用exifr库提取所有EXIF数据
      const exif = await exifr.parse(file, {
        gps: true,           // 提取GPS信息
        exif: true,          // 提取EXIF信息
        iptc: true,          // 提取IPTC信息
        icc: true,           // 提取颜色配置文件
        tiff: true,          // 提取TIFF信息
      })

      if (!exif) {
        console.log('📷 未找到EXIF信息')
        return {}
      }

      console.log('📷 原始EXIF数据:', exif)

      // 提取拍摄时间
      const dateTaken = exif.DateTimeOriginal || exif.CreateDate || exif.ModifyDate

      // 提取GPS位置
      let location = ''
      let latitude = exif.latitude
      let longitude = exif.longitude

      if (latitude && longitude) {
        // 将GPS坐标转换为可读的位置描述
        location = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
        console.log('📍 GPS位置:', location)
      }

      // 提取相机信息
      const make = exif.Make || ''
      const model = exif.Model || ''
      const camera = make && model ? `${make} ${model}`.trim() : make || model || ''

      const info: ExifInfo = {
        dateTaken: dateTaken ? new Date(dateTaken) : undefined,
        location,
        camera,
        latitude,
        longitude,
        make,
        model,
        // 保存完整的EXIF数据
        ...exif
      }

      console.log('✅ 提取的EXIF信息:', {
        dateTaken: info.dateTaken?.toLocaleString(),
        location: info.location,
        camera: info.camera
      })

      return info
    } catch (error) {
      console.error('❌ 提取EXIF信息失败:', error)
      return {}
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length > 0) {
      setFiles(selectedFiles)
      const urls: string[] = []
      
      // 提取第一个文件的EXIF信息用于预览
      if (selectedFiles[0]) {
        const exif = await extractExifData(selectedFiles[0])
        setExifInfo(exif)
      }

      selectedFiles.forEach((file) => {
        const reader = new FileReader()
        reader.onloadend = () => {
          urls.push(reader.result as string)
          if (urls.length === selectedFiles.length) {
            setPreviewUrls(urls)
          }
        }
        reader.readAsDataURL(file)
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (files.length === 0) {
      toast({
        title: "请选择照片",
        description: "请先选择要上传的照片",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    try {
      // 上传所有文件，并为每个文件提取EXIF信息
      const uploadPromises = files.map(async (file) => {
        // 提取当前文件的EXIF信息
        const exif = await extractExifData(file)
        
        // 上传照片，附带EXIF信息
        return photoStore.addPhoto(
          file, 
          title || file.name.replace(/\.[^/.]+$/, ""),
          exif  // 传递EXIF信息
        )
      })
      
      const results = await Promise.all(uploadPromises)
      
      const successCount = results.filter(photo => photo.aiProcessed !== false).length
      const aiProcessedCount = results.filter(photo => photo.aiProcessed === true).length

      // 显示成功信息，包括EXIF提取的信息
      const exifMsg = exifInfo?.dateTaken || exifInfo?.location 
        ? `\n${exifInfo.dateTaken ? '📅 ' + exifInfo.dateTaken.toLocaleDateString() : ''}${exifInfo.location ? ' 📍 位置已保存' : ''}`
        : ''

      toast({
        title: "上传成功",
        description: `${successCount}/${files.length} 张照片上传成功，${aiProcessedCount} 张完成AI分析${exifMsg}`,
      })

      // 清空表单
      setTitle("")
      setCategory("")
      setDescription("")
      setTags("")
      setPreviewUrls([])
      setFiles([])
      setExifInfo(null)
      setOpen(false)
    } catch (error) {
      console.error('❌ 上传失败:', error)
      toast({
        title: "上传失败",
        description: error instanceof Error ? error.message : "照片上传失败，请重试",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemovePreview = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    const newUrls = previewUrls.filter((_, i) => i !== index)
    setFiles(newFiles)
    setPreviewUrls(newUrls)
  }

  const handleRemoveAllPreviews = () => {
    setFiles([])
    setPreviewUrls([])
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) => file.type.startsWith("image/"))

    if (droppedFiles.length === 0) {
      toast({
        title: "Invalid file",
        description: "Please upload image files only",
        variant: "destructive",
      })
      return
    }

    // 添加到现有文件列表
    const newFiles = [...files, ...droppedFiles]
    setFiles(newFiles)
    
    // 生成预览
    const urls: string[] = []
    droppedFiles.forEach((file) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        urls.push(reader.result as string)
        if (urls.length === droppedFiles.length) {
          setPreviewUrls([...previewUrls, ...urls])
        }
      }
      reader.readAsDataURL(file)
    })
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []).filter((file) => file.type.startsWith("image/"))

    if (selectedFiles.length === 0) return

    // 添加到现有文件列表
    const newFiles = [...files, ...selectedFiles]
    setFiles(newFiles)
    
    // 生成预览
    const urls: string[] = []
    selectedFiles.forEach((file) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        urls.push(reader.result as string)
        if (urls.length === selectedFiles.length) {
          setPreviewUrls([...previewUrls, ...urls])
        }
      }
      reader.readAsDataURL(file)
    })

    e.target.value = ""
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="lg"
          className="gap-2 shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all"
          data-upload-button="true"
        >
          <Upload className="h-5 w-5" />
          上传照片
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="text-2xl">上传新照片</DialogTitle>
          <DialogDescription className="text-base">添加照片到您的相册，并选择合适的分类</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-3">
            <Label htmlFor="photo" className="text-base">
              照片
            </Label>
            {previewUrls.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    已选择 {files.length} 张照片
                  </p>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleRemoveAllPreviews}
                    className="text-destructive hover:text-destructive"
                  >
                    <X className="h-4 w-4 mr-2" />
                    清空所有
                  </Button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {previewUrls.map((url, index) => (
                    <div key={index} className="relative group">
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg border-2 border-border"
                      />
                      <Button
                        type="button"
                        variant="destructive"
                        size="icon"
                        className="absolute top-2 right-2 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6"
                        onClick={() => handleRemovePreview(index)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>

                {/* 显示第一张照片的EXIF信息 */}
                {exifInfo && (exifInfo.dateTaken || exifInfo.location || exifInfo.camera) && (
                  <div className="bg-muted/50 rounded-lg p-3 space-y-2">
                    <p className="text-sm font-medium text-foreground">📷 照片信息</p>
                    <div className="space-y-1.5 text-sm text-muted-foreground">
                      {exifInfo.dateTaken && (
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>拍摄时间: {exifInfo.dateTaken.toLocaleString('zh-CN', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}</span>
                        </div>
                      )}
                      {exifInfo.location && (
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4" />
                          <span>位置: {exifInfo.location}</span>
                        </div>
                      )}
                      {exifInfo.camera && (
                        <div className="flex items-center gap-2">
                          <Camera className="h-4 w-4" />
                          <span>相机: {exifInfo.camera}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`
                  border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer
                  ${
                    isDragging
                      ? "border-primary bg-primary/5 scale-[1.02]"
                      : "border-border/50 hover:border-primary/50 hover:bg-accent/30"
                  }
                `}
              >
                <Input id="photo" type="file" accept="image/*" multiple onChange={handleFileChange} className="hidden" />
                <label htmlFor="photo" className="cursor-pointer flex flex-col items-center gap-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    {isDragging ? (
                      <Upload className="h-8 w-8 text-primary animate-bounce" />
                    ) : (
                      <ImagePlus className="h-8 w-8 text-primary" />
                    )}
                  </div>
                  <div>
                    <p className="text-lg font-medium text-foreground">
                      {isDragging ? "Drop photos here" : "Drag & drop photos here"}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
                  </div>
                  <Button type="button" variant="outline" size="sm" className="pointer-events-none bg-transparent">
                    Select Photos
                  </Button>
                </label>
              </div>
            )}
          </div>

          <div className="space-y-3">
            <Label htmlFor="title" className="text-base">
              标题 (可选)
            </Label>
            <Input
              id="title"
              placeholder="输入照片标题"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="h-11"
            />
          </div>

          <div className="space-y-3">
            <Label htmlFor="category" className="text-base">
              分类
            </Label>
            <Select value={category} onValueChange={setCategory} required>
              <SelectTrigger id="category" className="h-11">
                <SelectValue placeholder="选择分类" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <Label htmlFor="tags" className="text-base">
              标签（可选）
            </Label>
            <Input
              id="tags"
              placeholder="输入标签，用逗号或空格分隔"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="h-11"
            />
            <p className="text-xs text-muted-foreground">例如: sunset, mountain, landscape</p>
          </div>

          <div className="space-y-3">
            <Label htmlFor="description" className="text-base">
              描述（可选）
            </Label>
            <Textarea
              id="description"
              placeholder="添加照片描述"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setOpen(false)} size="lg">
              取消
            </Button>
            <Button type="submit" size="lg" className="shadow-lg shadow-primary/20" disabled={isUploading}>
              {isUploading ? "上传中..." : "上传"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
