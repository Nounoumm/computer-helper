"""应用配置 - 支持环境变量覆盖"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./pc_config.db"
    
    # AI 大模型推荐扩展配置（预留）
    llm_api_base_url: str | None = None  # 例如: https://your-llm-gateway.example.com
    llm_api_key: str | None = None
    llm_model: str | None = None  # 例如: gpt-4.1 / qwen-2-72b 等
    
    class Config:
        env_file = ".env"


settings = Settings()
