from .base_repo import BaseSQLAlchemyRepo
from database.models import Pay
from sqlalchemy import select, delete


class PayRepo(BaseSQLAlchemyRepo):
    model = Pay

    async def get_pay(self, user_id: int):
        sql = select(self.model).where(self.model.user_id == user_id)
        request = await self._session.execute(sql)
        user = request.scalar()
        return user

    async def add_pay(self, user_id: int, user_data: dict, intent_id: str):
        pay = self.model(user_id=user_id, user_data=user_data, intent_id=intent_id)
        self._session.add(pay)
        await self._session.commit()

    async def delete_pay(self, user_id: int):
        sql = delete(self.model).where(self.model.user_id == user_id)
        await self._session.execute(sql)
        await self._session.commit()


