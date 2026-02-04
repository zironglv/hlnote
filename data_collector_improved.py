"""
改进的数据收集器 - 增加重试机制和更好的错误处理
"""
import pandas as pd
import requests
import logging
from typing import Dict, Any, Optional
from io import BytesIO
import time
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 1.5):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避因子
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} 在 {max_attempts} 次尝试后失败: {str(e)}")
                        raise
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"{func.__name__} 第 {attempt + 1} 次尝试失败，{wait_time:.1f}秒后重试... 错误: {str(e)}")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


class ImprovedDataCollector:
    """改进的数据收集器，支持多种数据源和重试机制"""

    def __init__(self):
        self.logger = logger

    @retry(max_attempts=3, delay=2.0, backoff=1.5)
    def fetch_excel_data(self, url: str, timeout: int = 30) -> Optional[pd.DataFrame]:
        """
        从Excel文件获取数据（主要数据源）

        Args:
            url: Excel文件URL
            timeout: 超时时间（秒）

        Returns:
            DataFrame or None
        """
        try:
            self.logger.info(f"开始下载Excel数据: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # 检测文件类型
            content_type = response.headers.get('content-type', '')
            if 'excel' in content_type or 'spreadsheet' in content_type:
                self.logger.info("检测到Excel格式数据，使用read_excel解析")
                df = pd.read_excel(BytesIO(response.content))
            else:
                self.logger.info("检测到CSV格式数据，使用read_csv解析")
                df = pd.read_csv(BytesIO(response.content))

            self.logger.info(f"成功获取数据，共 {len(df)} 行记录")
            return df

        except requests.Timeout:
            raise Exception(f"请求超时（{timeout}秒）")
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"数据解析失败: {str(e)}")

    def fetch_valuation_data_primary(self, index_code: str) -> Dict[str, Any]:
        """
        获取估值数据（主要方法：从Excel文件）

        Args:
            index_code: 指数代码

        Returns:
            估值数据字典
        """
        try:
            # 尝试从Excel文件获取PE数据
            url = f"https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/{index_code}indicator.xls"
            df = self.fetch_excel_data(url)

            if df is not None and len(df) > 0:
                latest = df.iloc[0]

                # 提取PE数据
                pe_value = None
                for pe_col in ['市盈率2（计算用股本）P/E2', '市盈率1（总股本）P/E1', '市盈率2', '市盈率1']:
                    if pe_col in latest:
                        pe_value = float(latest[pe_col]) if pd.notna(latest[pe_col]) else None
                        if pe_value is not None:
                            break

                # 提取股息率数据
                dividend_value = None
                for div_col in ['股息率2（计算用股本）D/P2', '股息率1（总股本）D/P1', '股息率2', '股息率1']:
                    if div_col in latest:
                        dividend_value = float(latest[div_col]) if pd.notna(latest[div_col]) else None
                        if dividend_value is not None:
                            break

                # 计算历史分位数
                if pe_value is not None:
                    pe_values = []
                    for pe_col in ['市盈率2（计算用股本）P/E2', '市盈率1（总股本）P/E1', '市盈率2', '市盈率1']:
                        if pe_col in df.columns:
                            pe_series = df[pe_col].replace([float('inf'), -float('inf')], None).dropna()
                            if len(pe_series) > 0:
                                pe_values.extend(pe_series.tolist())
                                break

                    if len(pe_values) > 0:
                        pe_min = min(pe_values)
                        pe_max = max(pe_values)
                        if pe_max != pe_min:
                            pe_percentile = (pe_value - pe_min) / (pe_max - pe_min) * 100
                        else:
                            pe_percentile = 50.0
                    else:
                        pe_percentile = 50.0
                else:
                    pe_percentile = None

                return {
                    'pe': pe_value,
                    'pb': None,  # PB数据不可用
                    'dividend_yield': dividend_value,
                    'pe_percentile': pe_percentile,
                    'pb_percentile': None,
                    'data_source': 'excel'
                }

        except Exception as e:
            self.logger.warning(f"从Excel获取估值数据失败: {str(e)}")

        return {}

    @retry(max_attempts=2, delay=1.0, backoff=1.0)
    def fetch_valuation_data_backup(self, index_code: str) -> Dict[str, Any]:
        """
        获取估值数据（备份方法：使用AKShare API）

        Args:
            index_code: 指数代码

        Returns:
            估值数据字典
        """
        try:
            import akshare as ak
            self.logger.info(f"尝试使用AKShare API获取指数 {index_code} 的估值数据")

            df = ak.stock_zh_index_value_csindex(symbol=index_code)

            if df is not None and len(df) > 0:
                latest = df.iloc[0]

                # 提取PE数据
                pe_value = None
                for pe_col in ['市盈率2', '市盈率1']:
                    if pe_col in latest:
                        pe_value = float(latest[pe_col]) if pd.notna(latest[pe_col]) else None
                        if pe_value is not None:
                            break

                # 提取股息率数据
                dividend_value = None
                for div_col in ['股息率2', '股息率1']:
                    if div_col in latest:
                        dividend_value = float(latest[div_col]) if pd.notna(latest[div_col]) else None
                        if dividend_value is not None:
                            break

                # 计算历史分位数
                if pe_value is not None and '市盈率2' in df.columns:
                    pe_series = df['市盈率2'].replace([float('inf'), -float('inf')], None).dropna()
                    if len(pe_series) > 0:
                        pe_min = float(pe_series.min())
                        pe_max = float(pe_series.max())
                        if pe_max != pe_min:
                            pe_percentile = (pe_value - pe_min) / (pe_max - pe_min) * 100
                        else:
                            pe_percentile = 50.0
                    else:
                        pe_percentile = 50.0
                else:
                    pe_percentile = None

                self.logger.info(f"AKShare API获取成功: PE={pe_value}, 股息率={dividend_value}")

                return {
                    'pe': pe_value,
                    'pb': None,
                    'dividend_yield': dividend_value,
                    'pe_percentile': pe_percentile,
                    'pb_percentile': None,
                    'data_source': 'akshare'
                }

        except ImportError:
            self.logger.warning("AKShare未安装，跳过API调用")
        except Exception as e:
            self.logger.warning(f"AKShare API获取失败: {str(e)}")

        return {}

    @retry(max_attempts=3, delay=2.0, backoff=1.5)
    def fetch_bond_yield(self, bond_type: str = "10y") -> Dict[str, Any]:
        """
        获取国债收益率数据

        Args:
            bond_type: 债券类型（10y, 5y, 1y等）

        Returns:
            债券收益率数据
        """
        try:
            import akshare as ak
            self.logger.info(f"获取{bond_type}国债收益率数据")

            bond_yield_df = ak.bond_china_yield()

            if bond_yield_df is None or len(bond_yield_df) == 0:
                return {}

            yield_column_mapping = {
                '10y': '10年',
                '5y': '5年',
                '1y': '1年'
            }
            yield_column = yield_column_mapping.get(bond_type, '10年')

            # 筛选国债收益率曲线
            bond_data = bond_yield_df[bond_yield_df['曲线名称'].astype(str).str.contains('国债')]

            if bond_data.empty:
                self.logger.warning("未找到国债收益率曲线")
                return {}

            # 获取最新收益率
            latest_bond = bond_data.iloc[0]
            current_yield = float(latest_bond[yield_column]) if pd.notna(latest_bond[yield_column]) else None

            # 计算变化（如果有历史数据）
            yield_change = None
            if len(bond_data) > 1 and yield_column in bond_data.columns:
                recent_yields = bond_data[yield_column].dropna()
                if len(recent_yields) >= 2:
                    yield_change = float(recent_yields.iloc[0] - recent_yields.iloc[1])

            # 获取日期
            date_str = None
            if '日期' in bond_data.columns:
                date_str = str(bond_data['日期'].iloc[0])

            self.logger.info(f"成功获取国债收益率: {current_yield}%")

            return {
                'current_yield': current_yield,
                'yield_history': bond_data[yield_column].tolist()[:30],
                'yield_change': yield_change,
                'date': date_str,
                'data_source': 'akshare'
            }

        except ImportError:
            self.logger.warning("AKShare未安装，跳过国债收益率获取")
        except Exception as e:
            self.logger.warning(f"获取国债收益率失败: {str(e)}")

        return {}

    def get_valuation_data(self, index_code: str) -> Dict[str, Any]:
        """
        获取估值数据（自动选择最佳数据源）

        Args:
            index_code: 指数代码

        Returns:
            估值数据字典
        """
        # 首先尝试从Excel获取
        data = self.fetch_valuation_data_primary(index_code)

        # 如果Excel失败，尝试AKShare API
        if not data or data.get('pe') is None:
            self.logger.info("Excel数据获取失败，尝试AKShare API")
            backup_data = self.fetch_valuation_data_backup(index_code)
            if backup_data:
                data = backup_data

        # 标注数据缺失情况
        if data.get('pb') is None:
            self.logger.info("PB数据不可用（数据源暂不提供）")
            data['pb_note'] = '数据源暂不提供PB数据'

        return data


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    collector = ImprovedDataCollector()

    # 测试Excel数据获取
    print("=" * 60)
    print("测试1: 从Excel获取估值数据")
    print("=" * 60)
    data = collector.get_valuation_data('H30269')
    print(f"PE: {data.get('pe')}")
    print(f"PB: {data.get('pb')}")
    print(f"股息率: {data.get('dividend_yield')}")
    print(f"PE分位数: {data.get('pe_percentile')}")
    print(f"数据源: {data.get('data_source')}")

    # 测试国债收益率获取
    print("\n" + "=" * 60)
    print("测试2: 获取国债收益率")
    print("=" * 60)
    bond_data = collector.fetch_bond_yield()
    print(f"10年期国债收益率: {bond_data.get('current_yield')}%")
    print(f"变化: {bond_data.get('yield_change')}")