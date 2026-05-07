#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
TransferData 完整流程执行脚本

一键执行所有子技能，生成 DTStack 可发布的数据同步任务包。

流程:
  主流程 (数据同步任务):
    1. MysqlReader       - 读取 MySQL 配置 Excel，生成读取端配置
    2. HdfsWriter        - 读取 HDFS 配置 Excel，生成写入端配置
    3. Parser            - 整合源和目标配置，生成字段映射
    4. ParseSqlText      - 拼接 reader + writer + parser 配置
    5. ParseScriptBase64 - Base64 编码封装 (数据同步任务)
    6. AssembleModel     - 组装发布包

  独立分支 (SQL 任务):
    ParseScript          - 读取 sql.txt + task_task_info.csv，生成 SQL 任务脚本
    AssembleScripyModel  - 组装 SQL 任务发布包

分支说明:
  - 数据同步任务：走主流程 (1→2→3→4→5→6)，使用 ParseScriptBase64 + AssembleModel
  - SQL 任务：走独立分支 (ParseScript → AssembleScripyModel)

输出:
  C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/

用法:
  python3 run_all.py                    # 默认：执行主流程 (数据同步)
  python3 run_all.py --sync             # 显式执行主流程 (数据同步)
  python3 run_all.py --sql              # 执行独立分支 (SQL 任务)
  python3 run_all.py --all              # 执行全部流程
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 基础路径
WORKSPACE = Path("/home/shuofeng/.openclaw/workspace")
TRANSFER_DATA = WORKSPACE / "skills" / "TransferData"

# 主流程脚本 (数据同步任务)
MAIN_FLOW_SCRIPTS = [
    ("1️⃣  MysqlReader", TRANSFER_DATA / "MysqlReader" / "scripts" / "generate_config.py"),
    ("2️⃣  HdfsWriter", TRANSFER_DATA / "HdfsWriter" / "scripts" / "generate_config.py"),
    ("3️⃣  Parser", TRANSFER_DATA / "Parser" / "scripts" / "generate_config.py"),
    ("4️⃣  ParseSqlText", TRANSFER_DATA / "ParseSqlText" / "scripts" / "parse_sql_text.py"),
    ("5️⃣  ParseScriptBase64", TRANSFER_DATA / "ParseScriptBase64" / "scripts" / "parse_script.py"),
    ("6️⃣  AssembleModel", TRANSFER_DATA / "AssembleModel" / "scripts" / "assemble_package.py"),
]

# 独立分支脚本 (SQL 任务)
SQL_BRANCH_SCRIPTS = [
    ("📝  ParseScript", TRANSFER_DATA / "ParseScript" / "scripts" / "generate_config.py"),
    ("📦  AssembleScripyModel", TRANSFER_DATA / "AssembleScripyModel" / "scripts" / "assemble_package.py"),
]

# 完整流程（主流程 + 独立分支）
ALL_SCRIPTS = MAIN_FLOW_SCRIPTS + SQL_BRANCH_SCRIPTS


def print_header(mode):
    """打印标题"""
    print("")
    print("=" * 70)
    if mode == "sql":
        print("                    TransferData - SQL 任务生成流程")
    elif mode == "all":
        print("                    TransferData - 全部流程")
    else:
        print("                    TransferData 数据同步配置生成流程")
    print("=" * 70)
    print("")
    print(f"  开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  工作目录：{WORKSPACE}")
    print(f"  运行模式：{mode}")
    print("")


def print_footer(mode, failed):
    """打印结尾"""
    print("")
    print("=" * 70)
    print("                           ✅ 完成!")
    print("=" * 70)
    print("")
    print(f"  结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  运行模式：{mode}")
    print("")
    
    if mode == "sql":
        print("  📦 SQL 任务发布包位置:")
        print("     C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/")
        print("")
        print("  发布包内容:")
        print("     ├── package.json           (包配置)")
        print("     ├── task_catalogue.json    (任务目录)")
        print("     ├── task.xls               (任务 Excel)")
        print("     ├── error.log              (错误日志)")
        print("     └── tasks/")
        print("         └── test_sparksql.json  (SQL 任务脚本)")
        print("")
        print("  下一步:")
        print("     在 DTStack 平台导入发布包即可执行 SQL 任务")
    elif mode == "sync":
        print("  📦 数据同步任务发布包位置:")
        print("     C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/")
        print("")
        print("  发布包内容:")
        print("     ├── package.json           (包配置)")
        print("     ├── task_catalogue.json    (任务目录)")
        print("     ├── task.xls               (任务 Excel)")
        print("     ├── error.log              (错误日志)")
        print("     └── tasks/")
        print("         └── mysql2hive_script.json  (任务脚本)")
        print("")
        print("  下一步:")
        print("     在 DTStack 平台导入发布包即可执行数据同步任务")
    elif mode == "all":
        print("  📦 发布包位置:")
        print("     C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/ (数据同步任务)")
        print("     C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/ (SQL 任务)")
        print("")
        print("  下一步:")
        print("     在 DTStack 平台导入发布包即可执行相应任务")
    print("")
    
    if failed:
        print("  ⚠️  以下步骤失败:")
        for name in failed:
            print(f"     - {name}")
        print("")


