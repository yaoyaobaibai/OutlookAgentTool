# OutlookAgent 核心技能文档

> 加载: `skill(name="SKILL")` 或读取 `.sisyphus/skills/SKILL.md`
> 完整版本: `.sisyphus/skills/SKILL-extended.md`

---

## 一、项目核心约束（P0-必须遵守）

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

---

## 二、常见否决方案（不要再提）

### ❌ 方案1：通过参数传递 default_page_size [P0]
**否决原因**: 导致 `name 'default_page_size' is not defined` 运行时错误。参数链路跨 `main.py → gui.py` 两个模块，PyInstaller 打包后可能出现字节码不一致。
**替代方案**: 直接硬编码 `value="A3"`，简单可靠。

### ❌ 方案2：用 `signal.alarm` 做超时 [P0]
**否决原因**: Windows 不支持 `SIGALRM`。
**替代方案**: `threading.Thread` + `join(timeout)`。

### ❌ 方案3：模块级 import reportlab [P0]
**否决原因**: 该文件在非 Windows 环境 import 会失败（缺少 pywin32）。
**替代方案**: 函数内部 import。

### ❌ 方案4：中文字符串直接做代码替换 [P0]
**否决原因**: PowerShell 传递中编码不匹配 → 静默失败 → 代码实际未修改。
**替代方案**: 用行号定位 + 精确行替换，改完立即 `py_compile` + `read` 回读验证。

### ❌ 方案5：用 `extract_msg` 的 `rtfBody` 自己解析 RTF [P1]
**否决原因**: RTF 格式复杂，简单正则剥离控制码会把大部分内容删掉（len=110，实际应有数千字符）。
**替代方案**: 保持 extract_msg 的 htmlBody 优先，失败时降级到纯文本 fallback。

### ❌ 方案6：PyInstaller `--hidden-import=attachment_handler` [P1]
**否决原因**: `main.py` 用 `sys.path.insert()` 动态导入，PyInstaller 静态分析追踪不到修改后的字节码。
**替代方案**: 删除 `%APPDATA%\pyinstaller` 全局缓存后重建。

### ❌ 方案7：一次修复所有问题 [P1]
**否决原因**: 用户反馈"一次性修复太多容易出新的 bugs"。
**替代方案**: 逐个修复，每个修复后验证再继续。

### ❌ 方案14：直接用 extract_msg 读取所有 .msg 文件 [P1]
**否决原因**: extract_msg 库遇到 RTF 编码中的 byte 0x90 时会崩溃。
**替代方案**: Outlook COM 优先 + extract_msg 回退（双保险）。

### ❌ 方案15：删除所有 <style> 块再渲染 [P2]
**否决原因**: 某些 Outlook 邮件的 <style> 块占 HTML 的 93%，删除后几乎无内容。
**替代方案**: 两阶段渲染 — 先带样式尝试，失败后清理重试。

---

## 三、常见错误与修复速查表

| 错误签名 | 根因 | 修复命令 | 对应脚本 | 优先级 |
|----------|------|----------|----------|--------|
| `.msg` 正文只有纯文本 | CSS 处理顺序反了（先注后清） | 改为先清后注，确保 mm 单位 | 手动修复 | P0 |
| 合并卡死 / 切换纸张卡死 | WINWORD.EXE 僵尸进程 | `python scripts/fix_word_zombie.py` | `fix_word_zombie.py` | P0 |
| `name 'default_page_size' is not defined` | 参数传递在 PyInstaller 后失效 | 硬编码 `value="A3"` | 手动修复 | P0 |
| PowerShell 中文替换静默失败 | 编码不匹配 | 用 Python 脚本替代 PowerShell | 手动修复 | P0 |
| EXE 大小异常（小于 30MB） | PyInstaller 打包不完整 | `python scripts/check_exe_size.py <exe>` | `check_exe_size.py` | P1 |
| Excel A3 纸张大小不生效 | 未设置 ActivePrinter | 导出前设 `ActivePrinter = "Microsoft Print to PDF"` | 手动修复 | P1 |
| `PATH: _html_body_to_pdf` 日志不出现 | 诊断日志在 `_logging.disable()` 之后 | `python scripts/check_logging_order.py <file>` | `check_logging_order.py` | P1 |
| PyInstaller 不捡 attachment_handler.py | 动态路径导入导致 | `python scripts/clean_pyinstaller_cache.py` | `clean_pyinstaller_cache.py` | P1 |
| page_size 传递链断裂 | 附件转换调用没传 page_size | `python scripts/check_page_size_calls.py <file>` | `check_page_size_calls.py` | P1 |
| 子代理只分析不执行 | 默认分析模式 | 写 "EXECUTE all steps. Do NOT analyze" | 手动修复 | P1 |
| Outlook COM OpenSharedItem 失败 | 路径含 URL 编码或正斜杠 | `urllib.parse.unquote(msg_path).replace('/', '\\')` | 手动修复 | P0 |
| CJK 字体注册被静默 | 日志在 _logging.disable() 之后 | 移到 _logging.disable() 之前 | 手动修复 | P0 |
| xhtml2pdf 渲染 MSO 邮件失败 | MSO 条件注释不兼容 | 两阶段渲染（先试后清） | 手动修复 | P2 |

---

## 四、Agent 行为规则（关键规则）

