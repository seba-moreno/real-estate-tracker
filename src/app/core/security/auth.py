import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dependency_injector.wiring import inject, Provide
from app.core.interfaces.repositories.user_repository import IUserRepository
from app.core.security.jwt import JWT_ALGORITHM, JWT_SECRET
from app.infrastructure.containers.root_container import RootContainer


bearer = HTTPBearer(auto_error=True)


@inject  # type: ignore[misc]
def auth_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    repo: IUserRepository = Depends(
        Provide[RootContainer.repositories.user_repository]
    ),
) -> str:
    token = credentials.credentials
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = claims.get("sub")
        if not isinstance(username, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = repo.get_by_username(username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User disabled or not found",
        )

    return username
