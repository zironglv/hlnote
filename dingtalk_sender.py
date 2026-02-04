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
            
            # 构造钉钉消息（使用日报简洁版）
            message = self._build_dingtalk_message(html_content, chart_path, index_info, processed_data)            
            # 发送消息
            success = self._send_message(message)
            
            if success:
                logger.info("钉钉消息发送成功")
            else:
                logger.error("钉钉消息发送失败")
                
            return success
            
        except Exception as e:
            import traceback
            logger.error(f"钉钉消息发送过程中发生错误: {str(e)}")
            logger.error(f"错误堆栈: {traceback.format_exc()}")
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
        
        # 使用ReportGenerator生成日报简洁版HTML
        from report_generator import ReportGenerator
        report_generator = ReportGenerator()
        daily_report_html = report_generator.generate_daily_report({
            'metrics': metrics,
            'index_info': index_info,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 构造Markdown消息（双层级日报格式）
        markdown_content = self._build_daily_report_markdown(title, metrics, index_info, processed_data)
        
        # 保存日报简洁版到文件
        try:
            import os
            report_dir = "reports/daily"
            os.makedirs(report_dir, exist_ok=True)
            daily_report_path = os.path.join(report_dir, f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(daily_report_path, 'w', encoding='utf-8') as f:
                f.write(daily_report_html)
            logger.info(f"日报简洁版已保存: {daily_report_path}")
        except Exception as e:
            logger.warning(f"保存日报简洁版失败: {str(e)}")
        
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
            # 确保数值类型正确
            try:
                current_rate = float(data_metrics.get('current_rate', 0))
                avg_15d = float(data_metrics.get('avg_15d', 0))
                max_15d = float(data_metrics.get('max_15d', 0))
                min_15d = float(data_metrics.get('min_15d', 0))
                change_percent = float(data_metrics.get('change_percent', 0))
                percentile_15d = float(data_metrics.get('percentile_15d', 0))
                
                # 创建转换后的指标字典供趋势分析和投资建议使用
                converted_metrics = {
                    'current_rate': current_rate,
                    'avg_15d': avg_15d,
                    'max_15d': max_15d,
                    'min_15d': min_15d,
                    'change_percent': change_percent,
                    'percentile_15d': percentile_15d,
                    'pe': data_metrics.get('pe'),
                    'pb': data_metrics.get('pb'),
                    'pe_percentile': data_metrics.get('pe_percentile'),
                    'pb_percentile': data_metrics.get('pb_percentile'),
                    'bond_yield': data_metrics.get('bond_yield'),
                    'dividend_bond_spread': data_metrics.get('dividend_bond_spread'),
                    'investment_advice': data_metrics.get('investment_advice')
                }
                
                metrics.update({
                    'current_rate': f"{current_rate:.4f}",
                    'avg_15d': f"{avg_15d:.4f}",
                    'max_15d': f"{max_15d:.4f}",
                    'min_15d': f"{min_15d:.4f}",
                    'change_percent': f"{change_percent:+.2f}",
                    'percentile_15d': f"{percentile_15d:.1f}",
                    'trend_analysis': self._get_trend_analysis(converted_metrics),
                    'investment_advice': self._get_investment_advice(converted_metrics)
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"数据转换失败，使用默认值: {e}")
                # 使用默认值（数值类型）
                default_metrics = {
                    'current_rate': 5.0200,
                    'avg_15d': 5.0200,
                    'max_15d': 5.0900,
                    'min_15d': 4.9900,
                    'change_percent': 0.60,
                    'percentile_15d': 30.0
                }
                metrics.update({
                    'current_rate': f"{default_metrics['current_rate']:.4f}",
                    'avg_15d': f"{default_metrics['avg_15d']:.4f}",
                    'max_15d': f"{default_metrics['max_15d']:.4f}",
                    'min_15d': f"{default_metrics['min_15d']:.4f}",
                    'change_percent': f"{default_metrics['change_percent']:+.2f}",
                    'percentile_15d': f"{default_metrics['percentile_15d']:.1f}",
                    'trend_analysis': self._get_trend_analysis(default_metrics),
                    'investment_advice': self._get_investment_advice(default_metrics)
                })
        else:
            # 默认值（用于测试，数值类型）
            default_metrics = {
                'current_rate': 5.0200,
                'avg_15d': 5.0200,
                'max_15d': 5.0900,
                'min_15d': 4.9900,
                'change_percent': 0.60,
                'percentile_15d': 30.0
            }
            metrics.update({
                'current_rate': f"{default_metrics['current_rate']:.4f}",
                'avg_15d': f"{default_metrics['avg_15d']:.4f}",
                'max_15d': f"{default_metrics['max_15d']:.4f}",
                'min_15d': f"{default_metrics['min_15d']:.4f}",
                'change_percent': f"{default_metrics['change_percent']:+.2f}",
                'percentile_15d': f"{default_metrics['percentile_15d']:.1f}",
                'trend_analysis': self._get_trend_analysis(default_metrics),
                'investment_advice': self._get_investment_advice(default_metrics)
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

    def _build_daily_report_markdown(self, title: str, metrics: dict, index_info: dict = None, processed_data: dict = None) -> str:
        """
        构建日报格式的Markdown消息（包含国债收益率对比）
        
        Args:
            title: 消息标题
            metrics: 指标数据
            index_info: 指数信息
            processed_data: 处理后的数据
            
        Returns:
            str: Markdown格式的消息内容
        """
        # 获取投资建议
        investment_advice = metrics.get('investment_advice', {})
        if isinstance(investment_advice, dict):
            action = investment_advice.get('action', '持有')
            confidence = investment_advice.get('confidence', 0.5)
            summary = investment_advice.get('summary', '')
        else:
            action = '持有'
            confidence = 0.5
            summary = ''
        
        # 获取指数名称和代码
        index_name = index_info.get('name', '未知指数') if index_info else '中证红利低波指数'
        index_code = index_info.get('code', '') if index_info else ''
        
        # 构造趋势箭头
        change_percent = metrics.get('change_percent', 0)
        if isinstance(change_percent, str):
            try:
                change_percent = float(change_percent.replace('+', '').replace('%', ''))
            except:
                change_percent = 0
        
        trend_arrow = '📈' if change_percent > 0 else '📉' if change_percent < 0 else '➡️'
        
        # 获取估值数据
        pe = metrics.get('pe')
        pb = metrics.get('pb')
        pe_percentile = metrics.get('pe_percentile')
        pb_percentile = metrics.get('pb_percentile')
        
        # 获取国债收益率对比数据
        bond_yield = metrics.get('bond_yield')
        dividend_bond_spread = metrics.get('dividend_bond_spread')
        
        # 构建核心指标卡片
        core_metrics_section = f"""
📊 **核心指标卡片**
- 股息率: **{metrics.get('current_rate', 'N/A')}%** {trend_arrow} {metrics.get('change_percent', 'N/A')}%
- PE估值: **{pe if pe is not None else 'N/A'}倍** {'(低位)' if pe_percentile and pe_percentile < 30 else '(高位)' if pe_percentile and pe_percentile > 70 else ''}
- PB估值: **{pb if pb is not None else 'N/A'}倍** {'(低位)' if pb_percentile and pb_percentile < 30 else '(高位)' if pb_percentile and pb_percentile > 70 else ''}
- 国债对比: **{dividend_bond_spread if dividend_bond_spread is not None else 'N/A'}%** {'📈' if dividend_bond_spread and dividend_bond_spread > 0 else '📉' if dividend_bond_spread and dividend_bond_spread < 0 else '➡️'}
"""
        
        # 构建趋势分析
        # 安全获取数值类型
        try:
            percentile_val = float(metrics.get('percentile_15d', 50))
        except (ValueError, TypeError):
            percentile_val = 50.0
        
        trend_section = f"""
🎯 **趋势分析**
- 股息率历史分位数: **{metrics.get('percentile_15d', 'N/A')}%** {'(高位)' if percentile_val > 70 else '(低位)' if percentile_val < 30 else '(中位)'}
- 15日范围: **{metrics.get('min_15d', 'N/A')}%** ~ **{metrics.get('max_15d', 'N/A')}%**
- 15日均值: **{metrics.get('avg_15d', 'N/A')}%**
"""
        
        # 构建投资建议
        action_emoji = '🟢' if action == '买入' else '🟡' if action == '持有' else '🔴'
        
        # 安全处理confidence变量，确保是数值类型
        try:
            confidence_value = float(confidence) if confidence is not None else 0.5
        except (ValueError, TypeError):
            confidence_value = 0.5
        
        confidence_bar = '█' * int(confidence_value * 10) + '░' * (10 - int(confidence_value * 10))
        
        # 确保格式化安全
        confidence_percent = f"{confidence_value:.1%}" if isinstance(confidence_value, (int, float)) else "50.0%"
        
        advice_section = f"""
💡 **投资建议**
{action_emoji} **{action}** (信心度: {confidence_percent})
{confidence_bar}

📝 **理由摘要**
{summary}
"""
        
        # 构建完整消息
        markdown_content = f"""
## {title}

{core_metrics_section}

{trend_section}

{advice_section}

🔗 **查看更多**
📊 [完整分析报告](https://zironglv.github.io/hlnote/reports/{index_code}/index.html) | 📈 [历史数据](https://zironglv.github.io/hlnote/)

---
📈 *AI投研助手自动推送* | 数据仅供参考，投资有风险
"""
        
        return markdown_content
    
    def _get_trend_analysis(self, metrics: dict) -> str:
        """生成趋势分析文本（增强版）"""
        current = metrics.get('current_rate', 0)
        avg_15d = metrics.get('avg_15d', 0)
        percentile = metrics.get('percentile_15d', 50)
        change = metrics.get('change_percent', 0)
        
        analysis_parts = []
        
        # 安全处理数值变量，确保是数字类型
        try:
            current_value = float(current) if current is not None else 0.0
            avg_15d_value = float(avg_15d) if avg_15d is not None else 0.0
            percentile_value = float(percentile) if percentile is not None else 50.0
            change_value = float(change) if change is not None else 0.0
        except (ValueError, TypeError):
            current_value = 0.0
            avg_15d_value = 0.0
            percentile_value = 50.0
            change_value = 0.0
        
        # 相对均值分析
        current_formatted = f"{current_value:.4f}" if isinstance(current_value, (int, float)) else str(current_value)
        avg_formatted = f"{avg_15d_value:.4f}" if isinstance(avg_15d_value, (int, float)) else str(avg_15d_value)
        
        if current_value > avg_15d_value:
            analysis_parts.append(f"当前股息率({current_formatted}%)高于15日均值({avg_formatted}%)")
        elif current_value < avg_15d_value:
            analysis_parts.append(f"当前股息率({current_formatted}%)低于15日均值({avg_formatted}%)")
        else:
            analysis_parts.append(f"当前股息率({current_formatted}%)等于15日均值")
        
        # 分位数分析
        if percentile_value > 70:
            analysis_parts.append(f"处于历史较高水平(分位数{percentile_value:.1f}%)")
        elif percentile_value < 30:
            analysis_parts.append(f"处于历史较低水平(分位数{percentile_value:.1f}%)")
        else:
            analysis_parts.append(f"处于历史中等水平(分位数{percentile_value:.1f}%)")
        
        # 日变化分析
        if abs(change_value) > 0.1:
            direction = "上升" if change_value > 0 else "下降"
            analysis_parts.append(f"日内{direction}{abs(change_value):.2f}%")
        
        return "，".join(analysis_parts) + "。"
    
    def _get_investment_advice(self, metrics: dict) -> str:
        """生成投资建议（增强版）"""
        # 优先使用投资决策算法生成的建议
        investment_advice = metrics.get('investment_advice')
        if isinstance(investment_advice, dict):
            return investment_advice.get('summary', '建议结合其他技术指标和基本面分析做投资决策')
        
        # 备用逻辑
        percentile = metrics.get('percentile_15d', 50)
        pe = metrics.get('pe')
        bond_yield = metrics.get('bond_yield')
        
        advice_parts = []
        
        if percentile > 70:
            advice_parts.append("股息率处于历史高位，可考虑适度关注")
        elif percentile < 30:
            advice_parts.append("股息率处于历史低位，具有配置价值")
        
        if pe is not None:
            if pe < 12:
                advice_parts.append("PE估值较低，具备安全边际")
            elif pe > 20:
                advice_parts.append("PE估值较高，需注意风险")
        
        if bond_yield is not None and metrics.get('current_rate'):
            try:
                current_rate_value = float(metrics.get('current_rate', 0))
                spread = current_rate_value - bond_yield
                if spread > 1.0:
                    advice_parts.append(f"股息率显著高于国债收益率(差额{spread:.2f}%)")
                elif spread < 0:
                    advice_parts.append(f"股息率低于国债收益率(差额{spread:.2f}%)")
            except (ValueError, TypeError):
                logger.warning(f"无法计算股息率与国债收益率差值: current_rate={metrics.get('current_rate')}, bond_yield={bond_yield}")
        
        if not advice_parts:
            advice_parts.append("股息率处于合理区间，建议关注市场整体走势")
        
        return "；".join(advice_parts)

# 钉钉消息类型常量
DINGTALK_MSG_TYPES = {
    'text': 'text',
    'link': 'link', 
    'markdown': 'markdown',
    'actionCard': 'actionCard',
    'feedCard': 'feedCard'
}