# ParseSqlText Skill

## Description

SQL 文本解析与拼接技能。用于将 MySQL Reader 配置和 HDFS Writer 配置拼接成完整的同步任务 JSON 结构，生成符合 DTStack/DTInsight 框架的 job 配置。

## Capabilities

- 读取 MysqlReader/resoult/mysql_reader_config.json
- 读取 HdfsWriter/resoult/hdfs_writer_config.json
- 读取 Parser/resoult/parser.json
- 将 reader 和 writer 拼接为 job.content 数组
- 从 Parser 配置中提取 setting 参数
- 生成完整的 sql_text.json 结构
- 自动处理 job 字段的字符串化转义
- 添加 setting 配置（restore, errorLimit, speed）

## Input/Output Structure

### Input

- `MysqlReader/resoult/mysql_reader_config.json` - MySQL 源读取配置
- `HdfsWriter/resoult/hdfs_writer_config.json` - HDFS/Hive 目标写入配置
- `Parser/resoult/parser.json` - 数据同步映射配置（提供 setting 参数）

### Output

```json
{
  "job": {
    "content": [
      {
        "reader": { /* MySQL Reader 完整配置 */ },
        "writer": { /* HDFS Writer 完整配置 */ }
      }
    ],
    "setting": {
      "restore": {...},
      "errorLimit": {...},
      "speed": {...}
    }
  }
}
```

### Output Structure Explanation

| Field | Description | Source |
|-------|-------------|--------|
| `job.content` | 任务内容数组 | MysqlReader + HdfsWriter |
| `job.content[0].reader` | Reader 配置 | MysqlReader |
| `job.content[0].writer` | Writer 配置 | HdfsWriter |
| `job.setting` | 任务运行参数 | Parser.setting |
| `job.setting.restore` | 断点续传配置 | 自动生成 |
| `job.setting.errorLimit` | 错误记录限制 | Parser.setting.record |
| `job.setting.speed` | 速度控制 | Parser.setting.readerChannel/writerChannel |

## Task Structure

### Core JSON Template

