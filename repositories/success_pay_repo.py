from .base_repo import BaseSQLAlchemyRepo
from database.models import SuccessPay
from sqlalchemy import select, delete


class SuccessPayRepo(BaseSQLAlchemyRepo):
    model = SuccessPay

    async def get_success_pay(self, user_id: int = None, payment_id: str = None):
        sql = select(self.model).where(
            self.model.payment_id == payment_id if payment_id else self.model.user_id == user_id)
        request = await self._session.execute(sql)
        success_pay = request.scalar()
        return success_pay

    async def add_success_pay(self, user_id: int, payment_id: int, product_id: str):
        success_pay = self.model(payment_id=payment_id, user_id=user_id, product_id=product_id)
        self._session.add(success_pay)
        await self._session.commit()



