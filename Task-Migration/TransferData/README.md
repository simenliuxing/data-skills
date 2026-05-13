# TransferData 完整流程

## 概述

TransferData 是一个用于生成 **DTStack/DTInsight 数据同步任务配置** 的自动化流程，将 Excel 配置表转换为可直接提交到 DTStack 平台的任务包。

## 流程概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TransferData 完整流程                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════    │
│   主流程：数据同步任务 (MySQL → Hive)                                   │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│   📊 Excel 配置表          ⚙️ 配置生成              📦 任务封装          │
│                                                                         │
│   mysql_info.xlsx  ──→  MysqlReader  ──→  mysql_reader_config.json     │
│        │                                                                │
│        │                    Parser                                      │
│        │                         ↓                                      │
│        │                    字段映射                                    │
│        │                         ↓                                      │
│   hdfs_info.xlsx  ──→  HdfsWriter   ──→  hdfs_writer_config.json       │
│                              │                                          │
│                              ↓                                          │
│                        parser.json                                      │
│                              ↓                                          │
│                        ParseSqlText                                     │
│                              ↓                                          │
│                        sql_text.json                                    │
│                              ↓                                          │
│                   ParseScriptBase64                                     │
│                   (Base64 编码)                                         │
│                              ↓                                          │
│                   mysql2hive_script.json                                │
│                              ↓                                          │
│                        AssembleModel                                    │
│                              ↓                                          │
│              package_YYYYMMDD_HHMMSS/                                   │
│                              ↓                                          │
│                   📤 提交到 DTStack 平台                                 │
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════    │
│   独立分支：SQL 任务 (不依赖主流程)                                      │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│   📄 sql.txt               📝 SQL 脚本生成           📦 发布包组装       │
│        +                                                               │
│   📊 task_task_info.csv  ──→  ParseScript  ──→  test_sql.json  ──→  AssembleScripyModel  ──→  package_YYYYMMDD_HHMMSS/
│                                                                         │
│   说明：独立流程，生成 SQL 任务发布包，可导入 DTStack 平台                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 两种运行模式

### 模式一：主流程（数据同步任务）

**适用场景**: MySQL → Hive/Spark 数据同步任务

**流程步骤**:

```
1️⃣  MysqlReader       → mysql_reader_config.json
2️⃣  HdfsWriter        → hdfs_writer_config.json
3️⃣  Parser            → parser.json
4️⃣  ParseSqlText      → sql_text.json
5️⃣  ParseScriptBase64 → mysql2hive_script.json
6️⃣  AssembleModel     → package_YYYYMMDD_HHMMSS/
```

### 模式二：独立分支（SQL 任务）

**适用场景**: Spark SQL、Flink SQL 等纯 SQL 任务

**流程步骤**:

```
📝  ParseScript  → test_sql.json
```

**输入文件**:
- `sql.txt` - SQL 脚本内容
- `task_task_info.csv` - 任务依赖关系

**说明**: 独立流程，不依赖主流程的任何输出，不生成发布包

---

## 主流程详解（数据同步任务）

### 步骤 1️⃣: MysqlReader

**作用**: 读取 MySQL 配置 Excel，生成读取端配置

**输入**: 
- `/mnt/c/Users/67461/Desktop/sync_test/model/mysql_info.xlsx`

**输出**: 
- `skills/TransferData/MysqlReader/resoult/mysql_reader_config.json`

**脚本**: 
```bash
python3 skills/TransferData/MysqlReader/scripts/generate_config.py
```

---

### 步骤 2️⃣: HdfsWriter

**作用**: 读取 HDFS 配置 Excel，生成写入端配置

**输入**: 
- `/mnt/c/Users/67461/Desktop/sync_test/model/hdfs_info.xlsx`

**输出**: 
- `skills/TransferData/HdfsWriter/resoult/hdfs_writer_config.json`

**脚本**: 
```bash
python3 skills/TransferData/HdfsWriter/scripts/generate_config.py
```

---

### 步骤 3️⃣: Parser

