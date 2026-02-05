#!/bin/bash
# AI投研助手部署脚本

echo "🚀 开始部署 AI投研助手项目"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 环境检查通过"

# 检查并安装依赖
if [ -f "requirements.txt" ]; then
    echo "📦 安装项目依赖..."
    pip3 install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "⚠️ 未找到 requirements.txt 文件"
fi

# 验证关键文件
echo "🔍 验证项目文件..."
files=(
    "main.py"
    "data_collector.py" 
    "data_processor.py"
    "optimized_report_generator.py"
    "index_config.py"
    "index.html"
)

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 关键文件缺失: $file"
        exit 1
    else
        echo "✅ 找到文件: $file"
    fi
done

echo "✅ 项目文件验证通过"

# 测试数据收集功能
echo "🧪 测试数据收集功能..."
python3 -c "
from data_collector import DataCollector
from index_config import index_manager
import logging
logging.basicConfig(level=logging.WARNING)

try:
    collector = DataCollector()
    indexes = index_manager.get_all_indexes()
    if indexes:
        test_data = collector.fetch_csv_data(indexes[0].url)
        print('✅ 数据收集功能正常')
    else:
        print('⚠️ 未找到配置的指数')
except Exception as e:
    print(f'❌ 数据收集功能测试失败: {e}')
    exit 1
"

echo "✅ 功能测试通过"

# 生成测试报告
echo "📊 生成最新测试报告..."
python3 generate_optimized_reports.py

echo "✅ 测试报告生成完成"

echo "🎉 AI投研助手部署完成！"
echo ""
echo "📋 部署后操作："
echo "1. 检查生成的报告: open index.html"
echo "2. 运行主程序: python3 main.py"
echo "3. 查看报告: 在浏览器中打开 http://localhost:8080"
echo ""
echo "💡 提示：项目已准备好提交到GitHub"