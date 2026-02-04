"""
数据收集模块 - 负责从网络获取CSV数据、估值数据和国债收益率数据
"""

import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any
import io
import os
import akshare as ak
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataCollector:
    """数据收集器"""
    
    def __init__(self, csv_url: str = None):
        """
        初始化数据收集器
        
        Args:
            csv_url: CSV文件的URL地址
        """
        # 默认使用中证指数的红利低波指数数据（Excel格式）
        self.csv_url = csv_url or "https://csi-web-dev.oss-cn-shanghai-finance-1-pub.aliyuncs.com/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls"
        self.timeout = 30  # 请求超时时间
        
    def fetch_csv_data(self, url: str = None) -> pd.DataFrame:
        """
        获取CSV数据
        
        Args:
            url: 可选的URL参数，如果提供则使用此URL而非实例URL
            
        Returns:
            pandas.DataFrame: 解析后的数据
            
        Raises:
            Exception: 数据获取或解析失败时抛出异常
        """
        try:
            target_url = url or self.csv_url
            logger.info(f"开始获取CSV数据: {target_url}")
            
            # 发送HTTP请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(target_url, timeout=self.timeout, headers=headers)
            response.raise_for_status()  # 检查HTTP状态码
            
            # 检查响应内容大小
            if len(response.content) < 1000:  # 最少应该有1KB
                logger.warning(f"响应内容过短: {len(response.content)} 字节")
            
            # 判断文件格式并解析
            if target_url.endswith('.xls') or target_url.endswith('.xlsx'):
                # Excel格式数据
                df = pd.read_excel(io.BytesIO(response.content))
                logger.info("检测到Excel格式数据，使用read_excel解析")
            else:
                # CSV格式数据
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(io.StringIO(csv_content))
                logger.info("使用read_csv解析CSV数据")
            
            logger.info(f"成功获取数据，共{len(df)}行记录")
            logger.debug(f"数据列名: {list(df.columns)}")
            
            return df
            
        except requests.RequestException as e:
            logger.warning(f"网络请求失败: {str(e)}")
            # 网络请求失败时尝试使用本地文件
            # 提取URL中的文件名或使用默认文件名
            local_file = None
            if url:
                if not url.startswith('http'):
                    # 本地文件路径
                    local_file = url
                else:
                    # 从URL中提取文件名
                    import re
                    match = re.search(r'/([^/]+\.xls[x]?)$', url)
                    if match:
                        local_file = match.group(1)
            
            if not local_file:
                local_file = '930955indicator.xls'  # 默认本地文件
                
            if os.path.exists(local_file):
                logger.info(f"尝试使用本地文件: {local_file}")
                try:
                    df = pd.read_excel(local_file)
                    logger.info(f"本地文件读取成功，共{len(df)}行记录")
                    return df
                except Exception as local_e:
                    logger.error(f"本地文件读取失败: {str(local_e)}")
                    raise Exception(f"无法获取数据: 网络请求失败({str(e)})且本地文件读取失败({str(local_e)})")
            else:
                logger.error(f"找不到本地文件: {local_file}")
                raise Exception(f"无法获取CSV数据: {str(e)} 且无本地备份文件")
        except pd.errors.EmptyDataError as e:
            logger.error(f"CSV数据为空: {str(e)}")
            raise Exception(f"CSV数据格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"数据获取过程中发生未知错误: {str(e)}")
            raise Exception(f"数据获取失败: {str(e)}")
    
    def fetch_valuation_data(self, index_code: str) -> Dict[str, Any]:
        """
        获取指数估值数据（PE）

        Args:
            index_code: 指数代码

        Returns:
            Dict: 包含PE估值数据的字典
        """
        try:
            logger.info(f"开始获取指数 {index_code} 的估值数据")

            # 使用AKShare获取指数估值数据
            # 注意：这个API只提供PE数据，不提供PB数据
            try:
                valuation_df = ak.stock_zh_index_value_csindex(symbol=index_code)
            except:
                # 如果失败，尝试使用6位代码
                valuation_df = ak.stock_zh_index_value_csindex(symbol=str(index_code))

            if valuation_df.empty:
                logger.warning(f"未找到指数 {index_code} 的估值数据")
                return {
                    'pe': None,
                    'pe_percentile': None,
                    'pe_history': [],
                    'pb_history': []
                }
            
            # 提取最新数据
            latest_data = valuation_df.iloc[0]
            
            # 尝试不同的列名
            pe_value = None
            pb_value = None
            
            for pe_col in ['市盈率2', '市盈率1', 'pe', 'PE']:
                if pe_col in latest_data:
                    pe_value = float(latest_data[pe_col])
                    break

            # 计算历史分位数（如果有历史数据）
            pe_percentile = None

            if 'pe' in valuation_df.columns and len(valuation_df) > 10:
                current_pe = pe_value if pe_value else valuation_df['pe'].iloc[0]
                pe_percentile = (valuation_df['pe'] <= current_pe).sum() / len(valuation_df) * 100

            logger.info(f"指数 {index_code} 估值数据获取成功: PE={pe_value}")

            return {
                'pe': pe_value,
                'pe_percentile': pe_percentile,
                'pe_history': valuation_df['pe'].tolist()[:30] if 'pe' in valuation_df.columns else []
            }

        except Exception as e:
            logger.error(f"获取估值数据失败: {str(e)}")
            return {
                'pe': None,
                'pe_percentile': None,
                'pe_history': [],
                'pb_history': []
            }
    
    def fetch_bond_yield(self, bond_type: str = "10y") -> Dict[str, Any]:
        """
        获取国债收益率数据
        
        Args:
            bond_type: 债券类型，支持 '10y'(10年期), '5y'(5年期), '1y'(1年期)
            
        Returns:
            Dict: 包含国债收益率数据的字典
        """
        try:
            logger.info(f"开始获取{bond_type}国债收益率数据")
            
            # 使用AKShare获取国债收益率数据
            bond_yield_df = ak.bond_china_yield()
            
            if bond_yield_df.empty:
                logger.warning("未找到国债收益率数据")
                return {
                    'current_yield': None,
                    'yield_history': [],
                    'yield_change': None,
                    'date': None
                }
            
            # 映射债券类型到列名
            yield_column_mapping = {
                '10y': '10年',
                '5y': '5年',
                '1y': '1年'
            }
            yield_column = yield_column_mapping.get(bond_type, '10年')
            
            # 筛选国债收益率曲线
            bond_data = bond_yield_df[bond_yield_df['曲线名称'].astype(str).str.contains('国债')]
            
            if bond_data.empty:
                logger.warning(f"未找到国债收益率数据")
                return {
                    'current_yield': None,
                    'yield_history': [],
                    'yield_change': None,
                    'date': None
                }
            
            # 获取最新收益率
            latest_bond = bond_data.iloc[0]
            current_yield = float(latest_bond[yield_column]) if pd.notna(latest_bond[yield_column]) else None
            
            # 计算收益率变化
            yield_change = None
            if len(bond_data) > 1:
                previous_yield = float(bond_data.iloc[1][yield_column]) if pd.notna(bond_data.iloc[1][yield_column]) else None
                if current_yield and previous_yield:
                    yield_change = current_yield - previous_yield
            
            date_str = latest_bond['日期'] if '日期' in latest_bond else None
            
            logger.info(f"成功获取国债收益率: {current_yield}%")
            
            return {
                'current_yield': current_yield,
                'yield_history': bond_data[yield_column].tolist()[:30] if yield_column in bond_data.columns else [],
                'yield_change': yield_change,
                'date': date_str
            }
            
        except Exception as e:
            logger.warning(f"获取国债收益率失败: {str(e)}")
            return {
                'current_yield': None,
                'yield_history': [],
                'yield_change': None,
                'date': None
            }
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        验证数据完整性
        
        Args:
            df: 待验证的数据框
            
        Returns:
            bool: 数据是否有效
        """
        if df.empty:
            logger.warning("数据框为空")
            return False
            
        # 检查必要的列是否存在
        required_columns = ['日期Date', '股息率2（计算用股本）D/P2']  # 根据实际Excel结构调整
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"缺少必要列: {missing_columns}")
            return False
            
        # 检查是否有足够的数据
        if len(df) < 5:  # 至少需要5天的数据
            logger.warning(f"数据量不足，仅有{len(df)}条记录")
            return False
            
        return True