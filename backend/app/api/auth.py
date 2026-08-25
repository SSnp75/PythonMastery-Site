"""Authentication routes — GitHub OAuth2 login."""
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/github")
async def github_login():
    """Redirect to GitHub OAuth2 authorization."""
    # TODO: redirect to GitHub authorize URL
    return {"redirect_url": "https://github.com/login/oauth/authorize?client_id=..."}


@router.get("/github/callback")
async def github_callback(code: str):
    """Exchange GitHub code for access token, create/find user, return JWT."""
    # TODO: exchange code → token → get user info → issue JWT
    return {"access_token": "...", "token_type": "bearer"}


@router.get("/me")
async def get_current_user():
    """Get the authenticated user's profile."""
    # TODO: decode JWT, return user
    return {"id": 1, "username": "alice", "reputation": 42}
