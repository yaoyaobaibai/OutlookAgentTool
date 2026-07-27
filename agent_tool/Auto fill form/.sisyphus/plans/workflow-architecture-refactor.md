# FormFiller 多工作流架构重构计划

## TL;DR

> **核心目标**: 将现有的单体 `form_filler.py`（1204行，硬编码CSMS逻辑）重构为**插件式工作流架构**。每个工作流是一个自包含的文件夹（`workflow.json` + 可选 `handlers.py`），通过 GUI 下拉菜单切换时，所有参数（URL、选择器、字段、处理器、附件配置）自动切换。
>
> **交付物**:
> - 重构后的 `form_filler.py`（全新架构）
> - `workflow_engine.py` + `workflow_manager.py`（核心引擎）
> - `handlers/` 处理器包（8个内置处理器类型）
> - `workflows/csms_create_proposal/`（CSMS 工作流配置）
> - `workflows/gracubuy_create_gr/`（GR-Acubuy 工作流配置）
> - 更新后的打包脚本和文档
>
> **预估工作量**: Large（10-15个工作日）
> **并行执行**: 是 - 5个执行波次
> **关键路径**: 项目结构 → WorkflowEngine → GUI → 集成

---

## Context

### 原始需求
将现有 CSMS 表单自动填充程序重构为多工作流架构，支持在不同自动化流程之间切换。第一个新工作流是 GR-Acubuy（Singtel iValua 采购平台的收货单创建）。

### 访谈总结
**关键决策**:
- **架构方案**: 插件式工作流（方案A），每个工作流自包含文件夹
- **配置方式**: 纯 JSON 配置（约90%）+ 内置处理器 + 可选 Python 钩子（约5%）
- **代码策略**: 全量重写 `form_filler.py`，废弃旧单体架构
- **测试策略**: 无自动化测试，通过 Agent QA 验证
- **错误处理**: 自动重试2-3次 → 失败停止 + 显示错误
- **登录方式**: GR-Acubuy 使用简单表单登录（非SSO）
- **忽略文件**: `auto_create_proposal.py` 暂不处理

### Metis 审查
**已解决的关键问题**:
- **GR-Acubuy SelectorControl 复杂性**: 确认使用自定义 Semantic UI 组件，需独立处理器
- **级联依赖**: 字段需支持 post_fill 事件触发 + 等待 AJAX + 重试
- **隐藏区域**: 处理器需先展开隐藏 section 再填充
- **登录机制**: 已确认为表单登录，非 SSO
- **回归基线**: 计划 Task 0 创建 CSMS 行为 Playwright 验证脚本
- **错误恢复**: 自动重试后停止（用户确认）
- **Excel 列映射**: 每个工作流独立配置

---

## Work Objectives

### 核心目标
构建一个可扩展的多工作流自动化框架，支持通过纯配置添加新工作流，无需修改核心代码。

### 具体交付物
- 全新项目结构（`workflows/`、`handlers/`、`workflow_engine.py`）
- Workflow JSON Schema（工作流配置标准）
- 8个内置字段处理器（input/select/autocomplete/datepicker/popup_search/file_upload/checkbox/post_fill）
- WorkflowEngine（导航执行 + 字段遍历 + 事件触发 + 错误处理）
- WorkflowManager（工作流发现、加载、切换、持久化）
- GUI 重构（工作流选择器、动态字段加载）
- CSMS 工作流完整配置（迁移现有功能）
- GR-Acubuy 工作流配置（新建）
- 更新后的 PyInstaller 打包

### Definition of Done
- [ ] GUI 下拉菜单可切换 CSMS ↔ GR-Acubuy 工作流
- [ ] 切换后：登录URL、字段列表、附件配置自动更新
- [ ] CSMS 工作流执行结果与现有 `form_filler.py` 行为一致（通过 Playwright 回归脚本验证）
- [ ] GR-Acubuy 工作流可成功执行完整流程
- [ ] 在 `workflows/` 中添加新文件夹即可自动出现在下拉菜单中（无需改代码）
- [ ] 错误重试机制正常工作（失败重试2次 → 停止 + 错误信息）
- [ ] 打包为 EXE 后可正常运行

### Must Have
- 工作流切换零代码（纯配置驱动）
- CSMS 现有功能完整保留（回归通过）
- GR-Acubuy 所有必填字段成功填充

### Must NOT Have（防护栏）
- ❌ 不支持并发执行（一次一个工作流）
- ❌ 不支持计划任务 / 定时触发
- ❌ 不支持数据库后端（配置纯 JSON 文件）
- ❌ 不支持 Web 管理界面
- ❌ 不支持插件热加载（启动时加载）
- ❌ `workflow.json` 内不包含条件分支逻辑（if/then/else）
- ❌ `auto_create_proposal.py` 不在本计划范围内

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - 所有验证通过 Agent 执行。不允许依赖"用户手动确认"的验收标准。

### 测试决策
- **自动化测试**: 无（无 pytest/vitest 等）
- **验证方式**: Agent 执行 Playwright / curl / Bash 命令验证
- **回归基线**: Task 0 创建 CSMS 行为 Playwright 验证脚本（重构前后对比）

### QA 策略
每个 Task 必须包含 Agent 可执行的 QA 场景。证据保存到 `.sisyphus/evidence/task-N-scenario.ext`。

- **UI/浏览器**: Playwright - 导航、填充、断言、截图
- **配置验证**: Bash - 验证 JSON schema、文件结构
- **GUI 功能**: Playwright（需启动 tkinter GUI）或手动辅助验证

---

## Execution Strategy

### 并行执行波次

```
Wave 0 (Pre-task - 回归基线, 单任务):
├── Task 0: CSMS 行为回归验证脚本

Wave 1 (Foundation - 4 并行):
├── Task 1: 项目结构重组
├── Task 2: Workflow JSON Schema 定义 + 验证器
├── Task 3: WorkflowManager 类
└── Task 4: BaseHandler + HandlerRegistry

Wave 2 (Handlers - 5 并行):
├── Task 5: InputHandler + SelectHandler + CheckboxHandler
├── Task 6: AutoCompleteHandler (iValua SelectorControl)
├── Task 7: DatePickerHandler
├── Task 8: PopupSearchHandler
└── Task 9: FileUploadHandler

Wave 3 (Engine + GUI - 2 并行):
├── Task 10: WorkflowEngine（导航 + 字段遍历 + 事件 + 重试）
└── Task 11: GUI 重构 + 工作流选择器

Wave 4 (Workflow 配置 - 2 并行):
├── Task 12: CSMS 工作流配置（迁移现有）
└── Task 13: GR-Acubuy 工作流配置（新建）

Wave 5 (集成 + 收尾 - 2 并行):
├── Task 14: 集成测试 + 边界情况处理
└── Task 15: 打包更新 + 文档更新

Final Wave (最终验证):
├── F1: Plan Compliance Audit (oracle)
├── F2: Code Quality Review (unspecified-high)
├── F3: Real Manual QA (unspecified-high + playwright)
└── F4: Scope Fidelity Check (deep)
```

### 依赖矩阵

```
Task 0: 无依赖 → Blocks nothing（参考基线）
Task 1: 无依赖 → Blocks 2,3,4
Task 2: 1 → Blocks 3, 12, 13
Task 3: 1,2 → Blocks 10, 11
Task 4: 1 → Blocks 5,6,7,8,9
Task 5: 4 → Blocks 10
Task 6: 4 → Blocks 10
Task 7: 4 → Blocks 10
Task 8: 4 → Blocks 10
Task 9: 4 → Blocks 10
Task 10: 2,3,5,6,7,8,9 → Blocks 12,13,14
Task 11: 3,10 → Blocks 14
Task 12: 2,10 → Blocks 14
Task 13: 2,10 → Blocks 14
Task 14: 10,11,12,13 → Blocks 15
Task 15: 14 → Blocks 无
```

### Agent 调度摘要

- **Wave 0**: 1 agent - `unspecified-high`
- **Wave 1**: 4 agents - `quick`(T1), `unspecified-high`(T2), `unspecified-high`(T3), `unspecified-high`(T4)
- **Wave 2**: 5 agents - 全部 `unspecified-high`
- **Wave 3**: 2 agents - `unspecified-high`(T10), `visual-engineering`(T11)
- **Wave 4**: 2 agents - `unspecified-high`(T12), `unspecified-high`(T13)
- **Wave 5**: 2 agents - `unspecified-high`(T14), `writing`(T15)
- **Final**: 4 agents - `oracle`, `unspecified-high`, `unspecified-high`, `deep`

---

## TODOs

