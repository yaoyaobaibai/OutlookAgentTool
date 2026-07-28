# 表单自动填充工具

使用 Playwright 实现网页表单自动填充的 GUI 工具。

## 安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 安装 Playwright 浏览器：
```bash
playwright install chromium
```

## 使用方法

1. 打开目标网页，登录或填写表单页面

2. 运行程序：
```bash
python form_filler.py
```

3. 在 GUI 界面中配置字段：
   - 点击"添加字段"添加要填充的表单字段
   - **字段名称**: 自定义标识（如 username, password）
   - **CSS 选择器**: 网页元素的 CSS 选择器（如 input#username, input[name="password"]）
   - **默认值**: 要填充的内容

4. 点击"启动填充"开始自动填充

## 获取 CSS 选择器

在浏览器中按 F12 打开开发者工具：
1. 点击左上角的箭头图标（选择工具）
2. 点击要填充的输入框
3. 右键点击 HTML 代码 -> Copy -> Copy selector

常见选择器示例：
- `input#username` - ID 为 username 的 input
- `input[name="password"]` - name 属性为 password 的 input
- `.login-form input[type="text"]` - 类名为 login-form 下的文本输入框

## 注意事项

- 程序会使用当前已打开的网页页面进行填充
- 确保在点击"启动填充"前，目标网页已经打开
- 可以动态添加/修改/删除字段配置
- 配置会保存在 form_config.json 文件中
