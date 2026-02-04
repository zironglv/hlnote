#!/usr/bin/env python3
"""
调试版本 - 多指数投研助手
功能：打印详细的诊断信息，帮助定位钉钉只发送测试消息的问题
"""

import os
import sys
from datetime import datetime
import logging
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_index_analyzer import MultiIndexAnalyzer, run_multi_index_analysis
from index_config import IndexConfig, index_manager
from dingtalk_sender import DingTalkSender

# 配置日志 - 更详细的调试级别
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_index_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """调试主函数"""
    # 获取钉钉Webhook配置
    dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK')
    
    # 设置matplotlib后端以避免GUI相关问题
    try:
        import matplotlib
        matplotlib.use('Agg')
        logger.info("📊 matplotlib后端设置为Agg")
    except Exception as e:
        logger.warning(f"matplotlib后端设置失败: {str(e)}")
    
    try:
        logger.info("=== 调试模式启动 ===")
        
        # 系统信息
        import platform
        logger.info(f"🖥️ 系统: {platform.system()} {platform.release()}")
        logger.info(f"🐍 Python: {platform.python_version()}")
        
        # 检查钉钉Webhook
        if dingtalk_webhook:
            logger.info(f"✅ 检测到 DINGTALK_WEBHOOK (长度: {len(dingtalk_webhook)} 字符)")
            logger.info(f"   Webhook URL: {dingtalk_webhook[:60]}...")
        else:
            logger.warning("⚠️ 未找到 DINGTALK_WEBHOOK 环境变量")
        
        # 获取指数配置
        indexes = index_manager.get_all_indexes()
        logger.info(f"📊 配置的指数数量: {len(indexes)}")
        
        for idx in indexes:
            logger.info(f"   - {idx.name} ({idx.code}): {idx.url}")
        
        # 测试钉钉连接
        logger.info("=== 测试钉钉连接 ===")
        try:
            sender = DingTalkSender(webhook_url=dingtalk_webhook)
            test_result = sender.test_connection()
            if test_result:
                logger.info("✅ 钉钉测试消息发送成功")
            else:
                logger.error("❌ 钉钉测试消息发送失败")
        except Exception as e:
            logger.error(f"❌ 钉钉测试异常: {str(e)}")
            logger.error(traceback.format_exc())
        
        # 运行多指数分析
        logger.info("=== 开始多指数分析（详细调试）===")
        
        analyzer = MultiIndexAnalyzer(dingtalk_webhook=dingtalk_webhook)
        
        # 第一步：分析所有指数
        logger.info("--- 步骤1: 分析所有指数 ---")
        analysis_results = analyzer.analyze_all_indexes()
        
        logger.info(f"分析完成，结果数量: {len(analysis_results)}")
        for i, result in enumerate(analysis_results):
            logger.info(f"   [{i+1}] {result.index_config.name} ({result.index_config.code})")
            logger.info(f"       成功: {result.success}")
            if not result.success:
                logger.error(f"       错误: {result.error_message}")
            else:
                logger.info(f"       数据行数: {len(result.raw_data) if result.raw_data is not None else 0}")
                logger.info(f"       报告长度: {len(result.report_html) if result.report_html else 0} 字符")
                logger.info(f"       图表路径: {result.chart_path}")
                logger.info(f"       处理数据键: {list(result.processed_data.keys()) if result.processed_data else 'None'}")
        
        # 第二步：发送报告
        logger.info("--- 步骤2: 发送报告到钉钉 ---")
        send_results = analyzer.send_results_via_dingtalk(analysis_results)
        
        logger.info(f"发送完成，结果数量: {len(send_results)}")
        for code, success in send_results.items():
            status = "✅ 成功" if success else "❌ 失败"
            logger.info(f"   {code}: {status}")
        
        # 第三步：生成总结报告
        logger.info("--- 步骤3: 生成总结报告 ---")
        try:
            analyzer._send_summary_report(analysis_results, send_results, include_summary=True)
            logger.info("✅ 总结报告生成完成")
        except Exception as e:
            logger.error(f"❌ 总结报告生成失败: {str(e)}")
            logger.error(traceback.format_exc())
        
        # 最终统计
        success_count = sum(1 for r in analysis_results if r.success)
        sent_count = sum(1 for sent in send_results.values() if sent)
        
        logger.info("=== 最终统计 ===")
        logger.info(f"📊 指数总数: {len(analysis_results)}")
        logger.info(f"✅ 分析成功: {success_count}")
        logger.info(f"❌ 分析失败: {len(analysis_results) - success_count}")
        logger.info(f"📤 发送成功: {sent_count}")
        logger.info(f"📭 发送失败: {len(send_results) - sent_count}")
        
        logger.info("=== 调试完成 ===")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行错误: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
