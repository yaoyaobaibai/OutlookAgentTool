# GR-Acubuy Create Goods Receipt 完整工作流（gracubuy_gr_flow）

## TL;DR

> **Quick Summary**: 基于录制 `recorder_log_20260731_140316.json` 构建 GR-Acubuy Create Goods Receipt 完整 4 阶段自动化工作流。扩展引擎支持多阶段（stages）执行，新建 `workflows/gracubuy_gr_flow/` 工作流（含 workflow.json 内嵌字段配置 + Excel 数据模板），注册到 settings.json。
>
> **Deliverables**:
> - `workflows/schema/workflow-schema.json` — 新增可选 `stages` 数组定义（每阶段含 navigation/fields/post_fill）
> - `workflow_engine.py` — `execute()` 检测 stages 逐阶段执行，无 stages 走旧逻辑（向后兼容）
> - `workflows/gracubuy_gr_flow/workflow.json` — 完整 4 阶段工作流（顶层 fields 汇总 + stages 执行序列）
> - `workflows/gracubuy_gr_flow/GR_Goods_Receipt_Data_Template.xlsx` — 字段值 Excel 模板
> - `workflows/settings.json` — 注册新工作流
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: schema/stages → engine/stages → workflow.json → Excel 模板 → 验证

---

## Context

### Original Request
用户提供 Acubuy 系统（Singtel iValua）的操作录制，要求起草一份**从登录之后开始**的工作流，最终转成程序可用形态：工作流文件（workflow.json 合一含字段配置）+ 字段值 Excel 模板。

### Interview Summary
**Key Discussions**:
- 流程范围：**完整 4 阶段**（① 填创建表单+Save ② 编辑明细数量 ③ 工作流推进按钮 ④ 选审批人+Save），全部自动化
- 文件组织：**新建独立目录** `workflows/gracubuy_gr_flow/`（不复用现有 gracubuy_create_gr draft）
- 交付形态：workflow.json **合一**（内嵌 fields 配置）+ 独立 Excel 模板
- 多阶段支持：**扩展 schema + engine 支持 stages**（选项 1），旧工作流不受影响
- browser.channel：待定（录制是 Edge，schema 支持 chrome/msedge/chromium）→ **默认 msedge**（与录制一致，可覆盖）

**Research Findings**:
- 现有 `WorkflowEngine.execute()` 是单轮 `login → navigation → fields → post_fill`（workflow_engine.py:102-157）
- `form_filler.py` 的 `get_field_definitions()` 读顶层 `fields`；`_build_field_values()` 用 `df.iloc[0]` 按列名（= 字段 label）取值 —— **stages 方案必须顶层保留 fields 汇总**
- `autocomplete_handler.py` 读 `search_input_selector`（非 schema 的 `search_selector`，命名不一致），且**不支持"搜索值 ≠ 选中值"两步交互**
- `file_upload_handler.py` 支持 `html5_uploader` 模式（upload_button_selector + file_input_selector）
- 录制中 modal.aspx 触发 `frame_loaded` → 弹窗是 frame/iframe，但 input handler 无 iframe 支持（schema 已有 iframe_selector 字段）
- Excel 模板参考：`workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx`（Sheet1，第1行 header=字段名，第2行=示例值）

### Metis Review
**Identified Gaps** (addressed):
- stages 扩展的 GUI 兼容：顶层保留汇总 fields，GUI/Excel 映射不变
- autocomplete 两步交互：Order 需支持"搜索编号 → 选择 PO"（search_value + 匹配选择）
- modal/iframe 处理：Quantity 字段需要 iframe 上下文
- Excel 字段名跨阶段唯一性：6 字段无冲突，已确认
- 中文审批人/Unicode：Excel 模板需 UTF-8，匹配用包含式（has-text）

---

## Work Objectives

### Core Objective
将录制中的 4 阶段 GR 创建流程固化为可被 FormFiller 程序执行的工作流，含数据模板。

### Concrete Deliverables
1. `workflows/schema/workflow-schema.json` 新增 `stages` 定义（向后兼容）
2. `workflow_engine.py` 支持 stages 逐阶段执行
3. `workflows/gracubuy_gr_flow/workflow.json`（4 阶段完整配置）
4. `workflows/gracubuy_gr_flow/GR_Goods_Receipt_Data_Template.xlsx`
5. `workflows/settings.json` 注册 `gracubuy_gr_flow`

### Definition of Done
- [ ] `python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json` → exit 0
- [ ] 现有工作流（csms_create_proposal、csms_proposal_group_v2）加载验证仍通过（向后兼容）
- [ ] Excel 模板列名与 workflow.json fields keys 完全一致
- [ ] 引擎单测覆盖：单轮（旧）与多阶段（新）两条路径

### Must Have
- 4 阶段完整自动化：创建→明细编辑→推进→审批人
- 登录后开始（login.enabled=false，或由外部 SSO 完成）
- Order 两步交互：搜索 `6000017449` → 选中 `PO0147739`
- 明细编辑弹窗（modal.aspx frame）内 Quantity 改为 100
- 审批人 Amy Yin - (Band C) 选择

### Must NOT Have (Guardrails)
- 不破坏现有 3 个工作流的加载与执行（向后兼容是硬约束）
- 不在本计划中实现 Acubuy 的 SSO 自动登录（登录由人工/外部完成）
- 不改 `form_filler.py` GUI（顶层 fields 汇总方案保证 GUI 无需改动）
- 不为通用性引入过度抽象（只加 stages 机制，不加通用 DSL）

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES（tests/csms_regression.py, tests/test_integration.py 存在，但用 pytest）
- **Automated tests**: TDD for engine stages；tests-after for workflow.json/Excel
- **Framework**: pytest
- **TDD**: stages 引擎任务按 RED（失败测试）→ GREEN（实现）→ REFACTOR

