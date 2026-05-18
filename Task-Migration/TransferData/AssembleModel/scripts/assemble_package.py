#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
AssembleModel - DTStack Package Assembler

Reads generated task scripts from ParseScriptBase64 and assembles them into a DTStack deployable package.
Output: C:/Users/67461/Desktop/package_<timestamp>/

Reference: C:/Users/67461/Desktop/sync_model/sync_xd/
"""

import json
import shutil
import base64
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
OUTPUT_BASE = Path("/mnt/c/Users/67461/Desktop")

# Input: Task script from ParseScriptBase64 (data sync task)
PARSE_SCRIPT_RESOULT = Path(__file__).parent.parent.parent / "ParseScriptBase64" / "resoult" / "mysql2hive_script.json"

# Fallback to ParseScript/test_sql.json for SQL tasks (independent branch)
PARSE_SCRIPT_RESOULT_FALLBACK = Path(__file__).parent.parent.parent / "ParseScript" / "resoult" / "test_sql.json"

# Reference files (from sync_xd)
REF_PACKAGE_JSON = REFERENCES_DIR / "package.json"
REF_TASK_CATALOGUE = REFERENCES_DIR / "task_catalogue.json"
REF_TASK_XLS = REFERENCES_DIR / "task.xls"
REF_TASK_JSON = REFERENCES_DIR / "mysql2hive_task.json"


def read_task_script():
    """Read the generated task script from ParseScriptBase64 (primary) or ParseScript (fallback)"""
    # Try primary source first (data sync task)
    if PARSE_SCRIPT_RESOULT.exists():
        print(f"  读取主输入：{PARSE_SCRIPT_RESOULT}")
        with open(PARSE_SCRIPT_RESOULT, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Fallback to SQL task
    if PARSE_SCRIPT_RESOULT_FALLBACK.exists():
        print(f"  使用备用输入：{PARSE_SCRIPT_RESOULT_FALLBACK}")
        with open(PARSE_SCRIPT_RESOULT_FALLBACK, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"找不到任务脚本文件：{PARSE_SCRIPT_RESOULT} 或 {PARSE_SCRIPT_RESOULT_FALLBACK}")


def read_reference_task():
    """Read reference task JSON from sync_xd"""
    if REF_TASK_JSON.exists():
        with open(REF_TASK_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def extract_data_sources(task_script):
    """Extract data source info from task script"""
    data_sources = []
    seen_sources = set()
    
    try:
        sql_text = task_script.get("taskInfo", {}).get("sqlText", "")
        decoded = json.loads(base64.b64decode(sql_text).decode('utf-8'))
        
        # Extract from job config
        job_str = decoded.get("job", "{}")
        job = json.loads(job_str)
        content = job.get("job", {}).get("content", [])
        
        for item in content:
            # Reader data source
            reader = item.get("reader", {})
            reader_param = reader.get("parameter", {})
            reader_ds_info = reader_param.get("dataSourceInfo", {})
            ds_name = reader_ds_info.get("dataSourceName")
            ds_type = reader_ds_info.get("dataSourceType")
            if ds_name and ds_name not in seen_sources:
                data_sources.append({
                    "dataSourceName": ds_name,
                    "dataSourceType": ds_type
                })
                seen_sources.add(ds_name)
            
            # Writer data source
            writer = item.get("writer", {})
            writer_param = writer.get("parameter", {})
            writer_ds_info = writer_param.get("dataSourceInfo", {})
            ds_name = writer_ds_info.get("dataSourceName")
            ds_type = writer_ds_info.get("dataSourceType")
            if ds_name and ds_name not in seen_sources:
                data_sources.append({
                    "dataSourceName": ds_name,
                    "dataSourceType": ds_type
                })
                seen_sources.add(ds_name)
    except Exception as e:
        print(f"Warning: Could not extract data sources: {e}")
    
    return data_sources


def extract_engine_info(task_script):
    """Extract engine info from task script"""
    engine_list = []
    
    try:
        sql_text = task_script.get("taskInfo", {}).get("sqlText", "")
        decoded = json.loads(base64.b64decode(sql_text).decode('utf-8'))
        job_str = decoded.get("job", "{}")
        job = json.loads(job_str)
        content = job.get("job", {}).get("content", [])
        
        seen_engines = set()
        for item in content:
            writer = item.get("writer", {})
            writer_param = writer.get("parameter", {})
            schema = writer_param.get("schema")
            if schema and schema not in seen_engines:
                engine_list.append({
                    "engineType": 1,
                    "schema": schema
                })
                seen_engines.add(schema)
    except:
        engine_list = [{"engineType": 1, "schema": "zy_test"}]
    
    return engine_list


def build_package_json(task_script, timestamp):
    """Build package.json following sync_xd format"""
    data_sources = extract_data_sources(task_script)
    engine_list = extract_engine_info(task_script)
    
    # Read reference template
    ref_package = {}
    if REF_PACKAGE_JSON.exists():
        with open(REF_PACKAGE_JSON, 'r', encoding='utf-8') as f:
            ref_package = json.load(f)
    
    # Build package.json based on reference
    package_json = {
        "createTime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "createUser": ref_package.get("createUser", "admin@dtstack.com"),
        "dataSourceList": data_sources if data_sources else ref_package.get("dataSourceList", []),
        "engineList": engine_list if engine_list else ref_package.get("engineList", []),
        "packageDesc": ref_package.get("packageDesc", "1"),
        "packageName": f"package_{timestamp.strftime('%Y%m%d_%H%M%S')}",
        "projectName": ref_package.get("projectName", "zy_test"),
        "tenantName": ref_package.get("tenantName", "培训演示"),
        "userNameList": ref_package.get("userNameList", [])
    }
    
    return package_json


def build_task_catalogue(task_script):
    """Build task_catalogue.json following sync_xd format"""
    # Read reference template
    ref_catalogue = {}
    if REF_TASK_CATALOGUE.exists():
        with open(REF_TASK_CATALOGUE, 'r', encoding='utf-8') as f:
            ref_catalogue = json.load(f)
    
    # Get task info
    node_pid = task_script.get("taskInfo", {}).get("nodePid", 33357)
    project_id = task_script.get("taskInfo", {}).get("projectId", 695)
    tenant_id = task_script.get("taskInfo", {}).get("tenantId", 10719)
    
    # Build catalogue based on reference
    catalogue = {}
    for level, nodes in ref_catalogue.items():
        catalogue[level] = []
        for node in nodes:
            new_node = node.copy()
            new_node["projectId"] = project_id
            new_node["tenantId"] = tenant_id
            if node.get("nodeName") == "测试":
                new_node["id"] = node_pid
            catalogue[level].append(new_node)
    
    return catalogue


def build_task_json(task_script):
    """Build complete task JSON following sync_xd/mysql2hive.json format"""
    # Read reference task for structure
    ref_task = read_reference_task()
    
    if not ref_task:
        # Fallback to basic structure
        return task_script
    
    # Get existing task info from input
    task_info = task_script.get("taskInfo", {})
    ref_task_info = ref_task.get("taskInfo", {})
    
    # Build task JSON based on reference structure
    new_task_info = {
        "agentResourceId": ref_task_info.get("agentResourceId", 17),
        "appType": ref_task_info.get("appType", 1),
        "computeType": ref_task_info.get("computeType", 1),
        "createUserId": ref_task_info.get("createUserId", 1),
        "dependOnSettings": ref_task_info.get("dependOnSettings", 0),
        "dtuicTenantId": ref_task_info.get("dtuicTenantId", 0),
        "engineType": ref_task_info.get("engineType", 0),
        "exeArgs": ref_task_info.get("exeArgs", ""),
        "flowId": ref_task_info.get("flowId", 0),
        "id": ref_task_info.get("id", 0),
        "isDeleted": ref_task_info.get("isDeleted", 0),
        "isPublishToProduce": ref_task_info.get("isPublishToProduce", 0),
        "jobBuildType": ref_task_info.get("jobBuildType", 1),
        "mainClass": ref_task_info.get("mainClass", ""),
        "name": task_info.get("name", ref_task_info.get("name", "mysql2hive")),
        "nodePid": task_info.get("nodePid", ref_task_info.get("nodePid", 33357)),
        "ownerUserId": ref_task_info.get("ownerUserId", 1),
        "ownerUserName": ref_task_info.get("ownerUserName", "admin@dtstack.com"),
        "periodType": ref_task_info.get("periodType", 2),
        "projectId": task_info.get("projectId", ref_task_info.get("projectId", 695)),
        "projectScheduleStatus": ref_task_info.get("projectScheduleStatus", 0),
        "scheduleConf": ref_task_info.get("scheduleConf", "{\"isFailRetry\":true,\"beginDate\":\"2001-01-01\",\"min\":0,\"periodType\":\"2\",\"hour\":0,\"selfReliance\":0,\"endDate\":\"2121-01-01\",\"maxRetryNum\":\"3\"}"),
        "scheduleStatus": ref_task_info.get("scheduleStatus", 2),
        "sqlText": task_info.get("sqlText", ""),
        "submitStatus": ref_task_info.get("submitStatus", 1),
        "taskDesc": ref_task_info.get("taskDesc", ""),
        "taskGroup": ref_task_info.get("taskGroup", 0),
        "taskId": ref_task_info.get("taskId", 0),
        "taskParams": ref_task_info.get("taskParams", "pipeline.operator-chaining = false"),
        "taskType": ref_task_info.get("taskType", 2),
        "tenantId": task_info.get("tenantId", ref_task_info.get("tenantId", 10719)),
        "yarnResourceName": ref_task_info.get("yarnResourceName", "saas")
    }
    
    task_json = {
        "taskInfo": new_task_info,
        "updateEnvParam": task_script.get("updateEnvParam", False)
    }
    
    return task_json


def create_package(task_script, output_dir):
    """Create the complete package structure following sync_xd format"""
    timestamp = datetime.now()
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir = output_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    
    # Get task name from script
    task_info = task_script.get("taskInfo", {})
    task_name = task_info.get("name", "mysql2hive_script")
    
    # 1. Build and write complete task JSON (following sync_xd format)
    task_json = build_task_json(task_script)
    task_output = tasks_dir / f"{task_name}.json"
    with open(task_output, 'w', encoding='utf-8') as f:
        json.dump(task_json, f, ensure_ascii=False, separators=(',', ':'))
    print(f"  ✓ Created: {task_output}")
    
    # 2. Create package.json (following sync_xd format)
    package_json = build_package_json(task_script, timestamp)
    package_output = output_dir / "package.json"
    with open(package_output, 'w', encoding='utf-8') as f:
        json.dump(package_json, f, ensure_ascii=False, separators=(',', ':'))
    print(f"  ✓ Created: {package_output}")
    
    # 3. Create task_catalogue.json (following sync_xd format)
    task_catalogue = build_task_catalogue(task_script)
    catalogue_output = output_dir / "task_catalogue.json"
    with open(catalogue_output, 'w', encoding='utf-8') as f:
        json.dump(task_catalogue, f, ensure_ascii=False, separators=(',', ':'))
    print(f"  ✓ Created: {catalogue_output}")
    
    # 4. Copy task.xls from reference
    xls_output = output_dir / "task.xls"
    shutil.copy2(REF_TASK_XLS, xls_output)
    print(f"  ✓ Created: {xls_output}")
    
    # 5. Create empty error.log
    error_log = output_dir / "error.log"
    error_log.touch()
    print(f"  ✓ Created: {error_log}")
    
    return package_json["packageName"]


def main():
    print("=" * 60)
    print("AssembleModel - DTStack Package Assembler")
    print("=" * 60)
    
    # Check input file (try primary first, then fallback)
    if not PARSE_SCRIPT_RESOULT.exists() and not PARSE_SCRIPT_RESOULT_FALLBACK.exists():
        print(f"\n错误：找不到任务脚本文件")
        print(f"  主输入：{PARSE_SCRIPT_RESOULT}")
        print(f"  备用输入：{PARSE_SCRIPT_RESOULT_FALLBACK}")
        print(f"  请先运行相应的脚本生成配置:")
        print(f"    - 数据同步任务：运行 ParseScriptBase64")
        print(f"    - SQL 任务：运行 ParseScript")
        return 1
    
    print(f"\n读取任务脚本...")
    task_script = read_task_script()
    
    # Generate package name with timestamp
    timestamp = datetime.now()
    package_name = f"package_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    output_dir = OUTPUT_BASE / package_name
    
    print(f"\n创建发布包：{output_dir}")
    create_package(task_script, output_dir)
    
    print(f"\n{'=' * 60}")
    print(f"✅ 发布包生成成功!")
    print(f"   位置：{output_dir}")
    print(f"   名称：{package_name}")
    print(f"{'=' * 60}")
    
    return 0


if __name__ == "__main__":
    exit(main())
