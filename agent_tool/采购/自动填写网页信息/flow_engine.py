# -*- coding: utf-8 -*-
"""
多系统流程引擎 - 支持多系统切换的自动化流程执行引擎
"""

import json
import os
import time
import logging
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FlowEngine:
    """
    多系统流程执行引擎
    
    支持:
    - 多系统配置切换
    - 流程步骤执行
    - 变量模板解析
    - 表单填写
    - 附件上传
    - 日历控件处理
    """
    
    def __init__(self, base_dir: str = None):
        """
        初始化流程引擎
        
        Args:
            base_dir: 基础目录路径，默认为脚本所在目录
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.base_dir = base_dir
        self.systems_dir = os.path.join(base_dir, 'systems')
        self.flows_dir = os.path.join(base_dir, 'flows')
        
        # 当前配置
        self.system_config: Optional[Dict[str, Any]] = None
        self.flow_config: Optional[Dict[str, Any]] = None
        self.variables: Dict[str, Any] = {}
        
        # Playwright 对象
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # 运行状态
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        
        # 回调函数
        self.on_step_start = None
        self.on_step_complete = None
        self.on_error = None
        self.on_complete = None
    
    def load_system(self, system_file: str) -> bool:
        """
        加载系统配置
        
        Args:
            system_file: 系统配置文件名 (相对于 systems 目录)
        
        Returns:
            是否加载成功
        """
        try:
            system_path = os.path.join(self.systems_dir, system_file)
            if not os.path.exists(system_path):
                logger.error(f"系统配置文件不存在：{system_path}")
                return False
            
            with open(system_path, 'r', encoding='utf-8') as f:
                self.system_config = json.load(f)
            
            # 初始化变量
            self.variables['selectors'] = self.system_config.get('selectors', {})
            self.variables['base_url'] = self.system_config.get('base_url', '')
            self.variables['system_id'] = self.system_config.get('system_id', '')
            self.variables['system_name'] = self.system_config.get('system_name', '')
            
            logger.info(f"已加载系统配置：{self.system_config.get('system_name', '')}")
            return True
            
        except Exception as e:
            logger.error(f"加载系统配置失败：{e}")
            return False
    
    def load_flow(self, flow_file: str) -> bool:
        """
        加载流程配置
        
        Args:
            flow_file: 流程配置文件名 (相对于 flows 目录)
        
        Returns:
            是否加载成功
        """
        try:
            flow_path = os.path.join(self.flows_dir, flow_file)
            if not os.path.exists(flow_path):
                logger.error(f"流程配置文件不存在：{flow_path}")
                return False
            
            with open(flow_path, 'r', encoding='utf-8') as f:
                self.flow_config = json.load(f)
            
            # 合并流程变量
            flow_variables = self.flow_config.get('variables', {})
            self.variables.update(flow_variables)
            
            logger.info(f"已加载流程配置：{self.flow_config.get('flow_name', '')}")
            return True
            
        except Exception as e:
            logger.error(f"加载流程配置失败：{e}")
            return False
    
    def set_variable(self, key: str, value: Any):
        """设置变量值"""
        self.variables[key] = value
    
    def set_variables(self, variables: Dict[str, Any]):
        """批量设置变量"""
        self.variables.update(variables)
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """获取变量值"""
        return self.variables.get(key, default)
    
    def _resolve_template(self, text: str) -> str:
        """
        解析模板变量 {{variable_name}}
        
        Args:
            text: 包含模板变量的文本
        
        Returns:
            解析后的文本
        """
        if not isinstance(text, str):
            return text
        
        result = text
        for key, value in self.variables.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    result = result.replace(f'{{{{{key}.{sub_key}}}}}', str(sub_value))
            else:
                result = result.replace(f'{{{{{key}}}}}', str(value))
        
        return result
    
    def _resolve_selector(self, selector: str) -> str:
        """
        解析选择器模板
        
        Args:
            selector: CSS 选择器 (可能包含模板变量)
        
        Returns:
            解析后的选择器
        """
        return self._resolve_template(selector)
    
    def launch_browser(self, browser_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        启动浏览器
        
        Args:
            browser_config: 浏览器配置
        
        Returns:
            是否启动成功
        """
        try:
            if browser_config is None:
                browser_config = self.flow_config.get('browser', {}) if self.flow_config else {}
            
            browser_type = browser_config.get('type', 'chromium')
            headless = browser_config.get('headless', False)
            slow_mo = browser_config.get('slow_mo', 0)
            chrome_path = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
            
            self.playwright = sync_playwright().start()
            
            if browser_type == 'chrome':
                if chrome_path:
                    self.browser = self.playwright.chromium.launch(
                        headless=headless,
                        slow_mo=slow_mo,
                        executable_path=chrome_path
                    )
                else:
                    self.browser = self.playwright.chromium.launch(
                        headless=headless,
                        slow_mo=slow_mo
                    )
            elif browser_type == 'msedge':
                self.browser = self.playwright.chromium.launch(
                    headless=headless,
                    slow_mo=slow_mo,
                    channel='msedge'
                )
            else:
                self.browser = self.playwright.chromium.launch(
                    headless=headless,
                    slow_mo=slow_mo
                )
            
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()
            
            logger.info(f"浏览器启动成功：{browser_type}")
            return True
            
        except Exception as e:
            logger.error(f"浏览器启动失败：{e}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败：{e}")
    
    def execute_system_login(self) -> bool:
        """
        执行系统登录 (使用系统配置)
        
        Returns:
            是否登录成功
        """
        try:
            if not self.system_config:
                logger.error("未加载系统配置")
                return False
            
            login_config = self.system_config.get('login', {})
            base_url = self.system_config.get('base_url', '')
            login_url = login_config.get('url', '')
            
            # 导航到登录页
            full_url = base_url + login_url if not login_url.startswith('http') else login_url
            logger.info(f"导航到登录页：{full_url}")
            self.page.goto(full_url)
            self.page.wait_for_load_state('networkidle')
            
            # 填写登录字段
            fields = login_config.get('fields', {})
            for field_name, field_config in fields.items():
                selector = self._resolve_template(field_config.get('selector', ''))
                field_type = field_config.get('type', 'fill')
                value = self.variables.get(field_name, '')
                
                element = self.page.locator(selector).first
                
                if field_type == 'fill':
                    element.fill(value)
                    logger.info(f"  填写 {field_name}: {'*' * len(value) if field_name == 'password' else value}")
                elif field_type == 'click':
                    element.click()
                    logger.info(f"  点击 {field_name}")
            
            # 等待登录成功
            success_indicator = login_config.get('success_indicator', {})
            if success_indicator:
                selector = self._resolve_template(success_indicator.get('selector', ''))
                timeout = success_indicator.get('timeout', 10000)
                try:
                    self.page.wait_for_selector(selector, timeout=timeout)
                    logger.info("登录成功")
                except Exception as e:
                    logger.warning(f"等待登录成功指示器超时：{e}")
            
            return True
            
        except Exception as e:
            logger.error(f"登录失败：{e}")
            return False
    
    def execute_navigate(self, step: Dict[str, Any]) -> bool:
        """
        执行导航步骤
        
        Args:
            step: 步骤配置
        
        Returns:
            是否执行成功
        """
        try:
            url = self._resolve_template(step.get('url', ''))
            base_url = self.variables.get('base_url', '')
            full_url = base_url + url if not url.startswith('http') else url
            
            logger.info(f"导航到：{full_url}")
            self.page.goto(full_url)
            self.page.wait_for_load_state('networkidle')
            
            # 填写字段 (如果有)
            fields = step.get('fields', [])
            for field in fields:
                self._fill_field(field)
            
            # 等待
            wait_after = step.get('wait_after', 0)
            if wait_after > 0:
                time.sleep(wait_after / 1000)
            
            return True
            
        except Exception as e:
            logger.error(f"导航失败：{e}")
            return False
    
    def execute_form(self, step: Dict[str, Any]) -> bool:
        """
        执行表单填写步骤
        
        Args:
            step: 步骤配置
        
        Returns:
            是否执行成功
        """
        try:
            fields = step.get('fields', [])
            
            for field in fields:
                success = self._fill_field(field)
                if not success:
                    logger.warning(f"字段填写失败：{field.get('name', '')}")
            
            # 等待
            wait_after = step.get('wait_after', 0)
            if wait_after > 0:
                time.sleep(wait_after / 1000)
            
            return True
            
        except Exception as e:
            logger.error(f"表单填写失败：{e}")
            return False
    
    def _fill_field(self, field: Dict[str, Any]) -> bool:
        """
        填写单个字段
        
        Args:
            field: 字段配置
        
        Returns:
            是否填写成功
        """
        try:
            selector = self._resolve_selector(field.get('selector', ''))
            value = self._resolve_template(field.get('value', ''))
            field_type = field.get('type', 'fill')
            
            element = self.page.locator(selector).first
            
            if not element.count():
                logger.warning(f"元素未找到：{selector}")
                return False
            
            if field_type == 'fill':
                element.fill(value)
                logger.info(f"  填写 {field.get('name', '')}: {value}")
            
            elif field_type == 'select':
                element.select_option(value)
                logger.info(f"  选择 {field.get('name', '')}: {value}")
            
            elif field_type == 'click':
                element.click()
                logger.info(f"  点击 {field.get('name', '')}")
            
            elif field_type == 'datepicker':
                datepicker_config = field.get('datepicker_config', {})
                self._handle_datepicker(selector, value, datepicker_config)
                logger.info(f"  填写日期 {field.get('name', '')}: {value}")
            
            else:
                logger.warning(f"未知的字段类型：{field_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"填写字段失败：{e}")
            return False
    
    def _handle_datepicker(self, selector: str, value: str, config: Dict[str, Any]):
        """
        处理日历控件
        
        Args:
            selector: 日期字段选择器
            value: 日期值 (YYYY-MM-DD)
            config: 日历配置
        """
        try:
            # 点击日历按钮打开弹窗
            trigger = config.get('trigger', '')
            if trigger:
                date_btn = self.page.locator(trigger).first
                with self.page.expect_popup() as popup_info:
                    date_btn.click()
                
                cal_page = popup_info.value
                cal_page.wait_for_load_state('networkidle')
                
                # 解析日期
                parts = value.split('-')
                if len(parts) == 3:
                    year, month, day = parts
                    
                    # 选择年
                    year_selector = config.get('year', '')
                    if year_selector:
                        cal_page.locator(year_selector).select_option(year)
                    
                    # 选择月
                    month_selector = config.get('month', '')
                    if month_selector:
                        cal_page.locator(month_selector).select_option(month)
                    
                    # 选择日
                    day_pattern = config.get('day_pattern', '')
                    if day_pattern:
                        day_selector = day_pattern.replace('{day}', day)
                        cal_page.locator(day_selector).click()
                
                # 等待弹窗关闭
                time.sleep(1)
            else:
                # 直接填写
                self.page.locator(selector).fill(value)
                
        except Exception as e:
            logger.error(f"日历控件处理失败：{e}")
            # 回退到直接填写
            self.page.locator(selector).fill(value)
    
    def execute_attachments(self, step: Dict[str, Any]) -> bool:
        """
        执行附件上传步骤
        
        Args:
            step: 步骤配置
        
        Returns:
            是否执行成功
        """
        try:
            attachments = step.get('attachments', [])
            attach_config = self.system_config.get('attachment_config', {})
            
            for i, attach in enumerate(attachments, 1):
                logger.info(f"上传附件 {i}: {attach.get('file_path', '')}")
                
                category = self._resolve_template(attach.get('category', ''))
                file_path = self._resolve_template(attach.get('file_path', ''))
                description = self._resolve_template(attach.get('description', ''))
                
                # 构建选择器
                category_selector = attach_config.get('category_prefix', '') + str(i)
                file_selector = attach_config.get('file_prefix', '') + str(i)
                desc_selector = attach_config.get('desc_prefix', '') + str(i)
                
                # 选择 Category
                if category and category_selector:
                    try:
                        self.page.locator(category_selector).select_option(category)
                        logger.info(f"  选择 Category: {category}")
                    except Exception as e:
                        logger.warning(f"  Category 选择失败：{e}")
                
                # 上传文件
                if file_path and os.path.exists(file_path):
                    try:
                        self.page.locator(file_selector).set_input_files(file_path)
                        logger.info(f"  上传文件：{file_path}")
                    except Exception as e:
                        logger.warning(f"  文件上传失败：{e}")
                else:
                    logger.warning(f"  文件不存在：{file_path}")
                
                # 填写 Description
                if description and desc_selector:
                    try:
                        self.page.locator(desc_selector).fill(description)
                        logger.info(f"  填写 Description: {description}")
                    except Exception as e:
                        logger.warning(f"  Description 填写失败：{e}")
                
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"附件上传失败：{e}")
            return False
    
    def execute_action(self, step: Dict[str, Any]) -> bool:
        """
        执行动作步骤 (点击等)
        
        Args:
            step: 步骤配置
        
        Returns:
            是否执行成功
        """
        try:
            actions = step.get('actions', [])
            
            for action in actions:
                action_type = action.get('type', 'click')
                selector = self._resolve_selector(action.get('selector', ''))
                
                if action_type == 'click':
                    self.page.locator(selector).click()
                    logger.info(f"  点击：{selector}")
                
                elif action_type == 'wait':
                    wait_time = action.get('time', 1000)
                    time.sleep(wait_time / 1000)
                    logger.info(f"  等待：{wait_time}ms")
            
            # 等待
            wait_after = step.get('wait_after', 0)
            if wait_after > 0:
                time.sleep(wait_after / 1000)
            
            return True
            
        except Exception as e:
            logger.error(f"动作执行失败：{e}")
            return False
    
    def execute_step(self, step: Dict[str, Any]) -> bool:
        """
        执行单个步骤
        
        Args:
            step: 步骤配置
        
        Returns:
            是否执行成功
        """
        step_type = step.get('type', '')
        
        if step_type == 'system_login':
            return self.execute_system_login()
        
        elif step_type == 'navigate':
            return self.execute_navigate(step)
        
        elif step_type == 'form':
            return self.execute_form(step)
        
        elif step_type == 'attachments':
            return self.execute_attachments(step)
        
        elif step_type == 'action':
            return self.execute_action(step)
        
        else:
            logger.warning(f"未知的步骤类型：{step_type}")
            return False
    
    def execute_flow(self) -> bool:
        """
        执行完整流程
        
        Returns:
            是否执行成功
        """
        if not self.flow_config:
            logger.error("未加载流程配置")
            return False
        
        if not self.system_config:
            logger.error("未加载系统配置")
            return False
        
        self.is_running = True
        steps = self.flow_config.get('steps', [])
        self.total_steps = len(steps)
        self.current_step = 0
        
        logger.info(f"开始执行流程：{self.flow_config.get('flow_name', '')}")
        logger.info(f"总步骤数：{self.total_steps}")
        
        try:
            # 启动浏览器
            if not self.launch_browser():
                return False
            
            for i, step in enumerate(steps):
                self.current_step = i + 1
                step_name = step.get('name', f'Step {i+1}')
                
                logger.info(f"\n{'='*50}")
                logger.info(f"执行步骤 [{i+1}/{self.total_steps}]: {step_name}")
                logger.info(f"{'='*50}")
                
                # 回调：步骤开始
                if self.on_step_start:
                    self.on_step_start(i + 1, self.total_steps, step_name)
                
                # 执行步骤
                success = self.execute_step(step)
                
                # 回调：步骤完成
                if self.on_step_complete:
                    self.on_step_complete(i + 1, self.total_steps, step_name, success)
                
                if not success:
                    logger.error(f"步骤失败：{step_name}")
                    if self.on_error:
                        self.on_error(f"步骤失败：{step_name}")
                    return False
                
                time.sleep(0.5)
            
            logger.info(f"\n{'='*50}")
            logger.info("流程执行完成!")
            logger.info(f"{'='*50}")
            
            if self.on_complete:
                self.on_complete(True, "流程执行成功")
            
            return True
            
        except Exception as e:
            logger.error(f"流程执行异常：{e}")
            if self.on_error:
                self.on_error(f"流程异常：{e}")
            return False
        
        finally:
            self.is_running = False
            self.close_browser()
    
    def execute_flow_async(self, callback_queue=None) -> bool:
        """
        异步执行流程 (用于 GUI 线程)
        
        Args:
            callback_queue: 回调队列 (用于 GUI 更新)
        
        Returns:
            是否执行成功
        """
        def step_start_callback(step: int, total: int, name: str):
            if callback_queue:
                callback_queue.put(('step_start', step, total, name))
        
        def step_complete_callback(step: int, total: int, name: str, success: bool):
            if callback_queue:
                callback_queue.put(('step_complete', step, total, name, success))
        
        def error_callback(error: str):
            if callback_queue:
                callback_queue.put(('error', error))
        
        def complete_callback(success: bool, message: str):
            if callback_queue:
                callback_queue.put(('complete', success, message))
        
        self.on_step_start = step_start_callback
        self.on_step_complete = step_complete_callback
        self.on_error = error_callback
        self.on_complete = complete_callback
        
        return self.execute_flow()


