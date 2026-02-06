from sqlalchemy import select
from app.core.domain.entities.user import User
from app.core.interfaces.repositories.user_repository import IUserRepository
from app.infrastructure.persistence.sql_alchemy.mappers.user_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.user_model import UserModel
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)


class UserRepository(SqlAlchemyRepository[User, UserModel], IUserRepository):
    def __init__(self) -> None:
        super().__init__(
            model=UserModel,
            to_model=to_model,
            to_domain=to_domain,
        )

    def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        with self._session() as db:
            result = db.execute(stmt).scalar_one_or_none()
            return to_domain(result) if result else None
