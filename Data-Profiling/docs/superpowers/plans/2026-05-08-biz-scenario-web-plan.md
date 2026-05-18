# 业务场景模拟器 - 网页版实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个 Skill，用户输入行业名称和探查深度后，自动生成一个交互式网页，展示业务线、流程、表结构、模拟数据和 ER 图。

**Architecture:** 单文件 HTML 模板 + Skill 工作流引导 LLM 分步生成业务数据 JSON，注入模板后输出完整网页。增量迭代通过读取已有 HTML 中的 JSON 数据实现。

**Tech Stack:** HTML5, CSS3 (Grid/Flexbox), Vanilla JS, Mermaid.js CDN, highlight.js CDN

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `Data-Profiling/templates/index.html` | HTML 页面模板，包含完整 CSS/JS 骨架，预留数据注入点 |
| `Data-Profiling/SKILL.md` | Skill 入口，定义生成工作流、LLM 提示词、增量迭代规则 |

---

### Task 1: 创建 HTML 模板骨架

**Files:**
- Create: `Data-Profiling/templates/index.html`

- [ ] **Step 1: 创建 HTML 基础结构**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>业务场景模拟器</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/github.min.css">
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11/highlight.min.js"></script>
    <style>
        /* CSS 在 Task 2 中填充 */
    </style>
</head>
<body>
    <div id="app">
        <header class="header">
            <h1>📊 业务场景模拟器</h1>
            <div class="header-info">
                <span id="industry-display"></span>
                <span id="depth-display"></span>
                <span id="time-display"></span>
                <button id="export-btn" class="btn">导出 HTML</button>
            </div>
        </header>
        <div class="main-container">
            <aside class="sidebar">
                <nav id="biz-nav"></nav>
            </aside>
            <main class="content">
                <div class="tabs">
                    <button class="tab-btn active" data-tab="process">业务流程</button>
                    <button class="tab-btn" data-tab="schema">表结构</button>
                    <button class="tab-btn" data-tab="data">模拟数据</button>
                    <button class="tab-btn" data-tab="er">ER图</button>
                </div>
                <div class="tab-content">
                    <div id="tab-process" class="tab-pane active"></div>
                    <div id="tab-schema" class="tab-pane"></div>
                    <div id="tab-data" class="tab-pane"></div>
                    <div id="tab-er" class="tab-pane"></div>
                </div>
            </main>
        </div>
        <footer class="footer">
            <span id="stats"></span>
        </footer>
    </div>

    <script>
        // 业务数据注入点 - Skill 执行时替换
        const BIZ_DATA = /* BIZ_DATA_PLACEHOLDER */;
    </script>
    <script>
        // JS 渲染逻辑在 Task 3 中填充
    </script>
