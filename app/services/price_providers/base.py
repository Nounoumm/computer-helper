"""价格源基类 - 新增 API 需实现此接口"""
from abc import ABC, abstractmethod
from typing import Optional


class PriceResult:
    def __init__(self, price: float, url: str | None = None, in_stock: bool = True):
        self.price = price
        self.url = url
        self.in_stock = in_stock


class BasePriceProvider(ABC):
    """扩展新价格源：继承此类并实现 fetch_price"""
    
    source_name: str = "base"
    
    @abstractmethod
    async def fetch_price(self, component_name: str, component_id: int, **kwargs) -> PriceResult | None:
        """
        根据组件名称或ID获取实时价格
        kwargs 可传入: sku_id, jd_sku, taobao_item_id 等平台特定参数
        """
        pass
    
    @abstractmethod
    async def search_components(self, keyword: str, component_type: str, limit: int = 10) -> list[dict]:
        """搜索组件及价格，用于数据源扩展"""
        pass
