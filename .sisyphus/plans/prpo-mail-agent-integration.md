# PRPOAgent 集成 Mail Agent - v1.3.0 完整版

> 创建日期：2026-07-11
> 关联规格：`.sisyphus/drafts/prpo-mail-agent-integration.md`
> 预计工期：1-2 小时
> 入口：`/start-work`

---

## TL;DR

> **目标**：让 `PRPOAgent.exe` 启动时自动拉起 Mail Agent 子进程，托盘退出时自动停止
> **发布目标**：v1.3.0（完整版，给用户前必须完成）
> **关键约束**：subprocess 必须 `creationflags=0x08000000`（不弹 cmd 窗口）；不修改 outlook_agent；日志英文 ASCII

---

## Context

### 背景
- v1.3.0 还没发给用户（PRPOAgent + Mail Agent 独立版）
- 用户需求：希望 PRPOAgent 启动时自动拉起 Mail Agent，不要每次手动开
- 已有设计文档：`.sisyphus/drafts/prpo-mail-agent-integration.md`

### 现状
- PRPOAgent.exe 是托盘 + tkinter 主窗口（system tray）
- Mail Agent 是独立 CLI：`python -m agents.mail_agent --run`
- 两者用相同的 v1.3.0 EXE
- 修 Mail Agent 重启 PRPOAgent 才能让它们协同

---

## Work Objectives

### Core Objective
PRPOAgent.exe 启动时自动拉起 Mail Agent 子进程；托盘退出时自动停止 Mail Agent。

### Concrete Deliverables
- `agent_tool/pr_po_agent/mail_controller.py` — Mail Agent 进程管理类
- `agent_tool/pr_po_agent/main.py` — 启动 + 退出时调 Mail Agent 控制器
- `agent_tool/pr_po_agent/ui/main_window.py` — 主窗口底部加状态栏
- `agent_tool/release_package/v1.3.0/PRPOAgent.exe` — 重建含新代码
- `agent_tool/release_package/v1.3.0/OutlookAgent_v1.3.0.zip` — 重新打包

### Definition of Done
- [ ] 双击 PRPOAgent.exe → 30 秒内 Mail Agent 子进程在任务管理器出现
- [ ] 主窗口底部状态栏显示 "邮件监听中" / "已停止"
- [ ] 关闭托盘 → Mail Agent 进程消失（无残留 zombie）
- [ ] 任务管理器有且仅有 1 个 Mail Agent 进程（不能多个 PRPOAgent 拉起多个）
- [ ] PRPOAgent 单实例锁依然有效（多窗口情况下不会重复启动 Mail Agent）
- [ ] 关闭后重启 PRPOAgent → Mail Agent 也会重新拉起
- [ ] OutlookAgent.exe / PDFMergeTool.exe 不受影响
- [ ] py_compile 全部通过
- [ ] 按 v1.3.0 完整版重打 EXE + ZIP + GitHub Release

### Must Have
- Mail Agent 通过 subprocess.Popen 拉起，`creationflags=0x08000000`（P0）
- 进程管理：start / stop / is_running 三个方法
- PRPOAgent 退出时优雅停止 Mail Agent（terminate + 5s timeout + kill）
- 主窗口底部加状态标签 + 启动/暂停按钮

### Must NOT Have
- ❌ 不修改 outlook_agent 任何代码
- ❌ 不修改 rules.yaml
- ❌ 不改 Mail Agent 内部逻辑
- ❌ 不做实时规则编辑
- ❌ 不做邮件通知弹窗
- ❌ 不在子进程做 print（--windowed EXE 中文会变 ??）

---

## Verification Strategy

### Test Decision
- **基础设施**：NO（项目无单元测试）
- **自动测试**：NO
- **手动验证**：必须
  - 启动 EXE → 任务管理器看进程
  - 主窗口看状态文字
  - 关闭托盘 → 进程消失
  - 日志检查英文 + 无残留

