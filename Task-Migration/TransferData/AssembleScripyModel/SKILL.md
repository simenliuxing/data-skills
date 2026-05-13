# AssembleScripyModel Skill

## Description

DTStack SQL 脚本发布包组装技能。读取 ParseScript 生成的 SQL 任务脚本，组装成 DTStack 平台可发布的完整目录结构。

## Position in TransferData Framework

```
TransferData 独立分支（SQL 任务）:

📄 sql.txt               📝 SQL 脚本生成           📦 发布包组装
     +
📊 task_task_info.csv  ──→  ParseScript  ──→  test_sql.json  ──→  AssembleScripyModel  ──→  package_YYYYMMDD_HHMMSS/
                                              (步骤 1)            (步骤 2)
```

与 AssembleModel 的区别：
- **AssembleModel**: 用于主流程数据同步任务（Base64 编码的 mysql2hive_script.json）
- **AssembleScripyModel**: 用于独立分支 SQL 任务（明文 SQL 脚本的 test_sql.json）

## Capabilities

- 读取 ParseScript/resoult/test_sql.json
- 生成 package.json 包配置
- 生成 task_catalogue.json 任务目录配置
- 复制 task.xls 模板文件
- 创建 tasks 子目录并放置任务脚本
- 输出到 Windows Desktop，文件夹命名：package_时间戳

## Input/Output Structure

### Input

- `ParseScript/resoult/test_sql.json` - ParseScript 生成的 SQL 任务脚本
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
    └── test_sparksql.json  # SQL 任务脚本
```

## Package Structure

### 目录结构说明

| 文件/目录 | 说明 | 来源 |
|-----------|------|------|
| `package.json` | 包配置信息（引擎、项目等） | 动态生成 |
| `task_catalogue.json` | 任务目录树结构 | 动态生成 |
| `task.xls` | 任务信息 Excel | 从 references 复制 |
| `error.log` | 错误日志文件 | 创建空文件 |
| `tasks/` | 任务脚本目录 | 创建 |
| `tasks/test_sparksql.json` | SQL 任务脚本 | 从 ParseScript 复制 |

### package.json 结构

```json
{
  "createTime": "2026-04-27 22:50:57",
  "createUser": "admin@dtstack.com",
  "engineList": [
    {"engineType": 1, "schema": "zy_test"}
  ],
  "packageDesc": "sql 脚本",
  "packageName": "BP_2026_04_27_049dac10",
  "projectName": "zy_test",
  "tenantName": "培训演示",
  "userNameList": []
}
```

### task_catalogue.json 结构

```json
{
  "0": [{
    "catalogueType": 0,
    "createUserId": 101769,
    "engineType": 0,
    "gmtCreate": 1772765702000,
    "gmtModified": 1772765702000,
    "id": 31153,
    "isDeleted": 0,
    "level": 0,
    "nodeName": "周期任务",
    "nodePid": 0,
    "orderVal": 1,
    "projectId": 695,
    "sort": 0,
    "tenantId": 10719
  }],
  "1": [{
    "catalogueType": 0,
    "createUserId": 101769,
    "engineType": 0,
    "gmtCreate": 1772765702000,
    "gmtModified": 1772765702000,
    "id": 31155,
    "isDeleted": 0,
    "level": 1,
    "nodeName": "任务开发",
    "nodePid": 31153,
    "projectId": 695,
    "sort": 0,
    "tenantId": 10719
  }],
  "2": [{
    "catalogueType": 0,
    "createUserId": 1,
    "engineType": 0,
    "gmtCreate": 1775980496000,
    "gmtModified": 1775980496000,
    "id": 33357,
    "isDeleted": 0,
    "level": 2,
    "nodeName": "测试",
    "nodePid": 31155,
    "projectId": 695,
    "sort": 0,
    "tenantId": 10719
  }]
}
```

## Usage

### 运行脚本

```bash
python3 skills/TransferData/AssembleScripyModel/scripts/assemble_package.py
```

### 输出位置

```
C:/Users/67461/Desktop/package_YYYYMMDD_HHMMSS/
```

### 文件夹命名规则

```
package_当前时间戳
```

示例：`package_20260427_225057`

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│           AssembleScripyModel 工作流程                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取 ParseScript/resoult/test_sql.json                  │
│                                                             │
│  2. 解析任务脚本中的信息                                     │
│     - taskInfo.name (任务名称)                              │
│     - taskInfo.projectId (项目 ID)                          │
│     - taskInfo.tenantId (租户 ID)                           │
│     - taskInfo.engineType (引擎类型)                        │
│                                                             │
│  3. 生成 package.json                                       │
│     - createTime                                            │
│     - packageName (package_时间戳)                          │
│     - engineList                                            │
│     - packageDesc: "sql 脚本"                               │
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

**ParseScript/resoult/test_sql.json:**
```json
{
  "taskInfo": {
    "name": "test_sparksql",
    "engineType": 1,
    "taskType": 0,
    "projectId": 695,
    "tenantId": 10719,
    "sqlText": "-- name test_sparksql\n-- type Spark SQL\n...",
    "nodePid": 33357
  },
  "taskTaskInfo": [...],
  "updateEnvParam": false
}
```

### 输出目录

```
C:/Users/67461/Desktop/package_20260427_225057/
├── package.json
├── task_catalogue.json
├── task.xls
├── error.log
└── tasks/
    └── test_sparksql.json
```

## Related Skills

| Skill | 作用 | 输出 |
|-------|------|------|
| [ParseScript](../ParseScript/SKILL.md) | SQL 任务脚本生成（步骤 1） | test_sql.json |
| **AssembleScripyModel** | **SQL 任务发布包组装（步骤 2）** | **package_时间戳/** |

## Complete TransferData Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  TransferData 完整流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  主流程（数据同步任务）：                                    │
│  1️⃣  MysqlReader                                            │
│  2️⃣  HdfsWriter                                             │
│  3️⃣  Parser                                                 │
│  4️⃣  ParseSqlText                                           │
│  5️⃣  ParseScriptBase64                                      │
│  6️⃣  AssembleModel                                          │
│                                                             │
│  独立分支（SQL 任务）：                                      │
│  📝  ParseScript                                            │
│  📦  AssembleScripyModel  ← 本技能                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Files

- `SKILL.md` - This file
- `references/package.json` - 包配置模板
- `references/task_catalogue.json` - 任务目录模板
- `references/task.xls` - 任务 Excel 模板
- `scripts/assemble_package.py` - 组装脚本
- `resoult/` - 临时输出目录（可选）

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 找不到任务脚本 | ParseScript 未运行 | 先运行 ParseScript 脚本 |
| 输出目录无法创建 | Windows 路径权限问题 | 检查 C 盘访问权限 |
| 任务信息解析失败 | test_sql.json 格式错误 | 检查 JSON 是否有效 |