- [x] 0. **创建 CSMS 行为回归验证脚本（Pre-task）**

  **What to do**:
  - 分析现有 `form_filler.py` 的 `_fill_form()` 方法（559-1174行），提取完整的 CSMS 自动化流程步骤
  - 创建一个独立的 Playwright 回归脚本 `tests/csms_regression.py`，不依赖 tkinter GUI
  - 脚本应覆盖以下步骤：
    1. 启动浏览器 → 访问登录页面
    2. 填写用户名/密码 → 点击登录
    3. 导航到 Create Proposal Group 页面
    4. 填写 Proposal # → 点击 GET CRM INFO → 等待 CRM 数据加载
    5. 填写 Date of Award
    6. 选择 Priming Project Manager（弹窗搜索）
    7. 选择 Currency Code 下拉框
    8. 填充其他输入字段
  - 每个步骤使用 `page.fill()` / `page.select_option()` / `page.click()` / `page.locator().wait_for()` 等 Playwright API
  - 每个步骤后使用 `expect(page.locator(...)).to_have_value(...)` 或 `page.input_value()` 验证值是否正确
  - 脚本应在脚本开头用 `#` 注释标注：测试目标、前置条件、预期结果
  - 注意：这是一个**离线验证脚本**，实际运行时需要目标页面可访问。脚本应包含 skip 机制，在无法访问目标页面时自动跳过（打印 WARNING）

  **Must NOT do**:
  - 不要连接 tkinter GUI
  - 不要修改 `form_filler.py`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要深入理解现有1204行代码并提取精确行为
  - **Skills**: `[]`（无特殊技能需求）
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO（单任务）
  - **Parallel Group**: Wave 0
  - **Blocks**: 无（参考基线）
  - **Blocked By**: 无

  **References**:
  - `form_filler.py:559-1174` - `_fill_form()` 方法，完整的 CSMS 自动化流程
  - `form_filler.py:594-687` - 自动登录逻辑（用户名/密码选择器探测）
  - `form_filler.py:711-748` - Proposal # + GET CRM INFO 处理
  - `form_filler.py:750-807` - Date of Award 处理
  - `form_filler.py:809-901` - Priming Project Manager 弹窗搜索
  - `form_filler.py:938-973` - ASP.NET 下拉框 `select_option` + `__doPostBack` 处理
  - `form_filler.py:976-984` - 文件上传处理
  - `form_filler.py:1008-1158` - 附件上传（Category/File/Description）

  **Acceptance Criteria**:
  - [ ] `tests/csms_regression.py` 文件存在
  - [ ] 脚本包含完整的8个步骤注释说明
  - [ ] 每个步骤包含 Playwright 断言验证
  - [ ] 脚本包含 `if __name__ == '__main__':` 入口
  - [ ] 脚本包含无法访问目标页面的 graceful skip 机制
  - [ ] 语法正确：`python -c "import py_compile; py_compile.compile('tests/csms_regression.py', doraise=True)"` → 无错误

  **QA Scenarios**:
  ```
  Scenario: 脚本语法和结构验证
    Tool: Bash
    Preconditions: tests/csms_regression.py 已创建
    Steps:
      1. python -c "import py_compile; py_compile.compile('tests/csms_regression.py', doraise=True)"
      2. grep -q "def test_" tests/csms_regression.py  # 确认包含测试函数
      3. grep -q "playwright" tests/csms_regression.py  # 确认使用 Playwright
    Expected Result: 语法检查通过，包含 Playwright 和测试函数
    Evidence: .sisyphus/evidence/task-0-syntax-check.txt

  Scenario: 离线运行（skip 机制）
    Tool: Bash
    Preconditions: 无网络/目标页面不可访问
    Steps:
      1. timeout 30 python tests/csms_regression.py --dry-run 2>&1 | tee output.log
      2. grep -i "skip\|WARNING\|dry.run" output.log
    Expected Result: 脚本应优雅跳过，不崩溃
    Evidence: .sisyphus/evidence/task-0-dry-run.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-0-syntax-check.txt`
  - [ ] `.sisyphus/evidence/task-0-dry-run.txt`

  **Commit**: YES
  - Message: `test(csms): add regression baseline script for CSMS automation behavior`
  - Files: `tests/csms_regression.py`

- [x] 1. **项目结构重组**

  **What to do**:
  - 创建新的项目目录结构（如下所示）
  - 移动/重组织现有文件
  - 创建 `workflows/` 目录和 `handlers/` 包
  - 创建 `__init__.py` 文件（含版本信息）
  - 删除不再需要的调试脚本（如 `测试下拉框.py`, `调试下拉框.py`, `检查页面结构.py`, `实际测试页面.py`, `测试修复版本.py`, `debug_form_filler.py`, `debug_error.py`, `simple_test.py`），建议移到 `_archive/` 目录而不是直接删除
  - 保留 `requirements.txt`, 批处理文件, spec 文件（后续 Task 更新）

  **新目录结构**:
  ```
  自动填充网页表单信息/
  ├── form_filler.py              # 主入口（重构后 - 仅 GUI 初始化）
  ├── workflow_engine.py           # 工作流执行引擎
  ├── workflow_manager.py          # 工作流管理（发现、加载、切换）
  ├── config_manager.py            # 配置管理（为兼容性保留）
  ├── attachment_manager.py        # 附件管理（简化版）
  ├── handlers/                    # 处理器包
  │   ├── __init__.py
  │   ├── base_handler.py          # 抽象基类
  │   ├── input_handler.py
  │   ├── select_handler.py
  │   ├── autocomplete_handler.py
  │   ├── datepicker_handler.py
  │   ├── popup_search_handler.py
  │   ├── file_upload_handler.py
  │   └── checkbox_handler.py
  ├── workflows/                   # 工作流配置目录
  │   ├── csms_create_proposal/
  │   │   └── workflow.json
  │   ├── gracubuy_create_gr/
  │   │   └── workflow.json
  │   └── settings.json            # 当前选中的工作流
  ├── tests/
  │   └── csms_regression.py       # 回归基线（Task 0）
  ├── _archive/                    # 旧脚本归档
  ├── html/                        # 保留 HTML 参考文件
  ├── requirements.txt
  ├── 执行打包.bat                 # 保留，后续更新
  ├── 运行程序.bat                 # 保留，后续更新
  └── form_filler.spec            # 保留，后续更新
  ```

  **Must NOT do**:
  - 不要在这个 Task 中编写任何业务逻辑代码
  - 不要移动或删除 `form_config.json`、`attachment_config.json`（后续 Task 处理）
  - 不要修改 `requirements.txt`（除非需要新增依赖）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯粹的文件操作，无复杂逻辑
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Tasks 2,3,4 并行）
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: 无

  **References**:
  - 当前项目根目录结构（见 README）
  - 本计划中的"新目录结构"

  **Acceptance Criteria**:
  - [ ] `handlers/__init__.py` 存在且包含 `__version__ = "1.0"`
  - [ ] `workflows/` 目录存在
  - [ ] `workflows/settings.json` 存在且为空配置 `{"current_workflow": ""}`
  - [ ] `tests/` 目录存在
  - [ ] `_archive/` 目录存在且包含旧调试脚本
  - [ ] 原始 `form_filler.py` 仍然存在（尚未修改）
  - [ ] `python -c "import handlers"` 成功（包可导入）

  **QA Scenarios**:
  ```
  Scenario: 验证目录结构
    Tool: Bash
    Preconditions: 结构创建完毕
    Steps:
      1. Test-Path -LiteralPath "handlers/__init__.py"
      2. Test-Path -LiteralPath "workflows/csms_create_proposal"
      3. Test-Path -LiteralPath "workflows/gracubuy_create_gr"
      4. Test-Path -LiteralPath "workflows/settings.json"
      5. Test-Path -LiteralPath "tests"
      6. Test-Path -LiteralPath "_archive"
    Expected Result: 所有路径存在
    Evidence: .sisyphus/evidence/task-1-directory-structure.txt

  Scenario: 验证 handlers 包可导入
    Tool: Bash
    Preconditions: handlers/__init__.py 存在
    Steps:
      1. python -c "from handlers import __version__; print(__version__)"
    Expected Result: 输出 "1.0"，无导入错误
    Evidence: .sisyphus/evidence/task-1-handlers-import.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-1-directory-structure.txt`
  - [ ] `.sisyphus/evidence/task-1-handlers-import.txt`

  **Commit**: YES
  - Message: `refactor(project): restructure project with workflows/ and handlers/ directories`
  - Files: 所有新建文件和移动的文件

