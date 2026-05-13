#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
ParseScript - Base64 Encoder for DTStack Task Scripts V2

Reads sql_text.json from ParseSqlText, encodes it to Base64,
and outputs the complete task script to the result directory.

Output: skills/TransferData/ParseScript/resoult/mysql2hive.json

Reference format from C:\Users\67461\Desktop\sync_model\tmp\mysql2hive.json
"""

import json
import base64
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent           # ParseScript/scripts
PARSE_SYNC_DIR = SCRIPT_DIR.parent            # ParseScript
PARSENC_PARENT = PARSE_SYNC_DIR.parent        # TransferData
PARSE_SQL_TEXT_RESOULT = PARSENC_PARENT / "ParseSqlText" / "resoult" / "sql_text.json"
REFERENCE_SCRIPT = PARSE_SYNC_DIR / "references" / "mysql2hive_script.json"
OUTPUT_DIR = PARSE_SYNC_DIR / "resoult"
OUTPUT_FILE = OUTPUT_DIR / "mysql2hive_script.json"


def read_sql_text():
    """Read sql_text.json from ParseSqlText resoult"""
    with open(PARSE_SQL_TEXT_RESOULT, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_reference_script():
    """Read reference mysql2hive_script.json for structure"""
    with open(REFERENCE_SCRIPT, 'r', encoding='utf-8') as f:
        return json.load(f)


def encode_to_base64(data):
    """Encode JSON data to Base64 string"""
    json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    return encoded


def build_task_script(sql_text_encoded, reference):
    """Build complete task script JSON matching reference structure"""
    # Copy taskInfo from reference
    task_info = reference.get("taskInfo", {}).copy()
    # Update sqlText with encoded value
    task_info["sqlText"] = sql_text_encoded
    
    return {
        "taskInfo": task_info,
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
    print("ParseScript Base64 编码器 V2")
    print("=" * 60)
    
    # Check input file
    if not PARSE_SQL_TEXT_RESOULT.exists():
        print(f"错误：找不到 sql_text.json")
        print(f"  路径：{PARSE_SQL_TEXT_RESOULT}")
        print(f"  请先运行 ParseSqlText 脚本生成配置")
        return 1
    
    print(f"\n读取 sql_text.json: {PARSE_SQL_TEXT_RESOULT}")
    sql_text = read_sql_text()
    
    print(f"读取参考模板：{REFERENCE_SCRIPT}")
    reference = read_reference_script()
    
    print("\n编码 sql_text 为 Base64...")
    sql_text_encoded = encode_to_base64(sql_text)
    print(f"  编码后长度：{len(sql_text_encoded)} 字符")
    
    print("\n构建任务脚本...")
    task_script = build_task_script(sql_text_encoded, reference)
    
    print(f"\n写入输出到：{OUTPUT_DIR}")
    write_output(task_script)
    
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
