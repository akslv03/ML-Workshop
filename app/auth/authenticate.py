from fastapi import Depends, HTTPException, status
from auth.jwt_handler import verify_access_token
from services.auth.cookieauth import OAuth2PasswordBearerWithCookie

oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/token")

async def authenticate_cookie(token: str = Depends(oauth2_scheme_cookie)) -> str:
    """
    Достает JWT из cookie, проверяет его и возвращает идентификатор пользователя (email).
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access",
        )
    decoded_token = verify_access_token(token)
    return decoded_token["user"]