#!/usr/bin/env python3
"""
测试真实Excel文件处理
"""

import os
import sys
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_real_excel():
    """测试真实Excel文件处理"""
    print("=== 测试真实Excel文件处理 ===")
    
    # 读取真实文件
    excel_file = '930955indicator.xls'
    if not os.path.exists(excel_file):
        print(f"❌ 找不到文件: {excel_file}")
        return
    
    print(f"✓ 找到文件: {excel_file}")
    
    # 读取Excel文件
    df = pd.read_excel(excel_file)
    print(f"✓ 文件读取成功，数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 显示数据概览
    print("\n数据概览:")
    print(df.head())
    
    # 测试数据处理模块
    print("\n=== 测试数据处理 ===")
    from data_processor import DataProcessor
    
    processor = DataProcessor()
    analysis_result = processor.analyze_data(df)
    
    print("✓ 数据分析完成")
    print(f"分析时间: {analysis_result['analysis_time']}")
    print("关键指标:")
    for key, value in analysis_result['metrics'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # 测试报告生成
    print("\n=== 测试报告生成 ===")
    from report_generator import ReportGenerator
    
    generator = ReportGenerator(output_dir="real_data_reports")
    html_content, chart_path = generator.generate_report(analysis_result)
    
    print("✓ 报告生成完成")
    print(f"HTML文件大小: {len(html_content)} 字符")
    print(f"图表文件: {chart_path}")
    
    # 保存报告
    with open("real_data_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ 报告已保存为 real_data_report.html")
    
    print("\n=== 测试总结 ===")
    print("✓ Excel文件读取: 成功")
    print("✓ 数据处理: 成功") 
    print("✓ 报告生成: 成功")
    print("🎉 所有测试通过！")

if __name__ == "__main__":
    test_real_excel()