```json
{
  "syncModel": 0,
  "createModel": 1,
  "job": "{\"job\":{\"content\":[{\"reader\":{\"parameter\":{...},\"name\":\"mysqlreader\"},\"writer\":{\"parameter\":{...},\"name\":\"hdfswriter\"}}],\"setting\":{\"restore\":{...},\"errorLimit\":{...},\"speed\":{...}}}}"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `syncModel` | int | 同步模式 (0=全量，1=增量) |
| `createModel` | int | 创建模式 (1=新建任务) |
| `job` | string | 字符串化的完整 job 配置 JSON |

### Job Content Structure

```json
{
  "job": {
    "content": [
      {
        "reader": {
          "parameter": { /* MySQL Reader 配置 */ },
          "name": "mysqlreader"
        },
        "writer": {
          "parameter": { /* HDFS Writer 配置 */ },
          "name": "hdfswriter"
        }
      }
    ],
    "setting": {
      "restore": {
        "maxRowNumForCheckpoint": 0,
        "isRestore": false,
        "restoreColumnName": "",
        "restoreColumnIndex": 0
      },
      "errorLimit": {
        "record": 100
      },
      "speed": {
        "readerChannel": 1,
        "writerChannel": 1,
        "bytes": 0,
        "channel": 1
      }
    }
  }
}
```

## Usage

### 拼接流程

1. 读取 `MysqlReader/resoult/mysql_reader_config.json`
2. 读取 `HdfsWriter/resoult/hdfs_writer_config.json`
3. 读取 `Parser/resoult/parser.json`
4. 提取 reader 和 writer 配置
5. 组合到 job.content 数组
6. 从 Parser 提取 setting 配置（readerChannel, writerChannel, record 等）
7. 生成最终的 sql_text.json 结构

### 运行脚本

```bash
python3 skills/TransferData/ParseSqlText/scripts/parse_sql_text.py
```

### 输出位置

```
skills/TransferData/ParseSqlText/resoult/sql_text.json
```

### 配置项说明

**syncModel:**
- `0` - 全量同步（每次完整复制）
- `1` - 增量同步（仅同步变化数据）

**createModel:**
- `1` - 新建任务模式

**setting.restore:**
- `isRestore` - 是否启用断点续传
- `maxRowNumForCheckpoint` - 检查点最大行数
- `restoreColumnName` - 续传列名
- `restoreColumnIndex` - 续传列索引

**setting.errorLimit:**
- `record` - 错误记录数限制（默认 100）

**setting.speed:**
- `readerChannel` - 读取并行度
- `writerChannel` - 写入并行度
- `bytes` - 速度限制 (0=无限制)
- `channel` - 总通道数

## Example

### 输入文件

**mysql_reader_config.json:**
```json
{
  "reader": {
    "parameter": {
      "connection": [{
        "jdbcUrl": ["jdbc:mysql://host:3306/db"],
        "table": ["table_name"],
        "username": "user",
        "password": "pass"
      }],
      "column": [{"key": "id", "type": "INT"}],
      "dataSourceInfo": {"dataSourceName": "source_mysql"}
    },
    "name": "mysqlreader"
  }
}
```

**hdfs_writer_config.json:**
```json
{
  "writer": {
    "parameter": {
      "path": "hdfs://ns1/path/to/table",
      "schema": "target_db",
      "table": "target_table",
      "writeMode": "overwrite",
      "column": [{"key": "id", "type": "int"}],
      "dataSourceInfo": {"dataSourceName": "target_hadoop"}
    },
    "name": "hdfswriter"
  }
}
```

### 输出文件

**sql_text.json:**
```json
{
  "syncModel": 0,
  "createModel": 1,
  "job": "{\"job\":{\"content\":[{\"reader\":{\"parameter\":{...},\"name\":\"mysqlreader\"},\"writer\":{\"parameter\":{...},\"name\":\"hdfswriter\"}}],\"setting\":{\"restore\":{\"isRestore\":false},\"errorLimit\":{\"record\":100},\"speed\":{\"readerChannel\":1,\"writerChannel\":1}}}}"
}
```

## Data Flow

```
┌─────────────────┐         ┌─────────────────┐
│  MysqlReader    │         │  HdfsWriter     │
│  resoult/       │         │  resoult/       │
│  mysql_reader_  │         │  hdfs_writer_   │
│  config.json    │         │  config.json    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │      Parser            │
         │      resoult/          │
         │      parser.json       │
         └───────────┬────────────┘
                     │
              ┌──────▼──────┐
              │ ParseSqlText│
              │             │
              │ 拼接 reader │
              │ + writer    │
              │ + setting   │
              │ (from Parser)│
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  resoult/   │
              │ sql_text.   │
              │ json        │
              └─────────────┘
```

## Related Skills

| Skill | 作用 | 输入 | 输出 |
|-------|------|------|------|
| [MysqlReader](../MysqlReader/SKILL.md) | MySQL 读取配置 | hdfs_info.xlsx | mysql_reader_config.json |
| [HdfsWriter](../HdfsWriter/SKILL.md) | HDFS 写入配置 | hdfs_info.xlsx | hdfs_writer_config.json |
| **ParseSqlText** | **配置拼接** | **以上两个 JSON** | **sql_text.json** |
| [ParseScript](../ParseScript/SKILL.md) | Base64 编码封装 | sql_text.json | mysql2hive_script.json |

## Files

- `SKILL.md` - This file
- `references/` - Reference examples (sql_text.json)
- `scripts/parse_sql_text.py` - Main parsing and merging script
- `resoult/` - Output directory for generated config

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到输入文件 | MysqlReader/HdfsWriter 未运行 | 先运行前序 skill 生成配置 |
| JSON 解析失败 | 输入文件格式错误 | 检查输入 JSON 是否有效 |
| 字段不匹配 | reader/writer 字段不一致 | 确保源和目标字段类型兼容 |
