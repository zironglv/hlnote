#!/usr/bin/env python3
"""
AI投研助手 - 主程序入口
功能：每日定时获取中证红利低波指数CSV数据，生成分析报告并通过邮件发送
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector
from data_processor import DataProcessor  
from report_generator import ReportGenerator
from dingtalk_sender import DingTalkSender
import local_config as config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dividend_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        logger.info("=== AI投研助手开始执行 ===")
        
        # 1. 数据收集
        collector = DataCollector(csv_url=config.CSV_URL)
        csv_data = collector.fetch_csv_data()
        
        # 2. 数据处理
        processor = DataProcessor()
        processed_data = processor.analyze_data(csv_data)
        
        # 3. 报告生成
        generator = ReportGenerator()
        report_html, chart_path = generator.generate_report(processed_data)
        
        # 4. 钉钉发送
        sender = DingTalkSender()
        success = sender.send_report(report_html, chart_path)
        
        if success:
            logger.info("=== 报告发送成功 ===")
        else:
            logger.error("=== 报告发送失败 ===")
            
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()