import asyncio
import csv
import ast
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient  # Used for creating indexes
from backend.src.core.models import BattlePet, PetType, Ability
from backend.src.repository.interface.database import DbBase


class MongoDb(DbBase):
    def __init__(self):
        # Ensure indexes synchronously with PyMongo
        pymongo_client = MongoClient("mongodb://localhost:3000/petdb")
        pm_db = pymongo_client.get_default_database()
        pm_db.abilities.create_index("id", unique=True)
        pm_db.battle_pets.create_index("id", unique=True)

        client = AsyncIOMotorClient(
            "mongodb://localhost:3000/petdb",
            uuidrepresentation="standard",
        )
        self.db = client.get_default_database()
        # self.db.abilities.create_index("id", unique=True) # pyright: ignore[reportUnusedCoroutine]
        # self.db.battle_pets.create_index("id", unique=True) # pyright: ignore[reportUnusedCoroutine]

    async def get_battle_pet(self, _id: int) -> BattlePet:
        """Retrieve a battle pet by its id."""
        data = await self.db.battle_pets.find_one({"id": _id})
        if data is None:
            raise ValueError(f"Battle pet with id {_id} not found")
        data.pop("_id", None)
        return BattlePet(**data)

    async def get_ability(self, _id: int) -> Ability:
        """Retrieve an ability by its ID."""
        data = await self.db.abilities.find_one({"id": _id})
        if data is None:
            raise ValueError(f"Ability with id {_id} not found")
        return Ability(**data)

    async def get_abilities_by_ids(self, ids: list[int]) -> list[Ability]:
        """Retrieve abilities by their IDs."""
        cursor = self.db.abilities.find({"id": {"$in": ids}})
        abilities = []
        async for document in cursor:
            document.pop("_id", None)
            abilities.append(Ability(**document))
        return abilities

    async def add_battle_pet(self, pet: BattlePet) -> None:
        """Add a new battle pet to the database."""
        await self.db.battle_pets.insert_one(pet.model_dump())

    async def add_ability(self, ability: Ability) -> None:
        """Add a new ability to the database."""
        await self.db.abilities.insert_one(ability.model_dump())

    async def get_all_battle_pets(self) -> list[BattlePet]:
        """Retrieve all battle pets from the database."""
        cursor = self.db.battle_pets.find()
        pets = []
        async for document in cursor:
            document.pop("_id", None)  # <- remove MongoDB's internal _id
            pets.append(BattlePet(**document))
        return pets

    async def get_all_abilities(self) -> list[Ability]:
        """Retrieve all abilities from the database."""
        cursor = self.db.abilities.find()
        abilities = []
        async for document in cursor:
            document.pop("_id", None)  # <- remove MongoDB's internal _id
            abilities.append(Ability(**document))
        return abilities

    async def get_battle_pet_by_type(self, pet_type: PetType) -> list[BattlePet]:
        """Retrieve all battle pets of a specific type."""
        cursor = self.db.battle_pets.find({"type": pet_type})
        pets = []
        async for document in cursor:
            document.pop("_id", None)  # <- remove MongoDB's internal _id
            pets.append(BattlePet(**document))
        return pets

    async def get_ability_by_type(self, ability_type: PetType) -> list[Ability]:
        """Retrieve all abilities of a specific type."""
        cursor = self.db.abilities.find({"type": ability_type})
        abilities = []
        async for document in cursor:
            document.pop("_id", None)
            abilities.append(Ability(**document))
        return abilities

    async def populate_battle_pets(self, battle_pets_file: Path) -> None:
        """Populate the database with battle pets."""
        with battle_pets_file.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pet = BattlePet(
                        id=int(row["ID"]),
                        name=row["Name"],
                        level=int(row["Level"]),
                        health=int(row["Health"]),
                        power=int(row["Power"]),
                        speed=int(row["Speed"]),
                        breed=row["Breed"],
                        abilities=sorted(ast.literal_eval(row["Abilities"])),
                        source=row["Source"],
                        type=PetType(row["Type"]),
                        popularity=int(row["Popularity"]),
                        is_untameable=row["Untameable"].strip().lower() == "true",
                    )
                    # Now do something with the validated pet object
                    await self.add_battle_pet(pet)  # or add to DB
                except Exception as e:
                    print(f"Failed to load pet {row.get('Name', '?')}: {e}")

    async def populate_abilities(self, abilities_file: Path) -> None:
        """Populate the database with abilities."""
        with abilities_file.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ability = Ability(
                        id=int(row["ID"]),
                        name=row["Name"],
                        damage=row["Damage"],
                        healing=row["Healing"],
                        duration=row["Duration"],
                        cooldown=row["Cooldown"],
                        accuracy=row["Accuracy"],
                        type=PetType(row["Type"]),
                        popularity=int(row["Popularity"]),
                        description=row["Description"],
                    )
                    await self.add_ability(ability)
                except Exception as e:
                    print(f"Failed to load ability {row.get('Name', '?')}: {e}")


# test the populate_battle_pets method
async def main():
    mongo_db = MongoDb()
    # Get project root by going up from the current file
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"

    battle_pets_file = DATA_DIR / "mop_battle_pets.csv"
    abilities_file = DATA_DIR / "mop_battle_pet_abilities.csv"

    await mongo_db.populate_battle_pets(battle_pets_file)
    await mongo_db.populate_abilities(abilities_file)
    print(await mongo_db.get_abilities_by_ids([593, 934, 519]))


if __name__ == "__main__":
    asyncio.run(main())
