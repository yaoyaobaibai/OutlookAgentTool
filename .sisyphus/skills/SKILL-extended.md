# OutlookAgent 完整技能文档

> 加载: `skill(name="SKILL-extended")` 或读取 `.sisyphus/skills/SKILL-extended.md`
> 核心版本: `.sisyphus/skills/SKILL.md`（精简版，日常使用）

---

## 一、项目核心约束（必须遵守，不可讨论）

### 1. subprocess 必须隐藏窗口 [P0]
```python
# ✅ 正确
subprocess.run([...], capture_output=True, creationflags=0x08000000)
subprocess.Popen([...], creationflags=0x08000000)

# ❌ 错误（会弹黑框）
subprocess.run([...], capture_output=True)
```
**原因**: PyInstaller `--windowed` 只影响 EXE 自身，不影响子进程。

### 2. reportlab 导入必须在函数内部 [P1]
```python
# ✅ 正确
def _build_paragraph(para_element, styles):
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer

# ❌ 错误（非 Windows 环境会失败）
from reportlab.platypus import Paragraph  # 模块级导入
```
**原因**: 非 Windows 平台无 pywin32，模块级导入会导致 import 失败。

### 3. attachment_handler.py 和 msg_to_pdf.py 必须同步 [P0]
两个文件各有一份 `_html_body_to_pdf`，**修改一处必须同步另一处**：
- CSS 处理逻辑（清除 + 注入顺序）
- @page CSS 格式（mm 单位 + margin）
- 超时保护机制
- 图片压缩逻辑（`_compress_image_if_needed`）
- CID 替换前验证
- 附件格式兼容（字典 vs 对象）
- `<a>` 标签替换 + CSS underline 移除
- weasyprint DLL 配置（`WEASYPRINT_DLL_DIRECTORIES`）
- 行间距 CSS（`line-height` + `p margin`）

### 4. CSS 处理顺序：先清后注 [P0]
```python
# ✅ 正确：先清后注
html_body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)  # 1.清
page_css = f'<style>@page {{ size: {w:.1f}mm {h:.1f}mm; margin: 15mm; }}</style>'       # 2.注

# ❌ 错误：先注后清 → 刚注入的样式被自己删掉 → 正文纯文本
```
**原因**: 现代邮件 CSS 包含大量浏览器专用样式，会导致渲染引擎卡死或空 PDF。

### 5. @page CSS 用 mm 不用 pt [P1]
```python
width_mm = page_size[0] * 0.3528   # pt → mm, 1pt = 0.3528mm
height_mm = page_size[1] * 0.3528
```
**原因**: xhtml2pdf 对 pt 支持不全，A3 会死循环。weasyprint 原生支持 mm，效果更可靠。

### 6. Word COM 后强制杀僵尸进程 [P1]
```python
pythoncom.CoUninitialize()
subprocess.run(["taskkill", "/f", "/im", "WINWORD.EXE"], 
               creationflags=0x08000000)
```
**原因**: Word COM 的 `Quit()` 可能静默失败，残留 WINWORD.EXE 导致下次卡死。

### 7. 诊断日志必须在 `_logging.disable()` 之前 [P1]
```python
logger.info("PATH: _html_body_to_pdf starting render...")  # ✅ 在 disable 之前
_logging.disable(_logging.CRITICAL)  # 禁用日志
```
**原因**: `_logging.disable(_logging.CRITICAL)` 会静默所有 logger 调用。

### 8. 所有日志必须纯英文 ASCII [P1]
**原因**: `--windowed` EXE 无 stderr，中文日志在查看器显示为 `??`。

### 9. Logo 过滤必须双重检查 [P2]
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

### 10. Excel COM 必须设置 ActivePrinter [P1]
```python
# 设置 ActivePrinter
excel.ActivePrinter = "Microsoft Print to PDF"
# 导出 PDF
workbook.ExportAsFixedFormat(0, output_path)
# 恢复原始打印机
excel.ActivePrinter = original_printer
```
**原因**: `ExportAsFixedFormat` 依赖默认打印机的纸张支持，不支持 A3 时静默降级到 A4。

### 11. Excel COM 必须显式释放 [P0]
```python
finally:
    try: excel.Quit()
    except: pass
    try: del workbook
    except: pass
    try: del excel
    except: pass
finally:
    pythoncom.CoUninitialize()
    subprocess.run(['taskkill', '/f', '/im', 'EXCEL.EXE'],
                   capture_output=True, timeout=5, creationflags=0x08000000)
```
**原因**: Excel COM 对象未释放会导致文件句柄被占用，用户无法打开原始 Excel 文件。

### 12. weasyprint 需设置 WEASYPRINT_DLL_DIRECTORIES [P1]
```python
if sys.platform == 'win32':
    if hasattr(sys, '_MEIPASS'):
        os.environ['WEASYPRINT_DLL_DIRECTORIES'] = sys._MEIPASS
    else:
        _msys = r'C:\msys64\mingw64\bin'
        if os.path.exists(_msys):
            os.environ['WEASYPRINT_DLL_DIRECTORIES'] = _msys
```
**原因**: weasyprint 使用 cffi 动态加载 GTK3 DLL，PyInstaller 打包后需要告诉它 DLL 的位置。

### 13. 邮件头部信息使用 `<div>` 布局 [P2]
```python
# ✅ 正确：用 div 布局
header_html = '<div style="margin-bottom: 4px;"><b>From:</b> ...</div>'

# ❌ 错误：用 table 布局（weasyprint 表格渲染行间距过大）
header_html = '<tr><td><b>From:</b></td><td>...</td></tr>'
```
**原因**: weasyprint 对 `<table>` 的渲染与 xhtml2pdf 不同，行间距过大。

