# 工业产品网站爬虫

## 功能说明
本脚本可以爬取 https://shwz888.gys.cn/supply/ 网站的产品信息，包括：
- 产品分类（9个主要分类）
- 产品名称
- 产品价格
- 产品图片（自动下载到本地）
- 产品详情链接

## 项目结构
```
tools/                                  # 根目录
├── venv/                              # Python虚拟环境（根目录）
├── requirements.txt                   # Python依赖包（根目录）
├── .gitignore                         # Git忽略文件（根目录）
└── product_scraper/                   # 爬虫项目文件夹
    ├── product_scraper.py             # 爬虫脚本（增强反爬版本）
    ├── config.json                    # 爬虫配置文件
    ├── run_scraper.sh                 # Linux/macOS运行脚本
    ├── run_scraper.bat                # Windows运行脚本
    ├── README.md                      # 使用说明
    ├── output/                        # 输出文件夹
    │   ├── products.xlsx              # Excel产品数据
    │   ├── images/                    # 产品图片
    │   └── debug_info.json            # 调试信息
    └── scraper.log                    # 运行日志
```

## 🚀 快速开始

### 自动运行（推荐）

**macOS/Linux:**
```bash
cd product_scraper
./run_scraper.sh
```

**Windows:**
```batch
cd product_scraper
run_scraper.bat
```

### 手动运行

1. **安装依赖**
```bash
# 在根目录安装依赖
cd tools
source venv/bin/activate    # macOS/Linux
# 或
venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

2. **运行脚本**
```bash
# 进入项目目录
cd product_scraper

# 运行爬虫
python product_scraper.py
```

## 🛡️ 强大的反反爬机制

### 核心特性
1. **智能延时系统**
   - 请求间延时：5-12秒随机
   - 分类间延时：15-30秒随机
   - 页面间延时：8-15秒随机
   - 随机长延时：30-90秒（30%概率触发）

2. **User-Agent轮换**
   - 9个真实浏览器User-Agent
   - 每次请求随机选择
   - 包含Chrome、Firefox、Safari、Edge

3. **人类行为模拟**
   - 随机鼠标移动停顿
   - 定期更新Referer头部
   - 模拟用户思考时间
   - 指数退避重试机制

4. **请求头优化**
   - 完整的浏览器请求头
   - Sec-Ch-Ua系列头部
   - 随机平台标识

5. **错误处理增强**
   - 8次重试机制
   - 服务器过载特殊处理（520/503错误）
   - 智能退避算法

## ⚙️ 配置说明

通过修改 `config.json` 调整反爬参数：

```json
{
  "scraper_settings": {
    "max_retries": 8,                    // 最大重试次数
    "timeout": 20,                       // 请求超时时间（秒）
    "delay_between_requests": [5, 12],   // 请求间延时范围（秒）
    "delay_between_categories": [15, 30], // 分类间延时范围（秒）
    "delay_between_pages": [8, 15],      // 页面间延时范围（秒）
    "random_sleep_probability": 0.3,     // 触发长延时概率
    "long_random_sleep_range": [30, 90], // 长延时范围（秒）
    "max_image_download_workers": 2,     // 图片下载并发数
    "image_download_timeout": 25         // 图片下载超时（秒）
  }
}
```

### 建议配置
- **保守模式**：增加延时范围，降低并发数
- **积极模式**：适当减少延时，但不建议低于默认值
- **服务器友好**：当前配置已经很友好，不建议调整更快

## 📊 输出结果

### 1. Excel文件 (`output/products.xlsx`)
包含多个工作表：
- **产品列表**：所有产品的汇总数据
- **各分类工作表**：按产品分类分别整理

### 2. 产品图片 (`output/images/`)
- 图片命名格式：`产品名称_哈希值.jpg`
- 自动验证图片完整性
- 支持多种图片格式（JPG, PNG, GIF, WebP）

### 3. 运行日志 (`scraper.log`)
详细记录：
- 延时策略执行情况
- 反爬机制触发记录
- 重试和错误恢复
- 性能统计信息

### 4. 调试信息 (`output/debug_info.json`)
包含：
- 总请求次数统计
- 使用的配置参数
- 图片下载成功率
- 分类爬取统计

## 🎯 爬取范围

### 产品分类（9个主要分类）
- 传感器 编码器 离合器
- 空调机柜 冷却装置  
- 互感器 控制器 隔离器
- 电磁阀 球阀 阀门 控制阀
- 电机 马达 泵 伺服驱动器
- 夹爪 气缸 油缸 齿轮箱 卡盘
- 开关 模块 电源 电容 电表
- 滤芯 电缆 插头 轴承
- 金属玻璃视镜 探头

### Excel文件结构
| 列名 | 说明 | 示例 |
|------|------|------|
| category | 产品分类 | "传感器 编码器 离合器" |
| name | 产品名称 | "德国FRAKO电容、FRAKO低压补偿电容器" |
| price | 产品价格 | "￥999.00" |
| url | 产品详情链接 | "https://shwz888.gys.cn/supply/4968752408.html" |
| image_url | 产品图片URL | "https://shwz888.gys.cn/images/product.jpg" |
| image_path | 本地图片路径 | "images/FRAKO电容_a1b2c3d4.jpg" |

## ⚠️ 重要提示

### 使用注意事项
1. **运行时间**：完整爬取需要2-4小时（因强大反爬机制）
2. **磁盘空间**：预留500MB-1GB空间存储图片
3. **网络稳定性**：建议在稳定网络环境下运行
4. **服务器友好**：已配置极其友好的延时策略
5. **法律合规**：请确保符合网站使用条款和法律法规

### 性能特点
- ✅ 极低的服务器压力（大量延时）
- ✅ 高成功率（强大重试机制）
- ✅ 人类行为模拟（难以检测）
- ✅ 配置化设计（灵活调整）
- ✅ 详细日志记录（便于调试）

### 常见问题处理
1. **520/503错误**：正常现象，脚本会自动处理
2. **运行缓慢**：这是设计特点，确保成功率
3. **部分分类失败**：服务器负载导致，可重新运行
4. **图片下载失败**：网络或链接问题，不影响产品数据

## 🔧 技术特色

- **智能配置系统**：JSON配置文件，灵活调整参数
- **多策略图片提取**：多种算法确保图片获取
- **并发控制**：合理的并发数避免服务器压力
- **错误恢复**：完善的异常处理和数据保护
- **日志系统**：详细记录运行过程和性能数据

这个版本的爬虫在保证成功率的同时，对目标服务器极其友好，是工业级的网站数据采集解决方案。