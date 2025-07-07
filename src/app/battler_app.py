from fastapi import FastAPI, APIRouter, HTTPException, Query
from src.core.pet_manager import PetManager
from src.core.models import BattlePet, PetType
from fastapi.middleware.cors import CORSMiddleware

class BattlerApp:
    def __init__(self):
        self.app = FastAPI(title="battler_app", version="0.0.1")
        self.router = APIRouter()
        self.manager = PetManager()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Or ["http://localhost:5173"] for dev only
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.router.get("/battle_pets/get")
        async def list_battle_pets() -> list[BattlePet]:
            return await self.manager.list_battle_pets()

        @self.router.get("/battle_pets/get_by_id")
        async def get_battle_pet_by_id(_id: int) -> BattlePet:
            return await self.manager.get_pet(_id)

        @self.router.get("/battle_pets/list_double_counters")
        async def list_double_counters(_type: str = Query(..., description="Pet type (e.g. 'Aquatic', 'Beast')")) -> \
        list[BattlePet]:
            try:
                type_enum = PetType(_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid pet type: {_type}")
            return await self.manager.double_tappers(type_enum)

        self.app.include_router(self.router)