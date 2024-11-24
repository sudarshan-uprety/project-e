from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    func
)


class Common(object):
    __abstract__ = True
    __tablename__ = "common"
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False, onupdate=func.now())
