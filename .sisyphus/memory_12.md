# Memory 12 — OutlookAgent v1.2.8 行间距优化、HTML 调试功能、weasyprint 迁移完善

> 来源会话: 2026-06-10 v1.2.8 行间距优化 + HTML 调试功能 + 打包发布
> 项目: OutlookAgent (C:\Open AI Proj)

---

## 一、已确定的技术决策

### 12.1 行间距优化：line-height 和 p margin 调整

**决策**: 将 `line-height` 从 `1.2` 改为 `1.0`，将 `p { margin: 0 0 8px 0; }` 改为 `p { margin: 0; }`

**原因**: 
- Outlook 使用 Word 渲染引擎，不遵循标准 CSS 的 margin 规范
- weasyprint 遵循标准 CSS 规范，默认 `p` 标签有 `margin: 1em 0`
- 测试发现 `margin-bottom: 0` 最接近 Outlook 的实际渲染效果
- `line-height: 1.0` 让行间距更紧凑

**代码**:
```python
page_css_parts.append('body { line-height: 1.0; }')
page_css_parts.append('p { margin: 0; }')
page_css_parts.append('div { margin: 0; }')
```

**影响文件**: 
- `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`

---

### 12.2 HTML 调试备份功能（可选）

**决策**: 添加 HTML 调试备份功能，默认关闭，通过环境变量 `PDFMERGE_DEBUG_HTML=1` 启用

**原因**: 
- 方便调试行间距问题
- 避免在生产环境中生成不必要的文件
- 通过环境变量控制，灵活启用

**代码**:
```python
# Save HTML backup for debugging (before weasyprint render)
# Only when PDFMERGE_DEBUG_HTML=1 environment variable is set
if os.environ.get('PDFMERGE_DEBUG_HTML') == '1':
    try:
        if final_output_dir:
            base_name = os.path.splitext(os.path.basename(output_pdf))[0]
            debug_html_path = os.path.join(final_output_dir, f"{base_name}_debug.html")
        else:
            debug_html_path = output_pdf.replace('.pdf', '_debug.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n')
            f.write('<style>\n' + page_css + '\n</style>\n')
            f.write('</head>\n<body>\n')
            f.write(html_body)
            f.write('\n</body>\n</html>')
        logger.info(f"DEBUG: HTML backup saved to {debug_html_path}")
    except Exception as e:
        logger.warning(f"DEBUG: Failed to save HTML backup: {e}")
```

**影响文件**: 
- `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`

---

### 12.3 final_output_dir 参数传递

**决策**: 在 `msg_to_pdf` 函数中添加 `final_output_dir` 参数，用于传递最终输出目录

**原因**: 
- `msg_to_pdf` 函数接收的 `output_pdf` 是临时目录中的文件
- HTML 备份需要保存到最终输出目录
- 通过参数传递，避免从临时路径推导

**代码**:
```python
def msg_to_pdf(
    msg_path: str, 
    output_pdf: str, 
    include_info_page: bool = False,
    page_size=None,
    include_attachments: bool = True,
    _depth: int = 0,
    final_output_dir: str = None
) -> Tuple[bool, str]:
```

**影响文件**: 
- `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`
- `agent_tool/pdf_merge_tool/main.py`（调用处）

---

### 12.4 final_output_dir 条件赋值

**决策**: 仅当 `final_output_dir` 为 `None` 时才从 `output_pdf` 推导

**原因**: 
- 之前的代码无条件覆盖了传入的参数
- `output_pdf` 是临时目录中的文件，推导出的目录是临时目录
- 需要保留传入的 `final_output_dir` 参数

**代码**:
```python
# Get final output directory for HTML debug backup
if not final_output_dir:
    final_output_dir = os.path.dirname(output_pdf)
```

**影响文件**: 
- `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`

---

## 二、已被明确否决的方案

| # | 方案 | 否决原因 | 替代方案 |
|:-:|------|----------|----------|
| 1 | 使用 `line-height: 1.2` | 行间距过大，不像 Outlook | 使用 `line-height: 1.0` |
| 2 | 使用 `p { margin: 0 0 8px 0; }` | 段落间距过大，不像 Outlook | 使用 `p { margin: 0; }` |
| 3 | HTML 备份始终生成 | 会在生产环境生成不必要的文件 | 通过环境变量控制，默认关闭 |
| 4 | 从 `output_pdf` 推导 `final_output_dir` | `output_pdf` 是临时路径，推导出的目录是临时目录 | 通过参数传递最终输出目录 |

---

## 三、常见错误及修复方式

### 12.1 msg_to_pdf() got an unexpected keyword argument 'final_output_dir'

**错误现象**: 
```
TypeError: msg_to_pdf() got an unexpected keyword argument 'final_output_dir'
```

**修复步骤**:
1. 在 `msg_to_pdf` 函数签名中添加 `final_output_dir: str = None` 参数
2. 确保函数签名与调用处的参数匹配

**代码**:
```python
def msg_to_pdf(
    msg_path: str, 
    output_pdf: str, 
    include_info_page: bool = False,
    page_size=None,
    include_attachments: bool = True,
    _depth: int = 0,
    final_output_dir: str = None  # 添加这个参数
) -> Tuple[bool, str]:
```

**影响文件**: `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`

---

### 12.2 HTML 备份保存到临时目录而不是最终输出目录

**错误现象**: HTML 备份文件保存在 `C:\Users\P1313993\AppData\Local\Temp\pdf_merge_tool_temp\_email_body_debug.html`，而不是最终输出目录

**修复步骤**:
1. 在 `main.py` 中传递 `final_output_dir=os.path.dirname(output_path)` 给 `msg_to_pdf`
2. 在 `msg_to_pdf` 中添加 `if not final_output_dir:` 条件判断
3. 保留传入的 `final_output_dir` 参数，不被覆盖

**代码**:
```python
# main.py
success, error = msg_to_pdf(file_path, temp_pdf, include_info_page=False, page_size=page_pts,
                            include_attachments=self.include_msg_attachments_var.get(),
                            final_output_dir=os.path.dirname(output_path))

# msg_to_pdf.py
if not final_output_dir:
    final_output_dir = os.path.dirname(output_pdf)
```

**影响文件**: 
- `agent_tool/pdf_merge_tool/main.py`
- `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py`

---

## 四、关键代码位置

| 文件 | 函数 | 说明 |
|------|------|------|
| `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py` | `_html_body_to_pdf()` | 邮件 HTML 转 PDF（weasyprint） |
| `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py` | `msg_to_pdf()` | MSG 文件转 PDF 主函数 |
| `agent_tool/pdf_merge_tool/main.py` | `_merge_worker()` | 合并工作线程，调用 msg_to_pdf |
| `agent_tool/pdf_merge_tool/converters/msg_to_pdf.py` | `_build_email_header_html()` | 生成邮件头部 HTML |

---

## 五、待记录的后续需求

- 无

---

## 六、版本信息

- **v1.2.8 已 release**
- 位置：`C:\Open AI Proj\agent_tool\release_package\OutlookAgent_v1.2.8\`
- GitHub：已推送（commit d8c575d）
- 主要变化：行间距优化、HTML 调试功能、weasyprint 迁移完善
