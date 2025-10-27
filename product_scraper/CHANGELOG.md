# 更新日志

## 2025-10-26 - 图片尺寸调整工具 v2.2

新增 **图片尺寸调整工具**，智能处理产品图片，确保图片尺寸符合展示要求。

### 新增文件
- `resize_images.py` - 图片尺寸调整脚本
- `run_resize.sh` - Linux/macOS 运行脚本
- `run_resize.bat` - Windows 运行脚本
- `RESIZE_IMAGES_README.md` - 详细使用说明

### 核心功能
- ✅ **智能筛选** - 只处理小于 750x750 的 JPG 图片
- ✅ **等比放大** - 保持原图宽高比，根据最小边自动计算缩放比例
- ✅ **高质量算法** - 使用 Pillow 的 LANCZOS 算法，确保图片清晰
- ✅ **安全处理** - 原图保留，处理后的图片添加 `big_` 前缀
- ✅ **避免重复** - 自动跳过已处理的 `big_` 开头的文件
- ✅ **统计对比** - 展示处理前后的图片尺寸分布

### 工作原理
1. 扫描 output 目录下所有 JPG 图片
2. 筛选出尺寸小于 750x750 的图片
3. 计算缩放比例（以最小边为基准）
4. 等比放大图片至最小边 ≥ 750px
5. 保存为 `big_原文件名.jpg`

### 使用方式
```bash
# macOS/Linux
./run_resize.sh

# Windows
run_resize.bat

# 或直接运行
python resize_images.py
```

### 图片质量保证
- **重采样算法**: LANCZOS（最高质量）
- **JPG 质量**: 95%
- **色彩子采样**: 4:4:4（关闭）
- **EXIF 保留**: 保持原图元数据

### 日志输出
- 自动生成 `resize_images.log` 文件
- 记录每张图片的处理详情
- 统计尺寸分布和处理结果

---

## 2025-10-26 - Output 处理工具 v2.1

新增 **Output 处理工具**，用于批量处理已爬取的数据。

### 新增文件
- `process_output.py` - 主处理脚本
- `run_process.sh` - Linux/macOS 运行脚本
- `run_process.bat` - Windows 运行脚本
- `PROCESS_OUTPUT_README.md` - 详细使用说明

### 功能 1: WebP 图片转 JPG
- ✅ 自动遍历 output 目录下的所有 WebP 图片
- ✅ 转换为高质量 JPG 格式（质量95）
- ✅ 保持原文件名（仅扩展名改变）
- ✅ 保存在与 WebP 相同位置
- ✅ **原 WebP 文件不删除**
- ✅ 自动处理透明通道（使用白色背景）
- ✅ 跳过已转换的文件

### 功能 2: 批量替换联系信息
- ✅ 遍历所有 `产品详情.md` 文件
- ✅ 批量替换联系信息：
  - 联系人：张小姐 → 孙女士
  - 手机：15021056285 → 17616263858
  - QQ：19625763603350634237 → 2474630730
  - Email：salesmicroframe.cn → 2474630730@qq.com
- ✅ 智能匹配：自动处理中间的空白符号
- ✅ 详细日志：记录每个文件的替换次数

### 使用方式
```bash
# macOS/Linux
./run_process.sh

# Windows
run_process.bat

# 或直接运行
python process_output.py
```

### 日志输出
- 自动生成 `process_output.log` 文件
- 记录详细的处理过程和结果
- 包含成功/失败统计信息

---

## 2025-10-25 - 重要改进 v2.0

根据 prompt.txt 中的要求，完成了以下改进：

### 1. 新增 Banner 图片爬取功能
- ✅ 从商品详情页左上角的图片 banner 中提取所有图片
- ✅ 解析 `data-config` 属性中的 `showing_image` 字段
- ✅ 同时从 `<img>` 标签的 `src` 属性获取图片 URL
- ✅ 自动过滤无效图片（占位符、加载动画等）

### 2. 新增详情页介绍图片爬取功能
- ✅ 从详情页 `sp-bd pdsx` 容器中提取所有介绍图片
- ✅ 支持多种图片属性：`src`, `data-original`, `data-src`, `data-lazy`
- ✅ 与 banner 图片一起下载保存

### 3. 重新组织 Excel 输出格式
调整为以下字段（按要求的顺序）：
- ✅ 商品名称
- ✅ 商品分类
- ✅ 商品价格
- ✅ 商品详情页 URL

工作表组织：
- ✅ 主表："产品汇总" - 包含所有产品
- ✅ 按分类创建独立工作表

### 4. 新增文件夹结构组织
- ✅ 按照 `分类名称/商品名称` 的方式创建文件夹
- ✅ 将每个产品的所有图片保存到对应文件夹
  - Banner 图片：命名为 `banner_1.jpg`, `banner_2.jpg` 等
  - 详情图片：命名为 `detail_1.jpg`, `detail_2.jpg` 等
- ✅ 将产品详情文本保存为 `产品详情.md` 文件

### 5. 改进的 `extract_product_details` 方法
- 原来返回：`str` (只有详情文本)
- 现在返回：`Tuple[str, List[str], List[str]]` (详情文本, banner图片列表, 详情图片列表)

### 6. 新增方法
- `extract_banner_images(soup)`: 提取 banner 图片 URL
- `extract_detail_images(soup)`: 提取详情页图片 URL
- `download_product_images_to_folders()`: 下载所有图片到分类/产品文件夹

### 文件结构示例

```
output/
├── products.xlsx                      # 产品汇总表（按要求的格式）
├── 离合器联轴器/                        # 分类文件夹
│   ├── FORMSPRAG超越离合器/              # 产品文件夹
│   │   ├── banner_1.jpg              # Banner 图片
│   │   ├── banner_2.jpg
│   │   ├── banner_3.jpg
│   │   ├── detail_1.jpg              # 详情图片
│   │   ├── detail_2.jpg
│   │   └── 产品详情.md                # 产品详情文本
│   └── 其他产品/
└── 其他分类/

```

### 配置说明

确保 `config.json` 中启用了详情页获取：

```json
{
  "scraper_settings": {
    "fetch_product_details": true,
    "details_delay_range": [5, 10]
  }
}
```

### 使用方法

```bash
# macOS/Linux
./run_scraper.sh

# Windows
run_scraper.bat

# 或直接运行
python product_scraper.py
```

### 注意事项

1. 爬取详情页和下载所有图片会显著增加运行时间
2. 建议保持适当的延时设置，避免触发反爬机制
3. 所有图片和详情文本按照分类和产品名称组织，便于后续使用
4. Excel 文件简洁明了，只包含必要的汇总信息
