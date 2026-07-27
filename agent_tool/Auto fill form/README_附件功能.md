# 表单自动填充工具 - 附件上传功能说明

## 功能概述

基于现有的 `form_filler.py` 程序，新增了附件上传管理功能。程序现在可以：

1. ✅ 从 Excel 文件读取表单字段值
2. ✅ 自动填充网页表单
3. ✅ **新增**：管理多个附件（添加、编辑、删除）
4. ✅ **新增**：自动上传附件到网页表单

## 新增功能

### 1. 附件管理界面

程序主界面下方新增了"附件上传管理"区域，包含：

- **附件列表**：显示所有已添加的附件
  - Category：附件类别（下拉选择）
  - File Path：文件路径
  - Description：描述信息

- **操作按钮**：
  - 添加附件：打开对话框添加新附件
  - 编辑附件：修改选中的附件信息
  - 删除附件：删除选中的附件

### 2. 附件配置保存

附件信息保存在 `attachment_config.json` 文件中，格式如下：

```json
{
  "attachments": [
    {
      "category": "Proposal Document",
      "file_path": "C:\\Documents\\proposal.pdf",
      "description": "项目建议书"
    },
    {
      "category": "Contract",
      "file_path": "C:\\Documents\\contract.docx",
      "description": "合同文件"
    }
  ]
}
```

### 3. 自动上传流程

程序在执行表单填充时，会按以下顺序处理附件：

1. 填充所有普通表单字段
2. 遍历附件列表
3. 对每个附件：
   - 选择对应的 Category（下拉框）
   - 上传文件（文件选择框）
   - 填写 Description（文本框）

## 使用方法

### 步骤 1：准备 Excel 文件

创建 Excel 文件，包含以下列名（与字段名称对应）：

| Proposal # | Cust Ref. No | Proposal/Contract Value | Selling Price Currency Code | Date of Award |
|------------|--------------|------------------------|----------------------------|---------------|
| P12345     | CR-2024-001  | 500000                 | USD                        | 01/15/2024    |

### 步骤 2：配置表单字段

在程序中添加工单字段（使用实际的选择器）：

```
字段名称：Proposal #
CSS 选择器：#ctl00_ContentPlaceHolder1_txtProposalNo
默认值：(从 Excel 读取)

字段名称：Cust Ref. No
CSS 选择器：#ctl00_ContentPlaceHolder1_txtCustRefNo
默认值：(从 Excel 读取)

字段名称：Proposal/Contract Value
CSS 选择器：#ctl00_ContentPlaceHolder1_txtContractValue
默认值：(从 Excel 读取)

字段名称：Selling Price Currency Code
CSS 选择器：#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode
默认值：(从 Excel 读取)

字段名称：Date of Award
CSS 选择器：#ctl00_ContentPlaceHolder1_dtDateofAward_txtDate
默认值：(从 Excel 读取)
```

### 步骤 3：添加附件

1. 点击"添加附件"按钮
2. 在弹出的对话框中：
   - 选择 Category（附件类别）
   - 点击"浏览"选择文件
   - 填写 Description（可选）
3. 点击"确定"保存

### 步骤 4：执行自动化

1. 输入目标网址（登录页面）
2. 选择浏览器类型
3. 选择 Excel 文件
4. 点击"启动填充"

程序会自动：
- 打开浏览器并访问登录页面
- 等待用户手动登录
- 导航到 Create Proposal Group 页面
- 填写所有表单字段（从 Excel 读取）
- 上传所有附件
- 完成填充（不自动提交）

## 附件上传的选择器配置

如果网页表单的附件上传区域选择器与默认不同，需要手动添加字段：

### 方式 1：使用默认选择器模式

程序默认使用以下选择器模式（`i` 为附件序号，从 1 开始）：

- Category 下拉框：`select[name='category_{i}']`
- 文件上传：`input[type='file'][name='file_{i}']`
- Description 文本框：`textarea[name='desc_{i}']`

### 方式 2：手动添加字段（推荐）

如果选择器不同，手动添加三个字段：

```
字段名称：Attachment 1 - Category
CSS 选择器：#actual_category_selector_1
默认值：Proposal Document

字段名称：Attachment 1 - File
CSS 选择器：file:#actual_file_input_1
默认值：C:\path\to\file.pdf

字段名称：Attachment 1 - Description
CSS 选择器：#actual_description_1
默认值：项目建议书文件
```

**注意**：文件上传字段的选择器需要添加 `file:` 前缀，程序会识别并特殊处理。

## 实际页面的选择器（基于 HTML 文件）

根据提供的 `create pg.html` 文件，关键选择器如下：

```
Proposal #: #ctl00_ContentPlaceHolder1_txtProposalNo
GET CRM INFO 按钮：#ctl00_ContentPlaceHolder1_btnInfo
Cust Ref. No: #ctl00_ContentPlaceHolder1_txtCustRefNo
Proposal/Contract Value: #ctl00_ContentPlaceHolder1_txtContractValue
Currency Code: #ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode
Date of Award: #ctl00_ContentPlaceHolder1_dtDateofAward_txtDate
Create 按钮：#ctl00_ContentPlaceHolder1_btnInsert
```

## 常见问题

### Q1: 附件上传失败？
**A**: 检查：
1. 文件路径是否正确
2. 网页表单的附件上传区域选择器是否正确
3. 是否需要先点击某个按钮展开附件上传区域

### Q2: 如何配置多个附件？
**A**: 依次点击"添加附件"，每个附件独立配置。程序会按顺序上传。

### Q3: Excel 中的列名必须和字段名称完全一致吗？
**A**: 是的，列名必须与字段名称完全匹配（区分大小写）。

### Q4: 可以自动点击 Create 按钮吗？
**A**: 可以。在 `_fill_form` 方法的最后添加：
```python
create_btn = self.page.locator('#ctl00_ContentPlaceHolder1_btnInsert')
create_btn.click()
```

## 配置文件说明

### form_config.json
存储表单字段配置：
```json
{
  "fields": [
    {
      "label": "Proposal #",
      "selector": "#ctl00_ContentPlaceHolder1_txtProposalNo",
      "value": "P12345"
    }
  ]
}
```

### attachment_config.json
存储附件配置：
```json
{
  "attachments": [
    {
      "category": "Proposal Document",
      "file_path": "C:\\path\\to\\file.pdf",
      "description": "项目建议书"
    }
  ]
}
```

## 运行示例

```bash
python form_filler.py
```

1. 输入目标网址：`https://csmstest.ncs.com.sg/UAT/`
2. 选择浏览器：Google Chrome
3. 选择 Excel 文件：`proposal_data.xlsx`
4. 添加附件（可选）
5. 点击"启动填充"

## 注意事项

1. **登录页面**：程序会打开登录页面，需要手动输入用户名密码（防止验证码）
2. **文件路径**：使用绝对路径，避免路径问题
3. **浏览器驱动**：确保已安装 Playwright (`pip install playwright`)
4. **浏览器安装**：首次运行需要安装浏览器 (`playwright install`)
5. **附件选择器**：根据实际网页结构调整附件上传区域的选择器

## 技术支持

如有问题，请检查：
1. 控制台输出的详细日志
2. 浏览器开发者工具中的元素选择器
3. Excel 文件格式是否正确
