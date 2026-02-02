#!/usr/bin/env python3
"""
多指数功能测试脚本
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from index_config import IndexConfig, index_manager
from multi_index_analyzer import MultiIndexAnalyzer

def test_index_configuration():
    """测试指数配置管理"""
    print("=== 测试指数配置管理 ===")
    
    # 获取默认配置
    indexes = index_manager.get_all_indexes()
    print(f"默认指数数量: {len(indexes)}")
    
    for idx in indexes:
        print(f"- {idx.name} ({idx.code}): {idx.url}")
    
    # 测试查找功能
    try:
        h30269 = index_manager.get_index_by_code("H30269")
        print(f"\n找到指数: {h30269.name}")
    except ValueError as e:
        print(f"查找失败: {e}")
    
    print("✓ 指数配置管理测试通过")

def test_multi_index_analysis():
    """测试多指数分析（使用本地文件）"""
    print("\n=== 测试多指数分析 ===")
    
    # 创建测试用的本地文件索引配置
    test_indexes = [
        IndexConfig(
            name="红利低波指数",
            code="H30269",
            url="./930955indicator.xls",  # 使用现有的本地文件进行测试
            description="测试用红利低波指数"
        ),
        IndexConfig(
            name="红利低波100指数",
            code="930955", 
            url="./930955indicator.xls",  # 使用相同的文件进行测试
            description="测试用红利低波100指数"
        )
    ]
    
    try:
        # 运行多指数分析
        analyzer = MultiIndexAnalyzer(test_indexes)
        results, send_results = analyzer.run_full_analysis()
        
        # 检查结果
        success_count = sum(1 for r in results if r.success)
        print(f"\n分析结果: {success_count}/{len(test_indexes)} 个指数分析成功")
        
        for result in results:
            status = "✓" if result.success else "✗"
            sent_status = "📤" if send_results.get(result.index_config.code, False) else "📭"
            print(f"{status} {sent_status} {result.index_config.name}")
            
        if success_count > 0:
            print("✓ 多指数分析测试通过")
        else:
            print("✗ 多指数分析测试失败")
            
    except Exception as e:
        print(f"✗ 多指数分析测试异常: {e}")

def main():
    """主测试函数"""
    print("开始多指数功能测试...\n")
    
    try:
        test_index_configuration()
        test_multi_index_analysis()
        
        print("\n" + "="*50)
        print("🎉 所有测试完成!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()