---

## 二、已被彻底否决的方案（不要再提）

### ❌ 方案1：通过参数传递 default_page_size [P0]
**否决原因**: 导致 `name 'default_page_size' is not defined` 运行时错误。参数链路跨 `main.py → gui.py` 两个模块，PyInstaller 打包后可能出现字节码不一致。
**替代方案**: 直接硬编码 `value="A3"`，简单可靠。

### ❌ 方案2：用 `signal.alarm` 做超时 [P0]
**否决原因**: Windows 不支持 `SIGALRM`。
**替代方案**: `threading.Thread` + `join(timeout)`。

### ❌ 方案3：模块级 import reportlab [P0]
**否决原因**: 该文件在非 Windows 环境 import 会失败（缺少 pywin32）。
**替代方案**: 函数内部 import。

### ❌ 方案4：只用 CID 字体 `STSong-Light` [P1]
**否决原因**: 在 PyInstaller 打包环境中 CID 字体数据可能不可用。
**替代方案**: 系统 TTF 优先，CID 降级。

### ❌ 方案5：模块级注册字体 [P1]
**否决原因**: `logging.basicConfig()` 在 `import converters` 之后执行，模块级代码的日志输出全部丢失。
**替代方案**: 懒加载初始化，放在 `_init_cjk_font()` 函数内。

### ❌ 方案6：CSS `font-family` 注入 `<body>` [P1]
**否决原因**: xhtml2pdf 的 `DEFAULT_CSS` 优先级更高，注入的样式被覆盖。
**替代方案**: 同时修改 `DEFAULT_CSS` 和 `DEFAULT_FONT`。

### ❌ 方案7：`page_combo.set("A3")` 设置默认值 [P2]
**否决原因**: 可能覆盖用户后续的 A4 选择。
**替代方案**: 用 `.current(0)` 设置默认选中项。

### ❌ 方案8：中文字符串直接做代码替换 [P0]
**否决原因**: PowerShell 传递中编码不匹配 → 静默失败 → 代码实际未修改。
**替代方案**: 用行号定位 + 精确行替换，改完立即 `py_compile` + `read` 回读验证。

### ❌ 方案9：用 `extract_msg` 的 `rtfBody` 自己解析 RTF [P1]
**否决原因**: RTF 格式复杂，简单正则剥离控制码会把大部分内容删掉（len=110，实际应有数千字符）。
**替代方案**: 保持 extract_msg 的 htmlBody 优先，失败时降级到纯文本 fallback。

### ❌ 方案10：PyInstaller `--hidden-import=attachment_handler` [P1]
**否决原因**: `main.py` 用 `sys.path.insert()` 动态导入，PyInstaller 静态分析追踪不到修改后的字节码。
**替代方案**: 删除 `%APPDATA%\pyinstaller` 全局缓存后重建。

### ❌ 方案11：修改 LibreOffice CLI 参数支持纸张大小 [P2]
**否决原因**: LibreOffice 的 `--convert-to pdf` 命令没有 `--paper-size` 参数。
**替代方案**: 接受限制，添加诊断日志说明。

### ❌ 方案12：用 Pillow 实现自定义纸张大小 [P2]
**否决原因**: Pillow fallback 固定 100×30px 像素渲染，无法适配纸张尺寸。
**替代方案**: 接受限制，添加诊断日志说明。

### ❌ 方案13：一次修复所有问题 [P1]
**否决原因**: 用户反馈"一次性修复太多容易出新的 bugs"。
**替代方案**: 逐个修复，每个修复后验证再继续。

### ❌ 方案14：在 OutlookAgent main.py 里单独写正文提取逻辑 [P1]
**否决原因**: 与 PDFMergeTool 的 `msg_to_pdf` 重复维护，且 OutlookAgent 调 PDFMergeTool 时本来就经过 msg_to_pdf。
**替代方案**: 复用 PDFMergeTool 的 `msg_to_pdf()` 函数。

### ❌ 方案15：`latin-1` fallback 画中文 [P1]
**否决原因**: reportlab `drawString` 仍会因字符无法编码而崩溃，`errors='replace'` 只能出 `?`。
**替代方案**: 系统 TTF 字体优先，CID 降级。

### ❌ 方案16：config 路径优先于同目录检测 [P1]
**否决原因**: 用户升级后旧 config 指向旧版本，所有修复不对新版本生效。
**替代方案**: 同目录 PDFMergeTool.exe 优先，config 作备胎。

### ❌ 方案17：无附件邮件直接报错拒绝 [P1]
**否决原因**: 用户需要正文单独输出为 PDF。
**替代方案**: 构造虚拟附件项 `{'name': '📧 邮件正文', 'is_virtual_body': True}`。

### ❌ 方案18：Word COM 渲染 HTML→PDF [P1]
**否决原因**: 本机 Word COM 返回 `RPC_E_SERVERCALL_REJECTED`，兼容性差；用户环境也可能无 Word。
**替代方案**: xhtml2pdf 优先 + 纯文本 fallback。

### ~~❌ 方案19~~ ✅ 已采纳：weasyprint 替代 xhtml2pdf [v1.2.7+]
**原否决原因**: pip 安装依赖重（需 cairo/pango 系统库），网络下载超时。
**现状**: v1.2.7 起已改用 weasyprint，解决了 xhtml2pdf 的 pt 单位死循环、CSS 支持差等问题。
**构建依赖**: 需安装 MSYS2 + pango（`winget install MSYS2.MSYS2`，然后 `pacman -S mingw-w64-x86_64-pango`）。

### ❌ 方案20：跳过大图片（>200KB） [P1]
**否决原因**: 用户截图丢失，内容缺失。
**替代方案**: 使用 PIL 压缩大图片后再嵌入。

