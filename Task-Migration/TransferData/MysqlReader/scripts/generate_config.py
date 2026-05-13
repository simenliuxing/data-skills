#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
MysqlReader Config Generator V2

Reads mysql_info.xlsx with two sheets:
- properties: data source configuration
- table_info: table and column information

Generates mysql_reader_config.json following the mysql_reader.json reference format exactly.

Output: skills/TransferData/MysqlReader/resoult/mysql_reader_config.json
"""

import json
import os
import zipfile
import re
from xml.etree import ElementTree as ET
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
MYSQL_READER_DIR = SCRIPT_DIR.parent
XLSX_INPUT = Path("/mnt/c/Users/67461/Desktop/sync_model/model/mysql_info.xlsx")
REFERENCE_JSON = MYSQL_READER_DIR / "references" / "mysql_reader.json"
OUTPUT_DIR = MYSQL_READER_DIR / "resoult"
OUTPUT_FILE = OUTPUT_DIR / "mysql_reader_config.json"


def get_sheet_names(zip_ref):
    """Get sheet names from workbook.xml"""
    try:
        with zip_ref.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            sheet_names = {}
            for sheet in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                name = sheet.get('name')
                r_id = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if name and r_id:
                    # Extract sheet number from r:id like "rId1" -> sheet1.xml
                    if r_id.startswith('rId'):
                        sheet_num = r_id[3:]
                        sheet_file = f'xl/worksheets/sheet{sheet_num}.xml'
                        sheet_names[name.lower()] = sheet_file
            
            return sheet_names
    except Exception as e:
        print(f"Warning: Could not parse sheet names: {e}")
        # Fallback to default mapping
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
                r = cell.get('r')  # e.g., "A1", "B1"
                t_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if t_elem is not None:
                    value = t_elem.text
                    
                    # Handle shared string references
                    if value and value.isdigit() and int(value) in shared_strings:
                        value = shared_strings[int(value)]
                    
                    cells[r] = value
            
            # Parse by row (assuming column A is key, column B is value)
            for coord, value in cells.items():
                # Parse coordinate like "A1" -> col="A", row="1"
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
        "jdbc": "",
        "username": "",
        "password": "",
        "dtCenterSourceId": None,
        "sourceIds": None,
        "schema": "",
        "table": ""
    }
    
    # Sort by row number and process
    for row_num in sorted(row_data.keys(), key=int):
        row = row_data[row_num]
        key = row.get('A', '')
        value = row.get('B', '')
        
        if not key:
            continue
        
        if key == "dataSourceName":
            config["dataSourceName"] = value
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
                config["dtCenterSourceId"] = None
        elif key == "sourceIds":
            try:
                config["sourceIds"] = int(value)
            except (ValueError, TypeError):
                config["sourceIds"] = None
        elif key == "schema":
            config["schema"] = value
        elif key == "table":
            config["table"] = value
    
    return config


def extract_schema_from_jdbc(jdbc_url):
    """Extract schema/database name from JDBC URL"""
    if not jdbc_url:
        return "unknown"
    match = re.search(r'jdbc:mysql://[^/]+/([^?]+)', jdbc_url)
    if match:
        return match.group(1).split('?')[0]
    return "unknown"


def extract_table_from_jdbc(jdbc_url):
    """Extract table name from JDBC URL or use default"""
    if not jdbc_url:
        return "unknown"
    # Try to extract from path
    match = re.search(r'/([^/?]+)(?:\?|$)', jdbc_url)
    if match:
        return match.group(1)
    return "unknown"


def extract_table_name_from_sql(create_sql):
    """Extract table name from CREATE TABLE SQL"""
    match = re.search(r'CREATE TABLE `([a-zA-Z_][a-zA-Z0-9_]*)`', create_sql)
    if match:
        return match.group(1)
    return "unknown"


def parse_table_info_sheet(row_data):
    """Parse table_info sheet for column definitions
    
    Sheet format:
    - A1: table name
    - B1: CREATE TABLE SQL with column definitions
    
    Example SQL:
    CREATE TABLE `students`(
        `id` INT COMMENT'',
        `name` VARCHAR(255) COMMENT'',
        `age` INT COMMENT''
    )comment''
    """
    columns = []
    table_name = ""
    
    # Sort by row number
    sorted_rows = sorted(row_data.keys(), key=int)
    if not sorted_rows:
        return columns, table_name
    
    # Get the CREATE TABLE SQL from B1 (row 1, column B)
    row1 = row_data.get('1', {})
    create_sql = row1.get('B', '')
    # A1 contains the table name
    table_name = row1.get('A', 'unknown')
    
    if not create_sql:
        return columns, table_name
    
    # Find content between parentheses
    match = re.search(r'\((.*)\)comment', create_sql, re.DOTALL)
    if match:
        columns_section = match.group(1)
        
        # Split by line and parse each column definition
        lines = columns_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('CREATE') or line.endswith(')comment'):
                continue
            
            # Remove leading comma if present
            if line.startswith(','):
                line = line[1:].strip()
            
            # Check if line starts with backtick (column name)
            if line.startswith('`'):
                # Remove backticks
                line = line.replace('`', '')
                
                # Parse: column_name TYPE COMMENT''
                # Example: id INT COMMENT''
                # Or: name VARCHAR(255) COMMENT''
                col_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+([A-Z]+)(?:\([^)]*\))?', line)
                if col_match:
                    columns.append({
                        'name': col_match.group(1),
                        'type': col_match.group(2)
                    })
    
    return columns, table_name


def build_mysql_reader_config(properties_config, columns, reference):
    """Build MySQL Reader configuration JSON matching reference structure exactly"""
    # Use schema from properties if available, otherwise extract from JDBC
    schema = properties_config.get("schema") or extract_schema_from_jdbc(properties_config["jdbc"])
    
    # Use table from properties if available
    table = properties_config.get("table")
    if not table:
        # Fallback to extracting from JDBC URL
        table = extract_table_from_jdbc(properties_config["jdbc"])
    
    # Build column list with full structure (matching reference format)
    column_list = []
    for col in columns:
        column_list.append({
            "customConverterType": col.get("type", "VARCHAR"),
            "name": col.get("name", ""),
            "isPart": False,
            "type": col.get("type", "VARCHAR"),
            "key": col.get("name", "")
        })
    
    # Build the complete configuration (matching reference structure exactly)
    reader_config = {
        "reader": {
            "parameter": {
                "password": properties_config["password"],
                "customSql": "",
                "startLocation": "",
                "dtCenterSourceId": properties_config["dtCenterSourceId"],
                "increColumn": "",
                "column": column_list,
                "dtCenterSourceIds": [properties_config["dtCenterSourceId"]] if properties_config["dtCenterSourceId"] else [],
                "connection": [{
                    "schema": schema,
                    "sourceId": properties_config["sourceIds"],
                    "password": properties_config["password"],
                    "jdbcUrl": [properties_config["jdbc"]],
                    "type": 1,
                    "table": [table],
                    "username": properties_config["username"]
                }],
                "sourceIds": [properties_config["sourceIds"]] if properties_config["sourceIds"] else [],
                "username": properties_config["username"],
                "dataSourceInfo": {
                    "dataSourceName": properties_config["dataSourceName"],
                    "dataSourceType": 1
                }
            },
            "name": "mysqlreader"
        }
    }
    
    return reader_config


def read_reference():
    """Read reference mysql_reader.json"""
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
    print("MysqlReader 配置生成器 V2 (多Sheet支持)")
    print("=" * 60)
    
    # Check input file
    if not XLSX_INPUT.exists():
        print(f"错误：找不到输入文件")
        print(f"  路径：{XLSX_INPUT}")
        return 1
    
    print(f"\n读取 Excel 文件：{XLSX_INPUT}")

    # Parse XLSX file
    properties_config = {}
    columns = []
    table_name = ""
    
    try:
        with zipfile.ZipFile(XLSX_INPUT, 'r') as zip_ref:
            # Get sheet names
            sheet_names = get_sheet_names(zip_ref)
            print(f"检测到的Sheet: {list(sheet_names.keys())}")
            
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
                columns, table_name = parse_table_info_sheet(table_info_data)
                # Override table from properties if exists
                if properties_config.get('table'):
                    table_name = properties_config['table']
            else:
                print(f"警告：未找到 table_info sheet，使用默认路径")
                table_info_data = parse_worksheet(zip_ref, 'xl/worksheets/sheet2.xml', shared_strings)
                columns, table_name = parse_table_info_sheet(table_info_data)
                if properties_config.get('table'):
                    table_name = properties_config['table']
            
            properties_config['table'] = table_name
    
    except Exception as e:
        print(f"错误：解析Excel文件失败: {e}")
        return 1
    
    print(f"\n解析配置:")
    print(f"  dataSourceName: {properties_config.get('dataSourceName', '')}")
    print(f"  jdbc: {properties_config.get('jdbc', '')[:60]}...")
    print(f"  username: {properties_config.get('username', '')}")
    print(f"  schema: {properties_config.get('schema', '')}")
    print(f"  table: {properties_config.get('table', '')}")
    print(f"  列数量：{len(columns)}")
    for col in columns:
        print(f"    - {col['name']}: {col['type']}")
    
    print(f"\n读取参考模板：{REFERENCE_JSON}")
    reference = read_reference()
    
    print("\n构建 MySQL Reader 配置...")
    reader_config = build_mysql_reader_config(properties_config, columns, reference)
    
    print(f"\n写入输出到：{OUTPUT_DIR}")
    write_output(reader_config)
    
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
