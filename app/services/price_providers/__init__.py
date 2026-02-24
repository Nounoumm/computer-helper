"""价格数据源 - 当前仅使用本地/手动价格"""
from app.services.price_providers.base import BasePriceProvider
from app.services.price_providers.manual import ManualPriceProvider


# 仅保留手动价格源，所有价格由数据库维护
PROVIDERS: dict[str, BasePriceProvider] = {
    "manual": ManualPriceProvider(),
}


def get_provider(source: str) -> BasePriceProvider | None:
    return PROVIDERS.get(source)
