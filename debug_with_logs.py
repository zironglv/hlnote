#!/usr/bin/env python3
"""
带详细日志的调试版本
专门用于捕获GitHub Actions中的所有错误细节
"""

import os
import sys
import traceback
import logging
from datetime import datetime

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_trace.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_execute(func, func_name):
    """安全执行函数并记录详细信息"""
    try:
        logger.info(f"🔍 开始执行: {func_name}")
        result = func()
        logger.info(f"✅ 成功完成: {func_name}")
        return result, True
    except Exception as e:
        logger.error(f"❌ 执行失败: {func_name}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error(f"详细堆栈:")
        traceback.print_exc()
        return None, False

def check_environment():
    """检查环境"""
    logger.info("=== 环境检查 ===")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"环境变量DINGTALK_WEBHOOK: {'已设置' if os.getenv('DINGTALK_WEBHOOK') else '未设置'}")
    
    # 检查必要文件
    files_to_check = ['main_multi.py', 'multi_index_analyzer.py', 'dingtalk_sender.py']
    for file in files_to_check:
        if os.path.exists(file):
            logger.info(f"✅ 文件存在: {file}")
        else:
            logger.error(f"❌ 文件缺失: {file}")
            raise FileNotFoundError(f"缺少必要文件: {file}")

def check_imports():
    """检查导入"""
    logger.info("=== 导入检查 ===")
    
    imports_to_test = [
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('matplotlib.pyplot', 'matplotlib'),
        ('openpyxl', 'openpyxl')
    ]
    
    for import_stmt, pkg_name in imports_to_test:
        try:
            __import__(import_stmt)
            logger.info(f"✅ 成功导入: {pkg_name}")
        except ImportError as e:
            logger.error(f"❌ 导入失败: {pkg_name} - {str(e)}")
            raise

def test_simple_operations():
    """测试简单操作"""
    logger.info("=== 简单操作测试 ===")
    
    # 测试pandas
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    logger.info(f"✅ DataFrame创建成功，形状: {df.shape}")
    
    # 测试网络
    import requests
    response = requests.get('https://httpbin.org/get', timeout=10)
    logger.info(f"✅ 网络请求成功，状态码: {response.status_code}")
    
    # 测试matplotlib
    import matplotlib.pyplot as plt
    plt.figure(figsize=(3, 2))
    plt.plot([1, 2, 3], [1, 4, 2])
    plt.savefig('debug_plot.png')
    plt.close()
    logger.info("✅ Matplotlib绘图成功")

def test_main_execution():
    """测试主程序执行"""
    logger.info("=== 主程序执行测试 ===")
    
    # 导入主模块
    from main_multi import main
    logger.info("✅ 成功导入main函数")
    
    # 执行主函数
    logger.info("🚀 开始执行main函数...")
    main()
    logger.info("✅ main函数执行完成")

def main():
    """主调试函数"""
    print("=" * 50)
    print("🔍 GitHub Actions详细调试模式")
    print("=" * 50)
    
    steps = [
        ("环境检查", check_environment),
        ("导入检查", check_imports),
        ("简单操作测试", test_simple_operations),
        ("主程序执行测试", test_main_execution)
    ]
    
    all_passed = True
    for step_name, step_func in steps:
        result, success = safe_execute(step_func, step_name)
        if not success:
            all_passed = False
            logger.error(f"❌ 步骤失败: {step_name}")
            break
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有步骤都成功执行！")
        return 0
    else:
        print("💥 执行过程中出现错误")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"程序退出码: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"程序崩溃: {str(e)}")
        traceback.print_exc()
        sys.exit(1)