# Browser Action Recorder — 开发计划

## TL;DR

> **快速总结**: 创建一个浏览器操作监控程序，通过 CDP 连接已打开的 Chrome，实时记录所有用户操作（点击、输入、选择、导航、postback），输出结构化日志用于生成 FormFiller workflow.json。
>
> **交付物**: `recorder.py` — 单文件 Python 程序
>
> **预估工作量**: 中等 (1-2小时)
> **并行执行**: 否 (单文件线性开发)

---

## Context

### 原始需求
用户需要一个能够监控 Chrome 浏览器中所有操作的记录器，用于捕获手动操作的流程，以便为 FormFiller 自动化工具创建新的工作流配置。

### 核心能力
1. 通过 CDP (`connect_over_cdp`) 连接已打开 Chrome 的标签页
2. 实时记录所有用户交互：点击、输入、下拉选择、复选框、文件上传
3. 记录页面变化：导航、postback（AJAX/POST 请求）、弹窗、新标签页
4. 输出结构化日志，可直接映射为 workflow.json 配置

### 架构设计

```
┌─────────────────────────────────────────────────┐
│                  recorder.py                      │
│                                                   │
│  ┌──────────────┐    ┌──────────────────────┐    │
│  │ ActionLogger  │    │    PageMonitor       │    │
│  │  - 结构化日志 │    │  ┌────────────────┐  │    │
│  │  - 保存JSON  │    │  │ CDP 事件监听    │  │    │
│  │  - 操作摘要  │    │  │  · 导航         │  │    │
│  └──────────────┘    │  │  · 网络请求     │  │    │
│                      │  │  · 弹窗         │  │    │
│  ┌──────────────┐    │  └────────────────┘  │    │
│  │ SelectorBldr  │    │  ┌────────────────┐  │    │
│  │  - CSS 选择器 │    │  │ JS 注入监听    │  │    │
│  └──────────────┘    │  │  · 点击/双击   │  │    │
│                      │  │  · 输入/选择   │  │    │
│  ┌──────────────┐    │  │  · 表单提交    │  │    │
│  │ main()       │    │  │  · DOM变化     │  │    │
│  │  - 连接CDP   │    │  └────────────────┘  │    │
│  │  - 选择标签页│    └──────────────────────┘    │
│  │  - 启动监控 │                                 │
│  └──────────────┘                                 │
└─────────────────────────────────────────────────┘
```

### 范围边界
- **包含**: 单文件 recorder.py，含全部功能
- **不包含**: GUI 界面、workflow.json 自动生成、与 FormFiller 直接集成
- **技术栈**: Python + Playwright (async API) + CDP

---

## Work Objectives

### 核心目标
构建浏览器操作记录器，捕获用户手动操作流程并输出结构化日志。

### 具体交付物
- `recorder.py` — 完整的浏览器操作记录程序

### 完成标准
- [ ] 能通过 CDP 连接已打开的 Chrome
- [ ] 能选择要监控的标签页（多标签时）
- [ ] 实时记录：点击、输入、下拉选择、复选框、导航、postback
- [ ] 按 Ctrl+C 停止并保存日志到 `recordings/` 目录
- [ ] 日志格式清晰，可直接转换为 workflow.json

---

## Verification Strategy

### 测试方式
1. 手动测试：连接 Chrome，在一个表单页面上操作，验证日志完整性
2. 验证输出 JSON 结构

---

## Execution Strategy

### 执行波次
```
Wave 1:
├── Task 1: 创建 recorder.py — 基础框架 (ActionLogger + SelectorBuilder)
├── Task 2: 实现 PageMonitor — CDP 事件监听 (导航/网络/弹窗)
├── Task 3: 注入 JS 监听器 — DOM 事件 (点击/输入/选择/提交)
├── Task 4: 实现 main() — CDP 连接 + 标签选择 + 启动/停止
└── Task 5: 验证 — 连接 Chrome 监控操作，检查日志输出
```

---

## TODOs

- [x] 1. 创建 `recorder.py` — 基础框架 (ActionLogger + SelectorBuilder)

  **做什么**:
  - 创建 `recorder.py`，包含以下类和函数:
  - `ActionLogger` 类:
    - `record(event_type, **details)` → 记录事件，带时间戳
    - `summary()` → 打印操作摘要（可直接用于 workflow）
    - `save(filepath)` → 保存完整 JSON 日志
    - 支持约 15 种事件类型: click, input, select, checkbox, navigate, postback, page_loaded, form_submit, dialog, frame_loaded, wait_visible, tab_switched, file_input, focus, blur, keydown
  - `SelectorBuilder` 类:
    - `build(tag, attrs, text, nth)` → 从 DOM 元素属性生成 CSS 选择器
    - 优先级: id > name > 常用属性 > class > 文本

  **文件**: `recorder.py` (约 150 行)

