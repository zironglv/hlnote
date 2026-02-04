"""
报告生成模块 - 负责生成图表和HTML报告
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
from typing import Dict, Tuple
import base64
from io import BytesIO

# 设置中文字体 - 支持GitHub Actions环境
import matplotlib
import sys

# 配置日志（提前定义，避免循环依赖）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 清理matplotlib字体缓存（兼容不同版本）
import matplotlib.font_manager
try:
    # 新版本matplotlib
    matplotlib.font_manager._rebuild()
except AttributeError:
    # 旧版本matplotlib或其他情况
    pass
except Exception as e:
    logger.warning(f"字体缓存重建失败: {e}")

# 检查是否在GitHub Actions环境中
if 'GITHUB_ACTIONS' in os.environ:
    # GitHub Actions环境，使用系统可用的中文字体
    try:
        # 尝试使用STHeiti或Songti等系统自带中文字体
        plt.rcParams['font.sans-serif'] = ['STHeiti', 'Songti SC', 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        # 设置字体大小
        plt.rcParams['font.size'] = 12
        logger.info("GitHub Actions环境使用STHeiti/Songti中文字体")
    except Exception as e:
        logger.warning(f"GitHub Actions中文字体设置失败: {e}")
        # 使用默认字体
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
else:
    # 本地环境，使用系统可用的中文字体
    try:
        # 优先使用STHeiti，其次是Songti，然后是系统默认字体
        plt.rcParams['font.sans-serif'] = ['STHeiti', 'Songti SC', 'Kaiti SC', 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        logger.info("本地环境使用STHeiti/Songti中文字体")
    except Exception as e:
        logger.warning(f"本地中文字体设置失败: {e}")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

# 全局设置
plt.rcParams['figure.autolayout'] = True

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
    
    def generate_report(self, analysis_data: Dict, output_dir: str = None) -> Tuple[str, str]:
        """
        生成完整报告
        
        Args:
            analysis_data: 分析数据字典
            output_dir: 输出目录，如果提供则使用此目录
            
        Returns:
            Tuple[str, str]: (HTML报告内容, 图表文件路径)
        """
        try:
            logger.info("开始生成报告...")
            
            # 确定输出目录
            target_output_dir = output_dir or self.output_dir
            
            # 生成图表
            chart_path = self.generate_chart(analysis_data['processed_data'], target_output_dir)
            
            # 生成HTML报告
            html_content = self.generate_html_report(analysis_data, chart_path, target_output_dir)
            
            logger.info("报告生成完成")
            
            # 保存HTML报告到文件
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                report_path = os.path.join(output_dir, 'index.html')
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML报告已保存到: {report_path}")
            
            return html_content, chart_path
            
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            raise Exception(f"报告生成过程中发生错误: {str(e)}")
    
    def generate_chart(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """
        生成股息率趋势图
        
        Args:
            df: 处理后的数据框
            output_dir: 输出目录，如果提供则使用此目录
            
        Returns:
            str: 图表文件路径
        """
        try:
            if 'dividend_rate' not in df.columns or 'date' not in df.columns:
                logger.warning("数据中缺少必要的列，无法生成图表")
                return ""
            
            # 准备数据
            dates = df['date']
            rates = df['dividend_rate']
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 绘制折线图
            ax.plot(dates, rates, marker='o', linewidth=2, markersize=6, color='#2E86AB')
            
            # 添加网格
            ax.grid(True, alpha=0.3)
            
            # 设置标题和标签
            ax.set_title('中证红利低波指数股息率趋势 (15日)', fontsize=16, pad=20)
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('股息率 (%)', fontsize=12)
            
            # 格式化x轴日期
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.xticks(rotation=45)
            
            # 调整Y轴范围，避免标签被截断
            y_min, y_max = rates.min(), rates.max()
            y_range = y_max - y_min
            ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.15)
            
            # 添加数值标签（优化位置，避免重叠）
            for i, (date, rate) in enumerate(zip(dates, rates)):
                # 根据位置调整标签位置
                offset_y = 10 if i % 2 == 0 else -15
                ax.annotate(f'{rate:.3f}', (date, rate), 
                           textcoords="offset points", xytext=(0, offset_y), ha='center',
                           fontsize=8, color='#2E86AB',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor='none'))            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            target_output_dir = output_dir or self.output_dir
            # 确保输出目录存在
            os.makedirs(target_output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_filename = f'dividend_trend_{timestamp}.png'
            chart_path = os.path.join(target_output_dir, chart_filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"图表已保存至: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"图表生成失败: {str(e)}")
            return ""
    
    def generate_html_report(self, analysis_data: Dict, chart_path: str, output_dir: str = None) -> str:
        """
        生成HTML报告
        
        Args:
            analysis_data: 分析数据
            chart_path: 图表路径
            output_dir: 输出目录
            
        Returns:
            str: HTML内容
        """
        metrics = analysis_data.get('metrics', {})
        trend_analysis = self._get_trend_analysis_text(metrics)
        
        # 读取图表并转为base64
        chart_base64 = ""
        if os.path.exists(chart_path):
            with open(chart_path, 'rb') as f:
                chart_base64 = base64.b64encode(f.read()).decode()
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>中证红利低波指数投研报告</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2E86AB; }}
                .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
                .metric-subtext {{ font-size: 12px; color: #888; margin-top: 2px; }}
                .chart-container {{ text-align: center; margin: 30px 0; }}
                .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .analysis {{ background: #e8f4f8; border-left: 4px solid #2E86AB; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
                .trend-indicator {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
                .trend-up {{ background: #d4edda; color: #155724; }}
                .trend-down {{ background: #f8d7da; color: #721c24; }}
                .trend-flat {{ background: #fff3cd; color: #856404; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 中证红利低波指数投研报告</h1>
                    <p>基于股息率的量化分析 | 更新时间: {analysis_data.get('analysis_time', 'N/A')}</p>
                </div>
                
                <div class="content">
                    <h2>📊 核心指标</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('current_rate', 0):.4f}%</div>
                            <div class="metric-label">当前股息率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('avg_15d', 0):.4f}%</div>
                            <div class="metric-label">15日均值</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('max_15d', 0):.4f}%</div>
                            <div class="metric-label">15日最高</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('min_15d', 0):.4f}%</div>
                            <div class="metric-label">15日最低</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('change_percent', 0):+.2f}%</div>
                            <div class="metric-label">日变化率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('percentile_15d', 0):.1f}%</div>
                            <div class="metric-label">历史分位数</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{self._format_metric(metrics.get('bond_yield'), 'N/A', '.2f')}%</div>
                            <div class="metric-label">国债收益率</div>
                            {'<div class="metric-subtext">10年期</div>' if metrics.get('bond_name') else ''}
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{self._format_metric(metrics.get('dividend_bond_spread'), 'N/A', '.2f')}%</div>
                            <div class="metric-label">股息率溢价</div>
                            {'<div class="metric-subtext">' + ('优势' if metrics.get('dividend_bond_spread', 0) > 0 else '劣势') + '</div>' if metrics.get('dividend_bond_spread') is not None else ''}
                        </div>
                    </div>
                    
                    <div class="analysis">
                        <h3>🎯 趋势分析</h3>
                        <p>{trend_analysis}</p>
                        <span class="trend-indicator trend-{'up' if metrics.get('daily_change', 0) > 0 else 'down' if metrics.get('daily_change', 0) < 0 else 'flat'}">
                            {'📈 上升趋势' if metrics.get('daily_change', 0) > 0 else '📉 下降趋势' if metrics.get('daily_change', 0) < 0 else '➡️ 横盘整理'}
                        </span>
                    </div>
                    
                    <div class="chart-container">
                        <h3>📈 股息率趋势图 (15日)</h3>
                        {'<img src="data:image/png;base64,' + chart_base64 + '" alt="股息率趋势图">' if chart_base64 else '<p>图表生成失败</p>'}
                    </div>
                    
                    <div class="analysis">
                        <h3>💡 多指标综合分析</h3>
                        <ul>
                            <li>股息率分析：当前股息率相对15日均值{'偏高' if metrics.get('current_rate', 0) > metrics.get('avg_15d', 0) else '偏低'}，历史分位数为{metrics.get('percentile_15d', 0):.1f}%，处于{'较高' if metrics.get('percentile_15d', 50) > 70 else '较低' if metrics.get('percentile_15d', 50) < 30 else '中等'}水平</li>
                            {'<li>估值分析：PE估值' + ('较低' if metrics.get('pe', 20) < 15 else '较高' if metrics.get('pe', 20) > 25 else '合理') + f'({metrics.get("pe", "N/A")}倍)</li>' if metrics.get('pe') else ''}
                            {'<li>国债对比：股息率相对10年期国债收益率' + ('有显著优势' if metrics.get('dividend_bond_spread', 0) > 1.0 else '基本相当' if metrics.get('dividend_bond_spread', 0) > 0 else '处于劣势') + f'(差额{metrics.get("dividend_bond_spread", 0):.2f}%)</li>' if metrics.get('dividend_bond_spread') is not None else ''}
                        </ul>
                    </div>
                    
                    <div class="analysis" style="background: #e8f4f8; border-left: 4px solid #2E86AB;">
                        <h3>🎯 投资决策建议</h3>
                        {'<div style="margin: 15px 0;">' + 
                         '<div style="font-size: 20px; font-weight: bold; color: ' + ('#28a745' if metrics.get('investment_advice', {}).get('action') == '买入' else '#ffc107' if metrics.get('investment_advice', {}).get('action') == '持有' else '#dc3545') + '; margin-bottom: 10px;">' +
                         ('🟢 建议买入' if metrics.get('investment_advice', {}).get('action') == '买入' else '🟡 建议持有' if metrics.get('investment_advice', {}).get('action') == '持有' else '🔴 建议卖出') + '</div>' +
                         '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">' +
                         '<strong>信心度：</strong>' + f'{metrics.get("investment_advice", {}).get("confidence", 0.5):.1%}' + '<br>' +
                         '<div style="background: #e9ecef; height: 10px; border-radius: 5px; margin: 5px 0 10px 0; overflow: hidden;">' +
                         '<div style="background: ' + ('#28a745' if metrics.get('investment_advice', {}).get('action') == '买入' else '#ffc107' if metrics.get('investment_advice', {}).get('action') == '持有' else '#dc3545') + f'; width: {metrics.get("investment_advice", {}).get("confidence", 0.5) * 100}%; height: 100%;"></div>' +
                         '</div>' +
                         '<strong>理由：</strong>' + (', '.join(metrics.get('investment_advice', {}).get('reasons', ['基于综合分析'])) if metrics.get('investment_advice', {}).get('reasons') else '基于综合分析') + '<br>' +
                         '<strong>风险：</strong>' + (', '.join(metrics.get('investment_advice', {}).get('risks', ['市场波动风险'])) if metrics.get('investment_advice', {}).get('risks') else '市场波动风险') + '<br>' +
                         '<strong>摘要：</strong>' + metrics.get('investment_advice', {}).get('summary', '建议结合个人风险承受能力做投资决策') +
                         '</div>' +
                         '</div>' if metrics.get('investment_advice') else '<p>投资决策建议生成中...</p>'}
                    </div>
                </div>
                
                <div class="footer">
                    <p>AI投研助手自动生成 | 数据来源：中证指数公司 | 仅供参考，投资有风险</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _get_trend_analysis_text(self, metrics: Dict) -> str:
        """生成趋势分析文本"""
        current = metrics.get('current_rate', 0)
        avg_15d = metrics.get('avg_15d', 0)
        percentile = metrics.get('percentile_15d', 50)
        change = metrics.get('change_percent', 0)
        
        analysis_parts = []
        
        # 相对均值分析
        if current > avg_15d:
            analysis_parts.append(f"当前股息率({current:.4f}%)高于15日均值({avg_15d:.4f}%)")
        else:
            analysis_parts.append(f"当前股息率({current:.4f}%)低于15日均值({avg_15d:.4f}%)")
        
        # 分位数分析
        if percentile > 70:
            analysis_parts.append(f"处于历史较高水平(分位数{percentile:.1f}%)")
        elif percentile < 30:
            analysis_parts.append(f"处于历史较低水平(分位数{percentile:.1f}%)")
        else:
            analysis_parts.append(f"处于历史中等水平(分位数{percentile:.1f}%)")
        
        # 日变化分析
        if abs(change) > 0.1:
            direction = "上升" if change > 0 else "下降"
            analysis_parts.append(f"日内{direction}{abs(change):.2f}%")
        
        return "，".join(analysis_parts) + "。"
    
    def _format_metric(self, value, default='N/A', format_spec=''):
        """格式化指标值，处理None和异常"""
        if value is None:
            return default
        try:
            if format_spec:
                return format(value, format_spec)
            return str(value)
        except (ValueError, TypeError):
            return default
    
    def generate_daily_report(self, analysis_data: Dict, chart_path: str = None) -> str:
        """
        生成日报简洁版（用于钉钉消息等场景）
        
        Args:
            analysis_data: 分析数据字典
            chart_path: 图表路径（可选）
            
        Returns:
            str: 日报简洁版HTML内容
        """
        metrics = analysis_data.get('metrics', {})
        index_info = analysis_data.get('index_info', {})
        
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
        
        # 趋势箭头
        change_percent = metrics.get('change_percent', 0)
        if isinstance(change_percent, str):
            try:
                change_percent = float(change_percent.replace('+', '').replace('%', ''))
            except:
                change_percent = 0
        
        trend_arrow = '📈' if change_percent > 0 else '📉' if change_percent < 0 else '➡️'
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>AI投研日报 - 简洁版</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 15px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); color: white; padding: 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 20px; }}
                .header p {{ margin: 5px 0 0 0; opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 20px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 15px 0; }}
                .metric-card {{ background: #f8f9fa; border-radius: 6px; padding: 15px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 18px; font-weight: bold; color: #2E86AB; }}
                .metric-label {{ font-size: 12px; color: #666; margin-top: 3px; }}
                .advice-section {{ background: #e8f4f8; border-radius: 8px; padding: 15px; margin: 15px 0; }}
                .advice-title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2E86AB; }}
                .advice-action {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .buy {{ color: #28a745; }}
                .hold {{ color: #ffc107; }}
                .sell {{ color: #dc3545; }}
                .confidence-bar {{ background: #e9ecef; height: 8px; border-radius: 4px; margin: 8px 0; overflow: hidden; }}
                .confidence-fill {{ height: 100%; }}
                .footer {{ text-align: center; padding: 15px; color: #666; font-size: 11px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 AI投研日报</h1>
                    <p>{index_info.get('name', '中证指数')} | {analysis_data.get('analysis_time', '')}</p>
                </div>
                
                <div class="content">
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{float(metrics.get('current_rate', 0)):.2f}% {trend_arrow}</div>
                            <div class="metric-label">股息率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('pe', 'N/A') if metrics.get('pe') else 'N/A'}</div>
                            <div class="metric-label">PE估值</div>
                        </div>
                        
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('dividend_bond_spread', 'N/A') if metrics.get('dividend_bond_spread') else 'N/A'}%</div>
                            <div class="metric-label">国债溢价</div>
                        </div>
                    </div>
                    
                    <div class="advice-section">
                        <div class="advice-title">🎯 投资建议</div>
                        <div class="advice-action {action}">
                            {'🟢 建议买入' if action == '买入' else '🟡 建议持有' if action == '持有' else '🔴 建议卖出'}
                        </div>
                        
                        <div style="margin: 10px 0;">
                            <div style="font-size: 14px; margin-bottom: 5px;">信心度: {confidence:.1%}</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: {confidence * 100}%; background: {'#28a745' if action == '买入' else '#ffc107' if action == '持有' else '#dc3545'};"></div>
                            </div>
                        </div>
                        
                        <div style="font-size: 13px; line-height: 1.4;">
                            {summary if summary else '基于多指标综合分析'}
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 15px 0; font-size: 12px; color: #666;">
                        💡 点击查看完整分析报告，获取详细图表和历史数据
                    </div>
                </div>
                
                <div class="footer">
                    <p>AI投研助手自动生成 | 数据仅供参考，投资有风险</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template