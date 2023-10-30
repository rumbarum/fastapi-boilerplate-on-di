from application.core.base_class.service import BaseService

from .repository import YourAlchemyRepository


class YourService(BaseService):
    repository: YourAlchemyRepository

    def __init__(self, repository):
        super().__init__(repository)
