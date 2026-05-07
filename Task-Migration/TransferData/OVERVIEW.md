# TransferData 框架概览

> 更新时间：2026-05-06

## 📋 概述

TransferData 是一个用于生成 **DTStack/DTInsight 数据同步任务配置** 的自动化框架，将 Excel/CSV 配置表和 SQL 脚本转换为可直接提交到 DTStack 平台的任务发布包。

## 🗺️ 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TransferData 完整流程                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════    │
│   主流程：数据同步任务 (MySQL → Hive) - 6 步                              │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│   📊 mysql_info.xlsx                                                    │
│        │                                                                │
│        ▼                                                                │
│   1️⃣  MysqlReader                                                       │
│        └──→ mysql_reader_config.json                                    │
│                                                                         │
│   📊 hdfs_info.xlsx                                                     │
│        │                                                                │
│        ▼                                                                │
│   2️⃣  HdfsWriter                                                        │
│        └──→ hdfs_writer_config.json                                     │
│                                                                         │
│        │                                                                │
│        ▼                                                                │
│   3️⃣  Parser (整合源 + 目标，生成字段映射)                               │
│        └──→ parser.json                                                 │
│                                                                         │
│        ▼                                                                │
│   4️⃣  ParseSqlText (拼接完整 job 配置)                                  │
│        └──→ sql_text.json                                               │
│                                                                         │
│        ▼                                                                │
│   5️⃣  ParseScriptBase64 (Base64 编码)                                  │
│        └──→ mysql2hive_script.json                                      │
│                                                                         │
│        ▼                                                                │
│   6️⃣  AssembleModel (组装发布包)                                       │
│        └──→ C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/             │
│                                                                         │
│        ▼                                                                │
│   📤 导入 DTStack 平台执行                                               │
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════    │
│   独立分支：SQL 任务 (Spark SQL/Flink SQL) - 2 步                         │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│   📄 sql.txt                                                            │
│        +                                                                │
│   📊 task_task_info.csv                                                 │
│        │                                                                │
│        ▼                                                                │
│   📝 ParseScript (步骤 1: 生成 SQL 任务脚本)                              │
│        └──→ test_sql.json                                               │
│                                                                         │
│        ▼                                                                │
│   📦 AssembleScripyModel (步骤 2: 组装发布包)                            │
│        └──→ C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/             │
│                                                                         │
│        ▼                                                                │
│   📤 导入 DTStack 平台执行                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
skills/TransferData/
│
├── 📄 run_all.py                    # 总控脚本（一键执行）
├── 📄 README.md                     # 详细文档
│
├── 📂 MysqlReader/                  # 主流程步骤 1
│   ├── 📄 SKILL.md
│   ├── 📂 references/               # 参考模板
│   ├── 📂 resoult/                  # 输出目录
│   └── 📂 scripts/
│       └── generate_config.py
│
├── 📂 HdfsWriter/                   # 主流程步骤 2
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   ├── 📂 resoult/
│   └── 📂 scripts/
│       └── generate_config.py
│
├── 📂 Parser/                       # 主流程步骤 3
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   ├── 📂 resoult/
│   └── 📂 scripts/
│       └── generate_config.py
│
├── 📂 ParseSqlText/                 # 主流程步骤 4
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   ├── 📂 resoult/
│   └── 📂 scripts/
│       └── parse_sql_text.py
│
├── 📂 ParseScriptBase64/            # 主流程步骤 5
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   ├── 📂 resoult/
│   └── 📂 scripts/
│       └── parse_script.py
│
├── 📂 AssembleModel/                # 主流程步骤 6
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   └── 📂 scripts/
│       └── assemble_package.py
│
├── 📂 ParseScript/                  # 独立分支步骤 1
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   ├── 📂 resoult/
│   └── 📂 scripts/
│       └── generate_config.py
│
└── 📂 AssembleScripyModel/          # 独立分支步骤 2
    ├── 📄 SKILL.md
    ├── 📂 references/
    ├── 📂 resoult/
    └── 📂 scripts/
        └── assemble_package.py
```

## 🚀 快速开始

### 一键执行

```bash
cd /home/shuofeng/.openclaw/workspace

# 执行主流程（数据同步任务，默认）
python3 skills/TransferData/run_all.py --sync

# 执行独立分支（SQL 任务）
python3 skills/TransferData/run_all.py --sql

# 执行全部流程（主流程 + 独立分支）
python3 skills/TransferData/run_all.py --all
```

### 手动执行

#### 主流程（数据同步任务）

```bash
# 步骤 1: MySQL Reader
python3 skills/TransferData/MysqlReader/scripts/generate_config.py

