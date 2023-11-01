import pytest_asyncio
from application.domain.user.models import User

from application.core import standalone_session

from application.server import app

from sqlalchemy import select

root_container = app.container

user_info = {
    "email": "this@mail.com",
    "password1": "password1",
    "password2": "password1",
    "nickname": "name_nik",
}


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup():
    @standalone_session
    async def create_user():
        await root_container.user_container.user_service().create_user(**user_info)
        return

    await create_user()

    yield

    @standalone_session
    async def delete_user():
        query = select(User).filter(User.email == user_info["email"])
        result = await root_container.session().execute(query)
        user = result.scalars().one()
        await root_container.session().delete(user)

    await delete_user()


@standalone_session
async def test_():
    q = select(User)
    result = await root_container.session().execute(q)
    assert result.scalars().first().email == user_info["email"]
