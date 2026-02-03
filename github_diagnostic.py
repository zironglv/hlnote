#!/usr/bin/env python3
"""
GitHub Actions 环境快速诊断脚本
专门用于定位导致 exit code 1 的具体问题
"""

import os
import sys
import traceback
from datetime import datetime

def log_step(step_name, status="INFO"):
    """记录步骤执行状态"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {step_name}"
    print(f"{status}: {message}")
    
    # 尝试发送到钉钉（如果配置了）
    try:
        webhook = os.getenv('DINGTALK_WEBHOOK')
        if webhook:
            from dingtalk_sender import DingTalkSender
            sender = DingTalkSender(webhook_url=webhook)
            msg = {
                "msgtype": "text",
                "text": {
                    "content": f"🔍 {message}"
                }
            }
            sender._send_message(msg)
    except Exception as e:
        print(f"DEBUG: 钉钉消息发送失败: {str(e)}")

def check_python_environment():
    """检查Python环境"""
    log_step("检查Python环境")
    try:
        import platform
        log_step(f"Python版本: {platform.python_version()}")
        log_step(f"系统平台: {platform.system()} {platform.release()}")
        return True
    except Exception as e:
        log_step(f"Python环境检查失败: {str(e)}", "ERROR")
        return False

def check_required_packages():
    """检查必需的包"""
    log_step("检查必需依赖包")
    required_packages = [
        ('pandas', 'pandas'),
        ('requests', 'requests'), 
        ('matplotlib', 'matplotlib'),
        ('openpyxl', 'openpyxl')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            log_step(f"✅ {package_name} - 已安装")
        except ImportError as e:
            log_step(f"❌ {package_name} - 缺失: {str(e)}", "ERROR")
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0

def check_matplotlib_backend():
    """检查matplotlib后端"""
    log_step("检查matplotlib配置")
    try:
        import matplotlib
        current_backend = matplotlib.get_backend()
        log_step(f"当前matplotlib后端: {current_backend}")
        
        # 尝试设置后端
        matplotlib.use('Agg')
        log_step("✅ matplotlib后端设置为Agg成功")
        return True
    except Exception as e:
        log_step(f"matplotlib配置失败: {str(e)}", "ERROR")
        return False

def check_working_directory():
    """检查工作目录和文件"""
    log_step("检查工作目录")
    try:
        cwd = os.getcwd()
        log_step(f"当前工作目录: {cwd}")
        
        # 检查必要文件
        required_files = [
            'main_multi.py',
            'multi_index_analyzer.py', 
            'dingtalk_sender.py',
            'index_config.py'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                log_step(f"✅ {file} - 存在")
            else:
                log_step(f"❌ {file} - 缺失", "ERROR")
                missing_files.append(file)
        
        return len(missing_files) == 0
    except Exception as e:
        log_step(f"工作目录检查失败: {str(e)}", "ERROR")
        return False

def check_network_access():
    """检查网络访问"""
    log_step("检查网络连接")
    try:
        import requests
        # 测试基本网络
        response = requests.get('https://www.baidu.com', timeout=5)
        log_step(f"✅ 网络连接正常 (状态码: {response.status_code})")
        
        # 测试数据源
        test_urls = [
            "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
            "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls"
        ]
        
        for i, url in enumerate(test_urls, 1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    log_step(f"✅ 数据源{i}可访问 (大小: {len(response.content)} bytes)")
                else:
                    log_step(f"⚠️ 数据源{i}访问异常: 状态码 {response.status_code}", "WARNING")
            except Exception as e:
                log_step(f"❌ 数据源{i}访问失败: {str(e)}", "ERROR")
        
        return True
    except Exception as e:
        log_step(f"网络检查失败: {str(e)}", "ERROR")
        return False

def check_dingtalk_config():
    """检查钉钉配置"""
    log_step("检查钉钉配置")
    try:
        webhook = os.getenv('DINGTALK_WEBHOOK')
        if webhook:
            log_step(f"✅ 检测到DINGTALK_WEBHOOK环境变量")
            log_step(f"Webhook长度: {len(webhook)} 字符")
            
            # 不进行实际连接测试以避免频率限制
            log_step("ℹ️ 跳过钉钉连接测试以避免频率限制")
            return True
        else:
            log_step("⚠️ 未找到DINGTALK_WEBHOOK环境变量", "WARNING")
            return True  # 没有钉钉配置不算错误
    except Exception as e:
        log_step(f"钉钉配置检查失败: {str(e)}", "ERROR")
        return False

def test_minimal_execution():
    """测试最小化执行"""
    log_step("测试最小化执行")
    try:
        # 导入主要模块
        from index_config import index_manager
        from data_collector import DataCollector
        from data_processor import DataProcessor
        
        log_step("✅ 核心模块导入成功")
        
        # 获取一个指数进行测试
        indexes = index_manager.get_all_indexes()
        if not indexes:
            log_step("❌ 没有配置的指数", "ERROR")
            return False
            
        test_index = indexes[0]
        log_step(f"测试指数: {test_index.name} ({test_index.code})")
        
        # 测试数据获取
        collector = DataCollector()
        raw_data = collector.fetch_csv_data(test_index.url)
        log_step(f"✅ 数据获取成功 ({len(raw_data)} 行)")
        
        # 测试数据处理
        processor = DataProcessor()
        processed_data = processor.analyze_data(raw_data)
        log_step("✅ 数据处理成功")
        
        return True
    except Exception as e:
        log_step(f"最小化执行测试失败: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

def main():
    """主诊断函数"""
    print("=" * 50)
    print("🔍 GitHub Actions 环境快速诊断")
    print("=" * 50)
    
    # 执行各项检查
    checks = [
        ("Python环境检查", check_python_environment),
        ("依赖包检查", check_required_packages),
        ("Matplotlib配置检查", check_matplotlib_backend),
        ("工作目录检查", check_working_directory),
        ("网络访问检查", check_network_access),
        ("钉钉配置检查", check_dingtalk_config),
        ("最小化执行测试", test_minimal_execution)
    ]
    
    results = []
    for name, func in checks:
        try:
            result = func()
            results.append((name, result))
            status = "✅ 通过" if result else "❌ 失败"
            log_step(f"{name}: {status}")
        except Exception as e:
            log_step(f"{name}: 执行异常 - {str(e)}", "ERROR")
            results.append((name, False))
            traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 诊断结果汇总:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n📈 总体结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有检查都通过！")
        return 0
    else:
        print("💥 存在问题需要修复")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)