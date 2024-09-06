from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.security import get_password_hash, verify_password
from bson import ObjectId

class UserService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def create_user(self, user: UserCreate) -> UserModel:
        user_dict = user.dict()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["is_active"] = True
        user_dict["role"] = "user"
        user_obj = await self.db.users.insert_one(user_dict)
        return await self.get_user(user_obj.inserted_id)

    async def get_user(self, user_id: str) -> UserModel:
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserModel(**user)

    async def get_user_by_email(self, email: str) -> UserModel:
        user = await self.db.users.find_one({"email": email})
        if user:
            return UserModel(**user)

    async def get_user_by_username(self, username: str) -> UserModel:
        user = await self.db.users.find_one({"username": username})
        if user:
            return UserModel(**user)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserModel:
        update_data = user_update.dict(exclude_unset=True)
        await self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return await self.get_user(user_id)

    async def delete_user(self, user_id: str) -> bool:
        result = await self.db.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def get_users(self, skip: int = 0, limit: int = 10):
        users = await self.db.users.find().skip(skip).limit(limit).to_list(length=limit)
        return [self.serialize_to_user_out(UserModel(**user)) for user in users]

    async def authenticate_user(self, username: str, password: str) -> UserModel:
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def serialize_to_user_out(self, user: UserModel) -> UserOut:
        return { "id": str(user.id),"email": user.email,"is_active": user.is_active, "role": user.role, "username": user.username}