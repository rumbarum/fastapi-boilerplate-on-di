import pytest
import pytest_asyncio
from application.domain.user.models import User

from application.core.db import standalone_session

from application.server import app

from sqlalchemy import select

from application.domain.auth.service import TokenService
from application.domain.auth.models import Token

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


token_service: TokenService = root_container.auth_container.token_service()

@pytest_asyncio.fixture(scope="function")
async def cleanup_token():
    yield

    @standalone_session
    async def delete_token():
        query = select(Token)
        session = root_container.session()
        result = await session.execute(query)
        token_list = result.scalars().all()
        for token in token_list:
            session().delete(token)

    await delete_token()


@pytest.mark.usefixtures("cleanup_token")
@pytest.mark.asyncio
@standalone_session
async def test_issue_token():
    user_id = 99999
    atk, rtk = await token_service.issue_token(
        user_id=user_id
    )
    query = select(Token).filter(Token.user_id == user_id).order_by(-Token.id)
    result = await root_container.session().execute(query)
    token = result.scalars().first()

    assert token.refresh_token == rtk
    assert token.user_id == user_id


@pytest.mark.usefixtures("cleanup_token")
@pytest.mark.asyncio
async def test_refresh_access_token():
    user_id = 109999
    atk, rtk = await token_service.issue_token(
        user_id=user_id
    )
    refreshed_access_token = await token_service.refresh_access_token(
        refresh_token=rtk
    )
    assert rtk != refreshed_access_token


@pytest.mark.usefixtures("cleanup_token")
@pytest.mark.asyncio
@standalone_session
async def test_revoke_refresh_token():
    user_id = 88888
    atk, rtk = await token_service.issue_token(
        user_id=user_id
    )
    await token_service.revoke_refresh_token(user_id=user_id)

    query = select(Token).filter(Token.user_id == user_id)
    result = await root_container.session().execute(query)
    token = result.scalars().one()
    assert token.is_valid == False

    assert token.refresh_token == rtk
    assert token.user_id == user_id
