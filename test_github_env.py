#!/usr/bin/env python3
"""
GitHub Actions专用测试脚本 - 简化版
用于在GitHub Actions环境中快速诊断问题
"""

import os
import sys
import logging

# 配置简单日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """简化版诊断测试"""
    print("=== GitHub Actions 环境诊断 ===")
    
    # 1. 检查环境变量
    webhook = os.getenv('DINGTALK_WEBHOOK')
    if webhook:
        print(f"✅ DINGTALK_WEBHOOK 已设置")
        print(f"   长度: {len(webhook)} 字符")
        print(f"   域名: {webhook.split('/')[2] if '/' in webhook else 'unknown'}")
    else:
        print("❌ DINGTALK_WEBHOOK 未设置")
        return False
    
    # 2. 检查网络
    try:
        import requests
        response = requests.get('https://www.baidu.com', timeout=5)
        print(f"✅ 网络连接正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 网络连接失败: {str(e)}")
        return False
    
    # 3. 测试数据源
    urls = [
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
        "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls"
    ]
    
    data_success = True
    for i, url in enumerate(urls, 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"✅ 数据源{i}访问成功")
            else:
                print(f"❌ 数据源{i}访问异常: 状态码{response.status_code}, 大小{len(response.content)}")
                data_success = False
        except Exception as e:
            print(f"❌ 数据源{i}访问失败: {str(e)}")
            data_success = False
    
    if not data_success:
        return False
    
    # 4. 测试钉钉连接
    try:
        # 添加项目路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from dingtalk_sender import DingTalkSender
        
        sender = DingTalkSender(webhook_url=webhook)
        print("🧪 测试钉钉消息发送...")
        success = sender.test_connection()
        if success:
            print("✅ 钉钉机器人连接测试成功")
        else:
            print("❌ 钉钉机器人连接测试失败")
            return False
    except Exception as e:
        print(f"❌ 钉钉测试异常: {str(e)}")
        return False
    
    # 5. 简化版分析测试
    try:
        from multi_index_analyzer import MultiIndexAnalyzer
        from index_config import index_manager
        
        indexes = index_manager.get_all_indexes()
        print(f"📊 配置指数数量: {len(indexes)}")
        
        analyzer = MultiIndexAnalyzer(indexes[:1], send_summary=False, dingtalk_webhook=webhook)  # 只测试第一个指数
        print("🚀 开始简化分析...")
        
        # 只分析一个指数来节省时间和资源
        result = analyzer.analyze_single_index(indexes[0])
        if result.success:
            print(f"✅ {indexes[0].name} 分析成功")
            # 尝试发送
            index_info = {
                'name': result.index_config.name,
                'code': result.index_config.code,
                'description': result.index_config.description
            }
            send_success = analyzer.dingtalk_sender.send_report(
                result.report_html,
                result.chart_path,
                index_info=index_info,
                processed_data=result.processed_data
            )
            if send_success:
                print("✅ 测试报告发送成功")
                return True
            else:
                print("❌ 测试报告发送失败")
                return False
        else:
            print(f"❌ {indexes[0].name} 分析失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ 分析测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)