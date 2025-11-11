#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 处理工具
功能1: 检测 Excel 文件中未被系统识别的列名
功能2: 精简 Excel 文件，仅保留列头和最多5条数据
"""

import os
import sys
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# 系统识别的列名数组
SYSTEM_COLUMNS = [
    "标题",
    "申请人",
    "公开(公告)号",
    "摘要",
    "公开(公告)日",
    "申请号",
    "申请日",
    "专利类型",
    "公开国别",
    "链接到incoPat",
    "IPC主分类",
    "IPC",
    "国民经济分类",
    "文献种类代码",
    "小类代码",
    "申请人贡献分",
    "标题(翻译)",
    "标题(小语种原文)",
    "摘要(小语种原文)",
    "摘要(翻译)",
    "标准化当前权利人",
    "当前权利人",
    "代理机构",
    "代理人",
    "审查员",
    "优先权信息",
    "优先权号",
    "优先权日",
    "最早优先权日",
    "优先权国别",
    "PCT国际申请号",
    "PCT国际公布号",
    "PCT进入国家阶段日",
    "首次公开日",
    "授权公告日",
    "实质审查生效日",
    "提出实审时长",
    "审查时长",
    "失效日",
    "专利寿命(月)",
    "标准类型",
    "标准项目",
    "标准号",
    "合享价值度",
    "技术稳定性",
    "技术先进性",
    "保护范围",
    "首项权利要求",
    "独立权利要求",
    "权利要求数量",
    "独立权利要求数量",
    "从属权利要求数量",
    "文献页数",
    "首权字数",
    "技术功效短语",
    "技术功效句",
    "技术功效1级",
    "技术功效2级",
    "技术功效3级",
    "技术功效TRIZ参数",
    "洛迦诺分类号",
    "EC",
    "CPC",
    "UC",
    "FI",
    "F-term",
    "新兴产业分类",
    "申请人(翻译)",
    "申请人(其他)",
    "标准化申请人",
    "第一申请人",
    "申请人数量",
    "申请人类型",
    "申请人国别代码",
    "申请人地址",
    "申请人地址(其他)",
    "申请人省市代码",
    "中国申请人地市",
    "中国申请人区县",
    "工商别名",
    "工商英文名",
    "工商注册地址",
    "工商公司类型",
    "工商成立日期",
    "工商统一社会信用代码",
    "工商注册号",
    "工商上市代码",
    "工商企业状态",
    "发明人",
    "发明(设计)人(其他)",
    "第一发明人",
    "当前发明人名称",
    "发明人数量",
    "发明人国别",
    "发明人地址",
    "发明(设计)人地址(其他)",
    "引证专利",
    "被引证专利",
    "家族引证",
    "家族被引证",
    "引证申请人",
    "被引证申请人",
    "家族引证申请人",
    "家族被引证申请人",
    "引证次数",
    "被引证次数",
    "家族引证次数",
    "家族被引证次数",
    "引证科技文献",
    "被引证国别(forward)",
    "引证类别",
    "简单同族",
    "扩展同族",
    "DocDB同族",
    "简单同族ID",
    "扩展同族ID",
    "DocDB同族ID",
    "简单同族个数",
    "扩展同族个数",
    "DocDB同族个数",
    "同族国家/地区",
    "母案",
    "分案",
    "一案双申",
    "专利有效性",
    "当前法律状态",
    "法律文书日期",
    "法律状态",
    "法律文书编号",
    "复审请求人",
    "无效请求人",
    "复审决定",
    "复审无效决定日",
    "复审无效法律依据",
    "转让次数",
    "转让执行日",
    "转让人",
    "受让人",
    "标准受让人",
    "许可次数",
    "许可合同备案日期",
    "许可人",
    "被许可人",
    "当前被许可人",
    "许可类型",
    "质押次数",
    "质押期限",
    "出质人",
    "质权人",
    "当前质权人",
    "诉讼次数",
    "原告",
    "被告",
    "诉讼类型",
    "法庭",
    "海关备案",
    "复审决定日",
    "无效决定日",
    "口审日期",
    "法律事件",
    "复审请求日",
    "小类名称",
    "中类代码",
    "中类名称",
    "大类代码",
    "大类名称"
]


def find_excel_files(directory):
    """递归查找所有 Excel 文件"""
    excel_files = []
    directory = Path(directory)
    
    # 支持的 Excel 文件扩展名
    excel_extensions = ['.xlsx', '.xls', '.xlsm']
    
    for ext in excel_extensions:
        excel_files.extend(directory.rglob(f'*{ext}'))
    
    return excel_files


def read_excel_headers(file_path):
    """读取 Excel 文件的第一行(列头)"""
    try:
        # 尝试使用 pandas 读取第一行
        df = pd.read_excel(file_path, nrows=0)
        return list(df.columns)
    except Exception as e:
        print(f"  ⚠️ 读取文件失败: {file_path}")
        print(f"     错误: {str(e)}")
        return []


def check_unrecognized_columns(input_directory):
    """
    功能1: 检测未被系统识别的列名
    """
    print("\n" + "="*80)
    print("功能1: 检测未被系统识别的列名")
    print("="*80)
    
    input_path = Path(input_directory)
    if not input_path.exists():
        print(f"❌ 错误: 目录不存在 - {input_directory}")
        return
    
    # 查找所有 Excel 文件
    excel_files = find_excel_files(input_directory)
    
    if not excel_files:
        print(f"❌ 未找到任何 Excel 文件在目录: {input_directory}")
        return
    
    print(f"\n✓ 找到 {len(excel_files)} 个 Excel 文件\n")
    
    # 收集所有未识别的列名
    unrecognized_columns_all = set()
    
    # 遍历每个文件
    for idx, file_path in enumerate(excel_files, 1):
        print(f"[{idx}/{len(excel_files)}] 处理: {file_path.relative_to(input_path)}")
        
        headers = read_excel_headers(file_path)
        if not headers:
            continue
        
        # 找出未被识别的列名
        unrecognized = set(headers) - set(SYSTEM_COLUMNS)
        
        if unrecognized:
            print(f"  → 发现 {len(unrecognized)} 个未识别列名: {', '.join(sorted(unrecognized))}")
            unrecognized_columns_all.update(unrecognized)
        else:
            print(f"  → 所有列名均已识别")
    
    # 输出汇总结果
    print("\n" + "="*80)
    print("汇总结果")
    print("="*80)
    
    if unrecognized_columns_all:
        print(f"\n共发现 {len(unrecognized_columns_all)} 个未被系统识别的列名:\n")
        for col in sorted(unrecognized_columns_all):
            print(f"  • {col}")
    else:
        print("\n✓ 所有文件的列名均已被系统识别")
    
    print("\n" + "="*80 + "\n")


def simplify_excel_files(input_directory, max_rows=5):
    """
    功能2: 精简 Excel 文件，仅保留列头和最多指定条数的数据
    """
    print("\n" + "="*80)
    print(f"功能2: 精简 Excel 文件 (保留列头 + 最多 {max_rows} 条数据)")
    print("="*80)
    
    input_path = Path(input_directory)
    if not input_path.exists():
        print(f"❌ 错误: 目录不存在 - {input_directory}")
        return
    
    # 创建输出目录
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 查找所有 Excel 文件
    excel_files = find_excel_files(input_directory)
    
    if not excel_files:
        print(f"❌ 未找到任何 Excel 文件在目录: {input_directory}")
        return
    
    print(f"\n✓ 找到 {len(excel_files)} 个 Excel 文件")
    print(f"✓ 输出目录: {output_dir}\n")
    
    success_count = 0
    error_count = 0
    
    # 遍历每个文件
    for idx, file_path in enumerate(excel_files, 1):
        relative_path = file_path.relative_to(input_path)
        print(f"[{idx}/{len(excel_files)}] 处理: {relative_path}")
        
        try:
            # 读取 Excel 文件，只读取前 max_rows 行数据
            df = pd.read_excel(file_path, nrows=max_rows)
            
            # 构建输出文件路径(保持相对目录结构)
            output_file = output_dir / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入精简后的数据
            df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"  ✓ 成功: 保留了 {len(df)} 条数据 → {output_file.relative_to(script_dir)}")
            success_count += 1
            
        except Exception as e:
            print(f"  ⚠️ 失败: {str(e)}")
            error_count += 1
    
    # 输出统计结果
    print("\n" + "="*80)
    print("处理结果统计")
    print("="*80)
    print(f"\n成功: {success_count} 个文件")
    print(f"失败: {error_count} 个文件")
    print(f"总计: {len(excel_files)} 个文件")
    print(f"\n输出目录: {output_dir}")
    print("\n" + "="*80 + "\n")


def main():
    """主函数"""
    print("\n" + "="*80)
    print(" Excel 处理工具")
    print("="*80)
    
    # 获取命令行参数
    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python process_excel.py <功能编号> <输入目录> [最大行数]")
        print("\n功能编号:")
        print("  1 - 检测未被系统识别的列名")
        print("  2 - 精简 Excel 文件(保留列头和最多5条数据)")
        print("  all - 执行所有功能")
        print("\n示例:")
        print("  python process_excel.py 1 /path/to/excel/folder")
        print("  python process_excel.py 2 /path/to/excel/folder")
        print("  python process_excel.py 2 /path/to/excel/folder 10")
        print("  python process_excel.py all /path/to/excel/folder")
        sys.exit(1)
    
    function_num = sys.argv[1]
    input_directory = sys.argv[2]
    max_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # 执行对应功能
    if function_num == '1':
        check_unrecognized_columns(input_directory)
    elif function_num == '2':
        simplify_excel_files(input_directory, max_rows)
    elif function_num.lower() == 'all':
        check_unrecognized_columns(input_directory)
        simplify_excel_files(input_directory, max_rows)
    else:
        print(f"\n❌ 错误: 无效的功能编号 '{function_num}'")
        print("   有效的功能编号: 1, 2, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
