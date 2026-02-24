"""推荐 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RecommendRequest, RecommendResponse
from app.services.recommender import recommend_config

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.post("", response_model=RecommendResponse)
async def get_recommendation(
    req: RecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    return await recommend_config(
        db,
        budget=req.budget,
        use_case=req.use_case,
        scene=req.scene,
        priority=req.priority,
        weight_performance=req.weight_performance,
        weight_cost=req.weight_cost,
        weight_aesthetics=req.weight_aesthetics,
    )
