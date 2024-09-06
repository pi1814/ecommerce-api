from pydantic import BaseModel, Field
from typing import List, Optional

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemOut(BaseModel):
    product_id: str
    quantity: int

class ShoppingCartCreate(BaseModel):
    user_id: str

class ShoppingCartUpdate(BaseModel):
    items: List[CartItemCreate]

class ShoppingCartOut(BaseModel):
    id: str
    user_id: str
    items: List[CartItemOut]