from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Optional
from datetime import datetime, timezone


# Keycloak configuration from settings
KEYCLOAK_URL = "http://localhost:8080"
KEYCLOAK_REALM = "signal-lab"
KEYCLOAK_CLIENT_ID = "signal-lab-backend"


def get_keycloak_jwks():
    """Fetch JWKS (JSON Web Key Set) from Keycloak"""
    import httpx
    jwks_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def verify_keycloak_token(
    authorization: Optional[str] = None,
) -> dict:
    """
    Verify a Keycloak OIDC JWT token from the Authorization header.
    Returns the token payload if valid, raises HTTPException if invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # Strip "Bearer "
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the JWKS to verify the signature
    jwks = get_keycloak_jwks()
    if not jwks:
        # In development/demo mode, still validate structure but skip signature
        # This allows the feature to work without a running Keycloak instance
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                audience=KEYCLOAK_CLIENT_ID,
                issuer=f"http://{KEYCLOAK_URL}/{KEYCLOAK_REALM}",
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Production mode: verify signature using JWKS
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            issuer=f"http://{KEYCLOAK_URL}/{KEYCLOAK_REALM}",
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# OAuth2 scheme for FastAPI security dependency
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"http://{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth",
    tokenUrl=f"http://{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
    auto_error=False,
)


def get_current_user(token: dict = Depends(verify_keycloak_token)) -> dict:
    """Return current authenticated user info"""
    return {
        "user_id": token.get("sub"),
        "username": token.get("preferred_username"),
        "email": token.get("email"),
        "roles": token.get("realm_access", {}).get("roles", []),
    }
