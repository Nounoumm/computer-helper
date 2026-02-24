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


def _resolve_weights(
    priority: str,
    scene: str | None,
    weight_performance: float | None,
    weight_cost: float | None,
    weight_aesthetics: float | None,
) -> tuple[float, float, float]:
    """
    根据优先级和用户自定义权重，计算归一化后的(性能, 性价比, 外观)权重。
    """
    if weight_performance is None and weight_cost is None and weight_aesthetics is None:
        # 未传自定义权重时，根据优先级给出默认比例（总和约等于 1）
        if priority == "performance":
            wp, wc, wa = 0.6, 0.25, 0.15
        elif priority == "cost":
            wp, wc, wa = 0.3, 0.55, 0.15
        elif priority == "aesthetics":
            wp, wc, wa = 0.25, 0.15, 0.6
        else:  # balanced
            wp, wc, wa = 0.45, 0.35, 0.2
            if scene in ("studio", "gaming_room"):
                # 在工作室/电竞房场景下，均衡模式稍微抬高外观权重
                wp, wc, wa = 0.4, 0.3, 0.3
    else:
        # 使用用户传入的 0-100 数值
        wp = float(weight_performance or 0.0)
        wc = float(weight_cost or 0.0)
        wa = float(weight_aesthetics or 0.0)

    total = wp + wc + wa
    if total <= 0:
        # 兜底：防止全为 0
        return 0.45, 0.35, 0.2
    return wp / total, wc / total, wa / total


async def get_components_by_type(
    db: AsyncSession,
    component_type: str,
    budget: float,
    w_perf: float,
    w_cost: float,
    w_aes: float,
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
    weight_performance: float | None = None,
    weight_cost: float | None = None,
    weight_aesthetics: float | None = None,
) -> dict:
    """
    生成推荐配置
    priority: performance 偏性能, cost 偏性价比, aesthetics 偏外观
    """
    ratio_map = get_budget_ratio(use_case)
    w_perf, w_cost, w_aes = _resolve_weights(
        priority=priority,
        scene=scene,
        weight_performance=weight_performance,
        weight_cost=weight_cost,
        weight_aesthetics=weight_aesthetics,
    )
    
    config = {}
    total = 0.0
    
    for ctype, ratio in ratio_map.items():
        part_budget = budget * ratio
        items = await get_components_by_type(
            db, ctype.value, part_budget,
            w_perf=w_perf,
            w_cost=w_cost,
            w_aes=w_aes,
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
        "weight_performance": round(w_perf, 3),
        "weight_cost": round(w_cost, 3),
        "weight_aesthetics": round(w_aes, 3),
    }
