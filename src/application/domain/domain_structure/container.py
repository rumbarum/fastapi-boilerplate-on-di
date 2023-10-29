from dependency_injector import containers, providers

from .models import YourModel
from .repository import YourRepository
from .service import YourService


# register below to core.domain.container.AppContainer
class YourDomainContainer(containers.DeclarativeContainer):

    your_repository = providers.Factory(YourRepository, YourModel)
    your_service = providers.Factory(YourService, your_repository)
