from pathlib import Path

from src.repository.interface.database import DbBase
from src.repository.mongo_db import MongoDb
from src.repository.redis_cache import get_cached, set_cached
from src.core.models import BattlePet, Ability, PetType


class PetDataHandler(DbBase):
    def __init__(self) -> None:
        self.db = MongoDb()

    async def get_all_battle_pets(self) -> list[BattlePet]:
        cache_key = f"battle_pets:all"
        cached = await get_cached(cache_key, BattlePet)
        if cached:
            print("Returning cached battle pets")
            return cached
        print("Fetching battle pets from database")
        db_pets = await self.db.get_all_battle_pets()
        await set_cached(cache_key, db_pets)
        return db_pets

    async def get_battle_pet(self, _id: int) -> BattlePet:
        cache_key = f"battle_pet:{_id}"
        cached = await get_cached(cache_key, BattlePet)
        if cached:
            print(f"Returning cached battle pet with id {_id}")
            return cached
        print(f"Fetching battle pet with id {_id} from database")
        db_pet = await self.db.get_battle_pet(_id)
        await set_cached(cache_key, db_pet.model_dump())
        return db_pet

    async def get_ability(self, _id: int) -> Ability:
        cache_key = f"ability:{_id}"
        cached = await get_cached(cache_key, Ability)
        if cached:
            print(f"Returning cached ability with id {_id}")
            return cached
        db_ability = await self.db.get_ability(_id)
        await set_cached(cache_key, db_ability)
        return db_ability

    async def populate_battle_pets(self, battle_pets_file: Path) -> None:
        """Populate the database with battle pets from a file. Do nothing for cache"""
        await self.db.populate_battle_pets(battle_pets_file)

    async def get_all_abilities(self) -> list[Ability]:
        cache_key = f"abilities:all"
        cached = await get_cached(cache_key, Ability)
        if cached:
            print("Returning cached abilities")
            return cached
        print("Fetching abilities from database")
        db_abilities = await self.db.get_all_abilities()
        await set_cached(cache_key, db_abilities)
        return db_abilities

    async def get_battle_pet_by_type(self, pet_type: PetType) -> list[BattlePet]:
        cache_key = f"battle_pets:type:{pet_type}"
        cached = await get_cached(cache_key, BattlePet)
        if cached:
            print(f"Returning cached battle pets of type {pet_type}")
            return cached
        print(f"Fetching battle pets of type {pet_type} from database")
        db_pets = await self.db.get_battle_pet_by_type(pet_type)
        await set_cached(cache_key, db_pets)
        return db_pets


