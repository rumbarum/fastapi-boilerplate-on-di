from dependency_injector import containers, providers

from .models import Token
from .repository import TokenAlchemyRepository
from .service import TokenService


class AuthContainer(containers.DeclarativeContainer):
    token_repository = providers.Factory(TokenAlchemyRepository, model=Token)
    token_service = providers.Factory(TokenService, repository=token_repository)
