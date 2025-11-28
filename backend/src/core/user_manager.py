from typing import Optional
import bcrypt
from src.repository.interface.database import DbBase
from src.core.user_model import User, UserCreateNative
from src.repository.mongo_user_db import UserMongoDb

def hash_password(password: str) -> bytes:
    password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    salt = hashed_password[:29]
    print(f"salt: {salt}")
    return hashed_password

def verify_password(password: str, hashed_password: bytes) -> bool:
    salt = hashed_password[:29]
    print(f"salt: {salt}")
    print(f"Comparing hashed password: {hashed_password} and password: {password.encode()}")
    is_valid_password = bcrypt.checkpw(password.encode(), hashed_password)

    if is_valid_password:
        print("Password is correct")
    else:
        print("Invalid password")
    return is_valid_password

class UserManager:
    def __init__(self, db: Optional[DbBase] = None) -> None:
        self.db = db or UserMongoDb()

    async def add_user_via_password(self, create_user: UserCreateNative) -> User:
        hashed_password = hash_password(create_user.password_plaintext)
        user_to_add = User(email=create_user.email, hashed_password=hashed_password)
        await self.db.add_user(user_to_add)
        return user_to_add

    async def get_user(self, email: str) -> User:
        return await self.db.get_user(email)

    async def verify_user(self, email: str, password: str) -> User | None:
        user = await self.db.get_user(email)
        if verify_password(password=password, hashed_password=user.hashed_password):
            return user
        else:
            return None

    async def add_pet_to_collection(self, pet_id: int, user_email: str) -> None:
        await self.db.add_pet_to_user(user_email, pet_id)


    async def get_or_create_oauth_user(
        self,
        email: str,
        *,
        discord: bool = False,
        google: bool = False,
    ) -> User:
        user = await self.db.get_user(email)
        if user:
            return user

        user = User(
            email=email,
            hashed_password=b"",
            discord=discord,
        )
        await self.db.add_user(user)
        return user