from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.core.domain.entities.auth import JwtToken
from app.core.interfaces.services.auth_service import IAuthService
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.auth_mapper import (
    login_schema_to_domain,
    register_schema_to_domain,
)
from app.presentation.api.v1.schemas.auth import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
@inject
def login(
    credentials: LoginRequest,
    service: IAuthService = Depends(Provide[RootContainer.services.auth_service]),
) -> JwtToken:
    domain_obj = login_schema_to_domain(credentials)
    return service.login(domain_obj)


@router.post("/register", status_code=201)
@inject
def register(
    credentials: RegisterRequest,
    service: IAuthService = Depends(Provide[RootContainer.services.auth_service]),
) -> None:
    domain_obj = register_schema_to_domain(credentials)
    return service.register(domain_obj)
