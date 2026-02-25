"""AI 大模型推荐 API

路径：/api/recommend/ai
- 行为：与 /api/recommend 类似，但会尝试调用外部 LLM 网关对推荐结果进行优化
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import RecommendRequest, RecommendResponse
from app.services.ai_recommender import recommend_with_llm


router = APIRouter(prefix="/api/recommend", tags=["recommend-ai"])


@router.post("/ai", response_model=RecommendResponse)
async def get_ai_recommendation(
    req: RecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    return await recommend_with_llm(
        db,
        budget=req.budget,
        use_case=req.use_case,
        scene=req.scene,
        priority=req.priority,
        weight_performance=req.weight_performance,
        weight_cost=req.weight_cost,
        weight_aesthetics=req.weight_aesthetics,
    )

