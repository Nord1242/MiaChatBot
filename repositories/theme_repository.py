from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ThemeTable
from .base_repo import BaseSQLAlchemyRepo


class ThemeRepo(BaseSQLAlchemyRepo):
    model = ThemeTable

    async def add_theme(self, user_id: int, theme_name: str):
        theme = self.model(theme_name=theme_name, telegram_user_id=user_id)
        self._session.add(theme)
        await self._session.commit()

    async def get_theme(self, theme_name: str, user_id: int = None):
        sql = select(self.model).where(self.model.theme_name == theme_name)
        request = await self._session.execute(sql)
        theme = request.scalar()
        return theme

    async def get_all_themes(self):
        sql = select(self.model)
        result = await self._session.execute(sql)
        result = result.scalars().all()
        return result

    async def delete_theme(self, user_id: int):
        sql = delete(self.model).where(self.model.telegram_user_id == user_id)
        theme = await self._session.execute(sql)
        await self._session.commit()



