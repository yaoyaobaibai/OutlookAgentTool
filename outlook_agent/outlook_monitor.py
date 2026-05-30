"""
Outlook 监控模块 - 监控 Outlook 新邮件
"""
import os
import json
import re
import logging
import pythoncom
from typing import Callable, Optional, List
from datetime import datetime, timedelta
from config import load_config

logger = logging.getLogger(__name__)

# 已处理的邮件ID缓存（避免重复处理）
_processed_email_ids = set()

# 持久化已处理邮件 ID，防止重启后重复提醒
_PROCESSED_IDS_FILE = os.path.join(os.path.expanduser("~"), "outlook_agent_processed.json")
try:
    if os.path.exists(_PROCESSED_IDS_FILE):
        with open(_PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
            saved = json.load(f)
            if isinstance(saved, list):
                _processed_email_ids = set(saved[-500:])  # keep last 500
except Exception:
    pass

def _save_processed_ids():
    try:
        with open(_PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(_processed_email_ids)[-500:], f, ensure_ascii=False)
    except Exception:
        pass


class OutlookMonitor:
    """Outlook 邮件监控类"""
    
    def __init__(self, keywords: List[str], match_mode: str = "any"):
        """
        初始化监控器
        
        Args:
            keywords: 关键字列表
            match_mode: 匹配模式 ('any' 或 'all')
        """
        self.keywords = keywords
        self.match_mode = match_mode
        self.outlook = None
        self.namespace = None
        self.inbox = None
        self.items = None
        self.on_email_callback = None
        self._running = False
        
    def connect(self) -> bool:
        """
        连接到 Outlook
        
        Returns:
            是否成功连接
        """
        try:
            import win32com.client
            
            # 初始化 COM
            pythoncom.CoInitialize()
            
            # 连接 Outlook
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            self.inbox = self.namespace.GetDefaultFolder(6)  # olFolderInbox = 6
            self.items = self.inbox.Items
            
            logger.info("成功连接到 Outlook")
            return True
            
        except Exception as e:
            logger.error(f"连接 Outlook 失败: {e}")
            return False
    
    def disconnect(self):
        """断开 Outlook 连接"""
        try:
            if self.outlook:
                self.outlook = None
                self.namespace = None
                self.inbox = None
                self.items = None
            
            # 释放 COM
            pythoncom.CoUninitialize()
            logger.info("已断开 Outlook 连接")
            
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
    
    def set_email_callback(self, callback: Callable):
        """
        设置新邮件回调函数
        
        Args:
            callback: 回调函数，参数为邮件信息字典
        """
        self.on_email_callback = callback
    
    def check_keywords(self, subject: str, body: str) -> bool:
        """
        检查邮件是否包含关键字
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            
        Returns:
            是否匹配关键字
        """
        text = f"{subject} {body}"
        
        matched_keywords = []
        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                matched_keywords.append(keyword)
        
        if self.match_mode == "any":
            return len(matched_keywords) > 0
        elif self.match_mode == "all":
            return len(matched_keywords) == len(self.keywords)
        else:
            return len(matched_keywords) > 0
    
    def extract_email_info(self, mail_item) -> dict:
        """
        提取邮件信息
        
        Args:
            mail_item: Outlook MailItem 对象
            
        Returns:
            邮件信息字典
        """
        try:
            # 获取发件人信息
            sender_email = "未知"
            sender_name = "未知"
            try:
                sender = mail_item.Sender
                sender_email = sender.Address if sender else "未知"
                sender_name = sender.Name if sender else "未知"
            except Exception:
                try:
                    sender_email = mail_item.SenderEmailAddress or "未知"
                except:
                    pass
                try:
                    sender_name = mail_item.SenderName or "未知"
                except:
                    pass
            
            # 获取附件信息（不保存 attachment_obj，避免跨线程问题）
            attachments = []
            for attachment in mail_item.Attachments:
                attachments.append({
                    'name': attachment.FileName,
                    'size': attachment.Size,
                    'index': attachment.Index,
                })
            
            return {
                'entry_id': mail_item.EntryID,
                'subject': mail_item.Subject or "(无主题)",
                'sender_email': sender_email,
                'sender_name': sender_name,
                'received_time': mail_item.ReceivedTime,
                'body': mail_item.Body or "",
                'html_body': mail_item.HTMLBody or "",
                'attachments': attachments,
            }
            
        except Exception as e:
            logger.error(f"提取邮件信息失败: {e}")
            return None
    
    def _on_item_add(self, item):
        """
        新邮件事件处理（内部方法）
        
        Args:
            item: 新邮件项
        """
        try:
            # 确保是邮件项
            if item.Class != 43:  # olMail = 43
                return
            
            # 提取邮件信息
            email_info = self.extract_email_info(item)
            if not email_info:
                return
            
            logger.info(f"检测到新邮件: {email_info['subject']}")
            
            # 检查关键字
            if self.check_keywords(email_info['subject'], email_info['body']):
                logger.info(f"邮件匹配关键字！主题: {email_info['subject']}")
                
                # 调用回调函数
                if self.on_email_callback:
                    self.on_email_callback(email_info)
                    
        except Exception as e:
            logger.error(f"处理新邮件时出错: {e}")
    
    def start_monitoring(self):
        """开始监控新邮件"""
        if not self.items:
            logger.error("未连接到 Outlook")
            return False
        
        try:
            # 使用 Win32com 的事件处理
            import win32com.client
            
            # 绑定事件
            win32com.client.WithEvents(self.items, self._create_event_class())
            
            self._running = True
            logger.info("开始监控新邮件...")
            return True
            
        except Exception as e:
            logger.error(f"启动监控失败: {e}")
            return False
    
    def _create_event_class(self):
        """创建事件处理类"""
        monitor = self
        
        class ItemsEvents:
            def ItemAdd(self, item):
                monitor._on_item_add(item)
        
        return ItemsEvents
    
    def poll_new_emails(self) -> List[dict]:
        """
        轮询获取匹配关键字的邮件
        
        使用 GetFirst()/GetNext() 遍历排序后的邮件列表，
        比 items.Item(i) 索引访问更可靠，避免大收件箱下索引错乱。
        
        Returns:
            匹配的邮件信息列表
        """
        global _processed_email_ids
        
        # 确保 COM 已初始化
        if not self.inbox:
            logger.info("首次轮询，初始化 COM 连接...")
            if not self.connect():
                logger.error("无法连接 Outlook")
                return []
        
        logger.info("开始轮询邮件...")
        
        try:
            # 获取收件箱 Items（处理 COM 过期重连）
            try:
                items = self.inbox.Items
            except Exception as e:
                logger.debug(f"COM 对象过期，重新连接: {e}")
                if not self.connect():
                    logger.error("重新连接失败")
                    return []
                items = self.inbox.Items
            
            if not items:
                logger.warning("无法获取邮件列表")
                return []
            
            # 按接收时间降序排序（最新在前）
            try:
                items.Sort("[ReceivedTime]", True)
                logger.info("邮件列表已按时间降序排列")
            except Exception as sort_error:
                logger.warning(f"排序失败（将使用原始顺序）: {sort_error}")
            
            # 读取配置
            config = load_config()
            monitor_mode = config.get("monitor_mode", "time")
            monitor_time_range = config.get("monitor_time_range", 60)
            monitor_count_limit = config.get("monitor_count_limit", 50)
            
            logger.info(
                "配置: mode=%s, time_range=%d分钟, count_limit=%d封",
                monitor_mode, monitor_time_range, monitor_count_limit
            )
            
            recent_emails = []
            checked_count = 0
            time_filtered_count = 0
            
            # 使用 GetFirst()/GetNext() 遍历（比 Item(i) 索引更可靠）
            try:
                mail = items.GetFirst()
            except Exception as e:
                logger.warning(f"GetFirst 失败: {e}")
                return []
            
            while mail is not None and checked_count < monitor_count_limit:
                checked_count += 1
                
                try:
                    # 获取 EntryID 用于去重
                    entry_id = None
                    try:
                        entry_id = mail.EntryID
                        if entry_id and entry_id in _processed_email_ids:
                            logger.debug(f"邮件 #{checked_count} 已处理过，跳过")
                            mail = items.GetNext()
                            continue
                    except Exception:
                        pass
                    
                    # 获取主题
                    try:
                        subject = mail.Subject or "(无主题)"
                    except Exception:
                        subject = "(无法获取主题)"
                    
                    # 获取接收时间（处理时区）
                    try:
                        received_time = mail.ReceivedTime
                        if hasattr(received_time, 'strftime'):
                            # datetime 类型
                            if hasattr(received_time, 'tzinfo') and received_time.tzinfo is not None:
                                received_time = received_time.replace(tzinfo=None)
                        else:
                            # COM 日期格式 → datetime
                            try:
                                received_time = datetime.fromtimestamp(
                                    (float(received_time) - 25569) * 86400.0
                                )
                            except Exception:
                                received_time = datetime.now()
                    except Exception:
                        received_time = datetime.now()
                    
                    # 时间过滤（time / both 模式）
                    if monitor_mode in ("time", "both"):
                        time_diff = datetime.now() - received_time
                        if time_diff > timedelta(minutes=monitor_time_range):
                            time_filtered_count += 1
                            logger.debug(
                                "邮件 #%d '%s' 超过%d分钟（差: %s），跳过",
                                checked_count, subject[:40], monitor_time_range, time_diff
                            )
                            mail = items.GetNext()
                            continue
                    
                    # 提取邮件信息
                    email_info = self.extract_email_info(mail)
                    if not email_info:
                        logger.warning(f"邮件 #{checked_count} 信息提取失败")
                        mail = items.GetNext()
                        continue
                    
                    # 关键字匹配
                    body = email_info.get('body', '')
                    matched = self.check_keywords(subject, body)
                    
                    if matched:
                        logger.info(f"✅ 邮件 #{checked_count} 匹配: {subject[:60]}")
                        if entry_id:
                            _processed_email_ids.add(entry_id)
                            _save_processed_ids()
                        recent_emails.append(email_info)
                    
                except Exception as e:
                    logger.error(f"处理邮件 #{checked_count} 时出错: {e}")
                
                # 移到下一封
                try:
                    mail = items.GetNext()
                except Exception:
                    logger.debug("GetNext 结束，已遍历完所有邮件")
                    break
            
            logger.info(
                "本轮检查 %d 封，时间过滤 %d 封，匹配 %d 封",
                checked_count, time_filtered_count, len(recent_emails)
            )
            return recent_emails
            
        except Exception as e:
            logger.error(f"轮询新邮件失败: {e}")
            import traceback
            traceback.print_exc()
            return []
