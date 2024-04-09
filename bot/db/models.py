import datetime

from sqlalchemy import Integer, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


# class User(Base):
#     __tablename__ = 'user'
#     id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    user_fullname: Mapped[str] = mapped_column()
    alert: Mapped[bool] = mapped_column(default=False)
    address: Mapped[str] = mapped_column(nullable=True)
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())



