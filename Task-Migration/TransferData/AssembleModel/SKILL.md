# AssembleModel Skill

## Description

DTStack 发布包组装技能。读取 ParseScript 生成的任务脚本，组装成 DTStack 平台可发布的完整目录结构。

## Capabilities

- 读取 ParseScriptBase64/resoult/mysql2hive_script.json（主要输入）
- 读取 ParseScript/resoult/test_sql.json（备用输入，用于 SQL 任务）
- 生成 package.json 包配置
- 生成 task_catalogue.json 任务目录配置
- 复制 task.xls 模板文件
- 创建 tasks 子目录并放置任务脚本
- 输出到 Windows Desktop，文件夹命名：package_时间戳

## Input/Output Structure

### Input

**主要输入（数据同步任务）:**
- `ParseScriptBase64/resoult/mysql2hive_script.json` - ParseScriptBase64 生成的 Base64 编码任务脚本

**备用输入（SQL 任务）:**
- `ParseScript/resoult/test_sql.json` - ParseScript 生成的 SQL 任务脚本

**参考模板:**
- `references/package.json` - 包配置模板
- `references/task_catalogue.json` - 任务目录模板
- `references/task.xls` - 任务 Excel 模板

### Output

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
├── package.json           # 包配置
├── task_catalogue.json    # 任务目录结构
├── task.xls              # 任务 Excel
├── error.log             # 错误日志 (空)
└── tasks/
    └── mysql2hive_script.json  # 任务脚本
```

## Package Structure

### 目录结构说明

| 文件/目录 | 说明 | 来源 |
|-----------|------|------|
| `package.json` | 包配置信息（数据源、引擎、项目等） | 动态生成 |
| `task_catalogue.json` | 任务目录树结构 | 动态生成 |
| `task.xls` | 任务信息 Excel | 从 references 复制 |
| `error.log` | 错误日志文件 | 创建空文件 |
| `tasks/` | 任务脚本目录 | 创建 |
| `tasks/mysql2hive_script.json` | Base64 编码的任务脚本 | 从 ParseScript 复制 |

### package.json 结构

```json
{
  "createTime": "2026-04-13 19:14:00",
  "createUser": "admin@dtstack.com",
  "dataSourceList": [
    {"dataSourceName": "zy_test_MYSQL", "dataSourceType": 1},
    {"dataSourceName": "zy_test_HADOOP", "dataSourceType": 45}
  ],
  "engineList": [
    {"engineType": 1, "schema": "zy_test"}
  ],
  "packageDesc": "1",
  "packageName": "package_20260413_191400",
  "projectName": "zy_test",
  "tenantName": "培训演示",
  "userNameList": []
}
```

### task_catalogue.json 结构

```json
{
  "0": [{
    "nodeName": "周期任务",
    "level": 0,
    "nodePid": 0,
    "id": 31153
  }],
  "1": [{
    "nodeName": "任务开发",
    "level": 1,
    "nodePid": 31153,
    "id": 31155
  }],
  "2": [{
    "nodeName": "测试",
    "level": 2,
    "nodePid": 31155,
    "id": 33357
  }]
}
```

## Usage

### 运行脚本

```bash
python3 skills/TransferData/AssembleModel/scripts/assemble_package.py
```

### 输出位置

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
```

### 文件夹命名规则

```
package_当前时间戳
```

示例：`package_20260413_191400`

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              AssembleModel 工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取 ParseScript/resoult/mysql2hive_script.json         │
│                                                             │
│  2. 解析任务脚本中的数据源信息                               │
│     - dataSourceName                                        │
│     - dataSourceType                                        │
│     - schema                                                │
│                                                             │
│  3. 生成 package.json                                       │
│     - createTime                                            │
│     - packageName (package_时间戳)                          │
│     - dataSourceList                                        │
│     - engineList                                            │
│                                                             │
│  4. 生成 task_catalogue.json                                │
│     - 周期任务 (level 0)                                    │
│     - 任务开发 (level 1)                                    │
│     - 测试 (level 2)                                        │
│                                                             │
│  5. 复制 task.xls 模板                                      │
│                                                             │
│  6. 创建 tasks/ 目录并放置任务脚本                           │
│                                                             │
│  7. 创建空 error.log 文件                                   │
│                                                             │
│  8. 输出到 C:/Users/67461/Desktop/package_时间戳/            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Example

### 输入文件

**ParseScript/resoult/mysql2hive_script.json:**
```json
{
  "taskInfo": {
    "name": "mysql2hive_script",
    "sqlText": "eyJzeW5jTW9kZWwiOjAsImNyZWF0ZU1vZGVsIjoxLCJqb2IiOiI...",
    "nodePid": 33357,
    "projectId": 695,
    "tenantId": 10719
  },
  "updateEnvParam": true
}
```

### 输出目录

```
C:/Users/67461/Desktop/package_20260413_191400/
├── package.json
├── task_catalogue.json
├── task.xls
├── error.log
└── tasks/
    └── mysql2hive_script.json
```

## Related Skills

| Skill | 作用 | 输出 |
|-------|------|------|
| [MysqlReader](../MysqlReader/SKILL.md) | MySQL 读取配置 | mysql_reader_config.json |
| [HdfsWriter](../HdfsWriter/SKILL.md) | HDFS 写入配置 | hdfs_writer_config.json |
| [ParseSqlText](../ParseSqlText/SKILL.md) | 配置拼接 | sql_text.json |
| [ParseScript](../ParseScript/SKILL.md) | Base64 编码封装 | mysql2hive_script.json |
| **AssembleModel** | **发布包组装** | **package_时间戳/** |

## Files

- `SKILL.md` - This file
- `references/package.json` - 包配置模板
- `references/task_catalogue.json` - 任务目录模板
- `references/task.xls` - 任务 Excel 模板
- `scripts/assemble_package.py` - 组装脚本
- `resoult/` - 临时输出目录（可选）

## Complete TransferData Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  TransferData 完整流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣  MysqlReader                                            │
│      mysql_info.xlsx → mysql_reader_config.json             │
│                                                             │
│  2️⃣  HdfsWriter                                             │
│      hdfs_info.xlsx → hdfs_writer_config.json               │
│                                                             │
│  3️⃣  ParseSqlText                                           │
│      拼接 → sql_text.json                                   │
│                                                             │
│  4️⃣  ParseScript                                            │
│      Base64 编码 → mysql2hive_script.json                   │
│                                                             │
│  5️⃣  AssembleModel  ← 最后一步                               │
│      组装发布包 → package_时间戳/                            │
│                                                             │
│  6️⃣  在 DTStack 平台导入发布包                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到任务脚本 | ParseScript 未运行 | 先运行 ParseScript 脚本 |
| 输出目录无法创建 | Windows 路径权限问题 | 检查 C 盘访问权限 |
| 数据源解析失败 | sqlText 解码错误 | 检查 Base64 编码是否有效 |
