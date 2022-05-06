from loader import async_sessionmaker
from repositories.repo import SQLAlchemyRepo


async def get_repo(repo):
    async with async_sessionmaker() as session:
        async with session.begin():
            repos_base = SQLAlchemyRepo(session=session)
            repos = repos_base.get_repo(repo)
            return repos
