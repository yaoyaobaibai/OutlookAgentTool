# OutlookAgent 项目指南

> 基于 Andrej Karpathy 编码原则 + 本项目血泪教训

## 1. 编码前思考
- 不要假设。不确定时显式写出假设
- 困惑时停下来，请求澄清
- 有更简单的方案就说

## 2. 简洁优先
- 不写"以后可能用"的代码
- **日志用英文 ASCII**：--windowed EXE 中文全变 ??
- 自问："高级工程师会说这过度设计吗？"

## 3. 精准修改

### 必须先问再改（不问不动手）
- 用户让你改 A → 不要顺便改 B、C、D
- 涉及 2 个以上文件 → 先说方案，等用户确认
- 改变现有函数的签名/行为 → 先说方案，等用户确认
- 不确定根因 → 先说你的分析，不要直接改

### 禁止顺手改
- 改 bug 时发现"可以更好" → 只修这个 bug，优化另开任务
- 路过一段代码有小问题 → 忽略，不在本次任务范围内
- 重构 → 除非用户明确要求，否则禁止

### 改完必验
- 改完立即 `python -m py_compile`
- 改完立即 read 回读确认内容正确

## 4. 目标驱动执行
- 强标准：日志出现 `CJK font registered ✓` 而非 "修复中文乱码"

## 项目结构
- agent_tool/outlook_agent/ → OutlookAgent.exe
- agent_tool/pdf_merge_tool/ → PDFMergeTool.exe
- agent_tool/release_package/ → 版本发布
- .sisyphus/ → 项目文档

## ⚠️ 关键陷阱
- _html_body_to_pdf 在 attachment_handler.py 和 msg_to_pdf.py 各有一份，修一个必须同步修另一个
- --windowed EXE 吞 stderr → logger.warning 是唯一可见输出
- 禁止 print() 中文 → cp1252 崩溃
- 动态路径导入 PyInstaller 可能追踪不到 → 需 --hidden-import
- 构建前 kill 旧进程，确认文件大小刷新，重新 ZIP

## 5. 会话管理
- **Handoff 时机**：遇到自然断点（需要测试、等待用户确认、API 余额不足）时生成临时 handoff（标记 session 编号）；会话结束时生成最终 handoff 合并或取代临时版本
- **SKILL 更新**：会话即将结束时，Agent 主动输出本次新增经验表格（错误签名→修复、决策、否决方案），格式为 Markdown 表格，供用户审查。用户确认后，Agent 分区追加到 SKILL-extended.md（不重写全文）
