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

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

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
            
            # 添加数值标签
            for i, (date, rate) in enumerate(zip(dates, rates)):
                ax.annotate(f'{rate:.4f}', (date, rate), 
                           textcoords="offset points", xytext=(0,10), ha='center',
                           fontsize=9, color='#2E86AB')
            
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
                        <h3>💡 投资参考</h3>
                        <ul>
                            <li>当前股息率相对15日均值{'偏高' if metrics.get('current_rate', 0) > metrics.get('avg_15d', 0) else '偏低'}</li>
                            <li>历史分位数为{metrics.get('percentile_15d', 0):.1f}%，处于{'较高' if metrics.get('percentile_15d', 50) > 70 else '较低' if metrics.get('percentile_15d', 50) < 30 else '中等'}水平</li>
                            <li>建议结合其他技术指标和基本面分析做投资决策</li>
                        </ul>
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