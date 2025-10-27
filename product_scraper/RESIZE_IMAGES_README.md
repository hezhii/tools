# 图片尺寸调整工具

## 功能说明

`resize_images.py` 脚本用于批量调整 output 目录中的 JPG 图片尺寸。

### 主要功能
1. **智能筛选**: 只处理小于 750x750 的图片
2. **等比放大**: 保持原始宽高比，将最小边放大到 750 以上
3. **高质量输出**: 使用 LANCZOS 算法和高质量参数
4. **安全处理**: 原图保留，处理后的图片添加 `big_` 前缀
5. **统计信息**: 显示处理前后的图片尺寸分布

### 处理规则

- **需要处理**: 宽度或高度任一小于 750px 的图片
- **跳过处理**: 宽度和高度都 >= 750px 的图片
- **输出命名**: 处理后的图片添加 `big_` 前缀
- **原图保留**: 原始图片不会被修改或删除

## 使用方法

### 方法 1: 使用运行脚本（推荐）

**macOS/Linux:**
```bash
cd product_scraper
./run_resize.sh
```

**Windows:**
```batch
cd product_scraper
run_resize.bat
```

### 方法 2: 直接运行 Python 脚本

```bash
cd product_scraper
python resize_images.py
```

## 运行示例

```bash
$ ./run_resize.sh

============================================================
图片尺寸调整工具
============================================================
目标尺寸: 750x750 (最小边)

Output 目录: /Users/.../product_scraper/output

正在统计图片尺寸信息...

图片尺寸统计（共 120 个图片）:
  小于 750x750: 45 个
  750x750 ~ 1500x1500: 60 个
  大于 1500x1500: 15 个
  带 big_ 前缀: 0 个

开始处理图片调整（目标最小尺寸: 750x750）...
找到 120 个 JPG 图片
✓ 调整成功: banner_1.jpg (500x500) -> big_banner_1.jpg (750x750)
✓ 调整成功: banner_2.jpg (600x400) -> big_banner_2.jpg (1125x750)
✓ 调整成功: detail_1.jpg (480x640) -> big_detail_1.jpg (750x1000)
  跳过（尺寸已满足）: banner_3.jpg (800x800)
  跳过（尺寸已满足）: detail_2.jpg (1200x900)
...

图片调整完成:
  总计: 120 个图片
  成功调整: 45 个
  跳过: 75 个（已满足尺寸要求或已处理）

正在统计图片尺寸信息...

图片尺寸统计（共 165 个图片）:
  小于 750x750: 0 个
  750x750 ~ 1500x1500: 105 个
  大于 1500x1500: 60 个
  带 big_ 前缀: 45 个

============================================================
处理完成！
============================================================
```

## 处理示例

### 示例 1: 正方形图片
```
原图: banner_1.jpg (500x500)
新图: big_banner_1.jpg (750x750)
说明: 等比放大 1.5 倍
```

### 示例 2: 横向图片
```
原图: banner_2.jpg (600x400)
新图: big_banner_2.jpg (1125x750)
说明: 以最小边（400）为准，放大 1.875 倍
```

### 示例 3: 纵向图片
```
原图: detail_1.jpg (480x640)
新图: big_detail_1.jpg (750x1000)
说明: 以最小边（480）为准，放大 1.5625 倍
```

### 示例 4: 已满足尺寸
```
原图: banner_3.jpg (800x800)
处理: 跳过（尺寸已满足）
说明: 宽高都 >= 750，无需处理
```

## 技术细节

### 图片质量优化

脚本使用以下技术确保最高质量：

1. **LANCZOS 重采样算法**
   - PIL 中最高质量的重采样滤镜
   - 专为放大图片设计
   - 保留图片细节，减少失真

2. **高质量 JPEG 参数**
   ```python
   quality=95          # JPEG 质量（0-100）
   optimize=True       # 优化文件大小
   subsampling=0       # 禁用色度子采样（保持最高质量）
   ```

3. **透明通道处理**
   - 自动检测带透明通道的图片
   - 使用白色背景替换透明部分
   - 确保 JPG 格式兼容性

### 尺寸计算逻辑

```python
# 以最小边为基准计算缩放比例
min_dimension = min(width, height)
scale_ratio = 750 / min_dimension

# 等比放大
new_width = int(width * scale_ratio)
new_height = int(height * scale_ratio)
```

## 文件结构

处理后的文件结构示例：

```
output/
└── 传感器 编码器 离合器/
    └── 贝加莱BR模块.../
        ├── banner_1.jpg           # 原图 (500x500)
        ├── big_banner_1.jpg       # 处理后 (750x750)
        ├── banner_2.jpg           # 原图 (800x600)
        └── 产品详情.md
```

## 输出日志

