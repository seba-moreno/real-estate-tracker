from dependency_injector import containers, providers
from app.infrastructure.containers.repositories_container import RepositoryContainer
from app.infrastructure.containers.services_container import ServiceContainer


class RootContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.presentation.api.v1.routes",
            "app.core.security",
        ]
    )

    repositories = providers.Container(
        RepositoryContainer,
    )

    services = providers.Container(
        ServiceContainer,
        repository_container=repositories,
    )
