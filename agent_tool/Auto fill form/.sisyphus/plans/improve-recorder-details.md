# Recorder 改进计划 — 详细操作捕获

## TL;DR

> **快速总结**: 增强 recorder.py 的 JS 注入层，捕获自定义下拉框、弹窗交互、隐藏 input 变化等细节操作，使日志能精确反映用户在页面上的每一步操作。
>
> **交付物**: `recorder.py` — 增强版 (JS 注入层重写)
>
> **预估工作量**: 中等 (1-2小时)

---

## 问题分析

### 用户反馈
"点击按钮出现弹窗并在其中选择了一些东西，程序并没有记录下来"

### 根因
现有 JS 注入代码有 3 个关键缺陷：

1. **未追踪隐藏 input 变化**: 自定义下拉框选择后，值写入隐藏 `<input>`，`input/change` 事件不会因程序化赋值而触发
2. **MutationObserver 不完整**: 只监听 `childList`，不监听 `attributes`，看不到弹窗的 class 变化（如 `.modal.active`）
3. **CSS 类名正则被 Python 转义破坏**: `split(/\\\\s+/)` 实际产生的 JS 正则不匹配空白字符

---

## 改进内容

### 1. 修复 CSS 类名正则 (关键)
`getSelector()` 中的 `split(/\\\\s+/)` → `split(/\\s+/)`，让 class 分割正常工作。

### 2. 增强 MutationObserver
- 添加 `attributes: true, attributeFilter: ['class', 'style', 'value']`
- 检测弹窗出现（class 添加 `active/visible/show` 等）
- 检测弹窗关闭（class 移除或 `display:none`）
- 检测隐藏 input 的 `value` 属性变化

### 3. 追踪隐藏 input 变化
在 MutationObserver 中添加对 `input[type=hidden]` 的 `value` 属性变化监听：
- 记录 `hidden_input_change` 事件
- 包含选择器、旧值、新值
- 关联最近的点击事件（确定是什么操作触发的）

### 4. 增强点击事件的上下文
在 `click` 事件中，检查点击目标是否在弹窗/下拉框内：
- 如果父元素有 `.modal`, `.popup`, `.dropdown`, `.menu` 等类 → 标记为 `in_popup: true`
- 记录弹窗/下拉框容器的选择器

### 5. 添加箭头键和 Space 键追踪
在 keydown 中添加 `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `Space`。

### 6. 添加 before/after 状态
在 `input` 事件中，先记录旧值，再记录新值。

---

## TODOs

- [x] 1. **修复 CSS 类名正则 bug** — `split(/\\\\s+/)` → `split(/\\s+/)`，移除 `ui-` 过滤

- [x] 2. **增强 MutationObserver** — 新增 attributes 监听；隐藏 input 值变化跟踪；弹窗打开/关闭检测

- [x] 3. **添加上下文追踪** — click 事件新增 in_popup / popup_selector / popup_type 字段

- [x] 4. **扩展键盘事件** — 新增 ArrowUp/Down/Left/Right/Space

- [x] 5. **添加 before/after 状态** — input 事件新增 old_value 字段

---

## 最终验证

- [x] 自定义下拉框选择 → 记录 `hidden_input_change`
- [x] 弹窗打开/关闭 → 记录 `popup_opened` / `popup_closed`
- [x] 点击弹窗内元素 → 记录 `in_popup`, `popup_type`, `popup_selector`
- [x] 输入框变化 → 记录 `old_value` + `value`
- [x] 箭头键导航 → 记录 keydown 事件
- [x] CSS 类名正则修复 → 选择器包含有用 class
- [x] **JS 注入方式修复**: `expose_function` → `Runtime.addBinding` + `addScriptToEvaluateOnNewDocument`
- [x] **type 覆盖 bug 修复**: `_on_request` 中 `type=` → `resource_type=`
