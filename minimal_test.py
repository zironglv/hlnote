#!/usr/bin/env python3
"""
极简测试脚本 - 用于验证基本功能
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_imports():
    """测试基本模块导入"""
    logger.info("🔍 测试基本模块导入...")
    
    try:
        import pandas as pd
        logger.info(f"✅ pandas 版本: {pd.__version__}")
    except ImportError as e:
        logger.error(f"❌ pandas 导入失败: {e}")
        return False
    
    try:
        import matplotlib
        logger.info(f"✅ matplotlib 版本: {matplotlib.__version__}")
    except ImportError as e:
        logger.error(f"❌ matplotlib 导入失败: {e}")
        return False
    
    try:
        import requests
        logger.info(f"✅ requests 版本: {requests.__version__}")
    except ImportError as e:
        logger.error(f"❌ requests 导入失败: {e}")
        return False
    
    try:
        import numpy as np
        logger.info(f"✅ numpy 版本: {np.__version__}")
    except ImportError as e:
        logger.error(f"❌ numpy 导入失败: {e}")
        return False
    
    return True

def test_project_modules():
    """测试项目模块导入"""
    logger.info("🔍 测试项目模块导入...")
    
    # 添加项目路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from index_config import IndexConfig, index_manager
        logger.info("✅ index_config 模块导入成功")
        
        # 测试获取指数配置
        indexes = index_manager.get_all_indexes()
        logger.info(f"✅ 成功获取 {len(indexes)} 个指数配置")
        for idx in indexes[:3]:  # 只显示前3个
            logger.info(f"  - {idx.name} ({idx.code})")
            
    except Exception as e:
        logger.error(f"❌ index_config 模块导入失败: {e}")
        return False
    
    try:
        from multi_index_analyzer import MultiIndexAnalyzer
        logger.info("✅ multi_index_analyzer 模块导入成功")
    except Exception as e:
        logger.error(f"❌ multi_index_analyzer 模块导入失败: {e}")
        return False
    
    try:
        from data_collector import DataCollector
        logger.info("✅ data_collector 模块导入成功")
    except Exception as e:
        logger.error(f"❌ data_collector 模块导入失败: {e}")
        return False
    
    try:
        from data_processor import DataProcessor
        logger.info("✅ data_processor 模块导入成功")
    except Exception as e:
        logger.error(f"❌ data_processor 模块导入失败: {e}")
        return False
    
    try:
        from report_generator import ReportGenerator
        logger.info("✅ report_generator 模块导入成功")
    except Exception as e:
        logger.error(f"❌ report_generator 模块导入失败: {e}")
        return False
    
    return True

def test_network_connectivity():
    """测试网络连接"""
    logger.info("🔍 测试网络连接...")
    
    try:
        import requests
        # 测试百度连接
        response = requests.get('https://www.baidu.com', timeout=10)
        if response.status_code == 200:
            logger.info("✅ 百度连接正常")
        else:
            logger.warning(f"⚠️ 百度返回状态码: {response.status_code}")
            
        # 测试数据源连接
        test_urls = [
            'https://www.csindex.com.cn/',
            'https://csi-web-dev.oss-cn-shanghai-finance-1-pub.aliyuncs.com/'
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                logger.info(f"✅ {url} 连接正常 (状态码: {response.status_code})")
            except Exception as e:
                logger.warning(f"⚠️ {url} 连接可能有问题: {e}")
                
    except Exception as e:
        logger.error(f"❌ 网络连接测试失败: {e}")
        return False
    
    return True

def test_matplotlib_backend():
    """测试matplotlib后端配置"""
    logger.info("🔍 测试matplotlib后端...")
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非GUI后端
        import matplotlib.pyplot as plt
        
        # 创建简单图表测试
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title('测试图表')
        plt.savefig('test_plot.png')
        plt.close()
        
        if os.path.exists('test_plot.png'):
            logger.info("✅ matplotlib 图表生成功能正常")
            os.remove('test_plot.png')  # 清理测试文件
        else:
            logger.error("❌ matplotlib 图表生成失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ matplotlib 测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    logger.info("🚀 开始极简功能测试...")
    
    tests = [
        ("基本模块导入", test_basic_imports),
        ("项目模块导入", test_project_modules),
        ("网络连接", test_network_connectivity),
        ("Matplotlib后端", test_matplotlib_backend)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                logger.info(f"✅ {test_name} 测试通过")
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {e}")
    
    logger.info("=" * 50)
    logger.info(f"📊 测试结果: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 所有测试通过！项目基本功能正常")
        return 0
    else:
        logger.error("💥 部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)