def run_script(name, script_path):
    """执行单个脚本"""
    print("-" * 70)
    print(f"  {name}")
    print("-" * 70)
    
    if not script_path.exists():
        print(f"  ❌ 错误：脚本不存在")
        print(f"     路径：{script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(WORKSPACE),
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  ❌ 错误：脚本执行失败 (返回码：{result.returncode})")
            return False
        
        print("")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return False


def run_main_flow():
    """运行主流程（数据同步任务）"""
    print("\n📌 运行模式：数据同步任务 (主流程)")
    print("   流程：MysqlReader → HdfsWriter → Parser → ParseSqlText → ParseScriptBase64 → AssembleModel")
    print("")
    
    failed = []
    
    for name, script_path in MAIN_FLOW_SCRIPTS:
        success = run_script(name, script_path)
        if not success:
            failed.append(name)
            print("")
            print("  ⚠️  该步骤失败，是否继续？(y/n): ", end="", flush=True)
            try:
                response = input().strip().lower()
                if response != 'y':
                    print("")
                    print("=" * 70)
                    print("                    ❌ 流程已终止")
                    print("=" * 70)
                    return failed
            except:
                pass
    
    return failed


def run_sql_branch():
    """运行 SQL 任务分支（独立流程）"""
    print("\n📌 运行模式：SQL 任务 (独立分支)")
    print("   流程：ParseScript → AssembleScripyModel")
    print("   说明：独立流程，不依赖主流程的任何输出，生成 SQL 任务发布包")
    print("")
    
    failed = []
    
    for name, script_path in SQL_BRANCH_SCRIPTS:
        success = run_script(name, script_path)
        if not success:
            failed.append(name)
            # 如果 ParseScript 失败，询问是否继续；如果 AssembleScripyModel 失败，直接继续
            if "ParseScript" in name:
                print("")
                print("  ⚠️  该步骤失败，是否继续？(y/n): ", end="", flush=True)
                try:
                    response = input().strip().lower()
                    if response != 'y':
                        print("")
                        print("=" * 70)
                        print("                    ❌ 流程已终止")
                        print("=" * 70)
                        return failed
                except:
                    pass
            else:
                print("")
                print("  ⚠️  该步骤失败，继续后续步骤...")
    
    return failed


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="TransferData 数据同步配置生成流程")
    parser.add_argument("--sync", action="store_true", help="执行主流程（数据同步任务，默认）")
    parser.add_argument("--sql", action="store_true", help="执行独立分支（SQL 任务）")
    parser.add_argument("--all", action="store_true", help="执行全部流程")
    args = parser.parse_args()
    
    # 确定模式
    if args.sql:
        mode = "sql"
    elif args.all:
        mode = "all"
    else:
        mode = "sync"  # 默认执行主流程
    
    print_header(mode)
    
    all_failed = []
    
    if mode == "sql":
        # 仅运行 SQL 任务分支
        failed = run_sql_branch()
        all_failed.extend(failed)
        
    elif mode == "sync":
        # 仅运行主流程
        failed = run_main_flow()
        all_failed.extend(failed)
        
    elif mode == "all":
        # 运行全部流程
        print("\n" + "=" * 70)
        print("  第一部分：主流程 (数据同步任务)")
        print("  流程：MysqlReader → HdfsWriter → Parser → ParseSqlText → ParseScriptBase64 → AssembleModel")
        print("=" * 70)
        failed = run_main_flow()
        all_failed.extend(failed)
        
        print("\n" + "=" * 70)
        print("  第二部分：独立分支 (SQL 任务)")
        print("  流程：ParseScript → AssembleScripyModel")
        print("=" * 70)
        failed = run_sql_branch()
        all_failed.extend(failed)
    
    print_footer(mode, all_failed)
    
    if all_failed:
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
