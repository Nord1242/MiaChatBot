from repositories.pay_repo import PayRepo
from web_app.get_repo import get_repo
import asyncio
import datetime


async def delete_old_pay():
    while True:
        print('1')
        repo: PayRepo = await get_repo(PayRepo)
        now = datetime.datetime.utcnow()
        next_day = now + datetime.timedelta(days=1)
        next_day = datetime.datetime.combine(next_day, datetime.time.min)
        await repo.delete_old_pay()
        difference = next_day - now
        total = difference.total_seconds()
        print(next_day)
        await asyncio.sleep(total)
