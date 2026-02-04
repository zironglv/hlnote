#!/usr/bin/env python3
"""
专门测试模块导入问题的调试脚本
"""

import sys
import os
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_module_import(module_name, import_statement):
    """测试单个模块导入"""
    print(f"\n🔍 测试导入: {module_name}")
    try:
        exec(import_statement)
        print(f"✅ {module_name} 导入成功")
        return True
    except Exception as e:
        print(f"❌ {module_name} 导入失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始模块导入调试...")
    
    # 测试基础模块
    basic_modules = [
        ("pandas", "import pandas as pd"),
        ("matplotlib", "import matplotlib"),
        ("requests", "import requests"),
        ("numpy", "import numpy as np")
    ]
    
    # 测试项目模块
    project_modules = [
        ("index_config", "from index_config import IndexConfig, index_manager"),
        ("data_collector", "from data_collector import DataCollector"),
        ("data_processor", "from data_processor import DataProcessor"),
        ("report_generator", "from report_generator import ReportGenerator"),
        ("dingtalk_sender", "from dingtalk_sender import DingTalkSender"),
        ("multi_index_analyzer", "from multi_index_analyzer import MultiIndexAnalyzer")
    ]
    
    print("\n" + "="*50)
    print("测试基础模块导入:")
    print("="*50)
    
    basic_passed = 0
    for module_name, import_stmt in basic_modules:
        if test_module_import(module_name, import_stmt):
            basic_passed += 1
    
    print("\n" + "="*50)
    print("测试项目模块导入:")
    print("="*50)
    
    project_passed = 0
    for module_name, import_stmt in project_modules:
        if test_module_import(module_name, import_stmt):
            project_passed += 1
    
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    print(f"基础模块: {basic_passed}/{len(basic_modules)} 通过")
    print(f"项目模块: {project_passed}/{len(project_modules)} 通过")
    
    if basic_passed == len(basic_modules) and project_passed == len(project_modules):
        print("🎉 所有模块导入测试通过!")
        return 0
    else:
        print("💥 存在导入问题，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)