### QA Policy
每个任务含 Agent-Executed QA Scenarios，证据存 `.sisyphus/evidence/`。

- **API/Backend**: Bash(python) 运行 pytest / validate_workflow.py / 读取 Excel 断言
- **Library**: Bash(python) import 模块，调用函数断言结果

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 独立并行):
├── Task 1: workflow-schema.json 新增 stages 定义 [quick]
├── Task 2: 引擎 stages 执行支持（TDD） [deep]
├── Task 3: autocomplete handler 两步交互增强 [deep]
├── Task 4: file_upload handler html5_uploader 验证/修正 [quick]
├── Task 5: input handler iframe 支持 [quick]
└── Task 6: settings.json 注册 gracubuy_gr_flow [quick]

Wave 2 (After Wave 1 - 依赖 schema/引擎契约):
├── Task 7: workflow.json 4 阶段配置 [deep]
└── Task 8: Excel 数据模板 [quick]

Wave 3 (After Wave 2 - 集成验证):
└── Task 9: 端到端验证（schema 校验 + 引擎单测 + Excel 映射断言） [unspecified-high]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 7 → Task 8 → Task 9 → F1-F4 → user okay
Parallel Speedup: ~55% faster than sequential
Max Concurrent: 6 (Wave 1)
```

### Dependency Matrix

- **1**: - - 7, 9
- **2**: - - 7, 9
- **3**: - - 7, 9
- **4**: - - 7, 9
- **5**: - - 7, 9
- **6**: - - 9
- **7**: 1, 2, 3, 4, 5 - 8, 9
- **8**: 7 - 9
- **9**: 7, 8, 6 - F1-F4

### Agent Dispatch Summary

- **1**: **6** - T1 → `quick`, T2 → `deep`, T3 → `deep`, T4 → `quick`, T5 → `quick`, T6 → `quick`
- **2**: **2** - T7 → `deep`, T8 → `quick`
- **3**: **1** - T9 → `unspecified-high`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. workflow-schema.json 新增 stages 定义

  **What to do**:
  - 在 `workflows/schema/workflow-schema.json` 顶层 `properties` 新增 `stages`（可选，不加入 required，保证向后兼容）：
    ```json
    "stages": {
      "type": "array",
      "description": "Ordered list of execution phases. Each stage has its own navigation/fields/post_fill. When present, the engine executes stages sequentially instead of the single top-level round.",
      "items": {
        "$ref": "#/$defs/stage_config"
      }
    }
    ```
  - 在 `$defs` 新增 `stage_config`：`{name, navigation[], fields, post_fill{}}`。**关键契约**：`fields` 使用 **string 数组**（字段名列表，引用顶层 `fields` 的 key），而非对象形态 —— 顶层 `fields` 是唯一事实源，GUI 显示/Excel 映射/引擎执行全部引用同一份配置（此契约由 Task 7 约定，Task 1 实现 schema 时必须支持此形态）：
    ```json
    "stage_config": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "name": { "type": "string" },
        "navigation": { "type": "array", "items": { "$ref": "#/$defs/navigation_step" } },
        "fields": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Field names referencing keys in the top-level 'fields' map. The engine executes them in order."
        },
        "post_fill": { "$ref": "#/$defs/post_fill" }
      },
      "required": ["fields"]
    }
    ```
  - 若采用 jsonschema 库严格校验，注意顶层 `post_fill`（properties.post_fill）与 `$defs` 中复用的定义：stage 的 post_fill 复用与顶层相同的结构（action 枚举 `manual_review`/`click_button` 即可覆盖本工作流需求）
  - 用 jsonschema 自测：构造一个含 stages 的样例 workflow（fields 为 string 数组），验证通过；构造含非法 stage 字段的样例，验证报错。
  - 注意：顶层 `fields` 仍需保留（GUI 和 Excel 映射依赖它），schema 不强制顶层 fields 与 stages 内 fields 一致。

  **Must NOT do**:
  - 不修改现有字段枚举（field_config.type 保持不变）
  - 不把 `stages` 设为 required —— 旧工作流没有 stages 必须继续有效

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件 JSON Schema 扩展，模式清晰（$ref 复用现有定义），无逻辑复杂度
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-6)
  - **Blocks**: Task 7 (workflow.json 依赖 stages schema)
  - **Blocked By**: None (can start immediately)

  **References**:
  **Pattern References**:
  - `workflows/schema/workflow-schema.json:90-174` - 顶层 navigation/fields/post_fill 现有定义，stages 的 $ref 目标
  - `workflows/schema/workflow-schema.json:176-417` - $defs 中 navigation_step/field_config/handler_config/post_fill_action 定义

  **Acceptance Criteria**:
  - [ ] stages 定义存在于 schema properties（可选，非 required）
  - [ ] $defs.stage_config 存在，含 name/navigation/fields/post_fill
  - [ ] 含 stages 的样例 workflow 通过 jsonschema 验证
  - [ ] 不含 stages 的旧样例 workflow 仍通过验证（向后兼容）

  **QA Scenarios**:

  ```
  Scenario: Schema accepts valid stages workflow
    Tool: Bash (python)
    Preconditions: schema 文件已修改
    Steps:
      1. 运行 python 脚本，构造含 2 个 stage 的样例 workflow dict
      2. 用 jsonschema.validate 校验
      3. 断言无 ValidationError
    Expected Result: 验证通过，无异常
    Failure Indicators: ValidationError 抛出（stage 结构定义有误）
    Evidence: .sisyphus/evidence/task-1-schema-valid-stages.txt

  Scenario: Schema rejects invalid stage field
    Tool: Bash (python)
    Preconditions: schema 文件已修改
    Steps:
      1. 构造 stage 含未知属性 "invalid_prop" 的样例
      2. 用 jsonschema 校验
      3. 断言抛出 ValidationError 且错误信息含 invalid_prop
    Expected Result: ValidationError 抛出，提示 additional property
    Failure Indicators: 校验静默通过（additionalProperties 未生效）
    Evidence: .sisyphus/evidence/task-1-schema-reject-invalid.txt

  Scenario: Legacy workflow without stages still validates
    Tool: Bash (python)
    Preconditions: schema 已修改
    Steps:
      1. 加载现有 csms_create_proposal/workflow.json
      2. 用新 schema 校验
      3. 断言无 ValidationError
    Expected Result: 旧工作流通过（stages 可选）
    Failure Indicators: 旧工作流报错（兼容性破坏）
    Evidence: .sisyphus/evidence/task-1-schema-legacy-compat.txt
  ```

  **Commit**: YES (groups with 2-6)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `workflows/schema/workflow-schema.json`
  - Pre-commit: `python -m pytest tests/test_integration.py -v`

- [ ] 2. 引擎 stages 执行支持（TDD）

  **What to do**:
  - 在 `workflow_engine.py` 的 `execute()` 中新增 stages 分支：
    ```python
    stages = self.config.get("stages")
    if stages:
        self._execute_stages(stages, field_values)
    else:
        # 现有单轮逻辑不变
    ```
  - 新增 `_execute_stages(stages, field_values)` 方法：对每个 stage：
    1. 临时将 self.config 的 navigation/fields/post_fill 替换为 stage 的值
    2. 调用现有的 execute_navigation() / execute_fields(field_values) / 顶层 post_fill 处理
    3. stage 间支持 `wait` 步骤（复用 navigation 的 wait_selector/wait_time）
  - 关键：`execute_fields` 需要能拿到**该 stage 的字段配置**——重构 `execute_fields` 接受可选的 fields_config 参数（默认 self.config），避免 stage 间字段互相污染
  - 顶层 `fields` 汇总与 stage 内 fields 的关系：stage 内 fields 是实际执行的字段集；顶层 fields 仅用于 GUI 显示/Excel 映射。`field_values` 按字段名全局匹配（跨 stage 字段名唯一，已确认）
  - 结果收集：每阶段 results 合并到 self.results，`get_results()` 汇总不变
  - TDD：先写测试 `tests/test_stages_engine.py`（RED），覆盖：
    - 无 stages 配置 → 走旧逻辑（回归测试）
    - 有 2 个 stages → 依次执行，字段按各 stage 配置填充
    - stage 1 post_fill 点击按钮后，stage 2 的 navigation 生效
    - 字段值跨 stage 传递（同一 field_values dict）
  - 用 Mock page 对象测试（不启动真实浏览器），断言调用的选择器序列

  **Must NOT do**:
  - 不修改现有 execute() 的单轮路径逻辑（保持逐行兼容）
  - 不引入异步/线程改造
  - 不改 GUI 调用引擎的接口签名（execute(username, password, field_values) 不变）

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 引擎核心逻辑修改，涉及向后兼容、状态管理、TDD，需要深度理解现有 execute/execute_fields/post_fill 流程
  - **Skills**: []
    - 无特殊技能需求，依赖对现有代码的深入理解

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-6)
  - **Blocks**: Task 7 (workflow.json 依赖 stages 引擎)
  - **Blocked By**: None (可独立，但需与 Task 1 的 schema 约定一致)

  **References**:
  **Pattern References**:
  - `workflow_engine.py:102-157` - execute() 主流程（login→navigation→fields→post_fill），stages 分支插入点
  - `workflow_engine.py:251-320` - execute_navigation()，stage 间复用的导航逻辑
  - `workflow_engine.py:326-409` - execute_fields()，需要重构为接受 fields_config 参数
  - `workflow_engine.py:478-521` - _handle_post_fill()，stage 内 post_fill 复用
  **Test References**:
  - `tests/test_integration.py` - 现有测试模式（mock page + 断言调用序列）

  **Acceptance Criteria**:
  - [ ] tests/test_stages_engine.py 存在，覆盖 4 个场景（无 stages 回归/多 stage 顺序/stage post_fill/字段传递）
  - [ ] python -m pytest tests/test_stages_engine.py → PASS
  - [ ] 现有 tests/test_integration.py → PASS（旧逻辑未破坏）
  - [ ] execute() 签名不变，旧工作流加载执行路径未改动

  **QA Scenarios**:

  ```
  Scenario: Multi-stage execution order
    Tool: Bash (python pytest)
    Preconditions: tests/test_stages_engine.py 已编写且引擎已实现
    Steps:
      1. 运行 python -m pytest tests/test_stages_engine.py -v
      2. 断言 4 个测试全部 PASS
    Expected Result: PASS，执行顺序符合 stage 定义顺序
    Failure Indicators: 任一测试失败（stage 顺序/字段配置切换错误）
    Evidence: .sisyphus/evidence/task-2-stages-tests.txt

  Scenario: Legacy single-round workflow regression
    Tool: Bash (python pytest)
    Preconditions: 引擎已实现
    Steps:
      1. 运行 python -m pytest tests/test_integration.py -v
      2. 断言全部 PASS
    Expected Result: 旧工作流路径不受影响
    Failure Indicators: 回归测试失败（execute() 单轮路径被改坏）
    Evidence: .sisyphus/evidence/task-2-legacy-regression.txt

  Scenario: Stage post_fill triggers navigation to next stage
    Tool: Bash (python)
    Preconditions: Mock page 配置
    Steps:
      1. 构造 config：stage1 填字段后 post_fill click_button → stage2 navigation wait_selector
      2. 执行 engine.execute(field_values=...)
      3. 断言 mock page 的调用序列为: fill → click(Save) → wait_for_selector(...)
    Expected Result: 跨阶段动作序列正确
    Failure Indicators: 调用序列缺失/顺序错误
    Evidence: .sisyphus/evidence/task-2-stage-transition.txt
  ```

  **Commit**: YES (groups with 1, 3-6)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `workflow_engine.py`, `tests/test_stages_engine.py`
  - Pre-commit: `python -m pytest tests/test_integration.py tests/test_stages_engine.py -v`

- [ ] 3. autocomplete handler 两步交互增强

  **What to do**:
  - 在 `handlers/autocomplete_handler.py` 中新增两步交互支持：
    - 读取 `handler_config.search_value`（schema 已有此字段定义但 handler 未实现）：若配置了 search_value，则先用 search_value 填充搜索框（触发服务端搜索），等下拉出现后用 **value（字段值）** 匹配并选中
    - 支持 `handler_config.result_selector`：覆盖默认的 `.menu > .item` 下拉项选择器（iValua 的实际下拉项是 `{selector}_MenuItem .item` 或 `span.text`，需从录制 HTML 确认）
    - 匹配策略：exact → case-insensitive partial → first item（现有逻辑保留）
    - 修复 `search_input_selector` vs `search_selector` 命名不一致：`hc.get("search_input_selector") or hc.get("search_selector") or f"{selector}_search"`（兼容两种键名）
  - 关键：iValua SelectorControl 的搜索输入是 `{selector}_search`（如 `#..._x_selOrder_search`），下拉项从录制看是 `#..._x_selOrder_147739 > span.text` 这类带 item id 的选择器 —— result_selector 需支持 `{selector}_MenuItem` 或配置具体值
  - 保持向后兼容：无 search_value 时行为与现在完全一致

  **Must NOT do**:
  - 不改变无 search_value 时的现有行为（默认 fill(value) + 匹配下拉）
  - 不重写整个 handler（只加分支）

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: iValua SelectorControl 交互复杂（搜索→下拉→选中），需结合录制 HTML 精确配置选择器
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4-6)
  - **Blocks**: Task 7 (workflow.json 的 Order/Approver 字段依赖)
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `handlers/autocomplete_handler.py:14-117` - 现有 execute()，两步交互插入点
  - `handlers/autocomplete_handler.py:119-164` - _find_search_input / _select_matching_item
  - `workflows/schema/workflow-schema.json:270-387` - handler_config 定义（search_value/result_selector 已声明）
  **External References**:
  - Acubuy 录制 `recordings/recorder_log_20260731_140316.json:574-760` - selOrder 搜索交互（输入 6000017449 → 选择 PO0147739）
  - Acubuy HTML `GR-Acubuy/GR-Acubuy/Create_ Group Procurement AcuBuy1.html` - selector 结构（_search input、.text 下拉项）

  **Acceptance Criteria**:
  - [ ] handler 支持 search_value + value 两步交互
  - [ ] handler 兼容 search_input_selector 和 search_selector 两种键名
  - [ ] result_selector 可配置
  - [ ] 无 search_value 时行为与修改前一致（现有测试通过）

  **QA Scenarios**:

  ```
  Scenario: Two-step search-then-select with search_value
    Tool: Bash (python)
    Preconditions: Mock page 模拟 iValua selector（搜索框 + 下拉项）
    Steps:
      1. 构造 field_config: selector=#sel, search_value="6000017449", value="PO0147739"
      2. 调用 handler.execute(field_config, "PO0147739")
      3. 断言 mock 调用序列: fill(search, "6000017449") → wait → click(item with text "PO0147739")
    Expected Result: 先搜索再选中，两步顺序正确
    Failure Indicators: 只用 value 填充（未用 search_value）或未选中下拉项
    Evidence: .sisyphus/evidence/task-3-autocomplete-two-step.txt

  Scenario: Backward compat - no search_value, old behavior
    Tool: Bash (python)
    Preconditions: Mock page
    Steps:
      1. 构造 field_config: selector=#sel（无 search_value）
      2. 调用 handler.execute(field_config, "X")
      3. 断言 fill(search, "X")（用 value 直接填充）
    Expected Result: 与旧行为一致
    Failure Indicators: 行为偏离（如缺少 fill 或选择错误）
    Evidence: .sisyphus/evidence/task-3-autocomplete-compat.txt
  ```

  **Commit**: YES (groups with 1-2, 4-6)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `handlers/autocomplete_handler.py`
  - Pre-commit: `python -m pytest tests/test_integration.py -v`

