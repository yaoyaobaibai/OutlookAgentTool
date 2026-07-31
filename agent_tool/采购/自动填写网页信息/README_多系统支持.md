# 多系统流程自动化 - 使用指南

## 📋 目录结构

```
自动填写网页信息/
├── systems/                    # 系统配置目录
│   ├── csms.json              # CSMS 系统配置
│   ├── acubuy.json            # Acubuy 系统配置
│   └── sap.json               # SAP 系统配置
├── flows/                      # 流程配置目录
│   ├── csms_create_proposal.json
│   ├── csms_update_contract.json
│   └── acubuy_create_pr.json
├── system_config.json          # 系统总配置
├── flow_engine.py              # 流程引擎
├── multi_system_app.py         # 多系统 GUI 主程序
└── README_多系统支持.md         # 本文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 2. 配置系统

编辑 `systems/csms.json`：

```json
{
  "system_id": "csms",
  "system_name": "CSMS",
  "base_url": "https://your-csms-url.com",  // ← 填写实际 URL
  "login": {
    "url": "/login.aspx",                    // ← 登录页路径
    "fields": {
      "username": {"selector": "#txtUsername", "type": "fill"},
      "password": {"selector": "#txtPassword", "type": "fill"},
      "submit": {"selector": "#btnLogin", "type": "click"}
    }
  }
}
```

### 3. 运行程序

```bash
python multi_system_app.py
```

---

## 🖥️ GUI 使用说明

### 界面布局

```
┌─────────────────────────────────────────────────────────┐
│  流程配置                                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 选择系统：[CSMS 🏢 ▼]  URL: https://csms...      │  │
│  │ 选择流程：[创建提案 📄 ▼]  自动创建 Proposal...   │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  变量配置                                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ proposal_no:      [P2024-001           ]          │  │
│  │ cust_ref_no:      [CR-2024-001         ]          │  │
│  │ contract_value:   [500000              ]          │  │
│  │ currency:         [USD                 ]          │  │
│  │ date_of_award:    [2024-12-31          ]          │  │
│  │ ...                                               │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  进度：[████████████████░░░░░░░░] 步骤 [2/5]: 填写信息  │
│  [▶ 开始执行] [⏹ 停止] [📂 日志] [❓ 帮助]              │
├─────────────────────────────────────────────────────────┤
│  执行日志                                                │
│  [2024-01-15 10:30:00] 加载系统配置：CSMS               │
│  [2024-01-15 10:30:01] 加载流程配置：创建提案            │
│  [2024-01-15 10:30:02] → 步骤 [1/5]: 登录系统           │
│  [2024-01-15 10:30:05] ✓ 步骤完成：登录系统             │
│  ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### 操作步骤

1. **选择系统**
   - 从下拉列表选择目标系统
   - 系统 URL 会自动显示

2. **选择流程**
   - 流程列表会根据系统自动过滤
   - 流程描述会显示在右侧

3. **配置变量**
   - 在变量配置区填写参数
   - 变量来自流程配置文件

4. **开始执行**
   - 点击"开始执行"
   - 观察进度条和日志

5. **切换系统**
   - 直接在下拉框选择另一个系统
   - 流程列表会自动更新

---

## 📝 配置文件说明

### 系统配置 (`systems/*.json`)

```json
{
  "system_id": "csms",              // 系统唯一标识
  "system_name": "CSMS",            // 系统显示名称
  "base_url": "https://...",        // 基础 URL
  "login": {                        // 登录配置
    "url": "/login.aspx",
    "fields": {
      "username": {"selector": "#txtUsername", "type": "fill"},
      "password": {"selector": "#txtPassword", "type": "fill"},
      "submit": {"selector": "#btnLogin", "type": "click"}
    },
    "success_indicator": {          // 登录成功标志
      "selector": "#dashboard",
      "timeout": 10000
    }
  },
  "selectors": {                    // 通用选择器
    "proposal_no": "#ctl00_...",
    "currency": "#ctl00_..."
  },
  "attachment_config": {            // 附件上传配置
    "category_prefix": "#ddlAttachmentCategory_",
    "file_prefix": "input[type='file'][id*='FileUpload_']",
    "desc_prefix": "#txtAttachmentDesc_"
  }
}
```

### 流程配置 (`flows/*.json`)

