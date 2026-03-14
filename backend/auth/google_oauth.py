import httpx
from fastapi import HTTPException

async def verify_google_token(token: str) -> dict:
    """Verifies a Google OAuth token and returns user info"""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google Token")
            return res.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to verify Google Token")
