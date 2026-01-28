from typing import Any, Iterable, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    dto_model: type[T]

    def to_dto(self, orm_obj: Any) -> T:
        dto = self.dto_model.model_validate(orm_obj)
        return dto

    def to_dto_list(self, orm_list: Iterable[Any]) -> list[T]:
        return [self.to_dto(o) for o in orm_list]
