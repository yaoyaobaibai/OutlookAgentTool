# Priming Project Manager 配置说明

## 🔍 LoginID 从哪里读取？

程序会从以下两个来源读取 Project Manager 的 LoginID：

### 方式 1：字段配置的默认值（推荐）

在添加字段时直接填写 LoginID 作为默认值：

**添加字段步骤**：
1. 点击"添加字段"
2. 填写：
   - **字段名称**：`Priming Project Manager`
   - **CSS 选择器**：`#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName`
   - **默认值**：`lin.zu`（你的 LoginID）
3. 点击"确定"

**优点**：
- ✅ 固定使用同一个 Project Manager
- ✅ 不需要在 Excel 中重复填写
- ✅ 配置一次，永久使用

---

### 方式 2：从 Excel 文件读取

如果你需要为不同的 Proposal 指定不同的 Project Manager，可以在 Excel 中添加一列：

**Excel 文件内容**：
```excel
Proposal #,Cust Ref. No,Proposal/Contract Value,Currency Code,Date of Award,Priming Project Manager
P12345,CR-2024-001,500000,USD,01/15/2024,lin.zu
P12346,CR-2024-002,750000,SGD,02/20/2024,wang.fang
P12347,CR-2024-003,1200000,EUR,03/10/2024,li.ming
```

**字段配置**：
```
字段名称：Priming Project Manager
CSS 选择器：#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName
默认值：（留空或不填）
```

**注意**：
- ⚠️ Excel 列名必须与字段名称**完全一致**
- ⚠️ 填写的是 LoginID（如：`lin.zu`），不是中文名字

---

## 📝 完整配置示例

### 场景 1：固定使用同一个 Project Manager

**配置字段**（在程序界面）：
```
1. Proposal #
   CSS 选择器：#ctl00_ContentPlaceHolder1_txtProposalNo
   默认值：（从 Excel 读取）

2. Cust Ref. No
   CSS 选择器：#ctl00_ContentPlaceHolder1_txtCustRefNo
   默认值：（从 Excel 读取）

3. Proposal/Contract Value
   CSS 选择器：#ctl00_ContentPlaceHolder1_txtContractValue
   默认值：（从 Excel 读取）

4. Selling Price Currency Code
   CSS 选择器：#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode
   默认值：（从 Excel 读取）

5. Date of Award
   CSS 选择器：#ctl00_ContentPlaceHolder1_dtDateofAward_txtDate
   默认值：（从 Excel 读取）

6. Priming Project Manager
   CSS 选择器：#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName
   默认值：lin.zu  ← 固定使用这个 LoginID
```

**Excel 文件**（不需要 Priming Project Manager 列）：
```excel
Proposal #,Cust Ref. No,Proposal/Contract Value,Currency Code,Date of Award
P12345,CR-2024-001,500000,USD,01/15/2024
P12346,CR-2024-002,750000,SGD,02/20/2024
```

---

### 场景 2：每个 Proposal 使用不同的 Project Manager

**配置字段**（在程序界面）：
```
1-5. 同上（其他必填字段）

6. Priming Project Manager
   CSS 选择器：#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName
   默认值：（留空，从 Excel 读取）
```

**Excel 文件**（包含 Priming Project Manager 列）：
```excel
Proposal #,Cust Ref. No,Proposal/Contract Value,Currency Code,Date of Award,Priming Project Manager
P12345,CR-2024-001,500000,USD,01/15/2024,lin.zu
P12346,CR-2024-002,750000,SGD,02/20/2024,wang.fang
P12347,CR-2024-003,1200000,EUR,03/10/2024,li.ming
```

---

## 🎯 执行流程

当程序处理到 "Priming Project Manager" 字段时：

1. **检测字段名称**
   - 包含 "Project Manager" 或 "Priming Project Manager"
   
2. **获取 LoginID**
   - 从字段的 `value` 属性读取
   - 这个值来自于：
     - 字段配置的默认值，或
     - Excel 中对应列的值

3. **打开搜索弹窗**
   - 点击放大镜按钮
   - 等待弹窗打开

4. **填写 LoginID**
   ```python
   login_id_input = popup.locator('#txtOAID')
   login_id_input.fill(pm_field['value'])  # 这里使用读取到的 LoginID
   ```

5. **搜索并选择**
   - 点击 Search 按钮
   - 等待搜索结果
   - 选择第一个结果
   - 点击 Select 确认

---

## 📊 日志输出示例

```
>>> 步骤 3: 选择 Priming Project Manager
  点击搜索按钮打开弹窗...
  搜索弹窗已打开
  已输入 LoginID: lin.zu  ← 这里显示实际使用的 LoginID
  已点击 Search 按钮
  已选择第一个搜索结果
  已点击 Select 按钮
```

---

## ⚠️ 常见问题

### Q1: 不知道 LoginID 是什么？
**A**: 
- LoginID 通常是员工的用户名
- 格式如：`lin.zu`, `wang.fang`
- 可以询问系统管理员或 HR

### Q2: 搜索不到用户？
**A**: 
- 检查 LoginID 是否正确
- 确认用户是否在职
- 确认用户是否有系统访问权限

### Q3: 弹窗没有打开？
**A**: 
- 浏览器可能阻止了弹窗
- 允许浏览器弹出窗口
- 检查网络连接

### Q4: 选择了错误的 Project Manager？
**A**: 
- 程序会选择搜索结果的**第一个**
- 确保 LoginID 搜索后，第一个结果就是目标用户
- 如果需要更精确的选择，需要修改代码逻辑

---

## 🔧 修改选择逻辑（高级）

如果需要选择特定行的结果（不是第一个），可以修改代码：

```python
# 原代码：选择第一个结果
first_row = popup.locator('table tr').nth(1)

# 修改为：选择第二个结果
second_row = popup.locator('table tr').nth(2)

# 或者：根据名字选择
rows = popup.locator('table tr')
for i in range(rows.count()):
    row = rows.nth(i)
    if row.text_content().contains('目标名字'):
        row.click()
        break
```

---

## 📋 快速配置步骤

### 方法 1：固定 LoginID（推荐）

1. 运行程序
2. 点击"添加字段"
3. 填写：
   - 字段名称：`Priming Project Manager`
   - CSS 选择器：`#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName`
   - **默认值：`lin.zu`**（你的 LoginID）
4. 点击"确定"
5. 完成！

### 方法 2：从 Excel 读取

1. 修改 Excel 文件，添加 "Priming Project Manager" 列
2. 填写每个 Proposal 对应的 LoginID
3. 在程序中添加字段（默认值留空）
4. 完成！

---

**最后更新**: 2026-07-22  
**版本**: 1.2
