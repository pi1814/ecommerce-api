from motor.motor_asyncio import AsyncIOMotorClient
from app.models.product import ProductModel
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from bson import ObjectId
from typing import List, Optional

class ProductService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def create_product(self, product: ProductCreate) -> ProductModel:
        product_dict = product.dict()
        product_obj = await self.db.products.insert_one(product_dict)
        return await self.get_product(product_obj.inserted_id)

    async def get_product(self, product_id: str) -> Optional[ProductModel]:
        product = await self.db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            return ProductModel(**product)
        return None

    async def update_product(self, product_id: str, product_update: ProductUpdate) -> Optional[ProductModel]:
        update_data = product_update.dict(exclude_unset=True)
        await self.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        return await self.get_product(product_id)

    async def delete_product(self, product_id: str) -> bool:
        result = await self.db.products.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

    async def get_products(self, skip: int = 0, limit: int = 10, sort_by: str = "name", sort_order: int = 1, category: Optional[str] = None) -> List[ProductModel]:
        filter_query = {}
        if category:
            filter_query["category"] = category

        cursor = self.db.products.find(filter_query)
        cursor.sort(sort_by, sort_order).skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)
        return [self.serialize_to_product_out(ProductModel(**product)) for product in products]

    async def update_stock(self, product_id: str, quantity: int) -> bool:
        result = await self.db.products.update_one(
            {"_id": ObjectId(product_id), "stock": {"$gte": quantity}},
            {"$inc": {"stock": -quantity}}
        )
        return result.modified_count > 0

    def serialize_to_product_out(self, product: ProductModel) -> ProductOut:
        return { "id": str(product.id),"name": product.name,"description": product.description, "price": product.price, "stock": product.stock, "category": product.category}