脚本运行后会在 `product_scraper` 目录下生成 `resize_images.log` 文件：

```
2025-10-26 15:00:00 - INFO - ============================================================
2025-10-26 15:00:00 - INFO - 图片尺寸调整工具
2025-10-26 15:00:00 - INFO - ============================================================
2025-10-26 15:00:00 - INFO - 目标尺寸: 750x750 (最小边)
2025-10-26 15:00:01 - INFO - 开始处理图片调整（目标最小尺寸: 750x750）...
2025-10-26 15:00:01 - INFO - 找到 120 个 JPG 图片
2025-10-26 15:00:02 - INFO - ✓ 调整成功: banner_1.jpg (500x500) -> big_banner_1.jpg (750x750)
...
```

## 注意事项

### 1. 磁盘空间
- 处理后会生成新文件，需要额外的磁盘空间
- 估算空间: 原图总大小 × 放大倍数的平方
- 例如: 500x500 放大到 750x750，文件大小约增加 2.25 倍

### 2. 处理时间
- 处理速度取决于图片数量和尺寸
- 大约 1-5 秒/图片（取决于原始尺寸）
- 100 张图片约需 2-8 分钟

### 3. 原图保留
- 原始图片**不会**被修改
- 可以安全地重复运行脚本
- 如需删除原图，需要手动删除

### 4. 重复运行
- 再次运行会跳过已存在的 `big_` 文件
- 不会重复处理
- 日志会追加，不会覆盖

## 常见问题

### Q1: 如何修改目标尺寸？

A: 编辑 `resize_images.py` 文件，修改 `TARGET_MIN_SIZE` 常量：

```python
# 目标最小尺寸
TARGET_MIN_SIZE = 1000  # 改为 1000x1000
```

### Q2: 如何调整图片质量？

A: 编辑 `resize_images.py` 文件，修改保存参数：

```python
resized_img.save(new_path, 'JPEG', quality=98, optimize=True, subsampling=0)
# 质量范围: 1-100，建议 90-98
```

### Q3: 处理后图片很模糊怎么办？

A: 可能是原图分辨率太低。建议：
1. 检查原图质量
2. 提高 JPEG 质量参数（95-98）
3. 考虑使用其他放大算法（如 AI 超分辨率）

### Q4: 如何批量删除 big_ 文件？

A: 使用以下命令：

```bash
# macOS/Linux
find output -name "big_*.jpg" -type f -delete

# Windows PowerShell
Get-ChildItem -Path output -Filter big_*.jpg -Recurse | Remove-Item
```

### Q5: 可以只处理特定文件夹的图片吗？

A: 修改脚本，指定特定路径：

```python
def main():
    # 只处理特定分类
    output_dir = Path(__file__).parent / 'output' / '传感器 编码器 离合器'
    # ...
```

### Q6: 原图尺寸已经很大，还能进一步放大吗？

A: 可以，但不推荐。放大已经较大的图片可能导致：
- 文件体积急剧增大
- 图片质量反而下降
- 没有实际价值

## 高级用法

### 自定义处理逻辑

编辑 `resize_images.py`，可以实现：

1. **固定尺寸（非等比）**
```python
new_width, new_height = 750, 750  # 强制 750x750
resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
```

2. **添加白边（保持等比但填充到固定尺寸）**
```python
# 先等比缩放
ratio = min(750/width, 750/height)
new_size = (int(width*ratio), int(height*ratio))
resized = img.resize(new_size, Image.Resampling.LANCZOS)

# 创建白色背景
background = Image.new('RGB', (750, 750), (255, 255, 255))
# 居中粘贴
offset = ((750 - new_size[0]) // 2, (750 - new_size[1]) // 2)
background.paste(resized, offset)
```

3. **批量压缩（减小文件大小）**
```python
img.save(new_path, 'JPEG', quality=80, optimize=True)
```

## 性能优化

对于大量图片的处理，可以启用多线程：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_images(output_dir: Path, min_size: int = TARGET_MIN_SIZE):
    # ...
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(resize_image, jpg_file, min_size) 
                   for jpg_file in jpg_files]
        
        for future in as_completed(futures):
            result = future.result()
            # ...
```

## 相关工具

本脚本是 product_scraper 工具集的一部分：

- **product_scraper.py** - 爬取产品数据
- **process_output.py** - WebP 转 JPG，替换联系信息
- **resize_images.py** - 调整图片尺寸（本工具）

建议处理流程：
1. 运行爬虫获取数据
2. 运行 `process_output.py` 转换格式和替换信息
3. 运行 `resize_images.py` 调整图片尺寸

## 相关文档

- **主文档**: [README.md](README.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)
- **WebP 转换工具**: [PROCESS_OUTPUT_README.md](PROCESS_OUTPUT_README.md)
