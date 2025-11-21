use calamine::{open_workbook, Reader, Xlsx, Xls, Data};
use clap::{Parser, Subcommand};
use colored::*;
use rust_xlsxwriter::Workbook;
use std::collections::{HashSet, HashMap};
use std::path::{Path, PathBuf};
use std::fs;
use walkdir::WalkDir;

/// Excel 工具集 - 列名检查、格式转换等功能
#[derive(Parser, Debug)]
#[command(name = "excel_tools")]
#[command(author = "Your Name")]
#[command(version = "1.0")]
#[command(about = "Excel 工具集：检测列名、转换格式", long_about = None)]
struct Args {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// 检测未被系统识别的列名
    Check {
        /// 输入目录路径
        #[arg(short, long)]
        input: PathBuf,

        /// 是否显示详细输出
        #[arg(short, long, default_value_t = false)]
        verbose: bool,
    },
    /// 将 xls 文件转换为 xlsx 格式
    Convert {
        /// 输入目录路径
        #[arg(short, long)]
        input: PathBuf,

        /// 输出目录路径
        #[arg(short, long)]
        output: PathBuf,
    },
}

/// 系统识别的列名数组
fn get_system_columns() -> HashSet<String> {
    vec![
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
        "大类名称",
    ]
    .into_iter()
    .map(String::from)
    .collect()
}

/// 读取 Excel 文件的列头
fn read_excel_headers(file_path: &Path) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let mut workbook: Xlsx<_> = open_workbook(file_path)?;
    
    // 获取第一个工作表
    if let Some(Ok(range)) = workbook.worksheet_range_at(0) {
        if let Some(first_row) = range.rows().next() {
            let headers: Vec<String> = first_row
                .iter()
                .map(|cell| cell.to_string())
                .collect();
            return Ok(headers);
        }
    }
    
    Ok(vec![])
}

/// 查找所有 Excel 文件
fn find_excel_files(directory: &Path) -> Vec<PathBuf> {
    WalkDir::new(directory)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.file_type().is_file() &&
            e.path().extension().and_then(|s| s.to_str())
                .map(|ext| ext == "xlsx" || ext == "xls" || ext == "xlsm")
                .unwrap_or(false)
        })
        .map(|e| e.path().to_path_buf())
        .collect()
}

/// 查找所有 xls 文件
fn find_xls_files(directory: &Path) -> Vec<PathBuf> {
    WalkDir::new(directory)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.file_type().is_file() &&
            e.path().extension().and_then(|s| s.to_str())
                .map(|ext| ext == "xls")
                .unwrap_or(false)
        })
        .map(|e| e.path().to_path_buf())
        .collect()
}

/// 检测未被系统识别的列名
fn check_unrecognized_columns(
    input_dir: &Path,
    verbose: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    println!("{}", "=".repeat(80).bright_blue());
    println!("{}", "检测未被系统识别的列名".bold().bright_blue());
    println!("{}", "=".repeat(80).bright_blue());
    println!();

    if !input_dir.exists() {
        eprintln!("{} 目录不存在: {:?}", "❌ 错误:".red().bold(), input_dir);
        std::process::exit(1);
    }

    let system_columns = get_system_columns();
    let excel_files = find_excel_files(input_dir);

    if excel_files.is_empty() {
        println!("{} 未找到任何 Excel 文件在目录: {:?}", "❌".red(), input_dir);
        return Ok(());
    }

    println!("✓ 找到 {} 个 Excel 文件\n", excel_files.len());

    let mut unrecognized_all: HashSet<String> = HashSet::new();
    let mut file_results: HashMap<PathBuf, Vec<String>> = HashMap::new();

    for (idx, file_path) in excel_files.iter().enumerate() {
        let relative_path = file_path.strip_prefix(input_dir).unwrap_or(file_path);
        print!("[{}/{}] 处理: ", idx + 1, excel_files.len());
        println!("{}", relative_path.display().to_string().cyan());

        match read_excel_headers(file_path) {
            Ok(headers) => {
                if headers.is_empty() {
                    println!("  {} 文件为空或无法读取列头", "⚠️".yellow());
                    continue;
                }

                let headers_set: HashSet<String> = headers.into_iter().collect();
                let unrecognized: Vec<String> = headers_set
                    .difference(&system_columns)
                    .cloned()
                    .collect();

                if !unrecognized.is_empty() {
                    let mut sorted = unrecognized.clone();
                    sorted.sort();
                    
                    if verbose {
                        println!(
                            "  {} 发现 {} 个未识别列名: {}",
                            "→".yellow(),
                            unrecognized.len(),
                            sorted.join(", ").yellow()
                        );
                    } else {
                        println!(
                            "  {} 发现 {} 个未识别列名",
                            "→".yellow(),
                            unrecognized.len()
                        );
                    }
                    
                    unrecognized_all.extend(unrecognized.iter().cloned());
                    file_results.insert(file_path.clone(), sorted);
                } else {
                    println!("  {} 所有列名均已识别", "→".green());
                }
            }
            Err(e) => {
                println!("  {} 读取失败: {}", "⚠️".yellow(), e);
            }
        }
    }

    // 输出汇总结果
    println!();
    println!("{}", "=".repeat(80).bright_blue());
    println!("{}", "汇总结果".bold().bright_blue());
    println!("{}", "=".repeat(80).bright_blue());
    println!();

    if unrecognized_all.is_empty() {
        println!("{} 所有文件的列名均已被系统识别", "✓".green().bold());
    } else {
        let mut sorted_all: Vec<String> = unrecognized_all.into_iter().collect();
        sorted_all.sort();

        println!(
            "共发现 {} 个未被系统识别的列名:\n",
            sorted_all.len().to_string().yellow().bold()
        );
        
        for col in sorted_all {
            println!("  • {}", col.yellow());
        }

        if verbose && !file_results.is_empty() {
            println!("\n{}", "详细信息:".bold());
            for (file_path, cols) in file_results {
                let relative_path = file_path.strip_prefix(input_dir).unwrap_or(&file_path);
                println!("\n  {}", relative_path.display().to_string().cyan());
                for col in cols {
                    println!("    - {}", col);
                }
            }
        }
    }

    println!();
    println!("{}", "=".repeat(80).bright_blue());
    println!();

    Ok(())
}

