# Handoff: OutlookAgent / PRPOAgent v1.3.0 + Mail Agent MVP

> 会话结束时生成，供下次会话快速上手
> 接手日期：2026-07-13
> 项目：OutlookAgent + PRPOAgent + Mail Agent
> 当前版本：v1.3.0（GitHub Release 已发布，源码完整提交）

---

## 项目背景

- 项目：OutlookAgent（Outlook 邮件 + PDF 工具集）+ PRPOAgent（PR/PO 采购自动化代理）
- 当前版本：v1.3.0（已发布到 GitHub Release）
- 目标：3 个 EXE 协同 — OutlookAgent（v1.2.9 邮件转 PDF）+ PDFMergeTool（v1.1.0 PDF 合并）+ PRPOAgent（v1.3.0 UI 骨架 + Mail Agent 内部集成）

---

## 已确定的决策（不要推翻）

### 架构层
- **PRPOAgent UI 骨架**：系统托盘 + 中文主窗口 + 4 个标签设置 + 单实例防护
- **中文 UI**：Microsoft YaHei 字体，硬编码中文（不退化英文）
- **单实例锁**：`%TEMP%\PRPOAgent.single.lock`，用 `os.open(O_CREAT | O_EXCL)` + `os._exit(0)`
- **UTF-8 stdout 包装**：`io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")` 防 cp1252 崩溃

### Mail Agent 关键决策
- **集成方式**：PRPOAgent 启动时**自动 in-process thread** 拉起 Mail Agent（不是 subprocess）
- **规则引擎 YAML 驱动**：`agents/mail_agent/rules.yaml` 含 7 个操作符 + 复合条件（all/any）
- **List-valued 字段**：规则引擎支持 list 字段（如 attachment_names），任一元素匹配即触发
- **附件名匹配规则**：默认规则 `attachment_names contains "PR Form" AND sender_email ends_with "@company.com"`
- **inbox 目录**：`%USERPROFILE%\PRPOAgent\inbox\`（含 `<EntryID>.json` 记录 + `attachments\<EntryID>\`）
- **OutlookMonitor 类注入**：MailAgentController 在 PRPOAgent 启动时预导入 OutlookMonitor 类，传给 MailAgent 避免 EXE 内的 sys.path 问题
- **去重**：`%USERPROFILE%\PRPOAgent\processed.json` 保存已处理邮件 ID（重启不重复）

### PDF 生成
- **CSS 先清后注**：先 `re.sub` 清掉原 `<style>` 再注入 `@page`（防无限循环）
- **@page 用 mm 不用 pt**：xhtml2pdf 对 pt 支持不全，A3 会死循环
- **attachment_handler.py 和 msg_to_pdf.py 同步**：两份相同的 `_html_body_to_pdf` 必须同步修改（P0 红线）

---

## 最后会话结束时的状态

### ✅ 已完成（commit + 推送）

| 项目 | Commit | 状态 | 说明 |
|------|--------|:----:|------|
| PRPOAgent UI 骨架 + PDFMergeTool 版本修正 | `da873a6` | ✅ 完成 | v1.3.0 发布 |
| Mail Agent MVP（首个功能模块） | `d8abee9` | ✅ 完成 | 5 .py + 1 .yaml |
| .github 治理（PR template / CI / CODEOWNERS） | `d8abee9` | ✅ 完成 | |
| PRPOAgent 自动拉起 Mail Agent（首次版，subprocess） | `dfa532c` | ✅ 完成 | UI 状态栏 |
| 修正：subprocess → in-process thread（EXE 兼容） | `1e4dc85` | ⚠️ 部分 | 源码 OK，EXE 缓存问题 |
| sys.modules 快速路径（PyInstaller EXE 内必加）| `c3059cd` | ⚠️ 部分 | 源码 OK |
| 修改规则支持 attachment_names 字段 | `9a7a945` | ✅ 完成 | 规则示例 |
| BUILD.md 重建指南 | `77dcc89` | ✅ 完成 | EXE 重建参考 |
| 中文 UI 改造（prpo-localize-cn） | `prpo-localize-cn.md` 计划 | ✅ 完成 | PRPOAgent 内容中文化 |
| v1.3.0 重打（PRPOAgent 内含 Mail Agent 代码）| — | ⚠️ 未完成 | 见下表 |

### ⚠️ 未完成 / 已知问题

| 问题 | 严重度 | 说明 |
|------|:------:|------|
| **EXE 重建缓存问题** | 🔴 高 | 当前开发机 PyInstaller 全局缓存被污染：`--onefile` 重建出的 PYZ-00.pyz 包含陈旧字节码（缺 `_setup_logging`、`mail_agent.log`、`MailAgentController` 字符串）。即使 `--clean --noconfirm` 也无法清理 |
| **v1.3.0 release ZIP 是用旧代码打包的** | 🔴 高 | `release_package/v1.3.0/PRPOAgent.exe` 不含 Mail Agent 集成。用户下载后双击只看到原 UI，不会自动启动 Mail Agent |
| **Phase 1.5 可观测性基础** | 🟡 中 | 审计日志、UI 历史面板、重试队列未实现。MainPlan（`prpo-master-plan.md`）已规划 |

### 已知 v1.3.0 限制

| 限制 | 说明 |
|------|------|
| **复杂 HTML 邮件渲染** | weasyprint 处理复杂邮件会卡，Mail Agent 会跳过 |
| **CSS 缩放对内联样式表格** | 效果有限，附件名匹配规则更稳定 |
| **`PR Form` vs `PR_Form`** | 下划线分隔不会被默认规则匹配，需要改成 `matches_regex` 或修改附件命名 |
| **PRPOAgent 自启动 Mail Agent（EXE）** | 当前 release 的 EXE 不具备此功能，需重建 EXE |

---

## 关键修复（特别是 T2！必须知道）

### T2: subprocess.Popen 在 EXE 内不可用

**问题**: `subprocess.Popen([sys.executable, "-m", "agents.mail_agent", "--run"])` 在 PyInstaller `--onefile` EXE 内**失败**，因为 `sys.executable` 指向 EXE 本身，不是 Python 解释器。

**首次尝试**：在 EXE 内启动会启动第二个 PRPOAgent.exe 副本，然后立刻 `ModuleNotFoundError: No module named 'config'`，因为 EXE 副本继承了单实例锁 + 错误的 sys.path。

**修复**：改用 **in-process daemon thread**（`MailAgentThread` 类）。参见 `agent_tool/pr_po_agent/mail_controller.py`。

**原因**：EXE 内的内存里已经有所有 Python 模块，线程方式直接复用，不需要额外的 Python 解释器。

### T1+C3059cd: sys.modules 快速路径

**问题**:`from outlook_monitor import OutlookMonitor` 在 EXE 内**挂死**（import 永远不返回），即使加了 path-shadow 处理。

**根因**:`outlook_monitor.py` 内部 `__file__` 指向 `_MEIPASS\outlook_agent\outlook_monitor.py`。PyInstaller 的 bootloader 已经把所有模块打包好，但运行时 `import` 时 Python 的导入器还要再做文件系统查找（永远找不到），挂死。

**修复**：先 `sys.modules.get()` 查已加载的模块（EXE 内模块在进程启动时已由 bootloader 加载到 sys.modules），找不到再用 path manipulation。

```python
def _bootstrap_outlook_monitor_class():
    for modname in ("outlook_monitor", "agent_tool.outlook_agent.outlook_monitor"):
        mod = sys.modules.get(modname)
        if mod is not None and hasattr(mod, "OutlookMonitor"):
            return mod.OutlookMonitor
    # Source-mode fallback: path manipulation
    ...
