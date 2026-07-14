# Memory 13 — PRPOAgent v1.3.0 + Mail Agent MVP 技术决策

> 来源会话: 2026-07-09 到 2026-07-13 PRPOAgent 集成 + Mail Agent 编写
> 项目: OutlookAgent / PRPOAgent / Mail Agent (C:\Open AI Proj\agent_tool)

---

## 一、已确定的技术决策

### 13.1 PyInstaller --onefile EXE 内 subprocess.Popen 不可用

**决策**: PRPOAgent + Mail Agent 集成必须用 in-process daemon thread，不能用 subprocess.Popen

**原因**: 在 PyInstaller --onefile EXE 内，`sys.executable` 指向 EXE 本身（不是 Python 解释器）。subprocess.Popen([sys.executable, "-m", "agents.mail_agent", "--run"]) 会启动第二个 PRPOAgent.exe 副本，然后报 `ModuleNotFoundError: No module named 'config'`

**代码**:
```python
# agent_tool/pr_po_agent/mail_controller.py
class MailAgentThread:
    def start(self):
        from agents.mail_agent.monitor import MailAgent
        self._agent = MailAgent(self.rules_path, outlook_monitor_class=self._outlook_monitor_class)
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
```

**影响文件**:
- `agent_tool/pr_po_agent/mail_controller.py` (替换原始 subprocess 方案)
- `agent_tool/pr_po_agent/main.py` (调 MailAgentController.start())

### 13.2 规则引擎支持 list-valued 字段

**决策**: 规则条件 `attachment_names contains "PR Form"` 必须支持 list 字段（任一元素匹配即触发）

**原因**: 用户场景是"邮件附件名包含 PR Form"，附件是列表不是单值。默认 `str()` 操作会把 list 转成 `"['PR Form.xlsx']"` 这种字符串，无法匹配。

**代码**:
```python
# agent_tool/pr_po_agent/agents/mail_agent/rules_engine.py
def _check_single_condition(email, condition):
    actual = _get_field(email, condition["field"])
    op = _OPERATORS[condition["op"]]
    if isinstance(actual, (list, tuple)):
        if not actual: return False
        return any(op(str(x), condition["value"]) for x in actual if x)
    return op(str(actual), condition["value"])
```

**影响文件**:
- `agent_tool/pr_po_agent/agents/mail_agent/rules_engine.py`
- `agent_tool/pr_po_agent/agents/mail_agent/monitor.py` (在 normalized 加 attachment_names list)
- `agent_tool/pr_po_agent/agents/mail_agent/rules.yaml` (新默认规则用 attachment_names)

### 13.3 PyInstaller EXE 内 import 挂死的解决方法

**决策**: 在 `_bootstrap_outlook_monitor_class()` 中先 `sys.modules.get()`，找不到再 path manipulation

**原因**: EXE 内 `outlook_monitor.py` 的 `__file__` 指向 `_MEIPASS\outlook_agent\outlook_monitor.py`。即使把 `_MEIPASS\agent_tool\outlook_agent` 加到 sys.path，Python 导入器还要做文件系统查找，永远找不到 → 挂死

**代码**:
```python
def _bootstrap_outlook_monitor_class():
    for modname in ("outlook_monitor", "agent_tool.outlook_agent.outlook_monitor"):
        mod = sys.modules.get(modname)
        if mod is not None and hasattr(mod, "OutlookMonitor"):
            return mod.OutlookMonitor
    # Source-mode fallback only
    ...
```

**影响文件**:
- `agent_tool/pr_po_agent/mail_controller.py`

---

## 二、已被明确否决的方案

| # | 方案 | 否决原因 | 替代方案 |
|:-:|------|----------|----------|
| 1 | subprocess.Popen 启动 Mail Agent | EXE 内 sys.executable 不可靠 | in-process daemon thread |
| 2 | `from agent_tool.outlook_agent.outlook_monitor` 绝对导入 | `agent_tool/` 没 `__init__.py`，不是 package | `sys.modules` 快速路径 |
| 3 | `--onefile` 自动解决缓存问题 | 当前开发机 PyInstaller 缓存污染 | 干净环境重建 或 `--onedir` |
| 4 | Mail Agent UI 默认开启 | 用户应能控制何时启动 | 启动时自动 run，UI 可手动 stop |
| 5 | `os._exit` 替代 `sys.exit` 关第二个 EXE | 没解决根本问题 | 改用 in-process thread |

---

## 三、常见错误及修复方式

### 13.1 修复: PyInstaller EXE 重建缓存问题

**错误现象**: 
- `py -c "print(b'_setup_logging' in open('dist/PRPOAgent.exe','rb').read())"` 返回 `False`
- 但源码明明有 `_setup_logging()` 函数（行 24）
- 删除 `dist/build/__pycache__` + `pyinstaller --clean --noconfirm` 后还是同样问题

**根因**: 开发机的 PyInstaller 全局缓存（`%APPDATA%\pyinstaller` 等目录）已损坏，新构建仍套用陈旧字节码

