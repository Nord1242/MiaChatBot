from sqlalchemy import insert, select, delete, update
from .base_repo import BaseSQLAlchemyRepo
from database.models import Users, Report, SuccessPay
from datetime import datetime, timedelta
from sqlalchemy.orm.collections import InstrumentedList


class UserRepo(BaseSQLAlchemyRepo):
    model_user = Users
    model_report = Report
    model_pay = SuccessPay

    async def get_all_user_id(self):
        sql = select(self.model_user.telegram_user_id)
        request = await self._session.execute(sql)
        return request.scalars().all()

    async def add_user(self, user_id: int, first_name: str, last_name: str, username: str):
        sql = insert(self.model_user).values(telegram_user_id=user_id, first_name=first_name, last_name=last_name,
                                             username=username).returning('*')
        result = await self._session.execute(sql)
        await self._session.commit()
        return result.first()

    #
    # async def add_success_pay(self, user_id: int, payment_id: int, product_id: str):
    #     # success_pay = self.model(payment_id=payment_id, user_id=user_id, product_id=product_id)
    #     self._session.add(success_pay)
    #     await self._session.commit()

    async def set_sub(self, user_id: int, day_sub: int, product_id: str, payment_id: int):
        datatime_sub = datetime.utcnow() + timedelta(days=day_sub)
        success_pay = self.model_pay(payment_id=payment_id, user_id=user_id, product_id=product_id)
        user: Users = await self.get_user(user_id=user_id)
        user.success_payment.append(success_pay)
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(
            product_date_end=datatime_sub)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_top(self, user_id: int, product_id: str, payment_id: int):
        datatime_top = datetime.utcnow() + timedelta(days=1)
        success_pay = self.model_pay(payment_id=payment_id, user_id=user_id, product_id=product_id)
        user: Users = await self.get_user(user_id=user_id)
        user.success_payment.append(success_pay)
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(
            top_date_end=datatime_top,
            top=True)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_time_ban(self, user_id: int, ban_info: str, ban_date: datetime, attempts: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(time_ban=ban_date,
                                                                                                ban_info=ban_info,
                                                                                                attempts=attempts,)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_ban(self, user_id: int, ban_info: str):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(ban=True,
                                                                                                ban_info=ban_info)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_sub_ban(self, user_id: int, ban_info: str):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(sub_ban=True,
                                                                                                ban_info=ban_info)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_human(self, user_id: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(is_human=True)
        await self._session.execute(sql)
        await self._session.commit()

    async def set_timeout(self, user_id: int):
        timeout_set = datetime.utcnow() + timedelta(hours=3.5)
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(timeout=timeout_set)
        await self._session.execute(sql)
        await self._session.commit()

    async def delete_timeout(self, user_id: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(timeout=None)
        await self._session.execute(sql)
        await self._session.commit()

    async def delete_time_ban(self, user_id: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(time_ban=None,
                                                                                                ban_info=None)
        await self._session.execute(sql)
        await self._session.commit()


    async def delete_ban(self, user_id: int, payment_id: int, product_id: str):
        success_pay = self.model_pay(payment_id=payment_id, user_id=user_id, product_id=product_id)
        user: Users = await self.get_user(user_id=user_id)
        user.success_payment.append(success_pay)
        sql = update(Users).where(Users.telegram_user_id == user_id).values(sub_ban=False, ban_info=None)
        sql_report = delete(Report).where(Report.user_id == user_id)
        await self._session.execute(sql)
        await self._session.execute(sql_report)
        await self._session.commit()

    async def delete_top(self, user_id: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(top_date_end=None,
                                                                                                top=False)
        await self._session.execute(sql)
        await self._session.commit()

    async def delete_sub(self, user_id: int):
        sql = update(self.model_user).where(self.model_user.telegram_user_id == user_id).values(product_date_end=None)
        await self._session.execute(sql)
        await self._session.commit()

    async def get_user(self, user_id: int):
        sql = select(self.model_user).where(self.model_user.telegram_user_id == user_id)
        request = await self._session.execute(sql)
        user = request.scalar()
        return user
