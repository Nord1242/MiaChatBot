import asyncio
import datetime


async def delete_old_pay():
    while True:
        print('3')

        now = datetime.datetime.utcnow()
        next_day = now + datetime.timedelta(days=1)
        next_day = datetime.datetime.combine(next_day, datetime.time.min)
        difference = next_day - now
        total = difference.total_seconds()
        await asyncio.sleep(total)
