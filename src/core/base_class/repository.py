from typing import Any, Generic, Optional, TypeVar

from dependency_injector.wiring import Provide
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session

from core.db import Transactional
from core.enums.repository import SynchronizeSessionEnum

session: async_scoped_session = Provide["session"]


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    model: ModelType

    def __init__(self, model: ModelType):
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        if hasattr(self.model, "id"):
            query = select(self.model.id == id)  # type: ignore[arg-type]
            result = await session.execute(query)
            return result.scalars().first()
        return None

    async def find_by_or_condition(
        self,
        where_condition: dict[str, str | int],
        is_first: bool = False,
    ) -> Any | list[ModelType] | None:
        cond_dict = {}
        for k, v in where_condition.items():
            if not hasattr(self.model, k):
                raise ValueError(f"{self.model} has no {k}")
            cond_dict[getattr(self.model, k)] = v
        query = select(self.model).where(or_(**cond_dict))  # type: ignore[arg-type]
        result = await session.execute(query)
        if is_first:
            return result.scalars().first()
        return result.scalars().all()

    async def find_by_and_condition(
        self,
        where_condition: dict[str, str | int],
        is_first: bool = False,
    ) -> Any | list[ModelType] | None:
        cond_dict = {}
        for k, v in where_condition.items():
            if not hasattr(self.model, k):
                raise ValueError(f"{self.model} has no {k}")
            cond_dict[getattr(self.model, k)] = v
        query = select(self.model).where(and_(**cond_dict))  # type: ignore[arg-type]
        result = await session.execute(query)
        if is_first:
            return result.scalars().first()
        return result.scalars().all()

    @Transactional()
    async def update_by_id(
        self,
        id: int,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        if hasattr(self.model, "id"):
            query = (
                update(self.model)  # type: ignore[arg-type]
                .where(self.model.id == id)
                .values(**params)
                .execution_options(synchronize_session=synchronize_session)
            )
            await session.execute(query)
        else:
            raise ValueError(f"{self.model} HAS NO ID")

    @staticmethod
    @Transactional()
    async def delete(model: ModelType) -> None:
        await session.delete(model)  # type: ignore[arg-type]

    @Transactional()
    async def delete_by_id(
        self,
        id: int,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        if hasattr(self.model, "id"):
            query = (
                delete(self.model)  # type: ignore[arg-type]
                .where(self.model.id == id)
                .execution_options(synchronize_session=synchronize_session)
            )
            await session.execute(query)
        else:
            raise ValueError(f"{self.model} HAS NO ID")

    @staticmethod
    @Transactional()
    async def save(model: ModelType) -> None:
        await session.add(model)  # type: ignore[func-returns-value]
