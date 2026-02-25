"""主应用"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import init_db
from app.routers import recommend, recommend_ai, components

app = FastAPI(
    title="PC 配置推荐系统",
    description="根据预算和场景智能推荐电脑硬件配置，支持实时价格同步",
)

app.include_router(recommend.router)
app.include_router(recommend_ai.router)
app.include_router(components.router)

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def index():
    p = Path(__file__).parent.parent / "static" / "index.html"
    if p.exists():
        return FileResponse(p)
    return {"message": "PC Config Recommender API", "docs": "/docs"}
