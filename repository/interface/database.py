from pathlib import Path
from typing import Protocol
from core.models import Ability, BattlePet

class DbBase(Protocol):
    async def get_battle_pet(self, name: str) -> BattlePet:
        """Retrieve a battle pet by its name."""
        pass

    async def get_ability(self, name: str) -> Ability:
        """Retrieve an ability by its name."""
        pass

    async def add_battle_pet(self, pet: BattlePet) -> None:
        """Add a new battle pet to the database."""
        pass

    async def add_ability(self, ability: Ability) -> None:
        """Add a new ability to the database."""
        pass

    async def populate_battle_pets(self, battle_pets_file: Path) -> None:
        """Populate the database with battle pets."""
        pass

    async def get_all_battle_pets(self) -> list[BattlePet]:
        """Retrieve all battle pets from the database."""
        pass

    async def get_all_abilities(self) -> list[Ability]:
        """Retrieve all abilities from the database."""
        pass

    async def get_battle_pet_by_type(self, pet_type: str) -> list[BattlePet]:
        """Retrieve all battle pets of a specific type."""
        pass

    async def get_ability_by_type(self, ability_type: str) -> list[Ability]:
        """Retrieve all abilities of a specific type."""
        pass