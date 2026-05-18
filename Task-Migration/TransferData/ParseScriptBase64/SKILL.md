# ParseScript Skill

## Description

脚本解析与 Base64 加密技能。用于将 ParseSqlText 生成的 JSON 配置进行 Base64 编码，并封装到完整的 DTStack/DTInsight 任务脚本结构中。

## Capabilities

- 读取 ParseSqlText/resoult/sql_text.json
- 对 job 字段值进行 Base64 编码
- 生成完整的任务脚本 JSON 结构
- 支持 taskInfo、taskParams 等配置
- 输出到 ParseScript/resoult 目录

## Input/Output Structure

### Input

- `ParseSqlText/resoult/sql_text.json` - ParseSqlText 生成的 JSON 配置

### Output

```json
{
  "taskInfo": {
    "name": "mysql2hive_script",
    "taskType": 2,
    "engineType": 0,
    "projectId": 695
  },
  "sqlText": "<base64-encoded-json>",
  "updateEnvParam": true
}
```

## Task Structure

### Core JSON Template

```json
{
  "taskInfo": {
    "agentResourceId": 17,
    "appType": 1,
    "computeType": 1,
    "engineType": 0,
    "name": "mysql2hive_script",
    "projectId": 695,
    "taskType": 2,
    "sqlText": "eyJzeW5jTW9kZWwiOjAsImNyZWF0ZU1vZGVsIjoxLCJqb2IiOiI..."}
  },
  "updateEnvParam": true
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `taskInfo` | object | 任务基本信息 |
| `taskInfo.name` | string | 任务名称 |
| `taskInfo.taskType` | int | 任务类型 (2=数据同步) |
| `taskInfo.engineType` | int | 引擎类型 (0=Flink) |
| `taskInfo.projectId` | int | 项目 ID |
| `sqlText` | string | Base64 编码的完整 job 配置 JSON |
| `updateEnvParam` | boolean | 是否更新环境参数 |

### sqlText Encoding Process

1. 读取 ParseSqlText 生成的 JSON:
   ```json
   {"syncModel":0,"createModel":1,"job":"{\"job\":{\"content\":[...]}}"}
   ```

2. 将整个 JSON 对象转换为字符串

3. 进行 Base64 编码

4. 将编码后的字符串赋值给 `sqlText` 字段

## Usage

### 运行脚本

```bash
python3 skills/TransferData/ParseScript/scripts/parse_script.py
```

### 处理流程

1. 读取 `ParseSqlText/resoult/sql_text.json`
2. 将整个 JSON 对象转换为字符串
3. 对字符串进行 Base64 编码
4. 创建完整的任务配置结构
5. 将编码后的字符串放入 `sqlText` 字段
6. 输出到 `ParseScript/resoult/mysql2hive_script.json`

### 输入文件位置

```
skills/TransferData/ParseSqlText/resoult/sql_text.json
```

### 输出位置

```
skills/TransferData/ParseScript/resoult/mysql2hive_script.json
```

### taskParams 配置示例

```bash
## 任务运行方式：
## per_job:单独为任务创建 flink yarn session，适用于低频率，大数据量同步
## session：多个任务共用一个 flink yarn session，适用于高频率、小数据量同步
## flinkTaskRunMode=per_job
## per_job 模式下 jobManager 配置的内存大小，默认 1024（单位 M)
## jobmanager.memory.mb=1024
## per_job 模式下 taskManager 配置的内存大小，默认 1024（单位 M）
## taskmanager.memory.mb=1024
## per_job 模式下每个 taskManager 对应 slot 的数量
## slots=1

## checkpoint 保存时间间隔
## flink.checkpoint.interval=300000
## 任务优先级，范围:1-1000
pipeline.operator-chaining = false
```

### scheduleConf 配置示例

```json
{
  "isFailRetry": true,
  "beginDate": "2001-01-01",
  "endDate": "2121-01-01",
  "periodType": "2",
  "hour": 0,
  "min": 0,
  "maxRetryNum": "3",
  "selfReliance": 0
}
```

## Example

### 输入 (sql_text.json)

```json
{
  "syncModel": 0,
  "createModel": 1,
  "job": "{\"job\":{\"content\":[{\"reader\":{...},\"writer\":{...}}]}}"
}
```

### 输出 (mysql2hive_script.json)

```json
{
  "taskInfo": {
    "name": "mysql2hive_script",
    "taskType": 2,
    "engineType": 0,
    "projectId": 695,
    "sqlText": "eyJzeW5jTW9kZWwiOjAsImNyZWF0ZU1vZGVsIjoxLCJqb2IiOiJ7XCJqb2JcIjp7XCJjb250ZW50XCI6W3tcInJlYWRlclwiOntcInBhcmFtZXRlclwiOnt...\n"
  },
  "updateEnvParam": true
}
```

## Related Skills

| Skill | 作用 | 输入 | 输出 |
|-------|------|------|------|
| [MysqlReader](../MysqlReader/SKILL.md) | MySQL 读取配置 | mysql_info.xlsx | mysql_reader_config.json |
| [HdfsWriter](../HdfsWriter/SKILL.md) | HDFS 写入配置 | hdfs_info.xlsx | hdfs_writer_config.json |
| [ParseSqlText](../ParseSqlText/SKILL.md) | 配置拼接 | 以上两个 JSON | sql_text.json |
| **ParseScript** | **Base64 编码封装** | **sql_text.json** | **mysql2hive_script.json** |

## Files

- `SKILL.md` - This file
- `references/mysql2hive_script.json` - 参考配置模板
- `scripts/parse_script.py` - Base64 编码脚本
- `resoult/mysql2hive_script.json` - 生成的任务脚本

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到 sql_text.json | ParseSqlText 未运行 | 先运行 ParseSqlText 脚本 |
| Base64 编码失败 | JSON 格式错误 | 检查输入 JSON 是否有效 |
| 输出目录不存在 | resoult 目录未创建 | 脚本会自动创建 |

## Complete Flow

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
│  4️⃣  ParseScript  ← 本步骤                                   │
│      Base64 编码 → mysql2hive_script.json                   │
│                                                             │
│  5️⃣  提交到 DTStack 平台执行                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
