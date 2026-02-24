"""API 请求/响应模型"""
from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    budget: int = Field(..., ge=2000, le=100000, description="预算(元)")
    use_case: str = Field(..., description="使用场景: office/gaming/design/development/streaming/light/all_round")
    scene: str | None = Field(None, description="使用场所: home/office/studio/gaming_room/portable")
    priority: str = Field("balanced", description="偏好: performance/cost/aesthetics/balanced")
    weight_performance: float | None = Field(
        None, ge=0, le=100, description="性能权重(0-100)，为空则按优先级自动分配"
    )
    weight_cost: float | None = Field(
        None, ge=0, le=100, description="性价比权重(0-100)，为空则按优先级自动分配"
    )
    weight_aesthetics: float | None = Field(
        None, ge=0, le=100, description="外观权重(0-100)，为空则按优先级自动分配"
    )


class ComponentBrief(BaseModel):
    id: int
    name: str
    brand: str
    model: str
    price: float
    performance_score: float | None
    aesthetics_score: float | None


class RecommendResponse(BaseModel):
    config: dict
    total_price: float
    budget: int
    use_case: str
    scene: str | None
    priority: str
    weight_performance: float | None = None
    weight_cost: float | None = None
    weight_aesthetics: float | None = None


class PriceUpdateRequest(BaseModel):
    component_id: int
    source: str = "manual"
    price: float
    url: str | None = None


class ComponentCreate(BaseModel):
    name: str
    component_type: str
    brand: str
    model: str
    performance_score: float = 50
    aesthetics_score: float = 50
    power_consumption: int = 0
    rgb_support: bool = False
    form_factor: str | None = None
    socket: str | None = None
    chipset: str | None = None
