# 项目部署配置指南

## GitHub 仓库部署状态
- ✅ 代码已成功部署到 GitHub 仓库：https://github.com/zironglv/hlnote.git

## 需要配置的安全密钥

### 1. 钉钉机器人 Webhook
- **用途**：用于接收每日指数分析报告
- **配置位置**：GitHub 仓库的 Settings → Secrets and variables → Actions
- **变量名**：`DINGTALK_WEBHOOK`
- **值**：您的钉钉机器人 Webhook URL

#### 如何设置钉钉机器人：
1. 在钉钉群中添加自定义机器人
2. 选择安全设置（建议使用关键词模式）
3. 添加关键词：`AI投研助手`、`股息率`、`报告`、`分析`、`投资`
4. 复制 Webhook 地址
5. 在 GitHub 仓库的 Secrets 中设置 `DINGTALK_WEBHOOK`

## GitHub Actions 自动化配置

### 工作流文件
- 文件位置：`.github/workflows/daily_report.yml`
- 执行频率：每天 UTC 时间 23:00（北京时间次日早上 7:00）
- 手动触发：支持在 GitHub Actions 页面手动运行

### 执行流程
1. 定时调度 → 多指数数据收集 → 并行处理 → 图表生成 → 钉钉推送

## 数据源配置

### 默认数据源
- 使用中证指数公司官方数据：https://www.csindex.com.cn/
- 数据格式：Excel (.xls) 文件
- 包含的指数：
  - 红利低波指数 (H30269)
  - 红利低波100指数 (930955)

### 自定义数据源
如需添加其他指数，可通过以下方式：
1. 修改 `index_config.py` 中的 `DEFAULT_INDEXES` 列表
2. 或在运行时使用 `add_custom_index()` 函数

## 项目结构说明

### 核心模块
- `main_multi.py` - 主程序入口
- `multi_index_analyzer.py` - 多指数分析器
- `data_collector.py` - 数据收集器
- `data_processor.py` - 数据处理器
- `report_generator.py` - 报告生成器
- `dingtalk_sender.py` - 钉钉消息发送器
- `index_config.py` - 指数配置管理

### 配置文件
- `.github/workflows/daily_report.yml` - GitHub Actions 工作流
- `requirements.txt` - Python 依赖包
- `config.md` - 详细配置说明

## 本地测试方法

### 环境要求
- Python 3.8+

### 安装依赖
```bash
pip install -r requirements.txt
pip install openpyxl
```

### 运行测试
```bash
python test_local.py
```

## 故障排查

### 常见问题
1. 如果 GitHub Actions 运行失败，请检查：
   - `DINGTALK_WEBHOOK` 密钥是否正确配置
   - 数据源 URL 是否可用
   - 网络连接是否正常

2. 如果报告生成失败，请检查：
   - Excel 文件格式是否正确
   - 数据列是否存在且格式正确

### 日志查看
- GitHub Actions 运行日志可在 Actions 标签页查看
- 本地运行日志保存在 `multi_index_dividend_analyzer.log`

## 维护说明

### 定期检查
- 检查数据源 URL 是否仍然有效
- 监控钉钉机器人是否正常接收消息
- 查看报告准确性

### 更新配置
如需更新指数配置或调整分析参数，可以直接编辑相应的配置文件。