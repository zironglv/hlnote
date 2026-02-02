"""
指数配置管理模块 - 管理多个指数的配置信息
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class IndexConfig:
    """指数配置类"""
    name: str  # 指数名称
    code: str  # 指数代码
    url: str   # 数据URL
    description: str = ""  # 描述
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.description:
            self.description = f"{self.name}({self.code})"

# 默认指数配置
DEFAULT_INDEXES = [
    IndexConfig(
        name="红利低波指数",
        code="H30269",
        url="https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
        description="中证红利低波指数"
    ),
    IndexConfig(
        name="红利低波100指数", 
        code="930955",
        url="https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930955indicator.xls",
        description="中证红利低波100指数"
    )
]

class IndexManager:
    """指数管理器"""
    
    def __init__(self, indexes: List[IndexConfig] = None):
        """
        初始化指数管理器
        
        Args:
            indexes: 指数配置列表，如果为None则使用默认配置
        """
        self.indexes = indexes or DEFAULT_INDEXES.copy()
    
    def get_index_by_code(self, code: str) -> IndexConfig:
        """
        根据代码获取指数配置
        
        Args:
            code: 指数代码
            
        Returns:
            IndexConfig: 指数配置对象
        """
        for index in self.indexes:
            if index.code == code:
                return index
        raise ValueError(f"未找到代码为 {code} 的指数配置")
    
    def get_all_indexes(self) -> List[IndexConfig]:
        """
        获取所有指数配置
        
        Returns:
            List[IndexConfig]: 所有指数配置列表
        """
        return self.indexes.copy()
    
    def add_index(self, index: IndexConfig):
        """
        添加新的指数配置
        
        Args:
            index: 指数配置对象
        """
        self.indexes.append(index)
    
    def remove_index(self, code: str):
        """
        移除指定代码的指数配置
        
        Args:
            code: 指数代码
        """
        self.indexes = [idx for idx in self.indexes if idx.code != code]
    
    def update_index(self, code: str, **kwargs):
        """
        更新指定代码的指数配置
        
        Args:
            code: 指数代码
            **kwargs: 要更新的属性
        """
        for i, index in enumerate(self.indexes):
            if index.code == code:
                for key, value in kwargs.items():
                    if hasattr(index, key):
                        setattr(index, key, value)
                break
        else:
            raise ValueError(f"未找到代码为 {code} 的指数配置")

# 全局索引管理器实例
index_manager = IndexManager()