</body>
</html>
```

- [ ] **Step 2: 提交**

```bash
git add Data-Profiling/templates/index.html
git commit -m "feat: add HTML template skeleton for biz scenario simulator"
```

---

### Task 2: 填充 CSS 样式

**Files:**
- Modify: `Data-Profiling/templates/index.html` (替换 `<style>` 内容)

- [ ] **Step 1: 写入完整 CSS**

替换 `<style>` 标签内的注释为以下 CSS：

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #f5f7fa;
    color: #262626;
    height: 100vh;
    overflow: hidden;
}

#app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.header {
    background: #fff;
    padding: 12px 24px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 { font-size: 18px; font-weight: 600; }

.header-info { display: flex; gap: 16px; align-items: center; font-size: 13px; color: #8c8c8c; }

.btn {
    padding: 6px 16px;
    background: #1890ff;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
}

.btn:hover { background: #40a9ff; }

.main-container {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.sidebar {
    width: 240px;
    background: #001529;
    color: #fff;
    overflow-y: auto;
    flex-shrink: 0;
}

.biz-line { border-bottom: 1px solid #ffffff1a; }

.biz-line-header {
    padding: 12px 16px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
}

.biz-line-header:hover { background: #ffffff0d; }

.biz-line-header .arrow { transition: transform 0.2s; font-size: 12px; }
.biz-line-header.expanded .arrow { transform: rotate(90deg); }

.process-list { display: none; }
.process-list.show { display: block; }

.process-item {
    padding: 8px 16px 8px 32px;
    cursor: pointer;
    font-size: 13px;
    color: #ffffffbf;
}

.process-item:hover { background: #ffffff0d; color: #fff; }
.process-item.active { background: #1890ff; color: #fff; }

.content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #f5f7fa;
}

.tabs {
    display: flex;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;
    padding: 0 16px;
}

.tab-btn {
    padding: 12px 20px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 14px;
    color: #8c8c8c;
    border-bottom: 2px solid transparent;
}

.tab-btn:hover { color: #1890ff; }
.tab-btn.active { color: #1890ff; border-bottom-color: #1890ff; }

.tab-content { flex: 1; overflow-y: auto; padding: 16px; }
.tab-pane { display: none; }
.tab-pane.active { display: block; }

.card {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.card h3 { font-size: 15px; margin-bottom: 12px; color: #262626; }
.card p { font-size: 13px; line-height: 1.6; color: #595959; }

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #e8e8e8;
}

th { background: #fafafa; font-weight: 600; color: #262626; }
td { color: #595959; }

.code-block {
    position: relative;
    background: #f6f8fa;
    border-radius: 6px;
    padding: 12px;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.5;
}

.copy-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    padding: 4px 8px;
    background: #fff;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.copy-btn:hover { border-color: #1890ff; color: #1890ff; }

.data-table-wrap {
    max-height: 400px;
    overflow: auto;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
}

.footer {
    background: #fff;
    padding: 8px 24px;
    border-top: 1px solid #e8e8e8;
    font-size: 12px;
    color: #8c8c8c;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.mermaid { display: flex; justify-content: center; padding: 16px 0; }

.pk-badge {
    display: inline-block;
    padding: 1px 6px;
    background: #fff7e6;
    color: #fa8c16;
    border-radius: 3px;
    font-size: 11px;
    margin-left: 4px;
}

.type-tag {
    display: inline-block;
    padding: 1px 6px;
    background: #f0f5ff;
    color: #2f54eb;
    border-radius: 3px;
    font-size: 11px;
    font-family: monospace;
}
```

- [ ] **Step 2: 提交**

```bash
git add Data-Profiling/templates/index.html
git commit -m "feat: add CSS styles for biz scenario simulator"
```

---

### Task 3: 填充 JavaScript 渲染逻辑

**Files:**
- Modify: `Data-Profiling/templates/index.html` (替换第二个 `<script>` 内容)

- [ ] **Step 1: 写入完整 JS 渲染逻辑**

替换第二个 `<script>` 标签内的注释为以下 JS：

