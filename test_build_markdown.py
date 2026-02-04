#!/usr/bin/env python3
"""
测试 _build_daily_report_markdown 方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dingtalk_sender import DingTalkSender

# 模拟数据
test_metrics = {
    'current_rate': '5.0200',  # 字符串类型，模拟实际数据
    'avg_15d': '5.0200',
    'max_15d': '5.0900',
    'min_15d': '4.9900',
    'change_percent': '+0.60',  # 字符串类型
    'percentile_15d': '30.0',   # 字符串类型
    'pe': 8.5,
    'pb': 1.2,
    'pe_percentile': 25.0,
    'pb_percentile': 30.0,
    'bond_yield': 2.5,
    'dividend_bond_spread': 2.52
}

test_index_info = {
    'name': '红利低波指数',
    'code': 'H30269',
    'description': '测试指数'
}

test_processed_data = {
    'metrics': test_metrics
}

def main():
    print("=== 测试 _build_daily_report_markdown ===")
    
    sender = DingTalkSender()
    
    try:
        print("调用 _build_daily_report_markdown...")
        result = sender._build_daily_report_markdown(
            title="测试标题",
            metrics=test_metrics,
            index_info=test_index_info,
            processed_data=test_processed_data
        )
        print("✅ 成功！")
        print(f"结果长度: {len(result)}")
        print("前200个字符:")
        print(result[:200])
        return 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