- [ ] 4. file_upload handler html5_uploader 验证/修正

  **What to do**:
  - 审查 `handlers/file_upload_handler.py` 的 `_handle_html5()` 是否适配 iValua 上传器：
    - 录制中点击的是 `#body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x_UploadButtonControl`（按钮），实际 file input 是 `#fileselect_..._20240807224049492_x`（隐藏，multiple）
    - 验证 `upload_button_selector` + `file_input_selector` 配置路径可用
    - 确认上传后等待逻辑（wait_for_upload_selector，iValua 上传后显示文件名列表）
  - 若发现 iValua 特有行为（如上传进度条、文件名列表容器），在 handler 中补充配置项或文档说明
  - 为 workflow.json 的 Attachment File 字段提供准确的 handler_config 参数值

  **Must NOT do**:
  - 不改变 native 模式行为
  - 不新增 iValua 专属 handler 类型（复用 file_upload + html5_uploader 模式）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 现有 html5_uploader 模式已实现，只需验证配置适配
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-3, 5-6)
  - **Blocks**: Task 7 (workflow.json 附件字段依赖)
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `handlers/file_upload_handler.py:69-102` - _handle_html5 实现
  - `workflows/schema/workflow-schema.json:270-387` - handler_config（file_input_selector/upload_button_selector 是自定义键，schema 需允许）
  **External References**:
  - 录制 `recorder_log_20260731_140316.json:963-1021` - 上传 PR0157310.pdf 完整交互
  - Acubuy HTML `Create_ Group Procurement AcuBuy1.html` - file_delivery 控件结构（UploadButtonControl + fileselect_ input）

  **Acceptance Criteria**:
  - [ ] 确认 html5_uploader 模式适配 iValua 上传（或记录需修正项）
  - [ ] workflow.json 附件字段的 handler_config 参数值已确定

  **QA Scenarios**:

  ```
  Scenario: html5_uploader config resolves iValua file input
    Tool: Bash (python)
    Preconditions: Mock page
    Steps:
      1. 构造 field_config: mode=html5_uploader, upload_button_selector=#UploadBtn, file_input_selector=#fileselect_x
      2. 调用 handler.execute(field_config, "C:/test/PR0157310.pdf")
      3. 断言 mock: click(#UploadBtn) → set_input_files("C:/test/PR0157310.pdf")
    Expected Result: 按钮点击 + 文件设置正确
    Failure Indicators: file input 找不到（selector 配置错误）
    Evidence: .sisyphus/evidence/task-4-file-upload-config.txt
  ```

  **Commit**: YES (groups with 1-3, 5-6)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `handlers/file_upload_handler.py` (如修改)
  - Pre-commit: `python -m pytest tests/test_integration.py -v`