```javascript
(function() {
    'use strict';

    let currentBizLine = 0;
    let currentProcess = 0;

    function init() {
        renderHeader();
        renderSidebar();
        renderTabs();
        selectBizLine(0, 0);
        mermaid.initialize({ startOnLoad: false, theme: 'default' });
    }

    function renderHeader() {
        document.getElementById('industry-display').textContent = '行业：' + BIZ_DATA.industry;
        const depthLabels = { 1: '轻量级', 2: '中等', default: '深度建模' };
        document.getElementById('depth-display').textContent = '深度：' + (depthLabels[BIZ_DATA.depth] || depthLabels.default) + '(' + BIZ_DATA.depth + ')';
        document.getElementById('time-display').textContent = '生成：' + BIZ_DATA.generateTime;
    }

    function renderSidebar() {
        const nav = document.getElementById('biz-nav');
        let html = '';
        BIZ_DATA.businessLines.forEach((line, i) => {
            html += '<div class="biz-line">';
            html += '<div class="biz-line-header" onclick="toggleBizLine(' + i + ')">';
            html += '<span>' + line.name + '</span><span class="arrow">▶</span>';
            html += '</div>';
            html += '<div class="process-list" id="processes-' + i + '">';
            line.processes.forEach((proc, j) => {
                html += '<div class="process-item" id="proc-' + i + '-' + j + '" onclick="selectProcess(' + i + ',' + j + ')">' + proc.name + '</div>';
            });
            html += '</div></div>';
        });
        nav.innerHTML = html;
    }

    function toggleBizLine(index) {
        const list = document.getElementById('processes-' + index);
        const header = list.previousElementSibling;
        list.classList.toggle('show');
        header.classList.toggle('expanded');
    }

    function selectBizLine(bizIndex, procIndex) {
        currentBizLine = bizIndex;
        currentProcess = procIndex;
        document.querySelectorAll('.process-item').forEach(el => el.classList.remove('active'));
        const el = document.getElementById('proc-' + bizIndex + '-' + procIndex);
        if (el) el.classList.add('active');
        const line = BIZ_DATA.businessLines[bizIndex];
        const proc = line.processes[procIndex];
        renderProcessTab(proc);
        renderSchemaTab(line, proc);
        renderDataTab(line, proc);
        renderERTab();
    }

    function selectProcess(bizIndex, procIndex) {
        selectBizLine(bizIndex, procIndex);
    }

    function renderTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('tab-' + this.dataset.tab).classList.add('active');
            });
        });
    }

    function renderProcessTab(proc) {
        const container = document.getElementById('tab-process');
        let html = '<div class="card"><h3>' + proc.name + '</h3>';
        html += '<p>' + proc.description + '</p></div>';
        if (proc.flowchart) {
            html += '<div class="card"><h3>流程图</h3>';
            html += '<div class="mermaid">' + proc.flowchart + '</div></div>';
        }
        html += '<div class="card"><h3>涉及数据表</h3><ul>';
        proc.tables.forEach(t => { html += '<li>' + t + '</li>'; });
        html += '</ul></div>';
        container.innerHTML = html;
        mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
    }

    function renderSchemaTab(line, proc) {
        const container = document.getElementById('tab-schema');
        let html = '';
        const tables = line.tables.filter(t => proc.tables.includes(t.name));
        tables.forEach(table => {
            html += '<div class="card"><h3>' + table.name + ' <span style="color:#8c8c8c;font-size:12px;font-weight:normal">' + table.comment + '</span></h3>';
            html += '<table><thead><tr><th>字段名</th><th>类型</th><th>说明</th></tr></thead><tbody>';
            table.columns.forEach(col => {
                html += '<tr><td>' + col.name;
                if (col.isPk) html += ' <span class="pk-badge">PK</span>';
                html += '</td><td><span class="type-tag">' + col.type + '</span></td>';
                html += '<td>' + col.comment + '</td></tr>';
            });
            html += '</tbody></table>';
            html += '<div style="margin-top:12px"><div class="code-block"><button class="copy-btn" onclick="copyDDL(this)">复制</button><pre><code class="language-sql">' + escapeHtml(table.ddl) + '</code></pre></div></div>';
            html += '</div>';
        });
        container.innerHTML = html;
        container.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
    }

    function renderDataTab(line, proc) {
        const container = document.getElementById('tab-data');
        let html = '';
        const tables = line.tables.filter(t => proc.tables.includes(t.name));
        tables.forEach(table => {
            html += '<div class="card"><h3>' + table.name + ' - 模拟数据 (' + table.data.length + ' 条)</h3>';
            if (table.data.length > 0) {
                html += '<div class="data-table-wrap"><table><thead><tr>';
                table.columns.forEach(col => { html += '<th>' + col.name + '</th>'; });
                html += '</tr></thead><tbody>';
                table.data.forEach(row => {
                    html += '<tr>';
                    table.columns.forEach(col => { html += '<td>' + escapeHtml(String(row[col.name] ?? '')) + '</td>'; });
                    html += '</tr>';
                });
                html += '</tbody></table></div>';
                html += '<div style="margin-top:12px"><div class="code-block"><button class="copy-btn" onclick="copySQL(this)">复制</button><pre><code class="language-sql">' + generateInserts(table) + '</code></pre></div></div>';
            }
            html += '</div>';
        });
        container.innerHTML = html;
        container.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
    }

    function renderERTab() {
        const container = document.getElementById('tab-er');
        let erDiagram = 'erDiagram\n';
        BIZ_DATA.businessLines.forEach(line => {
            if (line.relations) {
                line.relations.forEach(rel => {
                    const connector = rel.type === '1:1' ? '||--||' : '||--o{';
                    erDiagram += '    ' + rel.from + ' ' + connector + ' ' + rel.to + ' : "' + rel.field + '"\n';
                });
            }
        });
        container.innerHTML = '<div class="card"><h3>ER 关系图</h3><div class="mermaid">' + erDiagram + '</div></div>';
        mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
        updateStats();
    }

    function updateStats() {
        let tableCount = 0;
        BIZ_DATA.businessLines.forEach(line => { tableCount += line.tables.length; });
        document.getElementById('stats').textContent =
            '📦 共 ' + BIZ_DATA.businessLines.length + ' 个业务线 · ' + tableCount + ' 张表 · 深度：' + BIZ_DATA.depth + ' · 生成时间：' + BIZ_DATA.generateTime;
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function generateInserts(table) {
        if (!table.data || table.data.length === 0) return '-- 无数据';
        let sql = '';
        table.data.forEach(row => {
            const cols = table.columns.map(c => c.name).join(', ');
            const vals = table.columns.map(c => {
                const v = row[c.name];
                if (v === null || v === undefined) return 'NULL';
                if (typeof v === 'number') return v;
                return "'" + String(v).replace(/'/g, "''") + "'";
            }).join(', ');
            sql += 'INSERT INTO ' + table.name + ' (' + cols + ') VALUES (' + vals + ');\n';
        });
        return sql;
    }

    window.copyDDL = function(btn) {
        const code = btn.nextElementSibling.querySelector('code').textContent;
        navigator.clipboard.writeText(code).then(() => { btn.textContent = '已复制'; setTimeout(() => { btn.textContent = '复制'; }, 1500); });
    };

    window.copySQL = function(btn) {
        const code = btn.nextElementSibling.querySelector('code').textContent;
        navigator.clipboard.writeText(code).then(() => { btn.textContent = '已复制'; setTimeout(() => { btn.textContent = '复制'; }, 1500); });
    };

    document.getElementById('export-btn').addEventListener('click', function() {
        const html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'biz-scenario-' + BIZ_DATA.industry + '-' + BIZ_DATA.depth + '.html';
        a.click();
        URL.revokeObjectURL(url);
    });

    init();
})();
```

