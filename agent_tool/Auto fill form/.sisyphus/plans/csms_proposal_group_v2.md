# CSMS Proposal Group V2 — 新工作流创建计划

## TL;DR

> **快速摘要**: 基于录制文件 `recordings/recorder_log_20260728_192030.json`，创建一个全新的 CSMS Create Proposal Group 工作流（v2 版），包含 City 字段、附件上传配置和自动提交功能。
>
> **交付物**:
> - `workflows/csms_proposal_group_v2/workflow.json` — 完整工作流配置
> - `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx` — 参数输入 Excel 模板
> - `workflows/settings.json` — 更新注册新工作流
>
> **预估工作量**: 小
> **并行执行**: 否（文件间有依赖）
> **关键路径**: workflow.json → Excel 模板 → settings.json

---

## Context

### 原始请求
用户通过录制功能记录了一次在 CSMS 系统上填写 "Create Proposal Group" 表单的完整操作，希望基于此录制创建一个新的独立工作流，并配套 Excel 参数模板。

### 访谈总结
**关键讨论**:
- 用户要求"新增一个独立工作流"，不修改现有的 `csms_create_proposal` 工作流
- 工作流名称: **CSMS Proposal Group V2**
- 目录名: `csms_proposal_group_v2`

**录制分析发现**:
- 详见 `.sisyphus/drafts/csms_proposal_group_v2.md`

---

## Work Objectives

### 核心目标
基于录制文件创建一个功能完整的 CSMS Create Proposal Group 工作流 v2。

### 具体交付物
- [x] `workflows/csms_proposal_group_v2/workflow.json` — 工作流配置文件
- [x] `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx` — 参数输入模板
- [x] `workflows/settings.json` — 注册新工作流

### 完成标准
- [ ] 运行 `python workflows/schema/validate_workflow.py workflows/csms_proposal_group_v2/workflow.json` 通过 schema 验证
- [ ] Excel 模板列名与 workflow.json 中的字段名一致
- [ ] 启动程序后，GUI 下拉菜单中出现 "CSMS Proposal Group V2"

### Must Have
- 所有录制中出现的字段必须包含（Proposal #, City, Cust Ref. No, 等）
- 登录选择器使用录制中的精确 CSS 选择器
- 附件上传相关字段必须配置
- 与现有 csms_create_proposal 工作流完全独立

### Must NOT Have
- 不修改现有的 `csms_create_proposal/workflow.json`
- 不破坏其他工作流的注册状态

---

## Verification Strategy

> **零人工干预** — 所有验证由代理自动执行。

### 测试决策
- **测试基础设施**: 有（workflows/schema/validate_workflow.py）
- **自动化测试**: scheme 验证 + 文件存在性检查
- **验证方法**: Bash 命令直接验证

### QA 策略
每个任务执行后，立即用 Bash 工具验证：
1. 文件存在性
2. JSON 语法正确性（Python json.load）
3. Schema 验证通过
4. settings.json 格式正确

---

## Execution Strategy

### 并行执行波次

```
Wave 1 (Start Immediately - all independent):
├── Task 1: 创建 workflow.json
├── Task 2: 创建 Excel 模板
└── Task 3: 更新 settings.json

Wave FINAL (sequential verification):
├── Task F1: Schema 验证 + 完整性检查
└── Task F2: 汇总报告
```

**关键路径**: Task 1 → Task 2, Task 3 (无依赖，可并行)
**最大并发**: 3（所有 Wave 1 任务可并行）

---

## TODOs

