from sqlalchemy import select, update

from bot.db.database import async_session
from bot.db.models import User


async def create_profile(user_id: int, user_fullname: str, username: str, address: str = None, alert: bool = True):
    async with async_session() as session:
        user = (await session.execute(select(User.id).filter_by(user_id=user_id))).all()
        if not user:
            user = User(user_id=user_id, username=username, user_fullname=user_fullname, alert=alert, address=address)
            session.add(user)
            await session.commit()
            return False
        else:
            return True


async def update_profile_addr(user_id: int, address: str):
    async with async_session() as session:
        await session.execute(update(User).filter_by(user_id=user_id).values(address=address))
        await session.commit()


async def get_address(user_id: int):
    async with async_session() as session:
        resp = await session.execute(select(User.address).filter_by(user_id=user_id))
        return resp.first()[0]


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
