# 📷 EXIF信息保留功能

## ✅ 功能说明

照片上传时会自动提取并保存EXIF信息，包括：
- 📅 **拍摄时间** - 照片的原始拍摄时间
- 📍 **GPS位置** - 拍摄地点的经纬度坐标
- 📷 **相机信息** - 相机品牌和型号

## 🎯 技术实现

### 前端（Next.js）

#### 1. EXIF提取 (`webui/components/photo-upload.tsx`)

使用 `exifr` 库提取照片的EXIF数据：

```typescript
import exifr from "exifr"

const extractExifData = async (file: File): Promise<ExifInfo> => {
  const exif = await exifr.parse(file, {
    gps: true,           // 提取GPS信息
    exif: true,          // 提取EXIF信息
    iptc: true,          // 提取IPTC信息
    icc: true,           // 提取颜色配置文件
    tiff: true,          // 提取TIFF信息
  })
  
  return {
    dateTaken: exif.DateTimeOriginal || exif.CreateDate,
    location: `${exif.latitude}, ${exif.longitude}`,
    camera: `${exif.Make} ${exif.Model}`,
    latitude: exif.latitude,
    longitude: exif.longitude,
  }
}
```

#### 2. UI展示

上传预览时会显示EXIF信息：

```tsx
{exifInfo && (
  <div className="bg-muted/50 rounded-lg p-3">
    <p className="text-sm font-medium">📷 照片信息</p>
    
    {exifInfo.dateTaken && (
      <div className="flex items-center gap-2">
        <Calendar className="h-4 w-4" />
        <span>拍摄时间: {exifInfo.dateTaken.toLocaleString()}</span>
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
)}
```

#### 3. 数据传递 (`webui/lib/photo-store.ts`)

```typescript
async addPhoto(file: File, caption?: string, exifData?: any) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('caption', caption)
  formData.append('userId', user.id.toString())
  
  // 添加EXIF信息
  if (exifData) {
    const exifToSend = {
      dateTaken: exifData.dateTaken?.toISOString(),
      location: exifData.location,
      camera: exifData.camera,
      latitude: exifData.latitude,
      longitude: exifData.longitude,
    }
    formData.append('exifData', JSON.stringify(exifToSend))
  }
  
  await fetch('/api/photos/upload', {
    method: 'POST',
    body: formData
  })
}
```

### 中间层（Next.js API）

#### API路由 (`webui/app/api/photos/upload/route.ts`)

```typescript
export async function POST(request: NextRequest) {
  const formData = await request.formData()
  const file = formData.get('file') as File
  const exifDataStr = formData.get('exifData') as string
  
  // 转发到FastAPI
  const aiFormData = new FormData()
  aiFormData.append('file', file)
  aiFormData.append('exif_data', exifDataStr)
  
  const response = await fetch(`${fastApiUrl}/api/v1/photos/upload`, {
    method: 'POST',
    body: aiFormData
  })
}
```

### 后端（FastAPI + PostgreSQL）

#### 1. API端点 (`server/app/api/v1/photos.py`)

```python
@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    user_id: int = Form(...),
    exif_data: Optional[str] = Form(None),  # EXIF信息
    db: Session = Depends(get_db)
):
    # 解析EXIF数据
    if exif_data:
        exif_dict = json.loads(exif_data)
        taken_at = parser.parse(exif_dict['dateTaken'])
        location = exif_dict['location']
        camera_info = exif_dict['camera']
    
    # 创建照片记录
    photo = photo_service.create_photo(
        user_id=user_id,
        filename=file.filename,
        storage_path=storage_path,
        file_size=file_size,
        caption=caption,
        exif_data=exif_dict  # 保存EXIF数据
    )
    
    # 更新拍摄时间
    if taken_at:
        photo.taken_at = taken_at
        db.commit()
```

#### 2. 数据库模型 (`server/app/models.py`)

```python
class Photo(Base):
    __tablename__ = "photos"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    
    # EXIF相关字段
    taken_at = Column(DateTime, nullable=True)  # 拍摄时间
    exif_data = Column(JSON, nullable=True)     # 完整EXIF数据
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

## 📊 数据流程

```
1. 用户选择照片
   ↓
2. 前端提取EXIF信息 (exifr)
   ↓
3. 显示预览 + EXIF信息
   ↓
4. 用户点击上传
   ↓
5. FormData包含: file + caption + exifData
   ↓
