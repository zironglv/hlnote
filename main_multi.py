#!/usr/bin/env python3
"""
AI投研助手 - 多指数版本主程序
功能：每日定时获取多个中证指数数据，生成分析报告并通过钉钉分别发送
简化版：移除所有调试消息，只保留核心功能
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_index_analyzer import MultiIndexAnalyzer, run_multi_index_analysis
from index_config import IndexConfig, index_manager
# local_config 模块在GitHub Actions环境中不存在，移除依赖

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
    # 获取钉钉Webhook配置
    dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK')
    
    # 设置matplotlib后端以避免GUI相关问题
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非GUI后端
        logger.info("📊 matplotlib后端设置为Agg")
    except Exception as e:
        logger.warning(f"matplotlib后端设置失败: {str(e)}")
    
    try:
        logger.info("=== AI投研助手(多指数版)开始执行 ===")
        
        # 系统健康检查
        import platform
        system_info = f"🖥️ 系统: {platform.system()} {platform.release()}, Python: {platform.python_version()}"
        logger.info(system_info)
        
        # 检查钉钉Webhook配置
        if dingtalk_webhook:
            logger.info(f"✅ 检测到 DINGTALK_WEBHOOK (长度: {len(dingtalk_webhook)} 字符)")
        else:
            logger.warning("⚠️ 未找到 DINGTALK_WEBHOOK 环境变量")
        
        # 网络连通性检查
        try:
            import requests
            response = requests.get('https://www.baidu.com', timeout=5)
            logger.info("🌐 网络连接正常")
        except Exception as e:
            logger.warning(f"⚠️ 网络连接可能存在问题: {str(e)}")
        
        # 获取指数配置
        indexes = index_manager.get_all_indexes()
        logger.info(f"📊 配置的指数数量: {len(indexes)}")
        
        for idx in indexes:
            logger.info(f"- {idx.name} ({idx.code}): {idx.url}")
        
        # 测试钉钉机器人连接
        if dingtalk_webhook:
            logger.info("🧪 测试钉钉机器人连接...")
            try:
                from dingtalk_sender import DingTalkSender
                sender = DingTalkSender(webhook_url=dingtalk_webhook)
                test_result = sender.test_connection()
                if test_result:
                    logger.info("✅ 钉钉机器人连接测试成功")
                else:
                    logger.error("❌ 钉钉机器人连接测试失败")
            except Exception as e:
                logger.error(f"❌ 钉钉机器人连接测试异常: {str(e)}")
        
        # 运行多指数分析
        logger.info("=== 开始多指数投研分析 ===")
        
        # 创建分析器并运行完整分析
        analyzer = MultiIndexAnalyzer(dingtalk_webhook=dingtalk_webhook)
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
        
        return 0
        
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)