- [ ] 5. input handler iframe 支持

  **What to do**:
  - 审查 `handlers/input_handler.py`（和 select_handler 等）是否支持 iframe 上下文
  - 录制中阶段 2 的 `#body_x_txtQuantity` 位于 `modal.aspx`（frame_loaded 事件确认是 frame/iframe）
  - 在 handler 中支持 `handler_config.iframe_selector`（schema 已有该字段）：若配置了 iframe_selector，则 handler 先在 iframe 内定位字段
  - 实现方式：使用 `page.frame_locator(iframe_selector)` 包裹字段定位逻辑
  - 保持向后兼容：无 iframe_selector 时行为不变

  **Must NOT do**:
  - 不修改所有 handler（只处理 input，其他类型在 task 9 验证时按需补充）
  - 不假设 modal 是弹窗窗口（录制确认是 frame_loaded，不是 popup）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单 handler 增加 iframe 分支，模式明确
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4, 6)
  - **Blocks**: Task 7 (workflow.json Quantity 字段依赖)
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `handlers/input_handler.py` - 现有 input handler
  - `handlers/base_handler.py` - BaseHandler 接口
  - `workflows/schema/workflow-schema.json:300-307` - iframe_selector 字段定义
  **External References**:
  - 录制 `recorder_log_20260731_140316.json:1089-1234` - modal.aspx frame_loaded + Quantity 编辑

  **Acceptance Criteria**:
  - [ ] input handler 支持 iframe_selector 定位
  - [ ] 无 iframe_selector 时行为与旧一致
  - [ ] 单测覆盖 iframe 内定位

  **QA Scenarios**:

  ```
  Scenario: Input inside iframe located via iframe_selector
    Tool: Bash (python)
    Preconditions: Mock page 含 frame_locator 模拟
    Steps:
      1. 构造 field_config: selector=#body_x_txtQuantity, handler_config.iframe_selector=#modalFrame
      2. 调用 handler.execute(field_config, "100")
      3. 断言定位发生在 iframe 上下文内
    Expected Result: iframe 内 fill 成功
    Failure Indicators: 在顶层 page 定位（忽略 iframe）或报错
    Evidence: .sisyphus/evidence/task-5-iframe-input.txt

  Scenario: No iframe_selector - top-level behavior unchanged
    Tool: Bash (python)
    Preconditions: Mock page
    Steps:
      1. 构造 field_config: selector=#input（无 iframe_selector）
      2. 调用 handler.execute(field_config, "x")
      3. 断言顶层 page fill
    Expected Result: 与旧行为一致
    Failure Indicators: iframe 逻辑干扰顶层定位
    Evidence: .sisyphus/evidence/task-5-no-iframe-compat.txt
  ```

  **Commit**: YES (groups with 1-4, 6)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `handlers/input_handler.py`
  - Pre-commit: `python -m pytest tests/test_integration.py -v`

