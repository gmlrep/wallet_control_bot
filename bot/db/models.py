import datetime

from sqlalchemy import Integer, BigInteger, func
from sqlalchemy.orm import as_declarative, declared_attr, Mapped, mapped_column


@as_declarative()
class AbstractModel:
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    # Называет таблицы как классы
    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(AbstractModel):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    user_fullname: Mapped[str] = mapped_column()
    alert: Mapped[bool] = mapped_column(default=False)
    address: Mapped[str] = mapped_column(nullable=True)
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())