- [x] 2. **Workflow JSON Schema 定义 + 验证器**

  **What to do**:
  - 在 `workflows/` 下创建 `schema/` 目录，存放 JSON Schema 定义文件
  - 定义 `workflow-schema.json`（JSON Schema draft-07 格式），包含以下顶层字段：
    - `$schema`、`workflow_name`、`version`、`description`（基本信息）
    - `browser`（channel, executable_path）
    - `login`（url, enabled, fallback_selectors: {username[], password[], submit[]}）
    - `navigation`（action steps 数组：[{action, url?, selector?, wait_until?, timeout?}]）
    - `fields`（字段定义对象，key 为字段名称）：
      - 每个字段：`selector`, `type` (input/select/autocomplete/datepicker/popup_search/file_upload/checkbox), `required`, `default_value`
      - `handler_config`（可选，提供给处理器的额外参数）
      - `post_fill`（可选，填写后的触发动作）
      - `depends_on`（可选，字段依赖）
    - `handlers`（可选，工作流级别的特殊处理器配置）
    - `attachment`（可选，附件上传选择器配置）
    - `post_fill`（工作流级别的填充后动作）
  - 使用 `workflow-schema.json` 编写一个 `validate_workflow.py` 验证工具
  - `WorkflowManager` 在加载每个 workflow.json 时自动调用验证

  **Must NOT do**:
  - 不要添加 if/then/else 条件逻辑到 schema
  - 不要使任何字段类型与特定工作流耦合（schema 必须通用）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: JSON Schema 设计需要前瞻性，要考虑两个工作流的差异
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Tasks 1,3,4 并行）
  - **Blocks**: Tasks 3, 12, 13
  - **Blocked By**: Task 1

  **References**:
  - `form_config.json` - 现有 CSMS 字段配置格式
  - `attachment_config.json` - 现有附件配置格式
  - `form_filler.py:559-1174` - 现有自动化流程中隐含的参数
  - `workflows/csms_create_proposal/workflow.json`（本 Task 创建示例但不完整）

  **Acceptance Criteria**:
  - [ ] `workflows/schema/workflow-schema.json` 存在且为合法 JSON Schema
  - [ ] schema 使用 `$ref` 定义可复用类型（如 `selector_type`, `action_step`）
  - [ ] 所有必需的顶层字段在 `required` 中声明
  - [ ] `validate_workflow.py` 存在
  - [ ] `python validate_workflow.py workflows/csms_create_proposal/workflow.json` 可运行
  - [ ] invalid workflow.json → 验证器返回非零退出码 + 清晰错误信息

  **QA Scenarios**:
  ```
  Scenario: 验证 Schema 本身合法
    Tool: Bash
    Preconditions: workflow-schema.json 已创建
    Steps:
      1. python -c "import json; json.load(open('workflows/schema/workflow-schema.json'))"
    Expected Result: JSON 解析成功
    Evidence: .sisyphus/evidence/task-2-schema-valid.txt

  Scenario: 验证器拒绝无效配置
    Tool: Bash
    Preconditions: validate_workflow.py 已创建
    Steps:
      1. echo '{"bad": "config"}' > /tmp/bad-workflow.json
      2. python validate_workflow.py /tmp/bad-workflow.json 2>&1
    Expected Result: 退出码 ≠ 0，输出包含错误描述
    Evidence: .sisyphus/evidence/task-2-validation-fail.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-2-schema-valid.txt`
  - [ ] `.sisyphus/evidence/task-2-validation-fail.txt`

  **Commit**: YES
  - Message: `feat(schema): add workflow JSON schema and validator`
  - Files: `workflows/schema/workflow-schema.json`, `workflows/schema/validate_workflow.py`

- [x] 3. **WorkflowManager 类**

  **What to do**:
  - 在 `workflow_manager.py` 中实现 `WorkflowManager` 类
  - 功能：
    - `discover_workflows()`: 扫描 `workflows/` 目录，查找包含 `workflow.json` 的子目录
    - `load_workflow(name)`: 加载指定工作流的 `workflow.json`，执行 schema 验证
    - `list_workflows()`: 返回所有可用工作流的 `(name, display_name)` 列表
    - `get_current_workflow()`: 从 `workflows/settings.json` 读取当前选中的工作流
    - `set_current_workflow(name)`: 保存当前选中的工作流到 `settings.json`
    - `get_field_definitions()`: 返回当前工作流的字段定义列表（供 GUI 使用）
    - `get_workflow_info(name)`: 返回工作流的基本信息（名称、版本、描述）
  - 错误处理：`workflow.json` 不存在 → 抛出 `WorkflowNotFoundError`
  - 错误处理：schema 验证失败 → 抛出 `WorkflowValidationError`（包含验证器输出的详细信息）
  - 使用 `dataclass` 定义 `WorkflowInfo`、`FieldDefinition` 等数据结构

  **Must NOT do**:
  - 不要在这个类中包含任何 Playwright 或浏览器逻辑
  - 不要缓存工作流配置（每次调用重新读取）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要设计清晰的 API 接口供 GUI 和 Engine 使用
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Tasks 1,2,4 并行）
  - **Blocks**: Tasks 10, 11
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `workflows/schema/workflow-schema.json`（Task 2 产出，定义了配置结构）
  - `workflows/settings.json`（Task 1 创建）
  - `config_manager.py`（现有 ConfigManager 类可参考其 save/load 模式）

  **Acceptance Criteria**:
  - [ ] `WorkflowManager` 类存在且有完整的类型注解
  - [ ] `WorkflowInfo` dataclass 包含 `name`, `display_name`, `version`, `description`
  - [ ] `FieldDefinition` dataclass 包含 `label`, `selector`, `field_type`, `required`, `default_value`
  - [ ] `WorkflowNotFoundError` 和 `WorkflowValidationError` 自定义异常定义
  - [ ] 单元测试风格验证：运行 `python -c "from workflow_manager import WorkflowManager; wm = WorkflowManager(); print(len(wm.list_workflows()))"` → 输出 > 0
  - [ ] 无效工作流目录不崩溃，只打印 WARNING 并跳过

  **QA Scenarios**:
  ```
  Scenario: 发现工作流列表
    Tool: Bash
    Preconditions: WorkflowManager 已实现，workflows/ 目录至少有一个子目录含 workflow.json
    Steps:
      1. python -c "from workflow_manager import WorkflowManager; wm = WorkflowManager(); workflows = wm.list_workflows(); [print(f'{w[\"name\"]}: {w[\"display_name\"]}') for w in workflows]"
    Expected Result: 输出至少包含 "csms_create_proposal" 和 "gracubuy_create_gr"
    Evidence: .sisyphus/evidence/task-3-workflow-list.txt

  Scenario: 加载和切换工作流
    Tool: Bash
    Preconditions: WorkflowManager 已实现
    Steps:
      1. python -c "from workflow_manager import WorkflowManager; wm = WorkflowManager(); wm.set_current_workflow('csms_create_proposal'); print(wm.get_current_workflow())"
      2. python -c "from workflow_manager import WorkflowManager; wm = WorkflowManager(); info = wm.get_workflow_info('csms_create_proposal'); print(f'{info.name} v{info.version}')"
    Expected Result: 显示 "csms_create_proposal" 和版本号
    Evidence: .sisyphus/evidence/task-3-workflow-switch.txt

  Scenario: 无效工作流错误处理
    Tool: Bash
    Preconditions: 无
    Steps:
      1. python -c "from workflow_manager import WorkflowManager, WorkflowNotFoundError; wm = WorkflowManager(); wm.load_workflow('nonexistent_workflow')" 2>&1
    Expected Result: 抛出 WorkflowNotFoundError
    Evidence: .sisyphus/evidence/task-3-workflow-error.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-3-workflow-list.txt`
  - [ ] `.sisyphus/evidence/task-3-workflow-switch.txt`
  - [ ] `.sisyphus/evidence/task-3-workflow-error.txt`

  **Commit**: YES
  - Message: `feat(engine): add WorkflowManager for workflow discovery, loading and switching`
  - Files: `workflow_manager.py`

- [x] 4. **BaseHandler + HandlerRegistry**

  **What to do**:
  - 在 `handlers/base_handler.py` 中定义 `BaseHandler` 抽象基类
  - Handler 接口：
    ```python
    class BaseHandler(ABC):
        def __init__(self, page, workflow_config: dict):
            self.page = page
            self.workflow_config = workflow_config

        @abstractmethod
        def execute(self, field_config: dict, value: str) -> dict:
            """
            执行字段填充。
            参数:
                field_config: 字段配置（来自 workflow.json 的 fields[name]）
                value: 要填充的值
            返回:
                {"success": bool, "message": str, "evidence": dict}
            """
            pass

        def validate(self, field_config: dict) -> list:
            """验证 field_config 是否包含执行所需的所有参数。返回错误信息列表"""
            return []

        def retry_count(self) -> int:
            """返回此处理器的默认重试次数"""
            return 2
    ```
  - 在 `handlers/__init__.py` 中实现 `HandlerRegistry`：
    - `register(handler_type: str, handler_class: type[BaseHandler])`: 注册处理器
    - `get_handler(handler_type: str) -> BaseHandler`: 获取处理器实例
    - `get_handler_for_field(field_config: dict) -> BaseHandler`: 根据 field_config 的 type 获取
    - `list_handler_types() -> list`: 列出所有注册的类型
  - 在 `handlers/__init__.py` 中自动导入所有处理器子模块（`from .input_handler import InputHandler` 等）
  - 在 `handlers/__init__.py` 末尾自动注册所有处理器
  - 提供 `register_handler(type_name, handler_class)` 函数供用户在 `handlers.py` 中注册自定义处理器

  **Must NOT do**:
  - 不要在此 Task 中实现具体处理器逻辑（只在子模块中留 stub）
  - 不要引入外部依赖

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 接口设计决定整个架构的扩展性
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Tasks 1,2,3 并行）
  - **Blocks**: Tasks 5, 6, 7, 8, 9
  - **Blocked By**: Task 1

  **References**:
  - 标准的 Python ABC 用法
  - 现有的 `form_filler.py` 中字段处理逻辑（938-1001行）作为具体处理器设计的参考
  - `handlers/__init__.py`（Task 1 创建的包文件）

  **Acceptance Criteria**:
  - [ ] `BaseHandler` 是 `ABC` 子类
  - [ ] `execute()` 是 `@abstractmethod`
  - [ ] `HandlerRegistry` 类存在且工作
  - [ ] 尝试实例化 `BaseHandler` 直接抛出 `TypeError`
  - [ ] `python -c "from handlers import HandlerRegistry; r = HandlerRegistry(); print(r.list_handler_types())"` 可运行
  - [ ] 所有 8 个 handler 文件（含 stub 类）已创建在 `handlers/` 目录下

  **QA Scenarios**:
  ```
  Scenario: 验证抽象基类
    Tool: Bash
    Preconditions: base_handler.py 已实现
    Steps:
      1. python -c "from handlers.base_handler import BaseHandler; BaseHandler(None, {})" 2>&1
    Expected Result: TypeError: Can't instantiate abstract class
    Evidence: .sisyphus/evidence/task-4-abstract-check.txt

  Scenario: 验证 Registry
    Tool: Bash
    Preconditions: 所有 handler stub 已创建并注册
    Steps:
      1. python -c "from handlers import HandlerRegistry; r = HandlerRegistry(); types = r.list_handler_types(); print(f'Registered: {types}'); print(f'Count: {len(types)}')"
    Expected Result: 列出至少 "input", "select", "autocomplete", "datepicker", "popup_search", "file_upload", "checkbox"
    Evidence: .sisyphus/evidence/task-4-registry-list.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-4-abstract-check.txt`
  - [ ] `.sisyphus/evidence/task-4-registry-list.txt`

  **Commit**: YES
  - Message: `feat(engine): add BaseHandler abstract class and HandlerRegistry`
  - Files: `handlers/base_handler.py`, `handlers/__init__.py`（修改）, `handlers/*_handler.py`（8个 stub文件）

