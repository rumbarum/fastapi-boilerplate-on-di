from .repository import BaseRepository


class BaseService:
    repository: BaseRepository

    def __init__(self, repository: BaseRepository):
        self.repository = repository
