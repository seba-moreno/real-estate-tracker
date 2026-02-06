from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.core.domain.entities.auth import JwtToken, LoginCredentials, UserCreate
from app.core.domain.entities.user import User
from app.core.exceptions.domain_exceptions import PersistenceError, ValidationError
from app.core.interfaces.repositories.user_repository import IUserRepository
from app.core.interfaces.services.auth_service import IAuthService
from app.core.security.password import verify_password, hash_password
from app.core.security.jwt import JWT_EXPIRE_MIN, create_access_token
from app.infrastructure.logging.logger_with_correlation_id import get_logger


class AuthService(IAuthService):
    repo: IUserRepository

    def __init__(self, repository: IUserRepository, entity_name: str) -> None:
        self.repo = repository
        self.entity_name = entity_name
        self.logger = get_logger(type(self).__name__)

    def login(self, credentials: LoginCredentials) -> JwtToken:
        self.logger
        user = self.repo.get_by_username(credentials.username)

        if not user:
            self.logger.warning(
                "Login attempt failed for username",
                extra={"username": credentials.username},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not verify_password(credentials.password, user.password_hash):
            self.logger.warning(
                "Login attempt failed for username",
                extra={"username": credentials.username},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_active:
            self.logger.warning(
                "Login attempt failed for username: user is inactive",
                extra={"username": credentials.username},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive"
            )

        token = create_access_token(sub=user.username)

        return JwtToken(
            access_token=token,
            token_type="Bearer",
            expires_in=int(
                (
                    datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MIN)
                ).timestamp()
            ),
        )

    def register(self, user: UserCreate) -> None:
        try:
            existent_user = self.repo.get_by_username(user.username)
            if existent_user:
                self.logger.warning(
                    "Register user attempt failed: username already exists",
                    extra={"username": user.username},
                )
                raise ValidationError(
                    "Register user attempt failed: the provided Username is already on use"
                )

            hashed = hash_password(user.password)

            db_user = User(
                id=None,
                username=user.username,
                email=user.email,
                password_hash=hashed,
                is_active=user.is_active,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            self.logger.info("Registering user", extra={"username": user.username})
            self.repo.create(db_user)
            self.logger.info(
                "User registered successfully", extra={"username": user.username}
            )
        except Exception as ex:
            self.logger.exception("Register user operation failed")
            raise PersistenceError("Error registering user") from ex
