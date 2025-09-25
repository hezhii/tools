#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工业产品网站爬虫脚本
爬取 https://shwz888.gys.cn/supply/ 上的产品信息
具备强大的反反爬机制
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from PIL import Image
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from urllib.parse import quote

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self, base_url: str = "https://shwz888.gys.cn", config_file: str = "config.json"):
        self.base_url = base_url
        self.supply_url = f"{base_url}/supply/"
        self.session = requests.Session()
        
        # 加载配置文件
        self.config = self.load_config(config_file)
        
        # 从配置获取参数
        self.max_retries = self.config['scraper_settings']['max_retries']
        self.timeout = self.config['scraper_settings']['timeout']
        self.delay_requests = self.config['scraper_settings']['delay_between_requests']
        self.delay_categories = self.config['scraper_settings']['delay_between_categories']
        self.delay_pages = self.config['scraper_settings']['delay_between_pages']
        self.max_workers = self.config['scraper_settings']['max_image_download_workers']
        self.img_timeout = self.config['scraper_settings']['image_download_timeout']
        self.img_delay = self.config['scraper_settings'].get('image_download_delay', [3, 8])
        self.random_sleep_prob = self.config['scraper_settings'].get('random_sleep_probability', 0.3)
        self.long_sleep_range = self.config['scraper_settings'].get('long_random_sleep_range', [30, 90])
        
        # 从配置获取User-Agent列表
        self.user_agents = self.config['user_agents']
        
        # 设置会话头部
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # 创建输出目录
        self.output_dir = Path("output")
        self.images_dir = self.output_dir / "images"
        self.output_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        
        self.products_data = []
        self.failed_categories = []
        self.request_count = 0
        
        logger.info(f"配置加载完成 - 延时范围: 请求间{self.delay_requests}s, 分类间{self.delay_categories}s")
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"配置文件 {config_file} 加载成功")
                return config
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_file} 未找到，使用默认配置")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"配置文件解析错误: {e}，使用默认配置")
            return self.get_default_config()
            
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "scraper_settings": {
                "max_retries": 6,
                "timeout": 18,
                "delay_between_requests": [2, 5],
                "delay_between_categories": [8, 15],
                "delay_between_pages": [3, 8],
                "max_image_download_workers": 1,
                "image_download_timeout": 25,
                "image_download_delay": [3, 8],
                "random_sleep_probability": 0.2,
                "long_random_sleep_range": [15, 45]
            },
            "user_agents": [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
            ],
            "output_settings": {
                "excel_filename": "products.xlsx",
                "images_folder": "images",
                "create_category_sheets": True,
                "save_debug_info": True
            }
        }
        
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.user_agents)
    
    def validate_image_url(self, img_url: str) -> Optional[str]:
        """验证图片URL是否有效，过滤掉占位符和无效链接"""
        if not img_url:
            return None
            
        # 过滤掉明显的占位符和无效图片
        invalid_patterns = [
            'loading',          # 加载动画
            'placeholder',      # 占位符
            'default',          # 默认图片
            'no-image',         # 无图片
            'noimage',          # 无图片
            'blank',            # 空白图片  
            'transparent',      # 透明图片
            '1x1',              # 1x1像素图片
            'spacer',           # 间隔符图片
            'circle-loading.svg', # 加载动画SVG
        ]
        
        # 检查URL是否包含无效模式
        url_lower = img_url.lower()
        for pattern in invalid_patterns:
            if pattern in url_lower:
                logger.debug(f"过滤掉无效图片URL: {img_url} (匹配模式: {pattern})")
                return None
        
        # 检查文件扩展名
        parsed_url = urlparse(img_url)
        ext = os.path.splitext(parsed_url.path)[1].lower()
        
        # SVG图片通常是图标或占位符，跳过
        if ext == '.svg':
            logger.debug(f"跳过SVG图片: {img_url}")
            return None
        
        # 检查图片尺寸参数（如果有）- 过滤掉过小的图片
        if any(size in url_lower for size in ['1x1', '10x10', '20x20']):
            logger.debug(f"跳过小尺寸图片: {img_url}")
            return None
            
        return img_url
        
    def smart_delay(self, delay_range: List[int], context: str = ""):
        """智能延时 - 模拟真实用户行为"""
        base_delay = random.uniform(delay_range[0], delay_range[1])
        
        # 随机概率触发更长延时，模拟用户思考时间
        if random.random() < self.random_sleep_prob:
            extra_delay = random.uniform(self.long_sleep_range[0], self.long_sleep_range[1])
            logger.info(f"触发随机长延时 {extra_delay:.1f}s - {context}")
            time.sleep(extra_delay)
            
        logger.debug(f"延时 {base_delay:.1f}s - {context}")
        time.sleep(base_delay)
        
    def simulate_human_behavior(self):
        """模拟人类行为特征"""
        # 模拟鼠标移动停顿
        if random.random() < 0.1:
            pause = random.uniform(0.5, 2.0)
            time.sleep(pause)
            
        # 每隔一段时间更新Referer
        if self.request_count % 10 == 0:
            self.session.headers.update({
                'Referer': f"{self.base_url}/"
            })
            
    def get_page(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """获取网页内容，增强反反爬机制"""
        if retries is None:
            retries = self.max_retries
            
        self.request_count += 1
        
        for attempt in range(retries):
            try:
                # 模拟人类行为
                self.simulate_human_behavior()
                
                # 每次请求使用不同的User-Agent
                self.session.headers.update({
                    'User-Agent': self.get_random_user_agent(),
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': f'"{random.choice(["macOS", "Windows", "Linux"])}"'
                })
                
                logger.info(f"正在获取: {url} (尝试 {attempt + 1}/{retries})")
                
                # 请求前随机延时
                if attempt > 0:
                    self.smart_delay([3, 8], f"重试前延时")
                else:
                    self.smart_delay(self.delay_requests, f"正常请求延时")
                
                response = self.session.get(url, timeout=self.timeout)
                
                # 检查响应状态
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                    logger.debug(f"页面获取成功: {len(response.content)} bytes")
                    return soup
                elif response.status_code in [503, 520, 521, 522, 524]:
                    logger.warning(f"服务器过载 {response.status_code}, 将增加延时重试")
                    # 服务器过载时增加更长延时
                    extra_wait = random.uniform(15, 45)
                    time.sleep(extra_wait)
                else:
                    response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    # 指数退避 + 随机抖动 + 额外延时
                    wait_time = (2 ** attempt) + random.uniform(5, 15)
                    logger.info(f"等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"无法获取页面: {url}")
                    return None
    
    def get_categories(self) -> List[Dict[str, str]]:
        """获取产品分类列表"""
        logger.info("正在获取产品分类...")
        soup = self.get_page(self.supply_url)
        
        if not soup:
            logger.error("无法获取主页面，退出程序")
            return []
        
        categories = []
        
        # 查找产品分类链接
        category_links = soup.find_all('a', href=re.compile(r'/supply/g\d+_1\.html'))
        
        for link in category_links:
            category_name = link.get_text().strip()
            category_url = urljoin(self.base_url, link.get('href'))
            
            if category_name and '(' in category_name:  # 过滤掉包含数量的分类名
                # 提取分类名称（去掉数量部分）
                clean_name = re.sub(r'\s*\(\d+\)$', '', category_name).strip()
                categories.append({
                    'name': clean_name,
                    'url': category_url
                })
                logger.info(f"发现分类: {clean_name}")
        
        logger.info(f"共找到 {len(categories)} 个产品分类")
        return categories
    
    def get_total_pages(self, category_url: str) -> int:
        """获取某个分类的总页数"""
        soup = self.get_page(category_url)
        if not soup:
            return 1
        
        # 查找分页信息
        page_info = soup.find(string=re.compile(r'共\d+页'))
        if page_info:
            match = re.search(r'共(\d+)页', page_info)
            if match:
                return int(match.group(1))
        
        # 备选方法：查找分页链接
        page_links = soup.find_all('a', href=re.compile(r'/supply/g\d+_\d+\.html'))
        if page_links:
            page_numbers = []
            for link in page_links:
                match = re.search(r'g\d+_(\d+)\.html', link.get('href'))
                if match:
                    page_numbers.append(int(match.group(1)))
            if page_numbers:
                return max(page_numbers)
        
        return 1
    
    def extract_products_from_page(self, soup: BeautifulSoup, category_name: str) -> List[Dict]:
        """从页面中提取产品信息"""
        products = []
        product_links = soup.find_all('a', href=re.compile(r'/supply/\d+\.html'))
        found_products = set()
        for link in product_links:
            try:
                product_name = link.get_text().strip()
                product_url = urljoin(self.base_url, link.get('href'))
                if not product_name or len(product_name) < 5 or product_url in found_products:
                    continue
                found_products.add(product_url)
                img_url = None
                
                # 策略1: 查找a标签下的img（直接子节点）
                img = link.find('img')
                if img:
                    for attr in ['src', 'data-original', 'data-src', 'data-lazy']:
                        if img.get(attr):
                            img_url = urljoin(self.base_url, img.get(attr))
                            logger.debug(f"策略1找到图片: {img_url} (属性: {attr})")
                            break
                
                # 策略2: 针对dl/dt/dd结构 - 查找同级dt中的图片
                if not img_url:
                    # 检查是否在dd标签内
                    dd_parent = link.find_parent('dd')
                    if dd_parent:
                        # 找到包含dd的dl标签
                        dl_parent = dd_parent.find_parent('dl')
                        if dl_parent:
                            # 在dl中查找dt->a->img结构
                            dt_tags = dl_parent.find_all('dt')
                            for dt in dt_tags:
                                dt_link = dt.find('a')
                                if dt_link:
                                    img = dt_link.find('img')
                                    if img:
                                        for attr in ['data-original', 'src', 'data-src', 'data-lazy']:
                                            if img.get(attr):
                                                img_url = urljoin(self.base_url, img.get(attr))
                                                logger.debug(f"策略2(dl/dt结构)找到图片: {img_url} (属性: {attr})")
                                                break
                                        if img_url:
                                            break
                
                # 策略3: 查找a标签的父级容器内的img（原策略2增强版）
                if not img_url:
                    parent = link
                    for level in range(4):  # 增加搜索层级
                        parent = parent.find_parent() if parent else None
                        if not parent:
                            break
                        
                        # 在当前父级中查找所有img标签
                        imgs = parent.find_all('img', limit=3)  # 限制数量避免找到不相关图片
                        for img in imgs:
                            for attr in ['src', 'data-original', 'data-src', 'data-lazy']:
                                if img.get(attr):
                                    img_url = urljoin(self.base_url, img.get(attr))
                                    logger.debug(f"策略3找到图片(父级{level+1}层): {img_url} (属性: {attr})")
                                    break
                            if img_url:
                                break
                        if img_url:
                            break
                
                # 策略4: 查找a标签的兄弟节点中的img
                if not img_url:
                    # 查找前面的兄弟节点
                    prev_siblings = link.find_previous_siblings(['img', 'div', 'span', 'figure', 'dt'], limit=5)
                    for sibling in prev_siblings:
                        img = sibling.find('img') if sibling.name != 'img' else sibling
                        if img:
                            for attr in ['src', 'data-original', 'data-src', 'data-lazy']:
                                if img.get(attr):
                                    img_url = urljoin(self.base_url, img.get(attr))
                                    logger.debug(f"策略4(前兄弟节点)找到图片: {img_url} (属性: {attr})")
                                    break
                            if img_url:
                                break
                    
                    # 查找后面的兄弟节点
                    if not img_url:
                        next_siblings = link.find_next_siblings(['img', 'div', 'span', 'figure'], limit=3)
                        for sibling in next_siblings:
                            img = sibling.find('img') if sibling.name != 'img' else sibling
                            if img:
                                for attr in ['src', 'data-original', 'data-src', 'data-lazy']:
                                    if img.get(attr):
                                        img_url = urljoin(self.base_url, img.get(attr))
                                        logger.debug(f"策略4(后兄弟节点)找到图片: {img_url} (属性: {attr})")
                                        break
                                if img_url:
                                    break
                
                # 策略5: 查找style属性中的背景图片
                if not img_url:
                    parent = link
                    for level in range(3):
                        parent = parent.find_parent() if parent else None
                        if not parent:
                            break
                        style = parent.get('style')
                        if style:
                            m = re.search(r'url\(["\']?(.*?\.(?:jpg|jpeg|png|gif|webp))["\']?\)', style, re.I)
                            if m:
                                img_url = urljoin(self.base_url, m.group(1))
                                logger.debug(f"策略5找到背景图片: {img_url}")
                                break
                
                # 打印最终提取到的图片地址
                if img_url:
                    logger.info(f"产品: {product_name[:30]}... -> 图片: {img_url}")
                else:
                    logger.debug(f"产品: {product_name[:30]}... -> 未找到图片")
                
                # 验证图片URL有效性
                img_url = self.validate_image_url(img_url) if img_url else ""
                # 查找价格信息
                price = None
                price_pattern = re.compile(r'￥[\d,]+\.?\d*')
                price_container = link.find_parent()
                for _ in range(3):
                    if price_container:
                        price_text = price_container.find(string=price_pattern)
                        if price_text:
                            price_match = price_pattern.search(price_text)
                            if price_match:
                                price = price_match.group()
                                break
                        price_container = price_container.find_parent()
                    else:
                        break
                product_info = {
                    'category': category_name,
                    'name': product_name,
                    'url': product_url,
                    'image_url': img_url if img_url else "",
                    'price': price,
                    'image_path': None
                }
                products.append(product_info)
            except Exception as e:
                logger.warning(f"提取产品信息时出错: {e}")
                continue
        return products
    
    def download_image(self, image_url: str, product_name: str, max_retries: int = 3) -> Optional[str]:
        """下载产品图片"""
        if not image_url:
            return None
            
        for attempt in range(max_retries):
            try:
                # 使用随机User-Agent和延时
                headers = {'User-Agent': self.get_random_user_agent()}
                
                # 图片下载前延时，避免触发反爬
                delay = random.uniform(self.img_delay[0], self.img_delay[1])
                logger.debug(f"图片下载延时 {delay:.1f}s")
                time.sleep(delay)
                
                response = self.session.get(image_url, headers=headers, timeout=self.img_timeout)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('content-type', '').lower()
                if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'jpg', 'png', 'gif', 'webp']):
                    logger.warning(f"非图片内容类型: {content_type}")
                    return None
                
                # 检查响应内容是否为HTML（可能是验证页面）
                response_text = response.text[:500].lower()  # 只检查前500字符
                if any(html_indicator in response_text for html_indicator in ['<html', '<title', '验证', 'captcha', 'verify', '滑块']):
                    logger.warning(f"检测到可能的验证页面，停止图片下载: {image_url}")
                    raise Exception("遇到验证页面，停止下载")
                
                # 检查文件大小（太小可能是占位符）
                if len(response.content) < 1024:  # 小于1KB的图片可能是占位符
                    logger.warning(f"图片文件太小，跳过: {len(response.content)} bytes")
                    return None
                
                # 生成安全的文件名
                url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
                safe_name = re.sub(r'[^\w\s-]', '', product_name)[:50].strip()
                
                # 获取文件扩展名
                parsed_url = urlparse(image_url)
                ext = os.path.splitext(parsed_url.path)[1].lower()
                if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    ext = '.jpg'
                
                filename = f"{safe_name}_{url_hash}{ext}"
                filepath = self.images_dir / filename
                
                # 保存图片
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # 验证图片文件
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        # 检查图片尺寸，过滤掉太小的图片
                        if width < 50 or height < 50:
                            logger.warning(f"图片尺寸太小，删除: {width}x{height}")
                            filepath.unlink(missing_ok=True)
                            return None
                        
                        img.verify()  # 验证图片完整性
                    
                    logger.info(f"图片已下载: {filename} ({width}x{height})")
                    return str(filepath.relative_to(self.output_dir))
                    
                except Exception as img_error:
                    logger.warning(f"图片文件损坏，删除: {filename} - {img_error}")
                    filepath.unlink(missing_ok=True)
                    return None
                
            except Exception as e:
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['验证', 'captcha', 'verify', '滑块']):
                    logger.error(f"遇到验证机制，停止图片下载: {e}")
                    raise  # 重新抛出异常，停止所有图片下载
                    
                logger.warning(f"下载图片失败 (尝试 {attempt + 1}/{max_retries}) {image_url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))  # 失败后更长的等待时间
                
        return None
    
    def scrape_category(self, category: Dict[str, str]) -> List[Dict]:
        """爬取某个分类的所有产品"""
        category_name = category['name']
        category_url = category['url']
        
        logger.info(f"正在爬取分类: {category_name}")
        
        # 获取总页数
        total_pages = self.get_total_pages(category_url)
        logger.info(f"分类 {category_name} 共有 {total_pages} 页")
        
        category_products = []
        
        for page in range(1, total_pages + 1):
            try:
                # 构造分页URL
                if page == 1:
                    page_url = category_url
                else:
                    page_url = re.sub(r'_1\.html$', f'_{page}.html', category_url)
                
                logger.info(f"正在爬取第 {page} 页...")
                soup = self.get_page(page_url)
                
                if not soup:
                    logger.error(f"无法获取第 {page} 页内容")
                    continue
                
                # 提取产品信息
                products = self.extract_products_from_page(soup, category_name)
                category_products.extend(products)
                
                logger.info(f"第 {page} 页找到 {len(products)} 个产品")
                
                # 页面间延时
                if page < total_pages:
                    self.smart_delay(self.delay_pages, f"页面间延时")
                
            except Exception as e:
                logger.error(f"爬取第 {page} 页时出错: {e}")
                continue
        
        logger.info(f"分类 {category_name} 共找到 {len(category_products)} 个产品")
        return category_products
    
    def scrape_all(self):
        """爬取所有产品"""
        logger.info("开始爬取所有产品...")
        
        # 获取分类列表
        categories = self.get_categories()
        
        if not categories:
            logger.error("未找到任何产品分类")
            return
        
        # 爬取每个分类
        for i, category in enumerate(categories, 1):
            try:
                logger.info(f"正在处理分类 {i}/{len(categories)}: {category['name']}")
                products = self.scrape_category(category)
                
                if products:
                    self.products_data.extend(products)
                    logger.info(f"成功获取 {len(products)} 个产品")
                else:
                    logger.warning(f"分类 {category['name']} 未获取到产品")
                    self.failed_categories.append(category)
                
                # 分类间延时
                if i < len(categories):
                    self.smart_delay(self.delay_categories, f"分类间延时")
                
            except Exception as e:
                logger.error(f"处理分类 {category['name']} 时出错: {e}")
                self.failed_categories.append(category)
                continue
        
        logger.info(f"爬取完成，共获取 {len(self.products_data)} 个产品")
        if self.failed_categories:
            logger.warning(f"失败的分类: {[cat['name'] for cat in self.failed_categories]}")
    
    def download_images_parallel(self, max_workers: int = None):
        """并行下载产品图片，带验证码检测"""
        if max_workers is None:
            max_workers = self.max_workers
            
        logger.info("开始下载产品图片...")
        logger.info(f"图片下载策略: 单线程下载，延时{self.img_delay[0]}-{self.img_delay[1]}秒，避免触发反爬")
        
        products_with_images = [p for p in self.products_data if p.get('image_url')]
        if not products_with_images:
            logger.warning("没有找到任何图片链接")
            return
        
        success_count = 0
        verification_triggered = False
        
        # 使用线程池并行下载（实际只用1个线程）
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交下载任务
            future_to_product = {}
            for i, product in enumerate(products_with_images):
                future = executor.submit(self.download_image, product['image_url'], product['name'])
                future_to_product[future] = (i, product)
            
            # 处理完成的任务
            for future in as_completed(future_to_product):
                i, product = future_to_product[future]
                try:
                    image_path = future.result()
                    product['image_path'] = image_path
                    if image_path:
                        success_count += 1
                        logger.info(f"进度: {i+1}/{len(products_with_images)} - 成功: {success_count}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ['验证', 'captcha', 'verify', '滑块']):
                        logger.error(f"检测到验证机制，停止所有图片下载")
                        verification_triggered = True
                        # 取消所有未完成的任务
                        for remaining_future in future_to_product:
                            remaining_future.cancel()
                        break
                    else:
                        logger.error(f"下载图片时出错: {e}")
        
        if verification_triggered:
            logger.warning("由于触发验证机制，图片下载已提前停止")
            logger.warning("建议：等待一段时间后重新运行，或手动完成验证后继续")
        
        logger.info(f"图片下载完成: {success_count}/{len(products_with_images)} 成功")
        
        if success_count == 0 and len(products_with_images) > 0:
            logger.warning("没有成功下载任何图片，可能触发了反爬机制")
            logger.warning("建议检查网络连接或降低爬取频率")
    
    def save_to_excel(self, filename: str = None):
        """保存数据到Excel文件"""
        if not self.products_data:
            logger.warning("没有数据可保存")
            return
        
        if filename is None:
            filename = self.config['output_settings']['excel_filename']
            
        filepath = self.output_dir / filename
        
        # 创建DataFrame
        df = pd.DataFrame(self.products_data)
        # 保证image_url列存在且为字符串
        if 'image_url' not in df.columns:
            df['image_url'] = ""
        df['image_url'] = df['image_url'].astype(str)
        # 重新排序列，image_url放在image_path前
        columns = ['category', 'name', 'price', 'url', 'image_url', 'image_path']
        df = df[[col for col in columns if col in df.columns]]
        
        # 保存到Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='产品列表', index=False)
            
            # 按分类创建工作表
            if self.config['output_settings']['create_category_sheets']:
                for category in df['category'].unique():
                    category_df = df[df['category'] == category]
                    # Excel工作表名限制：最长31字符，不能包含特殊字符
                    safe_sheet_name = re.sub(r'[\\/*?:\[\]]', '', category)[:31]
                    try:
                        category_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    except Exception as e:
                        logger.warning(f"无法创建工作表 '{safe_sheet_name}': {e}")
        
        logger.info(f"数据已保存到: {filepath}")
        
        # 打印统计信息
        logger.info(f"总产品数: {len(df)}")
        logger.info("分类统计:")
        for category, count in df['category'].value_counts().items():
            logger.info(f"  {category}: {count} 个产品")
        
        # 图片下载统计
        has_images = df['image_path'].notna().sum()
        logger.info(f"成功下载图片: {has_images}/{len(df)} 个产品")
    
    def save_debug_info(self):
        """保存调试信息"""
        if not self.config['output_settings']['save_debug_info']:
            return
            
        debug_info = {
            'total_products': len(self.products_data),
            'failed_categories': [cat['name'] for cat in self.failed_categories],
            'categories_stats': {},
            'image_stats': {
                'total_products': len(self.products_data),
                'with_image_url': sum(1 for p in self.products_data if p.get('image_url')),
                'with_image_file': sum(1 for p in self.products_data if p.get('image_path')),
            },
            'scraper_stats': {
                'total_requests': self.request_count,
                'config_used': self.config
            }
        }
        
        # 按分类统计
        for product in self.products_data:
            category = product['category']
            if category not in debug_info['categories_stats']:
                debug_info['categories_stats'][category] = 0
            debug_info['categories_stats'][category] += 1
        
        debug_file = self.output_dir / 'debug_info.json'
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"调试信息已保存到: {debug_file}")

def main():
    """主函数"""
    try:
        scraper = ProductScraper()
        
        # 爬取所有产品数据
        scraper.scrape_all()
        
        if scraper.products_data:
            # 并行下载图片
            scraper.download_images_parallel()
            
            # 保存到Excel
            scraper.save_to_excel()
            
            # 保存调试信息
            scraper.save_debug_info()
            
            print(f"\n=== 爬取完成 ===")
            print(f"共获取 {len(scraper.products_data)} 个产品")
            print(f"数据保存在: {scraper.output_dir / scraper.config['output_settings']['excel_filename']}")
            print(f"图片保存在: {scraper.images_dir}")
            if scraper.failed_categories:
                print(f"失败的分类: {[cat['name'] for cat in scraper.failed_categories]}")
        else:
            print("未获取到任何产品数据")
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        raise

if __name__ == "__main__":
    main()