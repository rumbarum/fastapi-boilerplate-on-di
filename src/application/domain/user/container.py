from dependency_injector import containers, providers

from .models import User
from .repository import UserRepository
from .service import UserService


class UserContainer(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserRepository, model=User)
    user_service = providers.Factory(UserService, repository=user_repository)