- [x] 5. **InputHandler + SelectHandler + CheckboxHandler**

  **What to do**:
  - 在 `handlers/input_handler.py` 中实现 `InputHandler`:
    - `type`: "input"
    - 使用 `page.locator(selector).fill('')` → `fill(value)`
    - 支持 `textarea` 元素（与 input 相同处理）
    - `handler_config` 支持: `clear_first` (bool, 默认 true)
  - 在 `handlers/select_handler.py` 中实现 `SelectHandler`:
    - `type`: "select"
    - 使用 `page.locator(selector).select_option(value)`
    - `handler_config` 支持:
      - `trigger_postback` (bool, 默认 false): 为 true 时通过 JavaScript 触发 `__doPostBack`
      - `trigger_change_event` (bool, 默认 true): 触发 `change` 事件
      - `value_type` ("value" | "label", 默认 "value"): 按 value 或 label 选择
      - `wait_after_ms` (int, 默认 1000): 选择后等待时间
  - 在 `handlers/checkbox_handler.py` 中实现 `CheckboxHandler`:
    - `type`: "checkbox"
    - 解析值: "true"/"false", "1"/"0", "yes"/"no", True/False
    - 使用 `page.locator(selector).set_checked(bool_value)`
    - `handler_config` 支持: `force_click` (bool, 默认 false)

  **Must NOT do**:
  - 不要添加验证逻辑到处理器（验证由 `validate()` 方法处理）
  - 不要处理文件上传（由 FileUploadHandler 负责）
  - 不要处理非原生 select 元素（由 AutoCompleteHandler 负责）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要正确处理 ASP.NET 的 __doPostBack 机制
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 Tasks 6,7,8,9 并行）
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `form_filler.py:928-1001` - 字段类型检测和填充逻辑（select vs input）
  - `form_filler.py:938-973` - `__doPostBack` 触发逻辑
  - `form_filler.py:985-989` - input 填充逻辑

  **Acceptance Criteria**:
  - [ ] `InputHandler.execute()` 对 input 和 textarea 都正常工作
  - [ ] `SelectHandler.execute()` 支持 `select_option(value)` + `__doPostBack`
  - [ ] `CheckboxHandler.execute()` 支持 true/false, 1/0, yes/no
  - [ ] 每个 handler 都有 `validate()` 方法
  - [ ] `python -c "from handlers import HandlerRegistry; h = HandlerRegistry().get_handler('input'); print(h.__class__.__name__)"` → "InputHandler"

  **QA Scenarios**:
  ```
  Scenario: Handler 注册验证
    Tool: Bash
    Preconditions: 三个 handler 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; r = HandlerRegistry(); print(r.get_handler('input').__class__.__name__); print(r.get_handler('select').__class__.__name__); print(r.get_handler('checkbox').__class__.__name__)"
    Expected Result: 输出 "InputHandler\nSelectHandler\nCheckboxHandler"
    Evidence: .sisyphus/evidence/task-5-handlers-registered.txt

  Scenario: validate() 方法验证
    Tool: Bash
    Preconditions: handlers 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; r = HandlerRegistry(); errors = r.get_handler('input').validate({'selector': ''}); print(f'Errors: {errors}')"
    Expected Result: 空选择器应返回错误列表
    Evidence: .sisyphus/evidence/task-5-validate.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-5-handlers-registered.txt`
  - [ ] `.sisyphus/evidence/task-5-validate.txt`

  **Commit**: YES
  - Message: `feat(handlers): add InputHandler, SelectHandler and CheckboxHandler`
  - Files: `handlers/input_handler.py`, `handlers/select_handler.py`, `handlers/checkbox_handler.py`, `handlers/__init__.py`

- [x] 6. **AutoCompleteHandler（iValua SelectorControl）**

  **What to do**:
  - 在 `handlers/autocomplete_handler.py` 中实现 `AutoCompleteHandler`:
    - `type`: "autocomplete"
    - 支持两种模式（通过 `handler_config.mode` 配置）：
      - **"dropdown" 模式**（iValua Dropdown 类型）：
        1. 点击选择器 div 打开下拉菜单
        2. 在 `_search` 输入框中输入值
        3. 从 `.menu > .item` 列表中选择匹配项
        4. 点击确认
      - **"autocompletion" 模式**（iValua Autocompletion 类型）：
        1. 在 `_search` 输入框中输入值
        2. 等待服务器返回建议列表（wait_for_timeout）
        3. 从 `.scrolling.menu > .item` 中选择第一个匹配项
        4. 点击确认
    - `handler_config` 参数：
      - `mode`: "dropdown" | "autocompletion" (默认 "dropdown")
      - `search_input_selector`: 搜索输入框选择器（默认从 field selector + "_search" 拼接）
      - `dropdown_selector`: 下拉菜单选择器（默认 ".menu > .item"）
      - `wait_after_input_ms`: 输入后等待时间（默认 1000ms）
      - `clear_before`: 是否先清空（默认 true）
      - `hidden_input_selector`: 隐藏的 value input 选择器（某些 iValua 控件需要）

  **Must NOT do**:
  - 不要假设元素是原生 `<select>`（用 select_option 会失败）
  - 不要硬编码 iValua 特定的 class 名称（放在 handler_config 中）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: iValua 的自定义 SelectorControl 需要特殊的交互模式
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 Tasks 5,7,8,9 并行）
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `Create_ Group Procurement AcuBuy1.html` - 搜索 `SelectorControl` 和 `_search` 可找到具体 DOM 结构
  - `form_filler.py:938-973` - 原生 select 处理方式（AutoCompleteHandler 不应使用）
  - `form_filler.py:599-620` - 选择器探测模式（可作为 fallback 参考）

  **Acceptance Criteria**:
  - [ ] `AutoCompleteHandler` 支持 dropdown 和 autocompletion 两种模式
  - [ ] 两种模式通过 `handler_config.mode` 切换
  - [ ] 默认参数在无 `handler_config` 时也能工作
  - [ ] `validate()` 检查 `search_input_selector` 是否可构建

  **QA Scenarios**:
  ```
  Scenario: 处理器注册验证
    Tool: Bash
    Preconditions: autocomplete_handler.py 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; h = HandlerRegistry().get_handler('autocomplete'); print(h.__class__.__name__)"
    Expected Result: "AutoCompleteHandler"
    Evidence: .sisyphus/evidence/task-6-handler-registered.txt

  Scenario: 两种模式配置验证
    Tool: Bash
    Preconditions: handler 已实现
    Steps:
      1. python -c "from handlers.autocomplete_handler import AutoCompleteHandler; h = AutoCompleteHandler(None, {}); errors_dropdown = h.validate({'handler_config': {'mode': 'dropdown'}}); errors_auto = h.validate({'handler_config': {'mode': 'autocompletion'}}); print(f'Dropdown errors: {errors_dropdown}'); print(f'Autocompletion errors: {errors_auto}')"
    Expected Result: 两种模式均无关键错误（仅 selector 缺失警告）
    Evidence: .sisyphus/evidence/task-6-mode-validation.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-6-handler-registered.txt`
  - [ ] `.sisyphus/evidence/task-6-mode-validation.txt`

  **Commit**: YES
  - Message: `feat(handlers): add AutoCompleteHandler for iValua SelectorControl`
  - Files: `handlers/autocomplete_handler.py`, `handlers/__init__.py`