### ❌ 方案21：单次渲染尝试 [P1]
**否决原因**: 渲染失败时无回退，格式丢失。
**替代方案**: 三层降级渲染（sanitized CSS → strip all `<style>` → plain text）。

### ❌ 方案22：不检查 CID 是否存在就替换 [P1]
**否决原因**: `str.replace()` 找不到子串时静默返回原字符串，图片不显示但无报错。
**替代方案**: 替换前先验证 `cid:xxx` 是否存在于 HTML 中。

### ❌ 方案23：COM 路径不读取附件 [P1]
**否决原因**: COM 路径只返回 HTML，不返回附件数据，内嵌图片无法显示。
**替代方案**: `_read_msg_html_via_outlook` 返回 `(html_body, attachments)` 元组。

### ❌ 方案24：CSS `!important` 修复下划线 [P2]
**否决原因**: xhtml2pdf 可能不支持 `!important`，导致 CSS 修复无效。
**替代方案**: 移除 `<a>` 标签替换为 `<span>` + 移除 CSS `text-decoration:underline`。

### ❌ 方案25：`<b>` 标签改成 `<span style="font-weight: bold">` [P2]
**否决原因**: 没有解决下划线问题，根因不明。
**替代方案**: 保持 `<b>` 标签，下划线问题在 weasyprint 迁移后自行解决。

### ❌ 方案26：HTML 备份始终生成 [P1]
**否决原因**: 会在生产环境生成不必要的临时文件。
**替代方案**: 通过环境变量 `PDFMERGE_DEBUG_HTML=1` 控制，默认关闭。

### ❌ 方案27：从 `output_pdf` 推导 `final_output_dir` [P1]
**否决原因**: `output_pdf` 是临时目录中的文件，推导出的目录是临时目录，不是最终输出目录。
**替代方案**: 通过参数传递 `final_output_dir`，调用方传入 `os.path.dirname(output_path)`。

### ❌ 方案28：使用 `<table>` 布局邮件头部 [P2]
**否决原因**: weasyprint 对 `<table>` 的渲染与 xhtml2pdf 不同，行间距过大。
**替代方案**: 使用 `<div>` 布局，CSS 控制更精确。

---

## 三、常见错误与修复速查表

