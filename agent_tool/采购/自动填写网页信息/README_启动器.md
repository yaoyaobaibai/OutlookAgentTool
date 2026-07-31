# 🚀 多系统表单工具 - 快速启动指南

## 📋 目录

1. [快速开始](#快速开始)
2. [使用说明](#使用说明)
3. [添加新系统](#添加新系统)
4. [故障排除](#故障排除)

---

## 🎯 快速开始

### 1. 启动方式

**方式 1: 双击批处理文件**
```
双击：启动多系统工具.bat
```

**方式 2: 命令行启动**
```bash
cd C:\Users\p1325970\AILearn\OutlookAgentTool\agent_tool\采购\自动填写网页信息
python multi_system_launcher.py
```

### 2. 界面说明

```
┌─────────────────────────────────────────────────────────┐
│           🚀 多系统表单工具                              │
│         选择系统和流程，启动对应的程序                   │
├─────────────────────────────────────────────────────────┤
│ 1️⃣ 选择系统                                             │
│    [🏢 CSMS ▼]                                          │
│    系统：CSMS                                           │
│    ID: csms                                             │
│    说明：Contract & Supplier Management System          │
├─────────────────────────────────────────────────────────┤
│ 2️⃣ 选择流程                                             │
│    [📄 CSMS - 创建提案 ▼]                               │
│    自动创建 Proposal Group                              │
├─────────────────────────────────────────────────────────┤
│ 3️⃣ 选择程序                                             │
│    ⚙️ 自动推荐 (已选中)                                 │
│    📄 提案创建 (auto_create_proposal.py)                │
│    📝 表单填写 (form_filler.py)                         │
├─────────────────────────────────────────────────────────┤
│          [🚀 启动程序] [📂 打开配置] [❓ 帮助]          │
├─────────────────────────────────────────────────────────┤
│ 📋 日志                                                 │
│ [10:30:00] 启动器已就绪                                 │
│ [10:30:15] 已选择系统：CSMS                             │
│ [10:30:45] 启动程序：auto_create_proposal.py           │
│ [10:30:46] ✓ 程序已启动                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📖 使用说明

### 步骤 1: 选择系统

从下拉列表中选择目标系统：
- **🏢 CSMS** - Contract & Supplier Management System
- **🛒 Acubuy** - Procurement Management System
- **📊 SAP** - SAP ERP System

### 步骤 2: 选择流程

根据选择的系统，流程列表会自动过滤：

**CSMS 系统流程:**
- 📄 CSMS - 创建提案
- 📝 CSMS - 更新合同

**Acubuy 系统流程:**
- 🛍️ Acubuy - 创建采购申请

### 步骤 3: 选择程序

**三种选择:**

1. **⚙️ 自动推荐** (推荐)
   - 根据流程自动选择最合适的程序
   - 创建提案 → auto_create_proposal.py
   - 其他流程 → form_filler.py

2. **📄 提案创建**
   - 强制启动 auto_create_proposal.py
   - 适用于 CSMS 提案创建

3. **📝 表单填写**
   - 强制启动 form_filler.py
   - 适用于通用表单填写

### 步骤 4: 启动程序

点击 **🚀 启动程序** 按钮：
- 启动对应的 Python 程序
- 启动器自动最小化
- 日志显示启动状态

---

## ➕ 添加新系统

### 步骤 1: 创建系统配置文件

在 `systems/` 目录创建 `new_system.json`:

```json
{
  "system_id": "new_system",
  "system_name": "新系统名称",
  "description": "系统描述",
  "base_url": "https://new-system.com",
  "login": {
    "url": "/login",
    "fields": {
      "username": {"selector": "#username", "type": "fill"},
      "password": {"selector": "#password", "type": "fill"},
      "submit": {"selector": "#loginBtn", "type": "click"}
    }
  },
  "selectors": {
    "field1": "#actualSelector1",
    "field2": "#actualSelector2"
  },
  "programs": {
    "proposal": "auto_create_proposal.py",
    "form": "form_filler.py"
  }
}
```

### 步骤 2: 更新系统总配置

编辑 `system_config.json`,在 `systems` 数组中添加:

```json
{
  "system_id": "new_system",
  "system_name": "新系统",
  "file": "systems/new_system.json",
  "icon": "🆕",
  "description": "系统描述",
  "programs": {
    "proposal": "auto_create_proposal.py",
    "form": "form_filler.py"
  }
}
```

### 步骤 3: (可选) 添加流程

在 `flows/` 目录创建流程配置文件，然后在 `system_config.json` 的 `flows` 数组中添加流程信息。

### 步骤 4: 重启启动器

重新启动 `multi_system_launcher.py`,新系统会出现在下拉列表中。

---

## 🔧 故障排除

### Q1: 启动器无法启动

**症状**: 双击批处理文件后闪退

**解决方案**:
```bash
# 1. 检查 Python 安装
python --version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 手动启动查看错误
python multi_system_launcher.py
```

### Q2: 系统配置加载失败

**症状**: 启动后显示"system_config.json 不存在"

**解决方案**:
1. 检查 `system_config.json` 是否在正确目录
2. 运行启动器会自动创建默认配置
3. 手动编辑配置文件，确保 JSON 格式正确

### Q3: 程序启动失败

**症状**: 点击"启动程序"后无反应

**解决方案**:
1. 检查日志区域的错误信息
2. 确认 `auto_create_proposal.py` 和 `form_filler.py` 存在
3. 检查 Python 路径是否正确

### Q4: 系统切换后流程列表为空

**原因**: 该系统的流程配置未添加

**解决方案**:
1. 在 `system_config.json` 的 `flows` 数组中添加流程
2. 确保流程的 `system_id` 与系统配置匹配

---

## 📁 文件结构

```
自动填写网页信息/
├── multi_system_launcher.py    # 启动器（新增）
├── system_config.json          # 系统总配置
├── 启动多系统工具.bat          # 快速启动脚本
├── systems/                     # 系统配置目录
│   ├── csms.json
│   ├── acubuy.json
│   └── sap.json
├── flows/                       # 流程配置目录
│   ├── csms_create_proposal.json
│   ├── csms_update_contract.json
│   └── acubuy_create_pr.json
├── form_filler.py              # 表单填写工具（现有）
├── auto_create_proposal.py     # 提案创建工具（现有）
├── form_config.json            # 表单配置（现有）
└── attachment_config.json      # 附件配置（现有）
```

---

## 🎓 最佳实践

### 1. 使用自动推荐

让启动器根据流程自动选择程序，减少手动操作。

### 2. 配置文件版本控制

使用 Git 管理配置文件，便于团队协作和版本追溯。

### 3. 定期备份配置

定期备份 `system_config.json` 和 `systems/` 目录。

### 4. 测试新系统

添加新系统后，先测试基本功能，再投入使用。

---

## 📞 技术支持

如有问题，请：
1. 查看日志区域的错误信息
2. 检查配置文件格式
3. 联系开发团队

---

**版本**: 1.0  
**更新日期**: 2024-01-15
