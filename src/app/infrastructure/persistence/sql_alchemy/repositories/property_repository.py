from app.core.domain.entities.property import Property
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
    to_model,
    to_domain,
)
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)


class PropertyRepository(
    SqlAlchemyRepository[Property, PropertyModel], BaseRepository[Property]
):
    def __init__(self) -> None:
        super().__init__(
            model=PropertyModel,
            to_model=to_model,
            to_domain=to_domain,
        )