### QA Policy
每任务完成后立即验证：
- py_compile
- 实测启动 EXE（手动）
- 任务管理器确认子进程

---

## Execution Strategy

### 4 个任务串行

```
T1: mail_controller.py → T2: main.py 集成 → T3: UI 状态 → T4: 重打 EXE
```

- T1 是基础，必须先做完
- T2 改 main.py，依赖 T1
- T3 改 UI，可与 T2 并行（不同文件）
- T4 必须在 T1-T3 都成功后

### 安全护栏

1. **修改前备份**：复制现有 main.py 到 backup
2. **subprocess 隐藏窗口**：必须 `creationflags=0x08000000`
3. **不破坏现有 PRPOAgent UI**：T3 只追加，不改现有 widget
4. **单实例锁依然有效**：所有 Mail Agent 启动都通过唯一入口

---

## TODOs

- [x] 1. 创建 mail_controller.py（Mail Agent 进程管理类）

  **What to do**:
  - 新文件 `agent_tool/pr_po_agent/mail_controller.py`
  - 类 `MailAgentController`
  - 方法：
    - `start()` — 检查未运行则 Popen
    - `stop()` — terminate + wait 5s + kill
    - `is_running()` — poll() 检查
    - `restart()` — stop + start
  - subprocess.Popen 参数：
    ```python
    subprocess.Popen(
        [sys.executable, "-m", "agents.mail_agent", "--run"],
        cwd=<pr_po_agent_dir>,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=0x08000000,
    )
    ```
  - 所有日志英文 ASCII

  **Acceptance Criteria**:
  - `python -m py_compile` PASS
  - MailAgentController().start() 不抛异常
  - MailAgentController().is_running() 返回 True/False 正确
  - MailAgentController().stop() 在 is_running=False 时不抛

  **QA Scenarios**:
    ```
    Scenario: controller start/stop cycle
      Tool: Bash
      Steps:
        1. cd C:\Open AI Proj\agent_tool\pr_po_agent
        2. python -c "
    import sys; sys.path.insert(0, '.')
    from mail_controller import MailAgentController
    c = MailAgentController()
    c.start()
    import time; time.sleep(3)
    print('is_running:', c.is_running())
    c.stop()
    print('after stop is_running:', c.is_running())
    "
      Expected: 第一次 is_running=True, after stop is_running=False
    ```

---

- [x] 2. 修改 main.py：启动 PRPOAgent 时拉起 Mail Agent，退出时停止

  **What to do**:
  - 在 `main.py` 的 `main()` 函数中：
    - 创建 `MailAgentController()` 实例
    - 启动后调 `controller.start()`
    - 修改 `_on_close`（或 root.protocol("WM_DELETE_WINDOW") 的 handler）调 `controller.stop()`
  - 加 import 路径处理（与 T1 同）

  **Acceptance Criteria**:
  - `python -m py_compile` PASS
  - 启动 PRPOAgent → Mail Agent 出现
  - 关闭 PRPOAgent → Mail Agent 消失
  - 不影响单实例锁

  **QA Scenarios**:
    ```
    Scenario: PRPOAgent lifecycle pulls Mail Agent along
      Tool: 手动 + tasklist
      Steps:
        1. 启动 PRPOAgent.exe
        2. tasklist /FI "IMAGENAME eq python.exe"
        3. 关闭托盘
        4. tasklist /FI "IMAGENAME eq python.exe"
      Expected: 步骤 2 有 python 进程（Mail Agent），
                 步骤 4 没有（关闭被清理）
    ```

---

