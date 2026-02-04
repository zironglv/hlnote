"""
多指数数据处理器 - 处理多个指数的数据收集和分析
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

from index_config import IndexConfig, index_manager
from data_collector import DataCollector
from data_processor import DataProcessor
from report_generator import ReportGenerator
from dingtalk_sender import DingTalkSender

logger = logging.getLogger(__name__)

@dataclass
class IndexAnalysisResult:
    """单个指数分析结果"""
    index_config: IndexConfig
    raw_data: object  # 原始数据
    processed_data: Dict  # 处理后的数据
    report_html: str  # HTML报告
    chart_path: str   # 图表路径
    success: bool     # 是否成功
    error_message: str = ""  # 错误信息

class MultiIndexAnalyzer:
    """多指数分析器"""
    
    def __init__(self, indexes: List[IndexConfig] = None, send_summary: bool = True, dingtalk_webhook: str = None):
        """
        初始化多指数分析器
        
        Args:
            indexes: 要分析的指数列表，如果为None则使用全局配置
            send_summary: 是否发送总结报告，默认True
            dingtalk_webhook: 钉钉机器人webhook地址，默认None（使用环境变量或默认值）
        """
        self.indexes = indexes or index_manager.get_all_indexes()
        self.send_summary = send_summary
        self.data_collector = DataCollector()
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator()
        self.dingtalk_sender = DingTalkSender(webhook_url=dingtalk_webhook)
    
    def analyze_single_index(self, index_config: IndexConfig) -> IndexAnalysisResult:
        """
        分析单个指数
        
        Args:
            index_config: 指数配置
            
        Returns:
            IndexAnalysisResult: 分析结果
        """
        try:
            logger.info(f"开始分析指数: {index_config.name}({index_config.code})")
            
            # 1. 数据收集
            logger.info(f"获取数据: {index_config.url}")
            raw_data = self.data_collector.fetch_csv_data(index_config.url)
            
            # 2. 数据验证
            if not self.data_collector.validate_data(raw_data):
                raise Exception("数据验证失败")
            
            # 3. 数据处理
            processed_data = self.data_processor.analyze_data(raw_data)
            processed_data['index_info'] = {
                'name': index_config.name,
                'code': index_config.code,
                'description': index_config.description
            }
            
            # 3.5 获取估值数据（PE/PB）
            try:
                valuation_data = self.data_collector.fetch_valuation_data(index_config.code)
                if valuation_data and valuation_data.get('pe'):
                    processed_data['metrics'].update({
                        'pe': valuation_data.get('pe'),
                        'pb': valuation_data.get('pb'),
                        'pe_percentile': valuation_data.get('pe_percentile', 50),
                        'pb_percentile': valuation_data.get('pb_percentile', 50)
                    })
                    logger.info(f"成功获取估值数据: PE={valuation_data.get('pe')}, PB={valuation_data.get('pb')}")
            except Exception as e:
                logger.warning(f"获取估值数据失败: {str(e)}")
            
            # 3.6 获取国债收益率数据
            try:
                bond_yield = self.data_collector.fetch_bond_yield()
                if bond_yield:
                    processed_data['metrics']['bond_yield'] = bond_yield.get('current_yield')
                    processed_data['metrics']['bond_yield_change'] = bond_yield.get('yield_change')
                    # 计算股息率与国债收益率的差值
                    if processed_data['metrics'].get('current_rate') and bond_yield.get('current_yield'):
                        processed_data['metrics']['dividend_bond_spread'] = (
                            processed_data['metrics']['current_rate'] - bond_yield.get('current_yield')
                        )
                    logger.info(f"成功获取国债收益率: {bond_yield.get('current_yield')}%")
            except Exception as e:
                logger.warning(f"获取国债收益率失败: {str(e)}")
            
            # 4. 报告生成
            report_html, chart_path = self.report_generator.generate_report(
                processed_data, 
                output_dir=f"reports/{index_config.code}"
            )
            
            logger.info(f"指数 {index_config.name} 分析完成")
            
            return IndexAnalysisResult(
                index_config=index_config,
                raw_data=raw_data,
                processed_data=processed_data,
                report_html=report_html,
                chart_path=chart_path,
                success=True
            )
            
        except Exception as e:
            logger.error(f"指数 {index_config.name} 分析失败: {str(e)}")
            return IndexAnalysisResult(
                index_config=index_config,
                raw_data=None,
                processed_data={},
                report_html="",
                chart_path="",
                success=False,
                error_message=str(e)
            )
    
    def analyze_all_indexes(self) -> List[IndexAnalysisResult]:
        """
        分析所有配置的指数
        
        Returns:
            List[IndexAnalysisResult]: 所有指数的分析结果
        """
        logger.info(f"开始批量分析 {len(self.indexes)} 个指数")
        results = []
        
        for index_config in self.indexes:
            result = self.analyze_single_index(index_config)
            results.append(result)
            
            # 记录进度
            if result.success:
                logger.info(f"✓ {index_config.name} 分析成功")
            else:
                logger.error(f"✗ {index_config.name} 分析失败: {result.error_message}")
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量分析完成: {success_count}/{len(results)} 个指数分析成功")
        
        return results
    
    def send_results_via_dingtalk(self, results: List[IndexAnalysisResult]) -> Dict[str, bool]:
        """
        通过钉钉发送分析结果
        
        Args:
            results: 分析结果列表
            
        Returns:
            Dict[str, bool]: 每个指数的发送结果
        """
        send_results = {}
        
        # 检查钉钉发送器配置
        logger.info(f"钉钉发送器配置检查 - Webhook URL: {self.dingtalk_sender.webhook_url[:50]}...")
        
        for result in results:
            try:
                if result.success:
                    logger.info(f"发送 {result.index_config.name} 的分析报告")
                    # 构造指数信息
                    index_info = {
                        'name': result.index_config.name,
                        'code': result.index_config.code,
                        'description': result.index_config.description
                    }
                    
                    # 检查报告内容
                    if not result.report_html or len(result.report_html.strip()) == 0:
                        logger.warning(f"⚠️ {result.index_config.name} 报告内容为空，跳过发送")
                        send_results[result.index_config.code] = False
                        continue
                    
                    success = self.dingtalk_sender.send_report(
                        result.report_html, 
                        result.chart_path,
                        index_info=index_info,
                        processed_data=result.processed_data
                    )
                    send_results[result.index_config.code] = success
                    
                    if success:
                        logger.info(f"✓ {result.index_config.name} 报告发送成功")
                    else:
                        logger.error(f"✗ {result.index_config.name} 报告发送失败")
                else:
                    logger.warning(f"跳过发送 {result.index_config.name}: 分析失败")
                    send_results[result.index_config.code] = False
                    
            except Exception as e:
                logger.error(f"发送 {result.index_config.name} 报告时出错: {str(e)}")
                logger.exception("详细错误信息:")
                send_results[result.index_config.code] = False
        
        # 统计发送结果
        total_sent = len([r for r in send_results.values() if r])
        logger.info(f"📊 发送统计: 成功 {total_sent}/{len(send_results)} 个报告")
        
        return send_results
    
    def run_full_analysis(self) -> Tuple[List[IndexAnalysisResult], Dict[str, bool]]:
        """
        运行完整的多指数分析流程
        
        Returns:
            Tuple[List[IndexAnalysisResult], Dict[str, bool]]: (分析结果, 发送结果)
        """
        logger.info("=== 开始多指数投研分析 ===")
        
        try:
            # 1. 分析所有指数
            analysis_results = self.analyze_all_indexes()
            
            # 2. 发送报告
            send_results = self.send_results_via_dingtalk(analysis_results)
            
            # 3. 生成总结报告
            self._send_summary_report(analysis_results, send_results, include_summary=self.send_summary)
            
            logger.info("=== 多指数投研分析完成 ===")
            return analysis_results, send_results
            
        except Exception as e:
            logger.error(f"多指数分析过程中发生错误: {str(e)}")
            raise
    
    def _send_summary_report(self, analysis_results: List[IndexAnalysisResult], 
                               send_results: Dict[str, bool], include_summary: bool = True):
        """
        生成分析总结报告
        
        Args:
            analysis_results: 分析结果
            send_results: 发送结果
        """
        total_count = len(analysis_results)
        success_count = sum(1 for r in analysis_results if r.success)
        sent_count = sum(1 for sent in send_results.values() if sent)
        
        summary = f"""
