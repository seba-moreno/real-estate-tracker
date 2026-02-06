from abc import ABC, abstractmethod

from app.core.domain.entities.auth import JwtToken, LoginCredentials, UserCreate


class IAuthService(ABC):
    @abstractmethod
    def login(self, credentials: LoginCredentials) -> JwtToken: ...
    @abstractmethod
    def register(self, user: UserCreate) -> None: ...