| 错误签名 | 根因 | 修复命令 | 对应脚本 | 优先级 |
|----------|------|----------|----------|--------|
| `name 'default_page_size' is not defined` | 参数传递在 PyInstaller 后失效 | 硬编码 `value="A3"` | 手动修复 | P0 |
| `.msg` 正文只有纯文本 | CSS 处理顺序反了（先注后清） | 改为先清后注，确保 mm 单位 | 手动修复 | P0 |
| 合并卡死 / 切换纸张卡死 | WINWORD.EXE 僵尸进程 | `python scripts/fix_word_zombie.py` | `fix_word_zombie.py` | P0 |
| `python -m py_compile` 失败 | 语法错误或缩进问题 | 检查缩进，修复语法 | 手动修复 | P0 |
| PowerShell 中文替换静默失败 | 编码不匹配 | 用 Python 脚本替代 PowerShell | 手动修复 | P0 |
| EXE 大小异常（小于 30MB） | PyInstaller 打包不完整 | `python scripts/check_exe_size.py <exe>` | `check_exe_size.py` | P1 |
| 中文显示为 `??` | 日志包含非 ASCII 字符 | 所有日志改为纯英文 | 手动修复 | P1 |
| Excel A3 纸张大小不生效 | 未设置 ActivePrinter | 导出前设 `ActivePrinter = "Microsoft Print to PDF"` | 手动修复 | P1 |
| HTML 体积爆炸（25KB→1.39MB） | base64 内嵌图片过大 | 限制单张图片 200KB，超过跳过 | 手动修复 | P1 |
| ZIP 附件转换失败 | `temp_pdf` 路径不存在 | ZIP 类型跳过 `temp_pdf` 检查 | 手动修复 | P1 |
| Word 受保护文档纸张大小失败 | 无法修改 `PageSetup` | 先尝试 `doc.Unprotect()`，失败则跳过 | 手动修复 | P1 |
| 纯文本超出纸张宽度 | `drawString` 无自动换行 | 按 `font_size * 0.55` 估算字符宽度，超宽断行 | 手动修复 | P1 |
| RTF 编码错误 (byte 0x90) | extract_msg 库内部编码问题 | 降级到纯文本 fallback，等待 Outlook COM 替代 | 手动修复 | P1 |
| `PATH: _html_body_to_pdf` 日志不出现 | 诊断日志在 `_logging.disable()` 之后 | `python scripts/check_logging_order.py <file>` | `check_logging_order.py` | P1 |
| page_size 传递链断裂 | 附件转换调用没传 page_size | `python scripts/check_page_size_calls.py <file>` | `check_page_size_calls.py` | P1 |
| PyInstaller 不捡 attachment_handler.py | 动态路径导入导致 | `python scripts/clean_pyinstaller_cache.py` | `clean_pyinstaller_cache.py` | P1 |
| 子代理只分析不执行 | 默认分析模式 | 写 "EXECUTE all steps. Do NOT analyze" | 手动修复 | P1 |
| `extract_msg.Message()` 构造函数崩溃 | RTF 正文含 byte 0x90 | 无法修（库内部问题），需 Outlook COM 替代 | 手动修复 | P1 |
| 纯文本 fallback 包含 HTML 标签 | `.body` 属性可能包含原始 HTML | `re.sub(r'<[^>]+>', '', info['body'])` 剥离 | 手动修复 | P1 |
| LibreOffice fallback 缺 page_size | 函数签名没有 page_size 参数 | 补上 `page_size` 参数 | 手动修复 | P1 |
| Pillow fallback 缺 page_size | 函数签名没有 page_size 参数 | 补上 `page_size` 参数 | 手动修复 | P1 |
| `print` 中文崩溃 (cp1252) | `--windowed` EXE 的 sys.stdout 用 cp1252 | 模块级 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')` | 手动修复 | P0 |
| `'Message' object has no attribute 'senderEmail'` | extract_msg 版本属性不一致 | 所有属性用 `getattr(msg, 'attr', None) or default` | 手动修复 | P0 |
| Excel COM 被跳过 (RPC_E_SERVERCALL_REJECTED) | Excel COM 调用被拒绝 | 追加 openpyxl+Pillow 回退方案 | 手动修复 | P1 |
| tkinter 跨线程崩溃 ("main thread is not in main loop") | 子线程创建 GUI | 用 `root.after(0, callback)` 代替 `threading.Thread` | 手动修复 | P0 |
| 嵌入 .msg 报 "a bytes-like object is required, not 'Message'" | `attachment.data` 对 type==1 返回 Message 对象 | 用 `save(extractEmbedded=True)` 后重新打开 | 手动修复 | P0 |
| 临时文件冲突（合并出现旧内容） | 固定文件名 `temp_1.pdf` | 用 `uuid.uuid4().hex[:8]` 生成唯一名称 + 清空列表时 cleanup | 手动修复 | P1 |
| 图片压缩后不显示 | 压缩为 JPEG 但 MIME 类型还是 `image/png` | 压缩后更新 MIME 为 `image/jpeg` | 手动修复 | P1 |
| COM 路径图片不显示（HTML 只有 3KB） | `_read_msg_html_via_outlook` 只返回 HTML 不返回附件 | 函数返回 `(html_body, attachments)` 元组 | 手动修复 | P0 |
| PDF 中链接/邮箱有多余下划线 | xhtml2pdf 渲染 `<a>` 标签 + CSS underline | 移除 CSS `text-decoration:underline` + `<a>` 替换为 `<span>` | 手动修复 | P1 |
| 清空列表后再次合并出现旧内容 | `_clear_list()` 没清理临时文件 | 添加 `cleanup_temp_files()` 调用 | 手动修复 | P1 |
| Excel 文件被锁定（无法在其他程序中打开） | Excel COM 对象未释放，文件句柄被占用 | `finally` 块中 `del workbook/excel` + `taskkill EXCEL.EXE` | 手动修复 | P0 |
| weasyprint 纸张大小不生效（A3 输出为 A4） | 需用 `@page` CSS + mm 单位 + CSS 对象传递 | `CSS(string=page_css)` 传入 `write_pdf(stylesheets=[css_obj])` | 手动修复 | P1 |
| weasyprint 行间距过大 | 默认 CSS 与 xhtml2pdf 不同 | `body { line-height: 1.0; } p { margin: 0; } div { margin: 0; }` | 手动修复 | P1 |
| PyInstaller 缓存导致旧代码被执行 | `.pyc` 优先于 `.py` | `--clean` + 删 `__pycache__` + 删 `%APPDATA%\pyinstaller` | 手动修复 | P1 |
| `msg_to_pdf() got unexpected keyword argument` | 函数签名与调用处参数不匹配 | 确保函数签名包含调用方传入的所有参数 | 手动修复 | P1 |
| HTML 备份保存到临时目录 | `final_output_dir` 被无条件覆盖 | 仅当 `final_output_dir is None` 时才从 `output_pdf` 推导 | 手动修复 | P2 |

---

## 四、Agent 行为规则

### 规则1：提出新方案前先检查否决列表 [P0]
**行为**: 在提出任何新方案之前，必须先检查本文档的"已被彻底否决的方案"章节。
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

### 规则6：中文字符串替换必须用 Python 脚本 [P0]
**行为**: 禁止使用 PowerShell 的 `-replace` 进行中文字符串替换。
**原因**: PowerShell 传递中编码不匹配，会导致静默失败。
**执行**:
```python
# ✅ 正确：用 Python 脚本
python -c "
import pathlib
p = pathlib.Path('file.py')
content = p.read_text(encoding='utf-8')
content = content.replace('旧代码', '新代码')
p.write_text(content, encoding='utf-8')
"

# ❌ 错误：用 PowerShell
(Get-Content file.py) -replace '旧代码', '新代码' | Set-Content file.py
```

### 规则7：每个转换路径出口打标记 [P2]
**行为**: 在每个转换路径的出口添加唯一的英文标记（如 `PATH: Word COM OK`）。
**原因**: 用户可以快速搜索定位问题，一秒找到转换路径。
**执行**:
```python
# 在每个成功/失败路径添加标记
logger.info("PATH: Word COM OK")
logger.warning("PATH: Word FALLBACK python-docx")
logger.error("PATH: Word FAILED all methods")
```

### 规则8：上下文太长时果断新开会话 [P2]
**行为**: 当响应变慢、子代理质量下降时，果断新开会话。
**原因**: 上下文太长会导致编码错误、静默失败等问题。
**执行**:
```
1. 监控响应时间
2. 如果响应变慢，考虑新开会话
3. 使用 handoff 文件传递上下文
4. 在新会话中继续工作
```

### 规则9：测试数据不能上 GitHub [P1]
**行为**: 含保密数据的测试文件必须在 .gitignore 中排除，且从 git 历史中清除。
**原因**: 测试数据可能包含敏感信息，不能公开。
**执行**:
```
1. 在 .gitignore 中添加测试数据目录
2. 如果已提交，用 git filter-branch 清除历史
3. 验证 GitHub 上没有测试数据
```

