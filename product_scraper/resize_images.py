#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片尺寸调整脚本
功能：
1. 遍历 output 目录下的所有 JPG 图片
2. 将小于 750x750 的图片等比放大到 750x750 以上
3. 保持高质量输出
4. 处理后的图片添加 'big_' 前缀
"""

import os
from pathlib import Path
from PIL import Image
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resize_images.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 目标最小尺寸
TARGET_MIN_SIZE = 750


def calculate_new_size(width: int, height: int, min_size: int = TARGET_MIN_SIZE) -> tuple:
    """计算新的图片尺寸（等比放大到最小边 >= min_size）
    
    Args:
        width: 原图宽度
        height: 原图高度
        min_size: 目标最小尺寸
        
    Returns:
        (new_width, new_height) 新的宽高
    """
    # 如果已经满足尺寸要求，返回原尺寸
    if width >= min_size and height >= min_size:
        return width, height
    
    # 计算缩放比例（以最小边为准）
    min_dimension = min(width, height)
    scale_ratio = min_size / min_dimension
    
    # 计算新尺寸
    new_width = int(width * scale_ratio)
    new_height = int(height * scale_ratio)
    
    return new_width, new_height


def resize_image(image_path: Path, min_size: int = TARGET_MIN_SIZE) -> bool:
    """调整图片尺寸
    
    Args:
        image_path: 图片路径
        min_size: 目标最小尺寸
        
    Returns:
        是否成功处理
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            width, height = img.size
            
            # 检查是否需要调整
            if width >= min_size and height >= min_size:
                logger.debug(f"跳过（尺寸已满足）: {image_path.name} ({width}x{height})")
                return False
            
            # 计算新尺寸
            new_width, new_height = calculate_new_size(width, height, min_size)
            
            # 生成新文件名（添加 big_ 前缀）
            new_filename = f"big_{image_path.name}"
            new_path = image_path.parent / new_filename
            
            # 如果目标文件已存在，跳过
            if new_path.exists():
                logger.debug(f"跳过（目标文件已存在）: {new_filename}")
                return False
            
            # 使用高质量重采样算法放大图片
            # LANCZOS (ANTIALIAS) 是最高质量的重采样滤镜
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存图片，使用高质量参数
            if img.mode in ('RGBA', 'LA', 'P'):
                # 处理带透明通道的图片
                background = Image.new('RGB', resized_img.size, (255, 255, 255))
                if resized_img.mode == 'P':
                    resized_img = resized_img.convert('RGBA')
                background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                resized_img = background
            elif img.mode != 'RGB':
                resized_img = resized_img.convert('RGB')
            
            # 保存为 JPG，质量设置为 95，使用优化
            resized_img.save(new_path, 'JPEG', quality=95, optimize=True, subsampling=0)
            
            logger.info(f"✓ 调整成功: {image_path.name} ({width}x{height}) -> {new_filename} ({new_width}x{new_height})")
            return True
            
    except Exception as e:
        logger.error(f"✗ 处理失败 {image_path}: {e}")
        return False


def process_images(output_dir: Path, min_size: int = TARGET_MIN_SIZE):
    """遍历 output 目录下的所有 JPG 图片并调整尺寸
    
    Args:
        output_dir: output 目录路径
        min_size: 目标最小尺寸
    """
    logger.info(f"开始处理图片调整（目标最小尺寸: {min_size}x{min_size}）...")
    
    # 查找所有 JPG 图片（包括 .jpg 和 .jpeg）
    jpg_files = []
    jpg_files.extend(output_dir.rglob('*.jpg'))
    jpg_files.extend(output_dir.rglob('*.jpeg'))
    jpg_files.extend(output_dir.rglob('*.JPG'))
    jpg_files.extend(output_dir.rglob('*.JPEG'))
    
    # 过滤掉已经有 big_ 前缀的文件
    jpg_files = [f for f in jpg_files if not f.name.startswith('big_')]
    
    if not jpg_files:
        logger.info("未找到需要处理的 JPG 图片")
        return
    
    logger.info(f"找到 {len(jpg_files)} 个 JPG 图片")
    
    success_count = 0
    skipped_count = 0
    
    for jpg_file in jpg_files:
        result = resize_image(jpg_file, min_size)
        if result:
            success_count += 1
        else:
            skipped_count += 1
    
    logger.info(f"\n图片调整完成:")
    logger.info(f"  总计: {len(jpg_files)} 个图片")
    logger.info(f"  成功调整: {success_count} 个")
    logger.info(f"  跳过: {skipped_count} 个（已满足尺寸要求或已处理）")


def show_statistics(output_dir: Path):
    """显示图片尺寸统计信息
    
    Args:
        output_dir: output 目录路径
    """
    logger.info("\n正在统计图片尺寸信息...")
    
    # 查找所有 JPG 图片
    jpg_files = []
    jpg_files.extend(output_dir.rglob('*.jpg'))
    jpg_files.extend(output_dir.rglob('*.jpeg'))
    jpg_files.extend(output_dir.rglob('*.JPG'))
    jpg_files.extend(output_dir.rglob('*.JPEG'))
    
    if not jpg_files:
        logger.info("未找到 JPG 图片")
        return
    
    size_ranges = {
        'small': 0,      # < 750x750
        'medium': 0,     # 750x750 ~ 1500x1500
        'large': 0,      # > 1500x1500
    }
    
    big_prefix_count = 0
    
    for jpg_file in jpg_files:
        try:
            with Image.open(jpg_file) as img:
                width, height = img.size
                min_dimension = min(width, height)
                
                if jpg_file.name.startswith('big_'):
                    big_prefix_count += 1
                
                if min_dimension < 750:
                    size_ranges['small'] += 1
                elif min_dimension < 1500:
                    size_ranges['medium'] += 1
                else:
                    size_ranges['large'] += 1
        except Exception as e:
            logger.debug(f"无法读取图片尺寸 {jpg_file}: {e}")
    
    logger.info(f"\n图片尺寸统计（共 {len(jpg_files)} 个图片）:")
    logger.info(f"  小于 750x750: {size_ranges['small']} 个")
    logger.info(f"  750x750 ~ 1500x1500: {size_ranges['medium']} 个")
    logger.info(f"  大于 1500x1500: {size_ranges['large']} 个")
    logger.info(f"  带 big_ 前缀: {big_prefix_count} 个")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("图片尺寸调整工具")
    logger.info("=" * 60)
    logger.info(f"目标尺寸: {TARGET_MIN_SIZE}x{TARGET_MIN_SIZE} (最小边)")
    logger.info("")
    
    # 获取 output 目录路径
    output_dir = Path(__file__).parent / 'output'
    
    if not output_dir.exists():
        logger.error(f"Output 目录不存在: {output_dir}")
        return
    
    logger.info(f"Output 目录: {output_dir}")
    logger.info("")
    
    # 显示处理前的统计信息
    show_statistics(output_dir)
    logger.info("")
    
    # 处理图片
    process_images(output_dir, TARGET_MIN_SIZE)
    logger.info("")
    
    # 显示处理后的统计信息
    show_statistics(output_dir)
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("处理完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