- [x] 3. 修改 ui/main_window.py：状态栏 + 启动/暂停按钮

  **What to do**:
  - 在主窗口底部加状态栏（Frame 包含 Label + 按钮）
  - 状态栏组件：
    - 状态标签（自动刷新）："● 邮件监听中" / "○ 已停止"
    - 启动按钮："启动监听"
    - 停止按钮："停止监听"
  - 定时刷新（用 `root.after(2000, ...)` 轮询 is_running）
  - 按钮调 controller.start() / controller.stop()
  - 所有英文（按钮文本、状态文字）

  **Acceptance Criteria**:
  - `python -m py_compile` PASS
  - 状态栏在主窗口可见
  - 启动后状态文字变化
  - 停止后状态文字变化
  - 不影响现有其他 widget

  **QA Scenarios**:
    ```
    Scenario: UI status updates
      Tool: 手动
      Steps:
        1. 启动 PRPOAgent.exe
        2. 打开主窗口（托盘 → Show Window）
        3. 观察底部状态栏：应显示"邮件监听中"
        4. 点击"停止监听"按钮
        5. 2 秒内状态应变为"已停止"
      Expected: 状态文字根据 controller 状态变化
    ```

---

- [x] 4. 重建 PRPOAgent.exe + 重打包 + 上传 v1.3.0 完整版 Release

  **What to do**:
  - 清理 `dist/` 和 `build/`
  - PyInstaller 命令（参考 `agent_tool/pr_po_agent/BUILD.md`）
  - 复制新 EXE 到 `agent_tool/release_package/v1.3.0/`
  - 重打 `OutlookAgent_v1.3.0.zip`
  - `gh release upload` 上传新 ZIP（覆盖 v1.3.0 release 资源）
  - 在 release notes 加 changelog 一行："PRPOAgent now auto-launches Mail Agent"

  **Acceptance Criteria**:
  - `dist/PRPOAgent.exe` 大小 ~22-23 MB（包含 Mail Agent + 新集成代码）
  - ZIP 大小 ~135 MB
  - 上传后 SHA256 不同（与前一版）

  **QA Scenarios**:
    ```
    Scenario: ZIP upload verified
      Tool: gh CLI
      Steps:
        1. gh release view v1.3.0 --json assets
      Expected: OutlookAgent_v1.3.0.zip 存在，新 size
    ```

---

## Final Verification Wave

- [x] F1. 计划合规审计
  - [ ] Mail Agent 子进程有 creationflags=0x08000000
  - [ ] outlook_monitor.py 未修改
  - [ ] 日志全英文 ASCII
  - [ ] 4 个任务全部完成
  - [ ] 任务管理器进程检查通过

- [x] F2. 代码质量
  - [ ] py_compile 全部通过
  - [ ] `git grep "subprocess.*Popen" agent_tool/pr_po_agent/` 有 creationflags

- [ ] F3. 端到端验证
  - [ ] PRPOAgent.exe 启动 → Mail Agent 出现（任务管理器）
  - [ ] PRPOAgent.exe 退出 → Mail Agent 消失
  - [ ] 状态栏显示正确
  - [ ] 按钮可控制启停
  - [ ] 单实例锁依然有效

---

## Commit Strategy

| 任务 | Commit Message |
|------|---------------|
| 1 | `feat(prpo): add MailAgentController for process management` |
| 2 | `feat(prpo): auto-launch Mail Agent in main.py lifecycle` |
| 3 | `feat(prpo): show Mail Agent status in main window` |
| 4 | `chore(prpo): rebuild PRPOAgent.exe with Mail Agent auto-launch` |

---

## Success Criteria

- ✅ PRPOAgent.exe 双击 → Mail Agent 自动启动（任务管理器可见）
- ✅ 关闭 PRPOAgent → Mail Agent 也关闭
- ✅ 状态栏 + 按钮可控制
- ✅ v1.3.0 Release 资产已更新
- ✅ 代码测试 / py_compile 全 PASS
- ✅ 日志无中文
- ✅ outlook_monitor.py 未修改
- ✅ 单实例锁依然有效

## 不在范围（明确排除）

- ❌ 不修改 Mail Agent 内部逻辑
- ❌ 不做实时 rules.yaml 编辑
- ❌ 不做新邮件通知弹窗
- ❌ 不做任务列表接入（已在 PRPOAgent UI 中预留）
- ❌ 不写新模块（Extract / Decision 都不在 v1.3.0 范围）
