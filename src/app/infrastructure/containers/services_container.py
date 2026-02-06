from dependency_injector import containers, providers
from app.application.services.auth_service import AuthService
from app.application.services.concept_service import ConceptService
from app.application.services.contract_service import ContractService
from app.application.services.properties_concepts_service import (
    PropertiesConceptsService,
)
from app.application.services.property_service import PropertyService
from app.application.services.transaction_service import TransactionService


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

    auth_service = providers.Factory(
        AuthService,
        repository=repository_container.user_repository,
        entity_name="User",
    )
