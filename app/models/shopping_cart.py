from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List
from app.models.user import PyObjectId

class CartItem(BaseModel):
    product_id: PyObjectId
    quantity: int

class ShoppingCartModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    items: List[CartItem] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}