#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ParseSqlText 配置拼接脚本 V3
读取 MysqlReader、HdfsWriter 和 Parser 生成的配置，按照参考模板格式生成 sql_text.json

输出格式:
{
  "parser": "<Parser 配置的 JSON 字符串>",
  "syncModel": 0,
  "createModel": 0,
  "job": "<Job 配置的 JSON 字符串>"
}
"""

import json
import os
from datetime import datetime

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(SKILL_DIR, 'resoult')

# 输入文件路径
MYSQL_READER_CONFIG = os.path.join(SKILL_DIR, '../MysqlReader/resoult/mysql_reader_config.json')
HDFS_WRITER_CONFIG = os.path.join(SKILL_DIR, '../HdfsWriter/resoult/hdfs_writer_config.json')
PARSER_CONFIG = os.path.join(SKILL_DIR, '../Parser/resoult/parser.json')


def load_json_file(filepath):
    """加载 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_job_content(mysql_reader, hdfs_writer):
    """构建 job.content 数组"""
    reader_config = mysql_reader.get('reader', {})
    writer_config = hdfs_writer.get('writer', {})
    
    return [{
        "reader": reader_config,
        "writer": writer_config
    }]


def build_setting_from_parser(parser_config):
    """从 Parser 配置构建 job.setting"""
    parser_setting = parser_config.get('setting', {})
    
    reader_channel = parser_setting.get('readerChannel', 1)
    writer_channel = parser_setting.get('writerChannel', 1)
    
    return {
        "restore": {
            "maxRowNumForCheckpoint": 0,
            "isRestore": False,
            "restoreColumnName": "",
            "restoreColumnIndex": parser_setting.get('restoreColumnIndex', 0)
        },
        "errorLimit": {
            "record": parser_setting.get('record', 100)
        },
        "speed": {
            "readerChannel": reader_channel,
            "writerChannel": writer_channel,
            "bytes": 0,
            "channel": max(reader_channel, writer_channel)
        }
    }


def build_job_object(mysql_reader, hdfs_writer, parser_config):
    """构建完整的 job 对象"""
    return {
        "job": {
            "content": build_job_content(mysql_reader, hdfs_writer),
            "setting": build_setting_from_parser(parser_config)
        }
    }


def build_sql_text_config(mysql_reader, hdfs_writer, parser_config):
    """
    构建完整的 sql_text.json 配置
    
    输出格式:
    {
        "parser": "<Parser JSON 字符串>",
        "syncModel": 0,
        "createModel": 0,
        "job": "<Job JSON 字符串>"
    }
    """
    # 构建 job 对象并字符串化
    job_obj = build_job_object(mysql_reader, hdfs_writer, parser_config)
    job_str = json.dumps(job_obj, ensure_ascii=False, separators=(',', ':'))
    
    # Parser 配置字符串化
    parser_str = json.dumps(parser_config, ensure_ascii=False, separators=(',', ':'))
    
    # 构建最终配置
    return {
        "parser": parser_str,
        "syncModel": 0,
        "createModel": 0,
        "job": job_str
    }


def main():
    """主函数"""
    print("=" * 60)
    print("ParseSqlText 配置拼接器 V3")
    print("=" * 60)
    
    # 检查输入文件
    if not os.path.exists(MYSQL_READER_CONFIG):
        print(f"错误：找不到 MySQL Reader 配置文件")
        print(f"  路径：{MYSQL_READER_CONFIG}")
        return 1
    
    if not os.path.exists(HDFS_WRITER_CONFIG):
        print(f"错误：找不到 HDFS Writer 配置文件")
        print(f"  路径：{HDFS_WRITER_CONFIG}")
        return 1
    
    if not os.path.exists(PARSER_CONFIG):
        print(f"错误：找不到 Parser 配置文件")
        print(f"  路径：{PARSER_CONFIG}")
        return 1
    
    # 加载输入配置
    print(f"\n加载 MySQL Reader 配置：{MYSQL_READER_CONFIG}")
    mysql_reader = load_json_file(MYSQL_READER_CONFIG)
    
    print(f"加载 HDFS Writer 配置：{HDFS_WRITER_CONFIG}")
    hdfs_writer = load_json_file(HDFS_WRITER_CONFIG)
    
    print(f"加载 Parser 配置：{PARSER_CONFIG}")
    parser_config = load_json_file(PARSER_CONFIG)
    
    # 提取关键信息
    reader_param = mysql_reader.get('reader', {}).get('parameter', {})
    writer_param = hdfs_writer.get('writer', {}).get('parameter', {})
    parser_setting = parser_config.get('setting', {})
    
    print(f"\n源数据源：{reader_param.get('dataSourceInfo', {}).get('dataSourceName', 'N/A')}")
    print(f"目标数据源：{writer_param.get('dataSourceInfo', {}).get('dataSourceName', 'N/A')}")
    print(f"读取字段数：{len(reader_param.get('column', []))}")
    print(f"写入字段数：{len(writer_param.get('column', []))}")
    print(f"映射字段数：{len(parser_config.get('keymap', {}).get('target', []))}")
    print(f"读取并发：{parser_setting.get('readerChannel', 1)}")
    print(f"写入并发：{parser_setting.get('writerChannel', 1)}")
    
    # 加载参考模板
    reference_template = os.path.join(SKILL_DIR, 'references/sql_text.json')
    if os.path.exists(reference_template):
        print(f"\n加载参考模板：{reference_template}")
        reference = load_json_file(reference_template)
        print(f"模板格式：parser={('parser' in reference)}, syncModel={reference.get('syncModel')}, createModel={reference.get('createModel')}")
    else:
        reference = {}
    
    # 生成配置
    print("\n拼接 job 配置...")
    sql_text_config = build_sql_text_config(mysql_reader, hdfs_writer, parser_config)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 输出文件路径
    output_file = os.path.join(OUTPUT_DIR, 'sql_text.json')
    
    # 写入 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sql_text_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n配置已生成：{output_file}")
    print(f"parser 字段长度：{len(sql_text_config['parser'])} 字符")
    print(f"job 字段长度：{len(sql_text_config['job'])} 字符")
    print(f"syncModel: {sql_text_config['syncModel']}")
    print(f"createModel: {sql_text_config['createModel']}")
    print("=" * 60)
    print("生成成功!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
