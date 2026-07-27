# 工作流配置指南

## 结构

每个工作流是一个独立的目录，包含 `workflow.json` 配置文件。

```
workflows/
├── csms_create_proposal/     # CSMS Create Proposal Group（已激活）
│   └── workflow.json
├── gracubuy_create_gr/       # GR-Acubuy Create Goods Receipt（草稿）
│   └── workflow.json
└── schema/                   # 工作流 JSON Schema 定义
    ├── workflow-schema.json
    └── validate_workflow.py
```

## 添加新工作流

### 步骤 1: 创建目录

```
workflows/your_workflow_name/
```

### 步骤 2: 创建 workflow.json

参考现有配置创建，最少配置示例：
```json
{
  "workflow_name": "Your Workflow Name",
  "version": "1.0.0",
  "fields": {
    "Field Name": {
      "selector": "#your-css-selector",
      "type": "input",
      "required": true
    }
  }
}
```

### 步骤 3: 验证配置

```bash
python workflows/schema/validate_workflow.py workflows/your_workflow_name/workflow.json
```

### 步骤 4: 启动程序

工作流会自动出现在 GUI 下拉菜单中。

## workflow.json 配置说明

### 顶层字段

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| workflow_name | 是 | string | 工作流显示名称 |
| version | 是 | string | 语义化版本号 (如 1.0.0) |
| description | 否 | string | 工作流描述 |
| status | 否 | string | active/draft/deprecated |
| browser | 否 | object | 浏览器配置 |
| login | 否 | object | 登录配置 |
| navigation | 否 | array | 导航步骤 |
| fields | 是 | object | 表单字段定义 |
| post_fill | 否 | object | 填充后动作 |

### 支持字段类型

| 类型 | 说明 | 必需配置 |
|------|------|----------|
| input | 文本输入框 | selector |
| select | 原生 `<select>` 下拉框 | selector, handler_config |
| checkbox | 复选框 | selector |
| autocomplete | 自定义自动完成组件 | selector, handler_config.search_input_selector |
| datepicker | 日期选择器 | selector, handler_config.mode |
| popup_search | 弹窗搜索选择 | selector, handler_config.steps |
| file_upload | 文件上传 | selector, handler_config.mode |

### 字段依赖

使用 `depends_on` 指定字段依赖顺序：
```json
"Order": {
  "type": "autocomplete",
  "depends_on": "Supplier"
}
```
引擎会按拓扑顺序填充字段（Supplier 先于 Order）。

## 验证

所有配置应通过 schema 验证：
```bash
python workflows/schema/validate_workflow.py workflows/your_workflow/workflow.json
```
