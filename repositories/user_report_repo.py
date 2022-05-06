from .base_repo import BaseSQLAlchemyRepo
from database.models import Users, Report
from sqlalchemy import insert, select, delete, update


class UserReportRepo(BaseSQLAlchemyRepo):
    model = Report

    async def add_report(self, user_id: int, report: str, user: Users):
        report = self.model(complaint=report, user_id=user_id, counter=1)
        user.complaints.append(report)
        await self._session.commit()

    async def update_report(self, user_id: int, report: str, count: int):
        sql = update(self.model).where(self.model.user_id == user_id, self.model.complaint == report).values(
            counter=count + 1)
        await self._session.execute(sql)
        await self._session.commit()

    async def nulling_report(self, user_id: int, report: int):
        sql = update(self.model).where(self.model.user_id == user_id, self.model.complaint == report).values(counter=0)
        await self._session.execute(sql)
        await self._session.commit()

    async def nulling_all_report(self):
        sql = update(self.model).values(counter=0)
        await self._session.execute(sql)
        await self._session.commit()

# async def set_report(self, user_id: int, report_id: str):
#     sql =
