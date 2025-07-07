from pathlib import Path
from typing import Protocol
from backend.src.core.models import Ability, BattlePet, PetType


class DbBase(Protocol):
    async def get_battle_pet(self, _id: int) -> BattlePet:
        """Retrieve a battle pet by its name."""
        raise NotImplementedError()

    async def get_ability(self, _id: int) -> Ability:
        """Retrieve an ability by its name."""
        raise NotImplementedError()

    async def get_abilities_by_ids(self, ids: list[int]) -> list[Ability]:
        """Retrieve abilities by their IDs."""
        raise NotImplementedError()

    async def add_battle_pet(self, pet: BattlePet) -> None:
        """Add a new battle pet to the database."""
        raise NotImplementedError()

    async def add_ability(self, ability: Ability) -> None:
        """Add a new ability to the database."""
        raise NotImplementedError()

    async def populate_battle_pets(self, battle_pets_file: Path) -> None:
        """Populate the database with battle pets."""
        raise NotImplementedError()

    async def get_all_battle_pets(self) -> list[BattlePet]:
        """Retrieve all battle pets from the database."""
        raise NotImplementedError()

    async def get_all_abilities(self) -> list[Ability]:
        """Retrieve all abilities from the database."""
        raise NotImplementedError()

    async def get_battle_pet_by_type(self, pet_type: PetType) -> list[BattlePet]:
        """Retrieve all battle pets of a specific type."""
        raise NotImplementedError()

    async def get_ability_by_type(self, ability_type: PetType) -> list[Ability]:
        """Retrieve all abilities of a specific type."""
        raise NotImplementedError()