**作用**: 整合 Reader 和 Writer 配置，生成字段映射关系

**输入**: 
- `MysqlReader/resoult/mysql_reader_config.json`
- `HdfsWriter/resoult/hdfs_writer_config.json`

**输出**: 
- `skills/TransferData/Parser/resoult/parser.json`

**脚本**: 
```bash
python3 skills/TransferData/Parser/scripts/generate_config.py
```

**功能**:
- 整合源和目标数据源信息
- 生成字段映射关系 (keymap)
- 自动识别分区字段
- 生成任务运行参数 (setting)

---

### 步骤 4️⃣: ParseSqlText

**作用**: 拼接 Reader、Writer 和 Parser 配置，生成完整 job 配置

**输入**: 
- `MysqlReader/resoult/mysql_reader_config.json`
- `HdfsWriter/resoult/hdfs_writer_config.json`
- `Parser/resoult/parser.json`

**输出**: 
- `skills/TransferData/ParseSqlText/resoult/sql_text.json`

**脚本**: 
```bash
python3 skills/TransferData/ParseSqlText/scripts/parse_sql_text.py
```

---

### 步骤 5️⃣: ParseScriptBase64

**作用**: Base64 编码 + 任务封装，生成最终任务脚本

**输入**: 
- `ParseSqlText/resoult/sql_text.json`

**输出**: 
- `skills/TransferData/ParseScriptBase64/resoult/mysql2hive_script.json`

**脚本**: 
```bash
python3 skills/TransferData/ParseScriptBase64/scripts/parse_script.py
```

---

### 步骤 6️⃣: AssembleModel

**作用**: 组装发布包，生成 DTStack 可导入的完整目录

**输入**: 
- `ParseScriptBase64/resoult/mysql2hive_script.json`

**输出**: 
- `C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/`

**参考格式**: `C:/Users/67461/Desktop/sync_model/sync_xd/`

**脚本**: 
```bash
python3 skills/TransferData/AssembleModel/scripts/assemble_package.py
```

**生成内容**:
- `package.json` - 包配置（包含 dataSourceList, engineList 等）
- `task_catalogue.json` - 任务目录树结构
- `task.xls` - 任务 Excel 模板
- `error.log` - 错误日志（空）
- `tasks/mysql2hive_script.json` - 完整的任务脚本（含 taskInfo 全量字段）

---

## 独立分支详解（SQL 任务）

### 📝 ParseScript

**作用**: 读取 SQL 文件和任务依赖配置，生成 SQL 任务脚本

**输入**: 
- `C:/Users/67461/Desktop/sync_model/model/sql.txt`
- `C:/Users/67461/Desktop/sync_model/model/task_task_info.csv`

**输出**: 
- `skills/TransferData/ParseScript/resoult/test_sql.json`

**脚本**: 
```bash
python3 skills/TransferData/ParseScript/scripts/generate_config.py
```

**功能**:
- 读取 sql.txt 中的 SQL 内容
- 读取 task_task_info.csv 中的任务依赖关系
- 自动添加 SQL 头部注释（任务名、类型、作者、时间、描述）
- 生成完整的任务脚本 JSON 结构

**sql.txt 示例**:
```sql
select * from students
```

**task_task_info.csv 示例**:
```csv
customOffset,forwardDirection,isCurrentProject,projectAlias,taskName,taskType,upDownRelyType
0,1,TRUE,JSZC_DEMO,node1,44,0
```

---

## 一键执行

### 方式一：使用总控脚本（推荐）

```bash
cd /home/shuofeng/.openclaw/workspace

# 执行主流程（数据同步任务，默认）
python3 skills/TransferData/run_all.py --sync

# 执行独立分支（SQL 任务）
python3 skills/TransferData/run_all.py --sql

# 执行全部流程（主流程 + 独立分支）
python3 skills/TransferData/run_all.py --all
```

### 方式二：手动执行（主流程）

