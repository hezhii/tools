# 更新日志

## 2025-10-25 - 功能增强

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