- [ ] 1. 创建 `workflows/csms_proposal_group_v2/workflow.json`

  **做什么**:
  - 在 `workflows/csms_proposal_group_v2/` 目录下创建 `workflow.json`
  - 包含以下配置段:
    - `$schema`, `workflow_name`, `version`, `description`, `status`
    - `browser`: chrome
    - `login`: url + 录制精确选择器 fallback_selectors
    - `navigation`: goto 直接到表单页
    - `fields`: 全部 10 个字段（含 City、附件相关）
    - `attachment`: 附件配置段
    - `post_fill`: click_button 自动点 Create

  **字段配置详情**:

  | 字段名 | 类型 | 选择器 | 关键配置 |
  |--------|------|--------|----------|
  | Proposal # | input | #ctl00_ContentPlaceHolder1_txtProposalNo | post_fill: click_btnInfo + wait_upgProject |
  | City | input | #ctl00_ContentPlaceHolder1_txtCity | — |
  | Cust Ref. No | input | #ctl00_ContentPlaceHolder1_txtCustRefNo | — |
  | Proposal/Contract Value | input | #ctl00_ContentPlaceHolder1_txtContractValue | — |
  | Selling Price Currency Code | select | #ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode | trigger_postback, value_type=label |
  | Date of Award | datepicker | #ctl00_ContentPlaceHolder1_dtDateofAward_txtDate | date_format=MM/DD/YYYY |
  | Priming Project Manager | popup_search | #ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName | steps: fill→click→wait→click→click |
  | Attachment Category | select | #ctl00_ContentPlaceHolder1_wgAttachment_footer_ddlCategory1 | value_type=label |
  | Attachment File | file_upload | #ctl00_ContentPlaceHolder1_wgAttachment_footer_fileUpload0 | mode=native |
  | Attachment Description | input | #ctl00_ContentPlaceHolder1_wgAttachment_footer_txtEditDescription0 | post_fill: click lnkAdd |

  **不做什么**:
  - 不修改现有 `csms_create_proposal/workflow.json`

  **推荐代理配置**:
  - **分类**: `unspecified-low`
  - **技能**: `[]`
  - **理由**: 创建 JSON 配置文件，无需特殊技能

  **并行化**:
  - **可以并行**: YES
  - **并行组**: Wave 1（与 Task 2, 3 并行）
  - **阻塞**: 无
  - **被阻塞于**: 无

  **验收标准**:
  - [ ] 文件 `workflows/csms_proposal_group_v2/workflow.json` 存在
  - [ ] JSON 语法正确（python -c "import json; json.load(open('...'))"）
  - [ ] 包含所有 10 个字段定义
  - [ ] schema 验证通过

  **QA 场景**:

  ```
  场景: 验证 workflow.json 语法和 schema
    工具: Bash
    前置条件: 文件已创建
    步骤:
      1. python -c "import json; json.load(open('workflows/csms_proposal_group_v2/workflow.json'))"
      2. python workflows/schema/validate_workflow.py workflows/csms_proposal_group_v2/workflow.json
    预期结果: JSON 解析成功，schema 验证通过
    证据: .sisyphus/evidence/task-1-schema-valid.txt
  ```

  **提交**: NO（与 Task 2, 3 一起提交）
  - 消息: `feat(workflow): add CSMS Proposal Group V2 workflow from recording`
  - 文件: `workflows/csms_proposal_group_v2/workflow.json`

---

- [ ] 2. 创建 Excel 参数输入模板

  **做什么**:
  - 使用 openpyxl 创建 `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx`
  - 列名（与 workflow.json 字段名完全一致）:
    1. Proposal #
    2. City
    3. Cust Ref. No
    4. Proposal/Contract Value
    5. Selling Price Currency Code
    6. Date of Award
    7. Priming Project Manager
    8. Attachment Category
    9. Attachment File
    10. Attachment Description
  - 第一行为列标题（加粗）
  - 第二行为示例数据（使用录制中的值）
  - 列宽自适应内容
  - HKD, USD, SGD 等货币值旁加下拉数据验证（可选优化）

  **不做什么**:
  - 不使用 pandas（openpyxl 更适合格式控制）
  - 不添加宏或复杂公式

  **推荐代理配置**:
  - **分类**: `unspecified-low`
  - **技能**: `[]`
  - **理由**: 简单的 Excel 文件创建

  **并行化**:
  - **可以并行**: YES
  - **并行组**: Wave 1（与 Task 1, 3 并行）
  - **阻塞**: 无
  - **被阻塞于**: 无

  **验收标准**:
  - [ ] 文件 `CSMS_Proposal_Data_Template.xlsx` 存在
  - [ ] 列标题与 workflow.json 字段名一一对应
  - [ ] 示例数据行包含录制值
  - [ ] 文件可被 pandas 正常读取

  **QA 场景**:

  ```
  场景: 验证 Excel 模板格式
    工具: Bash
    前置条件: 文件已创建
    步骤:
      1. python -c "import openpyxl; wb=openpyxl.load_workbook('workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx'); ws=wb.active; print(ws.cell(1,1).value)"
      2. python -c "import pandas as pd; df=pd.read_excel('workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx'); print(df.columns.tolist())"
    预期结果: 第一列标题为 "Proposal #"，共 10 列
    证据: .sisyphus/evidence/task-2-excel-valid.txt
  ```

  **提交**: NO（与 Task 1, 3 一起提交）
  - 文件: `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx`

