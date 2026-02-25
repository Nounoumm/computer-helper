"""基于 AI 大模型的推荐扩展

设计思路：
- 先用现有规则引擎生成一个「基础配置」（保证即使 AI 不可用也有结果）
- 将用户输入 + 基础配置打包发给 LLM 网关（由你自己实现、对接任意大模型）
- 如果网关返回了新的 config，则用其覆盖/增强基础配置；否则回退到基础配置
"""
from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.recommender import recommend_config
from app.services.llm_client import call_llm_recommend


async def recommend_with_llm(
    db: AsyncSession,
    *,
    budget: int,
    use_case: str,
    scene: str | None = None,
    priority: str = "balanced",
    weight_performance: float | None = None,
    weight_cost: float | None = None,
    weight_aesthetics: float | None = None,
) -> Dict[str, Any]:
    """对外暴露的 AI 推荐入口。

    返回结构与原 RecommendResponse 基本一致，只是多了一个 "from_llm" 标记。
    """
    # 1. 先用规则引擎得到基础推荐
    base = await recommend_config(
        db,
        budget=budget,
        use_case=use_case,
        scene=scene,
        priority=priority,
        weight_performance=weight_performance,
        weight_cost=weight_cost,
        weight_aesthetics=weight_aesthetics,
    )

    # 2. 构造发给 LLM 网关的 payload
    payload = {
        "input": {
            "budget": budget,
            "use_case": use_case,
            "scene": scene,
            "priority": priority,
            "weight_performance": weight_performance,
            "weight_cost": weight_cost,
            "weight_aesthetics": weight_aesthetics,
        },
        "base_recommendation": base,
    }

    # 3. 调用 LLM 网关（如果未配置，会返回 None）
    llm_result = await call_llm_recommend(payload)

    if not llm_result:
        # 未接入 LLM 或调用失败，直接返回基础推荐
        base["from_llm"] = False
        return base

    # 4. 网关可选返回新的 config，我们按结构做一个覆盖/合并
    new_config = llm_result.get("config")
    if isinstance(new_config, dict) and new_config:
        merged = dict(base)
        merged["config"] = new_config
        merged["from_llm"] = True
        merged["llm_metadata"] = llm_result.get("metadata")
        return merged

    base["from_llm"] = False
    base["llm_metadata"] = llm_result.get("metadata")
    return base

