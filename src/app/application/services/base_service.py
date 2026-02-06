from typing import Generic, TypeVar
from app.infrastructure.logging.logger_with_correlation_id import get_logger
from app.core.exceptions.domain_exceptions import NotFoundError, PersistenceError
from app.core.interfaces.repositories.base_repository import BaseRepository

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(
        self,
        repository: BaseRepository[T],
        entity_name: str,
    ):
        self.repo = repository
        self.logger = get_logger(f"{type(self).__name__}<{entity_name}>")
        self.entity_name = entity_name

    def get_all(self) -> list[T]:
        self._log_get_all_start()
        results = self.repo.get_all()
        self._log_get_all_success(len(results))
        return results

    def get_by_id(self, entity_id: int) -> T:
        self._log_get_by_id_start(entity_id)
        entity = self.repo.get_by_id(entity_id)
        if entity is None:
            self._log_get_by_id_miss(entity_id)
            raise NotFoundError(f"{self.entity_name} {entity_id} not found")
        self._log_get_by_id_success(entity)
        return entity

    def create(self, entity: T) -> T:
        self._log_create_start(entity)
        try:
            created = self.repo.create(entity)
            self._log_create_success(created)
            return created
        except Exception as ex:
            self.logger.exception(f"Create {self.entity_name} operation failed")
            raise PersistenceError(f"Error creating {self.entity_name}") from ex

    def update(self, entity_id: int, entity: T) -> T:
        self._log_update_start(entity_id, entity)
        self.get_by_id(entity_id)
        try:
            updated = self.repo.update(entity_id, entity)
            self._log_update_success(updated)
            return updated
        except Exception as ex:
            self.logger.exception(f"Update {self.entity_name} operation failed")
            raise PersistenceError(f"Error updating {self.entity_name}") from ex

    def delete(self, entity_id: int) -> None:
        self._log_delete_start(entity_id)
        self.get_by_id(entity_id)

        try:
            self.repo.delete(entity_id)
            self._log_delete_success(entity_id)
        except Exception as ex:
            self.logger.exception(f"Delete {self.entity_name} operation failed")
            raise PersistenceError(f"Error deleting {self.entity_name}") from ex

    # Logging hooks
    def _log_get_all_start(self) -> None:
        self.logger.info(f"Fetching all {self.entity_name}")

    def _log_get_all_success(self, result_count: int) -> None:
        self.logger.info(
            f"Fetched all {self.entity_name}", extra={"count": result_count}
        )

    def _log_get_by_id_start(self, entity_id: int) -> None:
        self.logger.info(
            f"Fetching {self.entity_name}",
            extra={"id": entity_id},
        )

    def _log_get_by_id_miss(self, entity_id: int) -> None:
        self.logger.warning(
            f"{self.entity_name} not found",
            extra={"id": entity_id},
        )

    def _log_get_by_id_success(self, entity: T) -> None:
        self.logger.info(
            f"Fetched {self.entity_name}",
            extra={"entity": entity},
        )

    def _log_create_start(self, entity: T) -> None:
        self.logger.info(
            f"Creating {self.entity_name}",
            extra={"entity": entity},
        )

    def _log_create_success(self, entity: T) -> None:
        self.logger.info(
            f"{self.entity_name} created successfully",
            extra={"entity": entity},
        )

    def _log_update_start(self, entity_id: int, entity: T) -> None:
        self.logger.info(
            f"Updating {self.entity_name}",
            extra={"id": entity_id, "update": entity},
        )

    def _log_update_success(self, entity: T) -> None:
        self.logger.info(
            f"{self.entity_name} updated successfully",
            extra={"entity": entity},
        )

    def _log_delete_start(self, entity_id: int) -> None:
        self.logger.info(
            f"Deleting {self.entity_name}",
            extra={"id": entity_id},
        )

    def _log_delete_success(self, entity_id: int) -> None:
        self.logger.info(
            f"{self.entity_name} deleted successfully",
            extra={"id": entity_id},
        )
