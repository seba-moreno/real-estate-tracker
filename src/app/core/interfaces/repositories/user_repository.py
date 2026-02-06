from abc import ABC, abstractmethod
from app.core.domain.entities.user import User
from app.core.interfaces.repositories.base_repository import BaseRepository


class IUserRepository(BaseRepository[User], ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...
