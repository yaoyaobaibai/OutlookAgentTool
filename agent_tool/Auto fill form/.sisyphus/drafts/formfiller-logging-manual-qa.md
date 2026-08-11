# FormFiller 日志增强 - 手动验证手册

> 用途：人工验证 FormFiller 日志增强功能的正确性（文件日志 + GUI 日志区桥接 + 旧日志清理）。
> 适用版本：logging_setup.py + form_filler.py 日志增强改动后。
> 预计耗时：5-10 分钟。

---

## 1. 运行方式

1. 打开终端（PowerShell），进入项目目录：
   ```powershell
   cd C:\Users\p1325970\AILearn\Auto fill form
   ```
2. 用显式 Python 路径启动程序（本机裸 `python` 命令是静默 stub，必须用此路径）：
   ```powershell
   C:\Users\p1325970\AppData\Local\Python\bin\python.exe form_filler.py
   ```
3. 程序启动时**自动**完成以下动作，无需任何手动操作：
   - **不创建日志文件**（日志文件在每次点击"开始执行"时才创建，秒级命名，每次执行一个独立文件）
   - `cleanup_old_logs(days=30)` 清理 30 天前的旧日志
   - 挂接 GuiLogBridge，将 logging 记录桥接到 GUI 底部日志区
4. 点击"开始执行"运行一个工作流，此时才会创建本次执行的日志文件：
   - `configure_logging()` 以**秒级文件名** `app-YYYYMMDD-HHMMSS.log` 配置 root logger，写入程序目录下的 logs 文件夹（utf-8 编码），返回本次文件路径
   - 若同一秒内多次执行（冲突），自动追加 `-1` / `-2` 后缀（如 `app-20260810-151530-1.log`）
   - 每次执行**移除旧的 file handler 并新建本次文件**（swap 语义，root logger 上最多 1 个文件 handler）
   - 引擎日志写入 `=== 会话开始: <工作流名> ===` 会话标记

---

## 2. 预期日志内容（GUI 底部日志区）

### 2.1 启动横幅

**启动时**（`_create_widgets()` 后）日志区第一行显示**占位提示**，格式如下：

```
[i] 日志系统就绪（文件将在执行开始时创建）
```

**每次点击"开始执行"时**日志区显示本次执行的**秒级日志文件路径**，格式如下：

```
[i] 日志文件: <程序目录>/logs/app-20260810-151530.log
```

- `<程序目录>` 为程序所在目录（开发模式为项目根目录；打包 exe 后为 exe 同目录）
- 文件名中的日期为**当日日期**（YYYYMMDD），时间戳为**执行开始的时刻**（HHMMSS），每次执行一个独立文件
- 同一秒多次执行时文件名带 `-1` / `-2` 后缀（如 `app-20260810-151530-1.log`）

> 若执行时出现 `[!] 日志配置失败: ...`，说明日志配置异常，见第 6 节故障排查。

### 2.2 运行工作流后的新增日志（步骤 / 阶段 / 字段回调）

选择工作流并点击执行后，应看到以下格式的行：

```
>>> 步骤: login
>>> 步骤: navigation
>>> 步骤: stage:sso_login
>>> 步骤: stage:create_gr
>>> 处理字段: Order
```

对应回调（form_filler.py）：
- `>>> 步骤: {step}` —— 步骤开始（`_on_step_start`，step 为 `login` / `navigation` / `stage:xxx` 等）
- `<<< 步骤完成: {step}` —— 步骤完成（`_on_step_end`）
- `>>> 处理字段: {field_name}` —— 字段开始（`_on_field_start`）
- `  {field_name}: ✓ 成功 — {message}` / `✗ 失败` —— 字段结束（`_on_field_end`）

### 2.3 引擎 DEBUG 桥接日志（含 `[DEBUG]` 前缀）

由 GuiLogBridge 将 workflow_engine 的 logging 记录转发到 GUI 日志区，格式为 `[{LEVELNAME}] {message}`：

```
[DEBUG] Navigation step 1: 'goto' (optional=False)
[DEBUG] Filled '6000017449' into selector '#...'
```

常见引擎日志消息示例：
- `Navigating to login URL: ...`（INFO 级）
- `Navigation step %d: '%s' (optional=%s)`（DEBUG 级）
- `Filled '%s' into selector '%s'`（DEBUG 级）

> **注（预期行为，非缺陷）**：由于 GUI 对引擎日志开 DEBUG 全量，字段填充的 debug 行（如 `Filled ...`）会与字段回调日志（`>>> 处理字段: ...`）**重复显示**，二者内容角度不同，属预期设计。

---

## 3. 文件日志验证

