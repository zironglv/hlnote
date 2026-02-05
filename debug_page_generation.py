# 使用Playwright调试页面生成的测试脚本
import asyncio
from playwright.async_api import async_playwright
import os
import sys
from datetime import datetime
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector
from data_processor import DataProcessor  
from report_generator import ReportGenerator
from index_config import index_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_page_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def generate_test_report():
    """生成测试报告"""
    try:
        logger.info("开始生成测试报告...")
        
        # 获取配置的指数（使用第一个作为测试）
        indexes = index_manager.get_all_indexes()
        
        if not indexes:
            logger.error("没有找到任何指数配置")
            return None, None
        
        test_index = indexes[0]  # 使用第一个指数作为测试
        logger.info(f"使用指数: {test_index.name}({test_index.code}) 进行测试")
        
        # 1. 数据收集
        collector = DataCollector()
        
        # 获取股息率数据
        csv_data = collector.fetch_csv_data(test_index.url)
        
        # 获取估值数据（PE/PB）
        valuation_data = collector.fetch_valuation_data(test_index.code)
        
        # 获取国债收益率数据（10年期）
        bond_yield_data = collector.fetch_bond_yield('10y')
        
        # 2. 数据处理（整合所有数据）
        processor = DataProcessor()
        processed_data = processor.analyze_data(csv_data, bond_yield_data)
        
        # 将估值数据添加到处理结果中
        if valuation_data and 'pe' in valuation_data:
            processed_data['metrics']['pe'] = valuation_data['pe']
        
        # 添加指数信息
        processed_data['index_info'] = {
            'name': test_index.name,
            'code': test_index.code,
            'description': test_index.description
        }
        
        # 3. 报告生成
        generator = ReportGenerator()
        
        # 创建测试输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('test_reports', f'playwright_debug_{timestamp}')
        
        # 准备完整的分析数据
        analysis_data = {
            'processed_data': processed_data['processed_data'],  # 这是DataFrame，用于图表生成
            'metrics': processed_data.get('metrics', {}),
            'analysis_time': processed_data.get('analysis_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        
        report_html, chart_path = generator.generate_report(
            analysis_data, 
            output_dir=output_dir
        )
        
        # 也生成日报版本
        daily_report_html = generator.generate_daily_report(
            {'processed_data': processed_data, 'metrics': processed_data.get('metrics', {}), 'index_info': processed_data.get('index_info', {}), 'analysis_time': processed_data.get('analysis_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))},
            chart_path=chart_path
        )
        
        # 保存日报版本
        daily_report_path = os.path.join(output_dir, 'daily_report.html')
        with open(daily_report_path, 'w', encoding='utf-8') as f:
            f.write(daily_report_html)
        
        logger.info(f"完整报告已保存到: {os.path.join(output_dir, 'index.html')}")
        logger.info(f"日报版本已保存到: {daily_report_path}")
        logger.info(f"图表文件: {chart_path}")
        
        return os.path.join(output_dir, 'index.html'), daily_report_path
        
    except Exception as e:
        logger.error(f"生成测试报告失败: {str(e)}", exc_info=True)
        return None, None

async def test_page_with_playwright(html_path, report_type="full"):
    """使用Playwright打开并测试页面"""
    if not html_path or not os.path.exists(html_path):
        logger.error(f"HTML文件不存在: {html_path}")
        return False
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式以便观察）
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        # 设置页面视口大小
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # 导航到本地HTML文件
        file_url = f"file://{os.path.abspath(html_path)}"
        await page.goto(file_url)
        
        logger.info(f"页面已加载: {file_url}")
        
        # 等待页面加载完成
        await page.wait_for_load_state("networkidle")
        
        # 检查页面标题
        title = await page.title()
        logger.info(f"页面标题: {title}")
        
        # 截图以供检查
        screenshot_path = html_path.replace('.html', f'_{report_type}_screenshot.png')
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"页面截图已保存到: {screenshot_path}")
        
        # 检查页面元素
        try:
            # 检查是否有核心指标网格
            metrics_grid = await page.query_selector(".metrics-grid")
            if metrics_grid:
                logger.info("✅ 找到核心指标网格")
                
                # 获取指标数量
                metrics = await page.query_selector_all(".metric-card")
                logger.info(f"✅ 找到 {len(metrics)} 个指标卡片")
                
                # 输出每个指标的文本内容
                for i, metric in enumerate(metrics):
                    value = await metric.query_selector(".metric-value")
                    label = await metric.query_selector(".metric-label")
                    if value and label:
                        value_text = await value.inner_text()
                        label_text = await label.inner_text()
                        logger.info(f"  指标 {i+1}: {label_text} = {value_text}")
            else:
                logger.warning("⚠️ 未找到核心指标网格")
            
            # 检查趋势分析部分
            trend_analysis = await page.query_selector(".analysis")
            if trend_analysis:
                logger.info("✅ 找到趋势分析部分")
            else:
                logger.warning("⚠️ 未找到趋势分析部分")
            
            # 检查图表容器
            chart_container = await page.query_selector(".chart-container")
            if chart_container:
                chart_img = await page.query_selector(".chart-container img")
                if chart_img:
                    src = await chart_img.get_attribute("src")
                    if src and src.startswith("data:image"):
                        logger.info("✅ 找到图表且已嵌入")
                    else:
                        logger.info("✅ 找到图表容器，但可能使用外部链接")
                else:
                    logger.warning("⚠️ 图表容器中未找到图片")
            else:
                logger.warning("⚠️ 未找到图表容器")
                
        except Exception as e:
            logger.error(f"页面元素检查失败: {str(e)}")
        
        # 保持浏览器打开一段时间以便手动检查
        logger.info("浏览器将在10秒后关闭，您可以在此期间检查页面...")
        await page.wait_for_timeout(10000)  # 等待10秒
        
        # 关闭浏览器
        await browser.close()
        
        return True

async def main():
    """主函数 - 生成报告并用Playwright测试"""
    logger.info("开始Playwright页面生成调试...")
    
    # 生成测试报告
    full_report_path, daily_report_path = await generate_test_report()
    
    if full_report_path:
        logger.info("=== 测试完整报告页面 ===")
        success_full = await test_page_with_playwright(full_report_path, "full")
        
        logger.info("=== 测试日报页面 ===")
        success_daily = await test_page_with_playwright(daily_report_path, "daily")
        
        if success_full and success_daily:
            logger.info("✅ 页面生成和显示测试成功完成")
            print(f"\n📄 生成的报告文件:")
            print(f"   完整报告: {full_report_path}")
            print(f"   日报版本: {daily_report_path}")
        else:
            logger.error("❌ 页面测试未完全成功")
    else:
        logger.error("❌ 无法生成测试报告")

if __name__ == "__main__":
    asyncio.run(main())