# HdfsWriter Skill

## Description

HDFS/Hive 数据写入配置生成技能。读取 `hdfs_info.xlsx/csv` 中的数据结构配置信息，按照 DTStack/DTInsight 数据管道框架格式生成完整的 HDFS Writer 配置 JSON。

## Capabilities

- 读取 Excel/CSV 格式的 HDFS 配置信息
- 解析 Hive 连接参数（jdbc, username, password）
- 解析列定义（column.name, column.type）
- 自动生成 `fullColumnName`和`fullColumnType` 数组
- 生成符合 hdfs_writer.json 格式的配置
- 支持 HDFS_Writer.md 中的特殊参数配置
- 输出到 MysqlReader/resoult 目录

## Input Format

### hdfs_info.xlsx / hdfs_info.csv

```csv
dataSourceName,zy_test_HADOOP
dataSourceType,45
jdbc,jdbc:hive2://host:port/database
username,admin@dtstack.com
password,DTstack_PDSA
dtCenterSourceId,4007
sourceIds,2573
path,hdfs://ns1/dtInsight/hive/warehouse/zy_test.db/students
partition,pt=20260412
fileType,orc
column.name,id
column.type,int
column.name,name
column.type,string
column.name,age
column.type,int
defaultFS,hdfs://ns1
hadoopConfig,{...}
```

### CSV 字段说明

| 字段 | 描述 | 示例 |
|------|------|------|
| `dataSourceName` | 数据源名称 | `zy_test_HADOOP` |
| `dataSourceType` | 数据源类型 ID | `45` |
| `jdbc` | Hive JDBC 连接字符串 | `jdbc:hive2://...` |
| `username` | 用户名 | `admin@dtstack.com` |
| `password` | 密码 | `DTstack_PDSA` |
| `dtCenterSourceId` | DTCenter 数据源 ID | `4007` |
| `sourceIds` | 源 ID | `2573` |
| `path` | HDFS 存储路径 | `/user/hive/warehouse/...` |
| `partition` | 分区名称 | `pt=20260412` |
| `fileType` | 文件类型 | `orc`, `parquet`, `text` |
| `column.name` | 列名 | `id`, `name`, `age` |
| `column.type` | 列类型 | `int`, `string`, `bigint` |
| `defaultFS` | HDFS 默认文件系统 | `hdfs://ns1` |
| `hadoopConfig` | Hadoop 集群配置（JSON） | `{...}` |

## Output Format

### Generated JSON Structure

```json
{
  "writer": {
    "parameter": {
      "schema": "zy_test",
      "fileName": "pt=20260412",
      "dtCenterSourceId": 4007,
      "column": [
        {
          "customConverterType": "INT",
          "name": "id",
          "index": 0,
          "isPart": false,
          "type": "INT",
          "key": "id"
        }
      ],
      "dtCenterSourceIds": [4007],
      "writeMode": "overwrite",
      "encoding": "utf-8",
      "fullColumnName": ["id", "name", "age"],
      "dataSourceInfo": {
        "dataSourceName": "zy_test_HADOOP",
        "dataSourceType": 45
      },
      "path": "hdfs://ns1/dtInsight/hive/warehouse/zy_test.db/students",
      "password": "DTstack_PDSA",
      "partition": "pt=20260412",
      "hadoopConfig": {...},
      "defaultFS": "hdfs://ns1",
      "connection": [{
        "jdbcUrl": "jdbc:hive2://...",
        "table": ["students"]
      }],
      "table": "students",
      "fileType": "orc",
      "sourceIds": [2573],
      "username": "admin@dtstack.com",
      "fullColumnType": ["INT", "STRING", "INT"]
    },
    "name": "hdfswriter"
  }
}
```

### Special Parameters

#### fullColumnName / fullColumnType

这两个参数由脚本自动从 Excel/CSV 中的 `column.name`和`column.type` 字段生成：

- **fullColumnName**: 存放所有字段名称的数组
- **fullColumnType**: 存放所有字段类型的数组（大写）

```json
"fullColumnName": ["id", "name", "age"],
"fullColumnType": ["INT", "STRING", "INT"]
```

#### column 数组结构

每个字段包含以下属性：