**修复步骤**:
1. 在干净开发机或重启系统后重建
2. 用 `--onedir` 而非 `--onefile` 绕过 bytecode packing
3. 验证步骤：`python -c "data = open('dist/PRPOAgent.exe','rb').read(); print(b'mail_agent.log' in data, b'MailAgentController' in data)"`
4. 必须两个都返回 True，否则重新检查 hidden-imports

**影响文件**: `agent_tool/pr_po_agent/BUILD.md` (更新)

### 13.2 修复: PRPOAgent 启动时 PRN error

**错误现象**: 启动 `PRPOAgent.exe` 弹窗显示 "Unable to initialize device PRN"

**根因**: OutlookAgent v1.2.9 或 PDFMergeTool v1.1.0 启动时调用 Windows 打印 API 失败。这是历史 EXE 的内部行为，与 PRPOAgent.exe 或 Mail Agent 无关

**修复**: 忽略，邮件监听模块完全独立（独立进程或独立线程，不需要任何打印 API）

**影响文件**: 无

### 13.3 修复: Mail Agent 路径冲突

**错误现象**: `ModuleNotFoundError: cannot import name 'load_config' from 'config'`

**根因**: 
- `pr_po_agent/config.py` 和 `outlook_agent/config.py` 都叫 `config.py`
- 当 `outlook_agent` 在 `sys.path` 上时，`from config import load_config` 可能导入错误的 config

**修复**: 
- 临时移除 pr_po_agent 从 sys.path
- 清空 sys.modules 的 config 缓存
- 然后 import outlook_agent
- 最后恢复 pr_po_agent

**影响文件**:
- `agent_tool/pr_po_agent/agents/mail_agent/monitor.py:_import_outlook_monitor()`
- `agent_tool/pr_po_agent/mail_controller.py:_bootstrap_outlook_monitor_class()`

### 13.4 修复: 中文 EXE 日志显示 ??

**错误现象**: `--windowed` EXE 日志里中文显示成 `??`

**根因**: 进程启动时 `sys.stdout` 用 cp1252 编码，无法处理中文

**修复**: 
```python
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
```

**影响文件**: 所有 EXE 入口 (main.py, agents/mail_agent/__main__.py)

### 13.5 修复: Mail Agent 附件下载未触发

**错误现象**: Mail Agent 启动但 inbox 为空，附件没下载

**排查步骤**:
1. 检查 `%USERPROFILE%\PRPOAgent\mail_agent.log` 日志
2. 如果没有 "Polled N new emails" → Mail Agent 启动失败，看 main.py 错误
3. 如果有 "Polled" 但 "matched 0" → 规则不匹配，看 rules.yaml
4. 如果附件名匹配但是 `download_attachments` 没触发 → 检查 actions 列表

**影响文件**: `agent_tool/pr_po_agent/agents/mail_agent/rules.yaml`

---

## 四、关键代码位置

| 文件 | 函数 | 说明 |
|------|------|------|
| `agent_tool/pr_po_agent/main.py` | `main()` | PRPOAgent 入口 |
| `agent_tool/pr_po_agent/mail_controller.py` | `MailAgentController` | Mail Agent 进程管理（in-process thread） |
| `agent_tool/pr_po_agent/mail_controller.py` | `_bootstrap_outlook_monitor_class()` | OutlookMonitor 类获取（sys.modules 快速路径） |
| `agent_tool/pr_po_agent/ui/main_window.py` | `MainWindow` | 含 Mail Agent 状态栏 + Start/Stop 按钮 |
| `agent_tool/pr_po_agent/agents/mail_agent/monitor.py` | `MailAgent.__init__()` | 接受 outlook_monitor_class 注入 |
| `agent_tool/pr_po_agent/agents/mail_agent/monitor.py` | `_check_conditions()` | 支持 all/any 复合条件 |
| `agent_tool/pr_po_agent/agents/mail_agent/rules_engine.py` | `_check_single_condition()` | 支持 list-valued 字段 |
| `agent_tool/pr_po_agent/agents/mail_agent/rules.yaml` | — | 默认规则：attachment_names contains "PR Form" |
| `agent_tool/pr_po_agent/agents/mail_agent/__main__.py` | `cmd_check`, `cmd_run`, `cmd_path` | CLI 入口 |

---

## 五、待记录的后续需求

- v1.3.1: EXE 重建（解决 PyInstaller 缓存问题，待干净开发机）
- Phase 1.5: 可观测性基础（审计日志 + 重试队列）
- Phase 2.1: 报价单样本采集 + GPU 环境准备（Qwen-VL 16G+）
- Phase 2.3: 图片 OCR 提取（PaddleOCR + Qwen-VL）
- Phase 3: Acubuy 自动化（需 Playwright + 测试账号）
- Phase 4: SharePoint 集成（需 IT 开通 Graph API）
- 主计划修订: `prpo-master-plan.md` v2（18-25 周工期 + Phase 1.5 可观测性）
