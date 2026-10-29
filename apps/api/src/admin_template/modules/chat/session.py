import json

_MEMORY: dict[str, list[dict]] = {}


async def load_history(session_id: str) -> list[dict]:
    try:
        import redis.asyncio as redis

        from admin_template.core.settings import settings

        r = redis.from_url(settings.redis_url, decode_responses=True)
        raw = await r.get(f"chat:session:{session_id}")
        await r.aclose()
        if not raw:
            return _MEMORY.get(session_id, [])
        return json.loads(raw)
    except (OSError, ValueError, RuntimeError):
        return _MEMORY.get(session_id, [])


async def save_history(session_id: str, history: list[dict]) -> None:
    _MEMORY[session_id] = history
    try:
        import redis.asyncio as redis

        from admin_template.core.settings import settings

        r = redis.from_url(settings.redis_url, decode_responses=True)
        await r.set(f"chat:session:{session_id}", json.dumps(history), ex=3600)
        await r.aclose()
    except (OSError, RuntimeError):
        pass