- [ ] **Step 2: 提交**

```bash
git add Data-Profiling/templates/index.html
git commit -m "feat: add JS rendering logic for biz scenario simulator"
```

---

### Task 4: 编写 SKILL.md 工作流

**Files:**
- Modify: `Data-Profiling/SKILL.md` (完整重写)

- [ ] **Step 1: 写入完整 Skill 定义**

```markdown
---
name: 业务场景模拟
description: >
  输入一个行业名称和探查深度，自动生成该行业的业务场景模拟网页。
  包含业务线清单、业务流程、表结构 DDL、模拟数据、ER 关系图。
  当用户提到"业务场景"、"行业模拟"、"生成表结构"、"模拟数据"、
  "生成网页"、"数据建模"或输入行业名称时触发。
---

# 业务场景模拟

## 概述

本 Skill 接收用户输入的行业名称（如"电商"、"金融"、"医疗"）和探查深度（1/2/≥3），
通过 LLM 分步生成业务数据，注入 HTML 模板，输出一个可交互的单文件网页。

## 深度参数

| 探查次数 | 业务线数 | 每业务表数 | 流程描述 | 模拟数据量 |
|---------|---------|-----------|---------|-----------|
| 1 | 2-3 | 3-5 | 纯文字描述 | 每表 5-10 条 |
| 2 | 4-5 | 5-10 | 文字 + Mermaid 流程图 | 每表 10-20 条 |
| ≥3 | 5-8 | 10-20 | 完整流程图 + 异常分支 | 每表 20-50 条 |

## 核心工作流

### Step 1：读取模板

读取 `templates/index.html` 文件内容，作为输出 HTML 的骨架。

### Step 2：生成业务数据 JSON

根据用户输入的行业和深度，生成符合以下结构的 JSON 数据：

```json
{
  "industry": "行业名称",
  "depth": 数字,
  "generateTime": "YYYY-MM-DD HH:mm:ss",
  "businessLines": [
    {
      "name": "业务线名称",
      "description": "业务线描述",
      "processes": [
        {
          "name": "流程名称",
          "description": "流程描述",
          "flowchart": "graph LR\nA[步骤1] --> B[步骤2]",
          "tables": ["表名1", "表名2"]
        }
      ],
      "tables": [
        {
          "name": "表名",
          "comment": "表注释",
          "columns": [
            { "name": "字段名", "type": "类型", "comment": "注释", "isPk": true/false }
          ],
          "ddl": "CREATE TABLE ...;",
          "data": [{ "字段名": "值" }]
        }
      ],
      "relations": [
        { "from": "表A", "to": "表B", "type": "1:N 或 1:1", "field": "关联字段" }
      ]
    }
  ]
}
```

**生成规则：**
- 业务线名称要符合行业实际，不要编造不存在的业务
- 表命名遵循数仓规范：dim_（维度表）、dwd_（明细事实表）、dws_（汇总事实表）
- 字段命名使用 snake_case，类型使用 Hive/MySQL 常见类型
- 模拟数据要真实合理，符合业务场景
- 深度=1 时不生成 flowchart 字段

### Step 3：注入数据到模板

将生成的 JSON 数据替换模板中的 `/* BIZ_DATA_PLACEHOLDER */` 占位符。

```javascript
const BIZ_DATA = { ...生成的JSON... };
```

### Step 4：输出 HTML 文件

将填充后的 HTML 内容写入文件：

```
Data-Profiling/biz-scenario-{行业}-{时间戳}.html
```

文件名规则：`biz-scenario-{行业拼音或英文}-{YYYYMMDDHHmm}.html`

### Step 5：告知用户

输出文件路径，告知用户可以双击打开查看。

## 增量迭代

当用户要求调整深度时（如"把深度改为3"、"再深入一点"、"简化一些"）：

1. **读取已有 HTML 文件**，提取其中的 `BIZ_DATA` JSON 数据
2. **判断方向：**
   - **深化**（深度增加）：保留已有表，新增表到目标数量；已有表追加模拟数据；流程描述加深
   - **简化**（深度减少）：保留核心表，移除扩展表；模拟数据缩减到目标数量
3. **重新生成差异部分**，合并到已有数据
4. **重新注入模板**，覆盖原文件或生成新文件

## 示例

**用户输入：** 帮我生成电商行业的业务场景，深度2

**执行：**
1. 读取模板
2. 生成电商行业 JSON（商品管理、订单交易、用户中心、营销推广、物流 5 个业务线）
3. 每个业务线 5-10 张表，含 Mermaid 流程图
4. 每表 10-20 条模拟数据
5. 输出 `Data-Profiling/biz-scenario-dianshang-202605081430.html`

**用户输入：** 把深度改为3，继续深化

**执行：**
1. 读取已有 HTML，提取 BIZ_DATA
2. 深度从 2 升到 3，新增表到 10-20 张/业务线
3. 模拟数据追加到 20-50 条
4. 流程描述增加异常分支
5. 更新文件
```

