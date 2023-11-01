from core.base_class.repository import BaseRepository

from .models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, model):
        super().__init__(model)
