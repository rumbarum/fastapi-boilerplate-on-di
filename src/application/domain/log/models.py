import uuid

import sqlalchemy as sa
from sqlalchemy import BigInteger, Column
from sqlalchemy_utils import UUIDType

from application.core.db import Base
from application.core.db.mixins import TimestampMixin


class RequestResponseLog(Base, TimestampMixin):
    __tablename__ = "request_response_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(sa.INTEGER)
    ip = Column(sa.VARCHAR, nullable=False)
    port = Column(sa.INTEGER, nullable=False)
    agent = Column(sa.VARCHAR, nullable=False)
    method = Column(sa.VARCHAR(20), nullable=False)
    path = Column(sa.VARCHAR(20), nullable=False)
    response_status = Column(sa.SMALLINT, nullable=False)
    request_id = Column(UUIDType(binary=False), nullable=False, default=uuid.uuid4)
