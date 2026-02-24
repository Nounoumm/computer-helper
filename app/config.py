"""应用配置 - 支持环境变量覆盖"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./pc_config.db"
    
    # 如后续需要，可在此添加外部服务配置
    
    class Config:
        env_file = ".env"


settings = Settings()
