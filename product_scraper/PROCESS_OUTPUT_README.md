# Output 目录处理工具

## 功能说明

`process_output.py` 脚本用于批量处理 output 目录中的文件，包括：

### 1. 图片格式转换
- 遍历 output 目录下的所有 WebP 格式图片
- 将 WebP 图片转换为 JPG 格式
- 转换后的 JPG 图片放在与 WebP 相同的位置
- 文件名保持一致（仅扩展名改变）
- **原 WebP 文件不会被删除**

### 2. 联系信息替换
- 遍历 output 目录下的所有 `产品详情.md` 文件
- 替换以下联系信息：
  - **联系人**: `张小姐` → `孙女士`
  - **手机**: `15021056285` → `17616263858`
  - **QQ**: `19625763603350634237` → `2474630730`
  - **Email**: `salesmicroframe.cn` → `2474630730@qq.com`

**注意**：替换时会自动处理中间可能存在的空白符号（空格、制表符等）

## 使用方法

### 方法 1：使用运行脚本（推荐）

**macOS/Linux:**
```bash
cd product_scraper
./run_process.sh
```

**Windows:**
```batch
cd product_scraper
run_process.bat
```

### 方法 2：直接运行 Python 脚本

```bash
cd product_scraper
python process_output.py
```

## 运行示例

```bash
$ ./run_process.sh

==================================
处理 output 目录
==================================

激活虚拟环境...
运行处理脚本...
============================================================
开始处理 output 目录
============================================================
Output 目录: /Users/hezhou/.../product_scraper/output

开始处理图片转换...
找到 15 个 WebP 图片
✓ 转换成功: banner_1.webp -> banner_1.jpg
✓ 转换成功: banner_2.webp -> banner_2.jpg
✓ 转换成功: detail_1.webp -> detail_1.jpg
...
图片转换完成: 15/15 成功

开始处理产品详情文件...
找到 120 个产品详情文件
✓ 更新文件: 传感器 编码器 离合器/贝加莱BR模块.../产品详情.md (4 处替换)
✓ 更新文件: 电磁阀 球阀 阀门 控制阀/德国BURKERT.../产品详情.md (4 处替换)
...
产品详情处理完成: 120 个文件更新，共 480 处替换

============================================================
处理完成！
============================================================

完成！查看 process_output.log 了解详细信息
```

## 输出日志

脚本运行后会在 `product_scraper` 目录下生成 `process_output.log` 文件，包含详细的处理日志：

```
2025-10-26 14:30:00 - INFO - ============================================================
2025-10-26 14:30:00 - INFO - 开始处理 output 目录
2025-10-26 14:30:00 - INFO - ============================================================
2025-10-26 14:30:00 - INFO - Output 目录: /Users/.../output
2025-10-26 14:30:00 - INFO - 
2025-10-26 14:30:00 - INFO - 开始处理图片转换...
2025-10-26 14:30:00 - INFO - 找到 15 个 WebP 图片
2025-10-26 14:30:01 - INFO - ✓ 转换成功: banner_1.webp -> banner_1.jpg
...
```

## 注意事项

### 图片转换
1. **依赖库**：需要安装 Pillow 库（已包含在 requirements.txt 中）
2. **透明通道处理**：WebP 图片如果有透明通道，转换时会使用白色背景
3. **质量设置**：JPG 质量设置为 95，确保高质量输出
4. **重复运行**：如果 JPG 文件已存在，会跳过转换
5. **原文件保留**：WebP 原文件不会被删除

### 联系信息替换
1. **备份建议**：首次运行前建议备份 output 目录
2. **匹配模式**：使用正则表达式匹配，自动处理空白符差异
3. **不区分大小写**：Email 匹配时不区分大小写
4. **原地修改**：直接修改原文件，不创建备份

## 文件结构

处理后的文件结构示例：

```
output/
└── 传感器 编码器 离合器/
    └── 贝加莱BR模块.../
        ├── banner_1.webp        # 原 WebP 文件
        ├── banner_1.jpg         # 新转换的 JPG 文件
        ├── banner_2.webp
        ├── banner_2.jpg
        └── 产品详情.md           # 已更新联系信息
```

## 常见问题

### Q1: 如何只转换图片而不替换联系信息？
A: 修改 `process_output.py` 中的 `main()` 函数，注释掉 `process_markdown_files()` 行：

```python
def main():
    # ...
    process_images(output_dir)
    # process_markdown_files(output_dir)  # 注释这行
```

### Q2: 如何只替换联系信息而不转换图片？
A: 修改 `process_output.py` 中的 `main()` 函数，注释掉 `process_images()` 行：

```python
def main():
    # ...
    # process_images(output_dir)  # 注释这行
    process_markdown_files(output_dir)
```

### Q3: 转换失败了怎么办？
A: 查看 `process_output.log` 文件中的错误信息。常见原因：
- WebP 文件损坏
- 磁盘空间不足
- 权限问题

### Q4: 如何恢复原来的联系信息？
A: 脚本会直接修改文件，没有自动备份功能。建议：
- 首次运行前手动备份 output 目录
- 或者重新运行爬虫脚本获取原始数据

### Q5: 可以批量删除 WebP 文件吗？
A: 可以在转换完成后手动删除：

```bash
# macOS/Linux
find output -name "*.webp" -type f -delete

# Windows PowerShell
Get-ChildItem -Path output -Filter *.webp -Recurse | Remove-Item
```

**建议**：删除前先确认 JPG 文件都已正确生成

## 扩展功能

如需添加其他处理功能，可以修改 `process_output.py` 脚本：

1. 在脚本中添加新的处理函数
2. 在 `main()` 函数中调用新函数
3. 遵循现有的日志记录模式

示例：添加图片尺寸调整功能

```python
def resize_images(output_dir: Path, max_width: int = 1920):
    """调整图片尺寸"""
    # 实现代码...
    pass

def main():
    # ...
    process_images(output_dir)
    resize_images(output_dir)  # 添加新功能
    process_markdown_files(output_dir)
```

## 相关文件

- `process_output.py` - 主处理脚本
- `run_process.sh` - Linux/macOS 运行脚本
- `run_process.bat` - Windows 运行脚本
- `process_output.log` - 运行日志文件
- `PROCESS_OUTPUT_README.md` - 本说明文档
