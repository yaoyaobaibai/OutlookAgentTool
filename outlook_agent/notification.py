"""
通知模块 - Windows 通知和托盘图标
"""
import os
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        logger.info("通知管理器初始化成功")
    
    def show_notification(
        self, 
        title: str, 
        message: str, 
        duration: int = 10,
        callback: Optional[Callable] = None
    ):
        """
        显示 Windows 通知
        
        Args:
            title: 通知标题
            message: 通知内容
            duration: 显示时长（秒）
            callback: 点击回调函数
        """
        # 尝试使用 Windows 原生通知
        try:
            self._show_windows_notification(title, message, duration)
            logger.info(f"显示通知: {title}")
            return True
        except Exception as e:
            logger.debug(f"Windows 通知失败: {e}")
        
        # 备用方案：使用 tkinter 弹窗
        self._show_fallback_notification(title, message, callback)
        return True
    
    def _show_windows_notification(self, title: str, message: str, duration: int):
        """使用 Windows 原生通知"""
        import subprocess
        import sys
        import tempfile
        import os
        _CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0
        
        # 创建 PowerShell 脚本显示通知
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{title}</text>
            <text id="2">{message}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("OutlookAgent").Show($toast)
'''
        
        # 执行 PowerShell 脚本
        subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            timeout=10,
            creationflags=_CREATE_NO_WINDOW
        )
    
    def _show_fallback_notification(
        self, 
        title: str, 
        message: str, 
        callback: Optional[Callable] = None
    ):
        """
        备用通知方式（tkinter 弹窗）
        
        Args:
            title: 标题
            message: 消息
            callback: 回调函数
        """
        import tkinter as tk
        from tkinter import messagebox
        
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 显示消息框
        result = messagebox.showinfo(title, message)
        
        # 如果用户点击确定，调用回调
        if result and callback:
            callback()
        
        root.destroy()
    
    def show_email_alert(self, email_info: dict, callback: Optional[Callable] = None):
        """
        显示邮件警报通知
        
        Args:
            email_info: 邮件信息字典
            callback: 点击回调函数
        """
        title = "📧 新邮件检测"
        
        message_lines = [
            f"发件人: {email_info.get('sender_name', '未知')}",
            f"主题: {email_info.get('subject', '(无主题)')}",
            f"附件: {len(email_info.get('attachments', []))} 个",
            "",
            "点击查看详情"
        ]
        
        message = "\n".join(message_lines)
        
        self.show_notification(title, message, duration=10, callback=callback)


class TrayIcon:
    """系统托盘图标"""
    
    def __init__(self, icon_path: Optional[str] = None):
        """
        初始化托盘图标
        
        Args:
            icon_path: 图标文件路径（.ico）
        """
        self.icon_path = icon_path
        self.menu = None
        self._init_tray()
    
    def _init_tray(self):
        """初始化托盘"""
        try:
            import pystray
            from PIL import Image, ImageDraw
            
            # 创建默认图标
            if self.icon_path and os.path.exists(self.icon_path):
                self.icon_image = Image.open(self.icon_path)
            else:
                # 创建简单的默认图标
                self.icon_image = self._create_default_icon()
            
            logger.info("托盘图标初始化成功")
            
        except ImportError:
            logger.warning("pystray 未安装，托盘功能不可用")
            self.icon_image = None
        except Exception as e:
            logger.error(f"初始化托盘失败: {e}")
            self.icon_image = None
    
    def _create_default_icon(self):
        """创建默认图标"""
        try:
            from PIL import Image, ImageDraw
            
            # 创建 64x64 的图标
            width = 64
            height = 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 画一个简单的邮件图标
            # 蓝色背景圆
            draw.ellipse([8, 8, 56, 56], fill=(52, 152, 219, 255))
            
            # 白色信封
            draw.rectangle([16, 22, 48, 42], fill=(255, 255, 255, 255))
            draw.polygon([(16, 22), (32, 35), (48, 22)], fill=(255, 255, 255, 255))
            
            return image
            
        except Exception as e:
            logger.error(f"创建默认图标失败: {e}")
            return None
    
    def run(self, on_click: Optional[Callable] = None):
        """
        运行托盘图标
        
        Args:
            on_click: 点击回调函数
        """
        if not self.icon_image:
            return
        
        try:
            import pystray
            
            # 创建菜单
            menu = pystray.Menu(
                pystray.MenuItem("打开主窗口", on_click if on_click else lambda: None),
                pystray.MenuItem("退出", self._quit),
            )
            
            # 创建图标
            icon = pystray.Icon(
                "outlook_agent",
                self.icon_image,
                "Outlook 邮件监控",
                menu
            )
            
            self.icon = icon
            icon.run()
            
        except Exception as e:
            logger.error(f"运行托盘图标失败: {e}")
    
    def _quit(self):
        """退出托盘"""
        if hasattr(self, 'icon'):
            self.icon.stop()
    
    def update_tooltip(self, text: str):
        """
        更新托盘提示文本
        
        Args:
            text: 提示文本
        """
        if hasattr(self, 'icon'):
            self.icon.title = text