---

- [ ] 3. 更新 `workflows/settings.json`

  **做什么**:
  - 读取现有的 `workflows/settings.json`
  - 在 `workflow_list` 数组中添加新条目:
    ```json
    {
      "name": "csms_proposal_group_v2",
      "display_name": "CSMS Proposal Group V2"
    }
    ```
  - 不修改其他已有条目
  - 不修改 `current_workflow` 字段

  **不做什么**:
  - 不更改当前选中的工作流
  - 不影响其他工作流的配置

  **推荐代理配置**:
  - **分类**: `quick`
  - **技能**: `[]`
  - **理由**: 修改单个 JSON 文件的单行添加

  **并行化**:
  - **可以并行**: YES
  - **并行组**: Wave 1（与 Task 1, 2 并行）
  - **阻塞**: 无
  - **被阻塞于**: 无

  **验收标准**:
  - [ ] `workflows/settings.json` 包含新条目
  - [ ] JSON 语法正确
  - [ ] 其他条目未被修改
  - [ ] `current_workflow` 未改变

  **QA 场景**:

  ```
  场景: 验证 settings.json 更新
    工具: Bash
    前置条件: 文件已修改
    步骤:
      1. python -c "import json; s=json.load(open('workflows/settings.json')); names=[w['name'] for w in s['workflow_list']]; print(names)"
    预期结果: "csms_proposal_group_v2" 在 workflow_list 中
    证据: .sisyphus/evidence/task-3-settings-valid.txt
  ```

  **提交**: YES（与 Task 1, 2 一起提交）
  - 消息: `feat(workflow): add CSMS Proposal Group V2 workflow from recording`
  - 文件: `workflows/settings.json`

---

## Final Verification Wave

- [ ] F1. **完整性验证**

  **验证内容**:
  1. 运行 schema 验证
  2. 检查 Excel 列与字段名一致性
  3. 检查 settings.json 注册条目
  4. 验证所有文件存在

  输出: VERDICT: APPROVE/REJECT

- [ ] F2. **汇总报告**

  **内容**:
  - 文件列表及状态
  - 字段数量
  - 验证结果摘要
  - 使用说明

  输出: 最终报告呈现给用户

---

## Commit Strategy

- **1, 2, 3**: `feat(workflow): add CSMS Proposal Group V2 workflow from recording`
  - 文件: `workflows/csms_proposal_group_v2/workflow.json`, `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx`, `workflows/settings.json`

---

## Success Criteria

### 验证命令
```bash
python workflows/schema/validate_workflow.py workflows/csms_proposal_group_v2/workflow.json  # 预期: Validation passed
python -c "import pandas as pd; df=pd.read_excel('workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx'); print(len(df.columns))"  # 预期: 10
python -c "import json; s=json.load(open('workflows/settings.json')); print([w['name'] for w in s['workflow_list']])"  # 预期: 包含 csms_proposal_group_v2
```

### 最终检查清单
- [ ] workflow.json schema 验证通过
- [ ] Excel 模板 10 列，列名与字段名匹配
- [ ] settings.json 包含新工作流注册
- [ ] 不影响其他工作流
