from typing import Any, Generic, Optional, Type, TypeVar

from dependency_injector.wiring import Provide
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session

from core.db import Transactional
from core.enums.repository import SynchronizeSessionEnum

session: async_scoped_session = Provide["session"]


ModelType = TypeVar("ModelType")


class BaseRepo(Generic[ModelType]):
    Model: Type[ModelType]

    @classmethod
    async def get_by_id(cls, id: int) -> Optional[ModelType]:
        if hasattr(cls.Model, "id"):
            query = select(cls.Model.id == id)  # type: ignore[arg-type]
            result = await session.execute(query)
            return result.scalars().first()
        return None

    @classmethod
    async def find_by_or_condition(
        cls,
        where_condition: dict[str, str | int],
        is_first: bool = False,
    ) -> Any | list[ModelType] | None:
        cond_dict = {}
        for k, v in where_condition.items():
            if not hasattr(cls.Model, k):
                raise ValueError(f"{cls.Model} has no {k}")
            cond_dict[getattr(cls.Model, k)] = v
        query = select(cls.Model).where(or_(**cond_dict))  # type: ignore[arg-type]
        result = await session.execute(query)
        if is_first:
            return result.scalars().first()
        return result.scalars().all()

    @classmethod
    async def find_by_and_condition(
        cls,
        where_condition: dict[str, str | int],
        is_first: bool = False,
    ) -> Any | list[ModelType] | None:
        cond_dict = {}
        for k, v in where_condition.items():
            if not hasattr(cls.Model, k):
                raise ValueError(f"{cls.Model} has no {k}")
            cond_dict[getattr(cls.Model, k)] = v
        query = select(cls.Model).where(and_(**cond_dict))  # type: ignore[arg-type]
        result = await session.execute(query)
        if is_first:
            return result.scalars().first()
        return result.scalars().all()

    @classmethod
    @Transactional()
    async def update_by_id(
        cls,
        id: int,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        query = (
            update(cls.Model)  # type: ignore[arg-type]
            .where(cls.Model.id == id)
            .values(**params)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)

    @staticmethod
    @Transactional()
    async def delete(model: ModelType) -> None:
        await session.delete(model)  # type: ignore[arg-type]

    @classmethod
    @Transactional()
    async def delete_by_id(
        cls,
        id: int,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        query = (
            delete(cls.Model)  # type: ignore[arg-type]
            .where(cls.Model.id == id)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)

    @staticmethod
    @Transactional()
    async def save(model: ModelType) -> None:
        await session.add(model)  # type: ignore[func-returns-value]