- [ ] 6. settings.json 注册 gracubuy_gr_flow

  **What to do**:
  - 在 `workflows/settings.json` 的 `workflow_list` 数组追加：
    ```json
    {
      "name": "gracubuy_gr_flow",
      "display_name": "GR-Acubuy Create Goods Receipt"
    }
    ```
  - 不改变 `current_workflow`（保持现有选中值）
  - 注意：WorkflowManager 的 discover_workflows() 会自动扫描 workflows/ 目录，settings.json 的 workflow_list 是展示列表。确认 GUI 下拉能显示新工作流（可运行 `python -c "from workflow_manager import WorkflowManager; print(WorkflowManager().list_workflows())"` 验证）

  **Must NOT do**:
  - 不改变 current_workflow
  - 不改动其他工作流条目

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件 JSON 追加一条记录
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-5)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `workflows/settings.json` - 现有 workflow_list 结构
  - `workflow_manager.py:127-190` - discover_workflows 自动发现逻辑

  **Acceptance Criteria**:
  - [ ] settings.json 包含 gracubuy_gr_flow 条目
  - [ ] current_workflow 未被改动
  - [ ] WorkflowManager().list_workflows() 返回包含新工作流

  **QA Scenarios**:

  ```
  Scenario: New workflow discovered by WorkflowManager
    Tool: Bash (python)
    Preconditions: settings.json 已更新
    Steps:
      1. 运行 python -c "from workflow_manager import WorkflowManager; print([w['name'] for w in WorkflowManager().list_workflows()])"
      2. 断言输出含 'gracubuy_gr_flow'
    Expected Result: 新工作流被发现
    Failure Indicators: 未出现在列表中（settings.json 或目录结构问题）
    Evidence: .sisyphus/evidence/task-6-workflow-discovered.txt
  ```

  **Commit**: YES (groups with 1-5)
  - Message: `feat(engine): add stages support for multi-phase workflows`
  - Files: `workflows/settings.json`
  - Pre-commit: `python -m pytest tests/test_integration.py -v`

