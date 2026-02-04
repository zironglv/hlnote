#!/usr/bin/env python3
"""
检查 metrics 数据类型
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
import pandas as pd
import numpy as np

def create_test_data():
    """创建测试数据"""
    dates = pd.date_range('2024-01-01', '2024-01-20', freq='D')
    data = {
        '日期Date': dates,
        '股息率2（计算用股本）D/P2': np.random.uniform(4.5, 5.5, 20)
    }
    return pd.DataFrame(data)

def main():
    print("=== 检查 metrics 数据类型 ===")
    
    df = create_test_data()
    processor = DataProcessor()
    
    result = processor.analyze_data(df)
    
    print("分析结果键:", list(result.keys()))
    
    if 'metrics' in result:
        metrics = result['metrics']
        print("\n=== metrics 内容 ===")
        for key, value in metrics.items():
            print(f"{key}: {value} (类型: {type(value).__name__})")
    else:
        print("没有找到 metrics")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())