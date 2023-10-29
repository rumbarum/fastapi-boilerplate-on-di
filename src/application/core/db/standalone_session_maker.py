from uuid import uuid4

from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from .session_maker import reset_session_context, set_session_context

session: async_scoped_session = Provide["session"]


def standalone_session(func):
    async def _standalone_session(*args, **kwargs):
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)

        try:
            result = await func(*args, **kwargs)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.remove()
            reset_session_context(context=context)
        return result

    return _standalone_session