- [ ] 7. workflow.json 4 阶段配置

  **What to do**:
  - 创建 `workflows/gracubuy_gr_flow/workflow.json`，结构如下：
    ```json
    {
      "$schema": "../../workflows/schema/workflow-schema.json",
      "workflow_name": "GR-Acubuy Create Goods Receipt",
      "version": "1.0.0",
      "description": "Singtel iValua Acubuy 收货单创建完整流程（创建→明细编辑→审批人）。从登录后开始，使用多阶段执行。",
      "status": "active",
      "browser": { "channel": "msedge" },
      "login": { "url": "", "enabled": false },
      "fields": {
        "Order": { "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder", "type": "autocomplete", "required": true, "handler_config": { "search_value": "", "result_selector": "...", "wait_after_input_ms": 1500 } },
        "Code": { "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_txtCode", "type": "input", "required": true },
        "Internal Comment": { "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_udt_desc_delivery_20240807223748988", "type": "input", "required": true },
        "Attachment File": { "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x_UploadButtonControl", "type": "file_upload", "required": false, "handler_config": { "mode": "html5_uploader", "file_input_selector": "#fileselect_body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x" } },
        "Quantity": { "selector": "#body_x_txtQuantity", "type": "input", "required": false, "handler_config": { "iframe_selector": "iframe[src*='modal.aspx']" } },
        "Approver 2": { "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_selector_single_delivery_20240816105603081", "type": "autocomplete", "required": true, "handler_config": { "result_selector": "...", "wait_after_input_ms": 1500 } }
      },
      "stages": [
        {
          "name": "create_gr",
          "navigation": [
            { "action": "goto", "url": "https://singtel.ivalua.app/page.aspx/en/ord/delivery_manage?Create", "wait_until": "networkidle" },
            { "action": "wait_selector", "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_txtCode", "timeout": 20000 }
          ],
          "fields": ["Order", "Code", "Internal Comment", "Attachment File"],
          "post_fill": { "action": "click_button", "click_selector": "#proxyActionBar_x__cmdSave", "message": "保存创建 GR..." }
        },
        {
          "name": "edit_item",
          "navigation": [
            { "action": "wait_selector", "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_prxItem_x_gridDeliveryItems_grd", "timeout": 20000 },
            { "action": "click", "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_prxItem_x_gridDeliveryItems_grd_tr_794641_img___colManagegridDeliveryItems > i.iv-grid-fa-icon.fa-pencil-alt" },
            { "action": "wait_selector", "selector": "iframe[src*='modal.aspx']", "timeout": 15000 }
          ],
          "fields": ["Quantity"],
          "post_fill": { "action": "click_button", "click_selector": "#proxyActionBar_x__cmdEnd", "message": "保存并关闭明细编辑..." }
        },
        {
          "name": "advance_workflow",
          "navigation": [
            { "action": "wait_selector", "selector": "#proxyActionBar_x_valsingtel_receipt_v2create", "timeout": 20000 },
            { "action": "click", "selector": "#proxyActionBar_x_valsingtel_receipt_v2create" },
            { "action": "wait_selector", "selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_selector_single_delivery_20240816105603081_search", "timeout": 20000 }
          ],
          "fields": [],
          "post_fill": {}
        },
        {
          "name": "select_approver",
          "navigation": [],
          "fields": ["Approver 2"],
          "post_fill": { "action": "click_button", "click_selector": "#proxyActionBar_x__cmdSave", "message": "保存审批人..." }
        }
      ],
      "post_fill": { "action": "manual_review", "message": "GR 创建完成，请检查结果" }
    }
    ```
  - **重要决策**：stages 内 `fields` 用**字段名数组**（引用顶层 fields），而非内嵌完整配置 —— 这样顶层 fields 是唯一事实源，GUI 显示/Excel 映射/引擎执行全部引用同一份。schema 的 stage_config.fields 需支持此形态（string 数组），task 1 中设计时注意
  - **Order 字段的 search_value 问题**：录制中搜索值 `6000017449` 与选中值 `PO0147739` 不同。Excel 中 Order 列填什么？
    - 方案：Excel 填 **PO0147739**（选中值），search_value 从 Excel 的另一个列取？→ 不可行，handler 只收一个 value
    - **务实方案**：Excel 填搜索值 `6000017449`，handler 用 value fill 搜索框，结果列表出现后选 first（iValua 搜索结果第一个即匹配项）。autocomplete handler 现有逻辑已支持 first fallback。
    - **备选方案**：Order 拆两列 `Order Search` / `Order Select`，需要 handler 支持两值。→ 超出当前 handler 能力，标记为待用户决策（见 Decisions Needed）
  - 明确写清楚：使用"Excel 填搜索值 + 选 first"方案（务实、无需改 handler 签名）
  - 附件字段：确认 file_input_selector 指向 `#fileselect_..._x`
  - Quantity 的 iframe_selector：用 `iframe[src*='modal.aspx']`（从录制 URL 提取）
  - 校验 JSON 格式，用 schema 验证脚本通过

  **Must NOT do**:
  - 不在 workflow.json 中配置 Acubuy SSO 登录（login.enabled=false）
  - 不引入顶层 fields 之外的额外字段定义
  - 不硬编码录制中的 GR 单号 413955 或明细行 794641 的特定值（选择器保持通用，行号用 first 或动态定位）

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 需要精确映射录制交互到 schema 结构，涉及 stages 字段引用形态的契约设计
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 1-5 的契约）
  - **Parallel Group**: Wave 2 (with Task 8)
  - **Blocks**: Task 8, Task 9
  - **Blocked By**: Tasks 1, 2, 3, 4, 5

  **References**:
  **Pattern References**:
  - `workflows/gracubuy_create_gr/workflow.json` - 现有半成品，字段/选择器参考
  - `workflows/schema/workflow-schema.json` - 配置结构约束
  **External References**:
  - 录制 `recorder_log_20260731_140316.json` - 全部 4 阶段的选择器和值
  - Acubuy HTML 文件 - 字段真实结构验证

  **Acceptance Criteria**:
  - [ ] workflows/gracubuy_gr_flow/workflow.json 存在且 JSON 合法
  - [ ] python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json → Valid
  - [ ] 6 个字段（Order/Code/Internal Comment/Attachment File/Quantity/Approver 2）定义完整
  - [ ] 4 个 stages 顺序正确（create_gr→edit_item→advance_workflow→select_approver）

  **QA Scenarios**:

  ```
  Scenario: Workflow validates against schema
    Tool: Bash (python)
    Preconditions: workflow.json 已创建
    Steps:
      1. 运行 python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json
      2. 断言 exit 0 且输出含 "Valid"
    Expected Result: 校验通过
    Failure Indicators: 校验报错（字段类型/结构问题）
    Evidence: .sisyphus/evidence/task-7-workflow-valid.txt

  Scenario: Stages reference only existing fields
    Tool: Bash (python)
    Preconditions: workflow.json 已创建
    Steps:
      1. 运行 python 脚本，遍历 stages 中 fields 引用的名称
      2. 断言每个名称都存在于顶层 fields 中
    Expected Result: 无悬空引用
    Failure Indicators: stage 引用了顶层不存在的字段
    Evidence: .sisyphus/evidence/task-7-stage-field-refs.txt
  ```

  **Commit**: YES (groups with 8)
  - Message: `feat(workflow): add gracubuy_gr_flow with Excel data template`
  - Files: `workflows/gracubuy_gr_flow/workflow.json`
  - Pre-commit: `python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json`

