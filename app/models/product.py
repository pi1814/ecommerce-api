# app/models/product.py
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from app.models.user import PyObjectId

class ProductModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    price: float
    stock: int
    category: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}