- [x] 7. **DatePickerHandler**

  **What to do**:
  - 在 `handlers/datepicker_handler.py` 中实现 `DatePickerHandler`:
    - `type`: "datepicker"
    - 支持两种模式（通过 `handler_config.mode` 配置）：
      - **"direct_input" 模式**：
        1. 直接在日期输入框中 `fill()` 日期值
        2. 触发 `change` / `blur` 事件
      - **"popup" 模式**（CSMS Cal.aspx 风格）：
        1. 点击触发按钮打开日历弹窗
        2. 在弹窗页面中选择年、月、日
        3. 弹窗自动关闭
    - `handler_config` 参数：
      - `mode`: "direct_input" | "popup" (默认 "direct_input")
      - `date_format`: "MM/DD/YYYY" | "DD/MM/YYYY" | "YYYY-MM-DD"
      - `trigger_selector`: 触发按钮选择器（popup 模式必需）
      - `popup_wait_timeout_ms`: 等待弹窗加载时间（默认 5000ms）
      - `year_selector`: 年份选择器（popup 模式）
      - `month_selector`: 月份选择器（popup 模式）
      - `day_pattern`: 日期匹配模式，`{day}` 会被替换为实际日期（popup 模式）
    - 日期值解析：支持 `MM/DD/YYYY`、`YYYY-MM-DD`、Excel 序列号等常见格式
    - 处理 `pd.Timestamp` 类型（从 Excel 读取时）

  **Must NOT do**:
  - 不要假设所有日期选择器都是弹窗模式（GR-Acubuy 使用内联日期选择器）
  - 不要硬编码日期格式

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要处理多种日期选择模式
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 Tasks 5,6,8,9 并行）
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `form_filler.py:750-807` - CSMS Date of Award 处理（direct_input + change event）
  - `form_filler.py:762-780` - 日期解析逻辑
  - `Create_ Group Procurement AcuBuy1.html` - 搜索 `hasDatepicker` 或 `datepicker` 可找到内联日期选择器

  **Acceptance Criteria**:
  - [ ] 支持 direct_input 和 popup 两种模式
  - [ ] 支持 `MM/DD/YYYY` 和 `YYYY-MM-DD` 格式的输入值
  - [ ] 支持 `pd.Timestamp` 类型输入值
  - [ ] popup 模式完整执行：点击触发按钮 → 等待弹窗 → 选择年/月/日 → 关闭弹窗

  **QA Scenarios**:
  ```
  Scenario: 处理器注册验证
    Tool: Bash
    Preconditions: datepicker_handler.py 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; h = HandlerRegistry().get_handler('datepicker'); print(h.__class__.__name__)"
    Expected Result: "DatePickerHandler"
    Evidence: .sisyphus/evidence/task-7-handler-registered.txt

  Scenario: 日期解析测试
    Tool: Bash
    Preconditions: handler 已实现
    Steps:
      1. python -c "from handlers.datepicker_handler import DatePickerHandler; h = DatePickerHandler(None, {}); print(h._parse_date('01/15/2024')); print(h._parse_date('2024-01-15')); print(h._format_date('01/15/2024', 'YYYY-MM-DD'))"
    Expected Result: 日期解析和格式化正确
    Evidence: .sisyphus/evidence/task-7-date-parsing.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-7-handler-registered.txt`
  - [ ] `.sisyphus/evidence/task-7-date-parsing.txt`

  **Commit**: YES
  - Message: `feat(handlers): add DatePickerHandler with direct_input and popup modes`
  - Files: `handlers/datepicker_handler.py`, `handlers/__init__.py`

- [x] 8. **PopupSearchHandler（弹窗搜索）**

  **What to do**:
  - 在 `handlers/popup_search_handler.py` 中实现 `PopupSearchHandler`:
    - `type`: "popup_search"
    - 用途：处理需要打开弹窗 → 搜索 → 选择结果的字段（如 CSMS 的 Priming Project Manager）
    - 执行流程：
      1. 点击触发按钮（`trigger_selector`）
      2. 使用 `page.expect_popup()` 等待弹窗出现
      3. 在弹窗中执行搜索步骤序列（来自 `handler_config.steps`）
      4. 弹窗自动关闭
    - `handler_config` 参数：
      - `trigger_selector`: 触发弹窗的按钮选择器
      - `popup_timeout_ms`: 等待弹窗出现超时（默认 10000ms）
      - `steps`: 搜索步骤数组：
        ```json
        [
          {"action": "fill", "selector": "#txtOAID", "value_source": "field_value"},
          {"action": "click", "selector": "input[type='submit'][value*='Search']"},
          {"action": "wait", "timeout_ms": 2000},
          {"action": "click", "selector": "table tr:nth-child(2)"},
          {"action": "click", "selector": "input[type='submit'][value*='Select']"}
        ]
        ```
      - 支持的动作类型：`fill`, `click`, `wait`, `select_option`, `evaluate`
    - 如果 `expect_popup()` 超时，回退到在当前页面查找弹窗元素（某些 ASP.NET 弹窗可能不是真正的 popup）

  **Must NOT do**:
  - 不要硬编码搜索步骤（完全由 handler_config.steps 驱动）
  - 不要假设弹窗是独立窗口或 iframe（支持两种检测方式）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 弹窗处理需要处理 popup、iframe、同页面浮层等多种场景
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 Tasks 5,6,7,9 并行）
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `form_filler.py:809-901` - CSMS Priming Project Manager 弹窗搜索完整逻辑
  - `form_filler.py:834-848` - popup vs iframe 检测逻辑

  **Acceptance Criteria**:
  - [ ] 支持配置化的搜索步骤序列
  - [ ] 支持 `fill`, `click`, `wait`, `select_option`, `evaluate` 五种动作类型
  - [ ] popup 超时时自动回退到同页面查找
  - [ ] 每个步骤都有错误处理（单个步骤失败不崩溃）

  **QA Scenarios**:
  ```
  Scenario: 处理器注册验证
    Tool: Bash
    Preconditions: popup_search_handler.py 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; h = HandlerRegistry().get_handler('popup_search'); print(h.__class__.__name__)"
    Expected Result: "PopupSearchHandler"
    Evidence: .sisyphus/evidence/task-8-handler-registered.txt

  Scenario: 步骤配置验证
    Tool: Bash
    Preconditions: handler 已实现
    Steps:
      1. python -c "from handlers.popup_search_handler import PopupSearchHandler; h = PopupSearchHandler(None, {}); steps = [{'action': 'fill', 'selector': '#txtOAID'}, {'action': 'click', 'selector': '#btnSearch'}]; errors = h.validate({'handler_config': {'trigger_selector': '#btn', 'steps': steps}}); print(f'Errors: {errors}')"
    Expected Result: 合法配置无错误
    Evidence: .sisyphus/evidence/task-8-steps-validation.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-8-handler-registered.txt`
  - [ ] `.sisyphus/evidence/task-8-steps-validation.txt`

  **Commit**: YES
  - Message: `feat(handlers): add PopupSearchHandler with configurable search steps`
  - Files: `handlers/popup_search_handler.py`, `handlers/__init__.py`

- [x] 9. **FileUploadHandler**

  **What to do**:
  - 在 `handlers/file_upload_handler.py` 中实现 `FileUploadHandler`:
    - `type`: "file_upload"
    - 支持两种模式（通过 `handler_config.mode` 配置）：
      - **"native" 模式**（CSMS 风格）：
        1. 使用 `page.locator(selector).set_input_files(file_path)`
        2. 原生 `<input type="file">` 元素
      - **"html5_uploader" 模式**（iValua 风格）：
        1. 点击上传按钮打开文件选择器
        2. 使用 Playwright 的 `page.locator('input[type="file"]').set_input_files()` 选择文件
        3. 等待上传完成（监听 XHR 或等待进度条消失）
    - `handler_config` 参数：
      - `mode`: "native" | "html5_uploader"
      - `file_input_selector`: 文件输入选择器（native 模式）
      - `upload_button_selector`: 上传按钮选择器（html5_uploader 模式）
      - `wait_upload_complete_selector`: 上传完成后等待消失的元素选择器
      - `wait_upload_timeout_ms`: 上传超时时间（默认 30000ms）
    - 文件路径校验：执行 `os.path.exists()` 检查，不存在则返回错误

  **Must NOT do**:
  - 不要假设所有文件上传都是 native `<input type="file">`
  - 不要在处理器中处理附件管理的 Category/Description 逻辑（那是 WorkflowEngine 的职责）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: iValua 的 HTML5 Uploader 是异步的，需要等待上传完成
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 Tasks 5,6,7,8 并行）
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `form_filler.py:976-984` - 原生文件上传处理
  - `form_filler.py:1094-1120` - 附件文件中 file 上传选择器探测
  - `Create_ Group Procurement AcuBuy1.html:1751-1801` - HTML5 Uploader JavaScript 初始化代码

  **Acceptance Criteria**:
  - [ ] 支持 native 和 html5_uploader 两种模式
  - [ ] 文件路径不存在时返回错误（不崩溃）
  - [ ] html5_uploader 模式在上传完成后才返回

  **QA Scenarios**:
  ```
  Scenario: 处理器注册验证
    Tool: Bash
    Preconditions: file_upload_handler.py 已实现
    Steps:
      1. python -c "from handlers import HandlerRegistry; h = HandlerRegistry().get_handler('file_upload'); print(h.__class__.__name__)"
    Expected Result: "FileUploadHandler"
    Evidence: .sisyphus/evidence/task-9-handler-registered.txt

  Scenario: 文件不存在处理
    Tool: Bash
    Preconditions: handler 已实现
    Steps:
      1. python -c "from handlers.file_upload_handler import FileUploadHandler; h = FileUploadHandler(None, {}); result = h.execute({'handler_config': {'mode': 'native', 'file_input_selector': '#file'}, 'selector': '#file'}, '/nonexistent/file.pdf'); print(result)"
    Expected Result: {"success": false, "message": "File not found: ..."}
    Evidence: .sisyphus/evidence/task-9-file-not-found.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-9-handler-registered.txt`
  - [ ] `.sisyphus/evidence/task-9-file-not-found.txt`

  **Commit**: YES
  - Message: `feat(handlers): add FileUploadHandler with native and html5_uploader modes`
  - Files: `handlers/file_upload_handler.py`, `handlers/__init__.py`

