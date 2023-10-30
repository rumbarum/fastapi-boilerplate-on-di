from dependency_injector import containers, providers

from .models import User
from .repository import UserAlchemyRepository
from .service import UserService


class UserContainer(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserAlchemyRepository, model=User)
    user_service = providers.Factory(UserService, repository=user_repository)
