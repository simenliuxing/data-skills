#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
HdfsWriter Config Generator V2

Reads hdfs_info.xlsx with two sheets:
- properties: data source configuration
- table_info: table and column information

Generates hdfs_writer_config.json following the hdfs_writer.json reference format exactly.

Output: skills/TransferData/HdfsWriter/resoult/hdfs_writer_config.json
"""

import json
import os
import zipfile
import re
from xml.etree import ElementTree as ET
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
HDFS_WRITER_DIR = SCRIPT_DIR.parent
XLSX_INPUT = Path("/mnt/c/Users/67461/Desktop/sync_model/model/hdfs_info.xlsx")
REFERENCE_JSON = HDFS_WRITER_DIR / "references" / "hdfs_writer.json"
OUTPUT_DIR = HDFS_WRITER_DIR / "resoult"
OUTPUT_FILE = OUTPUT_DIR / "hdfs_writer_config.json"


def get_sheet_names(zip_ref):
    """Get sheet names from workbook.xml"""
    try:
        with zip_ref.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
            sheet_names = {}
            for sheet in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                name = sheet.get('name')
                r_id = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if name and r_id:
                    if r_id.startswith('rId'):
                        sheet_num = r_id[3:]
                        sheet_file = f'xl/worksheets/sheet{sheet_num}.xml'
                        sheet_names[name.lower()] = sheet_file
            
            return sheet_names
    except Exception as e:
        print(f"Warning: Could not parse sheet names: {e}")
        return {
            'properties': 'xl/worksheets/sheet1.xml',
            'table_info': 'xl/worksheets/sheet2.xml'
        }


def read_shared_strings(zip_ref):
    """Read sharedStrings.xml to get string values"""
    shared_strings = {}
    try:
        if 'xl/sharedStrings.xml' in zip_ref.namelist():
            with zip_ref.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for idx, si in enumerate(root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')):
                    t = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    if t is not None:
                        shared_strings[idx] = t.text
    except Exception as e:
        print(f"Warning: Could not read shared strings: {e}")
    
    return shared_strings


def parse_worksheet(zip_ref, worksheet_path, shared_strings):
    """Parse a single worksheet XML file"""
    row_data = {}
    
    try:
        with zip_ref.open(worksheet_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            # Read all cells
            cells = {}
            for cell in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                r = cell.get('r')
                t_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if t_elem is not None:
                    value = t_elem.text
                    
                    if value and value.isdigit() and int(value) in shared_strings:
                        value = shared_strings[int(value)]
                    
                    cells[r] = value
            
            # Parse by row
            for coord, value in cells.items():
                col = ''.join(c for c in coord if c.isalpha())
                row = ''.join(c for c in coord if c.isdigit())
                if row not in row_data:
                    row_data[row] = {}
                row_data[row][col] = value
                
    except Exception as e:
        print(f"Error parsing worksheet {worksheet_path}: {e}")
    
    return row_data


def parse_properties_sheet(row_data):
    """Parse properties sheet for data source configuration"""
    config = {
        "dataSourceName": "",
        "dataSourceType": 45,
        "jdbc": "",
        "username": "",
        "password": "",
        "dtCenterSourceId": None,
        "sourceIds": None,
        "path": "",
        "partition": "",
        "fileType": "orc",
        "defaultFS": "",
        "hadoopConfig": {}
    }
    
    for row_num in sorted(row_data.keys(), key=int):
        row = row_data[row_num]
        key = row.get('A', '')
        value = row.get('B', '')
        
        if not key:
            continue
        
        if key == "dataSourceName":
            config["dataSourceName"] = value
        elif key == "dataSourceType":
            try:
                config["dataSourceType"] = int(value)
            except (ValueError, TypeError):
                pass
        elif key == "jdbc":
            config["jdbc"] = value
        elif key == "username":
            config["username"] = value
        elif key == "password":
            config["password"] = value
        elif key == "dtCenterSourceId":
            try:
                config["dtCenterSourceId"] = int(value)
            except (ValueError, TypeError):
                pass
        elif key == "sourceIds":
            try:
                config["sourceIds"] = int(value)
            except (ValueError, TypeError):
                pass
        elif key == "path":
            config["path"] = value
        elif key == "partition":
            config["partition"] = value
        elif key == "fileType":
            config["fileType"] = value
        elif key == "defaultFS":
            config["defaultFS"] = value
        elif key == "hadoopConfig":
            try:
                config["hadoopConfig"] = json.loads(value)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse hadoopConfig: {e}")
                config["hadoopConfig"] = {}
    
    return config


def parse_table_info_sheet(row_data):
    """Parse table_info sheet for column definitions
    
    Sheet format:
    - A1: table name
    - B1: CREATE TABLE SQL with column definitions and partition info
    
    Example SQL:
    CREATE TABLE `zy_test`.`students`(
        `id` INT COMMENT'',
        `name` STRING COMMENT'',
        `age` INT COMMENT'',
        `pt` STRING
    )USING orc
    PARTITIONED BY(
        pt
    )COMMENT''
    """
    columns = []
    table_name = ""
    partition_columns = []
    
    sorted_rows = sorted(row_data.keys(), key=int)
    if not sorted_rows:
        return columns, table_name, partition_columns
    
    row1 = row_data.get('1', {})
    create_sql = row1.get('B', '')
    table_name = row1.get('A', 'unknown')
    
    if not create_sql:
        return columns, table_name, partition_columns
    
    # Find content between first ( and )USING or )PARTITIONED
    match = re.search(r'\((.*)\)USING', create_sql, re.DOTALL | re.IGNORECASE)
    if not match:
        match = re.search(r'\((.*)\)\s*PARTITIONED', create_sql, re.DOTALL | re.IGNORECASE)
    
    if match:
        columns_section = match.group(1)
        
        # Split by line and parse each column definition
        lines = columns_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('CREATE'):
                continue
            
            # Remove leading comma if present
            if line.startswith(','):
                line = line[1:].strip()
            
            # Check if line starts with backtick (column name)
            if line.startswith('`'):
                # Remove backticks
                line = line.replace('`', '')
                
                # Parse: column_name TYPE COMMENT''
                col_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+([A-Z]+)(?:\([^)]*\))?(?:\s+COMMENT.*)?', line)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    columns.append({
                        'name': col_name,
                        'type': col_type.lower()
                    })
    
    # Parse PARTITIONED BY section
    partition_match = re.search(r'PARTITIONED BY\s*\(([^)]+)\)', create_sql, re.IGNORECASE)
    if partition_match:
        partition_section = partition_match.group(1)
        # Extract partition column names
        partition_cols = re.findall(r'`?([a-zA-Z_][a-zA-Z0-9_]*)`?', partition_section)
        partition_columns = partition_cols
    
    return columns, table_name, partition_columns


def extract_schema_from_path(path):
    """Extract schema/database name from HDFS path"""
    if not path:
        return "unknown"
    # Look for pattern like /zy_test.db/
    match = re.search(r'/([a-zA-Z_][a-zA-Z0-9_]*)\.db', path)
    if match:
        return match.group(1)
    return "unknown"


def extract_table_from_path(path):
    """Extract table name from HDFS path"""
    if not path:
        return "unknown"
    # Get last part of path before any partition
    path = path.rstrip('/')
    parts = path.split('/')
    if parts:
        return parts[-1]
    return "unknown"


def build_hdfs_writer_config(properties_config, columns, partition_columns, table_name, reference):
    """Build HDFS Writer configuration JSON matching reference structure exactly"""
    # Extract schema from path
    schema = extract_schema_from_path(properties_config["path"])
    
    # Use table name from table_info sheet
    table = table_name if table_name else extract_table_from_path(properties_config["path"])
    
    # Build path by concatenating properties path with table name
    # Ensure path ends with table name (e.g., .../zy_test.db/students)
    base_path = properties_config.get("path", "").rstrip('/')
    if table and not base_path.endswith(f'/{table}'):
        full_path = f"{base_path}/{table}"
    else:
        full_path = base_path
    
    # Build column array with full structure
    column_array = []
    full_column_names = []
    full_column_types = []
    
    for idx, col in enumerate(columns):
        col_type_upper = col.get("type", "STRING").upper()
        column_array.append({
            "customConverterType": col_type_upper,
            "name": col.get("name", ""),
            "index": idx,
            "isPart": col.get("name", "") in partition_columns,
            "type": col_type_upper,
            "key": col.get("name", "")
        })
        full_column_names.append(col.get("name", ""))
        full_column_types.append(col_type_upper)
    
    # Build connection array
    connection = [{
        "jdbcUrl": properties_config.get("jdbc", ""),
        "table": [table] if table else []
    }]
    
    # Build dataSourceInfo
    data_source_info = {
        "dataSourceName": properties_config.get("dataSourceName", "unknown"),
        "dataSourceType": properties_config.get("dataSourceType", 45)
    }
    
    # Build the complete configuration
    writer_config = {
        "writer": {
            "parameter": {
                "schema": schema,
                "fileName": properties_config.get("partition", ""),
                "dtCenterSourceId": properties_config.get("dtCenterSourceId"),
                "column": column_array,
                "dtCenterSourceIds": [properties_config.get("dtCenterSourceId")] if properties_config.get("dtCenterSourceId") else [],
                "writeMode": "overwrite",
                "encoding": "utf-8",
                "fullColumnName": full_column_names,
                "dataSourceInfo": data_source_info,
                "path": full_path,
                "password": properties_config.get("password", ""),
                "partition": properties_config.get("partition", ""),
                "hadoopConfig": properties_config.get("hadoopConfig", {}),
                "defaultFS": properties_config.get("defaultFS", ""),
                "connection": connection,
                "table": table,
                "fileType": properties_config.get("fileType", "orc"),
                "sourceIds": [properties_config.get("sourceIds")] if properties_config.get("sourceIds") else [],
                "username": properties_config.get("username", ""),
                "fullColumnType": full_column_types
            },
            "name": "hdfswriter"
        }
    }
    
    return writer_config


def read_reference():
    """Read reference hdfs_writer.json"""
    with open(REFERENCE_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_output(config):
    """Write output to resoult directory"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Output written to: {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("HdfsWriter 配置生成器 V2 (多 Sheet 支持)")
    print("=" * 60)
    
    # Check input file
    if not XLSX_INPUT.exists():
        print(f"错误：找不到输入文件")
        print(f"  路径：{XLSX_INPUT}")
        return 1
    
    print(f"\n读取 Excel 文件：{XLSX_INPUT}")

    properties_config = {}
    columns = []
    partition_columns = []
    table_name = ""
    
    try:
        with zipfile.ZipFile(XLSX_INPUT, 'r') as zip_ref:
            # Get sheet names
            sheet_names = get_sheet_names(zip_ref)
            print(f"检测到的 Sheet: {list(sheet_names.keys())}")
            
            # Read shared strings
            shared_strings = read_shared_strings(zip_ref)
            
            # Parse properties sheet
            properties_sheet_path = sheet_names.get('properties', 'xl/worksheets/sheet1.xml')
            if properties_sheet_path in zip_ref.namelist():
                print(f"解析 properties sheet: {properties_sheet_path}")
                properties_data = parse_worksheet(zip_ref, properties_sheet_path, shared_strings)
                properties_config = parse_properties_sheet(properties_data)
            else:
                print(f"警告：未找到 properties sheet，使用默认路径")
                properties_data = parse_worksheet(zip_ref, 'xl/worksheets/sheet1.xml', shared_strings)
                properties_config = parse_properties_sheet(properties_data)
            
            # Parse table_info sheet
            table_info_sheet_path = sheet_names.get('table_info', 'xl/worksheets/sheet2.xml')
            if table_info_sheet_path in zip_ref.namelist():
                print(f"解析 table_info sheet: {table_info_sheet_path}")
                table_info_data = parse_worksheet(zip_ref, table_info_sheet_path, shared_strings)
                columns, table_name, partition_columns = parse_table_info_sheet(table_info_data)
            else:
                print(f"警告：未找到 table_info sheet，使用默认路径")
                table_info_data = parse_worksheet(zip_ref, 'xl/worksheets/sheet2.xml', shared_strings)
                columns, table_name, partition_columns = parse_table_info_sheet(table_info_data)
    
    except Exception as e:
        print(f"错误：解析 Excel 文件失败：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"\n解析配置:")
    print(f"  dataSourceName: {properties_config.get('dataSourceName', '')}")
    print(f"  jdbc: {properties_config.get('jdbc', '')[:60]}...")
    print(f"  username: {properties_config.get('username', '')}")
    print(f"  path: {properties_config.get('path', '')}")
    print(f"  fileType: {properties_config.get('fileType', '')}")
    print(f"  table: {table_name}")
    print(f"  schema: {extract_schema_from_path(properties_config.get('path', ''))}")
    print(f"  列数量：{len(columns)}")
    for col in columns:
        is_part = col.get("name", "") in partition_columns
        part_marker = " [PARTITION]" if is_part else ""
        print(f"    - {col['name']}: {col['type']}{part_marker}")
    
    print(f"\n读取参考模板：{REFERENCE_JSON}")
    reference = read_reference()
    
    print("\n构建 HDFS Writer 配置...")
    writer_config = build_hdfs_writer_config(properties_config, columns, partition_columns, table_name, reference)
    
    print(f"\n写入输出到：{OUTPUT_DIR}")
    write_output(writer_config)
    
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
