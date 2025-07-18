import asyncio
import re
from typing import Optional, Any, Coroutine

from src.core.pet_type_chart import pet_type_matrix
from src.repository.pet_data_handler import PetDataHandler
from src.repository.interface.database import DbBase
from src.core.models import BattlePet, PetType, Ability
from src.core.semantic_search import SemanticSearch

def find_types_strong_against(target_type: PetType) -> list[PetType]:
    return [
        pet_type
        for pet_type, matchup in pet_type_matrix.items()
        if target_type in matchup.get("strong_against", [])
    ]


async def is_damage_ability(ability: Ability) -> bool:
    """Check if an ability is a damaging ability."""
    if ability.damage and ability.damage.strip().lower() != "0":
        return True
    #pattern = r"dealing\s+\d+\s+(" + "|".join([pt.value for pt in PetType]) + r")\s+damage"
    pattern =         r"\b\d+\s+(" + "|".join([pt.value for pt in PetType]) + r")\s+damage\b"

    desc_damage = re.search(pattern, ability.description, re.IGNORECASE)
    if desc_damage:
        print(f"✅✅✅ Description damage found in: {ability.name}")
        return True
    return False


class PetManager:
    def __init__(self, db: Optional[DbBase] = None) -> None:
        self.db = db or PetDataHandler()
        self.sem_search = SemanticSearch(db=self.db)

    async def list_battle_pets(self) -> list[BattlePet]:
        """List all battle pets in the database."""
        return await self.db.get_all_battle_pets()

    async def find_pets_with_ability_type(
        self, ability_type: PetType
    ) -> list[BattlePet]:
        # 1. Get all pets
        pets = await self.db.get_all_battle_pets()

        # 2. Get abilities of the requested type
        abilities = await self.db.get_ability_by_type(ability_type)

        # 3. Build a set of ability IDs of that type
        ability_ids_of_type = {ability.id for ability in abilities}

        # 4. Filter pets that reference one or more of those abilities
        matching_pets = [
            pet
            for pet in pets
            if any(ability_id in ability_ids_of_type for ability_id in pet.abilities)
        ]

        return matching_pets

    async def get_pet(self, _id: int) -> BattlePet:
        """Retrieve a battle pet by its ID."""
        return await self.db.get_battle_pet(_id)

    async def get_ability(self, _id: int) -> Ability:
        """Retrieve an ability by its ID."""
        return await self.db.get_ability(_id)

    async def find_pets_by_type(self, pet_type: PetType) -> list[BattlePet]:
        """Find all battle pets of a specific type."""
        return await self.db.get_battle_pet_by_type(pet_type)

    async def ability_is_effective_against(
        self, attack: Ability, defender: PetType
    ) -> bool:
        """Check if an ability is effective against a specific pet type."""
        # Get the type of the ability
        ability_type = await self.db.get_ability(attack.id)
        if not ability_type:
            return False

        # Check the pet type matrix
        if defender in pet_type_matrix[ability_type.type]["strong_against"]:
            return True
        return False

    async def attacker_is_effective_against(
        self, attacker: BattlePet, defender: BattlePet
    ) -> bool:
        """Check if an attack from one pet is effective against another."""
        for ability_id in attacker.abilities:
            ability = await self.db.get_ability(ability_id)
            if ability and await self.ability_is_effective_against(
                ability, defender.type
            ):
                return True
        return False

    async def list_pets_strong_against(self, target_type: PetType) -> list[BattlePet]:
        """List pets that have at least one damaging ability that is strong against the given type."""
        # Step 1: Get ability types strong against the target type
        strong_ability_types = find_types_strong_against(target_type)

        # Step 2: Fetch abilities of those types
        abilities = []
        for ability_type in strong_ability_types:
            abilities.extend(await self.db.get_ability_by_type(ability_type))

        # Step 3: Filter for damaging abilities
        damaging_abilities = []

        for ability in abilities:
            if await is_damage_ability(ability):
                print(f"✅ Included: {ability.name} (damage = {ability.damage})")
                damaging_abilities.append(ability)
            else:
                print(f"❌ Skipped: {ability.name} (damage = {ability.damage})")

        # Step 4: Collect their IDs
        damaging_ability_ids = {ability.id for ability in damaging_abilities}

        # Step 5: Get all pets
        all_pets = await self.db.get_all_battle_pets()

        # Step 6: Filter pets that use at least one damaging strong ability
        matching_pets = [
            pet
            for pet in all_pets
            if any(ability_id in damaging_ability_ids for ability_id in pet.abilities)
        ]

        return matching_pets

    async def list_pets_defensive_against(
        self, attack_type: PetType
    ) -> list[BattlePet]:
        """List all pets that are defensively strong (resistant to) a specific attack type."""
        resistant_types = pet_type_matrix.get(attack_type, {}).get("weak_against", [])
        pets = []
        for pet_type in resistant_types:
            pets.extend(await self.db.get_battle_pet_by_type(pet_type))
        return pets

    async def double_tappers(self, type_to_counter: PetType) -> list[BattlePet]:
        """List all pets that are double-tappers (strong against Aquatic and defensive against Flying)."""
        list_pets_strong_against = await self.list_pets_strong_against(type_to_counter)
        list_pets_defensive_against = await self.list_pets_defensive_against(
            type_to_counter
        )
        return list(set(list_pets_strong_against) & set(list_pets_defensive_against))

    async def sem_search_abilities(
        self, query: str, k: int = 5
    ) -> list[Ability]:
        ids, weights = self.sem_search.search_ability(query, k=k)
        ids = list(map(int, ids))
        return await self.db.get_abilities_by_ids(ids)



# test
async def main():
    manager = PetManager()
    await manager.sem_search.set_embeddings()
    ability_query = "causes burning"
    response = await manager.sem_search_abilities(ability_query)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
