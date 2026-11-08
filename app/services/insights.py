"""Insights: the AI service's 30-day backtest, cached for the demo app."""

from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import HTTPException

from app.config import Settings

_cache: dict[str, Any] = {}


def _backtest_url(settings: Settings) -> str:
    base = settings.ai_decision_url.rsplit("/v1/", 1)[0]
    return f"{base}/v1/backtest/month"


async def month_backtest(settings: Settings, refresh: bool = False) -> dict[str, Any]:
    """2,000 synthetic customers, 30 days, mixed cards — same inputs every time, so cache it."""
    if not refresh and "month" in _cache:
        return _cache["month"]
    if settings.use_mock_ai:
        raise HTTPException(status_code=503, detail="Insights need the AI decision service (USE_MOCK_AI=false)")
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(_backtest_url(settings), json={"n": 2000, "seed": 2026})
            response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 — surface a friendly message to the UI
        raise HTTPException(
            status_code=503, detail=f"AI service is waking up — try again in a minute ({exc})"
        ) from exc
    data: Optional[dict[str, Any]] = response.json()
    _cache["month"] = data
    return data