6. Next.js API接收并转发
   ↓
7. FastAPI接收并解析
   ↓
8. 保存到PostgreSQL:
   - photos表: taken_at, exif_data字段
   ↓
9. 返回照片信息（包含EXIF）
   ↓
10. 前端显示照片详情时展示EXIF
```

## 🎨 UI展示位置

### 1. 上传预览
```
┌─────────────────────────────┐
│  [照片预览图]               │
│                             │
│  📷 照片信息                │
│  📅 拍摄时间: 2024年10月22日│
│  📍 位置: 31.23, 121.47     │
│  📷 相机: Canon EOS 5D     │
└─────────────────────────────┘
```

### 2. 照片详情页 (`webui/components/photo-detail-dialog.tsx`)
```
┌─────────────────────────────┐
│  照片信息                   │
├─────────────────────────────┤
│  📅 上传时间: 2024-10-22   │
│  📅 拍摄时间: 2024-10-20   │
│  📍 地点: 31.23, 121.47    │
│  📷 相机: Canon EOS 5D     │
│  📏 尺寸: 4000 × 3000 px   │
└─────────────────────────────┘
```

## 🔧 使用方法

### 安装依赖

前端：
```bash
cd webui
pnpm add exifr
```

后端：
```bash
cd server
pip install python-dateutil  # 日期解析
```

### 测试

1. **选择带EXIF的照片**
   - 用手机拍摄的照片通常包含EXIF
   - 相机拍摄的RAW或JPEG照片

2. **上传照片**
   - 点击上传按钮
   - 选择照片
   - 查看预览区的EXIF信息

3. **查看详情**
   - 上传成功后
   - 点击照片卡片
   - 在详情对话框中查看完整信息

## 📝 支持的EXIF字段

### 基础信息
- `DateTimeOriginal` - 原始拍摄时间
- `CreateDate` - 创建日期
- `ModifyDate` - 修改日期

### GPS信息
- `latitude` - 纬度
- `longitude` - 经度
- `altitude` - 海拔
- `GPSTimeStamp` - GPS时间戳

### 相机信息
- `Make` - 相机品牌 (Canon, Nikon, Sony等)
- `Model` - 相机型号 (EOS 5D, D850等)
- `LensModel` - 镜头型号
- `FocalLength` - 焦距
- `FNumber` - 光圈值
- `ExposureTime` - 快门速度
- `ISO` - 感光度

### 图像信息
- `ImageWidth` - 图像宽度
- `ImageHeight` - 图像高度
- `Orientation` - 方向
- `ColorSpace` - 色彩空间

## 🚀 未来增强

### 1. 地图显示
```typescript
// 使用高德地图或百度地图API显示拍摄位置
{photo.latitude && photo.longitude && (
  <MapComponent 
    lat={photo.latitude} 
    lng={photo.longitude} 
  />
)}
```

### 2. 反向地理编码
```typescript
// 将GPS坐标转换为地址
const address = await getAddressFromCoords(
  photo.latitude, 
  photo.longitude
)
// "中国上海市浦东新区陆家嘴"
```

### 3. EXIF搜索
```typescript
// 按拍摄时间范围搜索
searchByDateRange(startDate, endDate)

// 按地点搜索
searchByLocation(latitude, longitude, radius)

// 按相机型号搜索
searchByCamera("Canon EOS 5D")
```

### 4. EXIF编辑
```typescript
// 允许用户修改EXIF信息
updatePhotoExif(photoId, {
  location: "新的位置",
  dateTaken: new Date()
})
```

## ⚠️ 注意事项

1. **隐私保护**
   - GPS位置是敏感信息
   - 建议添加隐私设置：是否公开位置信息
   - 分享照片时可选择是否包含EXIF

2. **文件大小**
   - EXIF数据会增加少量文件大小
   - 前端已过滤掉不必要的字段

3. **兼容性**
   - 并非所有照片都有EXIF
   - 某些编辑软件会移除EXIF
   - 截图通常没有EXIF

4. **性能**
   - EXIF提取是异步操作
   - 大文件可能需要较长时间
   - 建议显示提取进度

## 📚 参考资料

- [exifr文档](https://github.com/MikeKovarik/exifr)
- [EXIF标准](https://en.wikipedia.org/wiki/Exif)
- [GPS EXIF](https://exiftool.org/TagNames/GPS.html)

---

更新时间: 2024-10-22
版本: 1.0.0

