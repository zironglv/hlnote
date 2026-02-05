"""
最终验证：使用Playwright在无头模式下验证优化版报告
"""
import asyncio
from playwright.async_api import async_playwright
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def validate_optimized_report(html_path):
    """验证优化版报告"""
    if not html_path or not os.path.exists(html_path):
        logger.error(f"HTML文件不存在: {html_path}")
        return False
    
    async with async_playwright() as p:
        # 启动浏览器（无头模式）
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置页面视口大小
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # 导航到本地HTML文件
        file_url = f"file://{os.path.abspath(html_path)}"
        await page.goto(file_url)
        
        logger.info(f"验证页面: {html_path}")
        
        # 等待页面加载完成
        await page.wait_for_load_state("networkidle")
        
        # 验证页面标题
        title = await page.title()
        logger.info(f"  页面标题: {title}")
        
        # 验证关键元素
        checks = {
            "header": await page.query_selector(".header"),
            "stats-grid": await page.query_selector(".stats-grid"),
            "stat-cards": await page.query_selector_all(".stat-card"),
            "chart-container": await page.query_selector(".chart-container"),
            "analysis-section": await page.query_selector(".analysis-section"),
            "advice-card": await page.query_selector(".advice-card"),
            "footer": await page.query_selector(".footer")
        }
        
        # 输出验证结果
        for element, exists in checks.items():
            status = "✅" if exists else "❌"
            if element == "stat-cards":
                logger.info(f"  {status} {element}: {len(exists)} 个指标卡片")
            else:
                logger.info(f"  {status} {element}: {'存在' if exists else '不存在'}")
        
        # 截图验证
        screenshot_path = html_path.replace('.html', '_validation_screenshot.png')
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"  验证截图已保存: {screenshot_path}")
        
        # 关闭浏览器
        await browser.close()
        
        # 返回验证结果
        success = all([
            checks["header"],
            checks["stats-grid"],
            checks["stat-cards"],
            checks["footer"],
            len(checks["stat-cards"]) > 0  # 确保有指标卡片
        ])
        
        return success

async def main():
    """主函数 - 验证所有优化版报告"""
    logger.info("开始最终验证：优化版报告质量检查")
    
    # 查找所有优化版报告
    import glob
    report_paths = glob.glob("reports/optimized_*/optimized_index.html")
    
    if not report_paths:
        logger.error("未找到优化版报告文件")
        return
    
    logger.info(f"找到 {len(report_paths)} 个优化版报告")
    
    results = []
    for report_path in report_paths:
        logger.info(f"验证报告: {os.path.basename(os.path.dirname(report_path))}")
        success = await validate_optimized_report(report_path)
        results.append((report_path, success))
        logger.info(f"  验证结果: {'✅ 通过' if success else '❌ 失败'}\n")
    
    # 总结
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    logger.info("=== 最终验证总结 ===")
    logger.info(f"总报告数: {total}")
    logger.info(f"通过: {passed}")
    logger.info(f"失败: {failed}")
    
    if passed == total:
        logger.info("🎉 所有优化版报告验证通过！")
        print("\n✅ 优化版报告验证成功完成！")
        print(f"生成的优化版报告:")
        for report_path, _ in results:
            print(f"  - {report_path}")
    else:
        logger.error("❌ 部分报告验证失败")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