- [x] 10. **WorkflowEngine（导航 + 字段遍历 + 事件 + 重试）**

  **What to do**:
  - 在 `workflow_engine.py` 中实现 `WorkflowEngine` 类
  - 核心功能：
    1. **导航执行**: 遍历 `workflow.json` 中的 `navigation` 数组，执行每个 action
       - 支持的 action 类型：`goto`, `click`, `wait_selector`, `wait_time`, `evaluate`
       - 每个 action 支持 `timeout`、`optional`（失败时跳过不崩溃）参数
       - 模拟 `page.goto(url, wait_until=...)`、`page.click(selector)`、`page.wait_for_selector(selector, timeout=...)`
    2. **登录处理**: 解析 `workflow.json` 的 `login` 配置
       - 执行导航中的登录步骤（如果没有单独的 navigation 步骤）
       - 传入用户名/密码值
       - 使用 `login.fallback_selectors` 逐级尝试
    3. **字段遍历**: 按顺序处理 `fields` 中的每个字段
       - 通过 `HandlerRegistry` 获取对应类型的处理器
       - 调用 `handler.execute(field_config, value)` 
       - 处理 `depends_on` 依赖排序（先填充依赖字段）
       - 处理 `post_fill` 动作（如填写 Proposal # 后点击 CRM INFO 按钮）
    4. **重试机制**: 每个字段处理失败时自动重试
       - 从 `handler.retry_count()` 获取重试次数
       - 重试间等待 1s
       - 全部重试失败 → 抛出 `WorkflowError`（含失败字段名和原因）
    5. **附件处理**: 如果工作流有 `attachment` 配置，处理附件上传
       - 使用 FileUploadHandler 上传文件
       - 使用 SelectHandler 选择 Category
       - 使用 InputHandler 填写 Description
    6. **事件回调**: 在关键生命周期点触发回调
       - `on_step_start(step_name)` / `on_step_end(step_name)`
       - `on_field_start(field_name)` / `on_field_end(field_name, result)`
       - `on_error(field_name, error)` 
       - 这些回调由 GUI 注册，用于更新日志和进度条
  - 状态管理：
    - `current_state`: 记录当前执行到的步骤
    - `results`: 记录每个字段的执行结果 `{field_name: {"success": bool, "message": str}}`
    - `is_running`: bool，控制停止标志
  - 错误处理：
    - 字段级错误：触发重试 → 重试耗尽 → 抛出 `WorkflowFieldError`
    - 导航级错误：`optional=True` 时跳过并记录 WARNING；否则抛出 `WorkflowNavigationError`
    - 全局异常：捕获所有未预期异常，包装为 `WorkflowEngineError`

  **Must NOT do**:
  - 不要包含任何 tkinter 或 GUI 代码（Engine 是纯逻辑层）
  - 不要缓存 `page` 对象（由调用者传入）
  - 不要在工作流配置不存在时猜测默认值

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 这是整个架构的核心，需要协调所有子系统
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖多个前置任务）
  - **Parallel Group**: Wave 3（与 Task 11 并行）
  - **Blocks**: Tasks 12, 13, 14
  - **Blocked By**: Tasks 2, 3, 5, 6, 7, 8, 9

  **References**:
  - `form_filler.py:559-1174` - 现有 `_fill_form()` 方法作为参考
  - `workflow_manager.py` - WorkflowManager 类（Task 3 产出）
  - `handlers/` - 所有处理器（Tasks 5-9 产出）
  - `workflows/schema/workflow-schema.json` - 配置 schema（Task 2 产出）

  **Acceptance Criteria**:
  - [ ] `WorkflowEngine` 类可实例化
  - [ ] 导航执行：支持 goto, click, wait_selector, wait_time, evaluate
  - [ ] 字段遍历：按 `depends_on` 顺序处理字段
  - [ ] 重试机制：失败后重试，次数用完抛出 `WorkflowFieldError`
  - [ ] 事件回调：`on_step_start/on_step_end/on_field_start/on_field_end/on_error`
  - [ ] `stop()` 方法可在执行中安全停止
  - [ ] `python -c "from workflow_engine import WorkflowEngine; print('OK')"` → "OK"

  **QA Scenarios**:
  ```
  Scenario: 引擎导入和实例化
    Tool: Bash
    Preconditions: workflow_engine.py 已实现
    Steps:
      1. python -c "from workflow_engine import WorkflowEngine; print('Import OK')"
    Expected Result: "Import OK"
    Evidence: .sisyphus/evidence/task-10-engine-import.txt

  Scenario: 空配置错误处理
    Tool: Bash
    Preconditions: engine 已实现，schemas 已存在
    Steps:
      1. python -c "
from workflow_engine import WorkflowEngine
engine = WorkflowEngine(None, {'workflow_name': 'test', 'fields': {}})
result = engine.execute()
print(f'Result: {result}')
"
    Expected Result: 返回结果，不崩溃（空配置合法）
    Evidence: .sisyphus/evidence/task-10-empty-config.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-10-engine-import.txt`
  - [ ] `.sisyphus/evidence/task-10-empty-config.txt`

  **Commit**: YES
  - Message: `feat(engine): add WorkflowEngine with navigation, field iteration and retry logic`
  - Files: `workflow_engine.py`, `handlers/__init__.py`（修改）

- [x] 11. **GUI 重构 + 工作流选择器**

  **What to do**:
  - 重写 `form_filler.py` 的主 GUI 类 `FormFillerApp`
  - 新增 GUI 元素：
    1. **工作流选择器**: 顶部下拉菜单（`ttk.Combobox`）
       - 从 `WorkflowManager.list_workflows()` 获取列表
       - 选中时触发 `on_workflow_changed()` 事件
       - 界面自动切换：登录URL、字段列表、附件配置区域
    2. **动态字段区域**: 根据当前工作流的 `fields` 自动生成
       - 从 `WorkflowManager.get_field_definitions()` 获取
       - 生成字段行：字段名称（含 required 标记 *）+ 值输入框
       - 如果是下拉框类型且有 options，显示为 `ttk.Combobox`
    3. **日志面板**: 集成 `auto_create_proposal.py` 的日志文本框
       - 注册到 `WorkflowEngine` 的事件回调
       - `on_step_start` → 显示 `>>> 步骤 N: xxx`
       - `on_field_start` → 显示 `  处理字段 xxx`
       - `on_field_end` → 显示 `  ✓ 完成` 或 `  ✗ 失败`
       - `on_error` → 显示 `  ⚠️ 错误: xxx`
    4. **进度指示**: 显示当前进度（如 `字段 5/12`）
    5. **停止按钮**: 调用 `WorkflowEngine.stop()` 停止执行
  - 保留现有的：Excel 文件选择、浏览器设置、登录信息输入、附件管理
  - 移除不再需要的：手动添加/编辑/删除字段按钮（字段由工作流配置驱动）
  - 使用 `WorkflowManager.set_current_workflow()` 持久化工作流选择，下次启动自动恢复

  **Must NOT do**:
  - 不要在 GUI 中包含任何 Playwright 逻辑
  - 不要硬编码任何字段配置

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: tkinter GUI 重构需要良好的用户体验设计
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖多个前置任务）
  - **Parallel Group**: Wave 3（与 Task 10 并行）
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 3, 10

  **References**:
  - `form_filler.py:234-378` - 现有 GUI 创建代码
  - `form_filler.py:519-541` - `_start_filling` 方法
  - `auto_create_proposal.py:44-180` - 日志面板和停止按钮参考
  - `workflow_manager.py` - WorkflowManager（Task 3 产出）

  **Acceptance Criteria**:
  - [ ] GUI 顶部有工作流下拉菜单
  - [ ] 切换工作流时，字段列表和 URL 自动更新
  - [ ] 日志面板显示执行进度
  - [ ] 停止按钮可中断正在执行的流程
  - [ ] 工作流选择在程序重启后保持
  - [ ] `python form_filler.py` 可正常启动 GUI

  **QA Scenarios**:
  ```
  Scenario: GUI 启动验证
    Tool: Bash
    Preconditions: form_filler.py 已重写
    Steps:
      1. python -c "
import sys
sys.argv = ['form_filler.py', '--test']
from form_filler import FormFillerApp
app = FormFillerApp()
print(f'Workflows: {app.workflow_combo[\"values\"]}')
app.destroy()
"
    Expected Result: 列出 CSMS 和 GR-Acubuy 工作流
    Evidence: .sisyphus/evidence/task-11-gui-init.txt

  Scenario: 工作流切换验证
    Tool: Bash
    Preconditions: GUI 已实现
    Steps:
      1. python -c "
from form_filler import FormFillerApp
app = FormFillerApp()
app.workflow_combo.current(1)  # 切换到第二个工作流
app.on_workflow_changed()
print(f'URL: {app.target_url.get()}')
print(f'Fields count: {len(app.field_entries)}')
app.destroy()
"
    Expected Result: URL 和字段列表根据工作流变更
    Evidence: .sisyphus/evidence/task-11-workflow-switch.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-11-gui-init.txt`
  - [ ] `.sisyphus/evidence/task-11-workflow-switch.txt`

  **Commit**: YES
  - Message: `feat(gui): add workflow selector and dynamic field loading to GUI`
  - Files: `form_filler.py`