# 步骤 2: HDFS Writer
python3 skills/TransferData/HdfsWriter/scripts/generate_config.py

# 步骤 3: Parser - 字段映射
python3 skills/TransferData/Parser/scripts/generate_config.py

# 步骤 4: ParseSqlText
python3 skills/TransferData/ParseSqlText/scripts/parse_sql_text.py

# 步骤 5: ParseScriptBase64 - Base64 编码
python3 skills/TransferData/ParseScriptBase64/scripts/parse_script.py

# 步骤 6: AssembleModel - 组装发布包
python3 skills/TransferData/AssembleModel/scripts/assemble_package.py
```

#### 独立分支（SQL 任务）

```bash
# 步骤 1: ParseScript - 生成 SQL 任务脚本
python3 skills/TransferData/ParseScript/scripts/generate_config.py

# 步骤 2: AssembleScripyModel - 组装发布包
python3 skills/TransferData/AssembleScripyModel/scripts/assemble_package.py
```

## 📦 输出产物

### 主流程（数据同步任务）

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
├── package.json              # 包配置
├── task_catalogue.json       # 任务目录结构
├── task.xls                  # 任务 Excel
├── error.log                 # 错误日志
└── tasks/
    └── mysql2hive_script.json  # Base64 编码的任务脚本
```

### 独立分支（SQL 任务）

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
├── package.json              # 包配置
├── task_catalogue.json       # 任务目录结构
├── task.xls                  # 任务 Excel
├── error.log                 # 错误日志
└── tasks/
    └── test_sparksql.json    # SQL 任务脚本（明文）
```

## 📋 输入文件

### 主流程

| 文件 | 位置 | 说明 |
|------|------|------|
| `mysql_info.xlsx` | `/mnt/c/Users/67461/Desktop/sync_test/model/` | MySQL 数据源配置 |
| `hdfs_info.xlsx` | `/mnt/c/Users/67461/Desktop/sync_test/model/` | HDFS/Hive 数据源配置 |

### 独立分支

| 文件 | 位置 | 说明 |
|------|------|------|
| `sql.txt` | `C:/Users/67461/Desktop/sync_model/model/` | SQL 脚本内容 |
| `task_task_info.csv` | `C:/Users/67461/Desktop/sync_model/model/` | 任务依赖配置 |

## 🔧 技能列表

### 主流程技能

| 技能 | 步骤 | 作用 | 输入 | 输出 |
|------|------|------|------|------|
| [MysqlReader](./MysqlReader/SKILL.md) | 1 | MySQL 读取配置 | `mysql_info.xlsx` | `mysql_reader_config.json` |
| [HdfsWriter](./HdfsWriter/SKILL.md) | 2 | HDFS 写入配置 | `hdfs_info.xlsx` | `hdfs_writer_config.json` |
| [Parser](./Parser/SKILL.md) | 3 | 字段映射整合 | Reader + Writer 配置 | `parser.json` |
| [ParseSqlText](./ParseSqlText/SKILL.md) | 4 | 拼接完整 job | Reader + Writer + Parser | `sql_text.json` |
| [ParseScriptBase64](./ParseScriptBase64/SKILL.md) | 5 | Base64 编码 | `sql_text.json` | `mysql2hive_script.json` |
| [AssembleModel](./AssembleModel/SKILL.md) | 6 | 组装发布包 | `mysql2hive_script.json` | `package_*/` |

### 独立分支技能

| 技能 | 步骤 | 作用 | 输入 | 输出 |
|------|------|------|------|------|
| [ParseScript](./ParseScript/SKILL.md) | 1 | SQL 任务脚本生成 | `sql.txt` + `task_task_info.csv` | `test_sql.json` |
| [AssembleScripyModel](./AssembleScripyModel/SKILL.md) | 2 | SQL 发布包组装 | `test_sql.json` | `package_*/` |

## 🎯 使用场景

### 主流程适用场景

- MySQL → Hive 数据同步
- MySQL → Spark 数据同步
- 关系型数据库 → 大数据平台数据迁移
- 全量/增量数据同步任务

### 独立分支适用场景

- Spark SQL 任务
- Flink SQL 任务
- 纯 SQL 数据处理任务
- 需要任务依赖的 SQL 工作流

## 📝 下一步

生成发布包后：

1. 登录 DTStack 数据开发平台
2. 进入「任务管理」或「包管理」
3. 选择「导入包」
4. 选择生成的 `package_YYYYMMDD_HHMMSS` 目录
5. 确认导入
6. 在任务列表中查看并执行任务

## 📚 相关文档

- [完整文档](./README.md) - 详细的流程说明和故障排查
- 各技能的 `SKILL.md` 文件 - 详细的配置说明

---

*最后更新：2026-05-06*
