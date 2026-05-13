#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
ParseScriptV2 - SQL Script Generator

Reads sql.txt and task_task_info.csv from model directory,
generates test_sql.json task script.

Input:
- C:/Users/67461/Desktop/sync_model/model/sql.txt
- C:/Users/67461/Desktop/sync_model/model/task_task_info.csv

Output:
- skills/TransferData/ParseScriptV2/resoult/test_sql.json

Reference:
- C:/Users/67461/Desktop/sync_model/依赖任务模板/tasks/test_sparksql.json
"""

import json
import csv
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
MODEL_DIR = Path("/mnt/c/Users/67461/Desktop/sync_model/model")
REFERENCE_JSON = SCRIPT_DIR.parent / "references" / "test_sparksql.json"
OUTPUT_DIR = SKILL_DIR / "resoult"
OUTPUT_FILE = OUTPUT_DIR / "test_sql.json"

# Input files
SQL_TXT = MODEL_DIR / "sql.txt"
TASK_TASK_INFO_CSV = MODEL_DIR / "task_task_info.csv"


def read_sql_txt():
    """Read SQL content from sql.txt"""
    with open(SQL_TXT, 'r', encoding='utf-8') as f:
        return f.read().strip()


def read_task_task_info_csv():
    """Read task dependency info from CSV"""
    task_list = []
    with open(TASK_TASK_INFO_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task_info = {
                "customOffset": int(row.get("customOffset", 0)),
                "forwardDirection": int(row.get("forwardDirection", 1)),
                "isCurrentProject": row.get("isCurrentProject", "TRUE").upper() == "TRUE",
                "projectAlias": row.get("projectAlias", ""),
                "taskName": row.get("taskName", ""),
                "taskType": int(row.get("taskType", 0)),
                "upDownRelyType": int(row.get("upDownRelyType", 0))
            }
            task_list.append(task_info)
    return task_list


def read_reference():
    """Read reference template"""
    with open(REFERENCE_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_task_script(sql_content, task_deps, reference):
    """Build task script JSON matching reference structure"""
    # Copy taskInfo from reference
    task_info = reference.get("taskInfo", {}).copy()
    
    # Update sqlText with content from sql.txt
    # Add header comments
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task_name = task_info.get("name", "test_sparksql")
    
    sql_header = f"""-- name {task_name}
-- type Spark SQL
-- author admin@dtstack.com
-- create time {timestamp}
-- desc 
"""
    task_info["sqlText"] = sql_header + sql_content
    
    # Build taskTaskInfo from CSV
    task_task_info = task_deps
    
    return {
        "taskInfo": task_info,
        "taskTaskInfo": task_task_info,
        "updateEnvParam": reference.get("updateEnvParam", False)
    }


def write_output(task_script):
    """Write output to resoult directory"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(task_script, f, ensure_ascii=False, indent=2)
    print(f"Output written to: {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("ParseScript - SQL Script Generator")
    print("=" * 60)
    
    # Check input files
    if not SQL_TXT.exists():
        print(f"错误：找不到 sql.txt")
        print(f"  路径：{SQL_TXT}")
        return 1
    
    if not TASK_TASK_INFO_CSV.exists():
        print(f"错误：找不到 task_task_info.csv")
        print(f"  路径：{TASK_TASK_INFO_CSV}")
        return 1
    
    # Read SQL content
    print(f"\n读取 SQL 文件：{SQL_TXT}")
    sql_content = read_sql_txt()
    print(f"  SQL 内容：{sql_content[:50]}...")
    
    # Read task dependencies
    print(f"\n读取任务依赖：{TASK_TASK_INFO_CSV}")
    task_deps = read_task_task_info_csv()
    print(f"  依赖任务数：{len(task_deps)}")
    for dep in task_deps:
        print(f"    - {dep['taskName']} (type={dep['taskType']})")
    
    # Read reference template
    print(f"\n读取参考模板：{REFERENCE_JSON}")
    reference = read_reference()
    
    # Build task script
    print("\n生成任务脚本...")
    task_script = build_task_script(sql_content, task_deps, reference)
    
    # Write output
    print(f"\n写入输出到：{OUTPUT_DIR}")
    write_output(task_script)
    
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
