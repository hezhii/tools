# Excel 处理工具

用于处理专利数据 Excel 文件的工具脚本。

## 功能

### 功能 1: 检测未被系统识别的列名
- 递归遍历指定文件夹下所有的 Excel 文件(包括子目录)
- 读取每个 Excel 文件的第一行(列头)
- 与系统可识别列名数组进行比对
- 找出 Excel 中有而系统列名数组中没有的列名
- 汇总所有 Excel 文件的结果并去重后输出

### 功能 2: 精简 Excel 文件
- 遍历指定文件夹下的所有 Excel 文件
- 减少 Excel 中的数据量,仅保留列头和最多 5 条数据(可自定义)
- 将结果输出到脚本所在目录的 `output` 目录下
- 保持原始目录结构
- 不修改输入的原始数据

## 环境要求

- Python 3.7+
- pandas
- openpyxl
- xlrd

## 安装

### 1. 创建虚拟环境(推荐)

```bash
cd excel_processor
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本语法

```bash
python process_excel.py <功能编号> <输入目录> [最大行数]
```

### 参数说明

- `功能编号`: 
  - `1` - 检测未被系统识别的列名
  - `2` - 精简 Excel 文件
  - `all` - 执行所有功能
- `输入目录`: Excel 文件所在的目录路径
- `最大行数`: (可选) 功能2中保留的最大数据行数,默认为 5

### 使用示例

#### 1. 检测未识别的列名

```bash
python process_excel.py 1 /path/to/excel/folder
```

#### 2. 精简 Excel 文件(保留5条数据)

```bash
python process_excel.py 2 /path/to/excel/folder
```

#### 3. 精简 Excel 文件(保留10条数据)

```bash
python process_excel.py 2 /path/to/excel/folder 10
```

#### 4. 执行所有功能

```bash
python process_excel.py all /path/to/excel/folder
```

## 输出说明

### 功能 1 输出
- 在控制台打印每个文件的处理状态
- 显示每个文件中发现的未识别列名
- 最后输出所有未识别列名的去重汇总结果

### 功能 2 输出
- 精简后的 Excel 文件保存在 `excel_processor/output/` 目录下
- 保持与输入目录相同的子目录结构
- 控制台显示处理进度和统计结果

## 系统识别的列名

脚本中包含了 180+ 个系统可识别的专利数据列名,包括:
- 基本信息: 标题、申请人、公开号、摘要等
- 申请信息: 申请号、申请日、专利类型等
- 法律状态: 专利有效性、法律文书等
- 申请人信息: 地址、类型、工商信息等
- 引证信息: 引证专利、被引证专利等
- 同族信息: 简单同族、扩展同族等

详细列名列表请查看脚本中的 `SYSTEM_COLUMNS` 变量。

## 注意事项

1. 支持的 Excel 格式: `.xlsx`, `.xls`, `.xlsm`
2. 功能 2 不会修改原始文件,所有输出都在独立的 output 目录中
3. 如果文件读取失败,会在控制台显示警告信息,但不会中断整体处理流程
4. 建议在虚拟环境中运行脚本,避免依赖冲突

## 故障排除

### 错误: 未找到 pandas 或 openpyxl

确保已激活虚拟环境并安装了依赖:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 错误: 文件读取失败

可能原因:
- Excel 文件损坏
- 文件正在被其他程序打开
- 文件格式不支持

解决方法: 检查文件完整性,关闭可能占用文件的程序