- [x] 12. **CSMS 工作流配置**

  **What to do**:
  - 在 `workflows/csms_create_proposal/workflow.json` 中编写完整的 CSMS 工作流配置
  - 配置内容：
    - `workflow_name`: "CSMS Create Proposal Group"
    - `version`: "1.3"
    - `browser`: channel="chrome", executable_path 默认值
    - `login`:
      - `url`: "https://csmstest.ncs.com.sg/UAT/"
      - `fallback_selectors`: 从现有代码的 599-620 行提取用户名/密码/提交选择器
    - `navigation`:
      - CSMS 流程：goto Create PG 页面 → wait_for_selector Proposal # 输入框
    - `fields`:
      - **Proposal #**: type=input, 带 `post_fill` 动作（点击 CRM INFO 按钮 + 等待加载）
      - **Cust Ref. No**: type=input
      - **Proposal/Contract Value**: type=input
      - **Selling Price Currency Code**: type=select, handler_config.trigger_postback=true
      - **Date of Award**: type=datepicker, handler_config.mode="popup"（CSMS 的 Cal.aspx 风格，但在 v1.3 实际使用 direct_input，这里两种都可以配置）
      - **Priming Project Manager**: type=popup_search, 带完整 steps 配置
    - `handlers`:
      - popup_search 的完整步骤（同 Task 8 的示例）
    - `attachment`: 从现有 `form_filler.py:1036-1047` 提取选择器模式
    - `post_fill.action`: "manual_review", create_button 选择器
  - 数据来源：
    - 字段配置从 `form_config.json` 迁移
    - 附件配置从 `attachment_config.json` 迁移到 workflow 的 attachment 部分（可选项）
    - Excel 模板路径指向 `Proposal_Data_Template.csv`
  - 处理旧的 `form_config.json`：如果文件存在，启动时打印提示"已迁移到工作流配置"

  **Must NOT do**:
  - 不要在 workflow.json 中包含 `auto_create_proposal.py` 特有的字段
  - 不要破坏 schema 验证

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要精确映射现有 CSMS 行为到配置
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4（与 Task 13 并行）
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 2, 10

  **References**:
  - `form_config.json` - 当前字段配置（6个字段）
  - `attachment_config.json` - 当前附件配置
  - `form_filler.py:559-1174` - 完整自动化流程（需提取所有选择器和参数）
  - `Proposal_Data_Template.csv` - Excel 模板
  - `workflows/schema/workflow-schema.json` - 需符合 schema 验证

  **Acceptance Criteria**:
  - [ ] `workflow.json` 通过 schema 验证
  - [ ] 所有 6 个 CSMS 字段已配置
  - [ ] Proposal # 的 post_fill 动作（点击 CRM INFO）已配置
  - [ ] Date of Award 使用 direct_input 模式（与 v1.3 一致）
  - [ ] Selling Price Currency Code 配置了 trigger_postback
  - [ ] Priming Project Manager 配置了完整的弹窗搜索步骤
  - [ ] 附件配置的选择器与现有代码一致

  **QA Scenarios**:
  ```
  Scenario: Schema 验证
    Tool: Bash
    Preconditions: workflow.json 已创建，validate_workflow.py 存在
    Steps:
      1. python workflows/schema/validate_workflow.py workflows/csms_create_proposal/workflow.json
    Expected Result: 退出码 0，输出 "Valid: workflows/csms_create_proposal/workflow.json"
    Evidence: .sisyphus/evidence/task-12-schema-valid.txt

  Scenario: 字段数量验证
    Tool: Bash
    Preconditions: workflow.json 已创建
    Steps:
      1. python -c "import json; wf=json.load(open('workflows/csms_create_proposal/workflow.json')); print(f'Fields: {len(wf[\"fields\"])}')"
    Expected Result: 字段数量 ≥ 6
    Evidence: .sisyphus/evidence/task-12-field-count.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-12-schema-valid.txt`
  - [ ] `.sisyphus/evidence/task-12-field-count.txt`

  **Commit**: YES
  - Message: `feat(workflow): add CSMS Create Proposal workflow configuration`
  - Files: `workflows/csms_create_proposal/workflow.json`

- [x] 13. **GR-Acubuy 工作流配置**

  **What to do**:
  - 在 `workflows/gracubuy_create_gr/workflow.json` 中编写 GR-Acubuy 工作流配置
  - 配置内容：
    - `workflow_name`: "GR-Acubuy Create Goods Receipt"
    - `version`: "1.0"
    - `description`: "Singtel iValua 平台 Acubuy 采购收货单创建"
    - `browser`: channel="chrome"
    - `login`:
      - `url`: "https://singtel.ivalua.app/page.aspx/en/ord/delivery_manage?Create"
      - `fallback_selectors`: iValua 登录页面选择器（后续需要实际测试确定）
    - `navigation`:
      - 直接 goto Create 页面 → wait_for_selector 关键字段（如 `txtCode`）
    - `fields`（关键字段，基于 HTML 分析）:
      - **Delivery Note** (txtCode): type=input, required
      - **Supplier** (selSupplier): type=autocomplete, mode="autocompletion"
      - **Order** (selOrder): type=autocomplete, depends_on="Supplier"
      - **Movement Type** (selector_single_delivery_20240813130131934): type=autocomplete, mode="dropdown"
      - **Document Date** (datetime_delivery_20240821154312162): type=datepicker, mode="direct_input"
      - **Document Header Text** (udt_label_delivery_20240821161130552): type=input
      - **Service Item** (selector_single_delivery_20240820170609162): type=autocomplete
      - **Account Assignment Category**: type=autocomplete
      - **Internal Comment** (udt_desc_delivery_20240807223748988): type=input, required
      - **Approver 2 (Min Band E)**: type=autocomplete, 需先展开 hidden section
    - `handlers`:
      - 可能需要自定义 handler_config 来处理 iValua 的 SelectorControl 交互
    - `attachment`:
      - `mode`: "html5_uploader"
      - 基于 HTML 的分析配置上传选择器
    - `post_fill`:
      - `action`: "manual_review"（或 "click_button"）
      - `save_button_selector`: "#proxyActionBar_x__cmdSave"
      - `end_button_selector`: "#proxyActionBar_x__cmdEnd"

  **注意**: 此配置中的选择器（特别是自动完成字段的 `_search` 选择器）需要在实际页面上验证。配置中应包含 `"status": "draft"` 标记，表示此配置需要在实际环境中测试验证。

  **Must NOT do**:
  - 不要标记此配置为 "ready"（需要在真实页面测试后升级）
  - 不要假设所有字段的 `_search` 选择器都遵循相同模式

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要从 HTML 分析推断正确选择器
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4（与 Task 12 并行）
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 2, 10

  **References**:
  - `Create_ Group Procurement AcuBuy1.html` - Acubuy 创建页面 HTML（关键参考）
  - `Single Receipt _ ...AcuBuy2.html` / 3.html / 4.html - 其他页面
  - `workflows/schema/workflow-schema.json` - 需符合 schema 验证
  - `handlers/autocomplete_handler.py` - AutoCompleteHandler 配置参数

  **Acceptance Criteria**:
  - [ ] `workflow.json` 通过 schema 验证
  - [ ] 至少配置 10 个字段
  - [ ] Supplier、Order、Movement Type 使用 type=autocomplete
  - [ ] Supplier → Order 的 depends_on 依赖已配置
  - [ ] `status` 标记为 `"draft"`
  - [ ] 文档注释标明了每个字段的 HTML 来源

  **QA Scenarios**:
  ```
  Scenario: Schema 验证
    Tool: Bash
    Preconditions: workflow.json 已创建，validate_workflow.py 存在
    Steps:
      1. python workflows/schema/validate_workflow.py workflows/gracubuy_create_gr/workflow.json
    Expected Result: 退出码 0，输出 "Valid"
    Evidence: .sisyphus/evidence/task-13-schema-valid.txt

  Scenario: 配置完整性检查
    Tool: Bash
    Preconditions: workflow.json 已创建
    Steps:
      1. python -c "
import json
wf = json.load(open('workflows/gracubuy_create_gr/workflow.json'))
fields = wf['fields']
autocomplete = [k for k,v in fields.items() if v['type'] == 'autocomplete']
print(f'Autocomplete fields: {autocomplete}')
has_depends = any('depends_on' in v for v in fields.values())
print(f'Has dependencies: {has_depends}')
"
    Expected Result: 列出自动完成字段，有依赖关系
    Evidence: .sisyphus/evidence/task-13-config-check.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-13-schema-valid.txt`
  - [ ] `.sisyphus/evidence/task-13-config-check.txt`

  **Commit**: YES
  - Message: `feat(workflow): add GR-Acubuy Create GR workflow configuration (draft)`
  - Files: `workflows/gracubuy_create_gr/workflow.json`

