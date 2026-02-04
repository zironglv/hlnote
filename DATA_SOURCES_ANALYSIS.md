# 数据源分析报告

## 当前使用的数据源

### 1. 中证指数官网 Excel 文件（主要数据源）

**数据来源**: `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/{INDEX_CODE}indicator.xls`

**可用字段**:
- 日期Date
- 指数代码Index Code
- 指数中文全称Chinese Name(Full)
- 指数中文简称Index Chinese Name
- 指数英文全称English Name(Full)
- 指数英文简称Index English Name
- **市盈率1（总股本）P/E1**
- **市盈率2（计算用股本）P/E2**
- **股息率1（总股本）D/P1**
- **股息率2（计算用股本）D/P2**

**优点**:
- 官方数据源，准确可靠
- 包含最近20天的数据
- 可以计算历史分位数

**缺点**:
- 不包含PB数据
- 不包含国债收益率数据
- 需要手动计算分位数和平均值

### 2. AKShare - stock_zh_index_value_csindex（辅助数据源）

**接口**: `ak.stock_zh_index_value_csindex(symbol=index_code)`

**可用字段**:
- 日期
- 指数代码
- 指数中文全称
- 指数中文简称
- 指数英文全称
- 指数英文简称
- **市盈率1**
- **市盈率2**
- **股息率1**
- **股息率2**

**优点**:
- API调用方便
- 数据格式统一
- 可以作为Excel数据的备份

**缺点**:
- 同样不包含PB数据
- 数据量有限（只返回近期数据）
- 可能在GitHub Actions环境中不稳定

### 3. AKShare - bond_china_yield（国债收益率数据）

**接口**: `ak.bond_china_yield()`

**可用字段**:
- 曲线名称
- 1年
- 5年
- **10年**
- 20年
- 30年
- 50年

**优点**:
- 提供完整的国债收益率曲线
- 可以计算股息率vs国债收益率价差

**缺点**:
- 可能在GitHub Actions环境中不稳定
- 需要筛选国债曲线（排除其他债券类型）

## 数据缺失情况

### 1. PB（市净率）数据

**状态**: ❌ 不可用

**原因**:
- 中证指数官网Excel文件不包含PB数据
- AKShare的 `stock_zh_index_value_csindex` 接口不提供PB数据
- 其他接口（如 `index_value_hist_funddb`）在当前版本中已不存在

**替代方案**:
- 方案1: 从东方财富网或其他网站爬取（需要维护，可能不稳定）
- 方案2: 使用付费数据源（如Wind、同花顺iFinD）
- 方案3: 接受PB数据缺失，在报告中显示"N/A"

### 2. 数据稳定性问题

**问题**: AKShare数据在GitHub Actions环境中显示N/A，但在本地环境正常

**可能原因**:
1. **网络问题**: GitHub Actions运行器在中国大陆外，访问中文数据源可能较慢或超时
2. **API限制**: AKShare可能有IP访问频率限制
3. **Python版本差异**: 本地Python 3.13.4 vs GitHub Actions Python 3.11
4. **依赖库版本差异**: AKShare在GitHub Actions环境中可能使用不同版本

**解决方案**:
1. **增加重试机制**: 对API调用添加重试逻辑
2. **增加超时时间**: 设置更长的超时时间
3. **使用代理**: 在GitHub Actions中使用中国区代理
4. **降级处理**: 当API失败时，使用Excel数据作为备份

## 推荐的数据获取策略

### 优先级1: Excel文件（最稳定）
```python
# 使用中证指数官网Excel文件作为主要数据源
excel_data = fetch_excel_data(index_code)
```

### 优先级2: AKShare API（备份）
```python
# 如果Excel失败，尝试使用AKShare API
try:
    api_data = fetch_akshare_data(index_code)
except Exception as e:
    logger.warning(f"AKShare API失败，使用Excel数据")
```

### 优先级3: 历史数据缓存
```python
# 如果所有数据源都失败，使用上次成功的数据
if not data:
    data = load_cached_data(index_code)
```

## 代码改进建议

### 1. 增加重试机制

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"第{attempt + 1}次尝试失败，{delay}秒后重试...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def fetch_bond_yield():
    return ak.bond_china_yield()
```

### 2. 增加超时设置

```python
import requests
from akshare import stock_zh_index_value_csindex

# 设置请求超时
import akshare as ak
ak.set_timeout(30)  # 30秒超时
```

### 3. 接受数据缺失

在报告中明确说明哪些数据不可用：

```python
metrics = {
    'pe': pe_value if pe_value is not None else 'N/A',
    'pb': 'N/A (数据源暂不提供)',
    'bond_yield': bond_yield if bond_yield is not None else 'N/A'
}
```

## 其他免费数据源探索

### 1. Tushare
- 需要注册获取token
- 提供全面的A股数据
- 免费版有调用次数限制

### 2. Baostock
- 免费证券数据平台
- 提供历史行情数据
- 不需要注册

### 3. 证券宝
- 免费开源
- 提供大量准确数据
- 需要安装客户端

### 4. 东方财富网爬虫
- 数据最全面
- 可能违反网站使用条款
- 需要维护爬虫代码

## 结论

当前项目主要依赖中证指数官网Excel文件获取数据，这是最稳定的数据源。AKShare API作为备份，但存在稳定性问题。

**建议**:
1. ✅ 继续使用Excel文件作为主要数据源
2. ✅ 改进错误处理和重试机制
3. ✅ 接受PB数据缺失的现实
4. ⚠️ 探索其他免费数据源作为补充
5. ⚠️ 如果需要PB数据，考虑使用付费数据源

**GitHub Actions部署建议**:
1. 增加详细的日志输出
2. 使用缓存减少API调用
3. 考虑使用自托管runner改善网络访问
4. 在报告中明确标注数据来源和限制