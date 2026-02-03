#!/usr/bin/env python3
"""
深度诊断脚本 - 逐步排查GitHub Actions环境问题
"""

import os
import sys
import logging
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostic_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """检查运行环境"""
    print("=== 环境检查 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"环境变量DINGTALK_WEBHOOK: {'已设置' if os.getenv('DINGTALK_WEBHOOK') else '未设置'}")
    
    if os.getenv('DINGTALK_WEBHOOK'):
        webhook = os.getenv('DINGTALK_WEBHOOK')
        print(f"Webhook长度: {len(webhook)}")
        print(f"Webhook域名: {webhook.split('/')[2] if '/' in webhook else 'invalid'}")
    
    # 检查必要文件
    required_files = ['main_multi.py', 'multi_index_analyzer.py', 'dingtalk_sender.py', 'index_config.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 缺失")

def check_network_connectivity():
    """检查网络连接"""
    print("\n=== 网络连接检查 ===")
    import requests
    
    # 测试基础网络
    try:
        response = requests.get('https://www.baidu.com', timeout=5)
        print(f"✅ 百度访问成功 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 百度访问失败: {str(e)}")
        return False
    
    # 测试数据源
    test_urls = [
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls"
    ]
    
    for i, url in enumerate(test_urls, 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"✅ 数据源{i}访问成功 (大小: {len(response.content)} bytes)")
            else:
                print(f"❌ 数据源{i}异常: 状态码{response.status_code}, 大小{len(response.content)}")
                return False
        except Exception as e:
            print(f"❌ 数据源{i}访问失败: {str(e)}")
            return False
    
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n=== 依赖包检查 ===")
    required_packages = ['pandas', 'requests', 'matplotlib', 'openpyxl']
    
    for package in required_packages:
        try:
            if package == 'openpyxl':
                import openpyxl
                print(f"✅ {package} 版本: {openpyxl.__version__}")
            elif package == 'pandas':
                import pandas as pd
                print(f"✅ {package} 版本: {pd.__version__}")
            elif package == 'matplotlib':
                import matplotlib
                print(f"✅ {package} 版本: {matplotlib.__version__}")
            elif package == 'requests':
                import requests
                print(f"✅ {package} 版本: {requests.__version__}")
        except ImportError as e:
            print(f"❌ {package} 导入失败: {str(e)}")
            return False
    
    return True

def test_dingtalk_connection():
    """测试钉钉连接"""
    print("\n=== 钉钉连接测试 ===")
    webhook = os.getenv('DINGTALK_WEBHOOK')
    
    if not webhook:
        print("❌ 未设置DINGTALK_WEBHOOK环境变量")
        return False
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from dingtalk_sender import DingTalkSender
        
        sender = DingTalkSender(webhook_url=webhook)
        print("🧪 发送测试消息...")
        success = sender.test_connection()
        
        if success:
            print("✅ 钉钉机器人连接测试成功")
            return True
        else:
            print("❌ 钉钉机器人连接测试失败")
            # 检查具体错误
            try:
                # 尝试发送简单文本消息来获取详细错误信息
                test_msg = {
                    "msgtype": "text",
                    "text": {
                        "content": f"🔧 诊断测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
                result = sender._send_message(test_msg)
                print(f"📝 测试消息发送结果: {result}")
            except Exception as e:
                print(f"📝 测试消息发送异常: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 钉钉测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processing():
    """测试数据处理流程"""
    print("\n=== 数据处理测试 ===")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_collector import DataCollector
        from data_processor import DataProcessor
        from index_config import index_manager
        
        indexes = index_manager.get_all_indexes()
        print(f"📊 配置的指数数量: {len(indexes)}")
        
        # 测试第一个指数
        test_index = indexes[0]
        print(f"🧪 测试指数: {test_index.name} ({test_index.code})")
        
        # 数据收集
        collector = DataCollector()
        print(f"📥 获取数据: {test_index.url}")
        raw_data = collector.fetch_csv_data(test_index.url)
        print(f"✅ 数据获取成功，共{len(raw_data)}行")
        
        # 数据处理
        processor = DataProcessor()
        processed_data = processor.analyze_data(raw_data)
        print(f"✅ 数据处理完成")
        print(f"📊 关键指标: 当前股息率 {processed_data.get('current_rate', 'N/A'):.4f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据处理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation():
    """测试报告生成"""
    print("\n=== 报告生成测试 ===")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from report_generator import ReportGenerator
        from data_collector import DataCollector
        from data_processor import DataProcessor
        from index_config import index_manager
        
        # 获取处理后的数据
        indexes = index_manager.get_all_indexes()
        test_index = indexes[0]
        
        collector = DataCollector()
        processor = DataProcessor()
        generator = ReportGenerator()
        
        raw_data = collector.fetch_csv_data(test_index.url)
        processed_data = processor.analyze_data(raw_data)
        
        # 添加指数信息
        processed_data['index_info'] = {
            'name': test_index.name,
            'code': test_index.code,
            'description': test_index.description
        }
        
        # 生成报告
        html_report, chart_path = generator.generate_report(processed_data, output_dir=f"test_reports/{test_index.code}")
        print(f"✅ 报告生成成功")
        print(f"📄 HTML报告长度: {len(html_report)} 字符")
        print(f"📊 图表路径: {chart_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主诊断函数"""
    print("🔍 GitHub Actions 环境深度诊断")
    print("=" * 50)
    
    # 逐项检查
    checks = [
        ("环境检查", check_environment),
        ("网络连接", check_network_connectivity),
        ("依赖包", check_dependencies),
        ("钉钉连接", test_dingtalk_connection),
        ("数据处理", test_data_processing),
        ("报告生成", test_report_generation)
    ]
    
    results = {}
    for name, func in checks:
        try:
            result = func()
            results[name] = result
            print(f"\n{'✅' if result else '❌'} {name}: {'通过' if result else '失败'}")
        except Exception as e:
            print(f"\n💥 {name}: 执行异常 - {str(e)}")
            results[name] = False
            import traceback
            traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 诊断结果汇总:")
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    print(f"\n📈 总体结果: {success_count}/{total_count} 项通过")
    
    if success_count == total_count:
        print("🎉 所有检查都通过！")
        return True
    else:
        print("💥 存在问题需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)