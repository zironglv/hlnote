#!/usr/bin/env python3
"""
详细错误定位测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dingtalk_sender import DingTalkSender

# 模拟数据（与真实数据一致）
test_metrics = {
    'current_rate': '5.0200',  # 字符串，模拟实际数据
    'avg_15d': '5.0200',
    'max_15d': '5.0900',
    'min_15d': '4.9900',
    'change_percent': '+0.60',
    'percentile_15d': '30.0',
    'pe': 8.5,
    'pb': 1.2,
    'pe_percentile': 25.0,
    'pb_percentile': 30.0,
    'bond_yield': 2.5,
    'dividend_bond_spread': 2.52,
    'investment_advice': {
        'action': '持有',
        'confidence': 0.5,
        'summary': '股息率处于合理区间，建议关注市场整体走势'
    }
}

test_index_info = {
    'name': '红利低波指数',
    'code': 'H30269',
    'description': '测试指数'
}

test_processed_data = {
    'metrics': test_metrics
}

def test_extract_metrics():
    """测试 _extract_metrics_from_html"""
    print("=== 测试 _extract_metrics_from_html ===")
    sender = DingTalkSender()
    
    try:
        result = sender._extract_metrics_from_html("<html>test</html>", test_processed_data)
        print("✅ _extract_metrics_from_html 成功")
        print(f"结果: {result}")
        return True
    except Exception as e:
        print(f"❌ _extract_metrics_from_html 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_trend_analysis():
    """测试 _get_trend_analysis"""
    print("\n=== 测试 _get_trend_analysis ===")
    sender = DingTalkSender()
    
    try:
        # 使用转换后的指标
        converted_metrics = {
            'current_rate': 5.0200,
            'avg_15d': 5.0200,
            'max_15d': 5.0900,
            'min_15d': 4.9900,
            'change_percent': 0.60,
            'percentile_15d': 30.0,
            'pe': 8.5,
            'pb': 1.2,
            'pe_percentile': 25.0,
            'pb_percentile': 30.0,
            'bond_yield': 2.5,
            'dividend_bond_spread': 2.52
        }
        
        result = sender._get_trend_analysis(converted_metrics)
        print("✅ _get_trend_analysis 成功")
        print(f"结果: {result}")
        return True
    except Exception as e:
        print(f"❌ _get_trend_analysis 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_investment_advice():
    """测试 _get_investment_advice"""
    print("\n=== 测试 _get_investment_advice ===")
    sender = DingTalkSender()
    
    try:
        converted_metrics = {
            'current_rate': 5.0200,
            'avg_15d': 5.0200,
            'max_15d': 5.0900,
            'min_15d': 4.9900,
            'change_percent': 0.60,
            'percentile_15d': 30.0,
            'pe': 8.5,
            'pb': 1.2,
            'pe_percentile': 25.0,
            'pb_percentile': 30.0,
            'bond_yield': 2.5,
            'dividend_bond_spread': 2.52,
            'investment_advice': {
                'action': '持有',
                'confidence': 0.5,
                'summary': '测试摘要'
            }
        }
        
        result = sender._get_investment_advice(converted_metrics)
        print("✅ _get_investment_advice 成功")
        print(f"结果: {result}")
        return True
    except Exception as e:
        print(f"❌ _get_investment_advice 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_build_markdown():
    """测试 _build_daily_report_markdown"""
    print("\n=== 测试 _build_daily_report_markdown ===")
    sender = DingTalkSender()
    
    try:
        result = sender._build_daily_report_markdown(
            title="测试标题",
            metrics=test_metrics,
            index_info=test_index_info,
            processed_data=test_processed_data
        )
        print("✅ _build_daily_report_markdown 成功")
        print(f"结果长度: {len(result)}")
        return True
    except Exception as e:
        print(f"❌ _build_daily_report_markdown 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_send_report():
    """测试 send_report"""
    print("\n=== 测试 send_report ===")
    webhook = os.getenv('DINGTALK_WEBHOOK', 'https://oapi.dingtalk.com/robot/send?access_token=test')
    sender = DingTalkSender(webhook_url=webhook)
    
    try:
        html_content = "<h1>测试报告</h1><p>测试内容</p>"
        result = sender.send_report(
            html_content,
            chart_path=None,
            index_info=test_index_info,
            processed_data=test_processed_data
        )
        print(f"✅ send_report 成功: {result}")
        return result
    except Exception as e:
        print(f"❌ send_report 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("开始详细错误定位测试...\n")
    
    tests = [
        test_extract_metrics,
        test_get_trend_analysis,
        test_get_investment_advice,
        test_build_markdown,
        test_send_report
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n=== 测试结果 ===")
    print(f"总测试数: {len(results)}")
    print(f"成功: {sum(results)}")
    print(f"失败: {len(results) - sum(results)}")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
