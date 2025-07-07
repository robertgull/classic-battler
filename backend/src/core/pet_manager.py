import asyncio
from typing import Optional

from backend.src.core.pet_type_chart import pet_type_matrix
from backend.src.repository.mongo_db import MongoDb
from backend.src.repository.interface.database import DbBase
from backend.src.core.models import BattlePet, PetType, Ability


def find_types_strong_against(target_type: PetType) -> list[PetType]:
    return [
        pet_type
        for pet_type, matchup in pet_type_matrix.items()
        if target_type in matchup.get("strong_against", [])
    ]


class PetManager:
    def __init__(self, db: Optional[DbBase] = None) -> None:
        self.db = db or MongoDb()

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
            if ability.damage and ability.damage.strip().lower() != "0":
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


# test
async def main():
    manager = PetManager()
    double_tap_type = PetType.UNDEAD  # Example type for double-tapping

    list_pets_strong_against = await manager.list_pets_strong_against(double_tap_type)
    print(
        f"Pets strong against {double_tap_type}: {[pet.name for pet in list_pets_strong_against]}"
    )
    list_pets_defensive_against = await manager.list_pets_defensive_against(
        double_tap_type
    )
    print(
        f"Pets defensive against {double_tap_type}: {[pet.name for pet in list_pets_defensive_against]}"
    )
    combined_list = list(
        set(list_pets_strong_against) & set(list_pets_defensive_against)
    )
    print(
        f"Combined list of pets strong against {double_tap_type} and defensive against {double_tap_type}: {[pet for pet in combined_list]}"
    )
    print(
        f"Combined list of pets strong against {double_tap_type} and defensive against {double_tap_type}: {[f'{pet.name} from {pet.source}' for pet in combined_list]}"
    )


if __name__ == "__main__":
    asyncio.run(main())
