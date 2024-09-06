from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorClient
from app.api.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import ProductService
from typing import List, Optional
from app.schemas.user import UserOut

router = APIRouter()

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate, 
    db: AsyncIOMotorClient = Depends(get_db), 
    current_user: UserOut = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    return await product_service.create_product(product)

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str, 
    db: AsyncIOMotorClient = Depends(get_db), 
    current_user: UserOut = Depends(get_current_active_user)
):
    product_service = ProductService(db)
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product_service.serialize_to_product_out(product)

@router.get("/", response_model=List[ProductOut])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name", regex="^(name|price|stock)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    category: Optional[str] = None,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    product_service = ProductService(db)
    sort_order_int = 1 if sort_order == "asc" else -1
    return await product_service.get_products(skip, limit, sort_by, sort_order_int, category)

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: str, 
    product_update: ProductUpdate, 
    db: AsyncIOMotorClient = Depends(get_db), 
    current_user: UserOut = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    updated_product = await product_service.update_product(product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product_service.serialize_to_product_out(updated_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str, 
    db: AsyncIOMotorClient = Depends(get_db), 
    current_user: UserOut = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    deleted = await product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

@router.patch("/{product_id}/stock", status_code=status.HTTP_200_OK)
async def update_product_stock(
    product_id: str, 
    quantity: int = Query(..., gt=0), 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    updated = await product_service.update_stock(product_id, quantity)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update stock. Check if the product exists and has sufficient stock."
        )
    return {"message": "Stock updated successfully"}