1. 点击执行后，复制执行横幅中显示的本次日志文件路径（秒级）。
2. 打开该文件（程序目录下 `<程序目录>/logs/app-YYYYMMDD-HHMMSS.log`）。
3. 确认：
   - 文件名格式为 `app-YYYYMMDD-HHMMSS.log`，日期为**当日**，时间戳为**本次执行开始时刻**
   - **每次执行产生独立文件**（秒级命名）；同一秒内多次执行则产生 `app-YYYYMMDD-HHMMSS-1.log`、`-2.log` 等冲突后缀文件
   - 文件存在且持续增长（运行工作流后有明显新增内容）
   - 文件内容仅包含 **logging 模块记录**（handler 操作日志 + 引擎日志）；GUI 日志区的 `[i]`/`[?]`/`[!]` 横幅与状态行（`self._log`）**不会**写入文件
4. 用支持 **utf-8** 的编辑器打开（推荐 VS Code / Notepad++，默认编码选 UTF-8），确认**中文内容完好、无乱码**（FileHandler 已强制 `encoding='utf-8'`）。
5. 文件内容每行应包含：时间戳、级别、logger 名、消息，格式如下（对应 `LOG_FORMAT`）：
   ```
   2026-08-10 18:15:00,123 | INFO     | workflow_engine | Navigating to login URL: ...
   2026-08-10 18:15:01,456 | DEBUG    | workflow_engine | Navigation step 1: 'goto' (optional=False)
   ```
6. 文件首行应含会话标记（`=== 会话开始: <工作流名> ===`，由引擎 logger 写入）。

> 打包 exe 后 logs 文件夹在 exe 同目录下

---

## 4. 清理验证

1. 打开程序目录下的日志文件夹（`<程序目录>/logs/`），列出 `app-*.log` 文件。
2. 确认：
   - logs 文件夹中**只有近期日志**（30 天前的 `app-*.log` 会在启动时被 `cleanup_old_logs(days=30)` 自动删除）
3. **二次启动**程序（重新执行第 1 节命令），再次查看日志目录：
   - 确认**当日日志文件不被误删**（当日 mtime 距今 < 30 天，应保留）
   - 确认**再次执行后创建新的独立文件**（新秒级时间戳，而非复用旧文件——swap 语义：每次执行移除旧 file handler、新建本次文件，root logger 上最多 1 个文件 handler）

---

## 5. 打包验证（可选但推荐）

1. 运行打包脚本（`执行打包.bat`）生成 exe。
2. 运行 `dist/FormFiller/FormFiller.exe`。
3. 确认：
   - GUI 日志区启动时正常显示 `[i] 日志系统就绪（文件将在执行开始时创建）` 占位提示，执行时显示 `[i] 日志文件: ...` 横幅
   - 日志文件**写入 exe 同目录下的 logs 文件夹**（`<程序目录>/logs/app-YYYYMMDD-HHMMSS.log`），确认 logs 文件夹在 exe 同目录（**非** `_MEIPASS` 解压目录）

---

## 6. 故障排查

| 现象 | 可能原因 | 处理 |
|------|---------|------|
| GUI 日志区无启动占位提示 `[i] 日志系统就绪（文件将在执行开始时创建）` | `GuiLogBridge` 未在 `_create_widgets()` 之后挂接，`log_text` 尚不存在导致 `_log` 失败 | 检查 form_filler.py：日志配置代码必须在 `_create_widgets()` / `_init_workflow_selector()` **之后**（`self.log_text` 依赖它） |
| 执行时无 `[i] 日志文件: ...` 横幅 | `configure_logging()` 未在 `_start_execution` 的守卫通过后调用，或执行被前置校验拦截 | 检查 form_filler.py `_start_execution`：`configure_logging()` 必须在守卫通过后、横幅打印前调用（约 line 587） |
| 日志文件中文乱码 | 用非 utf-8 编码（如系统 ANSI/GBK）打开了文件 | 改用支持 utf-8 的编辑器打开；FileHandler 已强制 `encoding='utf-8'`，文件本身编码正确 |
| GUI 崩溃报 `TclError` | 日志区写入发生在 Tk 主循环销毁后 | 正常不会发生：GuiLogBridge.emit() 已 `try/except` 吞掉全部异常（post-destroy TclError 防护） |
| 裸 `python` 命令无任何输出 | 本机 `python` 是静默 stub | 必须用 `C:\Users\p1325970\AppData\Local\Python\bin\python.exe` 显式启动 |

---

## 验证结果反馈

完成以上 1-4 项（建议含第 5 项）后，请将验证结果（通过项 / 失败现象与截图）反馈给开发（Atlas）。
