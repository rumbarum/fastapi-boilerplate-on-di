from contextvars import ContextVar, Token

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Delete, Insert, Update

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


class RoutingSession(Session):
    @inject
    def get_bind(
        self,
        mapper=None,
        clause=None,
        writer_engine=Provide["writer_engine"],
        reader_engine=Provide["reader_engine"],
        **kw,
    ):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):  # type: ignore[attr-defined]
            return writer_engine.sync_engine
        else:
            return reader_engine.sync_engine


Base = declarative_base()
