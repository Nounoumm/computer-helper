"""LLM 客户端封装 - 预留对接任意大模型服务的空间

当前实现：
- 如果未配置 llm_api_base_url / llm_api_key，则直接返回 None，不影响原有逻辑
- 如果已配置，则向 {llm_api_base_url}/recommend 发送一个 POST 请求
  请求体中会包含用户输入和基础推荐结果，方便你在网关服务里接入任意大模型
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.config import settings


async def call_llm_recommend(
    payload: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """调用外部 LLM 网关，期望返回一个可选的推荐配置。

    约定：
    - 网关地址: {llm_api_base_url}/recommend
    - Header: Authorization: Bearer {llm_api_key} （可按需在你自己的服务里解析）
    - 请求体: JSON，payload 结构由本服务构造（见 ai_recommender）
    - 返回体示例:
      {
        "config": { ... 可选，结构与后端 recommend_config 返回的 config 一致 ... },
        "metadata": { ... 其他信息，可忽略 ... }
      }
    """
    if not settings.llm_api_base_url or not settings.llm_api_key:
        # 未配置网关时，直接跳过 AI 推荐
        return None

    url = settings.llm_api_base_url.rstrip("/") + "/recommend"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "X-Model": settings.llm_model or "",
                    "Content-Type": "application/json",
                },
            )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        # 为了不中断主流程，这里静默失败，调用方自行决定如何降级
        return None