```json
{
  "flow_id": "csms_create_proposal",
  "flow_name": "CSMS - 创建提案",
  "system_id": "csms",              // ← 引用系统
  "version": "1.0",
  
  "browser": {                      // 浏览器配置
    "type": "chrome",
    "headless": false,
    "slow_mo": 500
  },
  
  "steps": [                        // 流程步骤
    {
      "step_id": "login",
      "name": "登录系统",
      "type": "system_login",       // 使用系统配置的登录
      "wait_after": 2000
    },
    {
      "step_id": "fill_info",
      "name": "填写信息",
      "type": "form",
      "fields": [
        {
          "name": "proposal_no",
          "selector": "{{selectors.proposal_no}}",  // 模板变量
          "value": "{{proposal_no}}",               // 用户变量
          "type": "fill"
        }
      ]
    }
  ],
  
  "variables": {                    // 变量定义
    "proposal_no": "",
    "cust_ref_no": "",
    "currency": "USD"
  }
}
```

### 系统总配置 (`system_config.json`)

```json
{
  "systems": [                      // 系统列表
    {
      "system_id": "csms",
      "system_name": "CSMS",
      "file": "csms.json",
      "icon": "🏢"
    }
  ],
  "flows": [                        // 流程列表
    {
      "flow_id": "csms_create_proposal",
      "flow_name": "CSMS - 创建提案",
      "system_id": "csms",          // ← 关联系统
      "file": "csms_create_proposal.json",
      "icon": "📄"
    }
  ]
}
```

---

## 🔄 添加新系统

### 步骤 1: 创建系统配置

在 `systems/` 目录创建 `new_system.json`：

```json
{
  "system_id": "new_system",
  "system_name": "新系统",
  "base_url": "https://new-system.com",
  "login": {
    "url": "/login",
    "fields": {
      "username": {"selector": "#user", "type": "fill"},
      "password": {"selector": "#pass", "type": "fill"},
      "submit": {"selector": "#submit", "type": "click"}
    }
  }
}
```

### 步骤 2: 更新总配置

编辑 `system_config.json`：

```json
{
  "systems": [
    {
      "system_id": "new_system",
      "system_name": "新系统",
      "file": "new_system.json",
      "icon": "🆕"
    }
  ]
}
```

### 步骤 3: 创建流程

在 `flows/` 目录创建流程配置，`system_id` 设为 `new_system`。

---

## 🎯 多系统切换示例

### 场景：CSMS → Acubuy → CSMS

1. **启动程序**
   ```
   系统：[CSMS 🏢]
   流程：[创建提案 📄]
   ```

2. **切换到 Acubuy**
   ```
   系统：[Acubuy 🛒] ← 切换
   流程：[创建 PR 🛍️]   ← 自动更新
   ```

3. **执行 Acubuy 流程**
   - 填写 PR 相关变量
   - 点击开始执行

4. **切换回 CSMS**
   ```
   系统：[CSMS 🏢] ← 切换回来
   流程：[创建提案 📄] ← 自动恢复
   ```

5. **继续执行 CSMS 流程**
   - 变量配置独立，互不影响

---

## ⚙️ 高级功能

### 变量模板

在流程配置中使用 `{{variable}}` 语法：

```json
{
  "fields": [
    {
      "selector": "{{selectors.proposal_no}}",
      "value": "{{proposal_no}}"
    }
  ]
}
```

### 日历控件处理

```json
{
  "type": "datepicker",
  "datepicker_config": {
    "trigger": "#dateBtn",
    "year": "select[id*='Year']",
    "month": "select[id*='Month']",
    "day_pattern": "a:text('{day}')"
  }
}
```

### 附件上传

```json
{
  "type": "attachments",
  "attachments": [
    {
      "category": "Proposal Document",
      "file_path": "C:\\docs\\proposal.pdf",
      "description": "Main proposal"
    }
  ]
}
```

---

## 🐛 故障排除

### Q1: 系统切换后流程列表为空
**A**: 检查流程配置的 `system_id` 是否与系统配置匹配。

### Q2: 变量配置区域为空
**A**: 检查流程配置的 `variables` 部分是否正确。

### Q3: 登录失败
**A**: 
- 检查 `base_url` 和 `login.url` 是否正确
- 验证选择器是否匹配实际页面
- 查看日志中的详细错误信息

### Q4: 找不到元素
**A**:
- 使用浏览器开发者工具 (F12) 验证选择器
- 检查页面是否完全加载
- 增加 `wait_after` 等待时间

---

## 📞 技术支持

遇到问题请：
1. 查看执行日志
2. 检查配置文件语法
3. 验证选择器是否正确
4. 联系开发团队

---

## 📄 许可证

内部工具，仅供公司使用。
