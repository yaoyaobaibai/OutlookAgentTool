# FormFiller EXE 打包计划

## TL;DR

> **快速总结**: 使用 PyInstaller 将 FormFiller (Playwright 自动化填表 GUI 工具) 打包为 Windows EXE。利用现有的 `执行打包.bat` 脚本，`--onedir` 文件夹模式输出。
>
> **交付物**:
> - `dist/FormFiller/FormFiller.exe` — 主程序
> - `dist/FormFiller/` — 运行时依赖文件夹 (workflows, handlers, JSON 配置等)
> - `启动表单填充工具.bat` — 必须配合使用的启动脚本
>
> **预估工作量**: 小型 (30分钟)
> **并行执行**: 否 (单线程打包)
> **关键路径**: 运行打包脚本 → 验证输出

---

## Context

### 原始需求
用户希望将此 Python 程序 (Playwright + tkinter GUI 自动化填表工具) 打包为 Windows 可执行文件 (.exe)，方便在没有 Python 环境的机器上运行。

### 访谈摘要
**关键讨论**:
- 程序默认使用用户已安装的 Chrome 浏览器 (`channel="chrome"`)，无需捆绑 Chromium
- 使用 `--onedir` 文件夹模式输出
- 保留 `--console` 控制台窗口（便于调试和查看日志）
- 直接使用现有 `执行打包.bat` 脚本，不做代码改造

**环境现状**:
| 项目 | 状态 |
|------|------|
| Python 3.14.4 | ✅ 已安装 |
| PyInstaller 6.21.0 | ✅ 已安装 |
| Playwright 1.61.0 | ✅ 已安装 |
| Playwright 浏览器 (chromium) | ❌ 未安装 (可选，用于 Chromium 模式) |
| 现有打包脚本 | ✅ 可用 |

**路径加载分析**:
- 所有资源加载 (`workflows/`, `attachment_config.json` 等) 使用 CWD 相对路径
- 需要 `启动表单填充工具.bat` 设置工作目录 (`cd /d "%~dp0"`)
- **直接双击 EXE 会导致资源加载失败** — 必须通过启动脚本运行

### Metis 审查
**识别的问题** (已处理):
- **关键**: 启动脚本依赖 — `启动表单填充工具.bat` 必须随 EXE 分发，用户不能用双击方式运行 EXE
- **关键**: 打包后验证 — 不仅检查 EXE 存在，还要验证 workflows 被正确打包
- **中等**: `validate_workflow.py` 动态 importlib 加载 — 通过 `--add-data "workflows;workflows"` 已覆盖
- **中等**: pandas 延迟导入 — `--hidden-import pandas` 已在脚本中
- **低**: `--console` vs `--noconsole` — 用户选择保留 console

---

## Work Objectives

### 核心目标
将 `form_filler.py` 及其所有依赖打包为 Windows EXE，确保在目标机器上能正常运行。

### 具体交付物
- `dist/FormFiller/FormFiller.exe` — 可执行文件
- `dist/FormFiller/` — 完整的运行时目录 (workflows, handlers, JSON等)
- `dist/启动表单填充工具.bat` — 启动脚本 (复制版)

### 完成标准
- [ ] `dist/FormFiller/FormFiller.exe` 文件存在
- [ ] `dist/FormFiller/workflows/` 包含所有工作流目录 (csms_create_proposal, gracubuy_create_gr, gracubuy_login)
- [ ] `dist/FormFiller/attachment_config.json` 存在
- [ ] `dist/FormFiller/workflows/settings.json` 可写入 (启动后生成)
- [ ] `dist/启动表单填充工具.bat` 存在
- [ ] 没有多余文件混入 (`auto_create_proposal.py`, `tests/`, `_archive/`, `GR-Acubuy/`, `html/`)

### 必须包含
- `form_filler.py` + `workflow_manager.py` + `workflow_engine.py`
- `handlers/` 全部 7 个处理器模块
- `workflows/` 全部 3 个工作流配置
- `attachment_config.json` 配置文件
- `启动表单填充工具.bat` 启动脚本

### 不必包含 (Guardrails)
- 不捆绑 Chromium 浏览器（使用用户已安装的 Chrome）
- 不做代码改造（不添加 `resource_path()` 等）
- 不切换到 `--onefile` 单文件模式
- 不添加图标、安装程序、代码签名
- 不安装 Playwright 浏览器（除非 Chromium 模式需要）
- 不修改源文件 (`auto_create_proposal.py` 等保持不变)

