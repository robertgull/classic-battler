import asyncio
import csv
import ast
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

from core.models import BattlePet, PetType, Ability
from repository.interface.database import DbBase



class MongoDb(DbBase):
    def __init__(self):
        client = AsyncIOMotorClient(
            "mongodb://localhost:3000/petdb",
            uuidrepresentation="standard",
        )
        self.db = client.get_default_database()

    async def get_battle_pet(self, name: str) -> BattlePet:
        """Retrieve a battle pet by its name."""
        pass

    async def get_ability(self, name: str) -> Ability:
        """Retrieve an ability by its name."""
        pass

    async def add_battle_pet(self, pet: BattlePet) -> None:
        """Add a new battle pet to the database."""
        await self.db.battle_pets.insert_one(pet.model_dump())

    async def add_ability(self, ability: Ability) -> None:
        """Add a new ability to the database."""
        await self.db.abilities.insert_one(ability.model_dump())

    async def populate_battle_pets(self, battle_pets_file: Path) -> None:
        """Populate the database with battle pets."""
        with battle_pets_file.open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pet = BattlePet(
                        name=row["Name"],
                        level=int(row["Level"]),
                        health=int(row["Health"]),
                        power=int(row["Power"]),
                        speed=int(row["Speed"]),
                        breed=row["Breed"],
                        abilities=sorted(ast.literal_eval(row["Abilities"])),                        source=row["Source"],
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
        with abilities_file.open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ability = Ability(
                        name=row["Name"],
                        damage=row["Damage"],
                        healing=row["Healing"],
                        duration=row["Duration"],
                        cooldown=row["Cooldown"],
                        accuracy=row["Accuracy"],
                        type=PetType(row["Type"]),
                        popularity=int(row["Popularity"]),
                    )
                    await self.add_ability(ability)
                except Exception as e:
                    print(f"Failed to load ability {row.get('Name', '?')}: {e}")

#test the populate_battle_pets method
async def main():
    mongo_db = MongoDb()
    #await mongo_db.setup()
    #await mongo_db.populate_battle_pets(Path(
    #    r"C:\Users\Rober\repos\classic-battler\data\mop_battle_pets.csv"
    #))
    await mongo_db.populate_abilities(Path(
        r"C:\Users\Rober\repos\classic-battler\data\mop_battle_pet_abilities.csv"
    ))

if __name__ == "__main__":
    asyncio.run(main())