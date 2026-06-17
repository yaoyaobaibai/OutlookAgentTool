# OutlookAgent 核心技能文档

> 加载: `skill(name="SKILL")` 或读取 `.sisyphus/skills/SKILL.md`
> 完整版本（否决方案、错误速查表、经验教训）: `.sisyphus/skills/SKILL-extended.md`

---

## 一、项目核心约束（必须遵守）

### 1. subprocess 必须隐藏窗口 [P0]
```python
# ✅ 正确
subprocess.run([...], capture_output=True, creationflags=0x08000000)
subprocess.Popen([...], creationflags=0x08000000)

# ❌ 错误（会弹黑框）
subprocess.run([...], capture_output=True)
```
**原因**: PyInstaller `--windowed` 只影响 EXE 自身，不影响子进程。

### 2. CSS 处理顺序：先清后注 [P0]
```python
# ✅ 正确：先清后注
html_body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)  # 1.清
page_css = f'<style>@page {{ size: {w:.1f}mm {h:.1f}mm; margin: 15mm; }}</style>'       # 2.注

# ❌ 错误：先注后清 → 刚注入的样式被自己删掉 → 正文纯文本
```
**原因**: xhtml2pdf 的 CSS 解析器无法处理现代邮件 CSS，会导致卡死或空 PDF。

### 3. attachment_handler.py 和 msg_to_pdf.py 必须同步 [P0]
两个文件各有一份 `_html_body_to_pdf`，**修改一处必须同步另一处**：
- CSS 处理逻辑（清除 + 注入顺序）
- @page CSS 格式（mm 单位 + margin）
- 超时保护机制
- 图片压缩逻辑（`_compress_image_if_needed`）
- CID 替换前验证
- 附件格式兼容（字典 vs 对象）
- `<a>` 标签替换 + CSS underline 移除

### 4. @page CSS 用 mm 不用 pt [P1]
```python
width_mm = page_size[0] * 0.3528   # pt → mm, 1pt = 0.3528mm
height_mm = page_size[1] * 0.3528
```
**原因**: xhtml2pdf 对 pt 支持不全，A3 会死循环。

### 5. Word COM 后强制杀僵尸进程 [P1]
```python
pythoncom.CoUninitialize()
subprocess.run(["taskkill", "/f", "/im", "WINWORD.EXE"], 
               creationflags=0x08000000)
```
**原因**: Word COM 的 `Quit()` 可能静默失败，残留 WINWORD.EXE 导致下次卡死。

### 6. 诊断日志必须在 `_logging.disable()` 之前 [P1]
```python
logger.info("PATH: _html_body_to_pdf starting render...")  # ✅ 在 disable 之前
_logging.disable(_logging.CRITICAL)  # 禁用日志
```
**原因**: `_logging.disable(_logging.CRITICAL)` 会静默所有 logger 调用。

### 7. Logo 过滤必须双重检查 [P2]
```python
# Skip inline images (hidden=True)
if getattr(attachment, "hidden", False):
    continue
# Skip image attachments with contentId (logos/signatures)
cid = getattr(attachment, "contentId", None)
if cid:
    fn_lower = (attachment.longFilename or attachment.shortFilename or "").lower()
    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
        continue
```
**原因**: `extract_msg` 的 `hidden` 属性不可靠，部分 logo `hidden=False` 但仍有 `contentId`。

### 8. 所有日志必须纯英文 ASCII [P1]
**原因**: `--windowed` EXE 无 stderr，中文日志在查看器显示为 `??`。

### 9. Excel COM 必须设置 ActivePrinter [P1]
```python
excel.ActivePrinter = "Microsoft Print to PDF"
workbook.ExportAsFixedFormat(0, output_path)
excel.ActivePrinter = original_printer  # 恢复
```
**原因**: `ExportAsFixedFormat` 依赖默认打印机的纸张支持，不支持 A3 时静默降级到 A4。

---

## 二、Agent 行为规则

### 规则1：提出新方案前先检查否决列表 [P0]
**行为**: 在提出任何新方案之前，必须先检查否决方案。
**执行**: 先 `Read .sisyphus/skills/SKILL-extended.md` 的"已被彻底否决的方案"章节，确认方案不在列表中再提出。

### 规则2：排查错误前先查速查表 [P0]
**行为**: 遇到报错时，先查错误速查表。
**执行**: 先 `Read .sisyphus/skills/SKILL-extended.md` 的"常见错误与修复速查表"章节，表中有对应条目则直接用已知修复方案。

### 规则3：每次给出代码后附带验证命令 [P0]
**行为**: 每次提供代码修改后，必须附带验证命令（`python -m py_compile` + 回读确认）。

### 规则4：一次只修一个问题 [P1]
**行为**: 每次只修复一个问题，验证通过后再修下一个。
**原因**: 一次性修复太多容易引入新的 bug。

### 规则5：改 attachment_handler.py 必须同步 msg_to_pdf.py [P1]
**行为**: 修改 `attachment_handler.py` 的 `_html_body_to_pdf` 后，必须同步修改 `msg_to_pdf.py` 的对应函数。
**执行**: 两个文件都运行 `py_compile` 验证。

### 规则6：部署前必须验证 EXE 包含修改 [P1]
**行为**: PyInstaller 构建后，验证 EXE 大小合理（PDFMergeTool ~41MB, OutlookAgent ~38MB），必要时清除缓存重建。

### 规则7：中文字符串替换必须用 Python 脚本 [P0]
**行为**: 禁止用 PowerShell `-replace` 做中文替换（编码不匹配会静默失败）。
**替代**: 用 Python `pathlib.read_text` + `str.replace` + `write_text`。

### 规则8：测试数据不能上 GitHub [P1]
**行为**: `agent_tool/测试/` 含保密数据，已在 .gitignore 中排除。

---

## 附录：完整文档索引

| 内容 | 位置 |
|------|------|
| 否决方案（24 条） | SKILL-extended.md §二 |
| 错误速查表（33 行） | SKILL-extended.md §三 |
| Agent 行为规则（完整 10 条） | SKILL-extended.md §四 |
| 经验教训（按版本） | SKILL-extended.md §五 |
| 项目结构 / 构建 / 验证清单 / 日志位置 | SKILL-extended.md 附录 |

---

*精简版 — 完整版本见 `.sisyphus/skills/SKILL-extended.md`*