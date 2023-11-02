# FastAPI Boilerplate

Source is from [Teamhide's fastapi-boilerplate](https://github.com/teamhide/fastapi-boilerplate)

# Base Features
- Async SQLAlchemy session
- Custom user class
- Dependencies for specific permissions
- Celery
- Dockerize(Hot reload)
- Cache

# Added Features

- Code dependencies are managed by [Dependency Injector](https://python-dependency-injector.ets-labs.org/) under `src/application/container.py`
- All projects settings are injected by `.env` file thorough pydantic Settings. (refer `src/application/core/config/settings_model.py`)
- More simplified skeleton
  - separate src(fastapi app related code) and others(docker, tests)
  - [Netflix dispatcher style domain component](https://github.com/Netflix/dispatch)
- Static type check(by mypy) is done.
- Log router for request and response logging (`src/application/core/fastapi/log_router.py`) can log Internal Server Error 
- makefile (for easier development)
- Separate poetry dependency group into 2, one is for production, other is for develop
- Aiohttp client for request external service (`src/application/core/external_service/http_client`)
- Authentication middleware for external auth server (`src/application/core/middlewares/authentication_external`)
- Classified Exception Class (`src/application/core/exceptions`)
- Json Encoder Extended CustomORJSONResponse for faster serialization(`src/application/core/fastapi/custom_json_response.py`)
- Async test samples on pytest-asyncio with samples 

# Project Config
make .env.local file by
```
touch .env.local
```
and fill out it with below.

```shell
TITLE='FastAPI APP'
DESCRIPTION='This is Local'
VERSION='0.1.0'
ENV='dev'
DEBUG=True
APP_HOST='0.0.0.0'
APP_PORT=8000
APP_DOMAIN='127.0.0.1'
WRITER_DB_URL='postgresql+asyncpg://postgres:fastapi@127.0.0.1:5432/fastapi'
READER_DB_URL='postgresql+asyncpg://postgres:fastapi@127.0.0.1:5432/fastapi'
JWT_SECRET_KEY='fastapi'
JWT_ALGORITHM='HS256'
SENTRY_SDN=None
CELERY_BROKER_URL='amqp://user:bitnami@localhost:5672/'
CELERY_BACKEND_URL='redis://:password123@localhost:6379/0'
REDIS_HOST='localhost'
REDIS_PORT=6379

CLIENT_TIME_OUT=5
SIZE_POOL_AIOHTTP=100

AUTH_BASE_URL='http://ext-auth-url.com'
AUTH_CLIENT_ID='client'
AUTH_CLIENT_SECRET='secret'
AUTH_REFRESH_TOKEN_KEY='auth_related_value'
AUTH_SCOPE='write,read'

ALLOW_ORIGINS='*'
ALLOW_CREDENTIALS=True
ALLOW_METHODS='*'
ALLOW_HEADERS='*'
```

## Run

```python
python3 main.py --env local|dev|prod --debug
```
or
```shell
$ make run
```

## SQLAlchemy for asyncio context

```python
from application.core.db import Transactional
from dependency_injector.wiring import Provide

session = Provide["session"]

@Transactional()
async def create_user(self):
  session.add(User(email="padocon@naver.com"))
```

Do not use explicit `commit()`. `Transactional` class automatically do.

### Standalone session

According to the current settings, the session is set through middleware.

However, it doesn't go through middleware in tests or background tasks.

So you need to use the `@standalone_session` decorator.

```python
from application.core.db import standalone_session


@standalone_session
def test_something():
  ...
```

### Multiple databases

Go to `core/config.py` and edit `WRITER_DB_URL` and `READER_DB_URL` in the config class.


If you need additional logic to use the database, refer to the `get_bind()` method of `RoutingClass`.

## Custom user for authentication

```python
from fastapi import Request


@home_router.get("/")
def home(request: Request):
    return request.user.id
```

**Note. you have to pass jwt token via header like `Authorization: Bearer 1234`**

Custom user class automatically decodes header token and store user information into `request.user`

If you want to modify custom user class, you have to update below files.

1. `core/fastapi/schemas/current_user.py`
2. `core/fastapi/middlewares/authentication.py`

### CurrentUser

```python
class CurrentUser(BaseModel):
    id: int = Field(None, description="ID")
```

Simply add more fields based on your needs.

### AuthBackend

```python
current_user = CurrentUser()
```

After line 18, assign values that you added on `CurrentUser`.

## Top-level dependency

**Note. Available from version 0.62 or higher.**

Set a callable function when initialize FastAPI() app through `dependencies` argument.

Refer `Logging` class inside of `core/fastapi/dependencies/logging.py` 

## Dependencies for specific permissions

Permissions `IsAdmin`, `IsAuthenticated`, `AllowAll` have already been implemented.

```python
from application.core.fastapi.dependencies import (
  PermissionDependency,
)
from application.core.authority.permissions import IsAdmin

user_router = APIRouter()


@user_router.get(
  "",
  response_model=List[GetUserListResponseSchema],
  response_model_exclude={"id"},
  responses={"400": {"model": ExceptionResponseSchema}},
  dependencies=[Depends(PermissionDependency([IsAdmin]))],  # HERE
)
async def get_user_list(
        limit: int = Query(10, description="Limit"),
        prev: int = Query(None, description="Prev ID"),
):
  pass
```
Insert permission through `dependencies` argument.

If you want to make your own permission, inherit `BasePermission` and implement `has_permission()` function.

**Note. In order to use swagger's authorize function, you must put `PermissionDependency` as an argument of `dependencies`.**

## Event dispatcher

Refer the README of https://github.com/teamhide/fastapi-event

## Cache

### Caching by prefix

```python
from application.core.helpers.cache import cached


@cached(prefix="get_user", ttl=60)
async def get_user():
  ...
```

### Caching by tag

```python
from application.core.helpers.cache import cached, CacheTag


@cached(tag=CacheTag.GET_USER_LIST, ttl=60)
async def get_user():
  ...
```

Use the `cached` decorator to cache the return value of a function.

Depending on the argument of the function, caching is stored with a different value through internal processing.

### Custom Key builder

```python
from application.core.helpers.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
  async def make(self, function: Callable, prefix: str) -> str:
    ...
```

If you want to create a custom key, inherit the BaseKeyMaker class and implement the make() method.

### Custom Backend

```python
from application.core.helpers.cache.base import BaseBackend


class RedisBackend(BaseBackend):
  async def get(self, key: str) -> Any:
    ...

  async def set(self, response: Any, key: str, ttl: int = 60) -> None:
    ...

  async def delete_startswith(self, value: str) -> None:
    ...
```

If you want to create a custom key, inherit the BaseBackend class and implement the `get()`, `set()`, `delete_startswith()` method.

Set your custom backend or keymaker on   (`src/core/container/app.py`)

```python
# core/config/domain.py
...
# this change applied to cache manager automatically 
redis_backend = providers.Factory(YourRedisBackend)
redis_key_maker = providers.Factory(YourKeyMaker)
```

### Remove all cache by prefix/tag

```python
from application.core.helpers.cache import CacheTag

from dependency_injector.wiring import Provide

# You can get App's global obj from Provide["name"] by Dependency Injector 
cache_manager = Provide["cache_manager"]

await cache_manager.remove_by_prefix(prefix="get_user_list")
await cache_manager.remove_by_tag(tag=CacheTag.GET_USER_LIST)
```
