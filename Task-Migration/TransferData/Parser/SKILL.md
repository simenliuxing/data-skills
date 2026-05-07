# Parser Skill

## Description

Parser 技能用于整合 MysqlReader 和 HdfsWriter 的输出配置，生成统一的数据同步任务配置文件。该技能读取两个上游技能的输出结果，按照 DTStack/DTInsight 数据管道框架格式生成 parser.json 配置文件。

## Capabilities

- 读取 MysqlReader 的输出配置 (`mysql_reader_config.json`)
- 读取 HdfsWriter 的输出配置 (`hdfs_writer_config.json`)
- 整合源和目标数据源信息
- 生成字段映射关系 (keymap)
- 自动识别分区字段
- 生成符合 parser.json 模板的配置
- 输出到 Parser/resoult 目录

## Input Files

### 1. MysqlReader Output

路径：`../MysqlReader/resoult/mysql_reader_config.json`

包含 MySQL 数据源的读取配置：
- 数据源信息 (dataSourceName, dataSourceType)
- 连接信息 (jdbcUrl, schema, table)
- 字段列表 (column)

### 2. HdfsWriter Output

路径：`../HdfsWriter/resoult/hdfs_writer_config.json`

包含 HDFS/Hive 数据源的写入配置：
- 数据源信息 (dataSourceName, dataSourceType)
- 连接信息 (jdbcUrl, schema, table, path)
- 字段列表 (column)
- 分区信息 (partition)
- Hadoop 配置 (hadoopConfig)

### 3. Reference Template

路径：`references/parser.json`

参考模板，提供输出格式和默认值。

## Output Format

### Generated JSON Structure

```json
{
  "targetMap": {
    "sourceId": 2573,
    "name": "zy_test_HADOOP",
    "column": [
      {"part": false, "comment": "", "isPart": false, "type": "int", "key": "id"},
      {"part": false, "comment": "", "isPart": false, "type": "string", "key": "name"},
      {"part": false, "comment": "", "isPart": false, "type": "int", "key": "age"},
      {"part": true, "isPart": true, "type": "string", "key": "pt"}
    ],
    "schema": "zy_test",
    "type": {
      "partition": "pt=20260412",
      "writeMode": "overwrite",
      "type": 45,
      "table": "students"
    },
    "extralConfig": ""
  },
  "keymap": {
    "source": [
      {"comment": "", "isPart": false, "type": "INT", "key": "id"},
      {"precision": 100, "comment": "", "isPart": false, "type": "VARCHAR", "key": "name"},
      {"comment": "", "isPart": false, "type": "INT", "key": "age"}
    ],
    "target": [
      {"comment": "", "isPart": false, "type": "int", "key": "id"},
      {"comment": "", "isPart": false, "type": "string", "key": "name"},
      {"comment": "", "isPart": false, "type": "int", "key": "age"}
    ]
  },
  "sourceMap": {
    "sourceId": 2579,
    "schema": "zy_test",
    "sourceList": [{
      "sourceId": 2579,
      "schema": "zy_test",
      "tables": ["students"],
      "name": "zy_test_MYSQL",
      "type": 1,
      "key": "main"
    }],
    "name": "zy_test_MYSQL",
    "column": [
      {"part": false, "comment": "", "isPart": false, "type": "INT", "key": "id"},
      {"part": false, "precision": 100, "comment": "", "isPart": false, "type": "VARCHAR(100) ", "key": "name"},
      {"part": false, "comment": "", "isPart": false, "type": "INT", "key": "age"}
    ],
    "type": {
      "type": 1,
      "table": ["students"]
    },
    "extralConfig": ""
  },
  "setting": {
    "readerChannel": 1,
    "init": false,
    "writerChannel": 1,
    "record": 100,
    "restoreColumnIndex": 0,
    "speed": "-1",
    "isSaveDirty": 0
  }
}
```

### JSON Structure Explanation

#### targetMap (目标数据源映射)

| 字段 | 描述 | 来源 |
|------|------|------|
| `sourceId` | 数据源 ID | HdfsWriter.sourceIds |
| `name` | 数据源名称 | HdfsWriter.dataSourceInfo.dataSourceName |
| `column` | 字段列表 (包含分区字段) | HdfsWriter.column |
| `schema` | 数据库/模式名 | HdfsWriter.schema |
| `type.partition` | 分区配置 | HdfsWriter.partition |
| `type.writeMode` | 写入模式 | HdfsWriter.writeMode |
| `type.type` | 数据源类型 ID | HdfsWriter.dataSourceInfo.dataSourceType |
| `type.table` | 表名 | HdfsWriter.table |

