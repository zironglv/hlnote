#!/usr/bin/env python3
"""
调试脚本：模拟GitHub Actions环境来测试整个流程
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_github_action.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """模拟GitHub Actions执行流程"""
    logger.info("=== 开始调试GitHub Actions环境 ===")
    
    # 1. 检查环境变量
    logger.info("1. 检查环境变量配置")
    dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK')
    if dingtalk_webhook:
        logger.info(f"✅ DINGTALK_WEBHOOK 已设置 (长度: {len(dingtalk_webhook)})")
        logger.info(f"Webhook域名: {dingtalk_webhook.split('/')[2] if '/' in dingtalk_webhook else 'unknown'}")
    else:
        logger.warning("⚠️ DINGTALK_WEBHOOK 未设置")
    
    # 2. 检查网络连接
    logger.info("\n2. 检查网络连接")
    try:
        import requests
        response = requests.get('https://www.baidu.com', timeout=5)
        logger.info(f"✅ 百度访问正常 (状态码: {response.status_code})")
    except Exception as e:
        logger.error(f"❌ 网络连接问题: {str(e)}")
    
    # 3. 测试数据源访问
    logger.info("\n3. 测试数据源访问")
    test_urls = [
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls"
    ]
    
    for i, url in enumerate(test_urls, 1):
        try:
            logger.info(f"测试数据源 {i}: {url}")
            response = requests.get(url, timeout=10)
            logger.info(f"✅ 数据源{i}访问成功 (状态码: {response.status_code}, 大小: {len(response.content)} bytes)")
            
            # 尝试解析Excel
            import pandas as pd
            import io
            df = pd.read_excel(io.BytesIO(response.content))
            logger.info(f"✅ Excel解析成功，数据形状: {df.shape}")
            logger.info(f"列名: {list(df.columns)}")
            
        except Exception as e:
            logger.error(f"❌ 数据源{i}访问失败: {str(e)}")
    
    # 4. 测试钉钉连接
    logger.info("\n4. 测试钉钉机器人连接")
    if dingtalk_webhook:
        try:
            from dingtalk_sender import DingTalkSender
            sender = DingTalkSender(webhook_url=dingtalk_webhook)
            logger.info("🧪 发送测试消息...")
            success = sender.test_connection()
            if success:
                logger.info("✅ 钉钉机器人连接测试成功")
            else:
                logger.error("❌ 钉钉机器人连接测试失败")
        except Exception as e:
            logger.error(f"❌ 钉钉测试异常: {str(e)}")
    else:
        logger.warning("⚠️ 无钉钉Webhook配置，跳过测试")
    
    # 5. 模拟完整的分析流程
    logger.info("\n5. 模拟完整分析流程")
    try:
        from multi_index_analyzer import MultiIndexAnalyzer
        from index_config import index_manager
        
        indexes = index_manager.get_all_indexes()
        logger.info(f"配置的指数数量: {len(indexes)}")
        
        # 使用环境变量中的Webhook
        analyzer = MultiIndexAnalyzer(indexes, send_summary=False, dingtalk_webhook=dingtalk_webhook)
        
        logger.info("开始执行分析...")
        analysis_results, send_results = analyzer.run_full_analysis()
        
        # 输出结果统计
        success_count = sum(1 for r in analysis_results if r.success)
        sent_count = sum(1 for sent in send_results.values() if sent)
        
        logger.info(f"=== 分析完成 ===")
        logger.info(f"成功分析: {success_count}/{len(indexes)} 个指数")
        logger.info(f"成功发送: {sent_count}/{len(indexes)} 个报告")
        
        # 详细结果
        for result in analysis_results:
            status = "✓" if result.success else "✗"
            sent_status = "📤" if send_results.get(result.index_config.code, False) else "📭"
            logger.info(f"{status} {sent_status} {result.index_config.name}")
            if not result.success:
                logger.error(f"  错误: {result.error_message}")
                
    except Exception as e:
        logger.error(f"❌ 完整流程执行失败: {str(e)}")
        logger.exception("详细错误信息:")
    
    logger.info("=== 调试完成 ===")

if __name__ == "__main__":
    main()