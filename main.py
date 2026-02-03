#!/usr/bin/env python3
"""
AI投研助手增强版 - 主程序入口
功能：获取指数数据、估值数据、国债收益率，生成综合分析报告并通过钉钉发送
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
from index_config import index_manager

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

def analyze_single_index(index_config):
    """分析单个指数"""
    try:
        logger.info(f"开始分析指数: {index_config.name}({index_config.code})")
        
        # 1. 数据收集
        collector = DataCollector()
        
        # 获取股息率数据
        csv_data = collector.fetch_csv_data(index_config.url)
        
        # 获取估值数据（PE/PB）
        valuation_data = collector.fetch_valuation_data(index_config.code)
        
        # 获取国债收益率数据（10年期）
        bond_yield_data = collector.fetch_bond_yield('10y')
        
        # 2. 数据处理（整合所有数据）
        processor = DataProcessor()
        processed_data = processor.analyze_data(csv_data, valuation_data, bond_yield_data)
        
        # 添加指数信息
        processed_data['index_info'] = {
            'name': index_config.name,
            'code': index_config.code,
            'description': index_config.description
        }
        
        # 3. 报告生成
        generator = ReportGenerator()
        report_html, chart_path = generator.generate_report(processed_data)
        
        # 4. 钉钉发送
        sender = DingTalkSender()
        success = sender.send_report(report_html, chart_path, 
                                   index_info=processed_data['index_info'],
                                   processed_data=processed_data)
        
        if success:
            logger.info(f"{index_config.name} 报告发送成功")
        else:
            logger.error(f"{index_config.name} 报告发送失败")
        
        return {
            'success': success,
            'index_config': index_config,
            'processed_data': processed_data
        }
        
    except Exception as e:
        logger.error(f"指数 {index_config.name} 分析失败: {str(e)}")
        return {
            'success': False,
            'index_config': index_config,
            'error': str(e)
        }

def main():
    """主函数"""
    try:
        logger.info("=== AI投研助手增强版开始执行 ===")
        
        # 获取所有配置的指数
        indexes = index_manager.get_all_indexes()
        logger.info(f"共配置 {len(indexes)} 个指数")
        
        results = []
        
        # 分析每个指数
        for index_config in indexes:
            result = analyze_single_index(index_config)
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"=== 分析完成: {success_count}/{len(results)} 个指数分析成功 ===")
        
        # 生成总结报告
        if results:
            generate_summary_report(results)
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

def generate_summary_report(results):
    """生成总结报告"""
    try:
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            logger.warning("没有成功的分析结果，跳过总结报告")
            return
        
        # 构造总结消息
        summary_lines = [
            "📊 AI投研助手增强版分析总结",
            f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🔢 分析指数: {len(successful_results)}/{len(results)} 个成功",
            "",
            "📈 各指数分析结果:"
        ]
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            index_name = result['index_config'].name
            summary_lines.append(f"{status} {index_name}")
        
        summary_lines.extend([
            "",
            "💡 增强功能:",
            "- 股息率分析",
            "- PE/PB估值分析",
            "- 国债收益率对比",
            "- 投资决策建议",
            "- 双层级报告（日报+完整页面）",
            "",
            "🔗 查看完整报告请访问生成的HTML文件",
            "📈 数据仅供参考，投资有风险"
        ])
        
        summary_text = "\n".join(summary_lines)
        
        # 发送总结报告
        sender = DingTalkSender()
        
        # 构造简单的HTML格式总结
        summary_html = f"""
        <html>
        <body>
            <h2>AI投研助手增强版分析总结</h2>
            <p>分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>成功分析指数: {len(successful_results)}/{len(results)} 个</p>
            <ul>
        """
        
        for result in results:
            status = "成功" if result['success'] else "失败"
            index_name = result['index_config'].name
            summary_html += f"<li>{index_name}: {status}</li>"
        
        summary_html += """
            </ul>
            <p>增强功能已启用: 股息率 + PE/PB估值 + 国债收益率对比 + 投资决策建议</p>
            </body>
            </html>
        """
        
        # 发送总结
        sender.send_report(summary_html, None, 
                         index_info={'name': 'AI投研助手总结', 'code': 'SUMMARY'},
                         processed_data={'metrics': {}})
        
        logger.info("总结报告发送成功")
        
    except Exception as e:
        logger.error(f"生成总结报告失败: {str(e)}")

if __name__ == "__main__":
    main()