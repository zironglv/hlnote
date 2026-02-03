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
    # 初始化调试用的钉钉发送器
    dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK')
    debug_sender = None
    if dingtalk_webhook:
        from dingtalk_sender import DingTalkSender
        debug_sender = DingTalkSender(webhook_url=dingtalk_webhook)
        debug_sender.send_text_message("🚀 多指数AI投研助手开始运行 - 调试模式")
    
    try:
        logger.info("=== AI投研助手(多指数版)开始执行 ===")
        if debug_sender:
            debug_sender.send_text_message("🔧 节点1: 程序启动和环境检查")
        
        # 系统健康检查
        import platform
        system_info = f"🖥️ 系统: {platform.system()} {platform.release()}, Python: {platform.python_version()}"
        logger.info(system_info)
        if debug_sender:
            debug_sender.send_text_message(system_info)
        
        # 检查钉钉Webhook配置
        if dingtalk_webhook:
            webhook_info = f"✅ 检测到 DINGTALK_WEBHOOK (长度: {len(dingtalk_webhook)} 字符)"
            logger.info(webhook_info)
            if debug_sender:
                debug_sender.send_text_message(webhook_info)
        else:
            warning_msg = "⚠️ 未找到 DINGTALK_WEBHOOK 环境变量"
            logger.warning(warning_msg)
            if debug_sender:
                debug_sender.send_text_message(warning_msg)
        
        # 节点2: 网络连通性检查
        if debug_sender:
            debug_sender.send_text_message("🌐 节点2: 网络连通性检查")
        
        try:
            import requests
            response = requests.get('https://www.baidu.com', timeout=5)
            network_status = "🌐 网络连接正常"
            logger.info(network_status)
            if debug_sender:
                debug_sender.send_text_message(network_status)
        except Exception as e:
            network_error = f"⚠️ 网络连接可能存在问题: {str(e)}"
            logger.warning(network_error)
            if debug_sender:
                debug_sender.send_text_message(network_error)
        
        # 节点3: 获取指数配置
        if debug_sender:
            debug_sender.send_text_message("📊 节点3: 获取指数配置")
        
        indexes = index_manager.get_all_indexes()
        config_info = f"📊 配置的指数数量: {len(indexes)}"
        logger.info(config_info)
        if debug_sender:
            debug_sender.send_text_message(config_info)
        
        for idx in indexes:
            logger.info(f"- {idx.name} ({idx.code}): {idx.url}")
        
        # 节点4: 钉钉连接测试
        if debug_sender:
            debug_sender.send_text_message("🤖 节点4: 钉钉连接测试")
        
        if dingtalk_webhook:
            test_sender = DingTalkSender(webhook_url=dingtalk_webhook)
            logger.info("🧪 测试钉钉机器人连接...")
            if test_sender.test_connection():
                test_result = "✅ 钉钉机器人连接测试成功"
                logger.info(test_result)
                if debug_sender:
                    debug_sender.send_text_message(test_result)
            else:
                test_result = "❌ 钉钉机器人连接测试失败"
                logger.error(test_result)
                if debug_sender:
                    debug_sender.send_text_message(test_result)
        
        # 节点5: 运行多指数分析
        if debug_sender:
            debug_sender.send_text_message("📈 节点5: 开始多指数分析")
        
        # 设置 send_summary=False 来只发送指数报告而不发送总结报告
        analyzer = MultiIndexAnalyzer(indexes, send_summary=False, dingtalk_webhook=dingtalk_webhook)
        analysis_results, send_results = analyzer.run_full_analysis()
        
        # 节点6: 结果统计
        if debug_sender:
            debug_sender.send_text_message("📊 节点6: 分析结果统计")
        
        # 输出结果统计
        success_count = sum(1 for r in analysis_results if r.success)
        sent_count = sum(1 for sent in send_results.values() if sent)
        
        final_result = f"=== 分析完成 ===\n成功分析: {success_count}/{len(indexes)} 个指数\n成功发送: {sent_count}/{len(indexes)} 个报告"
        logger.info(final_result)
        if debug_sender:
            debug_sender.send_text_message(final_result)
        
        # 详细结果
        for result in analysis_results:
            status = "✓" if result.success else "✗"
            sent_status = "📤" if send_results.get(result.index_config.code, False) else "📭"
            result_msg = f"{status} {sent_status} {result.index_config.name}"
            logger.info(result_msg)
            if debug_sender:
                debug_sender.send_text_message(result_msg)
            if not result.success:
                error_detail = f"  错误: {result.error_message}"
                logger.error(error_detail)
                if debug_sender:
                    debug_sender.send_text_message(f"❌ {result.index_config.name}: {result.error_message}")
                
    except Exception as e:
        error_msg = f"❌ 程序执行出错: {str(e)}"
        logger.error(error_msg)
        if debug_sender:
            debug_sender.send_text_message(error_msg)
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