```bash
cd /home/shuofeng/.openclaw/workspace

# 1. MySQL Reader
python3 skills/TransferData/MysqlReader/scripts/generate_config.py

# 2. HDFS Writer
python3 skills/TransferData/HdfsWriter/scripts/generate_config.py

# 3. Parser - 字段映射
python3 skills/TransferData/Parser/scripts/generate_config.py

# 4. ParseSqlText
python3 skills/TransferData/ParseSqlText/scripts/parse_sql_text.py

# 5. ParseScriptBase64 - Base64 编码
python3 skills/TransferData/ParseScriptBase64/scripts/parse_script.py

# 6. AssembleModel
python3 skills/TransferData/AssembleModel/scripts/assemble_package.py
```

### 方式三：手动执行（独立分支 - SQL 任务）

```bash
cd /home/shuofeng/.openclaw/workspace

# 1. ParseScript - 生成 SQL 任务脚本
python3 skills/TransferData/ParseScript/scripts/generate_config.py

# 2. AssembleScripyModel - 组装发布包
python3 skills/TransferData/AssembleScripyModel/scripts/assemble_package.py
```

### 方式四：Shell 脚本

```bash
cat > run_transfer_data.sh << 'EOF'
#!/bin/bash
cd /home/shuofeng/.openclaw/workspace

echo "══════════════════════════════════════════════════════════════"
echo "              TransferData 数据同步配置生成流程"
echo "══════════════════════════════════════════════════════════════"

echo ""
echo "[1/6] MysqlReader..."
python3 skills/TransferData/MysqlReader/scripts/generate_config.py

echo ""
echo "[2/6] HdfsWriter..."
python3 skills/TransferData/HdfsWriter/scripts/generate_config.py

echo ""
echo "[3/6] Parser..."
python3 skills/TransferData/Parser/scripts/generate_config.py

echo ""
echo "[4/6] ParseSqlText..."
python3 skills/TransferData/ParseSqlText/scripts/parse_sql_text.py

echo ""
echo "[5/6] ParseScriptBase64..."
python3 skills/TransferData/ParseScriptBase64/scripts/parse_script.py

echo ""
echo "[6/6] AssembleModel..."
python3 skills/TransferData/AssembleModel/scripts/assemble_package.py

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ 完成！"
echo "══════════════════════════════════════════════════════════════"
EOF

chmod +x run_transfer_data.sh
./run_transfer_data.sh
```

---

## 目录结构

```
skills/TransferData/
│
├── 📄 run_all.py                    # 总控脚本（一键执行）
├── 📄 README.md                     # 本文档
│
├── 📂 MysqlReader/                  # 主流程步骤 1: MySQL 读取配置
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   ├── 📄 mysql_reader.json
│   │   └── 📄 MySQL_Reader.md
│   ├── 📂 resoult/
│   │   └── 📄 mysql_reader_config.json
│   └── 📂 scripts/
│       └── 📄 generate_config.py
│
├── 📂 HdfsWriter/                   # 主流程步骤 2: HDFS 写入配置
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   ├── 📄 hdfs_writer.json
│   │   └── 📄 HDFS_Writer.md
│   ├── 📂 resoult/
│   │   └── 📄 hdfs_writer_config.json
│   └── 📂 scripts/
│       └── 📄 generate_config.py
│
├── 📂 Parser/                       # 主流程步骤 3: 字段映射整合
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   └── 📄 parser.json
│   ├── 📂 resoult/
│   │   └── 📄 parser.json
│   └── 📂 scripts/
│       └── 📄 generate_config.py
│
├── 📂 ParseSqlText/                 # 主流程步骤 4: 拼接完整 job 配置
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   └── 📄 sql_text.json
│   ├── 📂 resoult/
│   │   └── 📄 sql_text.json
│   └── 📂 scripts/
│       └── 📄 parse_sql_text.py
│
├── 📂 ParseScriptBase64/            # 主流程步骤 5: Base64 编码封装
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   └── 📄 mysql2hive_script.json
│   ├── 📂 resoult/
│   │   └── 📄 mysql2hive_script.json
│   └── 📂 scripts/
│       └── 📄 parse_script.py
│
├── 📂 AssembleModel/                # 主流程步骤 6: 组装发布包
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   ├── 📄 package.json
│   │   ├── 📄 task_catalogue.json
│   │   └── 📄 task.xls
│   └── 📂 scripts/
│       └── 📄 assemble_package.py
│
├── 📂 ParseScript/                  # 独立分支步骤 1: SQL 任务脚本生成
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   └── 📄 test_sparksql.json
│   ├── 📂 resoult/
│   │   └── 📄 test_sql.json
│   └── 📂 scripts/
│       └── 📄 generate_config.py
│
└── 📂 AssembleScripyModel/          # 独立分支步骤 2: SQL 任务发布包组装
    ├── 📄 SKILL.md
    ├── 📂 references/
    │   ├── 📄 package.json
    │   ├── 📄 task_catalogue.json
    │   └── 📄 task.xls
    ├── 📂 resoult/
    └── 📂 scripts/
        └── 📄 assemble_package.py
```