- [ ] 8. Excel 数据模板

  **What to do**:
  - 创建 `workflows/gracubuy_gr_flow/GR_Goods_Receipt_Data_Template.xlsx`
  - Sheet1 结构（参考 CSMS_Proposal_Data_Template.xlsx）：
    - 第 1 行 = 表头（字段名，必须与 workflow.json 顶层 fields keys **完全一致**）
    - 第 2 行 = 示例值（从录制提取）
    - 列（6 列）：`Order | Code | Internal Comment | Attachment File | Quantity | Approver 2`
    - 示例值：`6000017449 | 12345 | 8889 | C:/path/to/PR0157310.pdf | 100 | Amy Yin - (Band C)`
  - 用 openpyxl 创建，设置列宽合理（Order/Attachment File 列宽大些）
  - 附件路径用相对或绝对占位示例（录制中是 `C:\fakepath\PR0157310.pdf`，模板中给真实示例路径占位）
  - 验证：用 python 读取模板，断言第 1 行 header 与 workflow.json fields keys 完全匹配（顺序不要求一致，但名称必须一一对应）

  **Must NOT do**:
  - 不添加 workflow.json 中不存在的列（会导致 Excel 值被忽略）
  - 不遗漏 workflow.json 中 required 字段的列

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单 Excel 生成 + 映射验证
  - **Skills**: []
    - 无特殊技能需求（用 openpyxl 直接创建）

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 Task 7 的字段定义）
  - **Parallel Group**: Wave 2 (with Task 7)
  - **Blocks**: Task 9
  - **Blocked By**: Task 7

  **References**:
  **Pattern References**:
  - `workflows/csms_proposal_group_v2/CSMS_Proposal_Data_Template.xlsx` - 现有模板结构（header 行 + 值行）
  - `form_filler.py:618-657` - _build_field_values 读取逻辑（df.iloc[0]，列名=字段名）

  **Acceptance Criteria**:
  - [ ] GR_Goods_Receipt_Data_Template.xlsx 存在
  - [ ] 第 1 行 header 与 workflow.json fields keys 完全一致
  - [ ] 第 2 行包含录制中的示例值

  **QA Scenarios**:

  ```
  Scenario: Excel headers match workflow field keys exactly
    Tool: Bash (python)
    Preconditions: Excel 模板 + workflow.json 已创建
    Steps:
      1. 运行 python 脚本，读取 Excel 第 1 行和 workflow.json fields keys
      2. 断言两集合完全相等（名称一一对应）
    Expected Result: header == fields keys，无多余无遗漏
    Failure Indicators: 名称不匹配（拼写/大小写/多余列）
    Evidence: .sisyphus/evidence/task-8-excel-mapping.txt

  Scenario: Template values readable by GUI loader
    Tool: Bash (python)
    Preconditions: Excel 模板已创建
    Steps:
      1. 运行 python，用 pandas.read_excel 读取模板，取 df.iloc[0]
      2. 断言含 6 个字段值（6000017449/12345/8889/PR0157310.pdf/100/Amy Yin）
    Expected Result: 6 个值可被 GUI 加载
    Failure Indicators: 值缺失或 NaN（列/行结构问题）
    Evidence: .sisyphus/evidence/task-8-excel-values.txt
  ```

  **Commit**: YES (groups with 7)
  - Message: `feat(workflow): add gracubuy_gr_flow with Excel data template`
  - Files: `workflows/gracubuy_gr_flow/GR_Goods_Receipt_Data_Template.xlsx`
  - Pre-commit: `python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json`