| 属性 | 描述 | 示例 |
|------|------|------|
| `customConverterType` | 自定义转换器类型 | `INT`, `STRING` |
| `name` | 字段名称 | `id` |
| `index` | 字段索引（从 0 开始） | `0` |
| `isPart` | 是否为分区字段 | `false` |
| `type` | 字段类型 | `INT` |
| `key` | 字段键名 | `id` |

## Special Parameters (from HDFS_Writer.md)

### 必需参数

| 参数 | 描述 | 类型 |
|------|------|------|
| `defaultFS` | HDFS namenode 地址 | string |
| `fileType` | 文件类型（text/orc/parquet） | string |
| `path` | 数据文件路径 | string |
| `column` | 写入字段列表 | List |

### 可选参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `hadoopConfig` | 集群 HA 模式配置 | - |
| `fileName` | 写入目录名称 | - |
| `writeMode` | 写入模式（append/overwrite） | append |
| `fieldDelimiter` | 字段分隔符（text 模式） | \001 |
| `encoding` | 编码格式（text 模式） | UTF-8 |
| `fullColumnName` | 字段名称数组 | column.name 集合 |
| `fullColumnType` | 字段类型数组 | column.type 集合 |
| `compress` | 压缩类型 | - |
| `partition` | 分区配置 | - |

### Write Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `overwrite` | 覆盖目标表（先删除后写入） | 全量同步、重建表 |
| `append` | 追加到目标表 | 增量同步、追加数据 |

### File Types

| Type | Description | Compress Options |
|------|-------------|------------------|
| `text` | textfile 文件格式 | GZIP, BZIP2 |
| `orc` | orcfile 文件格式 | SNAPPY, ZLIB, LZO |
| `parquet` | parquet 文件格式 | SNAPPY, GZIP, LZO |

## Usage

### 运行脚本

```bash
python3 skills/TransferData/HdfsWriter/scripts/generate_config.py
```

### 输出位置

```
skills/TransferData/HdfsWriter/resoult/hdfs_writer_config.json
```

### 输入文件位置

脚本会自动检测以下路径：
- XLSX: `/mnt/c/Users/67461/Desktop/sync_test/model/hdfs_info.xlsx`
- CSV: `/mnt/c/Users/67461/Desktop/sync_test/model/hdfs_info.csv`

优先使用 XLSX，如不可用则回退到 CSV。

## Task Structure

### Core JSON Template

```json
{
  "taskInfo": {
    "name": "hdfs_writer_task",
    "taskType": 2,
    "engineType": 0,
    "projectId": 121
  },
  "sqlText": {
    "parser": {
      "targetMap": {
        "schema": "dt_batch3",
        "table": "bd_es_test",
        "writeMode": "overwrite",
        "path": "/user/hive/warehouse/dt_batch3.db/bd_es_test",
        "columns": [
          {"key": "hitrulecode", "type": "string"},
          {"key": "event_time", "type": "datetime"}
        ]
      },
      "setting": {
        "writerChannel": 1,
        "record": 100,
        "speed": -1
      }
    }
  }
}
```

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 写入失败 | HDFS 权限不足 | 检查 HDFS 目录权限和用户授权 |
| 连接超时 | NameNode 不可达 | 验证网络和 defaultFS 配置 |
| 类型转换错误 | 源/目标类型不兼容 | 检查 column.type 映射 |
| 解析失败 | CSV 格式错误 | 确保 column.name 和 column.type 成对出现 |

## Security Notes

- 凭证安全存储（不要将密码/密钥提交到版本控制）
- 生产环境使用 Kerberos 认证
- 启用 HDFS 加密传输（SSL/TLS）
- 使用最小权限的服务账户

## Related Files

- `SKILL.md` - This file
- `references/hdfs_writer.json` - 参考配置模板
- `references/HDFS_Writer.md` - 参数配置说明文档
- `scripts/generate_config.py` - 配置生成脚本

## Related Skills

- [MysqlReader](../MysqlReader/SKILL.md) - MySQL 数据读取配置
- [ParseSqlText](../ParseSqlText/SKILL.md) - SQL 文本解析与拼接
- [ParseScript](../ParseScript/SKILL.md) - Base64 编码与任务脚本生成

配合使用可实现 MySQL → Hive 完整数据同步流程。
