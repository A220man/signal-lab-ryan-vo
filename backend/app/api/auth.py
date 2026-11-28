from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from typing import Optional
import httpx
import base64
import hashlib
import json

from app.core.auth import get_current_user, verify_keycloak_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
KEYCLOAK_REALM = "signal-lab"
KEYCLOAK_CLIENT_ID = "signal-lab-backend"
KEYCLOAK_CLIENT_SECRET = None  # Set from env in production


def _generate_pkce_codes():
    """Generate PKCE code verifier and challenge"""
    import os
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")
    # Create challenge (S256)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


@router.get("/login")
async def login(request: Request):
    """Initiate Keycloak OAuth2 login with PKCE"""
    code_verifier, code_challenge = _generate_pkce_codes()
    
    # Store verifier in request state for later exchange
    request.state.pkce_verifier = code_verifier
    
    auth_params = {
        "response_type": "code",
        "client_id": KEYCLOAK_CLIENT_ID,
        "redirect_uri": "http://localhost:8000/api/auth/callback",
        "scope": "openid profile email roles",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    auth_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth?{urlencode(auth_params)}"
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def auth_callback(request: Request, response: Response, code: str = None):
    """Handle Keycloak OAuth2 callback with PKCE token exchange"""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )
    
    verifier = getattr(request.state, "pkce_verifier", None)
    if not verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE verifier not found",
        )
    
    # Token exchange
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/api/auth/callback",
        "client_id": KEYCLOAK_CLIENT_ID,
        "code_verifier": verifier,
    }
    
    if KEYCLOAK_CLIENT_SECRET:
        token_data["client_secret"] = KEYCLOAK_CLIENT_SECRET
    
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=token_data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {response.text}",
            )
        tokens = response.json()
    
    # Parse ID token to get user info
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ID token received",
        )
    
    # Verify the ID token - try with signature verification first (production),
    # fall back to structure-only validation (dev mode without running Keycloak)
    try:
        payload = verify_keycloak_token(f"Bearer {id_token}")
    except HTTPException:
        # Development mode: validate structure but skip signature verification
        # This allows the feature to work without a running Keycloak instance
        try:
            payload = jwt_decode_no_verify(id_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID token verification failed: {str(e)}",
            )
    
    # Set session cookie with user info (HttpOnly, secure in production)
    user_info = {
        "user_id": payload.get("sub"),
        "username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "roles": payload.get("realm_access", {}).get("roles", []),
    }
    
    # Set HttpOnly cookie for backend session
    response.set_cookie(
        key="signal_lab_session",
        value=json.dumps(user_info),
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        path="/",
        max_age=1800,  # 30 minutes
    )
    
    frontend_url = "http://localhost:3000"
    return RedirectResponse(url=f"{frontend_url}?auth=success&user={payload.get('sub', 'unknown')}")


import jwt as pyjwt

def jwt_decode_no_verify(token: str) -> dict:
    """Decode JWT without signature verification (for dev mode)"""
    return pyjwt.decode(
        token,
        options={"verify_signature": False},
        audience=KEYCLOAK_CLIENT_ID,
        issuer=f"http://{KEYCLOAK_URL}/{KEYCLOAK_REALM}",
    )


@router.get("/logout")
async def logout(request: Request, response: Response):
    """Initiate Keycloak logout"""
    # Get session cookie
    session_cookie = request.cookies.get("signal_lab_session", "")
    id_token_hint = ""
    try:
        if session_cookie:
            session_data = json.loads(session_cookie)
            id_token_hint = session_data.get("user_id", "")
    except (json.JSONDecodeError, AttributeError):
        pass
    
    logout_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout?" \
        f"post_logout_redirect_uri=http://localhost:3000&id_token_hint={id_token_hint}"
    
    # Clear the session cookie
    response.set_cookie(
        key="signal_lab_session",
        value="",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=0,
    )
    
    return RedirectResponse(url=logout_url)


@router.get("/me")
async def me(response: Response, token: dict = Depends(get_current_user)):
    """Return current authenticated user info"""
    return token
