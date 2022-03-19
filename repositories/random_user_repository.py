from sqlalchemy import insert, select, delete

from database.models import RandomUserId
from .base_repo import BaseSQLAlchemyRepo


class RandomUsersRepo(BaseSQLAlchemyRepo):
    model = RandomUserId

    async def add_user(self, user_id: int):
        user = self.model(user_id=user_id)
        self._session.add(user)
        await self._session.commit()

    async def delete_user(self, user_id: int):
        sql = delete(self.model).where(self.model.user_id == user_id)
        await self._session.execute(sql)
        await self._session.commit()

    async def get_all_users(self):
        sql = select(self.model)
        result = await self._session.execute(sql)
        result = result.scalars().all()
        return result
