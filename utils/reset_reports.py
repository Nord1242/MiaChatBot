from repositories.user_repo import UserRepo
from repositories.user_report_repo import UserReportRepo
from web_app.get_repo import get_repo
import asyncio
import datetime


async def delete_report():
    while True:
        print('2')
        repo: UserRepo = await get_repo(UserRepo)
        report_repo: UserReportRepo = await get_repo(UserReportRepo)
        now = datetime.datetime.utcnow()
        next_day = now + datetime.timedelta(days=1)
        next_day = datetime.datetime.combine(next_day, datetime.time.min)
        await report_repo.nulling_all_report()
        difference = next_day - now
        total = difference.total_seconds()
        await asyncio.sleep(total)
