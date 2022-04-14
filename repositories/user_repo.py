from sqlalchemy import insert, select, delete, update
from datetime import datetime
from .base_repo import BaseSQLAlchemyRepo
from database.models import Users
from datetime import datetime


class UserRepo(BaseSQLAlchemyRepo):
    model = Users

    async def add_user(self, user_id: int, first_name: str, last_name: str, username: str):
        user = self.model(telegram_user_id=user_id, first_name=first_name, last_name=last_name, username=username)
        self._session.add(user)
        await self._session.commit()

    async def set_sub(self, user_id: int, datatime_sub: datetime):
        sql = update(self.model).where(self.model.telegram_user_id == user_id).values(sub=datatime_sub)
        await self._session.execute(sql)

    async def set_money(self, user_id: int, money: int):
        sql = update(self.model).where(self.model.telegram_user_id == user_id).values(money=money)
        await self._session.execute(sql)

    async def get_user(self, user_id: int):
        sql = select(self.model).where(self.model.telegram_user_id == user_id)
        request = await self._session.execute(sql)
        user = request.scalar()
        return user