- [ ] **Step 2: 提交**

```bash
git add Data-Profiling/SKILL.md
git commit -m "feat: add complete SKILL.md for biz scenario simulator"
```

---

### Task 5: 端到端测试

**Files:**
- 无新文件，验证已有文件

- [ ] **Step 1: 验证模板完整性**

```bash
cat Data-Profiling/templates/index.html | grep -c "BIZ_DATA_PLACEHOLDER"
# 期望输出: 1（有且仅有1个占位符）
```

- [ ] **Step 2: 手动注入测试数据验证渲染**

创建测试文件 `Data-Profiling/test-output.html`：

```bash
# 复制模板
cp Data-Profiling/templates/index.html Data-Profiling/test-output.html

# 用简单测试数据替换占位符（实际使用时由 LLM 生成完整数据）
# 验证双击打开后页面正常渲染
```

- [ ] **Step 3: 提交**

```bash
git add Data-Profiling/test-output.html
git commit -m "test: add test output file for biz scenario template"
```

---

## 计划自检

### 1. Spec 覆盖检查

| Spec 章节 | 对应 Task | 状态 |
|-----------|-----------|------|
| 页面布局 | Task 1, 2, 3 | ✅ |
| 技术栈（Mermaid/highlight.js CDN） | Task 1, 3 | ✅ |
| 数据模型 JSON 结构 | Task 4 | ✅ |
| 深度参数映射 | Task 4 | ✅ |
| 增量迭代机制 | Task 4 | ✅ |
| 交互细节（导航/Tab/状态栏） | Task 3 | ✅ |
| 样式规范 | Task 2 | ✅ |
| 导出功能 | Task 3 | ✅ |
| 文件输出路径 | Task 4 | ✅ |

### 2. 占位符扫描

计划中无 TBD/TODO，每个步骤包含完整代码。

### 3. 类型一致性

- `BIZ_DATA` 结构在 Task 3（JS 渲染）和 Task 4（SKILL.md 生成规则）中完全一致
- 字段名、方法名在各 Task 中统一

### 4. 范围检查

计划聚焦于单页面 HTML 生成，不包含后端/数据库/构建工具，范围清晰。