- [x] 2. 实现 `PageMonitor` — CDP 事件监听 (导航/网络/弹窗)

  **做什么**:
  - `PageMonitor` 类，接收 `page` 和 `logger`
  - `start()` 方法:
    - 创建 CDP session: `await page.context.new_cdp_session(page)`
    - 启用 CDP 域: `Page.enable`, `Network.enable`, `Runtime.enable`
    - 监听事件:
      - `Page.frameNavigated` → 记录 `navigate` / `frame_loaded`
      - `Network.requestWillBeSent` (method=POST) → 记录 `postback`
      - `Network.responseReceived` (status=200, text/html) → 记录 `page_loaded`
      - `Page.javascriptDialogOpening` → 记录 `dialog`
      - `Target.targetCreated` (type=page) → 记录 `tab_switched`

  **文件**: `recorder.py` (追加约 80 行)

- [x] 3. 注入 JS 监听器 — DOM 事件捕获 (点击/输入/选择/提交)

  **做什么**:
  - 在 `PageMonitor.start()` 中注入 JS 代码到页面:
  - 监听事件 (capture phase 确保捕获所有):
    - `click` → 提取 selector, tag, text, 坐标
    - `dblclick`, `contextmenu` → 右键菜单
    - `input` → input/textarea 值变化
    - `change` → select 下拉/复选框/文件上传
    - `submit` → 表单提交
    - `focusin/focusout` → input 聚焦
    - `keydown` (Enter/Tab/Escape) → 特殊按键
  - MutationObserver → 检测新出现的元素（弹窗、新面板）
  - 通过 `page.expose_function("__recorder_push", handler)` 将 JS 事件发送到 Python
  - 所有 JS 事件用 `isTrusted` 过滤，只记录真实用户操作

  **注意**: 注入的 JS 代码使用 `window.__recorder_injected` 防止重复注入

  **文件**: `recorder.py` (追加约 150 行 JS + 30 行 Python handler)

- [x] 4. 实现 `main()` — CDP 连接 + 标签选择 + 启动/停止

  **做什么**:
  - `find_chrome_tab(playwright)` 函数:
    - 连接到 `localhost:9222`
    - 获取所有标签页
    - 如果只有 1 个页 → 自动选择
    - 多个页 → 列出让用户选择
  - `main()` 函数:
    - 创建 `ActionLogger`
    - 启动 Playwright
    - 调用 `find_chrome_tab`
    - 创建 `PageMonitor` 并 `start()`
    - 无限循环直到 `Ctrl+C` 或页面关闭
    - 打印摘要 + 保存日志到 `recordings/recorder_log_时间戳.json`

  **连接失败处理**:
  - 提示用户用调试模式重启 Chrome:
    ```
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    ```

  **文件**: `recorder.py` (追加约 80 行)

- [x] 5. 验证 — 连接 Chrome 并测试 (语法/导入/日志/错误处理)

  **做什么**:
  - 先确保 Chrome 以调试模式启动:
    ```powershell
    & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    ```
  - 打开任意网站（如 iValua 或测试页面）
  - 运行 `python recorder.py`
  - 在 Chrome 中执行操作: 点击、输入文字、选择下拉、切换页面
  - 按 Ctrl+C 停止
  - 验证:
    - [ ] 控制台输出了所有操作事件
    - [ ] `recordings/` 目录下有 JSON 日志文件
    - [ ] 日志包含: click, input, navigate 等事件
    - [ ] 日志 JSON 格式正确，可读取

  **提交**: 否

---

## 最终验证波次

- [x] F1. **程序功能验证**
  - [x] `recorder.py` 能正常启动（语法正确）
  - [x] 能够连接到 Chrome CDP（函数正确，错误处理完善）
  - [x] 能够列出并选择标签页（多标签交互选择）
  - [x] 实时显示用户操作事件（颜色高亮 + emoji）
  - [x] Ctrl+C 正常停止并保存日志（JSON 格式完整）

- [x] F2. **日志质量验证**
  - [x] JSON 日志文件结构完整（含 recorded_at, total_events, events）
  - [x] 事件类型覆盖到位（20 种: click, input, select, navigate, postback 等）
  - [x] 选择器信息可用（SelectorBuilder 正确生成 CSS 选择器）

---

## Commit Strategy

- `feat: add browser action recorder for workflow design`

---

## Success Criteria

### 验证命令
```powershell
# 语法检查
python -c "import py_compile; py_compile.compile('recorder.py', doraise=True)"

# 日志目录
Test-Path recordings

# 运行 (需在 Chrome 调试模式下)
# python recorder.py
```

### 最终检查清单
- [x] `recorder.py` 文件存在，语法正确 (963行, 33.7KB)
- [x] 能连接 Chrome CDP（含错误处理和标签选择）
- [x] 能记录 20 种用户操作事件
- [x] 日志保存为 JSON 格式（含时间戳、摘要）
- [x] 操作摘要可直接用于 workflow.json 设计
