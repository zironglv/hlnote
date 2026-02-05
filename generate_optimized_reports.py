# 使用优化版报告生成器替换原有生成器的测试脚本
import os
import sys
from datetime import datetime
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector
from data_processor import DataProcessor  
from optimized_report_generator import OptimizedReportGenerator
from index_config import index_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_optimized_report_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_single_index(index_config):
    """分析单个指数并生成优化版报告"""
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
        processed_data = processor.analyze_data(csv_data, bond_yield_data)
        
        # 将估值数据添加到处理结果中
        if valuation_data and 'pe' in valuation_data:
            processed_data['metrics']['pe'] = valuation_data['pe']
        
        # 添加指数信息
        processed_data['index_info'] = {
            'name': index_config.name,
            'code': index_config.code,
            'description': index_config.description
        }
        
        # 3. 生成优化版报告
        generator = OptimizedReportGenerator()
        
        # 创建输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('reports', f'optimized_{timestamp}_{index_config.code}')
        
        # 准备完整的分析数据
        analysis_data = {
            'processed_data': processed_data['processed_data'],  # 这是DataFrame，用于图表生成
            'metrics': processed_data.get('metrics', {}),
            'analysis_time': processed_data.get('analysis_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        
        report_html, chart_path = generator.generate_report(analysis_data, output_dir=output_dir)
        
        logger.info(f"优化版报告已保存至 {output_dir}")
        
        return {
            'success': True,
            'index_config': index_config,
            'processed_data': processed_data,
            'report_path': os.path.join(output_dir, 'optimized_index.html')
        }
        
    except Exception as e:
        logger.error(f"指数 {index_config.name} 分析失败: {str(e)}")
        return {
            'success': False,
            'index_config': index_config,
            'error': str(e)
        }

def main():
    """主函数 - 使用优化版报告生成器生成报告"""
    try:
        logger.info("=== 开始使用优化版报告生成器 ===")
        
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
        
        # 输出生成的报告路径
        for result in results:
            if result['success']:
                logger.info(f"报告路径: {result['report_path']}")
        
        return results
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    results = main()
    
    print("\n📊 优化版报告生成完成!")
    print("生成的优化版报告文件:")
    for result in results:
        if result['success']:
            print(f"  - {result['report_path']}")
        else:
            print(f"  - 指数 {result['index_config'].name} 生成失败: {result.get('error', 'Unknown error')}")