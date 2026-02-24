"""组件与价格 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Component, Price
from app.schemas import ComponentCreate, PriceUpdateRequest
from app.services.price_sync import sync_component_price

router = APIRouter(prefix="/api", tags=["components"])


@router.get("/components")
async def list_components(
    component_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Component).options(selectinload(Component.prices))
    if component_type:
        q = q.where(Component.component_type == component_type)
    result = await db.execute(q)
    items = result.scalars().unique().all()
    out = []
    for c in items:
        prices = [{"source": p.source, "price": p.price, "url": p.url} for p in c.prices]
        min_price = min((p.price for p in c.prices), default=None)
        out.append({
            "id": c.id,
            "name": c.name,
            "component_type": c.component_type,
            "brand": c.brand,
            "model": c.model,
            "performance_score": c.performance_score,
            "aesthetics_score": c.aesthetics_score,
            "prices": prices,
            "min_price": min_price,
        })
    return {"items": out}


@router.post("/components", status_code=201)
async def create_component(
    body: ComponentCreate,
    db: AsyncSession = Depends(get_db),
):
    c = Component(
        name=body.name,
        component_type=body.component_type,
        brand=body.brand,
        model=body.model,
        performance_score=body.performance_score,
        aesthetics_score=body.aesthetics_score,
        power_consumption=body.power_consumption,
        rgb_support=body.rgb_support,
        form_factor=body.form_factor,
        socket=body.socket,
        chipset=body.chipset,
    )
    db.add(c)
    await db.flush()
    await db.refresh(c)
    return {"id": c.id, "name": c.name}


@router.put("/prices")
async def update_price(
    body: PriceUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Component).where(Component.id == body.component_id))
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(404, "Component not found")
    
    existing = next((p for p in comp.prices if p.source == body.source), None)
    if existing:
        existing.price = body.price
        existing.url = body.url
    else:
        p = Price(component_id=comp.id, source=body.source, price=body.price, url=body.url)
        db.add(p)
    return {"ok": True}


@router.post("/prices/sync/{component_id}")
async def trigger_sync(
    component_id: int,
    source: str = "manual",
    db: AsyncSession = Depends(get_db),
):
    p = await sync_component_price(db, component_id, source)
    if p:
        return {"ok": True, "price": p.price}
    return {"ok": False, "message": "Sync not available for this source"}