- [ ] 9. 端到端验证（schema 校验 + 引擎单测 + Excel 映射断言）

  **What to do**:
  - 运行完整验证链：
    1. `python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json` → Valid
    2. 回归：所有现有工作流（csms_create_proposal、csms_proposal_group_v2、gracubuy_create_gr、gracubuy_login）schema 校验仍通过
    3. `python -m pytest tests/test_integration.py tests/test_stages_engine.py -v` → 全 PASS
    4. Excel 映射断言脚本（见 Task 8 QA）
  - 模拟引擎加载 workflow.json（不启动浏览器）：用 Mock page 跑 stages 配置，断言 4 阶段调用序列
  - 验证 WorkflowManager.load_workflow("gracubuy_gr_flow") 成功且通过 schema 验证
  - 检查 browser.channel=msedge 是否被 GUI 支持（form_filler.py 的 browser_combo 含 msedge 选项）
  - 输出验证报告

  **Must NOT do**:
  - 不启动真实浏览器访问 Acubuy（需真实凭据，超出范围）
  - 不修改任何实现（纯验证）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 多步骤集成验证，需要综合判断
  - **Skills**: []
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 6, 7, 8

  **References**:
  - 所有前序任务的产出文件

  **Acceptance Criteria**:
  - [ ] 新工作流 schema 校验通过
  - [ ] 4 个现有工作流 schema 校验全部通过（回归）
  - [ ] 全部单元测试通过
  - [ ] Excel 映射断言通过
  - [ ] WorkflowManager 能加载新工作流

  **QA Scenarios**:

  ```
  Scenario: Full validation chain passes
    Tool: Bash (python)
    Preconditions: 所有任务完成
    Steps:
      1. 运行 validate_workflow.py 对新工作流 + 4 个现有工作流
      2. 运行 pytest 全部测试
      3. 运行 Excel 映射断言
      4. 断言全部成功
    Expected Result: 全部通过，无回归
    Failure Indicators: 任一环节失败
    Evidence: .sisyphus/evidence/task-9-e2e-validation.txt

  Scenario: Engine loads workflow with stages via WorkflowManager
    Tool: Bash (python)
    Preconditions: workflow.json 已创建
    Steps:
      1. 运行 python -c "from workflow_manager import WorkflowManager; c = WorkflowManager().load_workflow('gracubuy_gr_flow'); print(len(c.get('stages', [])))"
      2. 断言输出 4
    Expected Result: 4 个 stages 被正确加载
    Failure Indicators: 加载失败（schema 验证拦截或 JSON 错误）
    Evidence: .sisyphus/evidence/task-9-workflow-load.txt
  ```

  **Commit**: YES (groups with 6)
  - Message: `test(workflow): verify gracubuy_gr_flow end-to-end`
  - Files: `tests/*` (如新增断言脚本)
  - Pre-commit: 完整验证链

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest` + schema validation for all workflows. Review changed files for AI slop: over-abstraction, generic names, unused code, broken backward compat.
  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (schema→engine→workflow.json→Excel chain). Test edge cases: missing Excel, empty field values, stage transition failures.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1-6**: `feat(engine): add stages support for multi-phase workflows` - workflow-schema.json, workflow_engine.py, handlers/*
- **7-8**: `feat(workflow): add gracubuy_gr_flow with Excel data template` - workflows/gracubuy_gr_flow/*
- **9**: `test(workflow): verify gracubuy_gr_flow end-to-end` - tests/*, workflows/settings.json

---

## Success Criteria

### Verification Commands
```bash
# Schema validation
python workflows/schema/validate_workflow.py workflows/gracubuy_gr_flow/workflow.json   # → Valid, exit 0

# Existing workflows still valid
python workflows/schema/validate_workflow.py workflows/csms_create_proposal/workflow.json   # → Valid
python workflows/schema/validate_workflow.py workflows/csms_proposal_group_v2/workflow.json # → Valid
python workflows/schema/validate_workflow.py workflows/gracubuy_create_gr/workflow.json     # → Valid

# Unit tests
python -m pytest tests/test_integration.py -v   # → all pass

# Excel mapping (field keys == workflow.json fields keys)
python -c "..."   # → header row matches fields keys exactly
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
