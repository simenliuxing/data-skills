# TransferData2 - 多任务同步发布框架

> 创建时间：2026-05-09

## 📋 概述

TransferData2 是 TransferData 框架的扩展，专注于**多任务批量同步**场景。它将 `AssembleSyncJson` 和 `AssembleSyncReleasePackage` 整合在一起，提供从 Excel 配置到发布包的一站式解决方案。

## 🗺️ 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TransferData2 完整流程                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   📊 dataSource_info.xlsx  ──┐                                          │
│   📊 task_info.xlsx     ────┼──→ 步骤 1                                 │
│   📊 taskSchedule_info.xlsx─┘                                          │
│                    │                                                    │
│                    ▼                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  1️⃣  AssembleSyncJson                                           │  │
│   │      读取多源 Excel 配置，生成多个任务 JSON                          │  │
│   │      输出：resoult/mysql2hive_01.json, mysql2hive_02.json, ...  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                    │                                                    │
│                    ▼                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  2️⃣  AssembleSyncReleasePackage                                 │  │
│   │      读取所有任务 JSON，组装成 DTStack 发布包                        │  │
│   │      输出：C:/Users/67461/Desktop/sync_package_YYYYMMDD_HHMMSS/ │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                    │                                                    │
│                    ▼                                                    │
│   📤 导入 DTStack 平台执行                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
skills/TransferData2/
│
├── 📄 OVERVIEW.md                   # 本文档
│
├── 📂 AssembleSyncJson/             # 步骤 1: 多任务配置生成
│   ├── 📄 SKILL.md
│   ├── 📂 references/
│   │   └── 📄 mysql2hive_01.json    # 参考模板
│   ├── 📂 resoult/
│   │   └── 📄 *.json                # 生成的任务配置
│   └── 📂 scripts/
│       └── 📄 generate_config.py    # 配置生成脚本
│
└── 📂 AssembleSyncReleasePackage/   # 步骤 2: 多任务发布包组装
    ├── 📄 SKILL.md
    ├── 📂 references/
    │   ├── 📄 package.json          # 包配置模板
    │   ├── 📄 task_catalogue.json   # 任务目录模板
    │   ├── 📄 task.xls              # Excel 模板
    │   └── 📄 task_template.json    # 任务结构模板
    ├── 📂 resoult/
    └── 📂 scripts/
        └── 📄 assemble_sync_package.py  # 发布包组装脚本
```

## 🚀 快速开始

### 完整流程（推荐）

```bash
cd /home/shuofeng/.openclaw/workspace

# 步骤 1: 生成多任务配置
python3 skills/TransferData2/AssembleSyncJson/scripts/generate_config.py

# 步骤 2: 组装发布包
python3 skills/TransferData2/AssembleSyncReleasePackage/scripts/assemble_sync_package.py

# 输出位置：
# C:/Users/67461/Desktop/sync_package_YYYYMMDD_HHMMSS/
```

### 单步执行

#### 步骤 1: 生成任务配置

```bash
python3 skills/TransferData2/AssembleSyncJson/scripts/generate_config.py

# 输出：skills/TransferData2/AssembleSyncJson/resoult/*.json
```

#### 步骤 2: 组装发布包

```bash
python3 skills/TransferData2/AssembleSyncReleasePackage/scripts/assemble_sync_package.py

# 输出：C:/Users/67461/Desktop/sync_package_YYYYMMDD_HHMMSS/
```

## 📦 输出产物

### AssembleSyncJson 输出

```
skills/TransferData2/AssembleSyncJson/resoult/
├── mysql2hive_01.json    # 任务 1 配置
├── mysql2hive_02.json    # 任务 2 配置
└── ...                   # 更多任务
```

### AssembleSyncReleasePackage 输出

```
C:/Users/67461/Desktop/sync_package_YYYYMMDD_HHMMSS/
├── package.json              # 包配置（包含所有数据源）
├── task_catalogue.json       # 任务目录结构
├── task.xls                  # 任务 Excel
├── error.log                 # 错误日志（空）
└── tasks/
    ├── mysql2hive_01.json    # 任务脚本 1
    ├── mysql2hive_02.json    # 任务脚本 2
    └── ...                   # 更多任务
```

## 📋 输入文件

### Excel 配置文件

所有输入文件位于：`C:/Users/67461/Desktop/sync_model/model/`

| 文件 | 说明 | 必需 |
|------|------|------|
| `dataSource_info.xlsx` | 数据源配置（MySQL、HDFS 等） | ✅ |
| `task_info.xlsx` | 任务配置（表映射、字段映射） | ✅ |
| `taskSchedule_info.xlsx` | 任务调度依赖配置 | ✅ |

### Excel 格式说明

#### dataSource_info.xlsx

包含多个 sheet 页，每个 sheet 对应一个数据源：

| 字段 | 说明 | 示例 |
|------|------|------|
| 数据源类型 | `mysql` 或 `hdfs` | `mysql` |
| dataSourceName | 数据源名称 | `zy_test_MYSQL` |
| dataSourceType | 数据源类型 ID | `1` (MySQL), `45` (Hadoop) |
| jdbc | JDBC 连接字符串 | `jdbc:mysql://...` |
| username | 用户名 | `drpeco` |
| password | 密码 | `DT#passw0rd2024` |

#### task_info.xlsx

包含多个 sheet 页，每个 sheet 对应一个任务：

| 字段 | 说明 | 示例 |
|------|------|------|
| 源表表名 | MySQL 源表 | `students` |
| 源表字段 | 源字段名 | `id`, `name` |
| 是否映射 | `是` 或 `否` | `是` |
| 目标表表名 | Hive 目标表 | `students` |
| 目标表字段 | 目标字段名 | `id`, `name` |
| 分区字段 | 分区标识 | `分区字段`, `pt` |

#### taskSchedule_info.xlsx

任务依赖配置：

| 字段 | 说明 | 示例 |
|------|------|------|
| 任务名称 | 任务名 | `mysql2hive_01` |
| 上游依赖 | 依赖的任务 | `无`, `root` |

## 🔧 技能列表

| 技能 | 步骤 | 作用 | 输入 | 输出 |
|------|------|------|------|------|
| [AssembleSyncJson](./AssembleSyncJson/SKILL.md) | 1 | 多任务配置生成 | Excel 配置 | `resoult/*.json` |
| [AssembleSyncReleasePackage](./AssembleSyncReleasePackage/SKILL.md) | 2 | 多任务发布包组装 | `resoult/*.json` | `sync_package_*/` |

## 🎯 使用场景

- 批量 MySQL → Hive 数据同步任务
- 多个相关任务需要一次性发布
- 需要任务依赖关系的数据同步工作流
- 从 Excel 配置快速生成 DTStack 发布包

## 📝 下一步

生成发布包后：

1. 登录 DTStack 数据开发平台
2. 进入「包管理」或「任务管理」
3. 选择「导入包」
4. 选择生成的 `sync_package_YYYYMMDD_HHMMSS` 目录
5. 确认导入
6. 在任务列表中查看并执行任务

## 🔗 与 TransferData 的关系

TransferData2 是 TransferData 框架的扩展：

| 特性 | TransferData | TransferData2 |
|------|--------------|---------------|
| 任务数量 | 单任务 | 多任务批量 |
| 配置方式 | 多步骤手动 | Excel 一键生成 |
| 输出目录 | `package_*/` | `sync_package_*/` |
| 适用场景 | 独立任务 | 批量任务 |

TransferData 主框架位于：`skills/TransferData/`

---

*最后更新：2026-05-09*
