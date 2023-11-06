from sqlalchemy import BigInteger, Column

from application.core.db import Base
from application.core.fastapi.pydantic_models import ResponseBaseModel


class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class YourResponseModel(ResponseBaseModel):
    ...
