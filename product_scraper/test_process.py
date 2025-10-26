#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 process_output.py 脚本的功能
"""

import sys
from pathlib import Path

def test_imports():
    """测试导入"""
    print("测试导入...")
    try:
        from PIL import Image
        print("✓ PIL (Pillow) 导入成功")
    except ImportError:
        print("✗ PIL (Pillow) 导入失败 - 请运行: pip install Pillow")
        return False
    
    import re
    print("✓ re 模块导入成功")
    
    return True

def test_webp_files():
    """检查 WebP 文件"""
    print("\n检查 WebP 文件...")
    output_dir = Path(__file__).parent / 'output'
    
    if not output_dir.exists():
        print(f"✗ Output 目录不存在: {output_dir}")
        return False
    
    webp_files = list(output_dir.rglob('*.webp'))
    print(f"✓ 找到 {len(webp_files)} 个 WebP 文件")
    
    if webp_files:
        print(f"  示例: {webp_files[0].relative_to(output_dir)}")
    
    return True

def test_markdown_files():
    """检查 Markdown 文件"""
    print("\n检查产品详情文件...")
    output_dir = Path(__file__).parent / 'output'
    
    md_files = list(output_dir.rglob('产品详情.md'))
    print(f"✓ 找到 {len(md_files)} 个产品详情文件")
    
    if md_files:
        print(f"  示例: {md_files[0].relative_to(output_dir)}")
        
        # 检查是否包含需要替换的内容
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_contact = '张小姐' in content or '15021056285' in content
        if has_contact:
            print(f"  ✓ 文件包含需要替换的联系信息")
        else:
            print(f"  ℹ 文件不包含需要替换的联系信息（可能已经替换过）")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("process_output.py 功能测试")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_webp_files,
        test_markdown_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ 所有测试通过！可以运行 process_output.py")
    else:
        print("✗ 部分测试失败，请检查上述错误")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
