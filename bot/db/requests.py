import asyncio

from sqlalchemy import select, update, insert, delete

from bot.db.database import async_session
from bot.db.models import User, Address


async def create_profile(user_id: int, user_fullname: str, username: str):
    async with async_session() as session:
        user = (await session.execute(select(User.id).filter_by(user_id=user_id))).all()
        if not user:
            user = User(user_id=user_id, username=username, user_fullname=user_fullname)
            session.add(user)
            await session.commit()
            return False
        else:
            return True


async def update_profile_addr(user_id: int, address: str):
    async with async_session() as session:
        stmt = insert(Address).values(address=address, user_id=user_id)
        await session.execute(stmt)
        await session.commit()


async def get_address(user_id: int):
    async with async_session() as session:
        resp = await session.execute(select(Address).filter_by(user_id=user_id))
        address_list = [address.address for address in resp.scalars().all()]
        return address_list


async def get_addr_name(user_id: int):
    async with async_session() as session:
        stmt = select(Address).filter_by(user_id=user_id)
        resp = await session.execute(stmt)
        address_list = [[address.address, address.name] for address in resp.scalars().all()]
        return address_list


async def get_alert_status(user_id: int):
    async with async_session() as session:
        resp = await session.execute(select(User.alert).filter_by(user_id=user_id))
        return resp.first()[0]


async def update_profile_alert(user_id: int):
    alert = await get_alert_status(user_id=user_id)
    async with async_session() as session:
        await session.execute(update(User).filter_by(user_id=user_id).values(alert=not alert))
        await session.commit()


async def get_list_alert_user():
    async with async_session() as session:
        resp = await session.execute(select(User.user_id).filter_by(alert=True))
        return resp.scalars().all()


async def delete_address_by_user_id(user_id: int, address: str) -> None:
    async with async_session() as session:
        stmt = delete(Address).filter_by(user_id=user_id, address=address)
        await session.execute(stmt)
        await session.commit()


async def update_name_addr(user_id: int, address: str, addr_name: str):
    async with async_session() as session:
        stmt = update(Address).filter_by(user_id=user_id, address=address).values(name=addr_name)
        await session.execute(stmt)
        await session.commit()