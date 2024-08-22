from sqlalchemy import not_
from sqlalchemy.exc import IntegrityError

from bot.db.models import User
from bot.db.crud import CRUD


class UserService:

    def __init__(self):
        super().__init__()
        self.user_repo = CRUD(model=User)

    async def add_user(self, **data) -> bool:
        try:
            await self.user_repo.create(data=data)
            return True
        except IntegrityError:
            return False

    async def find_user_status(self, **filter_by):
        user = await self.user_repo.find_one(filter_by=filter_by)
        return user.alert

    async def update_alert(self, **filter_by):
        await self.user_repo.update(filter_by=filter_by,
                                    values={'alert': not_(User.alert)})
