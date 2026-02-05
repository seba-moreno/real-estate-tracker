from dependency_injector import containers, providers
from app.infrastructure.services.concept_service import ConceptService
from app.infrastructure.services.contract_service import ContractService
from app.infrastructure.services.properties_concepts_service import (
    PropertiesConceptsService,
)
from app.infrastructure.services.property_service import PropertyService
from app.infrastructure.services.transaction_service import TransactionService


class ServiceContainer(containers.DeclarativeContainer):
    repository_container = providers.DependenciesContainer()

    concept_service = providers.Factory(
        ConceptService,
        repository=repository_container.concept_repository,
        entity_name="Concept",
    )

    contract_service = providers.Factory(
        ContractService,
        repository=repository_container.contract_repository,
        entity_name="Contract",
    )

    properties_concepts_service = providers.Factory(
        PropertiesConceptsService,
        repository=repository_container.properties_concepts_repository,
        entity_name="PropertiesConcepts",
    )

    property_service = providers.Factory(
        PropertyService,
        repository=repository_container.property_repository,
        entity_name="Property",
    )

    transaction_service = providers.Factory(
        TransactionService,
        repository=repository_container.transaction_repository,
        entity_name="Transaction",
    )
