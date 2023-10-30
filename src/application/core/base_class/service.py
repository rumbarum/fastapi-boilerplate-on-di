from .repository import BaseAlchemyRepository


class BaseService:
    repository: BaseAlchemyRepository

    def __init__(self, repository: BaseAlchemyRepository):
        self.repository = repository
