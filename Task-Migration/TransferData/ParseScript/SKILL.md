# ParseScript Skill

## Description

SQL 脚本生成技能。读取 sql.txt 和 task_task_info.csv 文件，生成 DTStack/DTInsight 任务脚本配置。

## Capabilities

- 读取 sql.txt 中的 SQL 内容
- 读取 task_task_info.csv 中的任务依赖关系
- 生成完整的任务脚本 JSON 结构
- 自动添加 SQL 头部注释（任务名、类型、作者、时间、描述）
- 支持任务依赖配置
- 输出到 ParseScript/resoult 目录

## Input Files

### 1. sql.txt

路径：`C:/Users/67461/Desktop/sync_model/model/sql.txt`

内容示例：
```sql
select * from students
```

### 2. task_task_info.csv

路径：`C:/Users/67461/Desktop/sync_model/model/task_task_info.csv`

格式：
```csv
customOffset,forwardDirection,isCurrentProject,projectAlias,taskName,taskType,upDownRelyType
0,1,TRUE,JSZC_DEMO,node1,44,0
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `customOffset` | int | 自定义偏移量 |
| `forwardDirection` | int | 正向依赖方向 (1=正向) |
| `isCurrentProject` | bool | 是否当前项目 |
| `projectAlias` | string | 项目别名 |
| `taskName` | string | 依赖的任务名称 |
| `taskType` | int | 任务类型 |
| `upDownRelyType` | int | 上下依赖类型 (0=无) |

## Output Format

### Generated JSON Structure

```json
{
  "taskInfo": {
    "name": "test_sparksql",
    "engineType": 1,
    "taskType": 0,
    "projectId": 695,
    "sqlText": "-- name test_sparksql\n-- type Spark SQL\n-- author admin@dtstack.com\n-- create time 2026-04-27 23:45:00\n-- desc \nselect * from students",
    ...
  },
  "taskTaskInfo": [
    {
      "customOffset": 0,
      "forwardDirection": 1,
      "isCurrentProject": true,
      "projectAlias": "zy_test",
      "taskName": "mysql2hive",
      "taskType": 2,
      "upDownRelyType": 0
    }
  ],
  "updateEnvParam": false
}
```

### sqlText Format

SQL 内容会自动添加头部注释：

```sql
-- name <task_name>
-- type Spark SQL
-- author admin@dtstack.com
-- create time <timestamp>
-- desc 
<sql_content>
```

## Usage

### 运行脚本

```bash
python3 skills/TransferData/ParseScriptV2/scripts/generate_config.py
```

### 输出位置

```
skills/TransferData/ParseScriptV2/resoult/test_sql.json
```

## Task Structure

### taskInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | 任务名称 |
| `engineType` | int | 引擎类型 (1=Spark) |
| `taskType` | int | 任务类型 (0=SQL 任务) |
| `projectId` | int | 项目 ID |
| `sqlText` | string | SQL 脚本内容（含头部注释） |
| `scheduleConf` | string | 调度配置（JSON 字符串） |
| `taskParams` | string | 任务参数（Spark 配置） |

### taskTaskInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `customOffset` | int | 自定义偏移量 |
| `forwardDirection` | int | 依赖方向 |
| `isCurrentProject` | bool | 是否当前项目 |
| `projectAlias` | string | 项目别名 |
| `taskName` | string | 依赖任务名称 |
| `taskType` | int | 依赖任务类型 |
| `upDownRelyType` | int | 上下依赖类型 |

## Example

### 输入文件

**sql.txt:**
```sql
select * from students
```

**task_task_info.csv:**
```csv
customOffset,forwardDirection,isCurrentProject,projectAlias,taskName,taskType,upDownRelyType
0,1,TRUE,JSZC_DEMO,node1,44,0
```

### 输出文件

**test_sql.json:**
```json
{
  "taskInfo": {
    "name": "test_sparksql",
    "sqlText": "-- name test_sparksql\n-- type Spark SQL\n-- author admin@dtstack.com\n-- create time 2026-04-27 23:45:00\n-- desc \nselect * from students",
    ...
  },
  "taskTaskInfo": [
    {
      "taskName": "node1",
      "taskType": 44,
      ...
    }
  ],
  "updateEnvParam": false
}
```

## Related Files

- `SKILL.md` - This file
- `references/test_sparksql.json` - 参考配置模板
- `scripts/generate_config.py` - 配置生成脚本
- `resoult/test_sql.json` - 生成的输出文件

## Related Skills

| Skill | 作用 |
|-------|------|
| [MysqlReader](../MysqlReader/SKILL.md) | MySQL 读取配置生成 |
| [HdfsWriter](../HdfsWriter/SKILL.md) | HDFS 写入配置生成 |
| [Parser](../Parser/SKILL.md) | 数据同步映射配置 |
| [ParseSqlText](../ParseSqlText/SKILL.md) | SQL 文本拼接 |
| [ParseScript](../ParseScript/SKILL.md) | Base64 编码任务脚本 |
| [AssembleModel](../AssembleModel/SKILL.md) | 发布包组装 |
