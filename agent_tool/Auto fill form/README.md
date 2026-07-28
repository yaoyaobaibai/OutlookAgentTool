# FormFiller - 多工作流表单自动填充工具

使用 Playwright 实现多工作流表单自动填充的 GUI 工具。

## 架构

```
form_filler.py              - GUI 主程序（工作流选择器 + 动态字段加载）
workflow_manager.py         - 工作流管理（发现、加载、切换、持久化）
workflow_engine.py          - 工作流执行引擎（导航、字段填充、重试）
handlers/                   - 字段处理器包（7种内置类型）
workflows/                  - 工作流配置目录
```

## 特性

- **多工作流支持**: 通过 GUI 下拉菜单切换不同自动化流程
- **插件式架构**: 添加新工作流只需在 workflows/ 下创建配置文件夹
- **7种内置处理器**: input, select, checkbox, autocomplete, datepicker, popup_search, file_upload
- **Excel 数据导入**: 从 Excel 文件读取表单数据
- **附件上传**: 支持多个附件的 Category/File/Description 上传
- **错误重试**: 字段填充失败自动重试 2 次后停止

## 快速开始

1. 安装依赖: `pip install -r requirements.txt`
2. 安装浏览器: `playwright install chromium`
3. 运行: `python form_filler.py`

## 工作流切换

程序启动后，在顶部 "Workflow" 下拉菜单中选择工作流。
切换时自动更新：登录 URL、表单字段列表。

## 当前支持的工作流

| 工作流 | 状态 | 描述 |
|--------|------|------|
| CSMS Create Proposal Group | active | NCS CSMS 系统提案表单自动填充 |
| GR-Acubuy Create Goods Receipt | draft | Singtel iValua 平台收货单创建 |

## 添加新工作流

见 `workflows/README.md`

## 打包为 EXE

运行 `执行打包.bat`，生成的可执行文件在 `dist/FormFiller/` 目录。