📊 多指数投研分析总结
========================

📈 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔢 指数总数: {total_count}
✅ 分析成功: {success_count}
❌ 分析失败: {total_count - success_count}
📤 发送成功: {sent_count}

详细结果:
"""
        
        for result in analysis_results:
            status = "✅" if result.success else "❌"
            sent_status = "📤" if send_results.get(result.index_config.code, False) else "📭"
            summary += f"\n{status} {sent_status} {result.index_config.name} ({result.index_config.code})"
            if not result.success:
                summary += f" - {result.error_message}"
        
        # 禁用summary报告发送，只发送单个指数的日报
        if False:  # 暂时禁用summary报告
            try:
                # 构造包含多个指数信息的总结标题
                index_names = [result.index_config.name for result in analysis_results if result.success]
                indices_str = " & ".join(index_names)
                summary_with_indices = f"📊 {indices_str} 综合分析总结\n\n{summary}"
                
                # 为总结报告提供特殊的指数信息
                summary_index_info = {
                    'name': f'{indices_str} 综合分析',
                    'code': 'SUMMARY',
                    'description': f'包含 {len(index_names)} 个指数的综合分析'
                }
                
                # 计算汇总指标
                summary_metrics = {}
                if analysis_results and analysis_results[0].success:
                    # 使用第一个成功分析的指数数据作为汇总数据
                    first_metrics = analysis_results[0].processed_data.get('metrics', {})
                    summary_metrics = first_metrics.copy()
                
                self.dingtalk_sender.send_report(
                    summary_with_indices, 
                    None,
                    index_info=summary_index_info,
                    processed_data={'metrics': summary_metrics}
                )
                logger.info("总结报告发送成功")
            except Exception as e:
                logger.error(f"总结报告发送失败: {str(e)}")
        else:
            logger.info("跳过发送总结报告")

# 便利函数
def run_multi_index_analysis(indexes: List[IndexConfig] = None) -> Tuple[List[IndexAnalysisResult], Dict[str, bool]]:
    """
    运行多指数分析的便利函数
    
    Args:
        indexes: 指数配置列表
        
    Returns:
        Tuple[List[IndexAnalysisResult], Dict[str, bool]]: (分析结果, 发送结果)
    """
    analyzer = MultiIndexAnalyzer(indexes)
    return analyzer.run_full_analysis()