### 规则10：子代理不靠谱时自己动手 [P2]
**行为**: 当子代理多次只分析不执行时，用 bash + Python 脚本直接修改文件。
**原因**: 子代理可能默认分析模式，不执行实际修改。
**执行**:
```
1. 如果子代理 3 次不执行，自己动手
2. 用 bash + Python 脚本直接修改文件
3. 修改后验证文件内容
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
    └── OutlookAgent_v{VERSION}\ # 发布目录（版本号从 main.py 读取）
        ├── PDFMergeTool.exe
        ├── OutlookAgent.exe
        └── README.txt
```

---

## 附录：构建与发布

### build.bat 参数参考

**PDFMergeTool** (`agent_tool\pdf_merge_tool\build.bat`):
```
pyinstaller --onefile --windowed --name "PDFMergeTool" ^
  --hidden-import=converters --hidden-import=converters.txt_to_pdf ^
  --hidden-import=converters.image_to_pdf --hidden-import=converters.word_to_pdf ^
  --hidden-import=converters.excel_to_pdf --hidden-import=converters.pdf_merger ^
  --hidden-import=converters.msg_to_pdf --hidden-import=converters.zip_handler ^
  --hidden-import=utils --hidden-import=utils.file_utils --hidden-import=utils.page_numbers ^
  --hidden-import=utils.crash_dump ^
  --hidden-import=pypdf --hidden-import=PIL --hidden-import=PIL.Image ^
  --collect-all reportlab ^
  --hidden-import=reportlab.graphics.barcode.code128 ^
  --hidden-import=reportlab.graphics.barcode.code93 ^
  --hidden-import=reportlab.graphics.barcode.code39 ^
  --hidden-import=reportlab.graphics.barcode.eanbc ^
  --hidden-import=reportlab.graphics.barcode.usps ^
  --hidden-import=reportlab.graphics.barcode.usps4s ^
  --hidden-import=reportlab.graphics.barcode.ecc200datamatrix ^
  main.py
```

**OutlookAgent** (`agent_tool\outlook_agent\build.bat`):
```
pyinstaller --onefile --windowed --name "OutlookAgent" ^
  --hidden-import=attachment_handler ^
  --hidden-import=win32timezone --hidden-import=pythoncom --hidden-import=pywintypes ^
  --hidden-import=win10toast --hidden-import=extract_msg --hidden-import=olefile ^
  --hidden-import=weasyprint --hidden-import=cffi ^
  --collect-all weasyprint --collect-all reportlab ^
  main.py
```

**构建前置条件**（weasyprint 依赖）:
```
# 安装 MSYS2
winget install MSYS2.MSYS2

# 初始化 keyring + 安装 pango
C:\msys64\usr\bin\bash.exe -lc "pacman-key --init && pacman-key --populate"
C:\msys64\usr\bin\pacman.exe -S mingw-w64-x86_64-pango --noconfirm

# 构建时设置 PATH
$env:PATH = "C:\msys64\mingw64\bin;" + $env:PATH
```

### 完整发布流程

> **版本号**：从 main.py 的 `__version__` 读取，不要硬编码。以下用 `{VERSION}` 表示。

```
1. 确认版本号
   - 查看 agent_tool\outlook_agent\main.py 的 __version__
   - 确保两个 main.py 版本号一致

2. kill 旧进程
   taskkill /f /im OutlookAgent.exe
   taskkill /f /im PDFMergeTool.exe

3. 清理 + 构建
   Remove-Item -Force -Recurse agent_tool\pdf_merge_tool\dist,build,*.spec,__pycache__ -ErrorAction SilentlyContinue
   cmd /c "cd agent_tool\pdf_merge_tool && build.bat"
   Remove-Item -Force -Recurse agent_tool\outlook_agent\dist,build,*.spec,__pycache__ -ErrorAction SilentlyContinue
   cmd /c "cd agent_tool\outlook_agent && build.bat"

4. 验证 EXE
   - 大小：PDFMergeTool ~41MB, OutlookAgent ~38MB
   - 小于 30MB 说明打包不完整

5. 创建发布目录 + 复制 EXE
   $ver = (从 main.py 读取 __version__)
   New-Item -ItemType Directory -Path "agent_tool\release_package\OutlookAgent_v$ver"
   Copy-Item agent_tool\pdf_merge_tool\dist\PDFMergeTool.exe agent_tool\release_package\OutlookAgent_v$ver\ -Force
   Copy-Item agent_tool\outlook_agent\dist\OutlookAgent.exe agent_tool\release_package\OutlookAgent_v$ver\ -Force

6. 更新 README.txt
   - 找到上一版本的 README.txt（release_package 目录中最新的文件夹）
   - 在更新日志顶部追加新版本 changelog，不要重写
   - changelog 用用户能理解的语言（如"修复邮件格式丢失"）
   - 复制到新发布目录

7. 打 ZIP 包
   Compress-Archive -Path "agent_tool\release_package\OutlookAgent_v$ver\*" -DestinationPath "agent_tool\release_package\OutlookAgent_v$ver.zip" -Force
```

⚠️ 注意事项：
- EXE 被占用时无法覆盖 — 任务管理器杀进程，或先重命名旧文件再复制
- 版本号从 main.py 读取，不要硬编码
- README.txt 参考**上一个已发布版本**的格式

---

## 附录：验证检查清单

- [ ] `python -m py_compile` 通过
- [ ] EXE 大小正常（PDFMergeTool ~41MB, OutlookAgent ~38MB）
- [ ] attachment_handler.py 的改动是否需要同步到 msg_to_pdf.py
- [ ] 所有 subprocess 都有 `creationflags=0x08000000`
- [ ] 版本号已确认（两个 main.py 的 `__version__` 一致）
- [ ] 发布目录已创建且 EXE 已复制
- [ ] README.txt 已追加新版本 changelog
- [ ] ZIP 包已生成

