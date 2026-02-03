#!/usr/bin/env python3
"""
AI投研助手 - 多指数版本主程序
功能：每日定时获取多个中证指数数据，生成分析报告并通过钉钉分别发送
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_index_analyzer import MultiIndexAnalyzer, run_multi_index_analysis
from index_config import IndexConfig, index_manager
import local_config as config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_index_dividend_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数 - 多指数分析"""
    try:
        logger.info("=== AI投研助手(多指数版)开始执行 ===")
        
        # 系统健康检查
        import os
        import platform
        logger.info(f"🖥️  系统信息: {platform.system()} {platform.release()}")
        logger.info(f"🐍 Python版本: {platform.python_version()}")
        
        # 检查钉钉Webhook配置
        dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK')
        if dingtalk_webhook:
            logger.info(f"✅ 检测到 DINGTALK_WEBHOOK 环境变量 (长度: {len(dingtalk_webhook)} 字符)")
            # 隐藏敏感信息，只显示域名部分
            if 'access_token=' in dingtalk_webhook:
                token_start = dingtalk_webhook.find('access_token=') + 13
                token_end = min(token_start + 8, len(dingtalk_webhook))
                masked_url = dingtalk_webhook[:token_start] + '...' + dingtalk_webhook[token_end:]
                logger.info(f"🔗 Webhook URL: {masked_url}")
        else:
            logger.warning("⚠️ 未找到 DINGTALK_WEBHOOK 环境变量，将使用默认Webhook")
        
        # 检查网络连通性
        try:
            import requests
            response = requests.get('https://www.baidu.com', timeout=5)
            logger.info("🌐 网络连接正常")
        except Exception as e:
            logger.warning(f"⚠️ 网络连接可能存在问题: {str(e)}")
        
        # 获取所有配置的指数
        indexes = index_manager.get_all_indexes()
        logger.info(f"📊 配置的指数数量: {len(indexes)}")
        for idx in indexes:
            logger.info(f"- {idx.name} ({idx.code}): {idx.url}")
        
        # 测试钉钉连接
        if dingtalk_webhook:
            from dingtalk_sender import DingTalkSender
            test_sender = DingTalkSender(webhook_url=dingtalk_webhook)
            logger.info("🧪 测试钉钉机器人连接...")
            if test_sender.test_connection():
                logger.info("✅ 钉钉机器人连接测试成功")
            else:
                logger.error("❌ 钉钉机器人连接测试失败")
        
        # 运行多指数分析
        # 设置 send_summary=False 来只发送指数报告而不发送总结报告
        analyzer = MultiIndexAnalyzer(indexes, send_summary=False, dingtalk_webhook=dingtalk_webhook)
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
        logger.error(f"程序执行出错: {str(e)}")
        raise

def add_custom_index(name: str, code: str, url: str, description: str = ""):
    """
    添加自定义指数配置
    
    Args:
        name: 指数名称
        code: 指数代码
        url: 数据URL
        description: 描述
    """
    new_index = IndexConfig(
        name=name,
        code=code,
        url=url,
        description=description
    )
    index_manager.add_index(new_index)
    logger.info(f"已添加指数配置: {name} ({code})")

if __name__ == "__main__":
    # 示例：如何添加自定义指数
    # add_custom_index(
    #     name="自定义指数",
    #     code="XXXXXX",
    #     url="https://example.com/data.xls",
    #     description="自定义指数描述"
    # )
    
    main()