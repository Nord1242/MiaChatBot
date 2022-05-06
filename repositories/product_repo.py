from .base_repo import BaseSQLAlchemyRepo
from database.models import Product
from sqlalchemy import select


class ProductRepo(BaseSQLAlchemyRepo):
    model = Product

    async def get_product(self, product_id: str):
        sql = select(self.model).where(self.model.product_id == product_id)
        request = await self._session.execute(sql)
        product = request.scalar()
        return product

    async def get_all_product(self):
        sql = select(self.model)
        request = await self._session.execute(sql)
        products = request.scalars().all()
        return products
