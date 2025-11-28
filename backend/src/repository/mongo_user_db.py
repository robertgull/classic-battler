from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient  # Used for creating indexes
from src.core.user_model import User
from src.repository.interface.database import DbBase

class UserMongoDb(DbBase):
    def __init__(self):
        pymongo_client = MongoClient("mongodb://localhost:27018")
        pm_db = pymongo_client["userdb"]
        pm_db.users.create_index("email", unique=True)
        pm_db.identities.create_index(
            [("provider", 1), ("provider_user_id", 1)],
            unique=True,
        )

        self.async_client = AsyncIOMotorClient("mongodb://localhost:27018")
        self.db = self.async_client["userdb"]
        self.collection = self.db.users

    async def get_user(self, user_email: str) -> User | None:
        data = await self.db.users.find_one({"email": user_email})
        if data is None:
            return None
        data.pop("_id", None)  # the id is email, don't need this
        return User(**data)

    async def get_user_collection(self, user_email: str) -> User | None:
        data = await self.db.users.find_one({"email": user_email})
        if data is None:
            return None
        data.pop("_id", None)
        return User(**data) # Only return collection here

    async def add_user(self, user: User) -> None:
        await self.db.users.insert_one(user.model_dump())

    async def add_pet_to_user(self, user_email: str, pet_id: int) -> None:
        await self.collection.update_one(
            {"email": user_email},
            {"$push": {"collection": pet_id}}
        )