from motor.motor_asyncio import AsyncIOMotorClient
from app.models.shopping_cart import ShoppingCartModel, CartItem
from app.schemas.shopping_cart import ShoppingCartCreate, CartItemCreate, CartItemUpdate
from bson import ObjectId
from typing import Optional

class ShoppingCartService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def create_cart(self, cart: ShoppingCartCreate) -> ShoppingCartModel:
        cart_dict = cart.dict()
        cart_dict["user_id"] = ObjectId(cart_dict["user_id"])
        cart_obj = await self.db.shopping_carts.insert_one(cart_dict)
        return await self.get_cart(str(cart_obj.inserted_id))

    async def get_cart(self, cart_id: str) -> Optional[ShoppingCartModel]:
        cart = await self.db.shopping_carts.find_one({"_id": ObjectId(cart_id)})
        if cart:
            return ShoppingCartModel(**cart)
        return None

    async def get_cart_by_user(self, user_id: str) -> Optional[ShoppingCartModel]:
        cart = await self.db.shopping_carts.find_one({"user_id": ObjectId(user_id)})
        if cart:
            return ShoppingCartModel(**cart)
        return None

    async def add_item_to_cart(self, cart_id: str, item: CartItemCreate) -> Optional[ShoppingCartModel]:
        result = await self.db.shopping_carts.update_one(
            {"_id": ObjectId(cart_id)},
            {"$push": {"items": {"product_id": ObjectId(item.product_id), "quantity": item.quantity}}}
        )
        if result.modified_count:
            return await self.get_cart(cart_id)
        return None

    async def update_cart_item(self, cart_id: str, product_id: str, item_update: CartItemUpdate) -> Optional[ShoppingCartModel]:
        result = await self.db.shopping_carts.update_one(
            {"_id": ObjectId(cart_id), "items.product_id": ObjectId(product_id)},
            {"$set": {"items.$.quantity": item_update.quantity}}
        )
        if result.modified_count:
            return await self.get_cart(cart_id)
        return None

    async def remove_item_from_cart(self, cart_id: str, product_id: str) -> Optional[ShoppingCartModel]:
        result = await self.db.shopping_carts.update_one(
            {"_id": ObjectId(cart_id)},
            {"$pull": {"items": {"product_id": ObjectId(product_id)}}}
        )
        if result.modified_count:
            return await self.get_cart(cart_id)
        return None

    async def clear_cart(self, cart_id: str) -> Optional[ShoppingCartModel]:
        result = await self.db.shopping_carts.update_one(
            {"_id": ObjectId(cart_id)},
            {"$set": {"items": []}}
        )
        if result.modified_count:
            return await self.get_cart(cart_id)
        return None

    async def delete_cart(self, cart_id: str) -> bool:
        result = await self.db.shopping_carts.delete_one({"_id": ObjectId(cart_id)})
        return result.deleted_count > 0