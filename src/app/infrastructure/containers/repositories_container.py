from dependency_injector import containers, providers
from app.infrastructure.persistence.sql_alchemy.repositories.concept_repository import (
    ConceptRepository,
)
from app.infrastructure.persistence.sql_alchemy.repositories.contract_repository import (
    ContractRepository,
)
from app.infrastructure.persistence.sql_alchemy.repositories.properties_concepts_repository import (
    PropertiesConceptsRepository,
)
from app.infrastructure.persistence.sql_alchemy.repositories.property_repository import (
    PropertyRepository,
)
from app.infrastructure.persistence.sql_alchemy.repositories.transaction_repository import (
    TransactionRepository,
)
from app.infrastructure.persistence.sql_alchemy.repositories.user_repository import (
    UserRepository,
)


class RepositoryContainer(containers.DeclarativeContainer):
    concept_repository = providers.Factory(
        ConceptRepository,
    )

    contract_repository = providers.Factory(
        ContractRepository,
    )

    properties_concepts_repository = providers.Factory(
        PropertiesConceptsRepository,
    )

    property_repository = providers.Factory(
        PropertyRepository,
    )

    transaction_repository = providers.Factory(
        TransactionRepository,
    )

    user_repository = providers.Factory(
        UserRepository,
    )
