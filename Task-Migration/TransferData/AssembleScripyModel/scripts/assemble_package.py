#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
AssembleScripyModel - SQL 脚本发布包组装技能

读取 ParseScript 生成的 SQL 任务脚本，组装成 DTStack 平台可发布的完整目录结构。

Input:
- ../ParseScript/resoult/test_sql.json

Output:
- C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
  ├── package.json
  ├── task_catalogue.json
  ├── task.xls
  ├── error.log
  └── tasks/
      └── test_sparksql.json

Reference:
- C:/Users/67461/Desktop/sync_model/sql 脚本模板/
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import random
import string

# Paths
SCRIPT_DIR = Path(__file__).parent           # AssembleScripyModel/scripts
SKILL_DIR = SCRIPT_DIR.parent                # AssembleScripyModel
TRANSFER_DATA_DIR = SKILL_DIR.parent         # TransferData
PARSER_SCRIPT_OUTPUT = TRANSFER_DATA_DIR / "ParseScript" / "resoult" / "test_sql.json"
REFERENCE_DIR = SKILL_DIR / "references"
OUTPUT_BASE = Path("/mnt/c/Users/67461/Desktop")


def read_task_script():
    """读取 ParseScript 生成的任务脚本"""
    with open(PARSER_SCRIPT_OUTPUT, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_reference_template(name):
    """读取参考模板"""
    ref_path = REFERENCE_DIR / name
    if ref_path.exists():
        with open(ref_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def generate_package_name():
    """生成包名称（带随机后缀）"""
    timestamp = datetime.now().strftime("%Y_%m_%d")
    random_suffix = ''.join(random.choices(string.hexdigits.lower()[:16], k=8))
    return f"BP_{timestamp}_{random_suffix}"


def build_package_json(task_script, ref_template):
    """构建 package.json"""
    task_info = task_script.get("taskInfo", {})
    
    # 从参考模板获取默认值
    if ref_template:
        package = ref_template.copy()
    else:
        package = {
            "createTime": "",
            "createUser": "admin@dtstack.com",
            "engineList": [],
            "packageDesc": "sql 脚本",
            "packageName": "",
            "projectName": "zy_test",
            "tenantName": "培训演示",
            "userNameList": []
        }
    
    # 更新字段
    package["createTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    package["packageName"] = generate_package_name()
    
    # 从任务脚本中提取引擎信息
    engine_type = task_info.get("engineType", 1)
    engine_list = package.get("engineList", [])
    if not engine_list:
        engine_list = [{"engineType": engine_type, "schema": "zy_test"}]
    elif len(engine_list) > 0:
        engine_list[0]["engineType"] = engine_type
    
    package["engineList"] = engine_list
    
    return package


def build_task_catalogue_json(ref_template):
    """构建 task_catalogue.json"""
    if ref_template:
        return ref_template
    
    # 默认模板
    return {
        "0": [{
            "catalogueType": 0,
            "createUserId": 101769,
            "engineType": 0,
            "gmtCreate": int(datetime.now().timestamp() * 1000),
            "gmtModified": int(datetime.now().timestamp() * 1000),
            "id": 31153,
            "isDeleted": 0,
            "level": 0,
            "nodeName": "周期任务",
            "nodePid": 0,
            "orderVal": 1,
            "projectId": 695,
            "sort": 0,
            "tenantId": 10719
        }],
        "1": [{
            "catalogueType": 0,
            "createUserId": 101769,
            "engineType": 0,
            "gmtCreate": int(datetime.now().timestamp() * 1000),
            "gmtModified": int(datetime.now().timestamp() * 1000),
            "id": 31155,
            "isDeleted": 0,
            "level": 1,
            "nodeName": "任务开发",
            "nodePid": 31153,
            "projectId": 695,
            "sort": 0,
            "tenantId": 10719
        }],
        "2": [{
            "catalogueType": 0,
            "createUserId": 1,
            "engineType": 0,
            "gmtCreate": int(datetime.now().timestamp() * 1000),
            "gmtModified": int(datetime.now().timestamp() * 1000),
            "id": 33357,
            "isDeleted": 0,
            "level": 2,
            "nodeName": "测试",
            "nodePid": 31155,
            "projectId": 695,
            "sort": 0,
            "tenantId": 10719
        }]
    }


def copy_task_xls():
    """复制 task.xls 模板"""
    src = REFERENCE_DIR / "task.xls"
    if src.exists():
        return src
    return None


def write_output(output_dir, package_json, task_catalogue_json, task_xls_src, task_script):
    """写入输出文件"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入 package.json
    package_file = output_dir / "package.json"
    with open(package_file, 'w', encoding='utf-8') as f:
        json.dump(package_json, f, ensure_ascii=False, indent=2)
    print(f"  ✓ package.json")
    
    # 写入 task_catalogue.json
    catalogue_file = output_dir / "task_catalogue.json"
    with open(catalogue_file, 'w', encoding='utf-8') as f:
        json.dump(task_catalogue_json, f, ensure_ascii=False, indent=2)
    print(f"  ✓ task_catalogue.json")
    
    # 复制 task.xls
    if task_xls_src:
        task_xls_dst = output_dir / "task.xls"
        shutil.copy2(task_xls_src, task_xls_dst)
        print(f"  ✓ task.xls")
    else:
        print(f"  ⚠ task.xls 模板不存在，跳过")
    
    # 创建空 error.log
    error_log = output_dir / "error.log"
    error_log.touch()
    print(f"  ✓ error.log")
    
    # 创建 tasks/ 目录并复制任务脚本
    tasks_dir = output_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    
    # 从任务脚本中获取任务名称
    task_info = task_script.get("taskInfo", {})
    task_name = task_info.get("name", "test_sparksql")
    task_file = tasks_dir / f"{task_name}.json"
    
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_script, f, ensure_ascii=False, indent=2)
    print(f"  ✓ tasks/{task_name}.json")


def main():
    print("=" * 60)
    print("AssembleScripyModel - SQL 脚本发布包组装")
    print("=" * 60)
    
    # 检查输入文件
    if not PARSER_SCRIPT_OUTPUT.exists():
        print(f"\n错误：找不到 ParseScript 输出文件")
        print(f"  路径：{PARSER_SCRIPT_OUTPUT}")
        print(f"  请先运行 ParseScript 脚本生成任务脚本")
        return 1
    
    print(f"\n读取任务脚本：{PARSER_SCRIPT_OUTPUT}")
    task_script = read_task_script()
    
    task_info = task_script.get("taskInfo", {})
    print(f"  任务名称：{task_info.get('name', 'N/A')}")
    print(f"  引擎类型：{task_info.get('engineType', 'N/A')}")
    print(f"  项目 ID: {task_info.get('projectId', 'N/A')}")
    
    # 读取参考模板
    print(f"\n读取参考模板：{REFERENCE_DIR}")
    package_ref = read_reference_template("package.json")
    catalogue_ref = read_reference_template("task_catalogue.json")
    
    # 构建配置
    print("\n构建发布包配置...")
    package_json = build_package_json(task_script, package_ref)
    print(f"  包名称：{package_json['packageName']}")
    print(f"  包描述：{package_json['packageDesc']}")
    
    task_catalogue_json = build_task_catalogue_json(catalogue_ref)
    print(f"  目录层级：{len(task_catalogue_json)} 层")
    
    # 查找 task.xls 模板
    task_xls_src = copy_task_xls()
    if task_xls_src:
        print(f"  task.xls 模板：{task_xls_src}")
    
    # 生成输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_BASE / f"package_{timestamp}"
    
    print(f"\n写入输出到：{output_dir}")
    write_output(output_dir, package_json, task_catalogue_json, task_xls_src, task_script)
    
    print("\n" + "=" * 60)
    print("生成成功!")
    print("=" * 60)
    print(f"\n📦 发布包位置：{output_dir}")
    print("\n下一步:")
    print("  在 DTStack 平台导入发布包即可执行 SQL 任务")
    
    return 0


if __name__ == "__main__":
    exit(main())
