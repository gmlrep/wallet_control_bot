import datetime

from sqlalchemy import Integer, BigInteger, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    user_fullname: Mapped[str] = mapped_column()
    alert: Mapped[bool] = mapped_column(default=False)
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    address: Mapped['Address'] = relationship(back_populates='user')


class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    address: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'))

    user: Mapped['User'] = relationship(back_populates='address')