#### sourceMap (源数据源映射)

| 字段 | 描述 | 来源 |
|------|------|------|
| `sourceId` | 数据源 ID | MysqlReader.connection.sourceId |
| `schema` | 数据库名 | MysqlReader.connection.schema |
| `sourceList` | 数据源列表 | 从 MysqlReader 构建 |
| `name` | 数据源名称 | MysqlReader.dataSourceInfo.dataSourceName |
| `column` | 字段列表 | MysqlReader.column |
| `type.type` | 数据源类型 ID | MysqlReader.dataSourceInfo.dataSourceType |
| `type.table` | 表名 | MysqlReader.connection.table |

#### keymap (字段映射)

| 字段 | 描述 |
|------|------|
| `source` | 源字段列表 (来自 MySQL) |
| `target` | 目标字段列表 (来自 HDFS，排除分区字段) |

#### setting (任务设置)

| 字段 | 描述 | 默认值 |
|------|------|--------|
| `readerChannel` | 读取并发数 | 1 |
| `writerChannel` | 写入并发数 | 1 |
| `record` | 错误记录限制 | 100 |
| `speed` | 速度限制 (-1 表示不限速) | "-1" |
| `init` | 是否初始化 | false |
| `restoreColumnIndex` | 恢复字段索引 | 0 |
| `isSaveDirty` | 是否保存脏数据 | 0 |

## Column Type Mapping

### MySQL → HDFS/Hive 类型转换

| MySQL Type | HDFS/Hive Type |
|------------|----------------|
| INT | int |
| VARCHAR | string |
| BIGINT | bigint |
| DATETIME | string |
| TEXT | string |
| DECIMAL | decimal |

### Special Handling

- **VARCHAR 类型**: 在 source 中添加 `precision: 100`
- **分区字段**: 在 targetMap.column 中标记 `isPart: true`，在 keymap.target 中排除

## Usage

### 运行脚本

```bash
python3 skills/TransferData/Parser/scripts/generate_config.py
```

### 前置条件

1. 确保 MysqlReader 已运行并生成输出：
   ```
   skills/TransferData/MysqlReader/resoult/mysql_reader_config.json
   ```

2. 确保 HdfsWriter 已运行并生成输出：
   ```
   skills/TransferData/HdfsWriter/resoult/hdfs_writer_config.json
   ```

### 输出位置

```
skills/TransferData/Parser/resoult/parser.json
```

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐
│  MysqlReader    │     │  HdfsWriter     │
│  mysql_reader_  │     │  hdfs_writer_   │
│  config.json    │     │  config.json    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   Parser    │
              │  Skill      │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  parser.json│
              └─────────────┘
```

## Related Files

- `SKILL.md` - This file
- `references/parser.json` - 参考配置模板
- `scripts/generate_config.py` - 配置生成脚本

## Related Skills

- [MysqlReader](../MysqlReader/SKILL.md) - MySQL 数据读取配置
- [HdfsWriter](../HdfsWriter/SKILL.md) - HDFS/Hive 数据写入配置
- [ParseSqlText](../ParseSqlText/SKILL.md) - SQL 文本解析与拼接
- [ParseScript](../ParseScript/SKILL.md) - Base64 编码与任务脚本生成
- [AssembleModel](../AssembleModel/SKILL.md) - 任务模型组装

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到输入文件 | MysqlReader/HdfsWriter 未运行 | 先运行上游技能生成输出 |
| 字段数量不匹配 | 源和目标字段不一致 | 检查 MySQL 和 Hive 表结构 |
| 类型转换错误 | 不支持的类型映射 | 添加类型映射规则 |
| 分区字段缺失 | table_info 未定义分区 | 在 CREATE TABLE SQL 中添加 PARTITIONED BY |

## Example

### 输入：MySQL → Hive 数据同步

**源表 (MySQL):**
```sql
CREATE TABLE students (
    id INT,
    name VARCHAR(100),
    age INT
);
```

**目标表 (Hive):**
```sql
CREATE TABLE students (
    id INT,
    name STRING,
    age INT,
    pt STRING
) PARTITIONED BY (pt);
```

**输出 parser.json:**
- sourceMap.column: [id, name, age]
- targetMap.column: [id, name, age, pt] (包含分区字段)
- keymap.target: [id, name, age] (排除分区字段)
