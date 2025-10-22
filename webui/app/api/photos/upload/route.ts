import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  console.log('🚀 [Next.js API] 开始处理照片上传请求')
  
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const caption = formData.get('caption') as string
    const userId = formData.get('userId') as string
    const exifDataStr = formData.get('exifData') as string

    console.log('📋 [Next.js API] 请求参数:')
    console.log('  - 文件名:', file?.name)
    console.log('  - 文件大小:', file?.size)
    console.log('  - 文件类型:', file?.type)
    console.log('  - 用户ID:', userId)
    console.log('  - 描述:', caption)
    console.log('  - EXIF数据:', exifDataStr ? '✅ 已提供' : '❌ 无')

    if (!file) {
      console.log('❌ [Next.js API] 文件为空')
      return NextResponse.json(
        { error: '请选择要上传的文件' },
        { status: 400 }
      )
    }

    if (!userId) {
      console.log('❌ [Next.js API] 用户ID为空')
      return NextResponse.json(
        { error: '用户ID不能为空' },
        { status: 400 }
      )
    }

    // 调用FastAPI进行AI处理和存储
    const fastApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'
    
    try {
      // 简化认证，直接使用用户ID
      console.log('🔑 [Next.js API] 使用用户ID认证:')
      console.log('  - 用户ID:', userId)

      // 准备发送给FastAPI的数据
      const aiFormData = new FormData()
      aiFormData.append('file', file)
      if (caption) {
        aiFormData.append('caption', caption)
      }
      aiFormData.append('user_id', userId)
      
      // 传递EXIF信息到FastAPI
      if (exifDataStr) {
        aiFormData.append('exif_data', exifDataStr)
        const exifData = JSON.parse(exifDataStr)
        console.log('📷 [Next.js API] EXIF信息:')
        console.log('  - 拍摄时间:', exifData.dateTaken || '无')
        console.log('  - 位置:', exifData.location || '无')
        console.log('  - 相机:', exifData.camera || '无')
      }

      console.log('🚀 [Next.js API] 准备调用FastAPI...')
      console.log('📡 FastAPI URL:', `${fastApiUrl}/api/v1/photos/upload`)
      console.log('📦 FormData内容:')
      console.log('  - file:', file.name)
      console.log('  - caption:', caption || '无')
      console.log('  - user_id:', userId)
      console.log('  - exif_data:', exifDataStr ? '✅' : '❌')

      // 调用FastAPI的AI处理接口
      console.log('📤 [Next.js API] 发送请求到FastAPI...')
      const aiResponse = await fetch(`${fastApiUrl}/api/v1/photos/upload`, {
        method: 'POST',
        body: aiFormData,
      })

      console.log('📡 [Next.js API] FastAPI响应:')
      console.log('  - 状态码:', aiResponse.status)
      console.log('  - 状态文本:', aiResponse.statusText)
      console.log('  - 响应头:', Object.fromEntries(aiResponse.headers.entries()))

      if (!aiResponse.ok) {
        const errorText = await aiResponse.text()
        console.error('❌ [Next.js API] FastAPI处理失败:')
        console.error('  - 错误信息:', errorText)
        console.error('  - 响应状态:', aiResponse.status)
        return NextResponse.json(
          { error: `FastAPI处理失败 (${aiResponse.status}): ${errorText}` },
          { status: 500 }
        )
      }

      const aiResult = await aiResponse.json()
      console.log('✅ [Next.js API] FastAPI处理成功:')
      console.log('  - 响应数据:', JSON.stringify(aiResult, null, 2))
      
      // 构建照片URL
      const photoUrl = `${fastApiUrl}/uploads/${userId}/${aiResult.filename}`
      
      console.log('📸 [Next.js API] 构建照片信息:')
      console.log('  - 照片ID:', aiResult.photo_id)
      console.log('  - 文件名:', aiResult.filename)
      console.log('  - 照片URL:', photoUrl)
      console.log('  - EXIF数据:', aiResult.exif_data ? '有' : '无')
      console.log('  - 拍摄时间:', aiResult.taken_at)
      
      // 返回FastAPI的处理结果
      return NextResponse.json({
        success: true,
        photo: {
          id: aiResult.photo_id.toString(),
          url: photoUrl,
          title: caption || file.name.replace(/\.[^/.]+$/, ""),
          category: 'other',
          uploadedAt: new Date(), // 返回Date对象而不是字符串
          description: caption,
          tags: aiResult.tags || [],
          userId: parseInt(userId),
          aiProcessed: true,
          aiError: null,
          // 添加EXIF数据
          exif_data: aiResult.exif_data ? {
            camera: aiResult.exif_data.camera,
            location: aiResult.exif_data.location,
            dateTaken: aiResult.taken_at, // 使用taken_at字段
            ...aiResult.exif_data
          } : undefined,
        }
      })

    } catch (aiError) {
      console.error('❌ [Next.js API] FastAPI调用失败:')
      console.error('  - 错误类型:', aiError.constructor.name)
      console.error('  - 错误信息:', aiError.message)
      console.error('  - 错误堆栈:', aiError.stack)
      return NextResponse.json(
        { error: `FastAPI服务连接失败: ${aiError.message}` },
        { status: 500 }
      )
    }

  } catch (error) {
    console.error('❌ [Next.js API] 照片上传失败:')
    console.error('  - 错误类型:', error.constructor.name)
    console.error('  - 错误信息:', error.message)
    console.error('  - 错误堆栈:', error.stack)
    return NextResponse.json(
      { error: '照片上传失败，请重试' },
      { status: 500 }
    )
  }
}