"""手动/数据库价格源 - 作为默认数据源"""
from app.services.price_providers.base import BasePriceProvider, PriceResult


class ManualPriceProvider(BasePriceProvider):
    source_name = "manual"
    
    async def fetch_price(self, component_name: str, component_id: int, **kwargs) -> PriceResult | None:
        # 手动源不实时拉取，由数据库记录提供
        return None
    
    async def search_components(self, keyword: str, component_type: str, limit: int = 10) -> list[dict]:
        return []
