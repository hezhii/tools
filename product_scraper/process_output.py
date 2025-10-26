#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理 output 目录的脚本
功能：
1. 将 WebP 图片转换为 JPG 格式
2. 替换产品详情中的联系信息
"""

import os
import re
from pathlib import Path
from PIL import Image
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_output.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def convert_webp_to_jpg(webp_path: Path) -> bool:
    """将 WebP 图片转换为 JPG 格式
    
    Args:
        webp_path: WebP 图片路径
        
    Returns:
        是否转换成功
    """
    try:
        # 生成 JPG 文件路径（与 WebP 文件同名，仅扩展名不同）
        jpg_path = webp_path.with_suffix('.jpg')
        
        # 如果 JPG 文件已存在，跳过
        if jpg_path.exists():
            logger.debug(f"JPG 文件已存在，跳过: {jpg_path}")
            return True
        
        # 打开 WebP 图片
        with Image.open(webp_path) as img:
            # 如果图片有透明通道，转换为 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # 将图片粘贴到白色背景上
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存为 JPG
            img.save(jpg_path, 'JPEG', quality=95, optimize=True)
            
        logger.info(f"✓ 转换成功: {webp_path.name} -> {jpg_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ 转换失败 {webp_path}: {e}")
        return False


def process_images(output_dir: Path):
    """遍历 output 目录下的所有 WebP 图片并转换为 JPG
    
    Args:
        output_dir: output 目录路径
    """
    logger.info("开始处理图片转换...")
    
    # 查找所有 WebP 图片
    webp_files = list(output_dir.rglob('*.webp'))
    
    if not webp_files:
        logger.info("未找到 WebP 图片")
        return
    
    logger.info(f"找到 {len(webp_files)} 个 WebP 图片")
    
    success_count = 0
    for webp_file in webp_files:
        if convert_webp_to_jpg(webp_file):
            success_count += 1
    
    logger.info(f"图片转换完成: {success_count}/{len(webp_files)} 成功")


def replace_contact_info(content: str) -> tuple[str, int]:
    """替换产品详情中的联系信息
    
    Args:
        content: 文件内容
        
    Returns:
        (替换后的内容, 替换次数)
    """
    original_content = content
    replacements = 0
    
    # 替换规则（考虑中间可能有多个空白符）
    replacements_map = [
        # 联系人
        (r'联系人\s*:\s*张小姐', '联系人：孙女士'),
        # 手机
        (r'手机\s*:\s*15021056285', '手机：17616263858'),
        # QQ（处理多个数字的情况）
        (r'QQ\s*:\s*19625763603350634237', 'QQ：2474630730'),
        # Email
        (r'E-mail\s*:\s*salesmicroframe\.cn', 'E-mail：2474630730@qq.com'),
    ]
    
    for pattern, replacement in replacements_map:
        new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
        if count > 0:
            content = new_content
            replacements += count
            logger.debug(f"  替换 '{pattern}' -> '{replacement}': {count} 次")
    
    return content, replacements


def process_markdown_files(output_dir: Path):
    """遍历 output 目录下的所有产品详情.md 文件并替换联系信息
    
    Args:
        output_dir: output 目录路径
    """
    logger.info("开始处理产品详情文件...")
    
    # 查找所有 产品详情.md 文件
    md_files = list(output_dir.rglob('产品详情.md'))
    
    if not md_files:
        logger.info("未找到产品详情文件")
        return
    
    logger.info(f"找到 {len(md_files)} 个产品详情文件")
    
    processed_count = 0
    total_replacements = 0
    
    for md_file in md_files:
        try:
            # 读取文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换联系信息
            new_content, replacements = replace_contact_info(content)
            
            if replacements > 0:
                # 写回文件
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                processed_count += 1
                total_replacements += replacements
                logger.info(f"✓ 更新文件: {md_file.relative_to(output_dir)} ({replacements} 处替换)")
            else:
                logger.debug(f"  跳过文件（无需替换）: {md_file.relative_to(output_dir)}")
                
        except Exception as e:
            logger.error(f"✗ 处理文件失败 {md_file}: {e}")
    
    logger.info(f"产品详情处理完成: {processed_count} 个文件更新，共 {total_replacements} 处替换")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始处理 output 目录")
    logger.info("=" * 60)
    
    # 获取 output 目录路径
    output_dir = Path(__file__).parent / 'output'
    
    if not output_dir.exists():
        logger.error(f"Output 目录不存在: {output_dir}")
        return
    
    logger.info(f"Output 目录: {output_dir}")
    logger.info("")
    
    # 1. 处理图片转换
    process_images(output_dir)
    logger.info("")
    
    # 2. 处理产品详情
    process_markdown_files(output_dir)
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("处理完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
