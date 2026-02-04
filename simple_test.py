#!/usr/bin/env python3
"""
极简测试脚本 - 验证GitHub Actions环境中的基本功能
"""

import sys
import os

def main():
    print("🚀 开始极简测试...")
    
    # 测试基本导入
    try:
        import pandas as pd
        import requests
        print("✅ 依赖导入成功")
    except ImportError as e:
        print(f"❌ 依赖导入失败: {e}")
        return 1
    
    # 测试网络连接
    try:
        response = requests.get('https://www.baidu.com', timeout=5)
        print("✅ 网络连接正常")
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return 1
    
    # 测试基本文件操作
    try:
        os.makedirs("test_reports", exist_ok=True)
        with open("test_reports/test.txt", "w") as f:
            f.write("测试文件内容")
        print("✅ 文件操作正常")
    except Exception as e:
        print(f"❌ 文件操作失败: {e}")
        return 1
    
    print("🎉 所有测试通过!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"程序退出码: {exit_code}")
    sys.exit(exit_code)