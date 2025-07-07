from fastapi import FastAPI, APIRouter
from src.core.pet_manager import PetManager
from src.core.models import BattlePet

class BattlerApp:
    def __init__(self):
        self.app = FastAPI(title="battler_app", version="0.0.1")
        self.router = APIRouter()
        self.manager = PetManager()

        @self.router.get("/battle_pets/get")
        async def list_battle_pets() -> list[BattlePet]:
            return await self.manager.list_battle_pets()

        self.app.include_router(self.router)