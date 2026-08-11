# GR-Acubuy SSO 登录验证手册（测试版）

> 用途：在真实 Singtel iValua Acubuy 环境中验证 GR-Acubuy 测试版工作流的 SSO 登录流程。
> 对应工作流：`GR-Acubuy Create GR (TEST - 不提交)`（workflows/gracubuy_gr_flow_test/workflow.json，v1.1.0）
> 注意：本手册只用于人工执行验证，程序不会自动提交任何 GR 记录。

## 1. 运行方式

- 启动命令（使用真实 Python 解释器）：

  ```
  C:\Users\p1325970\AppData\Local\Python\bin\python.exe form_filler.py
  ```

- 在程序顶部的 Workflow 下拉菜单中选择：

  ```
  GR-Acubuy Create GR (TEST - 不提交)
  ```

- 关于浏览器启动方式（程序自动完成，无需人工干预）：

  - 程序会以"裸启动"方式打开一个全新的 Edge 实例（不通过 Playwright 的常规启动，避免注入自动化标志导致 Microsoft 登录策略拦截）。
  - 该 Edge 使用**固定 profile**：`formfiller_edge_profile`（位于系统临时目录）。
  - profile 固定意味着登录态会跨运行保留。**首次运行**时，程序会在弹出的 Edge 中定位到 Acubuy 登录页，请先在其中完成一次登录；登录态保存后，后续运行可跳过部分步骤（详见第 5 节）。

## 2. 预期流程（对照实际 workflow.json）

程序选中测试版工作流后，将依次执行 `sso_login` 和 `create_gr` 两个 stage，预期行为如下：

### sso_login 阶段

1. Edge 打开登录页：`https://singtel.ivalua.app/page.aspx/en/usr/login`（等待页面 load，最长 60 秒）。
2. 查找 **NCS Employee Login** 按钮（selector `#body_x_button_login_20240212134848558`，8 秒内查找）。该步骤是 optional，找不到会跳过。
3. 点击 NCS Employee Login 按钮（optional）→ 触发 SSO 重定向，跳转到 Microsoft 登录。
4. 若出现 Microsoft 账户选择器（`#tilesHolder .tile`，5 秒内查找，optional），点击第一个账户 tile。
   - 注意：SSO 重定向后登录域为 login.live.com 的 Microsoft 账户选择页，本步骤只负责点选账户，密码 / MFA 需人工完成。
5. 等待主页加载完成：导航栏 `#header_x_headerNavBar` 出现，最长等待 **120 秒**。若人工 MFA / 输密码耗时较长，本步骤会一直等待。
6. 主页就绪后，SSO 登录 stage 完成。

### create_gr 阶段

7. 跳转到 create 页面：`https://singtel.ivalua.app/page.aspx/en/ord/delivery_manage?Create`（等待 networkidle，最长 300 秒）。
8. 等待表单字段 `#body_x_tabc_prxDelivery_prxprxDelivery_x_txtCode` 出现（最长 60 秒）。
9. 依次填写：Order（autocomplete）、Code、Internal Comment、Attachment File（附件，可选）。
10. 填写完成后进入 **manual_review 人工审核**：**不会点击任何保存 / 提交按钮**，页面停在填写完成的表单状态，等待人工检查后手动关闭。

## 3. 检查项清单

请逐项执行并记录结果（✓ / ✗）：

- [ ] **NCS 按钮是否被找到并点击？**
      日志应显示 click `#body_x_button_login_20240212134848558`。
      若日志无此行，说明已处于已登录状态，optional 跳过，属正常。

- [ ] **账户选择器（#tilesHolder .tile）是否出现？**
      出现 = 程序点击了第一个账户 tile；
      不出现 = 直接通过（可能已登录，或登录策略未弹出选择器）。

- [ ] **主页标记 `#header_x_headerNavBar` 是否在 120 秒内出现？**
      这是 SSO 是否成功的硬性判断。超时即失败，进入故障排查（第 6 节）。

- [ ] **SSO 耗时约多久？**
      从点击登录（或页面打开）到主页 `#header_x_headerNavBar` 出现，记录秒数。
      录制实测参考：登录页 → 主页全程约 **26 秒**（不含人工输入密码 / MFA 的时间）。

- [ ] **是否需要手动 MFA / 密码？**
      若需要：程序在主页等待处保持等待，人工完成登录后应自动继续后续流程（不会卡死或报错）。

## 4. 无提交验证（关键安全边界）

- 测试版 create_gr 阶段的 post_fill 配置为 `manual_review`，**不点击保存按钮**，消息为"测试模式：字段已填写，未提交。请人工检查后手动关闭页面。"。
- 验证方式：本次运行结束后，登录 iValua，在收货单列表（delivery 相关 browse 页面）检查**没有新增 GR 记录**。
- 页面最终会停在填写完成的表单状态。请人工核对字段内容无误后，手动关闭 Edge 窗口结束本次运行。

## 5. 二次运行容错验证（验证已登录路径）

- **不清理** Edge profile（不删除 `formfiller_edge_profile`），再次运行同一工作流。
- 预期行为：若上次登录态已保留，NCS 按钮可能不出现（optional 跳过），程序直接等待主页加载 → 进入 create 页面。整个流程不应失败。
- 记录项：
  - 本次是否走了"已登录容错"路径（判断标准：日志中**没有** click NCS 按钮的记录）。
  - 从启动到进入 create 页面是否顺利、无报错。

## 6. 故障排查提示

- **NCS 按钮查找超时（8 秒）且主页也一直不出现**：
  可能被 Microsoft 登录策略拦截（例如需要在新开 Edge 中完成一次真实登录以建立可信会话）。
  处理：在程序弹出的 Edge 中手动完成一次 Acubuy 登录，然后再运行工作流。

- **主页等待超时（120 秒）**：
  可能是等待人工 MFA / 密码输入，或网络问题。
  处理：查看 Edge 窗口当前状态。若停留在登录 / MFA 页面，完成人工操作后流程会自动继续；若页面异常或无响应，检查网络后重试。

- **日志位置**：程序运行时的日志输出显示在 GUI 底部日志区，所有步骤的成败均以此为准。

## 证据保存

验证完成后，请将本手册第 3 节各检查项的 ✓ / ✗ 结果及耗时数据反馈给开发（Atlas），用于确认测试版工作流在真实环境中的 SSO 登录行为是否符合预期。
