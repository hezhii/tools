# Output 处理工具 - 快速上手指南

## 📦 新增文件

已为你创建了以下文件：

```
product_scraper/
├── process_output.py              # 主处理脚本
├── run_process.sh                 # macOS/Linux 运行脚本
├── run_process.bat                # Windows 运行脚本
├── test_process.py                # 测试脚本
├── PROCESS_OUTPUT_README.md       # 详细使用说明
└── process_output.log             # 运行日志（运行后生成）
```

## 🚀 快速开始

### 第一步：测试环境（可选）

```bash
python test_process.py
```

这将检查：
- Pillow 库是否安装
- WebP 文件是否存在
- 产品详情文件是否存在

### 第二步：运行处理脚本

**macOS/Linux:**
```bash
./run_process.sh
```

**Windows:**
```batch
run_process.bat
```

**或直接运行 Python:**
```bash
python process_output.py
```

## ✨ 主要功能

### 功能 1: WebP 转 JPG
- **输入**: output 目录下的所有 `.webp` 图片
- **输出**: 相同位置生成 `.jpg` 图片
- **保留**: 原 WebP 文件不会被删除
- **质量**: JPG 质量设置为 95

**示例：**
```
转换前：
output/分类/产品/banner_1.webp

转换后：
output/分类/产品/banner_1.webp  ← 原文件保留
output/分类/产品/banner_1.jpg   ← 新生成
```

### 功能 2: 批量替换联系信息
- **文件**: 所有 `产品详情.md` 文件
- **替换内容**:
  - 联系人: `张小姐` → `孙女士`
  - 手机: `15021056285` → `17616263858`
  - QQ: `19625763603350634237` → `2474630730`
  - Email: `salesmicroframe.cn` → `2474630730@qq.com`

**特点**:
- 智能匹配，自动处理空白符
- 原地修改，不创建备份
- 详细日志，记录每次替换

## 📊 运行示例

```bash
$ python process_output.py

============================================================
开始处理 output 目录
============================================================
Output 目录: /Users/.../product_scraper/output

开始处理图片转换...
找到 45 个 WebP 图片
✓ 转换成功: banner_1.webp -> banner_1.jpg
✓ 转换成功: banner_2.webp -> banner_2.jpg
✓ 转换成功: banner_3.webp -> banner_3.jpg
...
图片转换完成: 45/45 成功

开始处理产品详情文件...
找到 120 个产品详情文件
✓ 更新文件: 传感器.../产品详情.md (4 处替换)
✓ 更新文件: 电磁阀.../产品详情.md (4 处替换)
...
产品详情处理完成: 85 个文件更新，共 340 处替换

============================================================
处理完成！
============================================================
```

## 📝 日志文件

运行后会生成 `process_output.log` 文件，包含：
- 每个文件的处理状态
- 成功/失败统计
- 详细的错误信息（如果有）

查看日志：
```bash
# 查看完整日志
cat process_output.log

# 查看最后 20 行
tail -20 process_output.log

# 实时查看日志
tail -f process_output.log
```

## ⚠️ 注意事项

### 图片转换
1. **依赖库**: 需要 Pillow 库（已在 requirements.txt 中）
2. **透明通道**: 带透明通道的 WebP 会转换为白色背景的 JPG
3. **重复运行**: 如果 JPG 已存在会跳过，不会重复转换
4. **原文件**: WebP 文件**不会**被删除

### 联系信息替换
1. **备份建议**: 首次运行前建议备份 output 目录
2. **不可逆**: 替换后无法自动恢复，需要重新爬取
3. **原地修改**: 直接修改原文件，不创建备份文件
4. **匹配规则**: 使用正则表达式，可能匹配到类似内容

## 🔧 自定义修改

### 只转换图片（不替换联系信息）

编辑 `process_output.py`，注释掉相应行：

```python
def main():
    # ...
    process_images(output_dir)
    # process_markdown_files(output_dir)  # 注释这行
```

### 只替换联系信息（不转换图片）

编辑 `process_output.py`，注释掉相应行：

```python
def main():
    # ...
    # process_images(output_dir)  # 注释这行
    process_markdown_files(output_dir)
```

### 修改替换内容

编辑 `process_output.py` 中的 `replacements_map`：

```python
replacements_map = [
    (r'联系人\s*:\s*张小姐', '联系人：你的名字'),
    (r'手机\s*:\s*15021056285', '手机：你的手机号'),
    # ... 添加更多替换规则
]
```

## 🐛 故障排查

### 问题 1: ImportError: No module named 'PIL'

**解决**:
```bash
pip install Pillow
```

### 问题 2: 转换后的图片质量不好

**解决**: 编辑 `process_output.py`，调整质量参数：
```python
img.save(jpg_path, 'JPEG', quality=98, optimize=True)  # 提高到98
```

### 问题 3: 无法找到 output 目录

**解决**: 确保在 `product_scraper` 目录中运行脚本：
```bash
cd product_scraper
python process_output.py
```

### 问题 4: 权限错误

**解决**:
```bash
# 给脚本添加执行权限
chmod +x run_process.sh

# 或使用 sudo（不推荐）
sudo python process_output.py
```

## 📚 相关文档

- **详细说明**: [PROCESS_OUTPUT_README.md](PROCESS_OUTPUT_README.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)
- **主文档**: [README.md](README.md)

## 🎯 下一步

1. **运行测试**: `python test_process.py`
2. **运行处理**: `./run_process.sh` 或 `python process_output.py`
3. **查看日志**: `cat process_output.log`
4. **验证结果**: 检查 output 目录中的 JPG 文件和产品详情

## 💡 提示

- 首次运行建议先备份 output 目录
- 可以多次运行，已处理的文件会被跳过
- 日志文件会追加内容，不会覆盖
- 如需恢复，重新运行爬虫脚本即可
