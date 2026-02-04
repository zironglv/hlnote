#!/usr/bin/env python3
"""
完整集成测试 - 模拟真实场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_index_analyzer import MultiIndexAnalyzer
from index_config import IndexConfig

def main():
    print("=== 完整集成测试 ===")
    
    # 模拟真实的指数配置
    test_index = IndexConfig(
        code='H30269',
        name='红利低波指数',
        url='https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls',
        description='测试指数'
    )
    
    # 使用真实的 webhook（如果有环境变量）
    webhook = os.getenv('DINGTALK_WEBHOOK', 'https://oapi.dingtalk.com/robot/send?access_token=test')
    
    try:
        print("创建 MultiIndexAnalyzer...")
        analyzer = MultiIndexAnalyzer([test_index], dingtalk_webhook=webhook)
        
        print("分析单个指数...")
        result = analyzer.analyze_single_index(test_index)
        
        print(f"分析结果: success={result.success}")
        print(f"报告长度: {len(result.report_html) if result.report_html else 0}")
        print(f"图表路径: {result.chart_path}")
        print(f"处理数据键: {list(result.processed_data.keys()) if result.processed_data else 'None'}")
        
        if result.success:
            print("\n发送报告到钉钉...")
            send_result = analyzer.send_results_via_dingtalk([result])
            print(f"发送结果: {send_result}")
            
            if send_result.get('H30269', False):
                print("✅ 报告发送成功")
                return 0
            else:
                print("❌ 报告发送失败")
                return 1
        else:
            print(f"❌ 分析失败: {result.error_message}")
            return 1
            
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())