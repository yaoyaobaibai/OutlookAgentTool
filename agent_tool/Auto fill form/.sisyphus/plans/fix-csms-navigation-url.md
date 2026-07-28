# 修复 CSMS 登录后不跳转至 Create PG 页面

## TL;DR

> **快速总结**: `form_filler.py` 第 715-718 行在注入登录 URL 时错误地覆盖了导航步骤的跳转 URL，导致登录后无法跳转到 Create Proposal Group 页面。修复方法：删除导航 URL 覆盖代码。
>
> **交付物**:
> - `form_filler.py` — 修复 URL 覆盖 bug (删除 4 行代码)
>
> **预估工作量**: 小型 (5分钟)
> **并行执行**: 否 (线性流程)

---

## Context

### 原始请求
CSMS 流程在执行时，登录成功后没有自动跳转到 Create Proposal Group 页面，停留在登录页面或跳转到了错误的 URL。

### 根本原因分析

**问题位置**: `form_filler.py` 第 710-718 行，`_run_engine_thread` 方法

**Bug 复现路径**:
1. GUI 选择 CSMS 工作流后，`target_url` 被设置为登录 URL (`https://csmstest.ncs.com.sg/UAT/`)
2. 用户点击执行，代码进入 URL 注入逻辑
3. 第 714 行正确地将 `config["login"]["url"]` 设为登录 URL
4. **第 715-718 行 BUG**: 遍历 `config["navigation"]` 中的所有 `goto` 步骤，**也把它们的 URL 改成了登录 URL**
5. 导航步骤本应跳转到 `.../details_pg.aspx`（Create PG 页面），结果跳转回了登录页面
6. 后续 `wait_selector` 等待 `#ctl00_ContentPlaceHolder1_txtProposalNo` 自然超时

**工作流配置** (`workflows/csms_create_proposal/workflow.json`):
```json
"navigation": [
  { "action": "goto", "url": "https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx", ... },
  { "action": "wait_selector", "selector": "#ctl00_ContentPlaceHolder1_txtProposalNo", ... }
]
```

### 范围边界
- **包含**: 修复 URL 覆盖 bug（仅改代码，不打包）
- **不包含**: 登录成功验证增强、菜单导航替代方案、重新打包、其他工作流的修改

---

## Work Objectives

### 核心目标
修复 CSMS 工作流登录后无法跳转到 Create PG 页面的问题。

### 具体交付物
- `form_filler.py` — 移除了错误的导航 URL 覆盖代码

### 完成标准
- [ ] `form_filler.py` 中不再有 `navigation` 遍历覆盖 URL 的代码
- [ ] CSMS 工作流的 `target_url` 只更新 `login.url`，不再修改 `navigation` 中的 URL
- [ ] 代码语法正确，可正常导入

---

## Verification Strategy

### QA 策略
通过代码审查 + Python 语法检查验证修复正确性。

---

## Execution Strategy

单一波次，线性执行:

```
Wave 1:
└── Task 1: 修复 form_filler.py — 删除导航URL覆盖代码
```

---

## TODOs

- [x] 1. 修复 `form_filler.py` URL 注入逻辑

  **做什么**:
  - 定位到 `form_filler.py` 第 710-718 行的 `_run_engine_thread` 方法
  - **删除** 第 715-718 行的 `navigation` URL 覆盖代码块:
    ```python
    # 删除以下4行：
    if "navigation" in config and config["navigation"]:
        for step in config["navigation"]:
            if step.get("action") == "goto":
                step["url"] = url
    ```
  - 保留第 710-714 行的 login URL 注入:
    ```python
    url = self.target_url.get().strip()
    if url:
        if "login" in config and config["login"]:
            config["login"]["url"] = url
    ```

  **验证**:
  - [x] 代码审查: 确认 `form_filler.py` 中不再有 `step["url"] = url` 的代码
  - [x] 语法检查: `python -c "import py_compile; py_compile.compile('form_filler.py', doraise=True)"` 通过
  - [x] 逻辑验证: 确认 `login.url` 仍可被覆盖，`navigation` 中的 URL 保持工作流配置的原始值

  **提交**: 否

---

## 最终验证波次

- [x] F1. **代码修复验证**

  - [x] 确认 `form_filler.py` 中无 `step["url"] = url` 代码
  - [x] 确认 `config["login"]["url"]` 仍可被 GUI URL 覆盖
  - [x] 确认 `navigation` 中的 `goto` URL 保留工作流配置值

---

## Commit Strategy

- 无需提交

---

## Success Criteria

### 验证命令
```powershell
# 代码检查 — 应无匹配
Select-String -Path "form_filler.py" -Pattern 'step\["url"\] = url' -SimpleMatch

# 语法检查
python -c "import py_compile; py_compile.compile('form_filler.py', doraise=True)"
```

### 最终检查清单
- [x] `form_filler.py` 导航 URL 覆盖代码已移除
- [x] `form_filler.py` 语法检查通过
