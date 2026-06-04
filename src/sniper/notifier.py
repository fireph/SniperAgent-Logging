import httpx

SEVERITY_PRIORITY = {
    "info": 1,
    "low": 3,
    "medium": 5,
    "high": 8,
    "urgent": 10,
}


async def send_gotify(
    url: str, token: str, title: str, message: str, priority: int
) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{url.rstrip('/')}/message",
                params={"token": token},
                json={"title": title, "message": message, "priority": priority},
                timeout=10,
            )
            return resp.status_code == 200
    except httpx.HTTPError:
        return False
