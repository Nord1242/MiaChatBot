from sqlalchemy import insert, select, delete

from .base_repo import BaseSQLAlchemyRepo
from database.models import UserProfile


class ProfileRepo(BaseSQLAlchemyRepo):
    model = UserProfile

    async def add_user_profile(self, login: str, user_id: int):
        user_profile = self.model(login=login, telegram_user_id=user_id)
        self._session.add(user_profile)
        await self._session.commit()

    async def get_user_profile(self, user_id: int):
        sql = select(self.model.login, self.model.sub).where(self.model.telegram_user_id == user_id)
        request = await self._session.execute(sql)
        profile = request.fetchone()
        return profile

