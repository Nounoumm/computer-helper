"""配置推荐引擎 - 综合考虑性价比、性能、外观、场景"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Component, Price, ComponentType, UseCase, SceneType


# 各组件预算占比（游戏向）
BUDGET_RATIO_GAMING = {
    ComponentType.CPU: 0.15,
    ComponentType.GPU: 0.35,
    ComponentType.MOTHERBOARD: 0.08,
    ComponentType.RAM: 0.08,
    ComponentType.STORAGE: 0.10,
    ComponentType.PSU: 0.07,
    ComponentType.CASE: 0.07,
    ComponentType.COOLER: 0.05,
    ComponentType.MONITOR: 0.05,
}

# 办公向
BUDGET_RATIO_OFFICE = {
    ComponentType.CPU: 0.25,
    ComponentType.GPU: 0.05,
    ComponentType.MOTHERBOARD: 0.12,
    ComponentType.RAM: 0.15,
    ComponentType.STORAGE: 0.15,
    ComponentType.PSU: 0.06,
    ComponentType.CASE: 0.10,
    ComponentType.COOLER: 0.07,
    ComponentType.MONITOR: 0.05,
}

# 设计/创作向
BUDGET_RATIO_DESIGN = {
    ComponentType.CPU: 0.22,
    ComponentType.GPU: 0.25,
    ComponentType.MOTHERBOARD: 0.08,
    ComponentType.RAM: 0.15,
    ComponentType.STORAGE: 0.12,
    ComponentType.PSU: 0.06,
    ComponentType.CASE: 0.05,
    ComponentType.COOLER: 0.04,
    ComponentType.MONITOR: 0.03,
}

USE_CASE_RATIOS = {
    UseCase.GAMING: BUDGET_RATIO_GAMING,
    UseCase.DESIGN: BUDGET_RATIO_DESIGN,
    UseCase.STREAMING: BUDGET_RATIO_GAMING,  # 类似游戏
    UseCase.DEVELOPMENT: BUDGET_RATIO_OFFICE,
    UseCase.OFFICE: BUDGET_RATIO_OFFICE,
    UseCase.LIGHT: BUDGET_RATIO_OFFICE,
    UseCase.ALL_ROUND: BUDGET_RATIO_GAMING,
}


def get_budget_ratio(use_case: str):
    return USE_CASE_RATIOS.get(UseCase(use_case), BUDGET_RATIO_GAMING)


def _get_component_price(prices: list) -> float | None:
    if not prices:
        return None
    return min(p.price for p in prices)


async def get_components_by_type(
    db: AsyncSession,
    component_type: str,
    budget: float,
    prefer_performance: bool = True,
    prefer_aesthetics: bool = False,
    scene: str | None = None,
    limit: int = 5,
) -> list[tuple[Component, float]]:
    """按类型、预算、偏好筛选组件"""
    ratio = 1.2  # 允许略超预算
    max_price = budget * ratio
    
    from sqlalchemy.orm import selectinload
    q = (
        select(Component)
        .where(Component.component_type == component_type)
        .options(selectinload(Component.prices))
    )
    result = await db.execute(q)
    components = result.scalars().unique().all()
    
    scored: list[tuple[Component, float, float]] = []
    for comp in components:
        prices = comp.prices
        price = _get_component_price(prices)
        if price is None or price > max_price:
            continue
        
        # 性价比分 = 性能 / (价格/1000)
        perf = comp.performance_score or 50
        cost_eff = (perf + 1) / (price / 1000 + 0.01) if price else 0
        
        # 综合分：性能权重 + 性价比 + 外观
        w_perf = 0.5 if prefer_performance else 0.2
        w_cost = 0.3
        w_aes = 0.2 if prefer_aesthetics else 0.05
        aes = comp.aesthetics_score or 50
        
        score = w_perf * perf + w_cost * min(cost_eff, 50) + w_aes * aes
        scored.append((comp, price, score))
    
    scored.sort(key=lambda x: x[2], reverse=True)
    return [(c, p) for c, p, _ in scored[:limit]]


async def recommend_config(
    db: AsyncSession,
    budget: int,
    use_case: str,
    scene: str | None = None,
    priority: str = "balanced",  # performance / cost / aesthetics
) -> dict:
    """
    生成推荐配置
    priority: performance 偏性能, cost 偏性价比, aesthetics 偏外观
    """
    ratio_map = get_budget_ratio(use_case)
    prefer_perf = priority in ("performance", "balanced")
    prefer_aes = priority == "aesthetics" or (priority == "balanced" and scene in ("studio", "gaming_room"))
    
    config = {}
    total = 0.0
    
    for ctype, ratio in ratio_map.items():
        part_budget = budget * ratio
        items = await get_components_by_type(
            db, ctype.value, part_budget,
            prefer_performance=prefer_perf,
            prefer_aesthetics=prefer_aes,
            scene=scene,
            limit=3,
        )
        if items:
            comp, price = items[0]
            config[ctype.value] = {
                "id": comp.id,
                "name": comp.name,
                "brand": comp.brand,
                "model": comp.model,
                "price": round(price, 2),
                "performance_score": comp.performance_score,
                "aesthetics_score": comp.aesthetics_score,
            }
            total += price
    
    return {
        "config": config,
        "total_price": round(total, 2),
        "budget": budget,
        "use_case": use_case,
        "scene": scene,
        "priority": priority,
    }
