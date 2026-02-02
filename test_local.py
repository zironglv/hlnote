#!/usr/bin/env python3
"""
本地调试脚本 - 用于测试AI投研助手的各项功能
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
try:
    import local_config as config
except ImportError:
    print("警告: 未找到local_config.py配置文件，将使用默认配置")
    config = type('Config', (), {
        'EMAIL_USERNAME': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password',
        'RECIPIENT_EMAIL': 'recipient@example.com',
        'CSV_URL': 'https://example.com/test.csv',
        'LOCAL_TEST': True,
        'DEBUG_MODE': True
    })()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_collection():
    """测试数据收集功能"""
    print("\n=== 测试数据收集功能 ===")
    try:
        from data_collector import DataCollector
        
        collector = DataCollector(csv_url=config.CSV_URL)
        df = collector.fetch_csv_data()
        
        print(f"✓ 数据获取成功，共{len(df)}行记录")
        print(f"列名: {list(df.columns)}")
        print("前5行数据:")
        print(df.head())
        
        # 验证数据
        is_valid = collector.validate_data(df)
        print(f"数据验证结果: {'通过' if is_valid else '失败'}")
        
        return df if is_valid else None
        
    except Exception as e:
        print(f"✗ 数据收集测试失败: {str(e)}")
        logger.exception("数据收集异常详情:")
        return None

def test_data_processing(df):
    """测试数据处理功能"""
    print("\n=== 测试数据处理功能 ===")
    try:
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
                
        return analysis_result
        
    except Exception as e:
        print(f"✗ 数据处理测试失败: {str(e)}")
        logger.exception("数据处理异常详情:")
        return None

def test_report_generation(analysis_result):
    """测试报告生成功能"""
    print("\n=== 测试报告生成功能 ===")
    try:
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir="test_reports")
        html_content, chart_path = generator.generate_report(analysis_result)
        
        print("✓ 报告生成完成")
        print(f"HTML文件大小: {len(html_content)} 字符")
        print(f"图表文件: {chart_path}")
        
        # 保存测试报告
        with open("test_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✓ 测试报告已保存为 test_report.html")
        
        return html_content, chart_path
        
    except Exception as e:
        print(f"✗ 报告生成测试失败: {str(e)}")
        logger.exception("报告生成异常详情:")
        return None, None

def test_dingtalk_sending(html_content, chart_path):
    """测试钉钉发送功能"""
    print("\n=== 测试钉钉发送功能 ===")
    try:
        from dingtalk_sender import DingTalkSender
        
        # 使用配置的钉钉webhook
        sender = DingTalkSender()
        
        # 测试连接
        if sender.test_connection():
            print("✓ 钉钉机器人连接测试成功")
            
            # 发送测试消息
            success = sender.send_report(html_content, chart_path)
            if success:
                print("✓ 钉钉消息发送测试成功")
                return True
            else:
                print("✗ 钉钉消息发送失败")
                return False
        else:
            print("✗ 钉钉机器人连接测试失败")
            return False
            
    except Exception as e:
        print(f"✗ 钉钉发送测试失败: {str(e)}")
        logger.exception("钉钉发送异常详情:")
        return False

def create_sample_data():
    """创建示例数据用于测试"""
    print("\n=== 创建示例数据 ===")
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # 生成15天的模拟股息率数据
    dates = [datetime.now() - timedelta(days=i) for i in range(14, -1, -1)]
    base_rate = 0.035  # 3.5%基准股息率
    
    # 生成有一定趋势的模拟数据
    rates = []
    current_rate = base_rate
    for i in range(15):
        # 添加随机波动和趋势
        trend = 0.0002 * (7 - i)  # 中间高，两边低的趋势
        noise = np.random.normal(0, 0.001)  # 随机噪声
        current_rate += trend + noise
        rates.append(max(0.01, current_rate))  # 确保不低于1%
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'dividend_rate': rates
    })
    
    print("✓ 示例数据创建完成")
    print(f"数据范围: {df['dividend_rate'].min():.4f}% - {df['dividend_rate'].max():.4f}%")
    print(f"当前值: {df['dividend_rate'].iloc[-1]:.4f}%")
    
    return df

def main():
    """主测试函数"""
    print("=" * 50)
    print("AI投研助手 - 本地调试测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"本地测试模式: {config.LOCAL_TEST}")
    print(f"调试模式: {config.DEBUG_MODE}")
    
    # 步骤1: 创建示例数据或获取真实数据
    if config.LOCAL_TEST:
        df = create_sample_data()
    else:
        df = test_data_collection()
        if df is None:
            print("\n⚠ 无法获取真实数据，使用示例数据继续测试")
            df = create_sample_data()
    
    if df is None:
        print("\n✗ 测试终止：无法获取有效数据")
        return
    
    # 步骤2: 数据处理测试
    analysis_result = test_data_processing(df)
    if analysis_result is None:
        print("\n✗ 测试终止：数据处理失败")
        return
    
    # 步骤3: 报告生成测试
    html_content, chart_path = test_report_generation(analysis_result)
    if html_content is None:
        print("\n✗ 测试终止：报告生成失败")
        return
    
    # 步骤4: 钉钉发送测试
    dingtalk_success = test_dingtalk_sending(html_content, chart_path)
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"数据收集: {'✓' if config.LOCAL_TEST or df is not None else '✗'}")
    print(f"数据处理: {'✓' if analysis_result is not None else '✗'}")
    print(f"报告生成: {'✓' if html_content is not None else '✗'}")
    print(f"钉钉发送: {'✓' if dingtalk_success else '✗'}")
    print("=" * 50)
    
    if config.LOCAL_TEST:
        print("\n💡 提示:")
        print("1. 查看 test_report.html 文件预览报告效果")
        print("2. 在 local_config.py 中配置真实邮箱信息")
        print("3. 将 LOCAL_TEST 设为 False 进行完整测试")

if __name__ == "__main__":
    main()