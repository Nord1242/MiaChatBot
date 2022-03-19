from .base_repo import BaseSQLAlchemyRepo
from typing import Type, TypeVar
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

BaseSQLAlchemyRepoType = TypeVar("BaseSQLAlchemyRepoType", bound=BaseSQLAlchemyRepo)


class SQLAlchemyRepo:

    def __init__(self, session: AsyncSession):
        self._session = session

    @lru_cache()
    def get_repo(self, repo: Type[BaseSQLAlchemyRepo]) -> BaseSQLAlchemyRepoType:
        return repo(self._session)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
