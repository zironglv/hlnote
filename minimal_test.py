#!/usr/bin/env python3
"""
极简GitHub Actions测试脚本
用于验证最基本的Python执行环境
"""

import os
import sys
import json
from datetime import datetime

def main():
    print("=" * 40)
    print("🚀 极简GitHub Actions测试")
    print("=" * 40)
    
    # 基本环境信息
    print(f"🕐 时间: {datetime.now()}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📂 工作目录: {os.getcwd()}")
    print(f"📋 环境变量数量: {len(os.environ)}")
    
    # 检查关键环境变量
    critical_vars = ['GITHUB_ACTIONS', 'GITHUB_WORKSPACE', 'DINGTALK_WEBHOOK']
    for var in critical_vars:
        value = os.environ.get(var, '未设置')
        if var == 'DINGTALK_WEBHOOK' and value != '未设置':
            value = f"已设置 (长度: {len(value)})" 
        print(f"🔧 {var}: {value}")
    
    # 测试基本导入
    try:
        import pandas as pd
        import requests
        import matplotlib
        print("✅ 核心包导入成功")
    except Exception as e:
        print(f"❌ 包导入失败: {str(e)}")
        return 1
    
    # 测试简单网络请求
    try:
        response = requests.get('https://httpbin.org/get', timeout=5)
        print(f"✅ 网络请求成功 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 网络请求失败: {str(e)}")
        return 1
    
    # 测试简单数据处理
    try:
        data = {'日期': ['2024-01-01', '2024-01-02'], '数值': [1.0, 2.0]}
        df = pd.DataFrame(data)
        print(f"✅ DataFrame创建成功 (行数: {len(df)})")
    except Exception as e:
        print(f"❌ DataFrame操作失败: {str(e)}")
        return 1
    
    # 测试matplotlib
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(4, 3))
        plt.plot([1, 2, 3], [1, 4, 2])
        plt.savefig('test_plot.png')
        plt.close()
        print("✅ Matplotlib绘图成功")
    except Exception as e:
        print(f"❌ Matplotlib绘图失败: {str(e)}")
        return 1
    
    # 如果有钉钉配置，发送简单测试消息
    webhook = os.environ.get('DINGTALK_WEBHOOK')
    if webhook:
        try:
            from dingtalk_sender import DingTalkSender
            sender = DingTalkSender(webhook_url=webhook)
            test_msg = {
                "msgtype": "text",
                "text": {
                    "content": f"✅ GitHub Actions环境测试成功\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            result = sender._send_message(test_msg)
            if result:
                print("✅ 钉钉消息发送成功")
            else:
                print("⚠️ 钉钉消息发送失败（但不阻止程序）")
        except Exception as e:
            print(f"⚠️ 钉钉测试异常: {str(e)}（但不阻止程序）")
    
    print("\n" + "=" * 40)
    print("🎉 所有测试通过！")
    print("=" * 40)
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)