---

## Verification Strategy

### 测试决策
- **自动测试**: 否 (打包任务，非开发任务)
- **Agent 验证**: 每次任务都必须包含验证步骤

### QA 策略
每次任务完成后，通过 Bash/PowerShell 命令直接验证交付物。

---

## Execution Strategy

### 执行波次

仅有一个波次 (简单线性流程):

```
Wave 1 (顺序执行):
├── Task 1: 安装 Playwright 浏览器 (可选)
├── Task 2: 执行打包脚本
├── Task 3: 验证打包输出
├── Task 4: 复制启动脚本到 dist
└── Task 5: 最终完整性验证
```

---

## TODOs

- [x] 1. (可选) 安装 Playwright Chromium 浏览器 — **已跳过**: 默认使用用户Chrome, 无需安装

  **做什么**:
  - 运行 `playwright install chromium` 下载 Chromium 浏览器
  - 如果需要使用 GUI 中的 "Chromium (需下载)" 模式，则必须执行此步骤
  - **注意**: 默认使用 "Google Chrome" 模式（用户已安装的 Chrome），此步骤可选

  **不做**:
  - 不将浏览器打包进 EXE（仅在本地安装供开发测试使用）

  **验证**:
  - [-] 已跳过 (用户确认使用系统Chrome, 不需要Chromium模式)

  **提交**: 否

- [x] 2. 执行打包 — 运行 `执行打包.bat`

  **做什么**:
  - 运行 `执行打包.bat` 脚本
  - 脚本会自动:
    1. 清理旧的 `build/` 和 `dist/` 目录
    2. 调用 PyInstaller，参数包括:
       - `--onedir` 文件夹模式
       - `--console` 保留控制台窗口
       - `--add-data "form_config.json;."`
       - `--add-data "attachment_config.json;."`
       - `--add-data "workflows;workflows"`
       - `--add-data "handlers;handlers"`
       - 所有 handler 模块的 `--hidden-import`
       - `workflow_manager`, `workflow_engine` 的 `--hidden-import`
       - 排除 torch/tensorflow/onnxruntime 等大型库
    3. 输出到 `dist/FormFiller/`
  - 打包预计 3-8 分钟

  **不做**:
  - 不修改打包脚本内容
  - 不切换到 `--onefile` 模式

  **验证**:
  - [ ] 打包脚本 exit code = 0
  - [ ] `Test-Path -LiteralPath "dist/FormFiller/FormFiller.exe"` 返回 True
  - [ ] 文件大小 > 10MB (确保不是空文件)

  **提交**: 否

- [x] 3. 验证打包完整性 — 检查所有必需文件

  **做什么**:
  - 逐一验证打包输出目录中的关键文件
  - 确保没有遗漏

  **验证**:
  - [ ] `Get-ChildItem -LiteralPath "dist/FormFiller/workflows" -Directory | ForEach-Object { $_.Name }` 应包含:
    - `csms_create_proposal`
    - `gracubuy_create_gr`
    - `gracubuy_login`
  - [ ] `Test-Path -LiteralPath "dist/FormFiller/attachment_config.json"` 返回 True
  - [ ] `Test-Path -LiteralPath "dist/FormFiller/handlers"` 返回 True
  - [ ] `Test-Path -LiteralPath "dist/FormFiller/workflows/settings.json"` 应不存在 (首次启动后创建)
  - [ ] `Get-ChildItem -LiteralPath "dist/FormFiller" -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'auto_create_proposal|^tests$|^_archive$|^GR-Acubuy$|^html$' }` 应返回空 (无污染文件)

  **提交**: 否

- [x] 4. 复制启动脚本到 dist 目录

  **做什么**:
  - 将 `启动表单填充工具.bat` 复制到 `dist/` 目录（与 `dist/FormFiller/` 文件夹平级）
  - 此启动脚本通过 `cd /d "%~dp0"FormFiller` + `FormFiller.exe` 确保工作目录正确

  **重要**:
  - 用户必须通过此启动脚本运行程序
  - **直接双击 `FormFiller.exe` 会导致工作目录错误，资源加载失败！**

  **验证**:
  - [ ] `Test-Path -LiteralPath "dist/启动表单填充工具.bat"` 返回 True
  - [ ] 验证脚本内容: `Get-Content "dist/启动表单填充工具.bat"` 包含 `cd /d` 和 `FormFiller.exe`

  **提交**: 否