- [x] 14. **集成测试 + 边界情况处理**

  **What to do**:
  - 整合所有组件，确保端到端工作流正常工作
  - 测试场景：
    1. **工作流切换流程**: GUI 启动 → 切换工作流 → 验证字段列表 → 验证 URL → 验证 Excel 模板路径
    2. **CSMS 回归**: 使用 Task 0 的回归脚本验证新引擎产出与旧代码一致
    3. **配置错误处理**:
       - 缺失 `workflow.json` → WorkflowManager 抛出 `WorkflowNotFoundError`
       - schema 验证失败 → GUI 显示错误信息
       - 字段选择器无效 → Handler 返回 `{"success": false, "message": "..."}`
    4. **重试机制验证**: 模拟字段失败 → 确认重试 2 次 → 最终返回失败
    5. **停止机制**: 引擎执行中 → 调用 stop() → 确认停止
  - 边界情况修复：
    - 路径中的中文字符（"自动填充网页表单信息"）兼容性检查
    - 空 Excel 文件处理
    - 浏览器未安装时的提示信息
    - 网络超时处理
  - 修复集成过程中发现的任何 import 循环、接口不匹配、类型错误

  **Must NOT do**:
  - 不要在集成测试中修改 core handler 接口（如果接口有问题，在 Task 5-9 中修复）
  - 不要添加新功能（此 Task 只修复集成问题）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要全面测试所有组件交互
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖所有前置任务）
  - **Parallel Group**: Wave 5（与 Task 15 并行）
  - **Blocks**: 无
  - **Blocked By**: Tasks 10, 11, 12, 13

  **References**:
  - 所有之前 Task 产出的文件
  - `tests/csms_regression.py` - 回归基线

  **Acceptance Criteria**:
  - [ ] `python form_filler.py` 启动无错误
  - [ ] 工作流切换后所有界面元素更新
  - [ ] 无效配置的错误信息用户友好
  - [ ] 重试机制按预期工作
  - [ ] 停止按钮可中断执行
  - [ ] 中文字符路径不导致崩溃

  **QA Scenarios**:
  ```
  Scenario: 端到端工作流切换
    Tool: Bash
    Preconditions: 所有组件已集成
    Steps:
      1. python -c "
from form_filler import FormFillerApp
app = FormFillerApp()
# 验证默认加载
print(f'Default workflow: {app.workflow_combo.get()}')
# 切换工作流
app.workflow_combo.current(1)
app.on_workflow_changed()
print(f'After switch - URL: {app.target_url.get()[:50]}...')
print(f'After switch - Fields: {len(app.field_entries)}')
app.destroy()
"
    Expected Result: 工作流切换后 URL 和字段列表更新
    Evidence: .sisyphus/evidence/task-14-integration-switch.txt

  Scenario: 无效配置测试
    Tool: Bash
    Preconditions: 创建一个无效的 workflow.json 副本
    Steps:
      1. python -c "
from workflow_manager import WorkflowManager, WorkflowValidationError
import tempfile, os, json
# 创建一个无效配置
bad_dir = os.path.join('workflows', '_test_bad')
os.makedirs(bad_dir, exist_ok=True)
with open(os.path.join(bad_dir, 'workflow.json'), 'w') as f:
    json.dump({'bad': 'config'}, f)
try:
    wm = WorkflowManager()
    result = wm.list_workflows()
    print('Graceful handling: OK')
finally:
    import shutil
    shutil.rmtree(bad_dir, ignore_errors=True)
"
    Expected Result: 无效配置被跳过，不崩溃
    Evidence: .sisyphus/evidence/task-14-bad-config.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-14-integration-switch.txt`
  - [ ] `.sisyphus/evidence/task-14-bad-config.txt`

  **Commit**: YES
  - Message: `fix: integration fixes and edge case handling`
  - Files: 根据实际修复的文件确定

- [x] 15. **打包更新 + 文档更新**

  **What to do**:
  - 更新 `执行打包.bat`:
    - 添加新的 `.py` 文件（`workflow_engine.py`, `workflow_manager.py`）
    - 添加 `workflows/` 目录到 `--add-data`
    - 添加 `handlers/` 包
    - 确保 `--hidden-import` 包含所有 handler 模块
  - 更新 `form_filler.spec`（如果使用）同步
  - 更新 `运行程序.bat` 确保路径正确
  - 简化项目文档：
    - 更新 `README.md` 反映新架构
    - 创建 `workflows/README.md` 说明如何添加新工作流

  **Must NOT do**:
  - 不要添加新的依赖到 `requirements.txt`（除非确有必要）
  - 不要删除旧的批处理文件

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 主要是文档编写
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5（与 Task 14 并行）
  - **Blocks**: 无
  - **Blocked By**: Task 14

  **References**:
  - `执行打包.bat` - 现有打包脚本
  - `form_filler.spec` - 现有 spec 文件
  - `README.md` - 现有文档

  **Acceptance Criteria**:
  - [ ] `执行打包.bat` 成功执行无错误
  - [ ] 打包后的 EXE 可运行并显示工作流选择器
  - [ ] `workflows/README.md` 包含添加新工作流的步骤说明
  - [ ] README.md 反映新架构

  **QA Scenarios**:
  ```
  Scenario: 打包脚本语法验证
    Tool: Bash
    Preconditions: 执行打包.bat 已更新
    Steps:
      1. python -c "
# 验证 .bat 中引用了所有必要的文件
with open('执行打包.bat', 'r', encoding='utf-8') as f:
    content = f.read()
checks = ['workflow_engine.py', 'workflow_manager.py', 'handlers', 'workflows']
for c in checks:
    assert c in content, f'Missing: {c}'
print('All references found')
"
    Expected Result: 所有必要文件被引用
    Evidence: .sisyphus/evidence/task-15-batch-check.txt

  Scenario: 新工作流添加文档验证
    Tool: Bash
    Preconditions: workflows/README.md 已创建
    Steps:
      1. Test-Path -LiteralPath "workflows/README.md"
      2. Select-String -Pattern "步骤" -Path "workflows/README.md" -Quiet
    Expected Result: 文件存在且包含添加步骤说明
    Evidence: .sisyphus/evidence/task-15-doc-exists.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-15-batch-check.txt`
  - [ ] `.sisyphus/evidence/task-15-doc-exists.txt`

  **Commit**: YES
  - Message: `chore: update packaging scripts and add workflow documentation`
  - Files: `执行打包.bat`, `form_filler.spec`, `README.md`, `workflows/README.md`

---

## Commit Strategy

- **T0**: `test(csms): add regression baseline script`
- **T1**: `refactor(project): restructure project with workflows/ and handlers/ dirs`
- **T2**: `feat(schema): add workflow JSON schema and validator`
- **T3**: `feat(engine): add WorkflowManager for workflow discovery and switching`
- **T4**: `feat(engine): add BaseHandler and HandlerRegistry`
- **T5**: `feat(handlers): add InputHandler, SelectHandler and CheckboxHandler`
- **T6**: `feat(handlers): add AutoCompleteHandler for iValua SelectorControl`
- **T7**: `feat(handlers): add DatePickerHandler with configurable modes`
- **T8**: `feat(handlers): add PopupSearchHandler`
- **T9**: `feat(handlers): add FileUploadHandler`
- **T10**: `feat(engine): add WorkflowEngine with navigation and retry logic`
- **T11**: `feat(gui): add workflow selector and dynamic field loading`
- **T12**: `feat(workflow): add CSMS Create Proposal workflow configuration`
- **T13**: `feat(workflow): add GR-Acubuy Create GR workflow configuration`
- **T14**: `fix: integration fixes and edge case handling`
- **T15**: `chore: update packaging scripts and documentation`

---

## Final Verification Wave

> 4 个审查 Agent 并行运行。全部通过后方可认为计划完成。向用户展示汇总结果并等待明确确认。

- [x] F1. **Plan Compliance Audit** — `oracle`
  - 对照计划逐一验证每个 Must Have 是否实现
  - 搜索代码库确认 Must NOT Have 不存在
  - 检查 `.sisyphus/evidence/` 中所有证据文件
  - 输出: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  - 检查代码质量：异常处理、硬编码、重复代码、类型提示
  - 验证 handler 接口一致性
  - 输出: `Quality [PASS/FAIL] | Issues [N] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ playwright)
  - 从零开始执行每个 Task 的 QA 场景
  - 测试跨 Task 集成（工作流切换、CSMS 回归、Acubuy 流程）
  - 测试边界情况：无效配置、网络错误、字段缺失
  - 证据保存到 `.sisyphus/evidence/final-qa/`
  - 输出: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  - 逐 Task 对比"what to do"与实际代码差异
  - 检查是否有超范围实现或遗漏功能
  - 检测跨 Task 污染
  - 输出: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

## Success Criteria

### 最终检查清单
- [ ] GUI 工作流下拉菜单可切换 CSMS / GR-Acubuy
- [ ] CSMS 回归验证脚本全部通过
- [ ] GR-Acubuy 新建收货单流程可完成
- [ ] 错误重试机制正常工作
- [ ] 添加新工作流文件夹无需改代码
- [ ] 打包 EXE 运行正常