---

## 输入文件

### mysql_info.xlsx

**位置**: `/mnt/c/Users/67461/Desktop/sync_test/model/mysql_info.xlsx`

| 字段 | 说明 | 示例 |
|------|------|------|
| `dataSourceName` | 数据源名称 | `zy_test_MYSQL` |
| `jdbc` | JDBC 连接字符串 | `jdbc:mysql://host:3306/db` |
| `username` | 用户名 | `drpeco` |
| `password` | 密码 | `DT#passw0rd2024` |
| `dtCenterSourceId` | DTCenter 源 ID | `4013` |
| `sourceIds` | 源 ID | `2579` |
| `column.name` | 列名 | `id`, `name`, `age` |
| `column.type` | 列类型 | `INT`, `VARCHAR` |

### hdfs_info.xlsx

**位置**: `/mnt/c/Users/67461/Desktop/sync_test/model/hdfs_info.xlsx`

| 字段 | 说明 | 示例 |
|------|------|------|
| `dataSourceName` | 数据源名称 | `zy_test_HADOOP` |
| `dataSourceType` | 数据源类型 | `45` |
| `jdbc` | Hive JDBC | `jdbc:hive2://host:port/db` |
| `username` | 用户名 | `admin@dtstack.com` |
| `password` | 密码 | `DTstack_PDSA` |
| `path` | HDFS 路径 | `/user/hive/warehouse/...` |
| `partition` | 分区 | `pt=20260412` |
| `fileType` | 文件类型 | `orc` |
| `defaultFS` | HDFS 地址 | `hdfs://ns1` |
| `column.name` | 列名 | `id`, `name`, `age` |
| `column.type` | 列类型 | `int`, `string` |
| `hadoopConfig` | Hadoop 配置 | JSON 字符串 |

### sql.txt（独立分支）

**位置**: `C:/Users/67461/Desktop/sync_model/model/sql.txt`

**内容示例**:
```sql
select * from students
```

### task_task_info.csv（独立分支）

**位置**: `C:/Users/67461/Desktop/sync_model/model/task_task_info.csv`

**格式**:
```csv
customOffset,forwardDirection,isCurrentProject,projectAlias,taskName,taskType,upDownRelyType
0,1,TRUE,JSZC_DEMO,node1,44,0
```

---

## 输出文件

### 主流程（数据同步任务）

#### 中间产物

| 文件 | 路径 | 说明 |
|------|------|------|
| `mysql_reader_config.json` | `MysqlReader/resoult/` | MySQL 读取端配置 |
| `hdfs_writer_config.json` | `HdfsWriter/resoult/` | HDFS 写入端配置 |
| `parser.json` | `Parser/resoult/` | 字段映射配置 |
| `sql_text.json` | `ParseSqlText/resoult/` | 拼接后的 job 配置 |
| `mysql2hive_script.json` | `ParseScriptBase64/resoult/` | Base64 编码的任务脚本 |

