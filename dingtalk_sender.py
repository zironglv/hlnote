"""
钉钉机器人推送模块 - 负责将报告通过钉钉机器人发送
"""

import requests
import json
import logging
import os
from datetime import datetime
import base64
from typing import Optional

logger = logging.getLogger(__name__)

class DingTalkSender:
    """钉钉机器人发送器"""
    
    def __init__(self, webhook_url: str = None):
        """
        初始化钉钉机器人发送器
        
        Args:
            webhook_url: 钉钉机器人webhook地址
        """
        # 优先使用传入的URL，其次使用环境变量，最后使用默认值（仅用于测试）
        self.webhook_url = webhook_url or os.getenv('DINGTALK_WEBHOOK') or "https://oapi.dingtalk.com/robot/send?access_token=0b782dbef56eba11d5f2f136e4247ad5fb3d3022653adb3acd37bdf060b7dfcf"
        
    def send_report(self, html_content: str, chart_path: str = None, index_info: dict = None, processed_data: dict = None) -> bool:
        """
        发送报告到钉钉
        
        Args:
            html_content: HTML报告内容
            chart_path: 图表文件路径（可选）
            index_info: 指数信息字典（可选）
            processed_data: 处理后的数据字典（可选）
            
        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info("开始发送钉钉消息...")
            
            # 构造钉钉消息
            message = self._build_dingtalk_message(html_content, chart_path, index_info, processed_data)
            
            # 发送消息
            success = self._send_message(message)
            
            if success:
                logger.info("钉钉消息发送成功")
            else:
                logger.error("钉钉消息发送失败")
                
            return success
            
        except Exception as e:
            logger.error(f"钉钉消息发送过程中发生错误: {str(e)}")
            return False
    
    def _build_dingtalk_message(self, html_content: str, chart_path: str = None, index_info: dict = None, processed_data: dict = None) -> dict:
        """
        构造钉钉消息
        
        Args:
            html_content: HTML内容
            chart_path: 图表路径
            index_info: 指数信息字典
            processed_data: 处理后的数据字典
            
        Returns:
            dict: 钉钉消息字典
        """
        # 提取报告中的关键信息
        metrics = self._extract_metrics_from_html(html_content, processed_data)
        
        # 获取指数信息
        index_name = index_info.get('name', '未知指数') if index_info else '中证红利低波指数'
        index_code = index_info.get('code', '') if index_info else ''
        
        # 构造消息内容
        title = f"📈 {index_name}投研报告 - {datetime.now().strftime('%Y-%m-%d')}"
        if index_code:
            title += f" ({index_code})"
        
        # 构造Markdown消息
        markdown_content = f"""
## {title}

📊 **核心指标**
- 当前股息率: **{metrics.get('current_rate', 'N/A')}%**
- 15日均值: **{metrics.get('avg_15d', 'N/A')}%**
- 历史范围: **{metrics.get('min_15d', 'N/A')}%** ~ **{metrics.get('max_15d', 'N/A')}%**
- 日变化: **{metrics.get('change_percent', 'N/A')}%**
- 历史分位数: **{metrics.get('percentile_15d', 'N/A')}%**

🎯 **趋势分析**
{metrics.get('trend_analysis', '数据不足，无法进行趋势分析')}

💡 **投资参考**
{metrics.get('investment_advice', '建议结合其他技术指标和基本面分析做投资决策')}

---
📈 *AI投研助手自动推送*
"""
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown_content
            }
        }
        
        return message
    
    def _extract_metrics_from_html(self, html_content: str, processed_data: dict = None) -> dict:
        """
        从HTML中提取关键指标
        
        Args:
            html_content: HTML内容
            processed_data: 处理后的数据字典
            
        Returns:
            dict: 提取的指标字典
        """
        metrics = {}
        
        # 从处理后的数据中提取真实指标
        if processed_data and 'metrics' in processed_data:
            data_metrics = processed_data['metrics']
            metrics.update({
                'current_rate': f"{data_metrics.get('current_rate', 0):.4f}",
                'avg_15d': f"{data_metrics.get('avg_15d', 0):.4f}",
                'max_15d': f"{data_metrics.get('max_15d', 0):.4f}",
                'min_15d': f"{data_metrics.get('min_15d', 0):.4f}",
                'change_percent': f"{data_metrics.get('change_percent', 0):+.2f}",
                'percentile_15d': f"{data_metrics.get('percentile_15d', 0):.1f}",
                'trend_analysis': self._get_trend_analysis(data_metrics),
                'investment_advice': self._get_investment_advice(data_metrics)
            })
        else:
            # 默认值（用于测试）
            metrics.update({
                'current_rate': '5.0200',
                'avg_15d': '5.0200',
                'max_15d': '5.0900',
                'min_15d': '4.9900',
                'change_percent': '+0.60',
                'percentile_15d': '30.0',
                'trend_analysis': '当前股息率略高于15日均值，处于历史中等偏低水平',
                'investment_advice': '股息率处于合理区间，建议关注市场整体走势'
            })
        
        return metrics
    
    def _get_trend_analysis(self, metrics: dict) -> str:
        """生成趋势分析文本"""
        current = metrics.get('current_rate', 0)
        avg = metrics.get('avg_15d', 0)
        percentile = metrics.get('percentile_15d', 50)
        
        if current > avg:
            trend = "当前股息率高于15日均值"
        elif current < avg:
            trend = "当前股息率低于15日均值"
        else:
            trend = "当前股息率等于15日均值"
            
        if percentile > 70:
            level = "历史较高水平"
        elif percentile < 30:
            level = "历史较低水平"
        else:
            level = "历史中等水平"
            
        return f"{trend}，处于{level}"
    
    def _get_investment_advice(self, metrics: dict) -> str:
        """生成投资建议"""
        percentile = metrics.get('percentile_15d', 50)
        
        if percentile > 70:
            return "股息率处于历史高位，可考虑适度关注"
        elif percentile < 30:
            return "股息率处于历史低位，具有配置价值"
        else:
            return "股息率处于合理区间，建议关注市场整体走势"
    
    def _send_message(self, message: dict) -> bool:
        """
        发送钉钉消息
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            logger.debug(f"钉钉API响应: {result}")
            
            if result.get('errcode') == 0:
                return True
            else:
                logger.error(f"钉钉API错误: {result.get('errmsg')}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"钉钉消息发送网络错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"钉钉消息发送未知错误: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试钉钉机器人连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            test_message = {
                "msgtype": "text",
                "text": {
                    "content": f"🔔 AI投研助手连接测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n📊 股息率分析报告已生成，请查收！"
                }
            }
            
            success = self._send_message(test_message)
            
            if success:
                logger.info("钉钉机器人连接测试成功")
            else:
                logger.error("钉钉机器人连接测试失败")
                
            return success
            
        except Exception as e:
            logger.error(f"钉钉机器人连接测试异常: {str(e)}")
            return False

# 钉钉消息类型常量
DINGTALK_MSG_TYPES = {
    'text': 'text',
    'link': 'link', 
    'markdown': 'markdown',
    'actionCard': 'actionCard',
    'feedCard': 'feedCard'
}