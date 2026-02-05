from typing import Callable, Generic, Optional, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.interfaces.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.sql_alchemy.database import SessionLocal

DomainT = TypeVar("DomainT")
ModelT = TypeVar("ModelT")


class SqlAlchemyRepository(BaseRepository[DomainT], Generic[DomainT, ModelT]):
    def __init__(
        self,
        model: Type[ModelT],
        to_model: Callable[[DomainT], ModelT],
        to_domain: Callable[[ModelT], DomainT],
    ) -> None:
        self.model = model
        self._to_model = to_model
        self._to_domain = to_domain

    def _session(self) -> Session:
        return SessionLocal()

    def get_all(self) -> list[DomainT]:
        with self._session() as db:
            results = db.query(self.model).all()
            return [self._to_domain(row) for row in results]

    def get_by_id(self, entity_id: int) -> Optional[DomainT]:
        with self._session() as db:
            db_obj = db.get(self.model, entity_id)
            return self._to_domain(db_obj) if db_obj else None

    def create(self, entity: DomainT) -> DomainT:
        with self._session() as db:
            db_obj = self._to_model(entity)
            db.add(db_obj)
            try:
                db.commit()
                db.refresh(db_obj)
                return self._to_domain(db_obj)
            except SQLAlchemyError as ex:
                db.rollback()
                raise ex

    def update(self, entity_id: int, entity: DomainT) -> DomainT:
        with self._session() as db:
            if db.get(self.model, entity_id) is None:
                raise ValueError(f"{self.model.__name__} with id={entity_id} not found")

            new_obj = self._to_model(entity)
            setattr(new_obj, "id", entity_id)

            merged = db.merge(new_obj)
            try:
                db.commit()
                db.refresh(merged)
                return self._to_domain(merged)
            except SQLAlchemyError as ex:
                db.rollback()
                raise ex

    def delete(self, entity_id: int) -> bool:
        with self._session() as db:
            db_obj = db.get(self.model, entity_id)
            if db_obj is None:
                return False
            db.delete(db_obj)
            try:
                db.commit()
                return True
            except SQLAlchemyError as ex:
                db.rollback()
                raise ex