#### 最终产物

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
├── package.json              # 包配置
├── task_catalogue.json       # 任务目录结构
├── task.xls                  # 任务 Excel
├── error.log                 # 错误日志 (空)
└── tasks/
    └── mysql2hive_script.json  # 任务脚本
```

### 独立分支（SQL 任务）

#### 中间产物

| 文件 | 路径 | 说明 |
|------|------|------|
| `test_sql.json` | `ParseScript/resoult/` | SQL 任务脚本 |

#### 最终产物

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
├── package.json              # 包配置
├── task_catalogue.json       # 任务目录结构
├── task.xls                  # 任务 Excel
├── error.log                 # 错误日志
└── tasks/
    └── test_sparksql.json    # SQL 任务脚本
```

---

## 配置说明

### syncModel 同步模式

| 值 | 说明 | 适用场景 |
|------|------|----------|
| `0` | 全量同步 | 首次同步、重建表 |
| `1` | 增量同步 | 日常增量更新 |

### writeMode 写入模式

| 值 | 说明 | 适用场景 |
|------|------|----------|
| `overwrite` | 覆盖 | 全量同步 |
| `append` | 追加 | 增量同步 |

### fileType 文件类型

| 值 | 说明 | 压缩支持 |
|------|------|----------|
| `text` | 文本文件 | GZIP, BZIP2 |
| `orc` | ORC 列存 | SNAPPY, ZLIB, LZO |
| `parquet` | Parquet 列存 | SNAPPY, GZIP, LZO |

---

## 常见问题

### 1. 找不到输入文件

**错误**: `FileNotFoundError: .../mysql_info.xlsx`

**解决**: 确认 Excel 文件在正确位置：
```
/mnt/c/Users/67461/Desktop/sync_test/model/
```

### 2. 字段不匹配

**错误**: Reader 和 Writer 字段数量不一致

**解决**: 确保两个 Excel 中的 `column.name` 和 `column.type` 成对出现且数量一致

### 3. 输出目录无法创建

**错误**: `PermissionError: ...`

**解决**: 检查 Windows 路径访问权限，确保 WSL 可以访问 C 盘

### 4. Base64 编码失败

**错误**: `Invalid base64`

**解决**: 检查 ParseSqlText 生成的 JSON 格式是否正确

### 5. SQL 任务分支找不到输入文件

**错误**: `找不到 sql.txt` 或 `找不到 task_task_info.csv`

**解决**: 确认文件在正确位置：
```
C:/Users/67461/Desktop/sync_model/model/
```

### 6. AssembleScripyModel 找不到 ParseScript 输出

**错误**: `找不到 test_sql.json`

**解决**: 先运行 ParseScript 脚本生成任务脚本

---

## 下一步

### 主流程（数据同步任务）

生成发布包后，在 DTStack 平台中：

1. 登录 DTStack 数据开发平台
2. 进入「任务管理」或「包管理」
3. 选择「导入包」
4. 选择生成的 `package_YYYYMMDD_HHMMSS` 目录
5. 确认导入
6. 在任务列表中查看并执行同步任务

### 独立分支（SQL 任务）

生成发布包后，在 DTStack 平台中：

1. 登录 DTStack 数据开发平台
2. 进入「任务管理」或「包管理」
3. 选择「导入包」
4. 选择生成的 `package_YYYYMMDD_HHMMSS` 目录
5. 确认导入
6. 在任务列表中查看并执行 SQL 任务

---

## 相关文档

- [MysqlReader SKILL.md](./MysqlReader/SKILL.md)
- [HdfsWriter SKILL.md](./HdfsWriter/SKILL.md)
- [Parser SKILL.md](./Parser/SKILL.md)
- [ParseSqlText SKILL.md](./ParseSqlText/SKILL.md)
- [ParseScript SKILL.md](./ParseScript/SKILL.md) - 独立分支：SQL 任务脚本生成
- [ParseScriptBase64 SKILL.md](./ParseScriptBase64/SKILL.md) - 主流程：Base64 编码任务脚本生成
- [AssembleModel SKILL.md](./AssembleModel/SKILL.md)
