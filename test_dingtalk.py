#!/usr/bin/env python3
"""
极简钉钉测试 - 只测试发送功能，不包含复杂逻辑
"""

import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('test_dingtalk.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== 开始极简钉钉测试 ===")
    
    # 获取 webhook
    webhook = os.getenv('DINGTALK_WEBHOOK')
    if not webhook:
        logger.error("❌ 未找到 DINGTALK_WEBHOOK")
        return 1
    
    logger.info(f"✅ 找到 webhook: {webhook[:50]}...")
    
    # 测试导入
    try:
        from dingtalk_sender import DingTalkSender
        logger.info("✅ 成功导入 DingTalkSender")
    except Exception as e:
        logger.error(f"❌ 导入失败: {e}")
        return 1
    
    # 测试发送简单消息
    try:
        sender = DingTalkSender(webhook_url=webhook)
        logger.info("✅ 创建发送器成功")
        
        # 测试连接（发送测试消息）
        logger.info("📤 发送测试消息...")
        test_result = sender.test_connection()
        if test_result:
            logger.info("✅ 测试消息发送成功")
        else:
            logger.error("❌ 测试消息发送失败")
        
        # 直接发送简单报告
        logger.info("📤 发送简单报告...")
        html_content = "<h1>测试报告</h1><p>这是一个测试报告</p>"
        
        # 构造指数信息
        index_info = {
            'name': '测试指数',
            'code': 'TEST001',
            'description': '测试用指数'
        }
        
        # 构造处理数据
        processed_data = {
            'metrics': {
                'current_rate': 5.0,
                'avg_15d': 4.9,
                'max_15d': 5.1,
                'min_15d': 4.8,
                'change_percent': 0.5,
                'percentile_15d': 50.0
            }
        }
        
        report_result = sender.send_report(
            html_content,
            chart_path=None,
            index_info=index_info,
            processed_data=processed_data
        )
        
        if report_result:
            logger.info("✅ 简单报告发送成功")
        else:
            logger.error("❌ 简单报告发送失败")
        
        logger.info("=== 测试完成 ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
