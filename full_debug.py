#!/usr/bin/env python3
"""
完整的项目调试脚本 - 全面检查项目状态
"""

import sys
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_structure():
    """检查项目文件结构"""
    logger.info("🔍 检查项目文件结构...")
    
    required_files = [
        'main_multi_fixed.py',
        'multi_index_analyzer.py', 
        'index_config.py',
        'data_collector.py',
        'data_processor.py',
        'report_generator.py',
        'dingtalk_sender.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_name in required_files:
        if os.path.exists(file_name):
            logger.info(f"✅ {file_name}")
        else:
            logger.error(f"❌ 缺少文件: {file_name}")
            missing_files.append(file_name)
    
    return len(missing_files) == 0

def check_dependencies():
    """检查Python依赖"""
    logger.info("🔍 检查Python依赖...")
    
    required_packages = [
        'pandas',
        'matplotlib',
        'requests',
        'numpy',
        'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ 缺少依赖包: {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_data_collection():
    """测试数据收集功能"""
    logger.info("🔍 测试数据收集功能...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_collector import DataCollector
        
        collector = DataCollector()
        # 测试获取红利低波指数数据
        test_url = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls"
        data = collector.fetch_csv_data(test_url)
        
        if data is not None and len(data) > 0:
            logger.info(f"✅ 数据收集成功，获取到 {len(data)} 行数据")
            logger.info(f"数据列名: {list(data.columns)[:5]}")  # 显示前5列
            return True
        else:
            logger.error("❌ 数据收集失败：返回空数据")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据收集测试异常: {str(e)}")
        return False

def test_data_processing():
    """测试数据处理功能"""
    logger.info("🔍 测试数据处理功能...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_collector import DataCollector
        from data_processor import DataProcessor
        
        # 先获取数据
        collector = DataCollector()
        test_url = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls"
        raw_data = collector.fetch_csv_data(test_url)
        
        # 处理数据
        processor = DataProcessor()
        processed_data = processor.analyze_data(raw_data)
        
        if processed_data and 'metrics' in processed_data:
            metrics = processed_data['metrics']
            logger.info("✅ 数据处理成功")
            logger.info(f"当前股息率: {metrics.get('current_rate', 'N/A')}")
            logger.info(f"15日平均: {metrics.get('avg_15d', 'N/A')}")
            logger.info(f"投资建议: {metrics.get('investment_advice', {}).get('action', 'N/A')}")
            return True
        else:
            logger.error("❌ 数据处理失败：未生成有效指标")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据处理测试异常: {str(e)}")
        return False

def test_report_generation():
    """测试报告生成功能"""
    logger.info("🔍 测试报告生成功能...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_collector import DataCollector
        from data_processor import DataProcessor
        from report_generator import ReportGenerator
        
        # 获取并处理数据
        collector = DataCollector()
        processor = DataProcessor()
        generator = ReportGenerator()
        
        test_url = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls"
        raw_data = collector.fetch_csv_data(test_url)
        processed_data = processor.analyze_data(raw_data)
        
        # 生成报告
        html_content, chart_path = generator.generate_report(processed_data)
        
        if html_content and len(html_content) > 100:  # 简单检查报告长度
            logger.info("✅ 报告生成成功")
            logger.info(f"HTML长度: {len(html_content)} 字符")
            if chart_path and os.path.exists(chart_path):
                logger.info(f"图表生成成功: {chart_path}")
            return True
        else:
            logger.error("❌ 报告生成失败：内容过短或为空")
            return False
            
    except Exception as e:
        logger.error(f"❌ 报告生成测试异常: {str(e)}")
        return False

def test_multi_index_analysis():
    """测试多指数分析功能"""
    logger.info("🔍 测试多指数分析功能...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from multi_index_analyzer import MultiIndexAnalyzer
        from index_config import index_manager
        
        # 获取所有指数配置
        indexes = index_manager.get_all_indexes()
        logger.info(f"配置的指数数量: {len(indexes)}")
        
        # 创建分析器（不发送钉钉消息）
        analyzer = MultiIndexAnalyzer(indexes, send_summary=False)
        
        # 执行分析
        results, send_results = analyzer.run_full_analysis()
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"✅ 多指数分析完成: {success_count}/{len(indexes)} 个指数分析成功")
        
        for result in results:
            status = "✓" if result.success else "✗"
            logger.info(f"{status} {result.index_config.name}")
            if not result.success:
                logger.error(f"  错误详情: {result.error_message}")
        
        return success_count > 0  # 至少有一个成功就算通过
        
    except Exception as e:
        logger.error(f"❌ 多指数分析测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_github_actions_config():
    """检查GitHub Actions配置"""
    logger.info("🔍 检查GitHub Actions配置...")
    
    workflow_files = [
        '.github/workflows/ai-investment-assistant.yml',
        '.github/workflows/minimal_test.yml'
    ]
    
    config_ok = True
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            logger.info(f"✅ {workflow_file}")
        else:
            logger.warning(f"⚠️ 缺少工作流文件: {workflow_file}")
            config_ok = False
    
    # 检查关键配置项
    main_workflow = '.github/workflows/ai-investment-assistant.yml'
    if os.path.exists(main_workflow):
        with open(main_workflow, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DINGTALK_WEBHOOK' in content:
                logger.info("✅ 工作流配置了DINGTALK_WEBHOOK")
            else:
                logger.warning("⚠️ 工作流未配置DINGTALK_WEBHOOK")
                config_ok = False
    
    return config_ok

def main():
    """主调试函数"""
    logger.info("🚀 开始全面项目调试...")
    logger.info(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("项目文件结构", check_file_structure),
        ("Python依赖", check_dependencies),
        ("数据收集功能", test_data_collection),
        ("数据处理功能", test_data_processing),
        ("报告生成功能", test_report_generation),
        ("多指数分析功能", test_multi_index_analysis),
        ("GitHub Actions配置", check_github_actions_config)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    print("\n" + "="*60)
    print("📊 项目调试结果")
    print("="*60)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 正在测试: {test_name}")
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {str(e)}")
    
    print("\n" + "="*60)
    print(f"🎯 调试总结: {passed_tests}/{total_tests} 项测试通过")
    print("="*60)
    
    if passed_tests == total_tests:
        print("🎉 恭喜！所有测试都通过了！")
        print("✅ 项目可以正常部署到GitHub Actions")
        return 0
    else:
        print("💥 存在问题需要修复")
        print("📋 建议检查上述失败的测试项")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)