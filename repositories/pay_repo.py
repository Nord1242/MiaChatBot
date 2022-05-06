import datetime

from .base_repo import BaseSQLAlchemyRepo
from database.models import Pay
from sqlalchemy import select, delete, update


class PayRepo(BaseSQLAlchemyRepo):
    model = Pay

    async def get_pay(self, payment_id: int):
        sql = select(self.model).where(self.model.payment_id == payment_id)
        request = await self._session.execute(sql)
        user = request.scalar()
        return user

    async def add_pay(self, user_id: int, intent_id: str, user_data: dict, payment_id: str, product_data: dict):
        pay = self.model(user_id=user_id, intent_id=intent_id, user_data=user_data, payment_id=payment_id,
                         product_data=product_data)
        self._session.add(pay)
        await self._session.commit()

    async def delete_pay(self, payment_id: str = None):
        sql = delete(self.model).where(self.model.payment_id == payment_id)
        await self._session.execute(sql)
        await self._session.commit()

    async def delete_old_pay(self):
        now = datetime.datetime.utcnow()
        yesterday = now - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(yesterday, datetime.time.max)
        sql = delete(self.model).where(self.model.date <= yesterday)
        await self._session.execute(sql)
        await self._session.commit()

    async def update_pay(self, payment_id: str, product_data: dict):
        sql = update(self.model).where(self.model.user_id == payment_id).values(product_data=product_data)
        request = await self._session.execute(sql)
        await self._session.commit()
        # return request.scalar()