### 规则1：提出新方案前先检查否决列表 [P0]
**行为**: 在提出任何新方案之前，必须先检查本文档的"常见否决方案"章节。
**原因**: 避免重复尝试已知失败的方案，浪费时间和资源。
**执行**: 
```
1. 提出方案前，先搜索否决列表
2. 如果方案在否决列表中，直接告知用户并解释原因
3. 如果不在否决列表中，继续评估
```

### 规则2：每次给出代码后附带验证命令 [P0]
**行为**: 每次提供代码修改后，必须附带验证命令。
**原因**: 确保修改生效，避免"改了等于没改"的情况。
**执行**:
```python
# 修改代码后，立即运行：
python -m py_compile <修改的文件>

# 如果是关键修改，还需要：
# 1. 读取修改后的文件，确认内容正确
# 2. 检查文件大小是否合理
# 3. 如果涉及 PyInstaller，需要重新构建并验证 EXE
```

### 规则3：一次只修一个问题 [P1]
**行为**: 每次只修复一个问题，验证通过后再修下一个。
**原因**: 一次性修复太多容易引入新的 bug，难以定位问题。
**执行**:
```
1. 选择一个问题
2. 分析根因
3. 实施修复
4. 验证修复
5. 如果通过，继续下一个问题
6. 如果失败，分析原因并重试
```

### 规则4：改 attachment_handler.py 必须同步 msg_to_pdf.py [P1]
**行为**: 修改 `attachment_handler.py` 的 `_html_body_to_pdf` 后，必须同步修改 `msg_to_pdf.py` 的对应函数。
**原因**: 两个文件各有一份独立实现，不同步会导致行为不一致。
**执行**:
```
1. 修改 attachment_handler.py
2. 搜索 msg_to_pdf.py 中的对应代码
3. 应用相同的修改
4. 两个文件都运行 py_compile 验证
```

### 规则5：部署前必须验证 EXE 包含修改 [P1]
**行为**: PyInstaller 构建后，必须验证 EXE 包含最新的代码修改。
**原因**: PyInstaller 可能使用缓存的旧版字节码，导致修改不生效。
**执行**:
```
1. 构建 EXE
2. 用字符串搜索验证关键代码在 EXE 中存在
3. 检查 EXE 大小是否合理（PDFMergeTool ~41MB, OutlookAgent ~38MB）
4. 如果验证失败，清除缓存并重新构建
```

---

## 附录：项目结构速查

```
agent_tool\
├── pdf_merge_tool\              # PDFMergeTool GUI
│   ├── main.py                  # 主程序（纸张选择、合并调度）
│   ├── build.bat                # pyinstaller 构建
│   └── converters\
│       ├── word_to_pdf.py       # Word→PDF（COM→docx2pdf→LibreOffice→python-docx）
│       ├── msg_to_pdf.py        # .msg→PDF（含 _html_body_to_pdf）
│       └── ...
├── outlook_agent\               # OutlookAgent 监控
│   ├── main.py                  # 主逻辑（手动 .msg 上传 + 邮件监控）
│   ├── gui.py                   # 确认弹窗 GUI
│   ├── attachment_handler.py    # 附件提取 + _html_body_to_pdf（独立副本！需同步）
│   ├── merge_launcher.py        # 子进程调用 PDFMergeTool.exe
│   └── build.bat
└── release_package\
    └── OutlookAgent_v1.2.5\     # 发布目录（版本号需根据当前发布版本调整）
        ├── PDFMergeTool.exe
        ├── OutlookAgent.exe
        └── README.txt
```

---

## 附录：构建与发布

```powershell
# PDFMergeTool
Remove-Item -Force -Recurse agent_tool\pdf_merge_tool\dist,build,*.spec -ErrorAction SilentlyContinue
cmd /c "cd agent_tool\pdf_merge_tool && build.bat"

# OutlookAgent
Remove-Item -Force -Recurse agent_tool\outlook_agent\dist,build,*.spec -ErrorAction SilentlyContinue
cmd /c "cd agent_tool\outlook_agent && build.bat"

# 发布到 agent_tool\release_package（用户习惯的路径）
# 注意：版本号需根据当前发布版本调整，例如 OutlookAgent_v1.2.5
Copy-Item agent_tool\pdf_merge_tool\dist\PDFMergeTool.exe agent_tool\release_package\OutlookAgent_v1.2.5\ -Force
Copy-Item agent_tool\outlook_agent\dist\OutlookAgent.exe agent_tool\release_package\OutlookAgent_v1.2.5\ -Force
```

⚠️ EXE 被占用时无法覆盖 — 任务管理器杀进程，或先重命名旧文件再复制。

---

## 附录：验证检查清单

- [ ] `python -m py_compile` 通过
- [ ] EXE 大小正常（PDFMergeTool ~41MB, OutlookAgent ~38MB）
- [ ] attachment_handler.py 的改动是否需要同步到 msg_to_pdf.py
- [ ] 所有 subprocess 都有 `creationflags=0x08000000`
- [ ] 发布到 `agent_tool\release_package\OutlookAgent_v1.2.5\`
- [ ] 更新 README.txt

---

## 附录：日志位置

> 注意：以下路径为示例，实际路径因用户环境而异。

- PDFMergeTool: `C:\Users\<用户名>\PDFMergeTool_logs\`
- OutlookAgent: `C:\Users\<用户名>\outlook_agent_logs\`

---

*整合时间：2026-05-31*
*整合自：outlookagent-dev.md、memory_1.md 到 memory_4.md*
*完整版本：`.sisyphus/skills/SKILL-extended.md`*