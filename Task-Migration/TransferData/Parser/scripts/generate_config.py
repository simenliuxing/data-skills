#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Parser Skill - MySQL to HDFS Data Sync Configuration Generator

Reads output from MysqlReader and HdfsWriter skills,
generates a unified parser.json configuration for data synchronization.

Input:
- ../MysqlReader/resoult/mysql_reader_config.json
- ../HdfsWriter/resoult/hdfs_writer_config.json

Output:
- resoult/parser.json
"""

import json
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent  # Parser/scripts
PARSER_DIR = SCRIPT_DIR.parent       # Parser
PARSESNC_DIR = PARSER_DIR.parent     # TransferData
MYSQL_READER_OUTPUT = PARSESNC_DIR / "MysqlReader" / "resoult" / "mysql_reader_config.json"
HDFS_WRITER_OUTPUT = PARSESNC_DIR / "HdfsWriter" / "resoult" / "hdfs_writer_config.json"
REFERENCE_JSON = PARSER_DIR / "references" / "parser.json"
OUTPUT_DIR = PARSER_DIR / "resoult"
OUTPUT_FILE = OUTPUT_DIR / "parser.json"


def read_json_file(filepath):
    """Read JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_source_column(mysql_column):
    """Build sourceMap.column from MySQL Reader column"""
    columns = []
    for col in mysql_column:
        source_col = {
            "part": False,
            "comment": "",
            "isPart": col.get("isPart", False),
            "type": col.get("type", "STRING"),
            "key": col.get("name", "")
        }
        # Add precision for VARCHAR types
        if "VARCHAR" in col.get("type", "").upper():
            source_col["precision"] = 100
        columns.append(source_col)
    return columns


def build_target_column(hdfs_column):
    """Build targetMap.column from HDFS Writer column (includes partition columns)"""
    columns = []
    for col in hdfs_column:
        target_col = {
            "part": col.get("isPart", False),
            "comment": "",
            "isPart": col.get("isPart", False),
            "type": col.get("type", "STRING").lower(),
            "key": col.get("name", "")
        }
        columns.append(target_col)
    return columns


def build_keymap_target(hdfs_column):
    """Build keymap.target from HDFS Writer column (non-partition columns only)"""
    targets = []
    for col in hdfs_column:
        if col.get("isPart", False):
            continue
        
        target = {
            "comment": "",
            "isPart": col.get("isPart", False),
            "type": col.get("type", "STRING").lower(),
            "key": col.get("name", "")
        }
        targets.append(target)
    return targets


def build_parser_config(mysql_config, hdfs_config, reference):
    """Build parser.json configuration"""
    
    # Extract MySQL Reader parameters
    mysql_param = mysql_config.get("reader", {}).get("parameter", {})
    mysql_connection = mysql_param.get("connection", [{}])[0]
    mysql_columns = mysql_param.get("column", [])
    
    # Extract HDFS Writer parameters
    hdfs_param = hdfs_config.get("writer", {}).get("parameter", {})
    hdfs_columns = hdfs_param.get("column", [])
    
    # Build sourceMap
    source_map = {
        "sourceId": mysql_connection.get("sourceId", 0),
        "schema": mysql_connection.get("schema", ""),
        "sourceList": [{
            "sourceId": mysql_connection.get("sourceId", 0),
            "schema": mysql_connection.get("schema", ""),
            "tables": mysql_connection.get("table", []),
            "name": mysql_param.get("dataSourceInfo", {}).get("dataSourceName", ""),
            "type": mysql_param.get("dataSourceInfo", {}).get("dataSourceType", 1),
            "key": "main"
        }],
        "name": mysql_param.get("dataSourceInfo", {}).get("dataSourceName", ""),
        "column": build_source_column(mysql_columns),
        "type": {
            "type": mysql_param.get("dataSourceInfo", {}).get("dataSourceType", 1),
            "table": mysql_connection.get("table", [])
        },
        "extralConfig": ""
    }
    
    # Build targetMap
    target_map = {
        "sourceId": hdfs_param.get("sourceIds", [0])[0],
        "name": hdfs_param.get("dataSourceInfo", {}).get("dataSourceName", ""),
        "column": build_target_column(hdfs_columns),
        "schema": hdfs_param.get("schema", ""),
        "type": {
            "partition": hdfs_param.get("partition", ""),
            "writeMode": hdfs_param.get("writeMode", "overwrite"),
            "type": hdfs_param.get("dataSourceInfo", {}).get("dataSourceType", 45),
            "table": hdfs_param.get("table", "")
        },
        "extralConfig": ""
    }
    
    # Build keymap
    keymap = {
        "source": build_source_column(mysql_columns),
        "target": build_keymap_target(hdfs_columns)
    }
    
    # Build setting (use reference defaults)
    setting = reference.get("setting", {
        "readerChannel": 1,
        "init": False,
        "writerChannel": 1,
        "record": 100,
        "restoreColumnIndex": 0,
        "speed": "-1",
        "isSaveDirty": 0
    })
    
    # Build final parser config
    parser_config = {
        "targetMap": target_map,
        "keymap": keymap,
        "sourceMap": source_map,
        "setting": setting
    }
    
    return parser_config


def write_output(config):
    """Write output to resoult directory"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Output written to: {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("Parser 配置生成器")
    print("=" * 60)
    
    # Check input files
    if not MYSQL_READER_OUTPUT.exists():
        print(f"错误：找不到 MySQL Reader 输出文件")
        print(f"  路径：{MYSQL_READER_OUTPUT}")
        return 1
    
    if not HDFS_WRITER_OUTPUT.exists():
        print(f"错误：找不到 HDFS Writer 输出文件")
        print(f"  路径：{HDFS_WRITER_OUTPUT}")
        return 1
    
    print(f"\n读取 MySQL Reader 配置：{MYSQL_READER_OUTPUT}")
    mysql_config = read_json_file(MYSQL_READER_OUTPUT)
    
    print(f"读取 HDFS Writer 配置：{HDFS_WRITER_OUTPUT}")
    hdfs_config = read_json_file(HDFS_WRITER_OUTPUT)
    
    print(f"\n读取参考模板：{REFERENCE_JSON}")
    reference = read_json_file(REFERENCE_JSON)
    
    print("\n构建 Parser 配置...")
    parser_config = build_parser_config(mysql_config, hdfs_config, reference)
    
    print(f"\n写入输出到：{OUTPUT_DIR}")
    write_output(parser_config)
    
    # Print summary
    print("\n=== 配置摘要 ===")
    print(f"源数据源：{parser_config['sourceMap']['name']}")
    print(f"目标数据源：{parser_config['targetMap']['name']}")
    print(f"源字段数：{len(parser_config['sourceMap']['column'])}")
    print(f"目标字段数：{len(parser_config['targetMap']['column'])}")
    print(f"映射字段数：{len(parser_config['keymap']['target'])}")
    
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
