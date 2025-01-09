from typing import Optional
from uuid import UUID
from passlib.context import CryptContext
from models.user import UserInDB, UserCreate, UserUpdate
from core.mongodb import mongodb

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserInDB]:
        user_doc = await mongodb.db.users.find_one({"email": email})
        if user_doc:
            user_doc["id"] = str(user_doc.pop("_id"))
            return UserInDB(**user_doc)
        return None

    @staticmethod
    async def create_user(user_create: UserCreate) -> UserInDB:
        # Check if email already exists
        existing_user = await UserService.get_user_by_email(user_create.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user_db = UserInDB(
            email=user_create.email,
            full_name=user_create.full_name,
            nickname=user_create.nickname,
            hashed_password=UserService.hash_password(user_create.password)
        )

        # Store user data
        user_dict = user_db.model_dump()
        user_dict["_id"] = str(user_dict.pop("id"))
        await mongodb.db.users.insert_one(user_dict)
        
        return user_db

    @staticmethod
    async def update_user(user_id: UUID, user_update: UserUpdate) -> Optional[UserInDB]:
        update_data = user_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = UserService.hash_password(update_data.pop("password"))

        result = await mongodb.db.users.find_one_and_update(
            {"_id": str(user_id)},
            {"$set": update_data},
            return_document=True
        )

        if result:
            result["id"] = str(result.pop("_id"))
            return UserInDB(**result)
        return None
