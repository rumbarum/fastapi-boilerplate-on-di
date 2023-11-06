from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from dependency_injector.wiring import Provide
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import selectinload

from application.core.db import standalone_session
from application.core.enums.repository import (
    FilterInOrNot,
    FilterMethod,
    OrderingEnum,
    SynchronizeSessionEnum,
)
from application.core.repository.base import BaseRepository

session: async_scoped_session = Provide["session"]


ModelType = TypeVar("ModelType")
IdType = TypeVar("IdType")
OtherModelType = TypeVar("OtherModelType")


class BaseAlchemyRepository(BaseRepository, Generic[ModelType, IdType]):
    model: type[ModelType]

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, id: IdType) -> Optional[ModelType]:
        query = select(self.model.id == id)  # type: ignore[attr-defined]
        scalar_result = await session.scalars(query)
        return scalar_result.first()

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

    async def update_by_id(
        self,
        id: int,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        if hasattr(self.model, "id"):
            query = (
                update(self.model)  # type: ignore[arg-type]
                .where(self.model.id == id)  # type: ignore[attr-defined]
                .values(**params)
                .execution_options(synchronize_session=synchronize_session)
            )
            await session.execute(query)
        else:
            raise ValueError(f"{self.model} HAS NO ID")

    @staticmethod
    async def delete(model: ModelType) -> None:
        await session.delete(model)  # type: ignore[arg-type]

    async def delete_by_id(
        self,
        id: int,
        synchronize_session: SynchronizeSessionEnum = SynchronizeSessionEnum.FALSE,
    ) -> None:
        if hasattr(self.model, "id"):
            query = (
                delete(self.model)  # type: ignore[arg-type]
                .where(self.model.id == id)  # type: ignore[attr-defined]
                .execution_options(synchronize_session=synchronize_session)
            )
            await session.execute(query)
        else:
            raise ValueError(f"{self.model} HAS NO ID")

    @staticmethod
    def save(model: ModelType) -> None:
        session.add(model)  # type: ignore[func-returns-value]

    @standalone_session
    async def standalone_save(self, model: ModelType | OtherModelType) -> None:
        session.add(model)
        await session.commit()

    async def get_count(
        self, query=None, model: type[ModelType] | type[OtherModelType] | None = None
    ) -> ModelType | OtherModelType | None:
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if query is None:
            result = await session.execute(
                select(func.count()).select_from(select(model).subquery())  # type: ignore[arg-type, attr-defined]
            )
            return result.scalar_one()
        else:
            result = await session.execute(
                select(func.count()).select_from(query.subquery())
            )
            return result.scalar_one()

    def get_paging_query(self, query, page: int, per_page: int):
        """
        Get paging query for paginated, paging require get_ordering_query for correct result
        :param query: query
        :param page: page number
        :param per_page: page size
        :return: query
        """
        query = query.offset((page - 1) * per_page).limit(per_page)
        return query

    def get_timerange_query(
        self,
        time_columns: str,
        start_time: datetime,
        end_time: datetime,
        query=None,
        model: type[ModelType] | type[OtherModelType] | None = None,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if hasattr(model, "timerange_fields"):
            if time_columns not in model.timerange_fields:  # type: ignore[attr-defined, union-attr]
                raise ValueError(f"Time columns {time_columns} not in timerange_fields")
        table_columns = model.__table__.columns  # type: ignore[attr-defined, union-attr]
        if time_columns not in table_columns:
            if query is None:
                raise ValueError(
                    f"func: get_timerange_query got wrong time_columns {time_columns}"
                )
            else:
                return query
        col = getattr(model, time_columns)
        if query is None:
            query = select(model).filter(col.between(start_time, end_time))
        else:
            query = query.filter(col.between(start_time, end_time))

        return query

    def get_ordering_query(
        self,
        order_by: str,
        order: OrderingEnum = OrderingEnum.DESC,
        query=None,
        model: type[ModelType] | type[OtherModelType] | None = None,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if hasattr(model, "ordering_fields"):
            if order_by not in model.ordering_fields:  # type: ignore[attr-defined, union-attr]
                raise ValueError(f"Order by {order_by} not in ordering_fields")
        table_columns = model.__table__.columns  # type: ignore[attr-defined, union-attr]
        if order_by not in table_columns:
            if query is None:
                raise ValueError(
                    f"func: get_ordering_query got wrong order_by {order_by}"
                )
            else:
                return query
        if query is None:
            if order == OrderingEnum.ASC:
                query = select(model).order_by(table_columns[order_by].asc())  # type: ignore[attr-defined, arg-type, name-defined]
            else:
                query = select(model).order_by(table_columns[order_by].desc())  # type: ignore[attr-defined, arg-type, name-defined]
        else:
            if order == OrderingEnum.ASC:
                query = query.order_by(table_columns[order_by].asc())  # type: ignore[attr-defined, arg-type, name-defined]
            else:
                query = query.order_by(table_columns[order_by].desc())  # type: ignore[attr-defined, arg-type, name-defined]
        return query

    def get_search_query(
        self,
        search_column: str,
        search_value: Any,
        query=None,
        model: type[ModelType] | type[OtherModelType] | None = None,
        method: FilterMethod = FilterMethod.MATCH,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if hasattr(model, "search_fields"):
            if search_column not in model.search_fields:  # type: ignore[attr-defined, union-attr]
                raise ValueError(f"Search column {search_column} not in search_fields")
        table_columns = model.__table__.columns  # type: ignore[attr-defined, union-attr]
        if search_column not in table_columns:
            if query is None:
                raise ValueError(
                    f"func: get_search_query got wrong search_column {search_column}"
                )
            else:
                return query

        col = getattr(model, search_column)
        if method == FilterMethod.ILIKE:
            if query is None:
                query = select(model).filter(col.ilike(f"%{search_value}%"))  # type: ignore[attr-defined, arg-type, name-defined]
            else:
                query = query.filter(col.ilike(f"%{search_value}%"))
        elif method == FilterMethod.LIKE:
            if query is None:
                query = select(model).filter(  # type: ignore[attr-defined, arg-type, name-defined]
                    col.like(f"%{search_value}%")
                )  # type: ignore[attr-defined, arg-type, name-defined]
            else:
                query = query.filter(col.like(f"%{search_value}%"))
        else:
            if query is None:
                query = select(model).filter(col == search_value)  # type: ignore[attr-defined, arg-type, name-defined]
            else:
                query = query.filter(col == search_value)  # type: ignore[attr-defined, arg-type, name-defined]
        return query

    def get_in_filter_query(
        self,
        filter_value: list,
        filter_column: str,
        query=None,
        model: type[ModelType] | type[OtherModelType] | None = None,
        method: FilterInOrNot = FilterInOrNot.IN,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if hasattr(model, "filter_fields"):
            if filter_column not in model.filter_fields:  # type: ignore[attr-defined, union-attr]
                raise ValueError(f"Filter column {filter_column} not in filter_fields")
        table_columns = model.__table__.columns  # type: ignore[attr-defined, union-attr]
        if filter_column not in table_columns:
            if query is None:
                raise ValueError(
                    f"func: get_in_filter_query got wrong filter_column {filter_column}"
                )
            else:
                return query
        if not filter_value:
            if query is None:
                raise ValueError(f"func: get_in_filter_query got no filter_value")
            else:
                return query

        col = getattr(model, filter_column)
        if method == FilterInOrNot.IN:
            if query is None:
                query = select(model).filter(col.in_(filter_value))
            else:
                query = query.filter(col.in_(filter_value))
        else:
            if query is None:
                query = select(model).filter(col.notin_(filter_value))
            else:
                query = query.filter(col.notin_(filter_value))
        return query

    async def get_query_execute(self, query):
        result = await session.scalars(query)
        return result.all()

    async def get_first_query_execute(self, query):
        result = await session.scalars(query)
        return result.first()

    async def get_yield_per(self, query, per_value: int = 1000):
        result = await session.execute(query)
        return result.yield_per(per_value)

    async def get_query_execute_no_scalar(self, query):
        """Group by 혹은 'get_partial_column_query'을 할 경우에는
        `get_query_execute` 대신 이 함수로 query 실행하세요.
        scalar()를 하면 1번째 칼럼 데이터만 나옵니다.
        """
        result = await session.execute(query)
        return result

    def get_partial_column_query(
        self,
        select_columns: list[str],
        model: type[ModelType] | type[OtherModelType] | None = None,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        if not select_columns:
            return select(model)
        else:
            return select(model).with_only_columns(
                [getattr(model, column) for column in select_columns]
            )

    async def save_model_from_data(
        self, data, model: type[ModelType] | type[OtherModelType] | None = None
    ) -> None:
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        instance = model(**data)
        await self.standalone_save(instance)

    def get_selectinload_query(
        self,
        query,
        selectinload_column: str,
        model: type[ModelType] | type[OtherModelType] | None = None,
    ):
        if model is None:
            if self.model is not None:
                model = self.model
            else:
                raise ValueError(f"{self.__class__.__name__} has no model")
        table_columns = model.__table__.columns  # type: ignore[attr-defined, union-attr]
        if selectinload_column not in table_columns:
            raise ValueError(
                f"selectinload_column: {selectinload_column} not in table_columns"
            )
        if query is None:
            query = select(model).options(
                selectinload(table_columns[selectinload_column])
            )
        else:
            query = query.options(selectinload(table_columns[selectinload_column]))
        return query