- [x] 5. 最终验证 — 确保一切就绪

  **做什么**:
  - 综合检查所有交付物
  - 汇总打包后的目录结构

  **验证**:
  - [ ] 打包总大小: `(Get-ChildItem -LiteralPath "dist/FormFiller" -Recurse | Measure-Object -Property Length -Sum).Sum` 应在 50-200MB 之间
  - [ ] 目录结构展示: `Get-ChildItem -LiteralPath "dist" -Recurse -Depth 1 | Format-Table Name`
  - [ ] 确认 `启动表单填充工具.bat` 路径正确:
    ```powershell
    Get-Content "dist/启动表单填充工具.bat"
    # 应输出:
    # @echo off
    # chcp 65001 >nul
    # cd /d "%~dp0"
    # FormFiller\FormFiller.exe
    # pause
    ```

  **提交**: 否

---

## 最终验证波次

- [x] F1. **交付物核对** — 检查所有完成标准

  逐项核对:
  - [x] `dist/FormFiller/FormFiller.exe` 存在且大小合理 (26.94 MB)
  - [x] `dist/FormFiller/workflows/` 包含 3 个工作流
  - [x] `dist/FormFiller/attachment_config.json` 存在
  - [x] `dist/启动表单填充工具.bat` 存在且内容正确
  - [x] 无污染文件 (auto_create_proposal.py, tests/ 等未混入)

  **结果**: ✅ 通过

- [x] F2. **使用说明编写** — 告知用户怎样运行打包后的程序

  ## 如何使用打包后的程序

  ### 运行方式
  1. 将整个 `dist/` 文件夹复制到目标机器（任意位置均可）
  2. 确保目标机器已安装 **Chrome 浏览器** (或 Edge)
  3. 打开 `dist/` 文件夹，**双击 `启动表单填充工具.bat`**
  4. 在程序的 "Browser" 下拉菜单中保留默认的 **"Google Chrome"**
  5. 配置好工作流和其他参数后点击 "Run"
  6. ⚠️ **注意：不要直接双击 `FormFiller.exe`！** 必须通过启动脚本运行

  ### 目录结构说明
  ```
  dist/
  ├── 启动表单填充工具.bat   ← 双击这个启动
  └── FormFiller/
      ├── FormFiller.exe     ← 主程序（不要直接运行）
      ├── workflows/         ← 工作流配置（3个）
      ├── handlers/          ← 处理器模块（7种）
      ├── attachment_config.json
      └── ... (其他依赖文件)
  ```

  ### 注意事项
  - **Chrome 浏览器必须已安装** — 程序使用 `channel="chrome"` 调用系统 Chrome
  - 如需使用 "Chromium (需下载)" 模式，需先在目标机器运行 `playwright install chromium`
  - 防病毒软件可能误报 — PyInstaller 打包的程序常见现象，添加信任即可
  - 程序总大小约 392MB (因包含 pandas/numpy/scipy/playwright 等完整运行环境)
  - 首次启动时会自动创建 `workflows/settings.json` 保存上次使用的工作流

---

## Commit Strategy

- 无提交 (打包操作不生成代码变化)

---

## Success Criteria

### 验证命令
```powershell
# 检查 exe 是否存在
Test-Path -LiteralPath "dist/FormFiller/FormFiller.exe"

# 检查 workflows
Get-ChildItem -LiteralPath "dist/FormFiller/workflows" -Directory | Select-Object Name

# 检查启动脚本
Test-Path -LiteralPath "dist/启动表单填充工具.bat"
```

### 最终检查清单
- [x] `dist/FormFiller/FormFiller.exe` 存在且可执行 (26.94 MB)
- [x] 3 个工作流配置均已打包 (csms_create_proposal, gracubuy_create_gr, gracubuy_login)
- [x] handlers 模块完整 (7个处理器 + base + __init__)
- [x] 启动脚本就位 (dist/启动表单填充工具.bat)
- [x] 无多余文件污染
- [x] 分发说明已明确
