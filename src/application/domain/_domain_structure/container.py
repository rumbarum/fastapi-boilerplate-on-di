from dependency_injector import containers, providers

from .models import YourModel
from .repository import YourAlchemyRepository
from .service import YourService


# register below to core.domain.config.AppContainer
class YourDomainContainer(containers.DeclarativeContainer):

    your_repository = providers.Factory(YourAlchemyRepository, YourModel)
    your_service = providers.Factory(YourService, your_repository)
