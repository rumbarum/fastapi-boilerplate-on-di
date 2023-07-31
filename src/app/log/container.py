from dependency_injector import containers, providers

from .models import RequestResponseLog
from .repository import RequestResponseLogRepository
from .service import DatabaseLoghandler


class LogContainer(containers.DeclarativeContainer):
    token_repository = providers.Factory(
        RequestResponseLogRepository, model=RequestResponseLog
    )
    data_base_log_handler = providers.Factory(
        DatabaseLoghandler, repository=token_repository
    )
