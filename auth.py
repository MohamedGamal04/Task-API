"""Supabase Auth: the client, and the guard that protects routes.

Supabase is the Identity Provider — it stores the accounts, hashes the
passwords, and signs the tokens. This app never sees a stored password; it only
forwards credentials to Supabase and verifies the tokens it hands back.
"""
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Makes the "Authorize" padlock appear in Swagger UI on every route that
# depends on it. auto_error=False so we can return our own JSON error shape.
bearer_scheme = HTTPBearer(auto_error=False, description="Paste the access_token from /auth/login")


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """The guard. Verifies the bearer token with Supabase and returns the user.

    Used as a FastAPI dependency, so a protected route's body only runs after
    the token checks out — no auth code repeated per route.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    if response is None or response.user is None:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    return response.user
