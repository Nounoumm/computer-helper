"""数据库模型"""
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ComponentType(str, enum.Enum):
    CPU = "cpu"
    GPU = "gpu"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"
    COOLER = "cooler"
    MONITOR = "monitor"


class UseCase(str, enum.Enum):
    OFFICE = "office"           # 办公
    GAMING = "gaming"           # 游戏
    DESIGN = "design"           # 设计/创作
    DEVELOPMENT = "development" # 开发
    STREAMING = "streaming"     # 直播
    LIGHT = "light"             # 轻度使用
    ALL_ROUND = "all_round"     # 全能


class SceneType(str, enum.Enum):
    HOME = "home"               # 家用
    OFFICE = "office"           # 办公室
    STUDIO = "studio"           # 工作室
    GAMING_ROOM = "gaming_room" # 电竞房
    PORTABLE = "portable"       # 便携需求


class Component(Base):
    """硬件组件"""
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    component_type: Mapped[str] = mapped_column(String(50), index=True)
    brand: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(100))
    
    # 性能相关
    performance_score: Mapped[float] = mapped_column(Float, default=0)  # 0-100
    power_consumption: Mapped[int] = mapped_column(Integer, default=0)  # 瓦特
    
    # 外观/适用场景
    aesthetics_score: Mapped[float] = mapped_column(Float, default=50)  # 0-100 外观
    rgb_support: Mapped[bool] = mapped_column(default=False)
    form_factor: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ATX/mATX/ITX
    
    # 兼容性
    socket: Mapped[str | None] = mapped_column(String(50), nullable=True)  # CPU插槽
    chipset: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # 元数据
    spec_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    prices: Mapped[list["Price"]] = relationship("Price", back_populates="component", cascade="all, delete-orphan")


class Price(Base):
    """价格记录 - 支持多来源"""
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"), index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)  # jd/taobao/pdd/manual
    price: Mapped[float] = mapped_column(Float)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    component: Mapped["Component"] = relationship("Component", back_populates="prices")


class PresetConfig(Base):
    """预设配置模板"""
    __tablename__ = "preset_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    use_case: Mapped[str] = mapped_column(String(50), index=True)
    budget_min: Mapped[int] = mapped_column(Integer)
    budget_max: Mapped[int] = mapped_column(Integer)
    component_ids_json: Mapped[str] = mapped_column(Text)  # JSON: {cpu: 1, gpu: 2, ...}
    priority: Mapped[str] = mapped_column(String(20), default="balanced")  # performance/cost/aesthetics
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
