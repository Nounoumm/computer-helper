"""价格同步服务 - 从各数据源更新数据库"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Component, Price
from app.services.price_providers import get_provider


async def sync_component_price(
    db: AsyncSession,
    component_id: int,
    source: str = "manual",
) -> Price | None:
    """从指定来源同步单个组件价格"""
    provider = get_provider(source)
    if not provider:
        return None
    
    result = await db.execute(select(Component).where(Component.id == component_id))
    comp = result.scalar_one_or_none()
    if not comp:
        return None
    
    pr = await provider.fetch_price(comp.name, comp.id)
    if pr is None:
        return None
    
    # 更新或插入价格
    existing = next((p for p in comp.prices if p.source == source), None)
    if existing:
        existing.price = pr.price
        existing.url = pr.url
        return existing
    else:
        price = Price(component_id=comp.id, source=source, price=pr.price, url=pr.url)
        db.add(price)
        return price


async def sync_all_prices(db: AsyncSession, source: str = "manual") -> int:
    """同步所有组件价格 - 实际会遍历各 provider 的 search 或已知组件"""
    result = await db.execute(select(Component))
    components = result.scalars().unique().all()
    count = 0
    for comp in components:
        p = await sync_component_price(db, comp.id, source)
        if p:
            count += 1
    return count