/// 将 xls 文件转换为 xlsx 格式
fn convert_xls_to_xlsx(
    input_dir: &Path,
    output_dir: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    println!("{}", "=".repeat(80).bright_blue());
    println!("{}", "将 xls 文件转换为 xlsx 格式".bold().bright_blue());
    println!("{}", "=".repeat(80).bright_blue());
    println!();

    if !input_dir.exists() {
        eprintln!("{} 输入目录不存在: {:?}", "❌ 错误:".red().bold(), input_dir);
        std::process::exit(1);
    }

    // 创建输出目录
    fs::create_dir_all(output_dir)?;

    let xls_files = find_xls_files(input_dir);

    if xls_files.is_empty() {
        println!("{} 未找到任何 xls 文件在目录: {:?}", "❌".red(), input_dir);
        return Ok(());
    }

    println!("✓ 找到 {} 个 xls 文件", xls_files.len());
    println!("✓ 输出目录: {:?}\n", output_dir);

    let mut success_count = 0;
    let mut error_count = 0;

    for (idx, file_path) in xls_files.iter().enumerate() {
        let relative_path = file_path.strip_prefix(input_dir).unwrap_or(file_path);
        print!("[{}/{}] 转换: ", idx + 1, xls_files.len());
        println!("{}", relative_path.display().to_string().cyan());

        // 构建输出文件路径，保持目录结构
        let output_file = output_dir.join(relative_path).with_extension("xlsx");
        
        // 创建输出文件的父目录
        if let Some(parent) = output_file.parent() {
            fs::create_dir_all(parent)?;
        }

        match convert_single_xls_file(file_path, &output_file) {
            Ok(_) => {
                println!("  {} 成功: {:?}", "✓".green(), output_file.strip_prefix(output_dir).unwrap_or(&output_file));
                success_count += 1;
            }
            Err(e) => {
                println!("  {} 失败: {}", "⚠️".yellow(), e);
                error_count += 1;
            }
        }
    }

    // 输出统计结果
    println!();
    println!("{}", "=".repeat(80).bright_blue());
    println!("{}", "转换结果统计".bold().bright_blue());
    println!("{}", "=".repeat(80).bright_blue());
    println!();
    println!("成功: {} 个文件", success_count.to_string().green().bold());
    println!("失败: {} 个文件", error_count.to_string().yellow().bold());
    println!("总计: {} 个文件", xls_files.len());
    println!("\n输出目录: {:?}", output_dir);
    println!();
    println!("{}", "=".repeat(80).bright_blue());
    println!();

    Ok(())
}

/// 转换单个 xls 文件为 xlsx
fn convert_single_xls_file(
    input_path: &Path,
    output_path: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    // 读取 xls 文件
    let mut workbook: Xls<_> = open_workbook(input_path)?;
    
    // 创建新的 xlsx 工作簿
    let mut new_workbook = Workbook::new();

    // 获取所有工作表名称
    let sheet_names = workbook.sheet_names().to_vec();

    for sheet_name in sheet_names {
        if let Ok(range) = workbook.worksheet_range(&sheet_name) {
            // 在新工作簿中创建工作表
            let worksheet = new_workbook.add_worksheet();
            worksheet.set_name(&sheet_name)?;

            // 逐行逐列写入数据
            for (row_idx, row) in range.rows().enumerate() {
                for (col_idx, cell) in row.iter().enumerate() {
                    let row_num = row_idx as u32;
                    let col_num = col_idx as u16;

                    match cell {
                        Data::Int(i) => {
                            worksheet.write_number(row_num, col_num, *i as f64)?;
                        }
                        Data::Float(f) => {
                            worksheet.write_number(row_num, col_num, *f)?;
                        }
                        Data::String(s) => {
                            worksheet.write_string(row_num, col_num, s)?;
                        }
                        Data::Bool(b) => {
                            worksheet.write_boolean(row_num, col_num, *b)?;
                        }
                        Data::DateTime(dt) => {
                            // 尝试转换为字符串
                            worksheet.write_string(row_num, col_num, &format!("{}", dt))?;
                        }
                        Data::Error(e) => {
                            worksheet.write_string(row_num, col_num, &format!("ERROR: {:?}", e))?;
                        }
                        Data::Empty => {
                            // 空单元格不需要写入
                        }
                        _ => {
                            // 处理其他未预期的数据类型
                            worksheet.write_string(row_num, col_num, &cell.to_string())?;
                        }
                    }
                }
            }
        }
    }

    // 保存新的 xlsx 文件
    new_workbook.save(output_path)?;

    Ok(())
}

fn main() {
    let args = Args::parse();

    let result = match args.command {
        Commands::Check { input, verbose } => check_unrecognized_columns(&input, verbose),
        Commands::Convert { input, output } => convert_xls_to_xlsx(&input, &output),
    };

    if let Err(e) = result {
        eprintln!("{} {}", "错误:".red().bold(), e);
        std::process::exit(1);
    }
}