---

## 附录：日志位置

> 注意：以下路径为示例，实际路径因用户环境而异。

- PDFMergeTool: `C:\Users\<用户名>\PDFMergeTool_logs\`
- OutlookAgent: `C:\Users\<用户名>\outlook_agent_logs\`

---

## 附录：项目专属规则

### 测试目录不入 Git
`agent_tool/测试/` 含保密数据，已在 .gitignore 中排除。如已提交需用 git filter-branch 清除历史。

### README 更新规范
每次打包 release 时，基于前一个版本的 README.txt 追加新版本 changelog，不要重写。changelog 用用户能理解的语言（如"修复邮件格式丢失"），不要用技术术语（如"PyInstaller 打包不包含 attachment_handler.py"）。

### 版本号管理规则 [P0]

**何时更新版本号**：
- ✅ 正式 release 给用户时才更新版本号
- ❌ 测试阶段不要自动递增版本号

**构建流程**：
1. **测试阶段**：使用当前版本号构建，**不要修改** `__version__`
2. **正式发布**：用户明确要求时才更新 `__version__`
3. **构建前确认**：读取当前版本号，不要自动更新

**错误示范**：
```python
# ❌ 错误：每次构建都更新版本号
content = content.replace('__version__ = "1.2.10"', '__version__ = "1.2.11"')
```

**正确示范**：
```python
# ✅ 正确：读取当前版本号，不修改
version = re.search(r'__version__\s*=\s*"([^"]+)"', content).group(1)
print(f"Current version: {version}")
```

---

*整合时间：2026-05-31*
*整合自：outlookagent-dev.md、memory_1.md 到 memory_4.md*
*核心版本：`.sisyphus/skills/SKILL.md`（精简版，日常使用）*

---

## 五、经验教训（按版本）

### v1.2.0 经验 (2026-05-21)

#### 新增知识点
1. xhtml2pdf 对现代 CSS 选择器脆弱 → 必须清原始 `<style>` 块
2. `threading.Timer` 不能中断 C 扩展阻塞 → 用 `Thread.join(timeout)`
3. Word COM `Quit()` 可能静默失败 → 必须 `taskkill` 兜底
4. 跨模块参数传递在 PyInstaller 后可能失效 → 能硬编码就别传参

#### 坑
- CSS 顺序修了两遍才正确（第一遍改反了）
- 加了 taskkill 但忘加 `creationflags` → 新引入黑框 bug
- 两个 `_html_body_to_pdf` 独立副本，同步易遗漏
- 上下文太长导致 agent 质量下降

#### 教训
- 一次只修一个 bug，验证通过再下一个
- 改完立即检查 subprocess 调用有无窗口隐藏
- 改 attachment_handler.py 必须同步 msg_to_pdf.py

---

### v1.2.0 → v1.2.2 经验 (2026-05-21~26)

#### 新增知识点
1. **xhtml2pdf 字体需要双 patch**：`DEFAULT_CSS` 和 `DEFAULT_FONT` 两处都要改
2. **系统 TTF 字体 > CID 字体**：PyInstaller 打包后 CID 数据可能不可用
3. **懒加载字体初始化**：模块级代码在 `logging.basicConfig()` 之前执行 → 日志丢失
4. **Python 中文字符串替换静默失败**：PowerShell 传递中编码不匹配
5. **extract_msg 的 `hidden` 属性不可靠**：部分 logo `hidden=False` 但仍有 `contentId`
6. **Word COM `Close()` 失败会覆盖好 PDF**：SaveAs 后先验证 PDF 存在
7. **Trust Center 文件阻止**：`AutomationSecurity = 1` 不能绕过文件阻止设置
8. **Combobox `.set("A3")` 覆盖用户选择**：改用 `.current(0)` 设置默认选中项
9. **`--windowed` EXE 日志规范**：所有日志必须 `logger.warning` + 纯英文 ASCII
10. **PATH 标签策略**：每个转换路径出口加唯一英文标记

#### 坑
- 代码编辑至少 5 次静默失败：中文字符串替换编码不匹配
- `dist` 目录在部署前被清理 → 需要重新跑 PyInstaller（15 分钟）
- EXE 被运行的旧进程锁定 → `Copy-Item` 静默失败
- Python 插入脚本 `break` 没写对 → `attachment_handler.py` 被截断
- 字体候选只列了 3 个 → 用户电脑正好都没有 → 回退到 CID → 中文 ■
- `AutomationSecurity = 1` 以为能绕过 Trust Center → 实际只绕过了宏安全

#### 教训
1. **改完立即验证**：`py_compile` + `read` 回读关键行
2. **部署原子化**：kill 进程 → 构建 → 复制 → 验证文件大小
3. **中文字符串 → 行号定位**：禁止直接拼接中文做代码替换
4. **每个出口打标记**：`PATH: COM OK` / `PATH: FALLBACK python-docx`
5. **双 EXE 同步检查**：改 `_html_body_to_pdf` 必须两个文件都改
6. **不要假设用户环境**：候选列表至少 5 个字体
7. **上下文过长时果断新开会话**

---

### v1.2.3 → v1.2.4 经验 (2026-05-26~27)

#### 新增知识点
1. **深层嵌套附件提取无过滤**：需在所有附件提取路径插入过滤块（7 处）
2. **xhtml2pdf 表格拆页根因**：base64 内嵌图片才是主因，不是表格宽度
3. **`_logging.disable(_logging.CRITICAL)` 会静默所有 logger 调用**：诊断日志必须移到 disable 之前
4. **Excel COM PageSetup.PaperSize 只能用枚举**：不能直接设 PageWidth/PageHeight
5. **PyInstaller 动态路径导入陷阱**：EXE 中可能不含修改后的代码
6. **ZIP 文件双重处理**：Phase 0 解压后原 ZIP 仍保留在列表中
7. **README 版本号批量替换陷阱**：`-replace` 会改所有历史 changelog

#### 硬伤记录
| # | 硬伤 | 后果 | 修复 |
|:-:|------|------|------|
| 1 | `attachment_handler.py` 修复后 PyInstaller 5 次重建均不含修改 | Issue 1 阻塞 | 待解决 |
| 2 | 渲染日志放在 `_logging.disable()` 之后 | 用户看不到渲染成功/失败 | 移到 disable 之前 |
| 3 | Excel `else: ps = 9` 无条件强制 A4 | 用户选非标准尺寸时被覆盖 | 改为 `ps = None` |
| 4 | README `-replace` 改了所有历史版本号 | v1.2.3 changelog 变成 v1.2.4 | 精确行匹配修复 |
| 5 | PyInstaller 缓存 `.pyc` 优先于 `.py` | 源码改了但打包不生效 | `--clean` + 删 `__pycache__` |
| 6 | PowerShell 中文显示 `??` | 误判修改未生效 | 用 `read` 命令验证 |
| 7 | Sisyphus-Junior 多次只分析不执行 | 同一任务派发 3-5 次 | 写 "EXECUTE" |

#### 教训
1. **PyInstaller 打包是最大风险点**：改源码只是 50%，确认 EXE 含修改才是 100%
2. **CSS 注入要考虑图片场景**：base64 图片体积是正文的 2-3 倍
3. **一次修 1-2 个问题**：一口气改 4+ 个文件容易搞坏
4. **Handoff + Skills 文件是长期记忆**：上下文会稀释
5. **`/review-work` 应该在每次发版前跑**：5 个 agent 并行审查
6. **Sisyphus-Junior 需要 "EXECUTE" 关键词**

---

### v1.2.4 → v1.2.5 经验 (2026-05-27~30)

#### 新增知识点
1. **Excel COM `ExportAsFixedFormat` 依赖打印机**：必须设 `ActivePrinter = "Microsoft Print to PDF"`
2. **`extract_msg` 库的 `htmlBody` 会在初始化时崩溃**：RTF 正文含 byte 0x90 时构造函数就抛异常
3. **base64 内嵌图片体积爆炸**：必须限制单张图片 200KB，超过跳过
4. **ZIP 附件处理的 `temp_pdf` 路径问题**：ZIP 类型跳过该检查
5. **Word 受保护文档的 `Unprotect()`**：设置 PageSetup 前先尝试解除保护
6. **`txt_to_pdf` 的 `drawString` 无自动换行**：按字符宽度估算自动拆行
7. **page_size 传递链断裂**：8 处调用全部补上 `page_size=page_size`
8. **Word fallback 路径缺 page_size**：函数签名没有 page_size 参数

#### 硬伤记录
| # | 硬伤 | 后果 | 修复 |
|:-:|------|------|------|
| 1 | `msg.htmlBody` 抛编码异常但没有 try/except | HTML 渲染路径崩溃 | 包裹 try/except |
| 2 | 纯文本 fallback 包含 HTML 标签 | PDF 中显示原始标签 | `re.sub` 剥离 |
| 3 | `txt_to_pdf` 的 `drawString` 无换行 | 长行溢出页面右侧 | 按字符宽度估算拆行 |
| 4 | 附件转换没传 `page_size` | .msg 附件始终 A4 | 8 处调用补参数 |
| 5 | ZIP 处理后 `temp_pdf` 不存在 | 误报转换失败 | ZIP 类型跳过检查 |
| 6 | `extract_msg.Message()` 构造函数崩溃 | 所有 fallback 代码跑不到 | 需 Outlook COM 替代 |
| 7 | 子代理只分析不执行 | 代码修改没生效 | 用 bash 直接执行 |
| 8 | PowerShell 中文替换编码问题 | 替换失败但无报错 | 用 Python 脚本 |
| 9 | `ps` 变量未初始化 | 非标准尺寸时 NameError | `ps = None` 初始化 |

#### 教训
1. **先看日志再修代码**：日志里 `htmlBody failed` 和 `charmap codec` 就是根因
2. **子代理不靠谱时自己动手**：用 bash + Python 脚本直接修改文件更可靠
3. **`extract_msg` 库是最大风险**：RTF 编码问题无法绕过，只能用 Outlook COM 替代
4. **page_size 传递链必须完整**：主路径传了不代表附件路径也传了
5. **ZIP 处理是特殊路径**：ZIP 不创建自己的 PDF，后续检查逻辑要跳过
6. **上下文太长时果断新开会话**：响应变慢、子代理质量下降都是信号
7. **Git 是必须的**：没有 git 历史，无法追溯"默认值什么时候从 A3 变成 A4"
8. **测试数据不能上 GitHub**：含保密数据的测试文件必须在 .gitignore 中排除

---

*教训和坑整合时间：2026-06-01*
*来源：outlookagent-dev.md 本轮经验章节*

---

### v1.2.6 经验 (2026-06-03~04)

#### 新增知识点
1. **COM 路径必须返回附件数据**：`_read_msg_html_via_outlook` 需返回 `(html_body, attachments)` 元组，否则内嵌图片丢失
2. **附件格式兼容字典和对象**：COM 返回字典格式，extract_msg 返回对象格式，`_html_body_to_pdf` 必须两种都支持
3. **大图片压缩而非跳过**：`MAX_INLINE_IMG_SIZE = 200KB` 过于激进，应用 PIL 压缩（RGBA→RGB + JPEG quality=85）
4. **CID 替换前必须验证存在**：`str.replace()` 找不到子串静默返回原串，图片不显示但无报错
5. **图片压缩后必须更新 MIME 类型**：压缩为 JPEG 但 MIME 还是 `image/png` → 浏览器无法渲染
6. **三层降级渲染**：sanitized CSS → strip all `<style>` → plain text，单次尝试失败无回退
7. **诊断 HTML 必须保存**：渲染前保存到 `%TEMP%\email_debug.html`，否则难以定位渲染问题
8. **`<a>` 标签导致下划线**：xhtml2pdf 渲染 `<a>` 标签产生下划线，需替换为 `<span>` + 移除 CSS underline

#### 硬伤记录
| # | 硬伤 | 后果 | 修复 |
|:-:|------|------|------|
| 1 | COM 路径只返回 HTML 不返回附件 | 内嵌图片全部丢失 | 函数返回元组 |
| 2 | `getattr` 访问字典格式附件 | 返回默认值，图片不处理 | `isinstance(att, dict)` 分支 |
| 3 | 大图片直接跳过 | 用户截图丢失 | PIL 压缩 |
| 4 | CID 替换不验证存在 | 图片不显示但无报错 | 先检查再替换 |
| 5 | 压缩后 MIME 类型不更新 | 浏览器无法渲染 | 改为 `image/jpeg` |

#### 教训
1. **COM 和 extract_msg 是两条路径**：返回格式不同（字典 vs 对象），必须兼容
2. **压缩 > 跳过**：用户宁可看到压缩图也看不到丢失的截图
3. **CID 替换要先验证**：`str.replace` 的静默行为是隐形 bug 来源
4. **MIME 类型要跟着数据走**：数据变了 MIME 必须同步变

---

### v1.2.7 经验 (2026-06-06)

#### 新增知识点
1. **Excel COM 对象必须显式释放**：`finally` 块中 `del workbook/excel` + `taskkill EXCEL.EXE`，否则文件句柄被占用
2. **邮件头部信息注入**：在 HTML 渲染前注入 From/Sent/To/Cc/Subject，用 `<div>` 布局（不用 `<table>`）
3. **weasyprint 需设置 `WEASYPRINT_DLL_DIRECTORIES`**：PyInstaller 打包后需告诉 cffi DLL 的位置
4. **weasyprint 构建依赖 MSYS2 + pango**：`winget install MSYS2.MSYS2` + `pacman -S mingw-w64-x86_64-pango`

#### 硬伤记录
| # | 硬伤 | 后果 | 修复 |
|:-:|------|------|------|
| 1 | Excel COM 对象未释放 | 原始 Excel 文件被锁定 | `finally` 块显式删除 + taskkill |
| 2 | weasyprint DLL 路径未设置 | PyInstaller 打包后报 DLL 加载失败 | 设置 `WEASYPRINT_DLL_DIRECTORIES` |
| 3 | 邮件头部用 `<table>` 布局 | weasyprint 渲染行间距过大 | 改用 `<div>` 布局 |

#### 教训
1. **COM 对象必须显式释放**：Excel 比 Word 更容易泄漏句柄
2. **weasyprint 的 DLL 依赖**：PyInstaller 打包后需要特殊处理
3. **`<table>` vs `<div>`**：weasyprint 对表格渲染与 xhtml2pdf 不同，优先用 div

---

### v1.2.8 经验 (2026-06-10)

#### 新增知识点
1. **Outlook 使用 Word 渲染引擎**：不遵循标准 CSS 的 margin 规范，`p` 标签默认 margin 很小或为 0
2. **weasyprint 遵循标准 CSS**：默认 `p` 标签有 `margin: 1em 0`，需要显式清除
3. **行间距优化**：`line-height: 1.0` + `p { margin: 0; }` 最接近 Outlook 渲染效果
4. **HTML 调试备份功能**：通过环境变量 `PDFMERGE_DEBUG_HTML=1` 控制，默认关闭
5. **final_output_dir 参数传递**：避免从临时路径推导最终输出目录
6. **条件赋值**：`if not final_output_dir:` 避免覆盖传入的参数
7. **MSYS2/pango 构建依赖**：构建时需要设置 PATH，运行时 DLL 已打包到 EXE

#### 硬伤记录
| # | 硬伤 | 后果 | 修复 |
|:-:|------|------|------|
| 1 | `final_output_dir = os.path.dirname(output_pdf)` 无条件覆盖 | 传入的参数被忽略，HTML 备份保存到临时目录 | 改为 `if not final_output_dir:` 条件赋值 |
| 2 | `msg_to_pdf` 函数签名缺少 `final_output_dir` 参数 | `main.py` 调用时报 `unexpected keyword argument` | 添加参数到函数签名 |
| 3 | `p { margin: 0 0 8px 0; }` 段落间距过大 | PDF 输出不像 Outlook | 改为 `p { margin: 0; }` |
| 4 | `line-height: 1.2` 行间距过大 | PDF 输出不像 Outlook | 改为 `line-height: 1.0` |

#### 教训
1. **Outlook 用 Word 引擎**：不遵循标准 CSS，需要特殊处理 margin 和 line-height
2. **参数传递要完整**：`msg_to_pdf` 的 `final_output_dir` 参数需要从 `main.py` 传递
3. **条件赋值避免覆盖**：`if not final_output_dir:` 保留传入的参数
4. **环境变量控制调试功能**：避免在生产环境生成不必要的文件
5. **构建时设置 PATH**：MSYS2/pango DLL 需要在构建时可访问
6. **测试验证**：行间距问题需要实际测试邮件来验证效果

---

*v1.2.8 经验整合时间：2026-06-10*
*来源：行间距优化 + HTML 调试功能 + weasyprint 迁移完善*