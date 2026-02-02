# AI投研助手配置说明

## 钉钉机器人配置

### 必需配置
- 钉钉机器人Webhook URL已在代码中配置
- 无需额外环境变量配置

### 钉钉机器人设置
1. 在钉钉群中添加自定义机器人
2. 选择安全设置（建议使用关键词模式）
3. 添加关键词：`AI投研助手`、`股息率`、`报告`
4. 复制Webhook地址到代码中

## 邮箱配置（已废弃）

~~在GitHub仓库的Settings → Secrets and variables → Actions中设置以下环境变量：~~

### ~~必需配置~~
~~- `EMAIL_USERNAME`: 发件人邮箱地址~~
~~- `EMAIL_PASSWORD`: 邮箱授权码（不是登录密码）~~
~~- `RECIPIENT_EMAIL`: 收件人邮箱地址~~

### ~~可选配置（有默认值）~~
~~- `SMTP_SERVER`: SMTP服务器地址（默认gmail）~~
~~- `SMTP_PORT`: SMTP端口（默认587）~~

## 钉钉机器人消息格式

发送的消息包含：
- 📊 核心指标（当前股息率、历史范围等）
- 🎯 趋势分析
- 💡 投资参考建议
- 📈 自动推送标识

## 钉钉机器人安全设置

建议使用关键词安全模式，关键词包括：
- AI投研助手
- 股息率
- 报告
- 分析
- 投资

## CSV数据源配置

修改 `local_config.py` 中的 `CSV_URL` 参数指向正确的Excel文件地址。

## 自定义配置

可以在各模块的构造函数中传入自定义参数：
```python
collector = DataCollector(csv_url="your_excel_url")
sender = DingTalkSender(webhook_url="your_dingtalk_webhook")
```