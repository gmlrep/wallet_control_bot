import asyncio

from sqlalchemy import select, update, delete, insert

from bot.db.database import async_session
from bot.db.models import User, Address


class CRUD:
    def __init__(self, model):
        self.model = model

    async def create(self, data: dict):
        async with async_session() as session:
                stmt = insert(self.model).values(**data)
                await session.execute(stmt)
                await session.commit()

    async def read(self, filter_by: dict):
        async with async_session() as session:
            stmt = select(self.model).filter_by(**filter_by)
            data = await session.execute(stmt)
            return data.scalars().all()

    async def update(self, filter_by: dict, values: dict):
        async with async_session() as session:
            stmt = update(self.model).filter_by(**filter_by).values(values)
            await session.execute(stmt)
            await session.commit()

    async def delete(self, filter_by: dict):
        async with async_session() as session:
            stmt = delete(self.model).filter_by(**filter_by)
            await session.execute(stmt)
            await session.commit()

    async def find_one(self, filter_by: dict):
        async with async_session() as session:
            stmt = select(self.model).filter_by(**filter_by)
            data = await session.execute(stmt)
            return data.scalars().first()


# async def get_list_alert_user_addr() -> list:
#     async with async_session() as session:
#         stmt = select(User.user_id, Address.address).join(
#             Address, User.user_id == Address.user_id).filter(User.alert)
#         resp = await session.execute(stmt)
#         return resp.all()

# async def create_profile(user_id: int, user_fullname: str, username: str) -> bool:
#     async with async_session() as session:
#         try:
#             stmt = insert(User).values(user_id=user_id, username=username, user_fullname=user_fullname)
#             await session.execute(stmt)
#             await session.commit()
#             return True
#         except IntegrityError:
#             return False


# async def add_address(user_id: int, address: str):
#     async with async_session() as session:
#         stmt = insert(Address).values(address=address, user_id=user_id)
#         await session.execute(stmt)
#         await session.commit()


# async def get_addr_name(user_id: int) -> dict:
#     async with async_session() as session:
#         stmt = select(Address).filter_by(user_id=user_id)
#         resp = await session.execute(stmt)
#         address_list = {address.address: address.name for address in resp.scalars().all()}
#         return address_list


# async def get_alert_status(user_id: int) -> bool:
#     async with async_session() as session:
#         resp = await session.execute(select(User.alert).filter_by(user_id=user_id))
#         return resp.scalar()


# async def update_profile_alert(user_id: int):
#     async with async_session() as session:
#         stmt = update(User).filter_by(user_id=user_id).values(alert=not_(User.alert))
#         await session.execute(stmt)
#         await session.commit()


# async def delete_address_by_user_id(user_id: int, address: str) -> None:
#     async with async_session() as session:
#         stmt = delete(Address).filter_by(user_id=user_id, address=address)
#         await session.execute(stmt)
#         await session.commit()


# async def update_name_addr(user_id: int, address: str, addr_name: str):
#     async with async_session() as session:
#         stmt = update(Address).filter_by(user_id=user_id, address=address).values(name=addr_name)
#         await session.execute(stmt)
#         await session.commit()
