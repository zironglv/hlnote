"""
数据收集模块 - 负责从网络获取CSV数据
"""

import requests
import pandas as pd
import logging
from typing import Optional
import io
import os

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