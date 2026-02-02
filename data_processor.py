"""
数据处理模块 - 负责数据清洗、分析和指标计算
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        pass
    
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析CSV数据，提取关键指标
        
        Args:
            df: 原始CSV数据
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            logger.info("开始数据分析...")
            
            # 数据预处理
            processed_df = self._preprocess_data(df)
            
            # 计算关键指标
            metrics = self._calculate_metrics(processed_df)
            
            # 生成分析结果
            analysis_result = {
                'raw_data': df,
                'processed_data': processed_df,
                'metrics': metrics,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info("数据分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"数据分析失败: {str(e)}")
            raise Exception(f"数据分析过程中发生错误: {str(e)}")
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            df: 原始数据框
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        # 创建数据副本
        processed_df = df.copy()
        
        # 数据类型转换和清理
        # 注意：这里需要根据实际Excel结构调整列名
        if '日期Date' in processed_df.columns:
            processed_df['date'] = pd.to_datetime(processed_df['日期Date'], format='%Y%m%d', errors='coerce')
            processed_df = processed_df.dropna(subset=['date'])
        
        if '股息率2（计算用股本）D/P2' in processed_df.columns:
            processed_df['dividend_rate'] = pd.to_numeric(
                processed_df['股息率2（计算用股本）D/P2'], errors='coerce'
            )
            processed_df = processed_df.dropna(subset=['dividend_rate'])
        
        # 按日期降序排序（最新日期在前）
        if 'date' in processed_df.columns:
            processed_df = processed_df.sort_values('date', ascending=False)  # 按时间降序排列，最新日期在前
        
        # 只保留最近15天的数据
        if len(processed_df) > 15:
            processed_df = processed_df.head(15)
            
        logger.debug(f"预处理后数据形状: {processed_df.shape}")
        return processed_df
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        计算关键指标
        
        Args:
            df: 处理后的数据框
            
        Returns:
            Dict: 指标字典
        """
        metrics = {}
        
        if 'dividend_rate' not in df.columns:
            logger.warning("数据中未找到dividend_rate列")
            return metrics
            
        dividend_rates = df['dividend_rate']
        
        # 基础统计指标
        metrics['current_rate'] = float(dividend_rates.iloc[0]) if len(dividend_rates) > 0 else 0
        metrics['avg_15d'] = float(dividend_rates.mean())
        metrics['max_15d'] = float(dividend_rates.max())
        metrics['min_15d'] = float(dividend_rates.min())
        metrics['std_15d'] = float(dividend_rates.std())
        
        # 趋势指标
        if len(dividend_rates) >= 2:
            metrics['daily_change'] = float(dividend_rates.iloc[0] - dividend_rates.iloc[1])
            metrics['change_percent'] = float((metrics['daily_change'] / dividend_rates.iloc[1]) * 100) if dividend_rates.iloc[1] != 0 else 0
        
        # 相对位置指标
        metrics['percentile_15d'] = float(
            (dividend_rates.iloc[0] - metrics['min_15d']) / 
            (metrics['max_15d'] - metrics['min_15d']) * 100
        ) if metrics['max_15d'] != metrics['min_15d'] else 50
        
        logger.debug(f"计算得到的指标: {metrics}")
        return metrics
    
    def get_trend_analysis(self, df: pd.DataFrame) -> str:
        """
        获取趋势分析文本
        
        Args:
            df: 数据框
            
        Returns:
            str: 趋势分析描述
        """
        if 'dividend_rate' not in df.columns or len(df) < 2:
            return "数据不足，无法进行趋势分析"
            
        current_rate = df['dividend_rate'].iloc[0]
        previous_rate = df['dividend_rate'].iloc[1]
        
        if current_rate > previous_rate:
            trend = "上升"
        elif current_rate < previous_rate:
            trend = "下降"
        else:
            trend = "持平"
            
        return f"股息率{trend}，当前值为{current_rate:.4f}"