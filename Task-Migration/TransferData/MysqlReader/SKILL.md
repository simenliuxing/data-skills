# MysqlReader Skill

## Description

MySQL 数据读取配置生成技能。读取 `mysql_info.xlsx` 中的数据库连接和字段配置信息，按照 DTStack/DTInsight 数据管道框架格式生成完整的 MySQL Reader 配置 JSON。

## Capabilities

- 读取 Excel 格式的数据库配置信息
- 解析 JDBC 连接参数（url, username, password）
- 解析列定义（column.name, column.type）
- 自动生成 schema 和 table 名称
- 生成符合 mysql_reader.json 格式的配置
- 支持 MySQL_Reader.md 中的特殊参数配置
- 输出到本地 resoult 目录

## Input Format

### mysql_info.xlsx

| A 列 (Key) | B 列 (Value) |
|------------|-------------|
| dataSourceName | zy_test_MYSQL |
| jdbc | jdbc:mysql://host:port/database?params |
| username | drpeco |
| password | DT#passw0rd2024 |
| dtCenterSourceId | 4013 |
| sourceIds | 2579 |
| column.name | id |
| column.type | INT |
| column.name | name |
| column.type | VARCHAR |
| column.name | age |
| column.type | INT |

### Excel 字段说明

| 字段 | 描述 | 示例 |
|------|------|------|
| `dataSourceName` | 数据源名称 | `zy_test_MYSQL` |
| `jdbc` | JDBC 连接字符串 | `jdbc:mysql://...` |
| `username` | 数据库用户名 | `drpeco` |
| `password` | 数据库密码 | `DT#passw0rd2024` |
| `dtCenterSourceId` | DTCenter 数据源 ID | `4013` |
| `sourceIds` | 源 ID | `2579` |
| `column.name` | 列名 | `id`, `name`, `age` |
| `column.type` | 列类型 | `INT`, `VARCHAR` |

## Output Format

### Generated JSON Structure

```json
{
  "reader": {
    "parameter": {
      "password": "DT#passw0rd2024",
      "customSql": "",
      "startLocation": "",
      "dtCenterSourceId": 4013,
      "increColumn": "",
      "column": [
        {
          "customConverterType": "INT",
          "name": "id",
          "isPart": false,
          "type": "INT",
          "key": "id"
        }
      ],
      "dtCenterSourceIds": [4013],
      "connection": [{
        "schema": "zy_test",
        "sourceId": 2579,
        "password": "DT#passw0rd2024",
        "jdbcUrl": ["jdbc:mysql://..."],
        "type": 1,
        "table": ["students"],
        "username": "drpeco"
      }],
      "sourceIds": [2579],
      "username": "drpeco",
      "dataSourceInfo": {
        "dataSourceName": "zy_test_MYSQL",
        "dataSourceType": 1
      }
    },
    "name": "mysqlreader"
  }
}
```

### Column Structure

每个字段包含以下属性：

| 属性 | 描述 | 示例 |
|------|------|------|
| `customConverterType` | 自定义转换器类型 | `INT`, `VARCHAR` |
| `name` | 字段名称 | `id` |
| `isPart` | 是否为分区字段 | `false` |
| `type` | 字段类型 | `INT` |
| `key` | 字段键名 | `id` |

## Special Parameters (from MySQL_Reader.md)

### 必需参数

| 参数 | 描述 | 类型 |
|------|------|------|
| `connection` | 数据库连接参数 | List |
| `jdbcUrl` | JDBC 连接字符串 | List |
| `username` | 用户名 | String |
| `password` | 密码 | String |
| `column` | 读取字段列表 | List |

### 可选参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `schema` | 数据库 schema 名 | 从 JDBC URL 自动提取 |
| `table` | 表名 | 从 JDBC URL 自动提取 |
| `fetchSize` | 每次读取数据条数 | Integer.MIN_VALUE |
| `where` | 筛选条件 | - |
| `splitPk` | 并发切分字段 | - |
| `queryTimeOut` | 查询超时时间 (秒) | 1000 |
| `customSql` | 自定义查询 SQL | "" |
| `polling` | 是否开启间隔轮询 | false |
| `pollingInterval` | 轮询间隔 (毫秒) | 5000 |
| `increColumn` | 增量字段 | "" |
| `startLocation` | 增量查询起始位置 | "" |
| `useMaxFunc` | 是否保存 endLocation 数据 | false |

## Usage

### 运行脚本

```bash
python3 skills/TransferData/MysqlReader/scripts/generate_config.py
```

### 输入文件位置

```
/mnt/c/Users/67461/Desktop/sync_test/model/mysql_info.xlsx
```

### 输出位置

```
skills/TransferData/MysqlReader/resoult/mysql_reader_config.json
```

### 处理流程

1. 读取 `mysql_info.xlsx` Excel 文件
2. 解析配置参数（dataSourceName, jdbc, username, password 等）
3. 解析列定义（column.name + column.type 成对出现）
4. 从 JDBC URL 自动提取 schema 和 table 名称
5. 按照参考模板格式生成完整配置
6. 输出到 resoult 目录

## Example

### 输入 Excel 内容

| A | B |
|---|---|
| dataSourceName | zy_test_MYSQL |
| jdbc | jdbc:mysql://172.16.114.43:3306/zy_test |
| username | drpeco |
| password | DT#passw0rd2024 |
| dtCenterSourceId | 4013 |
| sourceIds | 2579 |
| column.name | id |
| column.type | INT |
| column.name | name |
| column.type | VARCHAR |
| column.name | age |
| column.type | INT |

### 输出 JSON

```json
{
  "reader": {
    "parameter": {
      "password": "DT#passw0rd2024",
      "dtCenterSourceId": 4013,
      "column": [
        {"customConverterType": "INT", "name": "id", "isPart": false, "type": "INT", "key": "id"},
        {"customConverterType": "VARCHAR", "name": "name", "isPart": false, "type": "VARCHAR", "key": "name"},
        {"customConverterType": "INT", "name": "age", "isPart": false, "type": "INT", "key": "age"}
      ],
      "dtCenterSourceIds": [4013],
      "connection": [{
        "schema": "zy_test",
        "sourceId": 2579,
        "jdbcUrl": ["jdbc:mysql://172.16.114.43:3306/zy_test"],
        "table": ["zy_test"],
        "username": "drpeco"
      }],
      "sourceIds": [2579],
      "dataSourceInfo": {
        "dataSourceName": "zy_test_MYSQL",
        "dataSourceType": 1
      }
    },
    "name": "mysqlreader"
  }
}
```

## Related Files

- `SKILL.md` - This file
- `references/mysql_reader.json` - 参考配置模板
- `references/MySQL_Reader.md` - 参数配置说明文档
- `scripts/generate_config.py` - 配置生成脚本

## Related Skills

- [HdfsWriter](../HdfsWriter/SKILL.md) - HDFS/Hive 数据写入配置
- [ParseSqlText](../ParseSqlText/SKILL.md) - SQL 文本解析与拼接
- [ParseScript](../ParseScript/SKILL.md) - Base64 编码与任务脚本生成

配合使用可实现 MySQL → Hive 完整数据同步流程。

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到输入文件 | Excel 文件路径错误 | 确认文件在 `/mnt/c/Users/67461/Desktop/sync_test/model/` |
| 列为空 | column.name 和 column.type 未成对出现 | 确保 Excel 中列名和列类型交替出现 |
| schema 提取失败 | JDBC URL 格式不标准 | 使用标准格式 `jdbc:mysql://host:port/database` |
