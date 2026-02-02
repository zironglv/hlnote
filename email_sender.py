"""
邮件发送模块 - 负责通过SMTP发送报告邮件
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class EmailSender:
    """邮件发送器"""
    
    def __init__(self, 
                 smtp_server: str = None,
                 smtp_port: int = None,
                 username: str = None,
                 password: str = None,
                 sender_email: str = None,
                 recipient_email: str = None):
        """
        初始化邮件发送器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 邮箱用户名
            password: 邮箱密码或授权码
            sender_email: 发送者邮箱
            recipient_email: 接收者邮箱
        """
        # 从环境变量获取配置，如果没有则使用默认值
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL', self.username)
        self.recipient_email = recipient_email or os.getenv('RECIPIENT_EMAIL')
        
        # 验证必要配置
        self._validate_config()
    
    def _validate_config(self):
        """验证邮件配置"""
        missing_configs = []
        
        if not self.username:
            missing_configs.append('EMAIL_USERNAME')
        if not self.password:
            missing_configs.append('EMAIL_PASSWORD')
        if not self.recipient_email:
            missing_configs.append('RECIPIENT_EMAIL')
            
        if missing_configs:
            raise ValueError(f"缺少必要的邮件配置: {', '.join(missing_configs)}")
    
    def send_report(self, html_content: str, chart_path: str = None) -> bool:
        """
        发送报告邮件
        
        Args:
            html_content: HTML邮件内容
            chart_path: 图表文件路径（可选）
            
        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info("开始发送邮件...")
            
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📈 中证红利低波指数投研报告 - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加附件（如果有图表）
            if chart_path and os.path.exists(chart_path):
                self._attach_file(msg, chart_path)
            
            # 发送邮件
            success = self._send_email(msg)
            
            if success:
                logger.info("邮件发送成功")
            else:
                logger.error("邮件发送失败")
                
            return success
            
        except Exception as e:
            logger.error(f"邮件发送过程中发生错误: {str(e)}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """
        添加附件到邮件
        
        Args:
            msg: 邮件对象
            file_path: 文件路径
        """
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= "{filename}"'
            )
            msg.attach(part)
            logger.debug(f"已添加附件: {filename}")
            
        except Exception as e:
            logger.warning(f"添加附件失败: {str(e)}")
    
    def _send_email(self, msg: MIMEMultipart) -> bool:
        """
        通过SMTP发送邮件
        
        Args:
            msg: 邮件对象
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建SMTP连接
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 启用TLS加密
            server.login(self.username, self.password)
            
            # 发送邮件
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            
            # 关闭连接
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP认证失败，请检查用户名和密码")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error("收件人被拒绝，请检查收件人邮箱地址")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"发送邮件时发生未知错误: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试SMTP连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.quit()
            logger.info("SMTP连接测试成功")
            return True
        except Exception as e:
            logger.error(f"SMTP连接测试失败: {str(e)}")
            return False

# 常用邮箱服务商配置示例
EMAIL_CONFIGS = {
    'gmail': {
        'server': 'smtp.gmail.com',
        'port': 587
    },
    'qq': {
        'server': 'smtp.qq.com',
        'port': 587
    },
    '163': {
        'server': 'smtp.163.com',
        'port': 25
    },
    'outlook': {
        'server': 'smtp-mail.outlook.com',
        'port': 587
    }
}

def get_email_config(provider: str) -> dict:
    """
    获取邮箱服务商配置
    
    Args:
        provider: 邮箱服务商名称(gmail/qq/163/outlook)
        
    Returns:
        dict: 配置字典
    """
    return EMAIL_CONFIGS.get(provider.lower(), EMAIL_CONFIGS['gmail'])