class SystemManager:
    """
    系统管理器 - 管理多个系统配置
    """
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.base_dir = base_dir
        self.systems_dir = os.path.join(base_dir, 'systems')
        self.systems: Dict[str, Dict[str, Any]] = {}
    
    def load_all_systems(self) -> Dict[str, Dict[str, Any]]:
        """加载所有系统配置"""
        self.systems = {}
        
        if not os.path.exists(self.systems_dir):
            logger.warning(f"系统配置目录不存在：{self.systems_dir}")
            return self.systems
        
        for filename in os.listdir(self.systems_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.systems_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        system_id = config.get('system_id', filename.replace('.json', ''))
                        self.systems[system_id] = config
                        logger.info(f"加载系统：{config.get('system_name', '')}")
                except Exception as e:
                    logger.error(f"加载系统配置失败 {filename}: {e}")
        
        return self.systems
    
    def get_system(self, system_id: str) -> Optional[Dict[str, Any]]:
        """获取指定系统配置"""
        return self.systems.get(system_id)
    
    def get_system_names(self) -> List[str]:
        """获取所有系统名称列表"""
        return [config.get('system_name', config.get('system_id', '')) 
                for config in self.systems.values()]


class FlowManager:
    """
    流程管理器 - 管理多个流程配置
    """
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.base_dir = base_dir
        self.flows_dir = os.path.join(base_dir, 'flows')
        self.flows: Dict[str, Dict[str, Any]] = {}
    
    def load_all_flows(self, filter_system_id: str = None) -> Dict[str, Dict[str, Any]]:
        """
        加载所有流程配置
        
        Args:
            filter_system_id: 可选的系统 ID 过滤器
        """
        self.flows = {}
        
        if not os.path.exists(self.flows_dir):
            logger.warning(f"流程配置目录不存在：{self.flows_dir}")
            return self.flows
        
        for filename in os.listdir(self.flows_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.flows_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        
                        # 过滤
                        if filter_system_id:
                            if config.get('system_id') != filter_system_id:
                                continue
                        
                        flow_id = config.get('flow_id', filename.replace('.json', ''))
                        self.flows[flow_id] = config
                        logger.info(f"加载流程：{config.get('flow_name', '')}")
                except Exception as e:
                    logger.error(f"加载流程配置失败 {filename}: {e}")
        
        return self.flows
    
    def get_flow(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """获取指定流程配置"""
        return self.flows.get(flow_id)
    
    def get_flow_names(self) -> List[str]:
        """获取所有流程名称列表"""
        return [config.get('flow_name', config.get('flow_id', '')) 
                for config in self.flows.values()]


if __name__ == '__main__':
    # 测试示例
    engine = FlowEngine()
    
    # 加载配置
    if engine.load_system('csms.json'):
        if engine.load_flow('csms_create_proposal.json'):
            # 设置变量
            engine.set_variable('proposal_no', 'P2024-001')
            engine.set_variable('cust_ref_no', 'CR-2024-001')
            
            # 执行流程
            engine.execute_flow()
