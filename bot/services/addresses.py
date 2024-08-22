from sqlalchemy.exc import IntegrityError

from bot.db.crud import CRUD
from bot.db.models import Address


class AddressService:

    def __init__(self):
        self.address_repo = CRUD(model=Address)

    async def add_address(self, **data):
        try:
            await self.address_repo.create(data=data)
        except IntegrityError:
            return

    async def find_address(self, **filter_by):
        data = await self.address_repo.read(filter_by=filter_by)
        address_list = {address.address: address.name for address in data}
        return address_list

    async def delete_address(self, **filter_by):
        await self.address_repo.delete(filter_by=filter_by)

    async def update_name_addr(self, name: str, **filter_by):
        await self.address_repo.update(filter_by=filter_by,
                                       values={'name': name})
