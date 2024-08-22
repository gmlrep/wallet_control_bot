from sqlalchemy import select

from bot.db.database import async_session
from bot.db.models import User, Address
from bot.services.users import UserService
from bot.services.addresses import AddressService


class Database(UserService, AddressService):

    @staticmethod
    async def find_addr_alert_user():
        async with async_session() as session:
            stmt = select(User.user_id, Address.address).join(
                Address, User.user_id == Address.user_id).filter(User.alert)
            resp = await session.execute(stmt)
            return resp.all()
