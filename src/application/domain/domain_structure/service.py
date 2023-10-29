from application.core.base_class.service import BaseService

from .repository import YourRepository


class YourService(BaseService):
    repository: YourRepository

    def __init__(self, repository):
        super().__init__(repository)