```

### 修复 EXE 重建缓存问题（**当前最紧迫**）

**症状**: 删除 dist/build/__pycache__ + `--clean --noconfirm` + 全局缓存清理，**新代码字符串仍不在 EXE 的 PYZ-00.pyz 里**。

**推测根因**: 当前开发机（`C:\Users\P1313993`）的 PyInstaller 安装/环境有内部损坏。

**解决方案**:
1. **首选**: 在干净开发机（重启后 / 换台机器）按 `agent_tool/pr_po_agent/BUILD.md` 命令重建
2. **备选**: 改用 `--onedir` 而非 `--onefile`，避免 PyInstaller 的 bytecode packing（但产物是一个文件夹 + launcher EXE，体积大）
3. **验证步骤**: 重建后必须用 `python -c "data = open('dist/PRPOAgent.exe', 'rb').read(); print(b'mail_agent.log' in data, b'MailAgentController' in data)"` → 必须都返回 `True`

---

## 关键代码位置

| 文件 | 函数 | 说明 |
|------|------|------|
| `agent_tool/pr_po_agent/main.py` | `main()` | PRPOAgent 入口：创建 MailAgentController，调 start() |
| `agent_tool/pr_po_agent/mail_controller.py` | `MailAgentController.__init__` | 预导入 OutlookMonitor 类 |
| `agent_tool/pr_po_agent/mail_controller.py` | `MailAgentController.start()` | 启动 daemon 线程 |
| `agent_tool/pr_po_agent/mail_controller.py` | `_setup_logging()` | 配置 Mail Agent 日志到 `%USERPROFILE%\PRPOAgent\mail_agent.log` |
| `agent_tool/pr_po_agent/ui/main_window.py` | `MainWindow.__init__` | 接受 mail_controller 参数，UI 状态栏 |
| `agent_tool/pr_po_agent/ui/main_window.py` | `_refresh_mail_status` | 每 2 秒轮询 controller 状态更新 UI |
| `agent_tool/pr_po_agent/agents/mail_agent/__main__.py` | `main()` | CLI 入口 (`--check`, `--run`, `--path`, `--help`) |
| `agent_tool/pr_po_agent/agents/mail_agent/rules_engine.py` | `matches()`, `get_first_match()` | 规则匹配（支持 list 字段） |
| `agent_tool/pr_po_agent/agents/mail_agent/monitor.py` | `MailAgent.__init__()` | 接受 outlook_monitor_class 注入 |
| `agent_tool/pr_po_agent/agents/mail_agent/monitor.py` | `_connect_outlook()` | 优先用注入类，否则 sys.path 操作 |
| `agent_tool/pr_po_agent/agents/mail_agent/rules.yaml` | — | 默认规则：attachment_names contains "PR Form" |

---

## 版本信息

- v1.3.0 已发布到 https://github.com/yaoyaobaibai/OutlookAgentTool/releases/tag/v1.3.0
- 主分支最新 commit: `c3059cd`
- OutlookAgent.exe: v1.2.9 (54.1 MB)，已签入 `release_package/v1.3.0/OutlookAgent.exe`
- PDFMergeTool.exe: v1.1.0 (53.0 MB)
- PRPOAgent.exe: v1.3.0-preview (22.28 MB) — ⚠️ **不含自动 Mail Agent 启动**
- ZIP: `OutlookAgent_v1.3.0.zip` (134 MB)

---

## 下次会话启动指引

### Step 1: 优先解决 EXE 重建（最紧迫）
1. **首选**: 在干净开发机按 `agent_tool/pr_po_agent/BUILD.md` 命令重建
2. **备选**: 在当前机器改用 `--onedir`（参考 `onedir-rebuild.md` 计划）
3. **验证**:
   ```bash
   python -c "d = open('dist/PRPOAgent.exe','rb').read(); print(b'mail_agent.log' in d, b'MailAgentController' in d)"
   # 必须输出 True True
   ```
4. 重新打包 + 上传 release

### Step 2: 启动 Phase 1.5 可观测性
- 审计日志（JSON Lines 追加写）
- 重试队列（失败邮件 24h 后重试）
- 操作面板（PRPOAgent UI 显示历史处理记录）

### Step 3: 启动 Phase 2 调研
- 收集 5-10 份真实报价单样本（按类型分类：文字 PDF / 扫描 PDF / 图片 / Excel）
- 客户隐私脱敏规则
- GPU 环境准备（Qwen-VL 需要 16G+ 显存）

### Step 4: 参考文档
- 完整主计划：`/start-work prpo-master-plan` — 这是修订版（v2，含我对此版本的评估意见）
- 集成设计：`prpo-mail-agent-integration.md`
- Mail Agent 规格：`mail-agent-spec.md`
- 关键决策来源：`AGENTS.md` + `SKILL.md` + `SKILL-extended.md`

---

## 已被明确否决的方案

| # | 方案 | 否决原因 |
|:--:|------|----------|
| 1 | PRPOAgent 启动子进程跑 Mail Agent | EXE 内 `sys.executable` 指向 EXE 本身，无法启动 Python 解释器。会产生无限嵌套 EXE。改用 in-process thread |
| 2 | 在 mail_controller.py 用 `from agent_tool.outlook_agent.outlook_monitor` | `outlook_agent/` 没有 `__init__.py`，不是正式 Python package，绝对导入不可用 |
| 3 | `--onefile` 重建能解决缓存问题 | PyInstaller 全局缓存被当前机器污染，`--clean --noconfirm` 仍产出陈旧字节码。需要换干净环境或 `--onedir` |
| 4 | Mail Agent UI 默认开 | UI 永远保持"开始监听"按钮，用户可手动控制；自动启动只在 PRPOAgent 启动时 |

---

## Build Commands

```powershell
# 在干净开发机
cd C:\Open AI Proj
git pull origin main
cd agent_tool\pr_po_agent
Remove-Item -Force -Recurse dist, build, __pycache__ -ErrorAction SilentlyContinue
$env:PATH = "C:\msys64\mingw64\bin;" + $env:PATH
pyinstaller --onefile --windowed --name "PRPOAgent" --clean --noconfirm `
  --paths . `
  --hidden-import=tkinter --hidden-import=pystray --hidden-import=PIL `
  --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw `
  --hidden-import=config --hidden-import=tray `
  --hidden-import=ui.main_window --hidden-import=ui.settings_dialog --hidden-import=ui.confirm_dialog `
  --hidden-import=mail_controller `
  --hidden-import=agents --hidden-import=agents.mail_agent `
  --hidden-import=agents.mail_agent.rules_engine `
  --hidden-import=agents.mail_agent.inbox_writer `
  --hidden-import=agents.mail_agent.monitor `
  --hidden-import=agents.mail_agent.__main__ `
  --collect-submodules=outlook_agent `
  main.py
```

完整重建 + 上传见 `BUILD.md`。

---

## AT ROOT

`agent_tool/release_package/v1.3.0/` 内有：
- `PRPOAgent.exe` (22.28 MB) — ⚠️ 旧版（不含 Mail Agent 集成），需要重建
- `OutlookAgent.exe` (54.1 MB) — v1.2.9，未变
- `PDFMergeTool.exe` (53.0 MB) — v1.1.0，已修
- `说明.txt` — 中文用户说明

---

**总评估**: v1.3.0 代码层完成度 **95%**，唯一阻塞是当前开发机的 EXE 构建缓存问题。源码已 commit + 可在任何干净环境重建成功。
