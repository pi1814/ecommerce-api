from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from app.api.dependencies import get_db, get_current_active_user
from app.schemas.shopping_cart import ShoppingCartCreate, ShoppingCartOut, CartItemCreate, CartItemUpdate
from app.services.shopping_cart_service import ShoppingCartService
from app.schemas.user import UserOut

router = APIRouter()

@router.post("/", response_model=ShoppingCartOut, status_code=status.HTTP_201_CREATED)
async def create_shopping_cart(
    cart: ShoppingCartCreate, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    new_cart = await cart_service.create_cart(cart)
    return await cart_service.serialize_to_shopping_cart_out(new_cart)

@router.get("/{cart_id}", response_model=ShoppingCartOut)
async def get_shopping_cart(
    cart_id: str, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart not found"
        )
    if str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shopping cart"
        )
    return await cart_service.serialize_to_shopping_cart_out(cart)

@router.get("/user/{user_id}", response_model=ShoppingCartOut)
async def get_shopping_cart_by_user(
    user_id: str, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shopping cart"
        )
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart_by_user(user_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart not found for this user"
        )
    return await cart_service.serialize_to_shopping_cart_out(cart)

@router.post("/{cart_id}/items", response_model=ShoppingCartOut)
async def add_item_to_cart(
    cart_id: str, 
    item: CartItemCreate, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart or str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping cart"
        )
    updated_cart = await cart_service.add_item_to_cart(cart_id, item)
    if not updated_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart not found"
        )
    return await cart_service.serialize_to_shopping_cart_out(updated_cart)

@router.put("/{cart_id}/items/{product_id}", response_model=ShoppingCartOut)
async def update_cart_item(
    cart_id: str, 
    product_id: str, 
    item_update: CartItemUpdate, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart or str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping cart"
        )
    updated_cart = await cart_service.update_cart_item(cart_id, product_id, item_update)
    if not updated_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart or item not found"
        )
    return await cart_service.serialize_to_shopping_cart_out(updated_cart)

@router.delete("/{cart_id}/items/{product_id}", response_model=ShoppingCartOut)
async def remove_item_from_cart(
    cart_id: str, 
    product_id: str, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart or str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping cart"
        )
    updated_cart = await cart_service.remove_item_from_cart(cart_id, product_id)
    if not updated_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart or item not found"
        )
    return await cart_service.serialize_to_shopping_cart_out(updated_cart)

@router.delete("/{cart_id}/clear", response_model=ShoppingCartOut)
async def clear_shopping_cart(
    cart_id: str, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart or str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping cart"
        )
    cleared_cart = await cart_service.clear_cart(cart_id)
    if not cleared_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart not found"
        )
    return await cart_service.serialize_to_shopping_cart_out(cleared_cart)

@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_cart(
    cart_id: str, 
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user)
):
    cart_service = ShoppingCartService(db)
    cart = await cart_service.get_cart(cart_id)
    if not cart or str(cart.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this shopping cart"
        )
    deleted = await cart_service.delete_cart(cart_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping cart not found"
        )