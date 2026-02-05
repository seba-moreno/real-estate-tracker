from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> list[T]: ...
    @abstractmethod
    def get_by_id(self, entity_id: int) -> T | None: ...
    @abstractmethod
    def create(self, entity: T) -> T: ...
    @abstractmethod
    def update(self, entity_id: int, entity: T) -> T: ...
    @abstractmethod
    def delete(self, entity_id: int) -> bool: ...
