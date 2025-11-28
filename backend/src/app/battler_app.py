from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Body
from src.core.pet_manager import PetManager
from src.core.user_manager import UserManager
from src.core.models import BattlePet, PetType, Ability
from src.core.user_model import UserCreateNative, User, UserOut
from fastapi.middleware.cors import CORSMiddleware
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

# google auth
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
# Innate auth
SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Discord auth
DISCORD_CLIENT_ID = ""
DISCORD_CLIENT_SECRET = ""
DISCORD_REDIRECT_URI = "http://localhost:5173/discord-callback"
DISCORD_TOKEN_URL = "https://discord.com/api/v10/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/v10/users/@me"

# https://discord.com/oauth2/authorize?client_id=1439358085104664737&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fdiscord-callback&scope=identify+email
class DiscordCodePayload(BaseModel):
    code: str

class AddPetRequest(BaseModel):
    pet_id: int

class UserInDB(BaseModel):#  TODO: REMOVE
    email: str
    hashed_password: str


fake_users_db = { #  TODO: REMOVE
    "testuser": UserInDB(
        email="testuser",
        hashed_password="fakehashedpassword",
    )
}

##################### INNATE AUTH ##################### not OAuth2, but maybe OK. TODO: REMOVE
def secure_hash(password: str) -> str:
    return "fakehashed" + password

def get_user(db, username: str) -> UserInDB | None:
    if username in db:
        return db[username]
    return None

def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = get_user(fake_users_db, username)
    if not user:
        return None
    if user.hashed_password != secure_hash(password):
        return None
    return None




def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=150))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

##################### GOOGLE AUTH #####################
def get_or_create_google_user(email: str) -> UserInDB:
    # In real life, look up in your DB and create if missing
    if email in fake_users_db:
        return fake_users_db[email]

    user = UserInDB(
        email=email,
        hashed_password="",
    )
    fake_users_db[email] = user
    return user


class BattlerApp:
    def __init__(self):
        self.app = FastAPI(title="battler_app", version="0.0.1")
        self.router = APIRouter()
        self.manager = PetManager()
        self.user_manager = UserManager()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  #  ["http://localhost:5173"] for dev
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email: str | None = payload.get("sub")
                if email is None:
                    raise credentials_exception
            except JWTError:
                raise credentials_exception

            user = await self.user_manager.get_user(email)
            if user is None:
                raise credentials_exception
            return user

        @self.router.get("/battle_pets/get")
        async def list_battle_pets() -> list[BattlePet]:
            return await self.manager.list_battle_pets()

        @self.router.get("/battle_pets/get_by_id")
        async def get_battle_pet_by_id(_id: int) -> BattlePet:
            return await self.manager.get_pet(_id)

        @self.router.get(
            "/users/me",
            response_model=UserOut,
            summary="Get current user (including collection)",
        )
        async def get_me(current_user: User = Depends(get_current_user)):
            collection = current_user.collection or []

            return UserOut(
                email=current_user.email,
                user_name=current_user.user_name,
                discord=current_user.discord,
                google=current_user.google,
                collection=collection,
            )

        @self.router.post(
            "/users/me/collection",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Add a pet to the current user's collection",
        )
        async def add_pet_to_collection(
            payload: AddPetRequest,
            current_user: User = Depends(get_current_user),
        ):
            await self.user_manager.add_pet_to_collection(
                pet_id=payload.pet_id,
                user_email=current_user.email,
            )
            return

        @self.router.get("/battle_pets/list_double_counters")
        async def list_double_counters(
            _type: str = Query(..., description="Pet type (e.g. 'Aquatic', 'Beast')"),
        ) -> list[BattlePet]:
            try:
                type_enum = PetType(_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid pet type: {_type}"
                )
            return await self.manager.double_tappers(type_enum)

        @self.router.get("/abilities/get_by_id")
        async def get_ability_by_id(_id: int) -> Ability:
            return await self.manager.get_ability(_id)

        @self.router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
        async def create_user(payload: UserCreateNative):
            existing = await self.user_manager.get_user(payload.email)
            if existing:
                raise HTTPException(status_code=400, detail="User already exists")
            user = await self.user_manager.add_user_via_password(payload)
            return user # TODO: Don't return the entire user

        @self.app.post("/token") ##################### INNATE AUTH #####################
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            user = await self.user_manager.verify_user(form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = create_access_token(
                data={"sub": user.email}
            )
            return {"access_token": access_token, "token_type": "bearer", "email": user.email}

        self.app.include_router(self.router)

        @self.app.post("/auth/google") ##################### GOOGLE AUTH ##################### TODO: FIX
        async def google_login(token: str = Body(..., embed=True)): # counts as OpenID Connect
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    google_requests.Request(),
                    GOOGLE_CLIENT_ID,
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token",
                )
            print(idinfo)
            if idinfo.get("iss") not in [
                "https://accounts.google.com",
                "accounts.google.com",
            ]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid issuer",
                )
            email = idinfo.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google account has no email",
                )

            user = get_or_create_google_user(email)

            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            print(f"Returning: access_token: {access_token}, token_type: bearer, username: {email}")
            return {"access_token": access_token, "token_type": "bearer", "username": email}

        @self.app.post("/auth/discord/exchange") ##################### DISCORD AUTH #####################
        async def discord_exchange(payload: DiscordCodePayload): # gets code
            data: dict = {
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": payload.code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            }

            async with httpx.AsyncClient() as client:
                token_res = await client.post( # get access_token from discord
                    DISCORD_TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if token_res.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Discord token exchange failed: {token_res.text}",
                    )

                token_data = token_res.json()
                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No access token from Discord",
                    )

                user_res = await client.get( # use access token to get bearer
                    DISCORD_USER_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if user_res.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Discord user fetch failed: {user_res.text}",
                    )

                discord_user = user_res.json() # discord_user contains id, username, discriminator, avatar, email (if scope=email)

                email = discord_user.get("email")
                username = email or f"discord:{discord_user['id']}" # emai l missing but so use discord id
                print(f"discord_user: {discord_user}, email: {email}, username: {username}")
                user = await self.user_manager.get_or_create_oauth_user(email, discord=True)

                access_token = create_access_token( #JWT
                    data={"sub": user.email}
                )
                return { # token back to frontend for protected functions
                    "access_token": access_token,
                    "token_type": "bearer",
                    "username": user.email
                }
