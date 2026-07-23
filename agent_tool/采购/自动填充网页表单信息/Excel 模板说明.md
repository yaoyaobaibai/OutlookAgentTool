# Excel 数据模板说明

## 📥 模板文件位置

**CSV 模板**：`Proposal_Data_Template.csv`

你可以：
1. 直接用 Excel 打开此 CSV 文件
2. 另存为 `.xlsx` 格式
3. 或使用此 CSV 文件（程序支持 CSV 和 XLSX）

---

## 📊 模板结构

### 列名说明

| 列名 | 必填 | 说明 | 示例 | 格式要求 |
|------|------|------|------|----------|
| **Proposal #** | ✅ | 提案编号 | P12345 | 文本 |
| **Cust Ref. No** | ✅ | 客户参考号 | CR-2024-001 | 文本 |
| **Proposal/Contract Value** | ✅ | 提案/合同金额 | 500000 | 数字（不带符号） |
| **Currency Code** | ✅ | 货币代码 | USD | 从下拉列表选择 |
| **Date of Award** | ✅ | 中标日期 | 01/15/2024 | MM/DD/YYYY |
| HQ BC Recog. | ❌ | 总部业务确认 | Sales Team | 文本 |
| **Tender Type** | ❌ | 招标类型 | Open | Open 或 Closed |
| End-Customer City | ❌ | 最终客户城市 | Singapore | 文本 |
| Project Number | ❌ | 项目编号 | PRJ-001 | 文本 |

---

## 📝 示例数据

```
Proposal #,Cust Ref. No,Proposal/Contract Value,Currency Code,Date of Award,HQ BC Recog.,Tender Type,End-Customer City,Project Number
P12345,CR-2024-001,500000,USD,01/15/2024,Sales Team,Open,Singapore,PRJ-001
P12346,CR-2024-002,750000,SGD,02/20/2024,Marketing,Closed,Kuala Lumpur,PRJ-002
P12347,CR-2024-003,1200000,EUR,03/10/2024,Business Dev,Open,Jakarta,PRJ-003
```

---

## 💡 货币代码选项

| 代码 | 货币名称 | 代码 | 货币名称 |
|------|---------|------|---------|
| USD | 美元 | SGD | 新加坡元 |
| EUR | 欧元 | MYR | 马来西亚林吉特 |
| CNY | 人民币 | GBP | 英镑 |
| JPY | 日元 | AUD | 澳元 |
| HKD | 港币 | INR | 印度卢比 |
| KRW | 韩元 | CHF | 瑞士法郎 |
| CAD | 加拿大元 | BRL | 巴西雷亚尔 |
| MXN | 墨西哥比索 | ZAR | 南非兰特 |
| THB | 泰铢 | IDR | 印尼盾 |

---

## 📋 使用步骤

### 步骤 1：打开模板
用 Excel 打开 `Proposal_Data_Template.csv`

### 步骤 2：填写数据
从第 2 行开始填写你的数据：
- 第 1 行是表头（不要修改）
- 第 2 行开始是数据行
- 可以填写多行数据

### 步骤 3：保存文件
- **推荐**：另存为 `.xlsx` 格式
- 或者直接使用 `.csv` 格式

### 步骤 4：在程序中使用
1. 运行 FormFiller 程序
2. 点击"浏览"按钮
3. 选择保存的 Excel/CSV 文件
4. 点击"启动填充"

---

## ⚠️ 注意事项

### ✅ 正确的格式
```
Proposal #      → P12345
Cust Ref. No    → CR-2024-001
Value           → 500000
Currency Code   → USD
Date of Award   → 01/15/2024
```

### ❌ 错误的格式
```
Proposal #      → P-12345 (不要带特殊符号)
Cust Ref. No    → CR/2024/001 (使用标准格式)
Value           → $500,000 (不要带货币符号和逗号)
Currency Code   → usd (必须大写)
Date of Award   → 2024-01-15 (必须是 MM/DD/YYYY)
```

---

## 🔧 常见问题

### Q1: 列名可以修改吗？
**A**: ❌ 不可以。列名必须与模板完全一致，否则程序无法识别。

### Q2: 可以删除某些列吗？
**A**: 
- 必填列（前 5 列）不能删除
- 可选列可以删除，程序会跳过

### Q3: 可以添加其他列吗？
**A**: ✅ 可以。程序只会读取它需要的列，其他列会被忽略。

### Q4: 日期格式不对会怎样？
**A**: 程序可能无法正确填充。请确保使用 **MM/DD/YYYY** 格式。

### Q5: 金额可以带小数点吗？
**A**: ✅ 可以。例如：`500000.50`

---

## 📊 在 Excel 中创建下拉列表（可选）

### 为 Currency Code 创建下拉列表：
1. 选中 D 列（Currency Code 列）的数据区域
2. 点击"数据" → "数据验证"
3. 选择"列表"
4. 输入：`USD,SGD,EUR,CNY,GBP,JPY,AUD,HKD,INR,KRW,CHF,CAD,BRL,MXN,ZAR,THB,IDR,MYR`
5. 点击"确定"

### 为 Tender Type 创建下拉列表：
1. 选中 G 列（Tender Type 列）的数据区域
2. 点击"数据" → "数据验证"
3. 选择"列表"
4. 输入：`Open,Closed`
5. 点击"确定"

---

## 📥 快速开始模板

复制以下内容到 Excel，保存为 `Proposal_Data.xlsx`：

| Proposal # | Cust Ref. No | Proposal/Contract Value | Currency Code | Date of Award | HQ BC Recog. | Tender Type | End-Customer City | Project Number |
|------------|--------------|------------------------|---------------|---------------|--------------|-------------|-------------------|----------------|
| P12345 | CR-2024-001 | 500000 | USD | 01/15/2024 | Sales Team | Open | Singapore | PRJ-001 |
|            |              |                        |               |               |              |             |                   |                |
|            |              |                        |               |               |              |             |                   |                |
|            |              |                        |               |               |              |             |                   |                |

---

## 🎯 完整示例

### 示例 1：新加坡项目
```
Proposal #: SIN-2024-001
Cust Ref. No: DBS-2024-Q1
Proposal/Contract Value: 850000
Currency Code: SGD
Date of Award: 03/01/2024
HQ BC Recog.: Financial Services
Tender Type: Open
End-Customer City: Singapore
Project Number: FIN-DBS-001
```

### 示例 2：马来西亚项目
```
Proposal #: MYS-2024-005
Cust Ref. No: MAY-2024-002
Proposal/Contract Value: 450000
Currency Code: MYR
Date of Award: 03/15/2024
HQ BC Recog.: Manufacturing
Tender Type: Closed
End-Customer City: Kuala Lumpur
Project Number: MFG-KL-005
```

---

## 📞 需要帮助？

如遇到问题：
1. 检查列名是否与模板完全一致
2. 确认日期格式为 MM/DD/YYYY
3. 确保货币代码大写
4. 查看程序控制台的错误信息

---

**文件位置**: `C:\Users\p1325970\AILearn\采购\自动填充网页表单信息\Proposal_Data_Template.csv`

**最后更新**: 2026-07-22
